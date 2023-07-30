// Parse Exception Directory and lookup syscall by name (sort by ssn number) https://www.mdsec.co.uk/2022/04/resolving-system-service-numbers-using-the-exception-directory/
BOOL SPT_PopulateSyscallList(void)
{
    // Return early if the list is already populated.
    if (SPT_SyscallList.Count) return TRUE;

#if defined(_WIN64)
    // If the process is 64-bit on a 64-bit OS, we need to search for syscall
    PSPT_PEB Peb = (PSPT_PEB)__readgsqword(0x60);
#else
    // If the process is 32-bit on a 32-bit OS, we need to search for sysenter
    PSPT_PEB Peb = (PSPT_PEB)__readfsdword(0x30);
#endif
    PSPT_PEB_LDR_DATA Ldr = Peb->Ldr;
    PIMAGE_EXPORT_DIRECTORY ExportDirectory = NULL;
    PIMAGE_RUNTIME_FUNCTION_ENTRY RuntimeFunctions = NULL;
    PVOID DllBase = NULL;
    

    // Get the DllBase address of NTDLL.dll. NTDLL is not guaranteed to be the second
    // in the list, so it's safer to loop through the full list and find it.
    PSPT_LDR_DATA_TABLE_ENTRY LdrEntry;
    for (LdrEntry = (PSPT_LDR_DATA_TABLE_ENTRY)Ldr->Reserved2[1]; LdrEntry->DllBase != NULL; LdrEntry = (PSPT_LDR_DATA_TABLE_ENTRY)LdrEntry->Reserved1[0])
    {
        DllBase = LdrEntry->DllBase;
        PIMAGE_DOS_HEADER DosHeader = (PIMAGE_DOS_HEADER)DllBase;
        PIMAGE_NT_HEADERS NtHeaders = SPT_RVA2VA(PIMAGE_NT_HEADERS, DllBase, DosHeader->e_lfanew);
        PIMAGE_DATA_DIRECTORY DataDirectory = (PIMAGE_DATA_DIRECTORY)NtHeaders->OptionalHeader.DataDirectory;
        DWORD ExportVirtualAddress = DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress;
        if (ExportVirtualAddress == 0) continue; // no export table? skip

        // Load ExportDirectory
        ExportDirectory = (PIMAGE_EXPORT_DIRECTORY)SPT_RVA2VA(ULONG_PTR, DllBase, ExportVirtualAddress);
        // Load the Exception Directory.
        DWORD ExceptionVirtualAddress = DataDirectory[IMAGE_DIRECTORY_ENTRY_EXCEPTION].VirtualAddress;
        RuntimeFunctions = SPT_RVA2VA(PIMAGE_RUNTIME_FUNCTION_ENTRY, DllBase, ExceptionVirtualAddress);

        // If this is NTDLL.dll, exit loop.
        PCHAR DllName = SPT_RVA2VA(PCHAR, DllBase, ExportDirectory->Name);

        // Ntdll.dll check corrected to remove compiler warning
        if ((*(ULONG*)DllName | 0x20202020) != 0x6c64746e) continue;
        if ((*(ULONG*)(DllName + 4) | 0x20202020) == 0x6c642e6c) break;
    }

    if (!RuntimeFunctions) return FALSE;

    // Load the Export Address Table
    PDWORD Functions = SPT_RVA2VA(PDWORD, DllBase, ExportDirectory->AddressOfFunctions);
    PDWORD Names = SPT_RVA2VA(PDWORD, DllBase, ExportDirectory->AddressOfNames);
    PWORD Ordinals = SPT_RVA2VA(PWORD, DllBase, ExportDirectory->AddressOfNameOrdinals);

    // Create Syscall list Entry
    PSPT_SYSCALL_ENTRY Entries = SPT_SyscallList.Entries;

    WORD ssn = 0;
    WORD padding = 0x0;
    // Search runtime function table.
    for (DWORD i = 0; RuntimeFunctions[i].BeginAddress; i++) {
        // Search export address table.
        for (DWORD cx = 0; cx < ExportDirectory->NumberOfNames; cx++) {
            PCHAR FunctionName = SPT_RVA2VA(PCHAR, DllBase, Names[cx]);
            PVOID FunctionAddress = SPT_RVA2VA(PVOID, DllBase, Functions[Ordinals[cx]]);

            // begin address rva?
            if (Functions[Ordinals[cx]] == RuntimeFunctions[i].BeginAddress) {
                // Is this a system call?
                if (*(USHORT*)FunctionName == 0x775a)
                {
                    Entries[ssn].Hash = SPT_HashSyscallName(FunctionName);
                    Entries[ssn].Address = FunctionAddress;

                    // All syscall stubs are identical for a Windows version
                    if (padding == 0x0) {
                        padding = SPT_DetectPadding(FunctionAddress);
                    }

                    // Set syscall entry with appropriate padding
                    Entries[ssn].SyscallAddress = SPT_RVA2VA(PVOID, Entries[ssn].Address, padding);
                    
                    // Increase the ssn value
                    ssn++;

                    // Update number of system calls found.
                    SPT_SyscallList.Count = ssn;

                    // No need to go further for this one
                    break;
                }
            }
        }
    }

    return TRUE;
}