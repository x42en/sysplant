structure = """#ifndef KNORMAL_ROUTINE
typedef struct _KNORMAL_ROUTINE
{
    PVOID NormalContext;
    PVOID SystemArgument1;
    PVOID SystemArgument2;
} KNORMAL_ROUTINE, *PKNORMAL_ROUTINE;
#endif
"""
structure3 = """#ifndef PS_CREATE_INFO_INIT_STATE_FLAGS
typedef struct _PS_CREATE_INFO_INIT_STATE_FLAGS
{
    UCHAR WriteOutputOnExit = 1;
    UCHAR DetectManifest = 1;
    UCHAR IFEOSkipDebugger = 1;
    UCHAR IFEODoNotPropagateKeyState = 1;
    UCHAR SpareBits1 = 4;
    UCHAR SpareBits2 = 8;
    UCHAR ProhibitedImageCharacteristics = 16;
} PS_CREATE_INFO_INIT_STATE_FLAGS, *PPS_CREATE_INFO_INIT_STATE_FLAGS;
#endif
"""
union = """#ifndef PS_ATTRIBUTE_UNION
typedef union _PS_ATTRIBUTE_UNION
{
    ULONG_PTR Value;
    PVOID ValuePtr;
} PS_ATTRIBUTE_UNION, *PPS_ATTRIBUTE_UNION;
#endif
"""
pointer = "typedef PPVOID* PVOID;\n"
standard = """typedef LANGID* = WORD;
    PLANGID* = ptr LANGID;
"""
enum = """#ifndef SECTION_INHERIT
typedef enum _SECTION_INHERIT
{
    ViewShare = 1,
    ViewUnmap = 2,
} SECTION_INHERIT, *PSECTION_INHERIT;
#endif
"""
debug = "#define SPT_DEBUG TRUE"
seed = "#define SPT_SEED 0x1"
stub = """#define NtOpenProcessToken NtOpenProcessToken
__asm__(\"NtOpenProcessToken: \\n\\
    push dword ptr 0x5b50179b \\n\\
    call SPT_Syscall \\n\\
\");
"""
definitions = """#ifndef KNORMAL_ROUTINE
typedef struct _KNORMAL_ROUTINE
{
    PVOID NormalContext;
    PVOID SystemArgument1;
    PVOID SystemArgument2;
} KNORMAL_ROUTINE, *PKNORMAL_ROUTINE;
#endif

EXTERN_C NTSTATUS NtQueueApcThread(
    IN HANDLE ThreadHandle,
    IN PKNORMAL_ROUTINE ApcRoutine,
    IN PVOID ApcArgument1,
    IN PVOID ApcArgument2,
    IN PVOID ApcArgument3
);
"""
