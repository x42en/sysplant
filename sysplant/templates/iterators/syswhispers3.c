PVOID SC_Address(PVOID NtApiAddress)
{
    DWORD searchLimit = 512;
    PVOID SyscallAddress;

#ifdef _WIN64
    // If the process is 64-bit on a 64-bit OS, we need to search for syscall
    BYTE syscall_code[] = {0x0f, 0x05, 0xc3};
    ULONG distance_to_syscall = 0x12;
#else
    // If the process is 32-bit on a 32-bit OS, we need to search for sysenter
    BYTE syscall_code[] = {0x0f, 0x34, 0xc3};
    ULONG distance_to_syscall = 0x0f;
#endif

#ifdef _M_IX86
    // If the process is 32-bit on a 64-bit OS, we need to jump to WOW32Reserved
    if (local_is_wow64())
    {
        return NULL;
    }
#endif

    // we don't really care if there is a 'jmp' between
    // NtApiAddress and the 'syscall; ret' instructions
    SyscallAddress = SPT_RVA2VA(PVOID, NtApiAddress, distance_to_syscall);

    if (!memcmp((PVOID)syscall_code, SyscallAddress, sizeof(syscall_code)))
    {
        return SyscallAddress;
    }

    // the 'syscall; ret' intructions have not been found,
    // we will try to use one near it, similarly to HalosGate

    for (ULONG32 num_jumps = 1; num_jumps < searchLimit; num_jumps++)
    {
        // let's try with an Nt* API below our syscall
        SyscallAddress = SPT_RVA2VA(
            PVOID,
            NtApiAddress,
            distance_to_syscall + num_jumps * 0x20);
        if (!memcmp((PVOID)syscall_code, SyscallAddress, sizeof(syscall_code)))
        {
            return SyscallAddress;
        }

        // let's try with an Nt* API above our syscall
        SyscallAddress = SPT_RVA2VA(
            PVOID,
            NtApiAddress,
            distance_to_syscall - num_jumps * 0x20);
        if (!memcmp((PVOID)syscall_code, SyscallAddress, sizeof(syscall_code)))
        {
            return SyscallAddress;
        }
    }

    return NULL;
}

// Parse Export Directory and lookup syscall by name (start with Nt and not Ntdll), sort addresses to retrieve syscall number https://github.com/crummie5/FreshyCalls
BOOL SPT_PopulateSyscallList()
{
    // Return early if the list is already populated.
    if (SPT_SyscallList.Count) return TRUE;

    #ifdef _WIN64
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

    DWORD NumberOfNames = ExportDirectory->NumberOfNames;
    PDWORD Functions = SPT_RVA2VA(PDWORD, DllBase, ExportDirectory->AddressOfFunctions);
    PDWORD Names = SPT_RVA2VA(PDWORD, DllBase, ExportDirectory->AddressOfNames);
    PWORD Ordinals = SPT_RVA2VA(PWORD, DllBase, ExportDirectory->AddressOfNameOrdinals);

    // Populate SPT_SyscallList with unsorted Zw* entries.
    DWORD i = 0;
    WORD padding = 0x0;
    PSPT_SYSCALL_ENTRY Entries = SPT_SyscallList.Entries;
    do
    {
        PCHAR FunctionName = SPT_RVA2VA(PCHAR, DllBase, Names[NumberOfNames - 1]);
        PVOID FunctionAddress = SPT_RVA2VA(PVOID, DllBase, Functions[Ordinals[NumberOfNames - 1]]);

        // Is this a system call?
        if (*(USHORT*)FunctionName == 0x775a)
        {
            Entries[i].Hash = SPT_HashSyscallName(FunctionName);
            Entries[i].Address = FunctionAddress;

            // All syscall stubs are identical for a Windows version
            if (padding == 0x0) {
                padding = SPT_DetectPadding(FunctionAddress);
            }

            Entries[i].SyscallAddress = SPT_RVA2VA(PVOID, Entries[i].Address, padding);

            i++;
            if (i == SPT_MAX_ENTRIES) break;
        }
    } while (--NumberOfNames);

    // Save total number of system calls found.
    SPT_SyscallList.Count = i;

    // Sort the list by address in ascending order.
    for (DWORD i = 0; i < SPT_SyscallList.Count - 1; i++)
    {
        for (DWORD j = 0; j < SPT_SyscallList.Count - i - 1; j++)
        {
            if (Entries[j].Address > Entries[j + 1].Address)
            {
                // Swap entries.
                SPT_SYSCALL_ENTRY TempEntry;

                TempEntry.Hash = Entries[j].Hash;
                TempEntry.Address = Entries[j].Address;
                TempEntry.SyscallAddress = Entries[j].SyscallAddress;

                Entries[j].Hash = Entries[j + 1].Hash;
                Entries[j].Address = Entries[j + 1].Address;
                Entries[j].SyscallAddress = Entries[j + 1].SyscallAddress;

                Entries[j + 1].Hash = TempEntry.Hash;
                Entries[j + 1].Address = TempEntry.Address;
                Entries[j + 1].SyscallAddress = TempEntry.SyscallAddress;
            }
        }
    }

    return TRUE;
}