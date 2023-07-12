# Use RunTime Function table from exception directory to gather SSN: https://www.mdsec.co.uk/2022/04/resolving-system-service-numbers-using-the-exception-directory/
# Auto calculate syscall offset
iterator SPT_Iterator(mi: MODULEINFO): (DWORD, int, int64) =
    var
        i: int = 0
        ssn: int = 0
    
    # Extract headers
    let codeBase = mi.lpBaseOfDll
    let dosHeader = cast[PIMAGE_DOS_HEADER](codeBase)
    let ntHeader = cast[PIMAGE_NT_HEADERS](cast[DWORD_PTR](codeBase) + dosHeader.e_lfanew)
    
    # Get export table
    let directory = ntHeader.OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT]
    let exports = codeBase{directory.VirtualAddress}[PIMAGE_EXPORT_DIRECTORY]
    
    # Get runtime functions table
    let dirExcept = ntHeader.OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXCEPTION]
    let rtf = codeBase{dirExcept.VirtualAddress}[PIMAGE_RUNTIME_FUNCTION_ENTRY] 
    
    var padding = 0x0

    # Loop runtime function table
    while rtf[i].BeginAddress:
        let current = rtf[i].BeginAddress
        # Reset pointers
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
            if (offset == current) and name.startsWith("Zw"):
                let hash = SPT_HashSyscallName(name)
                # All syscall stub are identical for a Windows version
                if padding == 0x0:
                    # Calculate jmp address avoiding EDR hooks
                    while (address{padding}[] != 0x0f) and (address{padding + 1}[] != 0x05):
                        padding += 1
                
                yield (hash, ssn, address{padding}[int64])
                # Increase syscall number
                ssn += 1
                break

            ++nameRef

        # Go next address
        i += 1

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

    var
        me32: MODULEENTRY32
        mi: MODULEINFO
    
    me32.dwSize = cast[DWORD](sizeof(MODULEENTRY32))

    # SKip to ntdll.dll
    hModule.Module32First(addr me32)
    # NTDLL.dll is not guaranteed to be first
    while hModule.Module32Next(addr me32):
        # Detect \ntdll.dll
        if "92110116100108108461001081080" in me32.szExePath.join():
            break
    
    handle.GetModuleInformation(me32.hModule, addr mi, cast[DWORD](sizeof(mi)))
    
    # Resolve ssn & address
    for hash, ssn, address in mi.SPT_Iterator():
        var entry = Syscall(ssn: ssn, address: address)
        ssdt[hash] = entry

    return