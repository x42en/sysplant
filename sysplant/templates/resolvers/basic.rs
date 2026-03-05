#[unsafe(no_mangle)]
pub unsafe extern "C" fn SPT_GetSyscallAddress(function_hash: DWORD) -> PVOID {
    // Ensure SPT_SyscallList is populated.
    if SPT_PopulateSyscallList() == FALSE {
        return ptr::null_mut();
    }

    for i in 0..SPT_SyscallList.Count as usize {
        if function_hash == SPT_SyscallList.Entries[i].Hash {
            return SPT_SyscallList.Entries[i].Address;
        }
    }

    ptr::null_mut()
}
