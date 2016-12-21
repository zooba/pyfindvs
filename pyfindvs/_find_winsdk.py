#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation
# All rights reserved.
#
# Distributed under the terms of the MIT License
#-------------------------------------------------------------------------

import os.path
from pyfindvs import _join_and_glob, WindowsSDKInstance
from pyfindvs._helper import getversion
from pyfindvs.reghelper import HKLM_32

_WIN10SDK_KEYS = [
    # Added just for detection purposes, and removed before returning
    ('WinSDK_Root', r'Windows Kits\Installed Roots', 'KitsRoot10', ''),
    
    ('WinSDK.ucrt', r'Windows Kits\Installed Roots', 'KitsRoot10', r'Include\*\ucrt'),
    ('WinSDK.um', r'Windows Kits\Installed Roots', 'KitsRoot10', r'Include\*\um'),
    ('WinSDK.shared', r'Windows Kits\Installed Roots', 'KitsRoot10', r'Include\*\shared'),
    ('WinSDK.libucrt', r'Windows Kits\Installed Roots', 'KitsRoot10', r'Lib\*\ucrt\x86'),
    ('WinSDK.libucrt_x64', r'Windows Kits\Installed Roots', 'KitsRoot10', r'Lib\*\ucrt\x64'),
    ('WinSDK.lib', r'Windows Kits\Installed Roots', 'KitsRoot10', r'Lib\*\um\x86'),
    ('WinSDK.lib_x64', r'Windows Kits\Installed Roots', 'KitsRoot10', r'Lib\*\um\x64'),
]

for tool in ['rc.exe', 'signtool.exe', 'makecat.exe', 'midl.exe', 'mc.exe']:
    _WIN10SDK_KEYS.extend([
        (tool, r'Windows Kits\Installed Roots', 'KitsRoot10', 'bin\\x86\\' + tool),
        (tool + '_x64', r'Windows Kits\Installed Roots', 'KitsRoot10', 'bin\\x64\\' + tool),
    ])

def findall():
    known_paths = {}
    value_cache = {}
    with HKLM_32[r'Software\Microsoft'] as root:
        for key, subkey, value_name, glob in _WIN10SDK_KEYS:
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

    root_path = known_paths.pop('WinSDK_Root', None)
    rc_exe = known_paths.get('rc.exe')
    if not root_path or not rc_exe:
        return []

    return [WindowsSDKInstance(
        'Windows 10 SDK',
        getversion(rc_exe),
        root_path,
        ['WinSDK', 'WinSDK.10'],
        known_paths
    )]
