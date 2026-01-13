"""nc4_tools.ncdataset - Contains the NCDataset class.

Module-level variables
----------------------
auto_mask
    Sets the default value of the `auto_mask` parameter for every dataset opened or
    created with `NCDataset`. Default is False.

Classes
-------
NCDataset
    Wrapper for `netCDF4.Dataset` that keeps track of the filename and keyword arguments,
    even when it closes.
NCDatasetError
    Raised when trying to change dataset calling arguments and the dataset is open.
NonScalarVariableError
    Raised when trying to use NCDataset.get_scalar_var() on a non-scalar variable
DatasetClosedError
    Raised when trying to access data in a closed dataset.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict

import netCDF4
from typing_extensions import Buffer, Self, Unpack

if TYPE_CHECKING:
    from netCDF4 import AccessMode, Format
else:
    AccessMode = str
    Format = str


class NCDatasetError(Exception):
    """General error class for NCDataset."""


class NonScalarVariableError(NCDatasetError):
    """Error raised when an scalar operation is attempted on a non-scalar variable."""

    def __init__(self, var: netCDF4.Variable):
        """Generate the error message from the variable data."""
        super().__init__(
            f"{var.name} is not a scalar variable (dimensions are {var.dimensions})"
        )


class DatasetClosedError(NCDatasetError):
    """Error raised when an operation is attempted on a closed dataset."""

    def __init__(self):
        """Initialize the error with a constant string."""
        super().__init__(
            "The dataset is not open and thus its contents are not accessible."
        )


auto_mask: bool = False


class _NC4DsKwargs(TypedDict, total=False):
    """Extra keyword arguments available for netCDF4.Dataset.__init__ (as of 1.7.2).

    Note: Technically, additional kwargs are allowed by __init__, but they are not used.
    """

    clobber: bool
    format: Format
    diskless: bool
    persist: bool
    keepweakref: bool
    memory: Buffer | int | None
    encoding: str | None
    parallel: bool
    comm: Any
    info: Any
    auto_complex: bool


class NCDataset(netCDF4.Dataset):
    """A wrapper class for `netCDF4.Dataset` that allows for reopening the dataset.

    NCDataset keeps track of the filename and keyword arguments, even when it closes, so
    that it may be re-opened without needing to store that information elsewhere.

    Examples
    --------
    >>> ds = NCDataset("example.nc", mode="w", keepopen=False, diskless=True, persist=True)
    >>> print(ds)
    NCDataset[netCDF4.Dataset]
    nc_path: example.nc
    nc_kwargs: {'diskless': True, 'persist': True, 'mode': 'w', 'clobber': False}
    (closed)
    >>> # Since mode was "w", mode is now automatically "a" (unless we set clobber=False)
    >>> # Changes to the kwargs can be made with update_params or just __call__
    >>> with ds(diskless=False):
    ...     # Can augment the netCDF4.Dataset here, just like netCDF4.Dataset
    ...     ds.createDimension("time", 1024)
    ...     print(ds)
    ...
    NCDataset[netCDF4.Dataset]
    nc_path: example.nc
    nc_kwargs: {'diskless': False, 'persist': True, 'mode': 'a', 'clobber': False}
    <class 'hpx_radar_recorder.ncdataset.NCDataset'>
    root group (NETCDF4 data model, file format HDF5):
        dimensions(sizes): time(1024)
        variables(dimensions):
        groups:

    """  # noqa: E501

    _private_atts = (
        "nc_path",
        "nc_kwargs",
        "auto_mask",
        "failfast",
        "_ctxmgr_depth",
        "_closeval",
    )  # for __getattr__ and __setattr__
    nc_path: Path
    nc_kwargs: dict[str, Any]
    auto_mask: bool
    failfast: bool
    _ctxmgr_depth: int
    _closeval: memoryview

    def __init__(
        self,
        nc_path: Path | str,
        mode: AccessMode = "r",
        *,
        keepopen: bool = True,
        failfast: bool = True,
        **nc_kwargs: Unpack[_NC4DsKwargs],
    ):
        """Initialize the NCDataset object.

        Opens or creates a netCDF4.Dataset and optionally leaves it open for modification.
        The file path and keyword arguments are retained for future use of the file.

        Parameters
        ----------
        nc_path
            Path to open or create the netCDF dataset.
        mode
            See `netCDF4.Dataset.__init__()`. For compatibility with `Dataset(path_to_ds,
            "r")` syntax.
        keepopen
            If True, the dataset is left open after creating/opening. (default) If False,
            the dataset file is created/opened (depending on mode) and closed again. This
            confirms that it exists and saves the keyword arguments for future
            interaction.
        failfast
            If true, accessing a variable or group in a closed dataset with
            `__getitem__()` (e.g. `dataset["myvar"]`) will fail immediately with a
            `DatasetClosedError`, rather than when something in the variable or group is
            used (and then only with `RuntimeError('NetCDF: Not a valid ID')`)
        **nc_kwargs
            Other arguments to pass to `netCDF4.Dataset.__init__()`. See the
            netCDF4-python docs for details.

        """
        self.nc_path = Path(nc_path)
        self.auto_mask = auto_mask  # use module-level default
        self.nc_kwargs = nc_kwargs | {"mode": mode}
        self.failfast = failfast
        self.open()
        if not keepopen:
            self.close()
        self._ctxmgr_depth = 0
        self._closeval = memoryview(
            b""
        )  # overriden when an open dataset is actually closed

    def get_scalar_var(self, varname: str, **kwargs: Any) -> Any:
        """Get a variable, if it exists. Otherwise return a default or raise an error.

        If the variable does not existing and a `default` value is not provided,
        whatever error is raised by netCDF4.Dataset will be raised (IndexError). A
        NonScalarVariableError will be raised if the variable is not scalar.
        """
        try:
            var_: netCDF4.Variable = self[varname]
        except IndexError:
            if "default" in kwargs:
                return kwargs["default"]
            raise
        try:
            return var_.getValue().item()
        except AttributeError:  # "scalar" strings don't have item()
            return var_.getValue()
        except IndexError:
            raise NonScalarVariableError(var_) from None

    # Have to override __getattr__ and __setattr__ to allow access to this class's
    # attributes.
    def __getattr__(self, name: str) -> Any:
        """Get any attribute of the dataset.

        __getattr__ first checks self._private_atts for any non-netCDF object attributes.
        It then ensures that the dataset is open, and if not, raises a DatasetClosedError.
        Lastly, it attempts to get the attribute from the dataset itself.
        """
        if name in self._private_atts:
            return self.__dict__[name]
        if not self.isopen():
            raise DatasetClosedError
        return super().__getattr__(name)

    def __setattr__(self, name: str, value: Any):
        """Set an attribute, if possible.

        If the attribute is a member of `NCDataset`, set it there. Then, check if the
        dataset is open and if not, raise a `DatasetClosedError`--otherwise set the
        attribute on the `netCDF4.Dataset`.
        """
        if name in self._private_atts:
            self.__dict__[name] = value
            return
        if not self.isopen():
            raise DatasetClosedError
        super().__setattr__(name, value)

    def __getattribute__(self, name: str) -> Any:
        """Get an attribute, if possible.

        If the attribute is a member of `NCDataset`, get it from there. Then, check if the
        dataset is open and if not, raise a `DatasetClosedError`--otherwise get the
        attribute from the `netCDF4.Dataset`.
        """
        try:
            return super().__getattribute__(name)
        except RuntimeError as rte:
            if "not a valid ID" in str(rte.args[0]).lower():
                raise DatasetClosedError from None
            raise

    def __getitem__(self, elem: str) -> Any:
        """Get a variable or group from a dataset.

        If `failfast` is set and the dataset is closed, raise a `DatasetClosedError`.
        Otherwise return the value from __getitem__ on the underlying netCDF4.Dataset.
        """
        if self.failfast and not self.isopen():
            raise DatasetClosedError
        return super().__getitem__(elem)

    def __enter__(self):
        """Enter a context manager block for this dataset, opening the dataset if needed.

        A depth counter is incremented such that the dataset may be "entered" and "exited"
        multiple times but is only closed when the counter has reached zero (outermost
        context block is exited).
        """
        self._ctxmgr_depth += 1
        self.open()
        return self

    def __exit__(self, *args: object):
        """Exit a context manager block for this dataset.

        The internal context depth counter is decremented and the dataset is closed when
        the outermost context block is exited.
        """
        self._ctxmgr_depth -= 1
        if self._ctxmgr_depth <= 0:
            self.close()

    def __call__(self, **kwargs: Any) -> Self:
        """If the dataset is closed, __call__ can be used to change the calling kwargs.

        Parameters
        ----------
        **kwargs
            Arguments to pass to `update_params()`.

        Returns
        -------
        NCDataset
            This NCDataset instance.

        """
        self.update_params(**kwargs)
        return self

    def __str__(self):
        """Provide a string representation of the NCDataset.

        `netCDF4.Dataset.__str__()` raises an error if the dataset is closed. This method
        instead simply shows the dataset path and initializer keyword arguments and either
        shows the summary from `netCDF4.Dataset.__str__()` or notes that the dataset is
        closed.
        """
        ds_repr = super().__str__() if self.isopen() else "(closed)"
        return (
            f"{self.__class__}[netCDF4.Dataset]"
            f"\nnc_path: {self.nc_path}"
            f"\nnc_kwargs: {self.nc_kwargs}"
            f"\n{ds_repr}"
        )

    def update_params(self, *, replace_kwargs: bool = False, **kwargs: Any) -> None:
        """Update keyword arguments passed to `netCDF4.Dataset.__init__().

        Parameters
        ----------
        replace_kwargs : bool, optional
            If True, the (k,v) pairs in `**kwargs` replace the previous keyword arguments.
            Otherwise, `**kwargs` amends the existing arguments. Default is False.
        **kwargs
            Keyword arguments for `netCDF4.Dataset.__init__()`.

        Raises
        ------
        NCDatasetError
            If called when the dataset is open.

        """
        if self.isopen():
            raise NCDatasetError("Cannot update calling parameters when dataset is open.")
        if replace_kwargs:
            self.nc_kwargs = kwargs
        else:
            self.nc_kwargs.update(kwargs)

    def open(self, **kwargs: Any) -> None:
        """Reopen the dataset with the same or new arguments.

        By default `clobber=False` (see doc for `netCDF4.Dataset.__init__()`). If
        `clobber==True`, it will revert to default (`False`) after the dataset is closed.
        Other kwargs will update the default kwargs.

        Parameters
        ----------
        **kwargs
            Updates to kwargs to pass to `netCDF4.Dataset.__init__()`.

        """
        if kwargs:
            self.update_params(**kwargs)
        if not self.isopen():
            super().__init__(self.nc_path, **self.nc_kwargs)
            super().set_auto_mask(self.auto_mask)

    def close(self) -> memoryview:
        """Close the dataset.

        Calls netCDF4.Dataset.close() but only if the dataset it open.
        Resets clobber to False and mode to "a" if it was "w".
        """
        if self.isopen():
            self._closeval = super().close()
        self.nc_kwargs["clobber"] = False
        if self.nc_kwargs.get("mode", "r") == "w":
            self.nc_kwargs["mode"] = "a"
        return self._closeval

    def set_auto_mask(self, value: bool) -> None:  # noqa: FBT001  # match superclass signature
        """Call `Varaible.set_auto_mask()` for all variables in this Dataset.

        See <https://unidata.github.io/netcdf4-python/#netCDF4.Dataset.set_auto_mask>

        Value preserved across dataset close/open, and OK to set with closed dataset.
        """
        if self.isopen():
            super().set_auto_mask(value)
        self.auto_mask = value

    # ###
    # Override variables, dimensions, and groups properties to "fail fast" if desired.
    # ###
    @property
    def variables(self) -> dict[str, netCDF4.Variable]:
        """The top-level variables in the dataset."""
        if self.failfast and not self.isopen():
            raise DatasetClosedError
        # get the base class property
        return super().variables

    @property
    def dimensions(self) -> dict[str, netCDF4.Dimension]:
        """The top-level dimensions in the dataaset."""
        if self.failfast and not self.isopen():
            raise DatasetClosedError
        # get the base class property
        return super().dimensions

    @property
    def groups(self) -> dict[str, netCDF4.Group]:
        """The top-level groups in the dataset."""
        if self.failfast and not self.isopen():
            raise DatasetClosedError
        # get the base class property
        return super().groups
