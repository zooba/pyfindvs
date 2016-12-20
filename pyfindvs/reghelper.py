#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation
# All rights reserved.
#
# Distributed under the terms of the MIT License
#-------------------------------------------------------------------------

import itertools
import os.path

try:
    import winreg
except ImportError:
    import _winreg as winreg

class RegHelper(object):
    def __init__(self, root_key, subkey, flags):
        if subkey:
            self.key = winreg.OpenKeyEx(root_key, subkey, 0, flags)
        else:
            self.key = root_key
        self.flags = flags

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()

    def close(self):
        winreg.CloseKey(self.key)

    def open_subkey(self, subkey, flags=None):
        if flags is None:
            flags = self.flags
        return type(self)(self.key, subkey, flags)

    def get_subkeys(self):
        subkey_names = []
        try:
            for i in itertools.count():
                subkey_names.append(winreg.EnumKey(self.key, i))
        except OSError:
            pass
        return subkey_names

    def __getitem__(self, subkey):
        return self.open_subkey(subkey)

    def __iter__(self):
        return iter(self.get_subkeys())

    def get_value(self, value_name=None):
        val, val_type = winreg.QueryValueEx(self.key, value_name)
        if val_type == winreg.REG_SZ:
            if '\0' in val:
                val = val[:val.index('\0')]
        elif val_type == winreg.REG_EXPAND_SZ:
            val = os.path.expandvars(val)

        return val

    def get_all_values(self):
        value_names = []
        try:
            for i in itertools.count():
                value_names.append(winreg.EnumValue(self.key, i))
        except OSError:
            pass
        return {k: self.get_value(k) for k in value_names}

HKLM_64 = RegHelper(winreg.HKEY_LOCAL_MACHINE, None, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
HKLM_32 = RegHelper(winreg.HKEY_LOCAL_MACHINE, None, winreg.KEY_READ | winreg.KEY_WOW64_32KEY)
HKCU = RegHelper(winreg.HKEY_CURRENT_USER, None, winreg.KEY_READ)
