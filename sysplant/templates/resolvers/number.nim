proc SPT_GetSyscallNumber(hash: DWORD): int =
    # Ensure SPT_SyscallList is populated.
    SPT_PopulateSyscalls()
    
    return ssdt[hash].ssn
