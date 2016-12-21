
from distutils.core import Command

import distutils.ccompiler
import pyfindvs.msbuildcompiler
import sys

class enable_msbuildcompiler(Command):
    description = 'enable the MSBuildCompiler class'

    user_options = []

    def initialize_options(self):
        distutils.ccompiler.compiler_class['msbuild'] = (
            '_msbuildcompiler',
            'MSBuildCompiler',
            'MSBuild project-based compiler',
        )

        distutils.ccompiler._default_compilers = (
            ('nt', 'msbuild'),
            ('win32', 'msbuild'),
        ) + distutils.ccompiler._default_compilers

        sys.modules['distutils._msbuildcompiler'] = pyfindvs.msbuildcompiler

    def finalize_options(self):
        pass

    def run(self):
        pass


