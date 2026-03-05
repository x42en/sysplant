unsafe fn sc_address(nt_api_address: PVOID) -> PVOID {
    let search_limit: u32 = 512;

    #[cfg(target_arch = "x86_64")]
    let syscall_code: [u8; 3] = [0x0f, 0x05, 0xc3];
    #[cfg(target_arch = "x86_64")]
    let distance_to_syscall: u32 = 0x12;

    #[cfg(target_arch = "x86")]
    let syscall_code: [u8; 3] = [0x0f, 0x34, 0xc3];
    #[cfg(target_arch = "x86")]
    let distance_to_syscall: u32 = 0x0f;

    // we don't really care if there is a 'jmp' between
    // NtApiAddress and the 'syscall; ret' instructions
    let syscall_address = SPT_RVA2VA!(PVOID, nt_api_address, distance_to_syscall);

    if core::slice::from_raw_parts(syscall_address as *const u8, 3) == syscall_code {
        return syscall_address;
    }

    // the 'syscall; ret' instructions have not been found,
    // we will try to use one near it, similarly to HalosGate
    for num_jumps in 1..search_limit {
        // let's try with an Nt* API below our syscall
        let addr_below = SPT_RVA2VA!(
            PVOID,
            nt_api_address,
            distance_to_syscall + num_jumps * 0x20
        );
        if core::slice::from_raw_parts(addr_below as *const u8, 3) == syscall_code {
            return addr_below;
        }

        // let's try with an Nt* API above our syscall
        let addr_above = SPT_RVA2VA!(
            PVOID,
            nt_api_address,
            distance_to_syscall.wrapping_sub(num_jumps * 0x20)
        );
        if core::slice::from_raw_parts(addr_above as *const u8, 3) == syscall_code {
            return addr_above;
        }
    }

    ptr::null_mut()
}

// Parse Export Directory and lookup syscall by name (start with Nt and not Ntdll),
// sort addresses to retrieve syscall number (SysWhispers3 variant)
// https://github.com/crummie5/FreshyCalls
#[unsafe(no_mangle)]
unsafe fn SPT_PopulateSyscallList() -> BOOL {
    if SPT_SyscallList.Count != 0 {
        return TRUE;
    }

    let peb = get_peb();
    let ldr = (*peb).Ldr;
    let mut export_directory: *mut IMAGE_EXPORT_DIRECTORY = ptr::null_mut();
    let mut dll_base: PVOID = ptr::null_mut();

    let mut ldr_entry = (*ldr).InMemoryOrderModuleList.Flink as *mut SPT_LDR_DATA_TABLE_ENTRY;
    while !(*ldr_entry).DllBase.is_null() {
        dll_base = (*ldr_entry).DllBase;
        let dos_header = dll_base as *const IMAGE_DOS_HEADER;
        let nt_headers = SPT_RVA2VA!(*const IMAGE_NT_HEADERS64, dll_base, (*dos_header).e_lfanew);
        let data_directory = (*nt_headers).OptionalHeader.DataDirectory.as_ptr();
        let va = (*data_directory.add(IMAGE_DIRECTORY_ENTRY_EXPORT)).VirtualAddress;
        if va == 0 {
            ldr_entry = (*ldr_entry).InMemoryOrderLinks.Flink as *mut SPT_LDR_DATA_TABLE_ENTRY;
            continue;
        }

        export_directory = SPT_RVA2VA!(*mut IMAGE_EXPORT_DIRECTORY, dll_base, va);

        let dll_name = SPT_RVA2VA!(*const u8, dll_base, (*export_directory).Name);
        if (*(dll_name as *const u32) | 0x20202020) != 0x6c64746e {
            ldr_entry = (*ldr_entry).InMemoryOrderLinks.Flink as *mut SPT_LDR_DATA_TABLE_ENTRY;
            continue;
        }
        if (*(dll_name.add(4) as *const u32) | 0x20202020) == 0x6c642e6c {
            break;
        }
        ldr_entry = (*ldr_entry).InMemoryOrderLinks.Flink as *mut SPT_LDR_DATA_TABLE_ENTRY;
    }

    if export_directory.is_null() {
        return FALSE;
    }

    let mut number_of_names = (*export_directory).NumberOfNames;
    let functions = SPT_RVA2VA!(*const DWORD, dll_base, (*export_directory).AddressOfFunctions);
    let names = SPT_RVA2VA!(*const DWORD, dll_base, (*export_directory).AddressOfNames);
    let ordinals = SPT_RVA2VA!(*const WORD, dll_base, (*export_directory).AddressOfNameOrdinals);

    let mut i: u32 = 0;
    let mut padding: u16 = 0;
    let entries = SPT_SyscallList.Entries.as_mut_ptr();
    while number_of_names > 0 {
        number_of_names -= 1;
        let function_name = SPT_RVA2VA!(*const i8, dll_base, *names.add(number_of_names as usize));
        let function_address = SPT_RVA2VA!(PVOID, dll_base, *functions.add(*ordinals.add(number_of_names as usize) as usize));

        // Is this a system call? "Zw" == 0x775a
        if *(function_name as *const u16) == 0x775a {
            (*entries.add(i as usize)).Hash = SPT_HashSyscallName(function_name);
            (*entries.add(i as usize)).Address = function_address;

            if padding == 0 {
                padding = SPT_DetectPadding(function_address);
            }

            (*entries.add(i as usize)).SyscallAddress =
                SPT_RVA2VA!(PVOID, (*entries.add(i as usize)).Address, padding);

            i += 1;
            if i == SPT_MAX_ENTRIES as u32 {
                break;
            }
        }
    }

    SPT_SyscallList.Count = i;

    // Sort the list by address in ascending order (bubble sort).
    for i in 0..(SPT_SyscallList.Count as usize).saturating_sub(1) {
        for j in 0..(SPT_SyscallList.Count as usize - i - 1) {
            if (*entries.add(j)).Address as usize > (*entries.add(j + 1)).Address as usize {
                let temp_hash = (*entries.add(j)).Hash;
                let temp_addr = (*entries.add(j)).Address;
                let temp_sys = (*entries.add(j)).SyscallAddress;

                (*entries.add(j)).Hash = (*entries.add(j + 1)).Hash;
                (*entries.add(j)).Address = (*entries.add(j + 1)).Address;
                (*entries.add(j)).SyscallAddress = (*entries.add(j + 1)).SyscallAddress;

                (*entries.add(j + 1)).Hash = temp_hash;
                (*entries.add(j + 1)).Address = temp_addr;
                (*entries.add(j + 1)).SyscallAddress = temp_sys;
            }
        }
    }

    TRUE
}
