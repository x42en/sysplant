#[unsafe(no_mangle)]
pub unsafe extern "C" fn SPT_GetRandomSyscallAddress(function_hash: DWORD) -> PVOID {
    // Ensure SPT_SyscallList is populated.
    if SPT_PopulateSyscallList() == FALSE {
        return ptr::null_mut();
    }

    loop {
        // Pickup random non-hooked syscall to JUMP to
        let index = (rand() as DWORD) % SPT_SyscallList.Count;
        // Avoid random bad luck...
        if function_hash == SPT_SyscallList.Entries[index as usize].Hash {
            continue;
        }
        // Do not choose hooked functions
        if SPT_SyscallList.Entries[index as usize].SyscallAddress
            == SPT_SyscallList.Entries[index as usize].Address
        {
            continue;
        }
        // Otherwise it's all good
        return SPT_SyscallList.Entries[index as usize].SyscallAddress;
    }
}

unsafe extern "C" {
    fn rand() -> i32;
}
