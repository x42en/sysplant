// Parse Exception Directory and lookup syscall by name (sort by ssn number)
// https://www.mdsec.co.uk/2022/04/resolving-system-service-numbers-using-the-exception-directory/
#[unsafe(no_mangle)]
unsafe fn SPT_PopulateSyscallList() -> BOOL {
    // Return early if the list is already populated.
    if SPT_SyscallList.Count != 0 {
        return TRUE;
    }

    let peb = get_peb();
    let ldr = (*peb).Ldr;
    let mut export_directory: *mut IMAGE_EXPORT_DIRECTORY = ptr::null_mut();
    let mut runtime_functions: *mut IMAGE_RUNTIME_FUNCTION_ENTRY = ptr::null_mut();
    let mut dll_base: PVOID = ptr::null_mut();

    // Get the DllBase address of NTDLL.dll. NTDLL is not guaranteed to be the second
    // in the list, so it's safer to loop through the full list and find it.
    let mut ldr_entry = (*ldr).Reserved2[1] as *mut SPT_LDR_DATA_TABLE_ENTRY;
    while !(*ldr_entry).DllBase.is_null() {
        dll_base = (*ldr_entry).DllBase;
        let dos_header = dll_base as *const IMAGE_DOS_HEADER;
        let nt_headers = SPT_RVA2VA!(*const IMAGE_NT_HEADERS64, dll_base, (*dos_header).e_lfanew);
        let data_directory = (*nt_headers).OptionalHeader.DataDirectory.as_ptr();
        let export_va = (*data_directory.add(IMAGE_DIRECTORY_ENTRY_EXPORT)).VirtualAddress;
        if export_va == 0 {
            ldr_entry = (*ldr_entry).Reserved1[0] as *mut SPT_LDR_DATA_TABLE_ENTRY;
            continue;
        }

        // Load ExportDirectory
        export_directory = SPT_RVA2VA!(*mut IMAGE_EXPORT_DIRECTORY, dll_base, export_va);
        // Load the Exception Directory.
        let exception_va = (*data_directory.add(IMAGE_DIRECTORY_ENTRY_EXCEPTION)).VirtualAddress;
        runtime_functions = SPT_RVA2VA!(*mut IMAGE_RUNTIME_FUNCTION_ENTRY, dll_base, exception_va);

        // If this is NTDLL.dll, exit loop.
        let dll_name = SPT_RVA2VA!(*const u8, dll_base, (*export_directory).Name);
        // "ntdl" case-insensitive check
        if (*(dll_name as *const u32) | 0x20202020) != 0x6c64746e {
            ldr_entry = (*ldr_entry).Reserved1[0] as *mut SPT_LDR_DATA_TABLE_ENTRY;
            continue;
        }
        // "l.dl" case-insensitive check
        if (*(dll_name.add(4) as *const u32) | 0x20202020) == 0x6c642e6c {
            break;
        }
        ldr_entry = (*ldr_entry).Reserved1[0] as *mut SPT_LDR_DATA_TABLE_ENTRY;
    }

    if runtime_functions.is_null() {
        return FALSE;
    }

    // Load the Export Address Table
    let functions = SPT_RVA2VA!(*const DWORD, dll_base, (*export_directory).AddressOfFunctions);
    let names = SPT_RVA2VA!(*const DWORD, dll_base, (*export_directory).AddressOfNames);
    let ordinals = SPT_RVA2VA!(*const WORD, dll_base, (*export_directory).AddressOfNameOrdinals);

    let entries = SPT_SyscallList.Entries.as_mut_ptr();
    let mut ssn: u16 = 0;
    let mut padding: u16 = 0;

    // Search runtime function table.
    let mut i: u32 = 0;
    while (*runtime_functions.add(i as usize)).BeginAddress != 0 {
        // Search export address table.
        for cx in 0..(*export_directory).NumberOfNames {
            let function_name = SPT_RVA2VA!(*const i8, dll_base, *names.add(cx as usize));
            let function_address = SPT_RVA2VA!(PVOID, dll_base, *functions.add(*ordinals.add(cx as usize) as usize));

            // begin address rva?
            if *functions.add(*ordinals.add(cx as usize) as usize) == (*runtime_functions.add(i as usize)).BeginAddress {
                // Is this a system call? "Zw" == 0x775a
                if *(function_name as *const u16) == 0x775a {
                    (*entries.add(ssn as usize)).Hash = SPT_HashSyscallName(function_name);
                    (*entries.add(ssn as usize)).Address = function_address;

                    // All syscall stubs are identical for a Windows version
                    if padding == 0 {
                        padding = SPT_DetectPadding(function_address);
                    }

                    // Set syscall entry with appropriate padding
                    (*entries.add(ssn as usize)).SyscallAddress = SPT_RVA2VA!(PVOID, (*entries.add(ssn as usize)).Address, padding);

                    ssn += 1;
                    SPT_SyscallList.Count = ssn as DWORD;
                    break;
                }
            }
        }
        i += 1;
    }

    TRUE
}
