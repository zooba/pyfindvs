#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation
# All rights reserved.
#
# Distributed under the terms of the MIT License
#-------------------------------------------------------------------------

from distutils.errors import DistutilsExecError, DistutilsPlatformError, \
                             DistutilsInternalError, CCompilerError
from distutils import log
from distutils.util import get_platform, execute

from collections import ChainMap
from copy import copy
from io import TextIOWrapper
from pyfindvs import findwithany

from .options import *
from .template import Template

import os.path
import subprocess
import sys

# A set containing the DLLs that are guaranteed to be available for
# all micro versions of this Python version. Known extension
# dependencies that are not in this set will be copied to the output
# path.
_BUNDLED_DLLS = frozenset(['vcruntime140.dll'])

_REQUIRED_PACKAGES = {
    'win32': ['Microsoft.Build', 'Microsoft.VisualCpp.Tools.HostX86.TargetX86', 'WinSDK'],
    'win-amd64': ['Microsoft.Build', 'Microsoft.VisualCpp.Tools.HostX86.TargetX64', 'WinSDK'],
}

_TOOL_KEY_SUFFIX = {
    'win32': '',
    'win-amd64': '_x64',
}

class MSBuildCompiler(object):
    """Concrete class that implements an interface to Microsoft Visual C++,
       as defined by the CCompiler abstract class."""

    compiler_type = 'msvc'

    def __init__(self, verbose=0, dry_run=0, force=0):
        self.dry_run = dry_run
        self.force = force

        self.options = GlobalOptions()
        self.out_options = OutputOptions()
        self.cl_options = ClCompileOptions()
        self.link_options = LinkOptions()
        self.lib_options = LibOptions()
        self.rc_options = RcOptions()
        self.midl_options = MidlOptions()

        self.additional_items = []

        self.plat_name = None
        self.initialized = False

    def initialize(self, plat_name=None):
        # multi-init means we would need to check platform same each time...
        assert not self.initialized, "don't init multiple times"
        if plat_name is None:
            plat_name = get_platform()

        # Update options instances for platform. These will raise if it is
        # not a supported platform
        self.options._for_plat(plat_name)
        self.out_options._for_plat(plat_name)
        self.cl_options._for_plat(plat_name)
        self.link_options._for_plat(plat_name)
        self.lib_options._for_plat(plat_name)
        self.rc_options._for_plat(plat_name)
        self.midl_options._for_plat(plat_name)

        # Get the available VS installs
        instances = findwithany(*_REQUIRED_PACKAGES[plat_name])
        if not instances:
            raise DistutilsPlatformError("no suitable Visual Studio "
                "installations found. Visit https://aka.ms/vcpython "
                "for information on obtaining one.")

        self._tool_key_suffix = _TOOL_KEY_SUFFIX[plat_name]
        self.vc_env = ChainMap(*(inst.known_paths
            for inst in sorted(instances, key=lambda i: i.version_info, reverse=True)))

        self.msbuild = self.vc_env['msbuild.exe']
        if 'MSVC\\14.1' in self.vc_env.get('cl.exe'):
            self.options.PlatformToolset = 'v141'

        if not self.options.DefaultWindowsSDKVersion:
            try:
                sdkver = max(v.version_info for v in instances if v.instance_id == 'winsdk10')
            except ValueError:
                sdkver = 8, 1
            self.options.DefaultWindowsSDKVersion = '.'.join(str(i) for i in sdkver)

        # When vcruntime140.dll becomes necessary, we should restore this code
        #vcruntime = self.vc_env.get('vcruntime140.dll')
        #if vcruntime:
        #    self.additional_items.append({"ItemType": "Content", "Include": vcruntime})

        self.initialized = True

    def _find_exe(self, tool, raise_if_missing=True):
        plattool = tool + self._tool_key_suffix
        try:
            return self.vc_env[plattool]
        except LookupError:
            pass
        if raise_if_missing:
            raise DistutilsPlatformError(tool + " is not available on this platform")

    def set_include_dirs(self, dirs):
        self.cl_options._add_opt('AdditionalIncludeDirectories', dirs)
        self.rc_options._add_opt('AdditionalIncludeDirectories', dirs)
        self.midl_options._add_opt('AdditionalIncludeDirectories', dirs)

    def set_libraries(self, names):
        self.link_options._add_opt('AdditionalDependencies', names)
        self.lib_options._add_opt('AdditionalDependencies', names)

    def set_library_dirs(self, dirs):
        self.link_options._add_opt('AdditionalLibraryDirectories', dirs)
        self.lib_options._add_opt('AdditionalLibraryDirectories', dirs)

    def set_link_objects(self, names):
        self.additional_items.extend({'ItemType': 'Link', 'Include': os.path.abspath(n)} for n in names)

    def define_macro(self, name, value):
        v = '{}={}'.format(name, value or '1')
        self.cl_options._add_opt('PreprocessorDefinitions', v)
        self.rc_options._add_opt('PreprocessorDefinitions', v)
        self.midl_options._add_opt('PreprocessorDefinitions', v)

    def undefine_macro(self, name):
        self.cl_options._add_opt('UndefinePreprocessorDefinitions', name)
        self.rc_options._add_opt('UndefinePreprocessorDefinitions', name)
        self.midl_options._add_opt('UndefinePreprocessorDefinitions', name)

    def set_runtime_library_dirs(self, dirs):
        pass

    def detect_language(self, sources):
        return 'c++'

    _SOURCE_KIND = {
        '.c': 'ClCompile',
        '.cpp': 'ClCompile',
        '.cxx': 'ClCompile',
        '.rc': 'ResourceCompile',
        '.idl': 'Midl',
    }

    def compile(self, sources,
                output_dir=None, macros=None, include_dirs=None, debug=0,
                extra_preargs=None, extra_postargs=None, depends=None):

        if not self.initialized:
            self.initialize()

        # Generate .vcxproj and return it as single object
        t = Template()
        global_options = copy(self.options)
        compile_options = [copy(self.cl_options), copy(self.rc_options), copy(self.midl_options)]
        all_options = compile_options + [global_options]
        if debug:
            for opts in all_options:
                opts._for_debug()
        if macros:
            for opts in compile_options:
                opts._add_opt('PreprocessorDefinitions', ['{}={}'.format(k, v) for k, v in macros if v])
                opts._add_opt('UndefinePreprocessorDefinitions', [k for k, v in macros if not v])
        if include_dirs:
            for opts in compile_options:
                opts._add_opt('AdditionalIncludeDirectories', include_dirs)
        if extra_preargs:
            global_options._add_opt('AdditionalOptions', extra_preargs, ' ')
        if extra_postargs:
            global_options._add_opt('AdditionalOptions', extra_postargs, ' ')

        if output_dir:
            global_options.IntDir = os.path.abspath(output_dir)
        if not global_options.IntDir.endswith('\\'):
            global_options.IntDir += '\\'

        t.merge_options(*all_options)

        all_sources = { }
        for s in sources:
            _, ext = os.path.splitext(s)
            full_s = os.path.abspath(s)
            s_kind = self._SOURCE_KIND.get(ext.lower())
            if s_kind:
                all_sources.setdefault(s_kind, []).append(full_s)
        for s in self.additional_items:
            s = dict(s)
            s_kind = s.pop('ItemType', None)
            if not s_kind:
                continue
            all_sources.setdefault(s_kind, []).append(s)

        for s_kind, items in all_sources.items():
            t.add_items(s_kind, items)

        os.makedirs(global_options.IntDir, exist_ok=True)

        proj_file = os.path.join(global_options.IntDir, 'template.g.vcxproj')
        t.save(proj_file)
        return [proj_file]


    _LINK_TARGET_DESC = {
        "static_lib": "StaticLibrary",
        "shared_object": "DynamicLibrary",
        "shared_library": "DynamicLibrary",
        "executable": "Executable",
    }

    @classmethod
    def _ensure_libs(cls, libraries):
        for lib in libraries:
            if os.path.splitext(lib)[-1].lower() not in {'.lib', '.obj'}:
                yield lib + '.lib'
            else:
                yield lib

    def link(self,
             target_desc,
             objects,
             output_filename,
             output_dir=None,
             libraries=None,
             library_dirs=None,
             runtime_library_dirs=None,
             export_symbols=None,
             debug=0,
             extra_preargs=None,
             extra_postargs=None,
             build_temp=None,
             target_lang=None):

        if not self.initialized:
            raise DistutilsInternalError("compiler was not initialized")

        out_opts = copy(self.out_options)
        out_subdir, out_filename = os.path.split(output_filename)
        out_filename, out_ext = os.path.splitext(out_filename)
        out_opts.OutDir = os.path.abspath(out_subdir)
        if output_dir:
            out_opts.OutDir = os.path.abspath(output_dir)
        if not out_opts.OutDir.endswith('\\'):
            out_opts.OutDir += '\\'
        out_opts.TargetName = out_filename
        out_opts.TargetExt = out_ext
        out_opts.ConfigurationType = self._LINK_TARGET_DESC[target_desc]

        link_options = [copy(self.link_options), copy(self.lib_options)]
        global_options = copy(self.options)
        all_options = link_options + [out_opts, global_options]

        if debug:
            for opts in all_options:
                opts._for_debug()
        if libraries:
            for opts in link_options:
                opts._add_opt('AdditionalDependencies', self._ensure_libs(libraries))
        if library_dirs:
            for opts in link_options:
                opts._add_opt('AdditionalLibraryDirectories', library_dirs)
        if extra_preargs:
            global_options._add_opt('AdditionalOptions', extra_preargs, ' ')
        if extra_postargs:
            global_options._add_opt('AdditionalOptions', extra_postargs, ' ')
        if build_temp:
            global_options.IntDir = os.path.abspath(build_temp)
            if not global_options.IntDir.endswith('\\'):
                global_options.IntDir += '\\'
        if out_ext.lower() == '.pyd':
            for opts in link_options:
                opts._set_opt('LinkDLL', 'true', warn_if_invalid=False)

        t = Template(objects[0])
        t.merge_options(*all_options)
        t.save(objects[0])

        verbose_log = os.path.join(global_options.IntDir, "verbose.log")
        errors_log = os.path.join(global_options.IntDir, "errors.log")
        cmd = [
            self.msbuild,
            '/nologo',
            '/noconlog',
            '/flp1:LogFile={};Verbosity=detailed;Encoding=UTF-8'.format(verbose_log),
            '/flp2:LogFile={};ErrorsOnly;WarningsOnly;Encoding=UTF-8'.format(errors_log),
            objects[0]
        ]

        log.info(' '.join('"{}"'.format(c) if ' ' in c else c for c in cmd))
        if not self.dry_run:
            os.makedirs(global_options.IntDir, exist_ok=True)
            p = subprocess.Popen(cmd)
            if p.wait() != 0:
                log.error('Build returned exit code {}. Errors follow'.format(p.returncode))
                with open(errors_log, 'r', encoding='utf-8-sig') as f:
                    for line in f:
                        if ': error' in line:
                            log.error(line)
                        else:
                            log.warn(line)
                raise CCompilerError("error building project. See '{}' for detailed log"
                    .format(verbose_log))

    def create_static_lib(self, objects, output_libname, output_dir=None, debug=0, target_lang=None):
        self.link("static_lib", objects, output_libname + ".lib", output_dir, debug=debug)

    def link_shared_lib(self, objects, output_libname, output_dir=None, libraries=None, library_dirs=None,
        runtime_library_dirs=None, export_symbols=None, debug=0, extra_preargs=None, extra_postargs=None,
        build_temp=None, target_lang=None):
        self.link("shared_library", objects,
                  output_libname, output_dir,
                  libraries, library_dirs, runtime_library_dirs,
                  export_symbols, debug,
                  extra_preargs, extra_postargs, build_temp, target_lang)


    def link_shared_object(self, objects, output_filename, output_dir=None, libraries=None, library_dirs=None,
        runtime_library_dirs=None, export_symbols=None, debug=0, extra_preargs=None, extra_postargs=None,
        build_temp=None, target_lang=None):
        self.link("shared_object", objects,
                  output_filename, output_dir,
                  libraries, library_dirs, runtime_library_dirs,
                  export_symbols, debug,
                  extra_preargs, extra_postargs, build_temp, target_lang)


    def link_executable(self, objects, output_progname, output_dir=None, libraries=None, library_dirs=None,
        runtime_library_dirs=None, debug=0, extra_preargs=None, extra_postargs=None, target_lang=None):
        self.link("executable", objects,
                  output_progname, output_dir,
                  libraries, library_dirs, runtime_library_dirs, None,
                  debug, extra_preargs, extra_postargs, None, target_lang)
