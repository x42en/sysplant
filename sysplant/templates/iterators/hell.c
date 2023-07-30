int isClean(PBYTE FunctionAddress, WORD cw) {
    // First opcodes should be :
    //    MOV R10, RCX
    //    MOV RCX, <syscall>
    if (*(FunctionAddress + cw) == 0x4c
        && *(FunctionAddress + 1 + cw) == 0x8b
        && *(FunctionAddress + 2 + cw) == 0xd1
        && *(FunctionAddress + 3 + cw) == 0xb8
        && *(FunctionAddress + 6 + cw) == 0x00
        && *(FunctionAddress + 7 + cw) == 0x00) {
        
        // Detect Syscall number
        BYTE high = *(FunctionAddress + 5 + cw);
        BYTE low = *(FunctionAddress + 4 + cw);

        return (high << 8) | low;
    }

    return -1;
}

// Parse Export Directory and look for opcode scheme: https://github.com/am0nsec/HellsGate/blob/master/HellsGate/main.c
BOOL SPT_PopulateSyscallList(void)
{
    // Return early if the list is already populated.
    if (SPT_SyscallList.Count) return TRUE;

#if defined(_WIN64)
    PSPT_PEB Peb = (PSPT_PEB)__readgsqword(0x60);
#else
    PSPT_PEB Peb = (PSPT_PEB)__readfsdword(0x30);
#endif
    PSPT_PEB_LDR_DATA Ldr = Peb->Ldr;
    PIMAGE_EXPORT_DIRECTORY ExportDirectory = NULL;
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
        DWORD VirtualAddress = DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress;
        if (VirtualAddress == 0) continue;

        ExportDirectory = (PIMAGE_EXPORT_DIRECTORY)SPT_RVA2VA(ULONG_PTR, DllBase, VirtualAddress);

        // If this is NTDLL.dll, exit loop.
        PCHAR DllName = SPT_RVA2VA(PCHAR, DllBase, ExportDirectory->Name);

        if ((*(ULONG*)DllName | 0x20202020) != 0x6c64746e) continue;
        if ((*(ULONG*)(DllName + 4) | 0x20202020) == 0x6c642e6c) break;
    }

    if (!ExportDirectory) return FALSE;

    PDWORD Functions = SPT_RVA2VA(PDWORD, DllBase, ExportDirectory->AddressOfFunctions);
    PDWORD Names = SPT_RVA2VA(PDWORD, DllBase, ExportDirectory->AddressOfNames);
    PWORD Ordinals = SPT_RVA2VA(PWORD, DllBase, ExportDirectory->AddressOfNameOrdinals);

    // Create Syscall list Entry
    PSPT_SYSCALL_ENTRY Entries = SPT_SyscallList.Entries;
    
    for (DWORD cx = 0; cx < ExportDirectory->NumberOfNames; cx++) {
        PCHAR FunctionName = SPT_RVA2VA(PCHAR, DllBase, Names[cx]);
        PVOID FunctionAddress = SPT_RVA2VA(PVOID, DllBase, Functions[Ordinals[cx]]);
        
		// Quick and dirty fix in case the function has been hooked
        WORD cw = 0;
        int ssn = -1;
        WORD padding = 0x0;
        while (TRUE) {
            // check if syscall, in this case we are too far
            if (*((PBYTE)FunctionAddress + cw) == 0x0f && *((PBYTE)FunctionAddress + cw + 1) == 0x05)
                break;

            // check if ret, in this case we are also probaly too far
            if (*((PBYTE)FunctionAddress + cw) == 0xc3)
                break;

            ssn = isClean((PBYTE)FunctionAddress, cw);
            if (ssn > -1) {
                Entries[ssn].Hash = SPT_HashSyscallName(FunctionName);
                Entries[ssn].Address = FunctionAddress;
                
                // All syscall stubs are identical for a Windows version
                if (padding == 0x0) {
                    padding = SPT_DetectPadding(Entries[ssn].Address);
                }

                Entries[ssn].SyscallAddress = SPT_RVA2VA(PVOID, Entries[ssn].Address, padding);

                // Save total number of system calls found.
                if (ssn > SPT_SyscallList.Count) {
                    SPT_SyscallList.Count = ssn + 1;
                }
                break;
            }
            
            cw++;
        };
	}

    return TRUE;
}
