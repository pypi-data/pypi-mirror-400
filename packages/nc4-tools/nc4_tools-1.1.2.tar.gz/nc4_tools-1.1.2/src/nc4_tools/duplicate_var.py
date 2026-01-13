"""nc4_tools.duplicate_var - Tools for cloning a dataset.

Public Functions
---------
get_createVar_kwargs
    Get the keyword arguments for creating a new variable from an existing variable.
contains_vlen
    Check if a netCDF4.Variable datatype is or contains a variable-length datatype.
duplicate_var
    Duplicate a variable in a dataset based on an existing variable in the dataset.
"""

import logging
from typing import Any

import numpy as np
from netCDF4 import CompoundType, Dataset, Variable, VLType

from nc4_tools._logging import trace

logger = logging.getLogger(__name__)


def get_createVar_kwargs(var: Variable) -> dict[str, Any]:
    """Get the keyword arguments for creating a new variable from an existing variable.

    Inputs
    ------
    var
        `netCDF4.Variable` that already exists in some (open) `netCDF4.Dataset`

    Returns
    -------
    kwargs
        Dict of keyword arguments to use with `netCDF4.Dataset.createVariable`

    """
    filters = var.filters()
    # copy these fields straight from `filters()`
    kwargs: dict[str, Any] = {
        filt_key: filters[filt_key]  # type: ignore[literal-required]
        for filt_key in ["complevel", "shuffle", "fletcher32"]
    }
    # Any of these in filters() set the compression type
    for comptype in ["zlib", "zstd", "bzip2"]:
        if filters[comptype]:  # type: ignore[literal-required]
            kwargs["compression"] = comptype
            break
    # blosc and szip details
    if filters["blosc"]:
        kwargs["compression"] = filters["blosc"]["compressor"]
        kwargs["blosc_shuffle"] = filters["blosc"]["shuffle"]
    if filters["szip"]:
        kwargs["compression"] = "szip"
        kwargs["szip_coding"] = filters["szip"]["coding"]
        kwargs["szip_pixels_per_block"] = filters["szip"]["pixels_per_block"]
    # chunking stuff
    if var.chunking() == "contiguous":
        kwargs["contiguous"] = True
    else:
        kwargs["chunksizes"] = var.chunking()
    # quantization stuff
    if hasattr(var, "least_significant_digit"):
        kwargs["least_significant_digit"] = var.least_significant_digit
    if quant := var.quantization():
        kwargs["significant_digits"] = quant[0]
        kwargs["quantize_mode"] = quant[1]
    # fill value
    if hasattr(var, "_FillValue"):
        kwargs["fill_value"] = var._FillValue
    return kwargs


def contains_vlen(datatype: Any) -> bool:
    """Check if a netCDF4.Variable datatype is or contains a variable-length datatype.

    Determine if a `netCDF4.Variable` datatype is or contains (in a CompoundType) a
    variable-length datatype. This is needed to determine if filters (compression) can be
    enabled on a variable.
    """
    if datatype is str:
        return True
    if isinstance(datatype, VLType):
        return True
    if isinstance(datatype, CompoundType):
        return _struct_dtype_has_vlen(datatype.dtype)
    return False


def _struct_dtype_has_vlen(dtype: np.dtype) -> bool:
    """Check if a structured dtype include a flexible-length dtype in any of its fields.

    Raises a `TypeError` if dtype is not a structured dtype.
    """
    if not dtype.names:
        raise TypeError("_struct_dtype_has_vlen only works on structured datatypes.")
    for fieldname in dtype.names:
        if dtype[fieldname].itemsize == 0:
            # flexible-length types (e.g. str) have an itemsize of 0
            return True
        if dtype[fieldname].names:  # nested structured datatype
            return _struct_dtype_has_vlen(dtype[fieldname])
    return False


def duplicate_var(
    template_var: Variable,
    new_var_name: str,
    new_ds: Dataset,
    *,
    try_zlib: bool = True,
    **createVar_kwargs: Any,
) -> None:
    """Duplicate a variable in a dataset based on an existing variable in the dataset.

    The filters and attributes of the new variable may me modified.

    Parameters
    ----------
    template_var
        Variable to use as a template for the new variable
    new_var_name
        Name for the new variable
    new_ds
        Dataset in which to create the new variable
    try_zlib
        Override any compression settings in the template variable and create this
        variable with some standard zlib compression settings. Does nothing regarding
        chunksizes.
    **createVar_kwargs
        Additional keyword arguments to pass to `new_ds.createVariable()`, possibly
        overriding values from the template variable or the standard compression settings.
        A common keyword argument to provide is `chunksizes` to set the chunk size for
        each dimension of the variable.

    """
    var_kwargs = get_createVar_kwargs(template_var)
    if try_zlib and not contains_vlen(template_var.datatype):
        # enable zlib compression and checksumming for all fixed-size variables.
        var_kwargs["zlib"] = True
        var_kwargs["contiguous"] = False  # required when using filters
        var_kwargs["complevel"] = 6
        var_kwargs["fletcher32"] = True
    var_kwargs |= createVar_kwargs
    # Create the var - note that it's OK to use var.dimensions as this is the
    # dimension _names_, not Dimension objects
    trace(
        logger,
        "Creating variable %s with datatype %s, dimensions %s and kwargs %s",
        new_var_name,
        template_var.datatype,
        template_var.dimensions,
        var_kwargs,
    )
    ds_var = new_ds.createVariable(
        new_var_name, template_var.datatype, template_var.dimensions, **var_kwargs
    )
    # Copy the variable attributes.
    for attrname in template_var.ncattrs():
        if attrname != "_FillValue":
            ds_var.setncattr(attrname, template_var.getncattr(attrname))
