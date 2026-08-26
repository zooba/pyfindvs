"""Tests for version-string parsing (VisualStudioInstance.version_info)."""

import pyfindvs


def test_basic_version():
    assert pyfindvs._make_versioninfo('15.9.28307.665') == (15, 9, 28307, 665)


def test_vs2019_version():
    assert pyfindvs._make_versioninfo('16.11.32')[0] == 16


def test_vs2022_version():
    assert pyfindvs._make_versioninfo('17.9.34728.123')[0] == 17


def test_vs2026_version():
    # Visual Studio "18.0"/2026 uses the same dotted-integer version scheme
    # as every release since VS2017.
    assert pyfindvs._make_versioninfo('18.0.1000.1') == (18, 0, 1000, 1)


def test_empty_version():
    assert pyfindvs._make_versioninfo('') == ()


def test_malformed_version_stops_at_first_non_integer():
    # Some SDK/registry version strings include non-numeric suffixes
    # (e.g. pre-release tags); parsing should stop rather than raise.
    assert pyfindvs._make_versioninfo('14.0.rc1.2') == (14, 0)


def test_fully_malformed_version():
    assert pyfindvs._make_versioninfo('not-a-version') == ()
