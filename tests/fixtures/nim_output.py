structure = """    KNORMAL_ROUTINE* {.pure.} = object
        NormalContext: PVOID
        SystemArgument1: PVOID
        SystemArgument2: PVOID
    PKNORMAL_ROUTINE* = ptr KNORMAL_ROUTINE
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
