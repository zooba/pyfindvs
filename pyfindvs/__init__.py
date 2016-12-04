#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation
# All rights reserved.
#
# Distributed under the terms of the MIT License
#-------------------------------------------------------------------------

__author__ = 'Steve Dower <steve.dower@microsoft.com>'
__version__ = '0.1.1'

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

class VisualStudioInstance:
    def __init__(self, name, version, path, packages):
        self.name = name
        self.version = version
        self.version_info = _make_versioninfo(version)
        self.path = path
        self.packages = frozenset(packages)

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
        _findall_cache = r = [VisualStudioInstance(*v) for v in _helper.findall()]
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
