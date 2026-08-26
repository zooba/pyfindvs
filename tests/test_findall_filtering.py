"""Tests for findall/findwithall/findwithany, covering caching and
filtering across a mix of VS2017/2019/2022/2026 instances."""

import pyfindvs


def _instance(instance_id, name, version, packages):
    return pyfindvs.VisualStudioInstance(
        instance_id, name, version, r'C:\VS\{}'.format(instance_id),
        packages, known_paths={},
    )


def _raw_tuple(instance_id, name, version, packages):
    # Mirrors what the native _helper.findall() extension returns: plain
    # (id, name, version, path, packages) tuples for pyfindvs.findall() to
    # wrap into VisualStudioInstance objects.
    return (instance_id, name, version, r'C:\VS\{}'.format(instance_id), packages)


INSTANCES = [
    _instance('vs2017', 'Visual Studio 2017', '15.9.28307.665',
              ['Microsoft.Build', 'Microsoft.Component.A']),
    _instance('vs2019', 'Visual Studio 2019', '16.11.33',
              ['Microsoft.Build', 'Microsoft.Component.B']),
    _instance('vs2022', 'Visual Studio 2022', '17.9.34728.123',
              ['Microsoft.Build', 'Microsoft.Component.A', 'Microsoft.Component.B']),
    _instance('vs2026', 'Visual Studio 2026', '18.0.1000.1',
              ['Microsoft.Build', 'Microsoft.Component.C']),
]


def test_findall_returns_cached_list(monkeypatch):
    calls = []

    def fake_findall():
        calls.append(1)
        return [
            _raw_tuple('vs2017', 'Visual Studio 2017', '15.9.28307.665', ['Microsoft.Build']),
            _raw_tuple('vs2026', 'Visual Studio 2026', '18.0.1000.1', ['Microsoft.Build']),
        ]

    monkeypatch.setattr(pyfindvs, '_findall', fake_findall)
    monkeypatch.setattr(pyfindvs, '_findall_cache', None)

    r1 = pyfindvs.findall()
    r2 = pyfindvs.findall()
    assert [i.instance_id for i in r1] == ['vs2017', 'vs2026']
    assert r2 == r1
    assert len(calls) == 1  # second call used the cache

    r3 = pyfindvs.findall(reset_cache=True)
    assert [i.instance_id for i in r3] == ['vs2017', 'vs2026']
    assert len(calls) == 2


def test_findall_swallows_native_oserror(monkeypatch):
    def raising_findall():
        raise OSError("no VS setup API registered")

    monkeypatch.setattr(pyfindvs, '_findall', raising_findall)
    monkeypatch.setattr(pyfindvs, '_findall_cache', None)

    # With an empty (but valid) fake registry, _find_vs2015/_find_winsdk
    # legitimately find nothing either, so the overall result is [].
    assert pyfindvs.findall(reset_cache=True) == []


def test_findwithall_requires_every_component(monkeypatch):
    monkeypatch.setattr(pyfindvs, 'findall', lambda: list(INSTANCES))
    result = pyfindvs.findwithall('Microsoft.Build', 'Microsoft.Component.A')
    assert {i.instance_id for i in result} == {'vs2017', 'vs2022'}


def test_findwithall_no_components_returns_all(monkeypatch):
    monkeypatch.setattr(pyfindvs, 'findall', lambda: list(INSTANCES))
    assert pyfindvs.findwithall() == INSTANCES


def test_findwithany_matches_at_least_one(monkeypatch):
    monkeypatch.setattr(pyfindvs, 'findall', lambda: list(INSTANCES))
    result = pyfindvs.findwithany('Microsoft.Component.B', 'Microsoft.Component.C')
    assert {i.instance_id for i in result} == {'vs2019', 'vs2022', 'vs2026'}


def test_findwithany_no_components_returns_nothing(monkeypatch):
    monkeypatch.setattr(pyfindvs, 'findall', lambda: list(INSTANCES))
    assert pyfindvs.findwithany() == []


def test_vs2026_is_discoverable_alongside_older_versions(monkeypatch):
    monkeypatch.setattr(pyfindvs, 'findall', lambda: list(INSTANCES))
    result = pyfindvs.findwithall('Microsoft.Build')
    versions = sorted(i.version_info[0] for i in result)
    assert versions == [15, 16, 17, 18]
