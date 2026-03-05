unsafe fn is_clean(function_address: PBYTE, cw: u16) -> i32 {
    // First opcodes should be:
    //    MOV R10, RCX
    //    MOV RCX, <syscall>
    if *function_address.add(cw as usize) == 0x4c
        && *function_address.add(1 + cw as usize) == 0x8b
        && *function_address.add(2 + cw as usize) == 0xd1
        && *function_address.add(3 + cw as usize) == 0xb8
        && *function_address.add(6 + cw as usize) == 0x00
        && *function_address.add(7 + cw as usize) == 0x00
    {
        let high = *function_address.add(5 + cw as usize);
        let low = *function_address.add(4 + cw as usize);
        return ((high as i32) << 8) | (low as i32);
    }
    -1
}

// Parse Export Directory and look for opcode scheme:
// https://github.com/am0nsec/HellsGate/blob/master/HellsGate/main.c
#[unsafe(no_mangle)]
unsafe fn SPT_PopulateSyscallList() -> BOOL {
    // Return early if the list is already populated.
    if SPT_SyscallList.Count != 0 {
        return TRUE;
    }

    let peb = get_peb();
    let ldr = (*peb).Ldr;
    let mut export_directory: *mut IMAGE_EXPORT_DIRECTORY = ptr::null_mut();
    let mut dll_base: PVOID = ptr::null_mut();

    // Get the DllBase address of NTDLL.dll.
    let mut ldr_entry = (*ldr).Reserved2[1] as *mut SPT_LDR_DATA_TABLE_ENTRY;
    while !(*ldr_entry).DllBase.is_null() {
        dll_base = (*ldr_entry).DllBase;
        let dos_header = dll_base as *const IMAGE_DOS_HEADER;
        let nt_headers = SPT_RVA2VA!(*const IMAGE_NT_HEADERS64, dll_base, (*dos_header).e_lfanew);
        let data_directory = (*nt_headers).OptionalHeader.DataDirectory.as_ptr();
        let va = (*data_directory.add(IMAGE_DIRECTORY_ENTRY_EXPORT)).VirtualAddress;
        if va == 0 {
            ldr_entry = (*ldr_entry).Reserved1[0] as *mut SPT_LDR_DATA_TABLE_ENTRY;
            continue;
        }

        export_directory = SPT_RVA2VA!(*mut IMAGE_EXPORT_DIRECTORY, dll_base, va);

        // If this is NTDLL.dll, exit loop.
        let dll_name = SPT_RVA2VA!(*const u8, dll_base, (*export_directory).Name);
        if (*(dll_name as *const u32) | 0x20202020) != 0x6c64746e {
            ldr_entry = (*ldr_entry).Reserved1[0] as *mut SPT_LDR_DATA_TABLE_ENTRY;
            continue;
        }
        if (*(dll_name.add(4) as *const u32) | 0x20202020) == 0x6c642e6c {
            break;
        }
        ldr_entry = (*ldr_entry).Reserved1[0] as *mut SPT_LDR_DATA_TABLE_ENTRY;
    }

    if export_directory.is_null() {
        return FALSE;
    }

    let functions = SPT_RVA2VA!(*const DWORD, dll_base, (*export_directory).AddressOfFunctions);
    let names = SPT_RVA2VA!(*const DWORD, dll_base, (*export_directory).AddressOfNames);
    let ordinals = SPT_RVA2VA!(*const WORD, dll_base, (*export_directory).AddressOfNameOrdinals);

    let entries = SPT_SyscallList.Entries.as_mut_ptr();

    for cx in 0..(*export_directory).NumberOfNames {
        let function_name = SPT_RVA2VA!(*const i8, dll_base, *names.add(cx as usize));
        let function_address = SPT_RVA2VA!(PVOID, dll_base, *functions.add(*ordinals.add(cx as usize) as usize));

        // Quick and dirty fix in case the function has been hooked
        let mut cw: u16 = 0;
        let mut ssn: i32 = -1;
        let mut padding: u16 = 0;
        loop {
            // check if syscall, in this case we are too far
            if *(function_address as PBYTE).add(cw as usize) == 0x0f
                && *(function_address as PBYTE).add(cw as usize + 1) == 0x05
            {
                break;
            }

            // check if ret, in this case we are also probably too far
            if *(function_address as PBYTE).add(cw as usize) == 0xc3 {
                break;
            }

            ssn = is_clean(function_address as PBYTE, cw);
            if ssn > -1 {
                (*entries.add(ssn as usize)).Hash = SPT_HashSyscallName(function_name);
                (*entries.add(ssn as usize)).Address = function_address;

                if padding == 0 {
                    padding = SPT_DetectPadding((*entries.add(ssn as usize)).Address);
                }

                (*entries.add(ssn as usize)).SyscallAddress =
                    SPT_RVA2VA!(PVOID, (*entries.add(ssn as usize)).Address, padding);

                if ssn as DWORD > SPT_SyscallList.Count {
                    SPT_SyscallList.Count = ssn as DWORD + 1;
                }
                break;
            }

            cw += 1;
        }
    }

    TRUE
}
