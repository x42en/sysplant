EXTERN_C PVOID SPT_Syscall(DWORD FunctionHash);
EXTERN_C PVOID SPT_Syscall(DWORD FunctionHash)
__asm__("SPT_Syscall: \\n\\
    pop eax \\n\\
    ##__DEBUG_INT__## \\n\\
    call SPT_GetSyscallNumber \\n\\
    add esp, 0x4 \\n\\
    mov ecx, [fs:0xc0] \\n\\
    test ecx, ecx \\n\\
    jne _wow64 \\n\\
    lea edx, [esp+4] \\n\\
    ##__DEBUG_INT__## \\n\\
    ##__SYSCALL_INT__## \\n\\
    ret \\n\\
_wow64: \\n\\
    xor ecx, ecx \\n\\
    lea edx, [esp+4] \\n\\
    ##__DEBUG_INT__## \\n\\
    call dword ptr[fs:0x0c] \\n\\
    ret \\n\\
");