#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation
# All rights reserved.
#
# Distributed under the terms of the MIT License
#-------------------------------------------------------------------------

class OptionsBase:
    def _add_opt(self, opt_name, right_arg, sep=';'):
        if not right_arg:
            return
        if not isinstance(right_arg, str):
            right_arg = sep.join(right_arg)
        existing = getattr(self, opt_name, None)
        if not existing:
            setattr(self, opt_name, right_arg)
            return
        setattr(self, opt_name, '{}{}{}'.format(existing, sep, right_arg))

    def _set_opt(self, opt_name, right_arg, warn_if_invalid=True):
        if not right_arg:
            right_arg = ''
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
    Platform = "Win32"
    PlatformToolset = "v140"
    IntDir = ""
    UseDebugLibraries = "false"

    def _for_debug(self):
        self.Configuration = "Debug"
        self.UseDebugLibraries = "true"

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

    AdditionalIncludeDirectories       = ""
    AdditionalOptions                  = ""
    AdditionalUsingDirectories         = ""
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
    ForcedIncludeFiles                 = ""
    ForcedUsingFiles                   = ""
    FunctionLevelLinking               = "true"
    GenerateXMLDocumentationFiles      = ""
    IgnoreStandardIncludePath          = ""
    InlineFunctionExpansion            = ""
    IntrinsicFunctions                 = "true"
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
    PreprocessorDefinitions            = ""
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
    UndefinePreprocessorDefinitions    = ""
    UseFullPaths                       = ""
    UseUnicodeForAssemblerListing      = ""
    WarningLevel                       = "Level3"
    WholeProgramOptimization           = ""
    WinRTNoStdLib                      = ""
    XMLDocumentationFileName           = ""
    CreateHotpatchableImage            = ""

    def _for_debug(self):
        self.FunctionLevelLinking = "false"
        self.IntrinsicFunctions = "false"
        self.Optimization = "Disabled"
        self.RuntimeLibrary = "MultithreadedDLL"

    def _for_plat(self, plat): pass

class LinkOptions(ItemOptionsBase):
    _ItemDefinitionGroup = "Link"

    AdditionalDependencies         = ""
    AdditionalLibraryDirectories   = ""
    AdditionalManifestDependencies = ""
    AdditionalOptions              = ""
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
    EnableCOMDATFolding            = "true"
    EnableUAC                      = ""
    EntryPointSymbol               = ""
    LinkErrorReporting             = ""
    FixedBaseAddress               = ""
    ForceFileOutput                = ""
    ForceSymbolReferences          = ""
    FunctionOrder                  = ""
    GenerateDebugInformation       = "true"
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
    OptimizeReferences             = "true"
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
        self.EnableCOMDATFolding = "false"
        self.OptimizeReferences = "false"

    def _for_plat(self, plat): pass

class LibOptions(ItemOptionsBase):
    _ItemDefinitionGroup = "Lib"

    AdditionalDependencies          = ""
    AdditionalLibraryDirectories    = ""
    # Global property
    #AdditionalOptions               = ""
    DisplayLibrary                  = ""
    ErrorReporting                  = ""
    ExportNamedFunctions            = ""
    ForceSymbolReferences           = ""
    IgnoreAllDefaultLibraries       = ""
    IgnoreSpecificDefaultLibraries  = ""
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
    _ItemDefinitionGroup = "RC"

    AdditionalIncludeDirectories    = ""
    AdditionalOptions               = ""
    Culture                         = ""
    IgnoreStandardIncludePath       = ""

    NullTerminateStrings            = ""
    PreprocessorDefinitions         = ""
    ResourceOutputFileName          = ""
    SuppressStartupBanner           = ""
    ShowProgress                    = ""
    UndefinePreprocessorDefinitions = ""

    def _for_debug(self): pass
    def _for_plat(self, plat): pass

class MidlOptions(ItemOptionsBase):
    _ItemDefinitionGroup = "Midl"

    AdditionalIncludeDirectories        = ""
    AdditionalMetadataDirectories       = ""
    AdditionalOptions                   = ""
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
    PreprocessorDefinitions             = ""
    ProxyFileName                       = ""
    RedirectOutputAndErrors             = ""
    ServerStubFile                      = ""
    StructMemberAlignment               = ""
    SuppressCompilerWarnings            = ""
    SuppressStartupBanner               = ""
    TargetEnvironment                   = ""
    TypeLibFormat                       = ""
    TypeLibraryName                     = ""
    UndefinePreprocessorDefinitions     = ""
    ValidateAllParameters               = ""
    WarnAsError                         = ""
    WarningLevel                        = ""

    def _for_debug(self): pass
    def _for_plat(self, plat): pass
