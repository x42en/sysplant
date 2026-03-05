const STEP_SIZE: i32 = 32;
const MAX_STEPS: i32 = 200;

unsafe fn is_clean(function_address: PBYTE, cw: u16, step: i32) -> i32 {
    let gap = step * STEP_SIZE;
    let offset = cw as i32 + gap;
    // First opcodes should be:
    //    MOV R10, RCX
    //    MOV RCX, <syscall>
    if *function_address.offset(offset as isize) == 0x4c
        && *function_address.offset((1 + offset) as isize) == 0x8b
        && *function_address.offset((2 + offset) as isize) == 0xd1
        && *function_address.offset((3 + offset) as isize) == 0xb8
        && *function_address.offset((6 + offset) as isize) == 0x00
        && *function_address.offset((7 + offset) as isize) == 0x00
    {
        let high = *function_address.offset((5 + offset) as isize);
        let low = *function_address.offset((4 + offset) as isize);
        return ((high as i32) << 8) | (low as i32) - step;
    }
    -1
}

// Parse Export Directory and look for opcode scheme (Tartarus's Gate variant):
// https://github.com/am0nsec/HellsGate/blob/master/HellsGate/main.c
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

    let functions = SPT_RVA2VA!(*const DWORD, dll_base, (*export_directory).AddressOfFunctions);
    let names = SPT_RVA2VA!(*const DWORD, dll_base, (*export_directory).AddressOfNames);
    let ordinals = SPT_RVA2VA!(*const WORD, dll_base, (*export_directory).AddressOfNameOrdinals);

    let entries = SPT_SyscallList.Entries.as_mut_ptr();

    for cx in 0..(*export_directory).NumberOfNames {
        let function_name = SPT_RVA2VA!(*const i8, dll_base, *names.add(cx as usize));
        let function_address = SPT_RVA2VA!(PVOID, dll_base, *functions.add(*ordinals.add(cx as usize) as usize));

        let mut cw: u16 = 0;
        let mut ssn: i32 = -1;
        let mut padding: u16 = 0;
        loop {
            if *(function_address as PBYTE).add(cw as usize) == 0x0f
                && *(function_address as PBYTE).add(cw as usize + 1) == 0x05
            {
                break;
            }

            if *(function_address as PBYTE).add(cw as usize) == 0xc3 {
                break;
            }

            ssn = is_clean(function_address as PBYTE, cw, 0);

            // Check current syscall is clean (Tartarus's method: JMP set on first or third instruction)
            if *(function_address as PBYTE).add(cw as usize) == 0xe9
                || *(function_address as PBYTE).add(3 + cw as usize) == 0xe9
            {
                for index in 1..=MAX_STEPS {
                    ssn = is_clean(function_address as PBYTE, cw, index);
                    if ssn > -1 {
                        break;
                    }
                    ssn = is_clean(function_address as PBYTE, cw, -index);
                    if ssn > -1 {
                        break;
                    }
                }
            }

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
