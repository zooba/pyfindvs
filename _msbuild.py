#-------------------------------------------------------------------------
# Copyright (c) Steve Dower
# All rights reserved.
#
# Distributed under the terms of the MIT License
#-------------------------------------------------------------------------

"""pymsbuild build configuration for pyfindvs.

Run ``python -m pymsbuild`` (or ``pip wheel .`` / ``pip install .``) to
build. See https://pypi.org/project/pymsbuild for details of the format.
"""

import os
import sys

from pathlib import Path

from pymsbuild import *

ROOT = Path(__file__).resolve().parent

__version__ = '0.7.0'

METADATA = {
    "Metadata-Version": "2.2",
    "Name": "pyfindvs",
    "Version": __version__,
    "Author": "Steve Dower",
    "Author-email": "steve.dower@python.org",
    "Project-url": [
        "Homepage, https://github.com/zooba/pyfindvs",
        "Source, https://github.com/zooba/pyfindvs",
        "Issues, https://github.com/zooba/pyfindvs/issues",
    ],
    "Summary": "Python module for locating Visual Studio",
    "Description": File("README.md"),
    "Description-Content-Type": "text/markdown",
    "Keywords": "visualstudio,msvc,msbuild,setup-configuration",
    "Classifier": [
        "Development Status :: 4 - Beta",
        "Environment :: Win32 (MS Windows)",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: 3.15",
        "Programming Language :: Python :: 3 :: Only",
    ],
    "Requires-Python": ">=3.8",
    "Requires-Dist": [],
}


def init_METADATA():
    # Releases are published from a tag push (see
    # .github/workflows/release.yml), and the tag name becomes the
    # package version -- same convention as pymsbuild's own _msbuild.py.
    # Only apply this for an actual tag ref; ignore branch/PR refs (e.g.
    # from the test workflow) so the version isn't silently overwritten
    # with something like "master".
    ghref = os.getenv("GITHUB_REF")
    if ghref and ghref.startswith("refs/tags/"):
        METADATA["Version"] = ghref[len("refs/tags/"):]

# Filled in for real (with the include/lib directories of the NuGet
# package below) by init_PACKAGE, once we know whether we're building a
# wheel (native module needed) or an sdist (no native build required).
_SETUP_CONFIG_INCLUDE = ItemDefinition("ClCompile")
_SETUP_CONFIG_LIB = ItemDefinition("Link")

PACKAGE = Package(
    "pyfindvs",
    PyFile("pyfindvs/*.py"),

    PydFile(
        "_helper",
        _SETUP_CONFIG_INCLUDE,
        _SETUP_CONFIG_LIB,
        CSourceFile("pyfindvs/pyfindvs.cpp"),
    ),

    Package(
        "msbuildcompiler",
        PyFile("pyfindvs/msbuildcompiler/*.py"),
        File("pyfindvs/msbuildcompiler/*.template"),
    ),

    File("entry_points.txt", IncludeInDistinfo=True),
)


# The Setup Configuration COM API (used by pyfindvs.cpp to discover
# VS2017/2019/2022/2026+ instances) ships as native headers/libs in this
# NuGet package. There is no C++ package manager configured for this
# project, so we fetch it here, exactly as the previous setup.py did.
_SETUP_CONFIG_PACKAGE_NAME = "Microsoft.VisualStudio.Setup.Configuration.Native"
_SETUP_CONFIG_PACKAGE_VERSION = "3.14.2075"


def _ensure_setup_configuration_package():
    packages_dir = ROOT / "packages"
    package_dir = packages_dir / "{}.{}".format(
        _SETUP_CONFIG_PACKAGE_NAME, _SETUP_CONFIG_PACKAGE_VERSION
    )
    if not package_dir.is_dir():
        from shutil import copyfileobj
        from tempfile import TemporaryDirectory
        from urllib.request import urlopen
        from zipfile import ZipFile

        package_url = "https://www.nuget.org/api/v2/package/{}/{}".format(
            _SETUP_CONFIG_PACKAGE_NAME, _SETUP_CONFIG_PACKAGE_VERSION
        )
        print("Fetching {} from NuGet...".format(_SETUP_CONFIG_PACKAGE_NAME))
        packages_dir.mkdir(exist_ok=True)
        with urlopen(package_url) as response, TemporaryDirectory(dir=packages_dir) as temp_dir:
            archive_path = Path(temp_dir) / "package.nupkg"
            with archive_path.open("wb") as archive:
                copyfileobj(response, archive)
            with ZipFile(archive_path) as package:
                extract_dir = Path(temp_dir) / package_dir.name
                extract_dir.mkdir()
                extract_root = os.path.abspath(extract_dir)
                for member in package.infolist():
                    member_path = member.filename.replace("/", os.sep)
                    destination = os.path.abspath(os.path.join(extract_root, member_path))
                    try:
                        is_within_extract_dir = (
                            os.path.commonpath((extract_root, destination)) == extract_root
                        )
                    except ValueError:
                        is_within_extract_dir = False
                    if not is_within_extract_dir:
                        raise RuntimeError("NuGet package contains an invalid path")
                    package.extract(member, extract_dir)
            extract_dir.rename(package_dir)
    if not package_dir.is_dir():
        raise RuntimeError("failed to acquire NuGet package {}".format(_SETUP_CONFIG_PACKAGE_NAME))
    return package_dir


def init_PACKAGE(tag=None):
    # Only required for wheel (i.e. real native) builds; sdists just need
    # the source files, not the NuGet package.
    if not tag or sys.platform != "win32":
        return

    native_dir = _ensure_setup_configuration_package() / "lib" / "native"
    include_dir = native_dir / "include"
    # $(Platform) is resolved by MSBuild itself (Win32/x64/ARM64), so the
    # correct one is always picked regardless of what we build on.
    lib_dir = native_dir / "v141" / "$(Platform)"

    _SETUP_CONFIG_INCLUDE.options["AdditionalIncludeDirectories"] = Prepend("{};".format(include_dir))
    _SETUP_CONFIG_LIB.options["AdditionalLibraryDirectories"] = Prepend("{};".format(lib_dir))
