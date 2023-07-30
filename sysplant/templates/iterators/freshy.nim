# Parse Export Directory and lookup syscall by name (start with Nt and not Ntdll), sort addresses to retrieve syscall number https://github.com/crummie5/FreshyCalls
iterator SPT_Iterator(mi: MODULEINFO): (int32, PBYTE) =
    # Extract headers
    let codeBase = mi.lpBaseOfDll
    let dosHeader = cast[PIMAGE_DOS_HEADER](codeBase)
    let ntHeader = cast[PIMAGE_NT_HEADERS](cast[DWORD_PTR](codeBase) + dosHeader.e_lfanew)
    
    # Get export table
    let directory = ntHeader.OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT]
    let exports = codeBase{directory.VirtualAddress}[PIMAGE_EXPORT_DIRECTORY]
    
    var
        nameRef = codeBase{exports.AddressOfNames}[PDWORD]
        funcRef = codeBase{exports.AddressOfFunctions}[PDWORD]
        ordinal = codeBase{exports.AddressOfNameOrdinals}[PWORD]
    
    # Search Begin Address in Export Table
    for j in 0 ..< exports.NumberOfFunctions:
        let
            name = $(codeBase{nameRef[]}[LPCSTR])
            offset = funcRef[ordinal[j][int]]
            address = codeBase{offset}[PBYTE]

        # Check offset with current function, ensure this is a syscall
        if name.startsWith("Nt") and not name.startsWith("Ntdll"):
            let hash: int32 = SPT_HashSyscallName(name)
            # Calculate jmp address avoiding EDR hooks
            yield (hash, address)
            
        ++nameRef

proc SPT_PopulateSyscalls =
    # Return short when work is already done
    if len(ssdt) > 0:
        return
    
    # Could set arg parse to check different process
    let pid = GetCurrentProcessId()

    # Create module snapshot
    let hModule = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, pid)
    defer: CloseHandle(hModule)

    # Store process handle
    let handle = OpenProcess(PROCESS_ALL_ACCESS, FALSE, pid)

    type Entry = tuple
        address: PBYTE
        hash: int32
    
    var
        me32: MODULEENTRY32
        mi: MODULEINFO
        tmp: seq[Entry]
    
    me32.dwSize = cast[DWORD](sizeof(MODULEENTRY32))

    # SKip to ntdll.dll
    hModule.Module32First(addr me32)
    # NTDLL.dll is not guaranteed to be first
    while hModule.Module32Next(addr me32):
        # Detect \ntdll.dll
        if "92110116100108108461001081080" in me32.szExePath.join():
            break
    
    handle.GetModuleInformation(me32.hModule, addr mi, cast[DWORD](sizeof(mi)))

    # Resolve address
    for hash, address in mi.SPT_Iterator():
        tmp.add((address, hash))
    
    # Sort syscalls by address
    tmp.sort(system.cmp)

    var padding = 0x0
    # Register syscalls
    for i in 0 ..< len(tmp):
        let
            address = tmp[i][0]
            hash = tmp[i][1]
        
        # All syscall stub are identical for a Windows version
        if padding == 0x0:
            padding = SPT_DetectPadding(address)

        ssdt[hash] = Syscall(address: address[PVOID], ssn: i[int32], syscallAddress: address{padding}[PVOID])

    return