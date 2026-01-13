import contextlib
import functools
import os
import tempfile

import numpy as np
import pytest

from nc4_tools import ncdataset
from nc4_tools.ncdataset import (
    DatasetClosedError,
    NCDataset,
    NCDatasetError,
    NonScalarVariableError,
)

TEST_FILE = tempfile.NamedTemporaryFile(suffix=".nc", delete=False).name

# always uses TEST_FILE
_NCDataset = functools.partial(NCDataset, TEST_FILE)


@pytest.fixture(autouse=True)
def rm_example():
    """Always remove EXAMPLE_FILE after every test in this module"""
    yield
    with contextlib.suppress(FileNotFoundError):
        os.remove(TEST_FILE)


@pytest.fixture(autouse=True)
def reset_module_automask():
    """Always reset ncdataset.auto_mask to False (the module default) after every test in
    this module."""
    yield
    ncdataset.auto_mask = False


def test_reopen():
    """Test that a closed dataset can be reopened"""
    with _NCDataset(mode="w") as ds:
        ds.createVariable("var1", int)
        ds["var1"][()] = 2
    with ds:
        assert ds["var1"][()] == 2


def test_nested_context():  # sourcery skip: extract-duplicate-method
    """Text that a dataset is only closed when the outermost context manager exits."""
    ds = _NCDataset("w", keepopen=False)
    with ds:
        with ds:
            assert ds.isopen()
        assert ds.isopen()
    assert not ds.isopen()

    ds = _NCDataset("w", keepopen=True)
    with ds:  # already open, but entering the context manager
        with ds:
            assert ds.isopen()
        assert ds.isopen()
    # exiting outermost context manager closes, even though it was open when we started.
    assert not ds.isopen()


def test_clobber_change():
    """Prove clobber functionality (see comments)"""
    # prove default after opening in write mode is opening in append mode
    with _NCDataset("w") as ds:
        ds.createVariable("var1", int)
    with ds:
        assert ds.nc_kwargs["mode"] == "a"
        assert "var1" in ds.variables
    # prove that next reopen is still in append mode
    with ds:
        assert ds.nc_kwargs["mode"] == "a"
        assert "var1" in ds.variables
    # prove clobber is reset on reopening
    with ds(mode="w", clobber=True):
        # Shouldn't raise an error since the old datset is clobbered
        ds.createVariable("var1", int)
    assert not ds.nc_kwargs["clobber"]
    with pytest.raises(OSError, match="NC_NOCLOBBER"):  # raised from netCDF4
        ds.open(mode="w")


def test_get_scalar():
    """Test the get_scalar_var function"""
    with _NCDataset("w") as ds:
        dim1 = ds.createDimension("dim1", 10)
        ds.createVariable("var1", float, ())
        ds.createVariable("var2", float, (dim1,))
        ds["var1"][()] = 23.1
        # gets the scalar var
        assert ds.get_scalar_var("var1") == pytest.approx(23.1)
        # raises if the variable is not a scalar
        with pytest.raises(NonScalarVariableError):
            ds.get_scalar_var("var2")
        # raises IndexError if the variable doesn't exist and no default is provided
        with pytest.raises(IndexError):
            ds.get_scalar_var("var3")
        # no error if the variable doesn't exist but a default is provided
        assert ds.get_scalar_var("var3", default=4) == 4


def test_auto_mask():  # sourcery skip: extract-method
    """Test set_auto_mask functionality"""
    # set up the dataset
    with _NCDataset(mode="w") as ds:
        ds.createVariable("var1", int)

    # first check the default module-wide setting is False
    assert not ncdataset.auto_mask
    with ds(mode="r"):
        assert not ds.auto_mask  # from module-wide setting (contrary to superclass)
        assert not np.ma.is_masked(ds["var1"][()])
        ds.set_auto_mask(True)
        assert np.ma.is_masked(ds["var1"][()])
    # dataset closed
    with ds:
        # Reopened -- var1 should return a MaskedContant
        assert np.ma.is_masked(ds["var1"][()])

    # test changing module-wide with new dataset
    ncdataset.auto_mask = True
    with _NCDataset(mode="r") as ds:
        assert np.ma.is_masked(ds["var1"][()])


def test_ds_closed():  # sourcery skip: extract-method
    """Test that an instructive error is raised when trying to access the dataset and it
    is closed"""
    # use failfast to ensure that unavailable variable access is immediately caught
    with _NCDataset(mode="w") as ds:
        ds.createVariable("var1", int)
        ds["var1"][()] = 3
        ds.someattr = "someattr"
        # these run fine when the dataset is open
        _ = str(ds["var1"][()])
        _ = str(ds.variables)
        _ = str(ds.dimensions)
        _ = str(ds.groups)
        _ = ds.someattr
        assert ds.someattr == "someattr"
    with pytest.raises(DatasetClosedError):
        _ = str(ds["var1"][()])
    with pytest.raises(DatasetClosedError):
        _ = str(ds.variables)
    with pytest.raises(DatasetClosedError):
        _ = str(ds.dimensions)
    with pytest.raises(DatasetClosedError):
        _ = str(ds.groups)
    with pytest.raises(DatasetClosedError):
        _ = ds.someattr


def test_change_calling_params():
    """Make sure we can only change calling params when the dataset is closed"""
    with _NCDataset("w") as ds:
        ds.createVariable("var1", int)
        with pytest.raises(NCDatasetError):
            ds.update_params(mode="r")
    ds.update_params(mode="r")
    with ds:
        # show that it's read-only now
        with pytest.raises(RuntimeError, match="HDF error"):
            ds["var1"][0] = 3
        with pytest.raises(RuntimeError, match="Write to read only"):
            ds.createVariable("var2", int)


def test_ds_str():
    """Test that str(dataset) ends with '(closed)' if it's closed"""
    ds = _NCDataset("w", keepopen=False)
    assert str(ds).endswith("(closed)")
