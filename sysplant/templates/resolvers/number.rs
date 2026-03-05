#[unsafe(no_mangle)]
pub unsafe extern "C" fn SPT_GetSyscallNumber(function_hash: DWORD) -> DWORD {
    // Ensure SPT_SyscallList is populated.
    if SPT_PopulateSyscallList() == FALSE {
        return u32::MAX; // -1 equivalent for unsigned
    }

    for i in 0..SPT_SyscallList.Count as usize {
        if function_hash == SPT_SyscallList.Entries[i].Hash {
            return i as DWORD;
        }
    }

    u32::MAX
}
