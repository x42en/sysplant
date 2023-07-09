proc SPT_GetSyscallAddress(hash: DWORD): ULONG_PTR =
    return cast[ULONG_PTR](ssdt[hash].address)