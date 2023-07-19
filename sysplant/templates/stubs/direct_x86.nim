proc SPT_Syscall {.asmNoStackFrame.} = 
    asm """
        pop eax
        ##__DEBUG_INT__##
        call `SPT_GetSyscallNumber`
        add esp, 0x4
        mov ecx, [fs:0xc0]
        test ecx, ecx
        jne _wow64
        lea edx, [esp+4]
        ##__DEBUG_INT__##
        ##__SYSCALL_INT__##
        ret
    _wow64:
        xor ecx, ecx
        lea edx, [esp+4]
        ##__DEBUG_INT__##
        call dword ptr[fs:0x0c]
        ret
    """