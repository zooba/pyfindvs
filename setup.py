#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation
# All rights reserved.
#
# Distributed under the terms of the MIT License
#-------------------------------------------------------------------------

import setuptools
import shutil
import sys

from pathlib import Path

with open('README', 'r', encoding='utf-8') as f:
    long_description = f.read()

PACKAGES = ['pyfindvs']
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
SETUP_CONFIG_LIB_PATH = SETUP_CONFIG_PATH / 'lib' / 'native' / 'v140' / PLATFORM
SETUP_CONFIG_DLL_PATH = SETUP_CONFIG_PATH / 'tools' / PLATFORM

from setuptools import Extension
EXT_MODULES = [Extension(
    'pyfindvs._helper',
    ['pyfindvs/pyfindvs.cpp'],
    include_dirs=[str(SETUP_CONFIG_H_PATH)],
    library_dirs=[str(SETUP_CONFIG_LIB_PATH)]
)]

CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Environment :: Win32 (MS Windows)',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: Microsoft :: Windows',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3 :: Only',
]

setup_cfg = dict(
    name='pyfindvs',
    version='0.3.0',
    description='Python module for locating Visual Studio',
    long_description=long_description,
    author='Microsoft Corporation',
    author_email='python@microsoft.com',
    url='https://github.com/zooba/pyfindvs',
    packages=PACKAGES,
    ext_modules=EXT_MODULES,
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS,
)

from setuptools import setup
setup(**setup_cfg)
