proc SPT_GetSyscallAddress(hash: DWORD): ULONG_PTR =
    # Ensure SPT_SyscallList is populated.
    SPT_PopulateSyscalls()
    
    return cast[ULONG_PTR](ssdt[hash].address)
