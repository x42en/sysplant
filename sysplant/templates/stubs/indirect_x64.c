EXTERN_C PVOID SPT_Syscall(DWORD FunctionHash);
EXTERN_C PVOID SPT_Syscall(DWORD FunctionHash)
__asm__("SPT_Syscall: \\n\\
    pop rax \\n\\
    pop rax \\n\\
    mov [rsp +8], rcx \\n\\
    mov [rsp+16], rdx \\n\\
    mov [rsp+24], r8 \\n\\
    mov [rsp+32], r9 \\n\\
    sub rsp, 0x28 \\n\\
    mov rcx, rax \\n\\
    ##__DEBUG_INT__## \\n\\
    call SPT_GetSyscallNumber \\n\\
    mov r15, rax \\n\\
    call ##__FUNCTION_RESOLVE__## \\n\\
    xchg r15, rax \\n\\
    add rsp, 0x28 \\n\\
    mov rcx, [rsp +8] \\n\\
    mov rdx, [rsp+16] \\n\\
    mov r8, [rsp+24] \\n\\
    mov r9, [rsp+32] \\n\\
    mov r10, rcx \\n\\
    ##__DEBUG_INT__## \\n\\
    jmp r15 \\n\\
");