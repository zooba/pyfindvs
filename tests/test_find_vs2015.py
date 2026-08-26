"""Tests for pyfindvs._find_vs2015 (the legacy, registry-based VS2015
finder), including malformed/missing registry metadata scenarios.
"""

import os.path

import pyfindvs._find_vs2015 as find_vs2015


def _fake_join_and_glob(base, pattern):
    # Mirrors the real _join_and_glob's *shape* (os.path.join then return
    # as-is) using the current platform's separator, so that downstream
    # os.path.dirname()/os.path.join() calls in the code under test behave
    # the same way they would on Windows, regardless of what platform the
    # tests happen to run on.
    return os.path.join(base, *pattern.split('\\')) if pattern else base


def _drive_path(*parts):
    return os.path.join('C:' + os.sep, *parts)


def test_no_vs2015_installed_returns_empty(fake_registry):
    # Base registry has Software\Microsoft but nothing about VS2015.
    assert find_vs2015.findall() == []


def test_vs2015_found_when_msenv_present(fake_registry, monkeypatch):
    root = _drive_path('Program Files (x86)', 'Microsoft Visual Studio 14.0')

    fake_registry['HKEY_LOCAL_MACHINE']['subkeys']['Software']['subkeys']['Microsoft']['subkeys'] = {
        'VisualStudio': {'subkeys': {'SxS': {'subkeys': {'VS7': {
            'values': {'14.0': (root + os.sep, 2)},  # REG_EXPAND_SZ
        }}}}},
    }

    monkeypatch.setattr(find_vs2015, '_join_and_glob', _fake_join_and_glob)
    monkeypatch.setattr(find_vs2015, 'getversion', lambda path: '14.0.25431.01')

    instances = find_vs2015.findall()
    assert len(instances) == 1
    inst = instances[0]
    assert inst.instance_id == 'vs2015'
    assert inst.name == 'Visual Studio 2015'
    assert inst.version == '14.0.25431.01'
    assert inst.version_info == (14, 0, 25431, 1)
    # msenv.dll itself is only used to compute the version/root, and must
    # not leak into the returned known_paths.
    assert 'msenv.dll' not in inst.known_paths
    assert inst.known_paths['devenv.exe'] == os.path.join(root, 'Common7', 'IDE', 'devenv.exe')
    assert inst.path == root


def test_vs2015_malformed_registry_value_ignored(fake_registry):
    # A value of the wrong shape/type (e.g. an int instead of a path) is
    # falsy/unusable and must be treated as "not found" rather than
    # crashing discovery.
    fake_registry['HKEY_LOCAL_MACHINE']['subkeys']['Software']['subkeys']['Microsoft']['subkeys'] = {
        'VisualStudio': {'subkeys': {'SxS': {'subkeys': {'VS7': {
            'values': {'14.0': (0, 4)},  # REG_DWORD, not a path at all
        }}}}},
    }
    assert find_vs2015.findall() == []


def test_vs2015_missing_msbuild_subkey_does_not_crash(fake_registry, monkeypatch):
    # Only the msenv.dll/devenv.exe key is present; MSBuild.ToolsVersions
    # and VC7 subkeys are entirely absent (as if a partial/repaired
    # install left the registry in an inconsistent state).
    root = _drive_path('VS2015')
    fake_registry['HKEY_LOCAL_MACHINE']['subkeys']['Software']['subkeys']['Microsoft']['subkeys'] = {
        'VisualStudio': {'subkeys': {'SxS': {'subkeys': {'VS7': {
            'values': {'14.0': (root, 1)},  # REG_SZ
        }}}}},
    }
    monkeypatch.setattr(find_vs2015, '_join_and_glob', _fake_join_and_glob)
    monkeypatch.setattr(find_vs2015, 'getversion', lambda path: '14.0.25123.0')

    instances = find_vs2015.findall()
    assert len(instances) == 1
    assert 'msbuild.exe' not in instances[0].known_paths
    assert 'vcvarsall.bat' not in instances[0].known_paths
