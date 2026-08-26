pyfindvs
========

Python client library for locating Visual Studio installations.

Supports Visual Studio 2017, 2019, 2022 and 2026 (major versions 15.x-18.x)
through the Setup Configuration API, as well as the older VS2015 (14.x) and
the Windows 10 SDK through the registry. Newer major versions of Visual
Studio are detected automatically, without requiring a code change, as long
as they keep using the installation layout introduced with VS2017.

Usage
=====

The basic functions are `findall`, `findwithall` and `findwithany`.

Calling `findall` will return a (potentially cached) list of currently installed copies of
Visual Studio. Each list item is a `VisualStudioInstance` object with attributes for
`name`, `version`, `version_info` (numeric parts of `version` as a tuple), `path` and
`packages` (a set of the installed components).

Calling `findwithall` or `findwithany` will only return instances of Visual Studio where
all/any of the specified package names are installed.

For example:

```
>>> pyfindvs.findall()
[<VisualStudioInstance at C:\Program Files\Microsoft Visual Studio\2026\Community>,
 <VisualStudioInstance at C:\Program Files (x86)\Microsoft Visual Studio\2017\BuildTools>]

>>> pyfindvs.findwithall('Microsoft.VisualStudio.Component.VC.Tools.x86.x64',
                         'Microsoft.VisualStudio.Component.Windows10SDK.10586')
[<VisualStudioInstance at C:\Program Files (x86)\Microsoft Visual Studio\2017\BuildTools>]

>>> pyfindvs.findwithany('Microsoft.VisualStudio.Component.VC.Tools.x86.x64',
                         'Microsoft.VisualStudio.Component.Windows10SDK.10586')
[<VisualStudioInstance at C:\Program Files\Microsoft Visual Studio\2026\Community>,
 <VisualStudioInstance at C:\Program Files (x86)\Microsoft Visual Studio\2017\BuildTools>]
```

Building
========

This project is built with [pymsbuild](https://pypi.org/project/pymsbuild), configured in
`_msbuild.py`. On Windows, `pip install .` (or `pip wheel .`) will detect and use your
Visual Studio installation automatically; the `Microsoft.VisualStudio.Setup.Configuration.Native`
NuGet package (used to build the native `_helper` extension) is fetched automatically the
first time you build.

Requires Python 3.8 or later (tested through 3.15).

Releases are published to PyPI automatically by `.github/workflows/release.yml` whenever a
tag matching `X.Y.Z` is pushed; the tag name becomes the package version. The sdist/wheel are
built on Windows (a `build` job, since the native `_helper` extension needs MSVC), then
published from a separate `publish` job on Ubuntu using
[PyPI's Trusted Publisher](https://docs.pypi.org/trusted-publishers/) support (OIDC) rather
than an API token, scoped to its own `pypi` GitHub Environment.

Testing
=======

Unit tests live in `tests/` and run with `pytest`. They do not require Visual Studio (or even
Windows) to be installed -- native/registry-backed pieces are replaced with lightweight fakes
so that version parsing, path resolution and filtering logic can be verified directly.

