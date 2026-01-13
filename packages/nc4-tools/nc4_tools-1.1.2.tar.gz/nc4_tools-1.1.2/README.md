# nc4-tools

A Python package combining a number of netCDF4 tools useful in various parts of my
workflow.

## Contents  <!-- omit in toc -->

<!--Automatically generated in VSCode with Markdown All in One extension-->
- [`NCDataset` class - An extension of netCDF4.Dataset](#ncdataset-class---an-extension-of-netcdf4dataset)
- [`NCTemplate` class - Dataset creation from a CDL file](#nctemplate-class---dataset-creation-from-a-cdl-file)
- [`NCVarSlicer` class - NetCDF variable slicer](#ncvarslicer-class---netcdf-variable-slicer)
- [`duplicate_var` module - Variable duplication functions](#duplicate_var-module---variable-duplication-functions)

## `NCDataset` class - An extension of netCDF4.Dataset

NCDataset is a subclass of netCDF4.Dataset from the [netCDF4 python
library](http://unidata.github.io/netcdf4-python/netCDF4/index.html#netCDF4.Dataset). The
primary goal of NCDataset has been to make dataset objects reusable--that is to be able to
re-open a closed dataset without re-specifying all the opening arguments.

### Features of NCDataset

- Track dataset path and initialization args (e.g. `mode`, `diskless`, `clobber` etc.) for
  re-use of the dataset object in multiple `with` blocks.
- If the dataset is opened in mulitple `with` blocks, do not close it until leaving the
  outermost `with` block. (Note that even if the Dataset was opened before outermost
  `with` block, it will close when leaving it.)
- Each dataset gets an `auto_mask` attribute that sets the `set_auto_mask` value on the
  dataset when the dataset is opened. By default, this is set to `False` (in contrast with
  `netcdf4.Dataset`), but may be changed by the module-level `auto_mask` variable.
- `keepopen=False` arg allows the dataset object to be created/opened but then closed
  immediately (for later use in a `with` block)
- `update_args(**kwargs)` can be used to update calling keyword args (though not the path
  to the dataset.)
  - `__call__(**kwargs)` calls `update_args(**kwargs)`.
- `open(**kwargs)` opens the dataset (if closed), updating the calling arguments with
  `**kwargs`. If the dataset is already open it does nothing.
- To help prevent accidental dataset overwrite:
  - After initialization, if `mode` is set to `"w"` it is automatically switched to `"a"`
    unless `clobber` is set to `True`.
  - If `clobber` is set to `True` at any point it reverts to `False` after the object is
    closed.
- `__str__` includes the dataset path and the open/closed state in addition to the stuff
  from `netcdf4.Dataset`
- `__getitem__` and `__getattr__` first check if the dataset is open and raise an
  `NCDatasetError` if the dataset is closed. Also, the `dimensions`, `variables`, and
  `groups` properties first check if the dataset is open (unless `failfast` is `False`).

### Examples

```python
>>> from nc4_tools.ncdataset import NCDataset
>>> ds = NCDataset("example.nc", mode="w", keepopen=False, diskless=True, persist=True)
>>> print(ds)
NCDataset[netCDF4.Dataset]
kwargs: {'diskless': True, 'persist': True, 'mode': 'w', 'clobber': False}
(closed)
>>> # Since mode was "w", mode is now automatically "a" (unless we set clobber=False)
>>> # Changes to the kwargs can be made with update_params or just __call__
>>> with ds(diskless=False):
...     # Can augment the netCDF4.Dataset here, just like netCDF4.Dataset
...     ds.createDimension("time", 1024)
...     print(ds)
...
NCDataset[netCDF4.Dataset]
kwargs: {'diskless': False, 'persist': True, 'mode': 'a', 'clobber': False}
<class 'hpx_radar_recorder.ncdataset.NCDataset'>
root group (NETCDF4 data model, file format HDF5):
    dimensions(sizes): time(1024)
    variables(dimensions):
    groups:
>>> # The dataset remains open in nested context managers
>>> print(f"DATASET NOT YET OPENED, ds.isopen(): {ds.isopen()}")
>>> with ds:
...     print(f"OUTER with BLOCK, ds.isopen(): {ds.isopen()}")
...     with ds:
...         print(f"INNER with BLOCK, ds.isopen(): {ds.isopen()}")
...     print(f"EXITED INNER with BLOCK, ds.isopen(): {ds.isopen()}")
... print(f"EXITED OUTER with BLOCK, ds.isopen(): {ds.isopen()}")
DATASET NOT YET OPENED, ds.isopen(): False
OUTER with BLOCK, ds.isopen(): True
INNER with BLOCK, ds.isopen(): True
EXITED INNER with BLOCK, ds.isopen(): True
EXITED OUTER with BLOCK, ds.isopen(): False
```

## `NCTemplate` class - Dataset creation from a CDL file

NCTemplate is a tool to create a template NetCDF4 dataset from a template NetCDF
[CDL](https://docs.unidata.ucar.edu/nug/current/_c_d_l.html) file using the `ncgen`
command-line utility (must be installed on the OS).

NCTemplate is a subclass of [NCDataset](README-ncdataset.md) and thus includes the
context-manager features of that class.

### Usage

```python
from nc4_tools.nctemplate import NCTemplate
with NCTemplate("template.cdl") as tmpl_ds, NCDataset("new_ds.nc", mode="w") as new_ds:
    # Add code here to copy dimensions, variables, and attributes from tmpl_ds to new_ds
    pass
```

## `NCVarSlicer` class - NetCDF variable slicer

### Introduction

In NetCDF schemas such as the [CFRadial Format](https://raw.githubusercontent.com/NCAR/CfRadial/master/old_docs/CfRadialDoc.v1.3.20130701.pdf),
one or more virtual dimensions may exist that subdivide a real dimension. In this
situation, ancillary variables must be provided to specify the start and stop indices in
the real dimension that are the boundaries of each unit in the virtual dimension.

In the case of the CFRadial format the _sweep_ dimension subdivides the _time_ dimension,
and the _sweep\_start\_ray\_index_ and _sweep\_end\_ray\_index_ variables specify the
start and end boundaries, in the _time_ dimension, of each sweep.

Once created, an NCVarSlicer object may be called with `__getitem__` (i.e. `[]`) syntax.
If a single integer index is provided, a single slice object is returned corresponding to
the real dimension bounds of that index in the virtual dimension. If a slice is provided,
then a list of slice objects is returned corresponding to each selected index in the
virtual dimension.

### Example Usage

Given:

- A netCDF file `dataset.nc` with timeseries data
  - Dimensions `time` and `sample_group`
  - Data variable `intensity(time)`
  - Group indexing variables `group_start_index(sample_group)` and
    `group_end_index(sample_group)`

```python
import netCDF4
from nc4_tools.ncvarslice import NCVarSlicer

with netCDF4.Dataset("dataset.nc") as ds:
    group_slicer = NCVarSlicer(ds["group_start_index"], ds["group_end_index"])
    for slc in group_slicer:
        # Work with each sample group
        sample_group_data = ds["intensity"][slc]

```

Equivalent to:

```python
import netCDF4

with netCDF4.Dataset("dataset.nc") as ds:
    for i in range(ds.dimensions["sample_group"].size):
        a = ds["group_start_index"][i]
        b = ds["group_end_index"][i] + 1
        # Work with each sample group
        sample_group_data = ds["intensity"][a:b]

```

#### CfRadial Example

```python
import netCDF4
from nc4_tools.ncvarslice import NCVarSlicer

with netCDF.Dataset("dataset.nc") as ds:
  for slc in NCVarSlicer(ds["sweep_start_ray_index"], ds["sweep_end_ray_index"]):
    # slc is a slice object providing the indices of the time dimension for a single radar
    # sweep
    sweep_power = ds["PWR"][slc][:]  # power values for all rays in sweep (at every range)
    sweep_times = ds["time"][slc]  # timestamps of the rays in the sweep
    sweep_azimuths = ds["azimuth"][slc]  # azimuths of the rays in the sweep

  # Or, to process groups of sweeps:
  sweeps_per_group = 4
  sweep_slicer = NCVarSlicer(ds["sweep_start_ray_index"], ds["sweep_end_ray_index"])
  for slc_i in range(0, len(varslicer), sweeps_per_group):
    sweep_slices = sweep_slicer[slc_i : slc_i + sweeps_per_group]
    ...  # sweep_slices is a list of slices for each sweep in the group
    ...  # perhaps do parallel processing on four sweeps at a time
```

## `duplicate_var` module - Variable duplication functions

### `get_createVar_kwargs()`

Use an existing `netCDF4.Variable` to get the keyword arguments for `netCDF4.Dataset.createVariable` to create an identical variable.

### `contains_vlen()`

Determine if a `netCDF4.Variable.datatype` is or contains (e.g. in a `CompoundType`) a
variable-length datatype. Useful for determining if compression may be applied to a
variable.

### `duplicate_var()`

Use an existing variable ina `netCDF4.Dataset` to create a variable in a new dataset with
the same or similar filters and attributes. I use this to streamline the process of
creating a new dataset based on an `NCTemplate` dataset (which in turn, is based on a
[CDL](https://docs.unidata.ucar.edu/nug/current/_c_d_l.html) file.)
