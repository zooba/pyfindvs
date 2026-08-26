"""Tests for pyfindvs._find_winsdk (the registry-based Windows 10 SDK
finder), including malformed/missing installation metadata.
"""

import os.path

import pyfindvs._find_winsdk as find_winsdk


def _fake_join_and_glob(base, pattern):
    return os.path.join(base, *pattern.split('\\')) if pattern else base


def test_no_winsdk_installed_returns_empty(fake_registry):
    assert find_winsdk.findall() == []


def test_winsdk_found_when_kitsroot_present(fake_registry, monkeypatch):
    root = os.path.join('C:', 'Program Files (x86)', 'Windows Kits', '10') + os.sep

    fake_registry['HKEY_LOCAL_MACHINE']['subkeys']['Software']['subkeys']['Microsoft']['subkeys'] = {
        'Windows Kits': {'subkeys': {'Installed Roots': {
            'values': {'KitsRoot10': (root, 2)},  # REG_EXPAND_SZ
        }}},
    }

    monkeypatch.setattr(find_winsdk, '_join_and_glob', _fake_join_and_glob)

    instances = find_winsdk.findall()
    assert len(instances) == 1
    inst = instances[0]
    assert inst.instance_id == 'winsdk10'
    assert inst.name == 'Windows 10 SDK'
    assert set(['WinSDK', 'WinSDK.10']) <= inst.packages
    assert 'WinSDK_Root' not in inst.known_paths
    assert 'WinSDK_Version' not in inst.known_paths
    assert inst.path == root.rstrip('\\/')


def test_winsdk_missing_version_glob_returns_empty(fake_registry, monkeypatch):
    # KitsRoot10 is set, but nothing matches the Include\* version glob
    # (e.g. a corrupted/partial install with no headers directory) --
    # _join_and_glob would return '' for WinSDK_Version, so no instance
    # should be reported.
    root = os.path.join('C:', 'Windows Kits', '10')
    fake_registry['HKEY_LOCAL_MACHINE']['subkeys']['Software']['subkeys']['Microsoft']['subkeys'] = {
        'Windows Kits': {'subkeys': {'Installed Roots': {
            'values': {'KitsRoot10': (root, 1)},  # REG_SZ
        }}},
    }

    def _join_and_glob_missing_version(base, pattern):
        if pattern and 'Include' in pattern:
            return ''
        return _fake_join_and_glob(base, pattern)

    monkeypatch.setattr(find_winsdk, '_join_and_glob', _join_and_glob_missing_version)

    assert find_winsdk.findall() == []


def test_winsdk_malformed_registry_value_ignored(fake_registry):
    fake_registry['HKEY_LOCAL_MACHINE']['subkeys']['Software']['subkeys']['Microsoft']['subkeys'] = {
        'Windows Kits': {'subkeys': {'Installed Roots': {
            'values': {'KitsRoot10': (0, 4)},  # REG_DWORD, not a path
        }}},
    }
    assert find_winsdk.findall() == []
