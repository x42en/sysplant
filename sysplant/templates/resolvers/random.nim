proc SPT_GetRandomSyscallAddress(hash: DWORD): ULONG_PTR =
    # Ensure SPT_SyscallList is populated.
    SPT_PopulateSyscalls()
    
    let entries = toSeq(ssdt.values)
    # Pickup random non-hooked syscall to JUMP to
    var entry: Syscall = entries.sample()
    
    # Avoid random bad luck...
    while entry.ssn == ssdt[hash].ssn:
        entry = entries.sample()

    return cast[ULONG_PTR](entry.address)
