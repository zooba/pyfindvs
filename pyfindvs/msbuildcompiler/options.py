#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation
# All rights reserved.
#
# Distributed under the terms of the MIT License
#-------------------------------------------------------------------------

class OptionsBase:
    def _add_opt(self, opt_name, right_arg, sep=';'):
        if not isinstance(right_arg, str):
            try:
                it = iter(right_arg)
            except TypeError:
                pass
            else:
                right_arg = sep.join(str(i) for i in it)
        existing = getattr(self, opt_name, None)
        if not existing:
            setattr(self, opt_name, right_arg)
            return
        setattr(self, opt_name, '{}{}{}'.format(existing, sep, right_arg))

    def _set_opt(self, opt_name, right_arg, warn_if_invalid=True):
        if not hasattr(self, opt_name):
            if warn_if_invalid:
                # TODO: warn
                pass
            return
        setattr(self, opt_name, right_arg)

    def _for_plat(self, plat):
        raise NotImplementedError('{}._for_plat must be overridden'.format(
            type(self).__name__))

    def _for_debug(self):
        raise NotImplementedError('{}._for_debug must be overridden'.format(
            type(self).__name__))

class GlobalOptionsBase(OptionsBase):
    def __init__(self):
        if not hasattr(self, '_PropertyGroup'):
            raise NotImplementedError('{}._PropertyGroup must be set'.format(
                type(self).__name__))

class ItemOptionsBase(OptionsBase):
    def __init__(self):
        if not hasattr(self, '_ItemDefinitionGroup'):
            raise NotImplementedError('{}._ItemDefinitionGroup must be set'.format(
                type(self).__name__))

class GlobalOptions(GlobalOptionsBase):
    _PropertyGroup = "Globals"

    Configuration = "Release"
    DefaultWindowsSDKVersion = ""
    GenerateManifest = True
    Platform = "Win32"
    PlatformToolset = "v140"
    IntDir = ""
    UseDebugLibraries = False

    def _for_debug(self):
        self.Configuration = "Debug"
        self.UseDebugLibraries = True

    def _for_plat(self, plat):
        if plat == 'win32':
            self.Platform = 'Win32'
        elif plat == 'win-amd64':
            self.Platform = 'x64'
        else:
            raise ValueError("'{}' is not a supported platform".format(plat))

class OutputOptions(GlobalOptionsBase):
    _PropertyGroup = "Outputs"

    OutDir = ""
    TargetName = ""
    TargetExt = ".pyd"
    ConfigurationType = "DynamicLibrary"

    def _for_debug(self): pass
    def _for_plat(self, plat): pass

class ClCompileOptions(ItemOptionsBase):
    _ItemDefinitionGroup = "ClCompile"

    AdditionalIncludeDirectories       = "%(AdditionalIncludeDirectories)"
    AdditionalOptions                  = "%(AdditionalOptions)"
    AdditionalUsingDirectories         = "%(AdditionalUsingDirectories)"
    AssemblerListingLocation           = ""
    AssemblerOutput                    = ""
    BasicRuntimeChecks                 = ""
    BrowseInformation                  = ""
    BrowseInformationFile              = ""
    BufferSecurityCheck                = ""
    CallingConvention                  = ""
    ControlFlowGuard                   = ""
    CompileAsManaged                   = ""
    CompileAsWinRT                     = ""
    CompileAs                          = ""
    DebugInformationFormat             = "ProgramDatabase"
    DisableLanguageExtensions          = ""
    DisableSpecificWarnings            = ""
    EnableEnhancedInstructionSet       = ""
    EnableFiberSafeOptimizations       = ""
    EnableParallelCodeGeneration       = ""
    EnablePREfast                      = ""
    EnforceTypeConversionRules         = ""
    ErrorReporting                     = ""
    ExceptionHandling                  = ""
    ExpandAttributedSource             = ""
    FavorSizeOrSpeed                   = ""
    FloatingPointExceptions            = ""
    FloatingPointModel                 = ""
    ForceConformanceInForLoopScope     = ""
    ForcedIncludeFiles                 = "%(ForcedIncludeFiles)"
    ForcedUsingFiles                   = "%(ForcedUsingFiles)"
    FunctionLevelLinking               = True
    GenerateXMLDocumentationFiles      = ""
    IgnoreStandardIncludePath          = ""
    InlineFunctionExpansion            = ""
    IntrinsicFunctions                 = True
    MinimalRebuild                     = ""
    MultiProcessorCompilation          = ""
    ObjectFileName                     = ""
    OmitDefaultLibName                 = ""
    OmitFramePointers                  = ""
    OpenMPSupport                      = ""
    Optimization                       = "MaxSpeed"
    PrecompiledHeader                  = ""
    PrecompiledHeaderFile              = ""
    PrecompiledHeaderOutputFile        = ""
    PREfastAdditionalOptions           = ""
    PREfastAdditionalPlugins           = ""
    PREfastLog                         = ""
    PreprocessKeepComments             = ""
    PreprocessorDefinitions            = "%(PreprocessorDefinitions)"
    PreprocessSuppressLineNumbers      = ""
    PreprocessToFile                   = ""
    ProcessorNumber                    = ""
    ProgramDataBaseFileName            = ""
    RemoveUnreferencedCodeData         = ""
    RuntimeLibrary                     = "MultithreadedDLL"
    RuntimeTypeInfo                    = ""
    SDLCheck                           = ""
    ShowIncludes                       = ""
    WarningVersion                     = ""
    SmallerTypeCheck                   = ""
    StringPooling                      = ""
    StructMemberAlignment              = ""
    SuppressStartupBanner              = ""
    TreatSpecificWarningsAsErrors      = ""
    TreatWarningAsError                = ""
    TreatWChar_tAsBuiltInType          = ""
    UndefineAllPreprocessorDefinitions = ""
    UndefinePreprocessorDefinitions    = "%(UndefinePreprocessorDefinitions)"
    UseFullPaths                       = ""
    UseUnicodeForAssemblerListing      = ""
    WarningLevel                       = "Level3"
    WholeProgramOptimization           = ""
    WinRTNoStdLib                      = ""
    XMLDocumentationFileName           = ""
    CreateHotpatchableImage            = ""

    def _for_debug(self):
        self.FunctionLevelLinking = False
        self.IntrinsicFunctions = False
        self.Optimization = "Disabled"
        self.RuntimeLibrary = "MultithreadedDLL"

    def _for_plat(self, plat): pass

