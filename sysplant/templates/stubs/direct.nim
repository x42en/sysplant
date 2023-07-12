##__PROC_DEFINITION__##
    asm """
        push dword ptr ##__FUNCTION_HASH__##
        call `SPT_Syscall`
    """