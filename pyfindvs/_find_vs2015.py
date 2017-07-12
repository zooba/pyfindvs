#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation
# All rights reserved.
#
# Distributed under the terms of the MIT License
#-------------------------------------------------------------------------

import os.path
from . import VisualStudioInstance, _join_and_glob, _PACKAGE_MAP
from ._helper import getversion
from .reghelper import HKLM_32

_VS2015_KEYS = [
    # We include msenv.dll to find the version number, but remove it before returning
    ('msenv.dll', r'VisualStudio\SxS\VS7', '14.0', r'Common7\IDE\msenv.dll'),

    ('msbuild.exe', r'MSBuild\ToolsVersions\14.0', 'MSBuildToolsPath', 'msbuild.exe'),
    ('msbuild.exe_x64', r'MSBuild\ToolsVersions\14.0', 'MSBuildToolsPath', r'amd64\msbuild.exe'),
    ('devenv.exe', r'VisualStudio\SxS\VS7', '14.0', r'Common7\IDE\devenv.exe'),
    ('vcvarsall.bat', r'VisualStudio\SxS\VC7', '14.0', r'vcvarsall.bat'),
    ('vcruntime140.dll', r'VisualStudio\SxS\VC7', '14.0', r'redist\x86\Microsoft.VC140.CRT\vcruntime140.dll'),
    ('vcruntime140.dll_x64', r'VisualStudio\SxS\VC7', '14.0', r'redist\x64\Microsoft.VC140.CRT\vcruntime140.dll'),
]

for tool in ['cl.exe', 'link.exe', 'lib.exe']:
    _VS2015_KEYS.extend([
        (tool, r'VisualStudio\SxS\VC7', '14.0', 'bin\\' + tool),
        (tool + '_x64', r'VisualStudio\SxS\VC7', '14.0', 'bin\\amd64\\' + tool),
        (tool + '_x86_64', r'VisualStudio\SxS\VC7', '14.0', 'bin\\x86_amd64\\' + tool),
    ])

def findall():
    known_paths = {}
    value_cache = {}
    with HKLM_32[r'Software\Microsoft'] as root:
        for key, subkey, value_name, glob in _VS2015_KEYS:
            try:
                v = value_cache[subkey, value_name]
            except KeyError:
                try:
                    with root[subkey] as sk:
                        value_cache[subkey, value_name] = v = sk.get_value(value_name)
                except OSError:
                    value_cache[subkey, value_name] = v = None

            if v:
                path = _join_and_glob(v, glob)
                if path:
                    known_paths[key] = path

    msenv = known_paths.pop('msenv.dll', None)
    if not msenv:
        return []

    packages = (p for p in (_PACKAGE_MAP.get(key) for key in known_paths) if p)

    root_path = os.path.dirname(os.path.dirname(os.path.dirname(msenv)))

    return [VisualStudioInstance(
        'vs2015',
        'Visual Studio 2015',
        getversion(msenv),
        root_path,
        packages,
        known_paths
    )]
