"""Tests for pyfindvs._get_known_paths, the code that maps a discovered
Visual Studio instance's install path + version into a dict of resolved
tool paths (msbuild.exe, cl.exe, devenv.exe, ...).

This is the piece that historically only understood Visual Studio 2017
(major version 15); these tests confirm that VS2019 (16.x), VS2022
(17.x) and VS2026 (18.x) instances now resolve their known paths too,
using the same glob-based, version-folder-agnostic templates.
"""

import pyfindvs


ALL_PACKAGES = frozenset(pyfindvs._PACKAGE_MAP.values())


def _fake_join_and_glob(paths):
    """Returns a _join_and_glob stand-in that resolves any (base, pattern)
    pair present in `paths` (a dict keyed by pattern) and otherwise acts
    as if nothing was found, without touching the real filesystem."""
    def _join_and_glob(base, pattern):
        if not pattern:
            return base
        return paths.get(pattern, '')
    return _join_and_glob


def test_known_paths_empty_for_missing_path():
    assert pyfindvs._get_known_paths('', (17, 0), ALL_PACKAGES) == {}


def test_known_paths_empty_for_short_version_info():
    assert pyfindvs._get_known_paths(r'C:\VS', (17,), ALL_PACKAGES) == {}
    assert pyfindvs._get_known_paths(r'C:\VS', (), ALL_PACKAGES) == {}


def test_known_paths_empty_below_vs2017(monkeypatch):
    # Older (pre-"vNext") installs, e.g. VS2015 (14.x), are handled by
    # _find_vs2015 instead, so the COM-based resolver should not attempt
    # to resolve any paths for them.
    monkeypatch.setattr(pyfindvs, '_join_and_glob', _fake_join_and_glob({
        r'MSBuild\*\Bin\msbuild.exe': r'C:\VS\MSBuild\14.0\Bin\msbuild.exe',
    }))
    assert pyfindvs._get_known_paths(r'C:\VS', (14, 0), ALL_PACKAGES) == {}


def _instance_paths(version_info, packages=ALL_PACKAGES):
    resolved = {
        r'MSBuild\*\Bin\msbuild.exe': r'C:\VS\MSBuild\Current\Bin\msbuild.exe',
        r'MSBuild\*\Bin\amd64\msbuild.exe': r'C:\VS\MSBuild\Current\Bin\amd64\msbuild.exe',
        r'Common7\IDE\devenv.exe': r'C:\VS\Common7\IDE\devenv.exe',
        r'VC\Auxiliary\Build\vcvarsall.bat': r'C:\VS\VC\Auxiliary\Build\vcvarsall.bat',
        'VC\\Tools\\MSVC\\*\\bin\\HostX86\\x86\\cl.exe': r'C:\VS\VC\Tools\MSVC\14.44\bin\HostX86\x86\cl.exe',
        'VC\\Tools\\MSVC\\*\\bin\\HostX64\\x64\\cl.exe': r'C:\VS\VC\Tools\MSVC\14.44\bin\HostX64\x64\cl.exe',
    }
    import unittest.mock
    with unittest.mock.patch.object(pyfindvs, '_join_and_glob', _fake_join_and_glob(resolved)):
        return pyfindvs._get_known_paths(r'C:\VS', version_info, packages)


def test_vs2017_known_paths_resolved():
    paths = _instance_paths((15, 9, 28307, 665))
    assert paths['msbuild.exe'] == r'C:\VS\MSBuild\Current\Bin\msbuild.exe'
    assert paths['devenv.exe'] == r'C:\VS\Common7\IDE\devenv.exe'
    assert paths['cl.exe'] == r'C:\VS\VC\Tools\MSVC\14.44\bin\HostX86\x86\cl.exe'


def test_vs2019_known_paths_resolved():
    paths = _instance_paths((16, 11, 33));
    assert paths['msbuild.exe']
    assert paths['cl.exe_x64']


def test_vs2022_known_paths_resolved():
    paths = _instance_paths((17, 9, 34728, 123))
    assert paths['msbuild.exe']
    assert paths['devenv.exe']
    assert paths['vcvarsall.bat']


def test_vs2026_known_paths_resolved():
    # The new/current generation of Visual Studio (2026, major version 18)
    # must be resolved using the same rules as 2017/2019/2022.
    paths = _instance_paths((18, 0, 1000, 1))
    assert paths['msbuild.exe'] == r'C:\VS\MSBuild\Current\Bin\msbuild.exe'
    assert paths['cl.exe'] == r'C:\VS\VC\Tools\MSVC\14.44\bin\HostX86\x86\cl.exe'
    assert paths['cl.exe_x64'] == r'C:\VS\VC\Tools\MSVC\14.44\bin\HostX64\x64\cl.exe'


def test_future_major_version_still_resolved():
    # Anything at or beyond the current "vNext" layout (>= 15) should keep
    # working without needing code changes for each new VS release.
    paths = _instance_paths((19, 0))
    assert paths['msbuild.exe']


def test_packages_filter_removes_ungranted_tools():
    # cl.exe/devenv.exe/msbuild.exe/vcvarsall.bat are all gated on their
    # mapped package IDs being present in the instance's package set; if
    # the corresponding workload isn't installed, the path should not be
    # resolved, even though the file glob would match. This holds for
    # VS2026/18.x exactly as it always has for VS2017.
    paths = _instance_paths((18, 0), packages=frozenset())
    assert 'cl.exe' not in paths
    assert 'cl.exe_x64' not in paths
    assert 'devenv.exe' not in paths
    assert 'msbuild.exe' not in paths
    assert 'vcvarsall.bat' not in paths
    # msbuild.exe_x64 has no package mapping of its own, so it is exempt
    # from filtering (matches pre-existing 2017 behaviour).
    assert paths['msbuild.exe_x64']
