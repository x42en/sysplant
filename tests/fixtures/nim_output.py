structure = """    KNORMAL_ROUTINE* {.pure.} = object
        NormalContext: PVOID
        SystemArgument1: PVOID
        SystemArgument2: PVOID
    PKNORMAL_ROUTINE* = ptr KNORMAL_ROUTINE
"""
structure3 = """    PS_CREATE_INFO_INIT_STATE_FLAGS* {.pure.} = object
        WriteOutputOnExit {.bitsize: 1.}: UCHAR
        DetectManifest {.bitsize: 1.}: UCHAR
        IFEOSkipDebugger {.bitsize: 1.}: UCHAR
        IFEODoNotPropagateKeyState {.bitsize: 1.}: UCHAR
        SpareBits1 {.bitsize: 4.}: UCHAR
        SpareBits2 {.bitsize: 8.}: UCHAR
        ProhibitedImageCharacteristics {.bitsize: 16.}: UCHAR
    PPS_CREATE_INFO_INIT_STATE_FLAGS* = ptr PS_CREATE_INFO_INIT_STATE_FLAGS
"""
union = """    PS_ATTRIBUTE_UNION {.pure, union.} = object
        Value: ULONG_PTR
        ValuePtr: PVOID
    PPS_ATTRIBUTE_UNION = ptr PS_ATTRIBUTE_UNION
"""
pointer = "    PPVOID* = ptr PVOID\n"
standard = """    LANGID* = WORD
    PLANGID* = ptr LANGID
"""
enum = """    SECTION_INHERIT* {.pure.} = enum
        ViewShare = 1,
        ViewUnmap = 2,
    PSECTION_INHERIT* = ptr SECTION_INHERIT
"""
debug = "const SPT_DEBUG = true"
seed = "const SPT_SEED = 0x1"
stub = """proc NtOpenProcessToken*(ProcessHandle: HANDLE, DesiredAccess: ACCESS_MASK, TokenHandle: PHANDLE) {.asmNoStackFrame.} =
    asm \"\"\"
        push dword ptr 0x5b50179b
        call `SPT_Syscall`
    \"\"\"
"""
definitions = """    KNORMAL_ROUTINE* {.pure.} = object
        NormalContext: PVOID
        SystemArgument1: PVOID
        SystemArgument2: PVOID
    PKNORMAL_ROUTINE* = ptr KNORMAL_ROUTINE
"""