class LinkOptions(ItemOptionsBase):
    _ItemDefinitionGroup = "Link"

    AdditionalDependencies         = "%(AdditionalDependencies)"
    AdditionalLibraryDirectories   = "%(AdditionalLibraryDirectories)"
    AdditionalManifestDependencies = "%(AdditionalManifestDependencies)"
    AdditionalOptions              = "%(AdditionalOptions)"
    AddModuleNamesToAssembly       = ""
    AllowIsolation                 = ""
    AppContainer                   = ""
    AssemblyDebug                  = ""
    AssemblyLinkResource           = ""
    BaseAddress                    = ""
    CLRImageType                   = ""
    CLRSupportLastError            = ""
    CLRThreadAttribute             = ""
    CLRUnmanagedCodeCheck          = ""
    CreateHotPatchableImage        = ""
    DataExecutionPrevention        = ""
    DelayLoadDLLs                  = ""
    Driver                         = ""
    EnableCOMDATFolding            = True
    EnableUAC                      = ""
    EntryPointSymbol               = ""
    LinkErrorReporting             = ""
    FixedBaseAddress               = ""
    ForceFileOutput                = ""
    ForceSymbolReferences          = ""
    FunctionOrder                  = ""
    GenerateDebugInformation       = True
    # Global property
    #GenerateManifest               = "$(GenerateManifest)"
    GenerateMapFile                = ""
    WindowsMetadataFile            = ""
    HeapCommitSize                 = ""
    HeapReserveSize                = ""
    IgnoreAllDefaultLibraries      = ""
    IgnoreEmbeddedIDL              = ""
    IgnoreSpecificDefaultLibraries = ""
    ImageHasSafeExceptionHandlers  = ""
    ImportLibrary                  = ""
    KeyContainer                   = ""
    LargeAddressAware              = ""
    LinkDLL                        = ""
    # Global property
    #LinkIncremental                = "$(LinkIncremental)"
    LinkStatus                     = ""
    LinkTimeCodeGeneration         = ""
    ManifestFile                   = ""
    ManifestEmbed                  = ""
    ManifestInput                  = ""
    MapExports                     = ""
    MapFileName                    = ""
    MergedIDLBaseFileName          = ""
    MergeSections                  = ""
    MidlCommandFile                = ""
    MinimumRequiredVersion         = ""
    ModuleDefinitionFile           = ""
    MSDOSStubFileName              = ""
    OptimizeReferences             = True
    OutputFile                     = ""
    PreventDllBinding              = ""
    Profile                        = ""
    ProfileGuidedDatabase          = ""
    ProgramDatabaseFile            = ""
    RandomizedBaseAddress          = ""
    NoEntryPoint                   = ""
    SectionAlignment               = ""
    SetChecksum                    = ""
    ShowProgress                   = ""
    SignHash                       = ""
    SpecifySectionAttributes       = ""
    StackCommitSize                = ""
    StackReserveSize               = ""
    StripPrivateSymbols            = ""
    SubSystem                      = ""
    SupportUnloadOfDelayLoadedDLL  = ""
    SupportNobindOfDelayLoadedDLL  = ""
    SuppressStartupBanner          = ""
    SwapRunFromCD                  = ""
    SwapRunFromNET                 = ""
    TargetMachine                  = ""
    TerminalServerAware            = ""
    TreatLinkerWarningAsErrors     = ""
    TurnOffAssemblyGeneration      = ""
    TypeLibraryFile                = ""
    TypeLibraryResourceID          = ""
    UACExecutionLevel              = ""
    UACUIAccess                    = ""
    Version                        = ""
    WindowsMetadataLinkKeyFile     = ""
    WindowsMetadataKeyContainer    = ""
    WindowsMetadataLinkDelaySign   = ""
    WindowsMetadataSignHash        = ""

    def _for_debug(self):
        self.EnableCOMDATFolding = False
        self.OptimizeReferences = False

    def _for_plat(self, plat): pass

