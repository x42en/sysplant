# -*- coding:utf-8 -*-


class SysPlantConstants:
    """
    Simple class storing constants for SysPlant app.

    """

    SEARCH_EXT = (".h", ".c", ".cpp", ".nim")
    TEMPLATE_EXT = "nim"
    NIM_TAB = "    "
    TAG_START = "##__"
    TAG_END = "__##"
    RANDOM_WORD_SIZE = 8
    INTERNAL_FUNCTIONS = [
        "SPT_SEED",
        "SPT_Iterator",
        "SPT_Syscall",
        "SPT_HashSyscallName",
        "SPT_GetSyscallNumber",
        "SPT_PopulateSyscalls",
        "SPT_GetSyscallAddress",
        "SPT_GetRandomSyscallAddress",
    ]
    DONUT_SYSCALLS = [
        "NtCreateSection",
        "NtMapViewOfSection",
        "NtUnmapViewOfSection",
        "NtContinue",
        "NtClose",
        "NtWaitForSingleObject",
        "NtProtectVirtualMemory",
        "NtAllocateVirtualMemory",
        "NtCreateFile",
        "NtGetContextThread",
        "NtFreeVirtualMemory",
        "NtQueryVirtualMemory",
        "NtCreateThreadEx",
        "NtFlushInstructionCache",
    ]
    COMMON_SYSCALLS = [
        "NtCreateProcess",
        "NtCreateThreadEx",
        "NtOpenProcess",
        "NtOpenProcessToken",
        "NtTestAlert",
        "NtOpenThread",
        "NtSuspendProcess",
        "NtSuspendThread",
        "NtResumeProcess",
        "NtResumeThread",
        "NtGetContextThread",
        "NtSetContextThread",
        "NtClose",
        "NtReadVirtualMemory",
        "NtWriteVirtualMemory",
        "NtAllocateVirtualMemory",
        "NtProtectVirtualMemory",
        "NtFreeVirtualMemory",
        "NtQuerySystemInformation",
        "NtQueryDirectoryFile",
        "NtQueryInformationFile",
        "NtQueryInformationProcess",
        "NtQueryInformationThread",
        "NtCreateSection",
        "NtOpenSection",
        "NtMapViewOfSection",
        "NtUnmapViewOfSection",
        "NtAdjustPrivilegesToken",
        "NtDeviceIoControlFile",
        "NtQueueApcThread",
        "NtWaitForSingleObject",
        "NtWaitForMultipleObjects",
    ]
