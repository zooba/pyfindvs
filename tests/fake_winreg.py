"""A minimal in-memory stand-in for the stdlib ``winreg`` module.

This lets ``pyfindvs.reghelper`` (and the modules that build on it) be
imported and exercised on platforms that don't have a real Windows
registry (or even a ``winreg`` module at all), such as in CI on Linux/Mac.

Tests populate ``TREE`` (or use :func:`set_tree`) to describe a fake
registry layout, then call the code under test as normal.
"""

import types

HKEY_LOCAL_MACHINE = "HKEY_LOCAL_MACHINE"
HKEY_CURRENT_USER = "HKEY_CURRENT_USER"

KEY_READ = 0x20019
KEY_WOW64_64KEY = 0x0100
KEY_WOW64_32KEY = 0x0200

REG_SZ = 1
REG_EXPAND_SZ = 2
REG_DWORD = 4

# Root of the fake registry. Each node is a dict with optional 'subkeys'
# (name -> node) and 'values' (name -> (value, type)) entries.
TREE = {}


def set_tree(tree):
    """Replace the entire fake registry contents."""
    TREE.clear()
    TREE.update(tree)


def reset():
    TREE.clear()


class _Key:
    __slots__ = ("node",)

    def __init__(self, node):
        self.node = node


def _root_node(key):
    if isinstance(key, _Key):
        return key.node
    return TREE.setdefault(key, {})


def OpenKeyEx(key, sub_key=None, reserved=0, access=0):
    node = _root_node(key)
    if sub_key:
        for part in str(sub_key).replace('/', '\\').split('\\'):
            if not part:
                continue
            try:
                node = node.get('subkeys', {})[part]
            except KeyError:
                raise FileNotFoundError(2, "The system cannot find the file specified")
    return _Key(node)


def CloseKey(key):
    pass


def EnumKey(key, index):
    node = _root_node(key)
    names = sorted(node.get('subkeys', {}))
    try:
        return names[index]
    except IndexError:
        raise OSError("no more data is available")


def EnumValue(key, index):
    node = _root_node(key)
    names = sorted(node.get('values', {}))
    try:
        name = names[index]
    except IndexError:
        raise OSError("no more data is available")
    return name, *node['values'][name]


def QueryValueEx(key, value_name):
    node = _root_node(key)
    try:
        entry = node['values'][value_name]
    except KeyError:
        raise FileNotFoundError(2, "The system cannot find the file specified")
    return entry


def install():
    """Install this module as ``sys.modules['winreg']`` if a real one is
    not already importable (i.e. we are not running on Windows)."""
    import sys
    try:
        import winreg  # noqa: F401
    except ImportError:
        sys.modules['winreg'] = sys.modules[__name__]
