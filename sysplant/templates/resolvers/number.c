EXTERN_C DWORD SPT_GetSyscallNumber(DWORD FunctionHash)
{
    // Ensure SPT_SyscallList is populated.
    if (!SPT_PopulateSyscallList())
        return -1;

    for (DWORD i = 0; i < SPT_SyscallList.Count; i++)
    {
        if (FunctionHash == SPT_SyscallList.Entries[i].Hash)
        {
            return i;
        }
    }

    return -1;
}