class LibOptions(ItemOptionsBase):
    _ItemDefinitionGroup = "Lib"

    AdditionalDependencies          = "%(AdditionalDependencies)"
    AdditionalLibraryDirectories    = "%(AdditionalLibraryDirectories)"
    # Global property
    #AdditionalOptions               = ""
    DisplayLibrary                  = ""
    ErrorReporting                  = ""
    ExportNamedFunctions            = ""
    ForceSymbolReferences           = ""
    IgnoreAllDefaultLibraries       = ""
    IgnoreSpecificDefaultLibraries  = "%(IgnoreSpecificDefaultLibraries)"
    LinkTimeCodeGeneration          = ""
    ModuleDefinitionFile            = ""
    Name                            = ""
    OutputFile                      = ""
    RemoveObjects                   = ""
    SubSystem                       = ""
    SuppressStartupBanner           = ""
    TargetMachine                   = ""
    TreatLibWarningAsErrors         = ""
    Verbose                         = ""

    def _for_debug(self): pass
    def _for_plat(self, plat): pass

class RcOptions(ItemOptionsBase):
    _ItemDefinitionGroup = "ResourceCompile"

    AdditionalIncludeDirectories    = "%(AdditionalIncludeDirectories)"
    AdditionalOptions               = "%(AdditionalOptions)"
    Culture                         = ""
    IgnoreStandardIncludePath       = ""

    NullTerminateStrings            = ""
    PreprocessorDefinitions         = "%(PreprocessorDefinitions)"
    ResourceOutputFileName          = ""
    SuppressStartupBanner           = ""
    ShowProgress                    = ""
    UndefinePreprocessorDefinitions = "%(UndefinePreprocessorDefinitions)"

    def _for_debug(self): pass
    def _for_plat(self, plat): pass

class MidlOptions(ItemOptionsBase):
    _ItemDefinitionGroup = "Midl"

    AdditionalIncludeDirectories        = "%(AdditionalIncludeDirectories)"
    AdditionalMetadataDirectories       = "%(AdditionalMetadataDirectories)"
    AdditionalOptions                   = "%(AdditionalOptions)"
    ApplicationConfigurationMode        = ""
    ClientStubFile                      = ""
    CPreprocessOptions                  = ""
    DefaultCharType                     = ""
    DllDataFileName                     = ""
    EnableErrorChecks                   = ""
    EnableWindowsRuntime                = ""
    Enumclass                           = ""
    ErrorCheckAllocations               = ""
    ErrorCheckBounds                    = ""
    ErrorCheckEnumRange                 = ""
    ErrorCheckRefPointers               = ""
    ErrorCheckStubData                  = ""
    # Global property
    #ExcludedInputPaths                  ="$(ExcludePath)"
    GenerateClientFiles                 = ""
    GenerateServerFiles                 = ""
    GenerateStublessProxies             = ""
    GenerateTypeLibrary                 = ""
    HeaderFileName                      = ""
    IgnoreStandardIncludePath           = ""
    InterfaceIdentifierFileName         = ""
    LocaleID                            = ""
    MkTypLibCompatible                  = ""
    MetadataFileName                    = ""
    OutputDirectory                     = ""
    PrependWithABINamepsace             = ""
    PreprocessorDefinitions             = "%(PreprocessorDefinitions)"
    ProxyFileName                       = ""
    RedirectOutputAndErrors             = ""
    ServerStubFile                      = ""
    StructMemberAlignment               = ""
    SuppressCompilerWarnings            = ""
    SuppressStartupBanner               = ""
    TargetEnvironment                   = ""
    TypeLibFormat                       = ""
    TypeLibraryName                     = ""
    UndefinePreprocessorDefinitions     = "%(UndefinePreprocessorDefinitions)"
    ValidateAllParameters               = ""
    WarnAsError                         = ""
    WarningLevel                        = ""

    def _for_debug(self): pass
    def _for_plat(self, plat): pass
