EXTERN_C PVOID SPT_GetSyscallAddress(DWORD FunctionHash);
EXTERN_C PVOID SPT_GetSyscallAddress(DWORD FunctionHash)
{
    for (DWORD i = 0; i < SW3_SyscallList.Count; i++)
    {
        if (FunctionHash == SW3_SyscallList.Entries[i].Hash)
        {
            return SW3_SyscallList.Entries[i].SyscallAddress;
        }
    }

    return NULL;
}