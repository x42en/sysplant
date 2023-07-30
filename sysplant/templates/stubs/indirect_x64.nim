proc SPT_Syscall {.asmNoStackFrame.} = 
    asm """
        pop rax
        pop r15
        mov [rsp +8], rcx
        mov [rsp+16], rdx
        mov [rsp+24], r8
        mov [rsp+32], r9
        sub rsp, 0x28
        mov rcx, r15
        ##__DEBUG_INT__##
        call `SPT_GetSyscallAddress`
        mov r15, rax
        add rsp, 0x28
        mov rcx, [rsp +8]
        mov rdx, [rsp+16]
        mov r8, [rsp+24]
        mov r9, [rsp+32]
        ##__DEBUG_INT__##
        jmp r15
    """