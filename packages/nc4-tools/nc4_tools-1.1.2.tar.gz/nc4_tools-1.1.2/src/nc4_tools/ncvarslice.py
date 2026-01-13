"""nc4_tools.ncvarslice - Contains the NCVarSlicer class.

The NCVarSlicer class is used for slicing a `netCDF4.Variable` along some dimension in to
another (possibly irregular) dimension. For example, slicing a day-of-year dimension into
months.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, overload

import numpy as np
import numpy.typing as npt
from typing_extensions import TypeGuard

if TYPE_CHECKING:
    import netCDF4


def isintarray(
    var: Any,
) -> TypeGuard[npt.NDArray[np.signedinteger] | npt.NDArray[np.unsignedinteger]]:
    """Confirm that some object is a numpy array of (some kind of) integers."""
    return isinstance(var, np.ndarray) and issubclass(var.dtype.type, np.integer)


class NCVarSlicer:
    """Class for slicing a netCDF4 variable using two other variables for indicies.

    In NetCDF schemata such as the CFRadial Format, one or more virtual dimensions may
    exist that subdivide a real dimension. In this situation, ancillary variables must be
    provided to specify the start and stop indices in the real dimension that are the
    boundaries of each unit in the virtual dimension.

    In the case of the CFRadial format the sweep dimension subdivides the time dimension,
    and the sweep_start_ray_index and sweep_end_ray_index variables specify the start and
    end boundaries of each sweep in the time dimension.

    Once created, NCVarSlicer object may be called with getitem (i.e. []) syntax. If a
    single integer index is provided, a single slice object is returned corresponding to
    the real dimension bounds of that index in the virtual dimension. If a slice is
    provided, then a list of slice objects is returned corresponding to each selected
    index in the virtual dimension.
    """

    def __init__(
        self,
        start_index_var: netCDF4.Variable,
        end_index_var: netCDF4.Variable,
        *,
        end_inclusive: bool = True,
        offline: bool = True,
    ):
        """Set up the NCVarSlicer object.

        Parameters
        ----------
        start_index_var : netCDF4.Variable
            Variable that supplies the start index in the real dimension for each point in
            the virtual dimension.
        end_index_var : netCDF4.Variable
            Variable that supplies the end index in the real dimension for each point in
            the virtual dimension.
        end_inclusive : bool, optional
            If True, the index values in end_index_var are the inclusive end boundaries in
            the real dimension for each unit in the virtual dimension. If False, they are
            exclusive boundaries. Default is True.
        offline : bool, optional
            If True (default) slices are calculated from the NetCDF file and saved in this
            instance. The slices can then be used if the NetCDF dataset is closed.

        """
        self._start_index_var: netCDF4.Variable = start_index_var
        self._end_index_var: netCDF4.Variable = end_index_var
        self.end_inclusive: bool = end_inclusive
        if offline:
            self._slices = self[:]
        self.offline: bool = offline

    @property
    def start_index_var(self) -> netCDF4.Variable:
        """The variable containing the starting indices of the slices."""
        try:
            # All NetCDF vars have a name, so this breaks if dataset is closed
            _ = self._start_index_var.name
        except RuntimeError as ex:
            if "Not a valid ID" in ex.args[0]:
                raise RuntimeError(
                    "The NetCDF4 dataset must be open to use the NCVarSlicer."
                ) from None
            raise
        return self._start_index_var

    @property
    def end_index_var(self) -> netCDF4.Variable:
        """The variable containing the ending indices of the slices."""
        try:
            # All NetCDF vars have a name, so this breaks if dataset is closed
            _ = self._end_index_var.name
        except RuntimeError as ex:
            if "Not a valid ID" in ex.args[0]:
                raise RuntimeError(
                    "The NetCDF4 dataset must be open to use the NCVarSlicer."
                ) from None
            raise
        return self._end_index_var

    @overload
    def __getitem__(self, key: int) -> slice: ...

    @overload
    def __getitem__(self, key: slice) -> list[slice]: ...

    def __getitem__(self, key: int | slice) -> slice | list[slice]:
        """Get the slice or slices to use on the data variable.

        `__getitem__` returns the slice[s] of the real dimension for the provided
        ind[ex/ices] in the virtual dimension.
        """
        if getattr(
            self, "offline", False
        ):  # getattr allows calling before offline is set
            return self._slices[key]
        if isinstance(key, int):
            idx = key
            start_idx = self.start_index_var[idx]
            end_idx = self.end_index_var[idx]
            assert isinstance(start_idx, int)
            assert isinstance(end_idx, int)
            if self.end_inclusive:
                end_idx += 1
            return slice(start_idx, end_idx)
        if isinstance(key, slice):
            slc = key
            starts = self.start_index_var[slc]
            ends = self.end_index_var[slc]
            assert isintarray(starts)
            assert isintarray(ends)
            if self.end_inclusive:
                ends += 1
            return [slice(start_idx, end_idx) for start_idx, end_idx in zip(starts, ends)]
        raise TypeError("NCVarSlicer expects an integer or slice as input")

    def __iter__(self):
        """Iterate over all slices defined by this slicer.

        The iterator yields each slice in sequence until no further slices are available.
        """
        i = 0
        while True:
            try:
                yield self[i]
            except IndexError:
                break
            i += 1


VarSlice = NCVarSlicer  # for backward compatibility
