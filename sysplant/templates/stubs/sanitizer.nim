# Egg hunter sanitizer: patches egg markers with real syscall opcodes at runtime
var SPT_EGG_PATTERN {.global.}: array[8, byte] = [ ##__EGG_BYTES__## ]

when defined(amd64):
    # syscall (0F 05) + nop (90) + nop (90) + ret (C3) + nop (90) + int3 (CC) + int3 (CC)
    var SPT_EGG_REPLACE {.global.}: array[8, byte] = [0x0F'u8, 0x05, 0x90, 0x90, 0xC3, 0x90, 0xCC, 0xCC]
else:
    # sysenter (0F 34) + nop (90) + nop (90) + ret (C3) + nop (90) + int3 (CC) + int3 (CC)
    var SPT_EGG_REPLACE {.global.}: array[8, byte] = [0x0F'u8, 0x34, 0x90, 0x90, 0xC3, 0x90, 0xCC, 0xCC]

proc SPT_SanitizeSyscalls*(): bool =
    var dwOldProtect: DWORD = 0

    # Get base address of the current module
    let pBase = cast[PVOID](GetModuleHandleA(nil))
    if pBase == nil:
        return false

    # Parse PE headers to find .text section
    let pDos = cast[PIMAGE_DOS_HEADER](pBase)
    let pNt = cast[PIMAGE_NT_HEADERS](cast[uint](pBase) + cast[uint](pDos.e_lfanew))
    let pFirstSection = cast[PIMAGE_SECTION_HEADER](cast[uint](pNt) + cast[uint](sizeof(IMAGE_NT_HEADERS)))

    var pText: PVOID = nil
    var szText: SIZE_T = 0

    for i in 0 ..< pNt.FileHeader.NumberOfSections.int:
        let pSection = cast[PIMAGE_SECTION_HEADER](cast[uint](pFirstSection) + cast[uint](i * sizeof(IMAGE_SECTION_HEADER)))
        let sectionName = cast[ptr uint32](addr pSection.Name[0])
        if sectionName[] == 0x7865742E'u32 or sectionName[] == 0x444F432E'u32:
            pText = cast[PVOID](cast[uint](pBase) + cast[uint](pSection.VirtualAddress))
            szText = cast[SIZE_T](pSection.Misc.VirtualSize)
            break

    if pText == nil or szText == 0:
        return false

    let dwEggSize = SPT_EGG_PATTERN.len

    # Make .text section writable
    if VirtualProtect(pText, szText, PAGE_EXECUTE_READWRITE, addr dwOldProtect) == 0:
        return false

    var dwPatched: int = 0

    # Scan for egg pattern and replace
    var i = 0
    while i <= szText.int - dwEggSize:
        var bMatch = true
        for j in 0 ..< dwEggSize:
            if cast[ptr byte](cast[uint](pText) + cast[uint](i + j))[] != SPT_EGG_PATTERN[j]:
                bMatch = false
                break

        if bMatch:
            for j in 0 ..< dwEggSize:
                cast[ptr byte](cast[uint](pText) + cast[uint](i + j))[] = SPT_EGG_REPLACE[j]
            dwPatched += 1
            i += dwEggSize
        else:
            i += 1

    # Restore original protection
    discard VirtualProtect(pText, szText, dwOldProtect, addr dwOldProtect)

    return dwPatched > 0

# Auto-patch egg markers at import time
discard SPT_SanitizeSyscalls()
