"""Shared pytest fixtures for the pyfindvs test suite.

The real ``pyfindvs`` package includes a native ``_helper`` extension
(compiled from ``pyfindvs.cpp``) that talks to the Visual Studio Setup
Configuration COM API, plus registry-backed helpers (``_find_vs2015``,
``_find_winsdk``) that rely on the Windows-only ``winreg`` module.

None of that is available (or meaningful) outside of Windows, and even on
Windows we don't want tests to depend on what happens to be installed on
the machine. So before anything imports ``pyfindvs``, we install minimal
stand-ins for the native pieces:

* ``pyfindvs._helper`` -- stubbed with no-op ``findall``/``getversion``.
* ``winreg`` -- replaced with an in-memory fake (see ``fake_winreg.py``)
  when the real module isn't importable.

Individual tests then monkeypatch these stand-ins (or the higher-level
functions built on top of them) to describe whatever scenario they want
to exercise.
"""

import sys
import types

import pytest

import fake_winreg

fake_winreg.install()

if 'pyfindvs._helper' not in sys.modules:
    try:
        import pyfindvs._helper  # noqa: F401
    except ImportError:
        _stub = types.ModuleType('pyfindvs._helper')
        _stub.findall = lambda: []
        _stub.getversion = lambda path: None
        sys.modules['pyfindvs._helper'] = _stub

# A minimal, always-present skeleton mirroring the real Windows registry
# (HKLM\Software\Microsoft always exists), so that _find_vs2015/_find_winsdk
# can be safely exercised without every test having to set this up. With
# nothing else present, both report no instances found -- i.e. this is the
# "nothing installed"/missing-metadata baseline. Tests add whatever extra
# subkeys/values they need on top of this.
BASE_REGISTRY_TREE = {
    'HKEY_LOCAL_MACHINE': {'subkeys': {'Software': {'subkeys': {'Microsoft': {}}}}},
    'HKEY_CURRENT_USER': {'subkeys': {'Software': {'subkeys': {'Microsoft': {}}}}},
}


@pytest.fixture(autouse=True)
def fake_registry():
    """Resets the fake Windows registry to a minimal, empty-but-valid
    baseline before each test, and clears it afterwards."""
    fake_winreg.set_tree({
        'HKEY_LOCAL_MACHINE': {'subkeys': {'Software': {'subkeys': {'Microsoft': {}}}}},
        'HKEY_CURRENT_USER': {'subkeys': {'Software': {'subkeys': {'Microsoft': {}}}}},
    })
    try:
        yield fake_winreg.TREE
    finally:
        fake_winreg.reset()

