#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation
# All rights reserved.
#
# Distributed under the terms of the MIT License
#-------------------------------------------------------------------------

import re
import setuptools
import shutil
import sys

from pathlib import Path

__author__ = 'Microsoft Corporation <python@microsoft.com>'
__version__ = '0.6.0'

AUTHOR_RE = re.match(r'(.+?)\s*\<(.+?)\>', __author__)

with open('README', 'r', encoding='utf-8') as f:
    long_description = f.read()

PACKAGES = ['pyfindvs', 'pyfindvs.msbuildcompiler']
PACKAGE_DATA = {
    'pyfindvs.msbuildcompiler': ['*.template'],
}

REQUIREMENTS = []

PLATFORM = 'x86'
if sys.maxsize > 2**32:
    PLATFORM = 'x64'

SETUP_ROOT = Path(__file__).resolve().parent

SETUP_CONFIG_PACKAGE_NAME = 'Microsoft.VisualStudio.Setup.Configuration.Native'
SETUP_CONFIG_PACKAGES = list((SETUP_ROOT / 'packages').glob(SETUP_CONFIG_PACKAGE_NAME + '*'))
if not SETUP_CONFIG_PACKAGES:
    from subprocess import check_call
    from urllib.request import urlretrieve
    print('Installing depedencies...')
    if (SETUP_ROOT / 'nuget.exe').is_file():
        nuget = str(SETUP_ROOT / 'nuget.exe')
    else:
        nuget, _ = urlretrieve('https://aka.ms/nugetclidl', filename=str(SETUP_ROOT / 'nuget.exe'))
    check_call([nuget, 'install', '-OutputDirectory', str(SETUP_ROOT / 'packages'), '-Prerelease', SETUP_CONFIG_PACKAGE_NAME])
    SETUP_CONFIG_PACKAGES = list((SETUP_ROOT / 'packages').glob(SETUP_CONFIG_PACKAGE_NAME + '*'))

SETUP_CONFIG_PATH = sorted(SETUP_CONFIG_PACKAGES)[-1]
SETUP_CONFIG_H_PATH = SETUP_CONFIG_PATH / 'lib' / 'native' / 'include'
SETUP_CONFIG_LIB_PATH = SETUP_CONFIG_PATH / 'lib' / 'native' / 'v141' / PLATFORM
SETUP_CONFIG_DLL_PATH = SETUP_CONFIG_PATH / 'tools' / PLATFORM

ENTRY_POINTS = {
    "distutils.commands": [
        "enable_msbuildcompiler=pyfindvs.msbuildcompiler.enable_msbuildcompiler:enable_msbuildcompiler"
    ],
}

from setuptools import Extension
EXT_MODULES = [Extension(
    'pyfindvs._helper',
    ['pyfindvs/pyfindvs.cpp'],
    include_dirs=[str(SETUP_CONFIG_H_PATH)],
    library_dirs=[str(SETUP_CONFIG_LIB_PATH)],
    # We use functions that are missing from python3.dll, so cannot actually do this
    #py_limited_api=True,
    #define_macros=[('Py_LIMITED_API', '0x03050000')],
)]

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Win32 (MS Windows)',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: Microsoft :: Windows',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3 :: Only',
]

setup_cfg = dict(
    name='pyfindvs',
    version=__version__,
    description='Python module for locating Visual Studio',
    long_description=long_description,
    author=AUTHOR_RE.group(1),
    author_email=AUTHOR_RE.group(2),
    url='https://github.com/zooba/pyfindvs',
    packages=PACKAGES,
    package_data=PACKAGE_DATA,
    ext_modules=EXT_MODULES,
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS,
    entry_points=ENTRY_POINTS,
)

from setuptools import setup
setup(**setup_cfg)
