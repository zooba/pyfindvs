"""Tests for the NuGet library directory selection in ``_msbuild.py``.

The Setup Configuration NuGet package ships its import libraries in
``lib/native/v141/{x86,x64,arm64}``, which are not the same names as the
MSBuild ``$(Platform)`` values, so ``init_PACKAGE`` maps them from the
wheel tag it is given.
"""

import importlib.util
import sys

from pathlib import Path

import pytest

pytest.importorskip('pymsbuild')

_SPEC = importlib.util.spec_from_file_location(
    'pyfindvs_msbuild_config',
    Path(__file__).resolve().parent.parent / '_msbuild.py',
)
_msbuild = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_msbuild)


@pytest.fixture(autouse=True)
def windows_build(tmp_path, monkeypatch):
    """Pretends we're building on Windows against an already-downloaded
    copy of the NuGet package."""
    monkeypatch.setattr(sys, 'platform', 'win32')
    monkeypatch.setattr(
        _msbuild, '_ensure_setup_configuration_package', lambda: tmp_path
    )
    monkeypatch.setattr(_msbuild._SETUP_CONFIG_INCLUDE, 'options', {})
    monkeypatch.setattr(_msbuild._SETUP_CONFIG_LIB, 'options', {})
    return tmp_path


def _lib_dirs():
    return str(_msbuild._SETUP_CONFIG_LIB.options['AdditionalLibraryDirectories'])


@pytest.mark.parametrize('platform_tag, expected', [
    ('win32', 'x86'),
    ('win_amd64', 'x64'),
    ('win_arm64', 'arm64'),
])
def test_lib_dir_matches_platform(windows_build, platform_tag, expected):
    _msbuild.init_PACKAGE('cp313-cp313-' + platform_tag)
    expected_dir = windows_build / 'lib' / 'native' / 'v141' / expected
    assert str(expected_dir) in _lib_dirs()


def test_unknown_platform_is_an_error():
    with pytest.raises(RuntimeError):
        _msbuild.init_PACKAGE('cp313-cp313-linux_x86_64')


def test_sdist_does_not_need_the_package():
    assert _msbuild.init_PACKAGE(None) is None
    assert 'AdditionalLibraryDirectories' not in _msbuild._SETUP_CONFIG_LIB.options
