# Check if stub is modified
proc isClean(address: PBYTE, cw: int32): bool =
    # First opcodes should be :
    #    MOV R10, RCX
    #    MOV RCX, <syscall>
    for i, value in @[byte 0x4c, 0x8b, 0xd1, 0xb8, 0xff, 0xff, 0x00, 0x00].pairs:
        # Skip syscall values
        if value == 0xff:
            continue
        if address{cw + i}[] != value:
            return false
    return true

# Parse Export Directory and look for opcode scheme: https://github.com/am0nsec/HellsGate/blob/master/HellsGate/main.c
iterator SPT_Iterator(mi: MODULEINFO): (DWORD, int32, int64) =
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
        
        var cw: int32 = 0
        # Check current function, ensure this is a syscall
        while true:
            # check if syscall, in this case we are too far
            if (address{cw}[] == 0x0f) and (address{cw + 1}[] == 0x05):
                break

            # check if ret, in this case we are also probaly too far
            if address{cw}[] == 0xc3:
                break

            if address.isClean(cw):
                let
                    hash = SPT_HashSyscallName(name)
                    found = address{cw}[int64]
                    
                # Retrieve the SSN taking care of the endianess 
                let
                    high_b = address{cw + 5}[]
                    low_b = address{cw + 4}[]
                    ssn: int32 = (high_b shl 8).bitor(low_b)[int32]
                
                yield (hash, ssn, found)
                break
            
            cw += 1
    
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

    # Resolve address
    for hash, ssn, address in mi.SPT_Iterator():
        ssdt[hash] = Syscall(address: address, ssn: ssn)

    return
