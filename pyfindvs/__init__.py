#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation
# All rights reserved.
#
# Distributed under the terms of the MIT License
#-------------------------------------------------------------------------

__author__ = 'Steve Dower <steve.dower@microsoft.com>'
__version__ = '0.3.0'

import glob
import os.path
import pyfindvs._helper as _helper

__all__ = ['VisualStudioInstance', 'findall', 'findwithall', 'findwithany']

def _make_versioninfo(version):
    r = []
    for b in version.split('.'):
        try:
            r.append(int(b))
        except ValueError:
            break
    return tuple(r)

def _join_and_glob(p1, p2):
    path = os.path.join(p1, p2)
    if '*' not in path:
        return path if os.path.exists(path) else ''
    paths = glob.glob(path)
    return max(paths) if paths else ''

_PACKAGE_MAP = {
    'msbuild.exe': 'Microsoft.Build',
    'devenv.exe': 'Microsoft.VisualStudio.Devenv',
    'vcruntime140.dll': 'Microsoft.VisualCpp.CRT.Redist.X86',
    'vcruntime140.dll_x64': 'Microsoft.VisualCpp.CRT.Redist.X64',
    'vcvarsall.bat': 'Microsoft.VisualCpp.Tools.Core',
    'cl.exe': 'Microsoft.VisualCpp.Tools.HostX86.Target.X86',
    'cl.exe_x64': 'Microsoft.VisualCpp.Tools.HostX64.Target.X64',
    'cl.exe_x86_64': 'Microsoft.VisualCpp.Tools.HostX64.Target.X86',
}

def _get_known_paths(path, version_info, packages):
    if not path or not version_info or len(version_info) < 2:
        return {}

    if version_info[:2] == (15, 0):
        return {k: _join_and_glob(path, v) for k, v in {
            'msbuild.exe': r'MSBuild\*\Bin\msbuild.exe',
            'msbuild.exe_x64': r'MSBuild\*\Bin\amd64\msbuild.exe',
            'devenv.exe': r'Common7\IDE\devenv.exe',
            'vcvarsall.bat': r'VC\Auxiliary\Build\vcvarsall.bat',
            'vcruntime140.dll_x64': r'VC\Redist\MSVC\*\x64\*\vcruntime140.dll',
            'vcruntime140.dll': r'VC\Redist\MSVC\*\x86\*\vcruntime140.dll',
        }.items() if k not in _PACKAGE_MAP or _PACKAGE_MAP[k] in packages}

class VisualStudioInstance:
    def __init__(self, name, version, path, packages, known_paths=None):
        self.name = name
        self.version = version
        self.version_info = _make_versioninfo(version)
        self.path = path
        self.packages = frozenset(packages)
        if known_paths:
            self.known_paths = dict(known_paths)
        else:
            self.known_paths = _get_known_paths(path, self.version_info, self.packages)

    def __repr__(self):
        return "<VisualStudioInstance at {}>".format(self.path)

    def __str__(self):
        return self.name

_findall_cache = None

def findall(reset_cache=False):
    '''findall(reset_cache=False) -> list[VisualStudioInstance]

    Returns a list of installed Visual Studio instances.

    Pass True for *reset_cache* to scan installed instances again.
    Otherwise, cached information may be returned.
    '''
    global _findall_cache
    r = _findall_cache
    if not r or reset_cache:
        r = [VisualStudioInstance(*v) for v in _helper.findall()]
        import pyfindvs._find_vs2015
        r.extend(pyfindvs._find_vs2015.findall())
        _findall_cache = r
    return r

def findwithall(*components):
    '''findwithall(*components) -> list[VisualStudioInstance]

    Returns a list of installed Visual Studio instances with all of
    the specified packages installed.
    '''
    components = set(components)
    return [vs for vs in findall() if len(components & vs.packages) == len(components)]

def findwithany(*components):
    '''findwithany(*components) -> list[VisualStudioInstance]

    Returns a list of installed Visual Studio instances with at least
    one of the specified packages installed.
    '''
    components = set(components)
    return [vs for vs in findall() if components & vs.packages]
