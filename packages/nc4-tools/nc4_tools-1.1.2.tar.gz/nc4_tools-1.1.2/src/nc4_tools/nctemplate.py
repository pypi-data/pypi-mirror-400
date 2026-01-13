"""nc4_tools.nctemplate - Provides the NCTemplate class.

The NCTemplate class may be used to create a template dataset from a netCDF CDL file.

This module requires the netCDF4 `ncgen` utility to be available on the system PATH.

Classes
-------
NCTemplate
    Subclass of `nc4_tools.ncdataset.NCDataset` that can create a dataset from a netCDF
    CDL file.
NCTemplateError
    Raised on import if the `ncgen` utility is not found in the system PATH, or if there
    is an error when calling `ncgen`.

"""

from __future__ import annotations

import shlex
import shutil
import subprocess
import tempfile
import time
from contextlib import suppress
from pathlib import Path
from typing import Any

from nc4_tools.ncdataset import NCDataset


class NCTemplateError(Exception):
    """Represent an error that occurs when using the NCTemplate class."""


class NCTemplate(NCDataset):
    """Class to create a template netCDF dataset.

    The template dataset may be created using a netCDF CDL file or by cloning the
    structure of an existing netCDF dataset.

    When used in a context manager (`with ... :`), the `NCDataset` is provided, rather
    than the NCTemplate object.
    """

    _private_atts = (*NCDataset._private_atts, "_tempfile")  # type: ignore[assignment]  # modifying the no. of elems in _private_atts
    _tempfile: bool = False

    def __init__(
        self,
        template_path: Path | str,
        new_nc_path: Path | None = None,
        **kwargs: Any,
    ):
        """Initialize the template dataset.

        Parameters
        ----------
        template_path : Path
            Path to an existing template NetCDF file, or a NetCDF CDL file to use to
            create the template NetCDF file.
        new_nc_path : Path, optional
            Path to generate the template NetCDF file, if template_path points to a CDL
            file. By default, the template NetCDF file is create with the same path and
            name as the CDL file with the nc extension. If template_path is a .nc file,
            this is ignored.
        **kwargs : optional
            Other arguments to pass in to netCDF4.Dataset

        Raises
        ------
        FileNotFoundError
            The template netCDF or CDL file was not found.
        ValueError
            The provided template file was not a .nc or .cdl file.

        """
        template_path = Path(template_path)
        if template_path.suffix.lower() == ".cdl":
            # Create the template NC file in the same dir as the cdl file if possible,
            # else in /tmp. Retry up to three times in case another instance of ncgen is
            # running (which causes an error)
            max_tries = 3
            nct_err = None
            for _ in range(max_tries):
                try:
                    tmpl_nc_path = self._ncgen(template_path, new_nc_path)
                    break
                except NCTemplateError as err:
                    nct_err = err
                    time.sleep(0.25)  # wait to try again
            else:
                # Didn't break, never got a tmpl_nc_path
                if nct_err:  # should always be true if we get here
                    raise nct_err
        elif template_path.suffix.lower() == ".nc":
            if not template_path.exists():
                raise FileNotFoundError(f"No file exists at {template_path}.")
            tmpl_nc_path = template_path
        else:
            raise ValueError(
                "NCTemplate expected a path ending in .cdl or .nc. Got"
                f" {template_path.suffix}."
            )
        super().__init__(tmpl_nc_path, **kwargs)

    def __del__(self):
        """Close the dataset and delete a tempfile if necessary."""
        if self.isopen():
            self.close()
        if self._tempfile:
            # delete the temporary nc file
            with suppress(FileNotFoundError):
                self.nc_path.unlink()

    def _ncgen(self, cdl_path: Path, new_nc_path: Path | None = None) -> Path:
        """Create a NetCDF file from a CDL file. Requires the NetCDF `ncgen` utility.

        If the NetCDF file cannot be created at the specified path, it is created as a
        tempfile.

        Parameters
        ----------
        cdl_path : Path
            Path to the CDL file to use to create the NetCDF file.
        new_nc_path : Path, optional
            Path to the new NetCDF file to create. If not provided, it is created in the
            dir with the CDL file with the same name as the CDL file.

        Returns
        -------
        Path
            Path to the created NetCDF file.

        Raises
        ------
        NCTemplateError
            If `ncgen` is missing or there is an error creating the NetCDF file.

        """
        cdl_dir = cdl_path.parent
        nc_name = f"{cdl_path.stem}.nc"
        tmpl_nc_path = new_nc_path or (cdl_dir / nc_name)
        # Make sure we can write the nc file to this spot.
        self._tempfile = False
        try:
            with tmpl_nc_path.open("w") as fobj:
                fobj.write("\0")
        except OSError:
            # If not, make a temporary nc file. (Silently! :O)
            tmpl_nc_path = Path(tempfile.gettempdir(), nc_name)
            self._tempfile = True
        # Remove an existing template NC file if it exists.
        with suppress(FileNotFoundError):
            tmpl_nc_path.unlink()

        ncgen_cmd = f'ncgen -b -k nc4 -o "{tmpl_nc_path}" "{cdl_path}"'
        # noinspection PyArgumentList
        result: subprocess.CompletedProcess = subprocess.run(  # noqa: S603  # command is OK
            shlex.split(ncgen_cmd), capture_output=True, check=False
        )
        if result.returncode != 0:
            raise NCTemplateError(
                "Error generating template nc file:"
                f" {result.stderr.decode('utf8').rstrip()}"
            )
        # tmpl_nc_path now points to the template NetCDF file
        return tmpl_nc_path


if not shutil.which("ncgen"):
    raise NCTemplateError(
        "The ncgen tool is not present or is not in PATH on this PC. Install netcdf-bin"
        " or similar."
    )
