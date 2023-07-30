proc SPT_GetRandomSyscallAddress(hash: DWORD): ULONG_PTR =
    # Ensure SPT_SyscallList is populated.
    SPT_PopulateSyscalls()
    
    let entries = toSeq(ssdt.values)
    
    var entry: Syscall
    while true:
        # Pickup random non-hooked syscall to JUMP to
        entry = entries.sample()
        # Avoid random bad luck...
        if entry.ssn == ssdt[hash].ssn:
            continue
        # Do not choose hooked functions
        if entry.syscallAddress == entry.address:
            continue
        # Otherwise it's all good
        break

    return cast[ULONG_PTR](entry.syscallAddress)
