// Egg hunter sanitizer: patches egg markers with real syscall opcodes at runtime
static unsigned char SPT_EGG_PATTERN[] = {##__EGG_BYTES__##};

#if defined(_M_X64) || defined(__x86_64__)
// syscall (0F 05) + nop (90) + nop (90) + ret (C3) + nop (90) + int3 (CC) + int3 (CC)
static unsigned char SPT_EGG_REPLACE[] = {0x0f, 0x05, 0x90, 0x90, 0xC3, 0x90, 0xCC, 0xCC};
#else
// sysenter (0F 34) + nop (90) + nop (90) + ret (C3) + nop (90) + int3 (CC) + int3 (CC)
static unsigned char SPT_EGG_REPLACE[] = {0x0f, 0x34, 0x90, 0x90, 0xC3, 0x90, 0xCC, 0xCC};
#endif

BOOL SPT_SanitizeSyscalls(void)
{
    DWORD dwOldProtect = 0;

    // Get base address of the current module
    PVOID pBase = (PVOID)GetModuleHandleA(NULL);
    if (!pBase)
        return FALSE;

    // Parse PE headers to find .text section
    PIMAGE_DOS_HEADER pDos = (PIMAGE_DOS_HEADER)pBase;
    PIMAGE_NT_HEADERS pNt = (PIMAGE_NT_HEADERS)((PBYTE)pBase + pDos->e_lfanew);
    PIMAGE_SECTION_HEADER pSection = IMAGE_FIRST_SECTION(pNt);

    PVOID pText = NULL;
    SIZE_T szText = 0;

    for (WORD i = 0; i < pNt->FileHeader.NumberOfSections; i++)
    {
        if (*(ULONG *)pSection[i].Name == 0x7865742E || // ".tex"
            *(ULONG *)pSection[i].Name == 0x444F432E)   // ".COD"
        {
            pText = (PVOID)((PBYTE)pBase + pSection[i].VirtualAddress);
            szText = pSection[i].Misc.VirtualSize;
            break;
        }
    }

    if (!pText || !szText)
        return FALSE;

    DWORD dwEggSize = sizeof(SPT_EGG_PATTERN);
    DWORD dwPatched = 0;

    // Make .text section writable
    if (!VirtualProtect(pText, szText, PAGE_EXECUTE_READWRITE, &dwOldProtect))
        return FALSE;

    // Scan for egg pattern and replace
    for (SIZE_T i = 0; i <= szText - dwEggSize; i++)
    {
        BOOL bMatch = TRUE;
        for (DWORD j = 0; j < dwEggSize; j++)
        {
            if (((PBYTE)pText)[i + j] != SPT_EGG_PATTERN[j])
            {
                bMatch = FALSE;
                break;
            }
        }

        if (bMatch)
        {
            for (DWORD j = 0; j < dwEggSize; j++)
            {
                ((PBYTE)pText)[i + j] = SPT_EGG_REPLACE[j];
            }
            dwPatched++;
            i += dwEggSize - 1;
        }
    }

    // Restore original protection
    VirtualProtect(pText, szText, dwOldProtect, &dwOldProtect);

    return (dwPatched > 0);
}

// Auto-init: patch egg markers before main()
// extern "C" prevents C++ name mangling so the asm .quad directive finds the symbol
extern "C" __attribute__((used)) void __SPT_EggHunterInit(void)
{
    SPT_SanitizeSyscalls();
}

// Register in CRT init table (.CRT$XCU) for automatic call before main()
// Using asm directives to avoid section attribute leaking to subsequent asm stubs
#if defined(_MSC_VER)
#pragma section(".CRT$XCU", read)
__declspec(allocate(".CRT$XCU")) static void (*__spt_init)(void) = __SPT_EggHunterInit;
#elif defined(__GNUC__)
__asm__(".section \".CRT$XCU\",\"dr\"\n\t"
        ".align 8\n\t"
        ".quad __SPT_EggHunterInit\n\t"
        ".text");
#endif
