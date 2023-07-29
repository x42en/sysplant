EXTERN_C PVOID SPT_GetSyscallAddress(DWORD FunctionHash)
{
    for (DWORD i = 0; i < SPT_SyscallList.Count; i++)
    {
        if (FunctionHash == SPT_SyscallList.Entries[i].Hash)
        {
            return SPT_SyscallList.Entries[i].Address;
        }
    }

    return NULL;
}