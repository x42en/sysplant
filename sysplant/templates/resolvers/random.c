EXTERN_C PVOID SPT_GetRandomSyscallAddress(DWORD FunctionHash)
{
    // Ensure SPT_SyscallList is populated.
    if (!SPT_PopulateSyscallList()) return NULL;

    DWORD index = ((DWORD) rand()) % SPT_SyscallList.Count;

    while (FunctionHash == SPT_SyscallList.Entries[index].Hash){
        // Spoofing the syscall return address
        index = ((DWORD) rand()) % SPT_SyscallList.Count;
    }
    return SPT_SyscallList.Entries[index].SyscallAddress;
}