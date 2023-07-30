EXTERN_C PVOID SPT_GetRandomSyscallAddress(DWORD FunctionHash)
{
    // Ensure SPT_SyscallList is populated.
    if (!SPT_PopulateSyscallList()) return NULL;

    DWORD index;

    while (TRUE){
        // Pickup random non-hooked syscall to JUMP to
        index = ((DWORD) rand()) % SPT_SyscallList.Count;
        // Avoid random bad luck...
        if (FunctionHash == SPT_SyscallList.Entries[index].Hash) {
            continue;
        }
        // Do not choose hooked functions
        if (SPT_SyscallList.Entries[index].SyscallAddress == SPT_SyscallList.Entries[index].Address) {
            continue;
        }
        // Otherwise it's all good
        break;
    }
    
    return SPT_SyscallList.Entries[index].SyscallAddress;
}
