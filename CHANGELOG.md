# Changelog

## Unreleased

- Added `Programming Language :: Python :: 3.14` / `3.15` classifiers; the
  test suite now runs against Python 3.8 through 3.15 in CI.
- Added `.github/workflows/test.yml`, a build/test workflow that runs the
  pytest suite (and exercises `pymsbuild`'s sdist/wheel build) across
  Python 3.8-3.15 on Windows (the only platform the native `_helper`
  extension can actually build/run on, so Ubuntu is not tested).
- Added `.github/workflows/release.yml`, a release workflow triggered by
  pushing a version tag (e.g. `0.8.0`); the tag becomes the package
  version (via `_msbuild.py`'s new `init_METADATA()`, matching the
  convention used by `pymsbuild` itself). It builds the sdist/wheel in a
  `build` job on Windows (required, since the native `_helper` extension
  needs MSVC), then a separate `publish` job on Ubuntu downloads those
  artifacts and publishes to PyPI using
  [Trusted Publishers](https://docs.pypi.org/trusted-publishers/) (OIDC),
  scoped to its own `pypi` GitHub Environment, rather than an API token.

## 0.7.0

- Added support for discovering Visual Studio 2019 (16.x), 2022 (17.x) and
  2026 (18.x) installations. Previously, `VisualStudioInstance.known_paths`
  (`msbuild.exe`, `cl.exe`, `devenv.exe`, etc.) were only resolved for VS2017
  (major version 15) instances, even though `findall()` already reported
  newer installations via the Setup Configuration COM API -- their
  `known_paths` were just silently empty. The resolver now recognises any
  installation using the layout introduced by VS2017 (major version >= 15),
  so future Visual Studio releases should continue to work without changes.
- Replaced the `setuptools`/`distutils`-based build (`setup.py`, `setup.cfg`)
  with a [`pymsbuild`](https://pypi.org/project/pymsbuild)-based build
  (`_msbuild.py`, `pyproject.toml`). `pip install .` / `pip wheel .` continue
  to work as before.
- Modernized supported Python versions to 3.8-3.13 (`Requires-Python >=3.8`).
- Updated package metadata (author/contact information).
- Added a `tests/` package-independent unit test suite covering version
  parsing, known-path resolution (including VS2019/2022/2026), malformed or
  missing registry/installation metadata, and `findwithall`/`findwithany`
  filtering.

## 0.6.0

- Previous setuptools-based release.
