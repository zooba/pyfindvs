"""Tests for the VisualStudioInstance/WindowsSDKInstance data objects."""

import pyfindvs


def test_basic_construction(monkeypatch):
    monkeypatch.setattr(pyfindvs, '_get_known_paths', lambda *a, **k: {})
    inst = pyfindvs.VisualStudioInstance(
        'vs-id', 'Visual Studio 2026', '18.0.1000.1',
        r'C:\Program Files\Microsoft Visual Studio\2026\Community\\',
        ['Microsoft.Build', 'Microsoft.VisualStudio.Devenv'],
    )
    assert inst.instance_id == 'vs-id'
    assert inst.name == 'Visual Studio 2026'
    assert inst.version == '18.0.1000.1'
    assert inst.version_info == (18, 0, 1000, 1)
    # Trailing path separators are stripped.
    assert inst.path == r'C:\Program Files\Microsoft Visual Studio\2026\Community'
    assert inst.packages == frozenset(['Microsoft.Build', 'Microsoft.VisualStudio.Devenv'])
    assert str(inst) == 'Visual Studio 2026'
    assert repr(inst) == "<VisualStudioInstance at {}>".format(inst.path)


def test_known_paths_passed_through_verbatim():
    # When known_paths is supplied explicitly (as _find_vs2015/_find_winsdk
    # do), it should be used as-is rather than recomputed.
    inst = pyfindvs.VisualStudioInstance(
        'vs2015', 'Visual Studio 2015', '14.0.25431.01', r'C:\VS2015',
        ['Microsoft.Build'], known_paths={'msbuild.exe': r'C:\VS2015\MSBuild\14.0\Bin\msbuild.exe'},
    )
    assert inst.known_paths == {'msbuild.exe': r'C:\VS2015\MSBuild\14.0\Bin\msbuild.exe'}


def test_malformed_version_does_not_raise():
    inst = pyfindvs.VisualStudioInstance(
        'bad', 'Broken Instance', 'not-a-version', r'C:\VS',
        [], known_paths={},
    )
    assert inst.version_info == ()
    assert inst.known_paths == {}


def test_windows_sdk_instance_is_a_visualstudioinstance():
    assert issubclass(pyfindvs.WindowsSDKInstance, pyfindvs.VisualStudioInstance)
