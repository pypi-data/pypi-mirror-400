"""nc4_tools - Modules to aid some tasks of working with the netcdf4-python library.

Modules
-------

nc4_tools.duplicate_var
    Includes the `duplicate_var` function to create a variable in a new dataset based on a
    variable in an existing dataset.
nc4_tools.ncdataset
    Includes the `NCDataset` class which subclasses `netCDF4.Dataset` to allow for
    re-opening a closed `Dataset` instance with the same parameters.
nc4tools.nctemplate
    Includes the NCTemplate class for creating a template dataset from a netCDF CDL file.
    This module requires the netCDF4 `ncgen` utility to be available on the system PATH.
nc4tools.ncvarslice
    Contains the NCVarSlicer class, used for slicing a `netCDF4.Variable` along some
    dimension in to another (possibly irregular) dimension. For example, slicing a
    day-of-year dimension into months.

Package-wide Variables
----------------------
__version__
    Version string for this release


"""

import importlib.metadata as _importlib_metadata

__version__ = _importlib_metadata.version(__name__)
