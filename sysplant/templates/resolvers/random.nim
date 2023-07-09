proc SPT_GetRandomSyscallAddress(hash: DWORD): ULONG_PTR =
    let entries = toSeq(ssdt.values)
    # Pickup random non-hooked syscall to JUMP to
    let entry: Syscall = entries.sample()
    return cast[ULONG_PTR](entry.address)