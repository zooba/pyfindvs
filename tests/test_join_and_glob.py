"""Tests for pyfindvs._join_and_glob, the small helper used to resolve
version-wildcarded install paths (e.g. "MSBuild\\*\\Bin\\msbuild.exe") to
a single, highest-sorting concrete path.
"""

import os

import pyfindvs


def test_no_wildcard_existing_path(tmp_path):
    f = tmp_path / "msbuild.exe"
    f.write_text("")
    assert pyfindvs._join_and_glob(str(tmp_path), "msbuild.exe") == str(f)


def test_no_wildcard_missing_path(tmp_path):
    assert pyfindvs._join_and_glob(str(tmp_path), "does-not-exist.exe") == ''


def test_empty_pattern_returns_base(tmp_path):
    assert pyfindvs._join_and_glob(str(tmp_path), '') == str(tmp_path)


def test_wildcard_picks_highest_match(tmp_path):
    # _join_and_glob sorts matches lexicographically (via sorted()), not
    # numerically, so use zero-padded version strings where lexicographic
    # and numeric ordering agree.
    for version in ("14.16.27023", "14.29.30133", "14.09.24215"):
        d = tmp_path / "MSVC" / version / "bin"
        d.mkdir(parents=True)
        (d / "cl.exe").write_text("")
    pattern = os.path.join("MSVC", "*", "bin", "cl.exe")
    result = pyfindvs._join_and_glob(str(tmp_path), pattern)
    assert result.endswith(os.path.join("14.29.30133", "bin", "cl.exe"))


def test_wildcard_no_match_returns_empty(tmp_path):
    pattern = os.path.join("MSVC", "*", "bin", "cl.exe")
    assert pyfindvs._join_and_glob(str(tmp_path), pattern) == ''
