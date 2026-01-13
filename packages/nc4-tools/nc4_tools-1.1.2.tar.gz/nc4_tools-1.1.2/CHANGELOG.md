# Changelog

All notable changes to the project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--see .vscode/settings.json for TOC settings -->
## Releases <!-- omit in toc -->

<!--Automatically generated in VSCode with Markdown All in One extension-->
- [Unreleased](#unreleased)
- [1.1.2 - 2026-01-06](#112---2026-01-06)
- [1.1.1 - 2024-12-09](#111---2024-12-09)
- [1.1.0 - 2024-11-08](#110---2024-11-08)
- [1.0.0 - 2024-06-05](#100---2024-06-05)
- [Pre-merge releases](#pre-merge-releases)

<!--REM release subheadings: Added, Fixed, Changed, Removed -->

## [Unreleased]

## [1.1.2] - 2026-01-06

- Change to `src/` layout
- Remove `single-version` dep
- Bump dev dependency versions
- Add a linting script that uses ruff and mypy
- Make some fixes and add some docs based on linting

## [1.1.1] - 2024-12-09

### Added

- `py.typed` marker file

## [1.1.0] - 2024-11-08

### Added

#### NCDatset

- Add a test
- `failfast` parameter - If `False`, base class functionality is restored where
  `__getitem__` access of variables and groups of a closed dataset is not an error until
  the Variable or Group data is accessed. Default is `True`, so `__getitem__()`
  immediately fails with `DatasetClosedError` if the dataset is closed.
- Properties `variables`, `dimensions`, and `groups` are subclassed to check if the
  dataset is open.

#### `nc4_tools.duplicate_var`

- New functions `get_createVar_kwargs()`, `contains_vlen()`, and `duplicate_var()`
  primarily for the purpose of creating a new variable in a dataset based on an existing
  variable in (the same or another) dataset.

### Fixed

- `NCDataset` -- changed `__repr__()` to `__str__` to avoid infinite recusion issue (not
  sure why this was happening.)

### Changed

- Updated netCDF4 minimum version to 1.7.2.
- Merged tools READMEs into main README.
- `ncdataset` - Specific subclass of `NCDatasetError` `DatasetClosedError` is raised when
  accessing a closed dataset.
- Changed project management and build system from Poetry to uv with hatchling build
  backend.
- `NCDataset` `mode` parameter now only accepts one of `netCDF4.AccessMode` literals (from
  new types in netCDF4 v1.7.2)

## [1.0.0] - 2024-06-05

Merge of ncdataset, nctemplate, and ncvarslice into nc4-tools

## Pre-merge releases

### [ncdataset-1.0.0] - 2021-02-10

- Major release
- `get_scalar_var` works with string vars.

### [ncdataset-0.3.0] - 2020-11-13

#### Added

- Issue #2: Track context manager depth so the dataset isn't closed until exiting the outermost `with` block.

### [ncdataset-0.2.3] - 2020-11-02

#### Added

- haller pypi upload script
- _version.py

#### Modified

- `__repr__` for `NCDataset` corrected to have `nc_kwargs`.

### [ncdataset-0.2.2_2] - 2020-10-02

#### Added

- CHANGELOG.md
- README.md
- Get version from package version indirectly so `pyproject.toml` is the only home of the version

### ncdataset-0.2.0

#### Changed

- **Breaking Change** - Changed keyword argument `createonly=False` to `keepopen=True`.

### ncdataset-0.1.0

- Initial development

### [nctemplate-1.1.1] - 2024-05-30

- Explicit exports in `__init__.py`
- Update for poetry 1.8.3 compat

### [nctemplate-1.1.0] - 2024-05-28

- Update docstrings
- Minor refactors
- Switch to ruff
- **Min python version 3.8**

### [nctemplate-1.0.1] - 2021-05-13

- Retry ncgen a few times if there is an error

### [nctemplate-1.0.0] - 2021-02-10

- ncdataset nctemplate-v1.0.0

### [nctemplate-0.1.3]

- ncdataset nctemplate-v0.3.0

### [nctemplate-0.1.2]

- Check for `ncgen` on import rather than call.

### [nctemplate-0.1.1] - 2021-02-08

- Raise any `OSError` from `subprocess.run` as NCTemplateError for `ncgen` not installed.

### [nctemplate-0.1.0] - 2020-10-08

- Initial release

### [ncvarslice-1.1.2]

- Added `__iter__` to be officially Iterable.

### [ncvarslice-1.1.1]

- Added `@typing.overload` to `__getitem__`.

### [ncvarslice-1.1.0]

- Added `offline` options (default True) to get slices at init time rather than at `__getitem__` time.

### [ncvarslice-1.0.0]

- Add license and add example to README

### [ncvarslice-0.3.0]

- Use [single-version](https://github.com/hongquan/single-version)  for `__version__`
- Rename `VarSlice` to `NCVarSlicer` (`VarSlice` still works)

### [ncvarslice-0.2.0]

#### Added

- Give a helpful error if the dataset isn't open

#### Modified

- Rename module _varslice.py to varslice.py (no need to be hidden)

### [ncvarslice-0.1.0]

First release.

<!--nc4-tools post-merge comparison links-->
[Unreleased]: https://gitlab.com/osu-nrsg/nc4-tools/-/compare/master...dev
[1.1.2]: https://gitlab.com/osu-nrsg/nc4-tools/-/compare/v1.1.1...v1.1.2
[1.1.1]: https://gitlab.com/osu-nrsg/nc4-tools/-/compare/v1.1.0...v1.1.1
[1.1.0]: https://gitlab.com/osu-nrsg/nc4-tools/-/compare/v1.0.0...v1.1.0
[1.0.0]: https://gitlab.com/osu-nrsg/nc4-tools/-/tags/v1.0.0

<!--ncdataset comparison links-->
[ncdataset-1.0.0]: https://gitlab.com/osu-nrsg/nc4-tools/-/compare/ncdataset-v0.3.0...ncdataset-v1.0.0
[ncdataset-0.3.0]: https://gitlab.com/osu-nrsg/nc4-tools/-/compare/ncdataset-v0.2.3...ncdataset-v0.3.0
[ncdataset-0.2.3]: https://gitlab.com/osu-nrsg/nc4-tools/-/compare/ncdataset-v0.2.2_2...ncdataset-v0.2.3
[ncdataset-0.2.2_2]: https://gitlab.com/osu-nrsg/nc4-tools/-/tree/ncdataset-v0.2.2_2

<!--nctemplate comparison links-->
[nctemplate-1.1.1]: https://gitlab.com/osu-nrsg/nc4-tools/compare/nctemplate-v1.1.0...nctemplate-v1.1.1
[nctemplate-1.1.0]: https://gitlab.com/osu-nrsg/nc4-tools/compare/nctemplate-v1.0.1...nctemplate-v1.1.0
[nctemplate-1.0.1]: https://gitlab.com/osu-nrsg/nc4-tools/compare/nctemplate-v1.0.0...nctemplate-v1.0.1
[nctemplate-1.0.0]: https://gitlab.com/osu-nrsg/nc4-tools/compare/nctemplate-v0.1.3...nctemplate-v1.0.0
[nctemplate-0.1.3]: https://gitlab.com/osu-nrsg/nc4-tools/compare/nctemplate-v0.1.2...nctemplate-v0.1.3
[nctemplate-0.1.2]: https://gitlab.com/osu-nrsg/nc4-tools/compare/nctemplate-v0.1.1...nctemplate-v0.1.2
[nctemplate-0.1.1]: https://gitlab.com/osu-nrsg/nc4-tools/compare/nctemplate-v0.1.0...nctemplate-v0.1.1
[nctemplate-0.1.0]: https://gitlab.com/osu-nrsg/nc4-tools/-/tree/nctemplate-v0.1.0

<!--ncvarslice comparison links-->
[ncvarslice-1.1.2]: https://gitlab.com/osu-nrsg/nc4-tools/-/compare/ncvarslice-v1.1.1...ncvarslice-v1.1.2
[ncvarslice-1.1.1]: https://gitlab.com/osu-nrsg/nc4-tools/-/compare/ncvarslice-v1.1.0...ncvarslice-v1.1.1
[ncvarslice-1.1.0]: https://gitlab.com/osu-nrsg/nc4-tools/-/compare/ncvarslice-v1.0.0...ncvarslice-v1.1.0
[ncvarslice-1.0.0]: https://gitlab.com/osu-nrsg/nc4-tools/-/compare/ncvarslice-v0.3.0...ncvarslice-v1.0.0
[ncvarslice-0.3.0]: https://gitlab.com/osu-nrsg/nc4-tools/-/compare/ncvarslice-v0.2.0...ncvarslice-v0.3.0
[ncvarslice-0.2.0]: https://gitlab.com/osu-nrsg/nc4-tools/-/compare/ncvarslice-v0.1.0...ncvarslice-v0.2.0
[ncvarslice-0.1.0]: https://gitlab.com/osu-nrsg/nc4-tools/-/tree/ncvarslice-v0.1.0
