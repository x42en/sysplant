# -*- coding: utf-8 -*-

structure = """#[repr(C)]
pub struct KNORMAL_ROUTINE {
    pub NormalContext: PVOID,
    pub SystemArgument1: PVOID,
    pub SystemArgument2: PVOID,
}
pub type PKNORMAL_ROUTINE = *mut KNORMAL_ROUTINE;
"""
structure3 = """#[repr(C)]
pub struct PS_CREATE_INFO_INIT_STATE_FLAGS {
    pub WriteOutputOnExit: UCHAR, // bitsize: 1
    pub DetectManifest: UCHAR, // bitsize: 1
    pub IFEOSkipDebugger: UCHAR, // bitsize: 1
    pub IFEODoNotPropagateKeyState: UCHAR, // bitsize: 1
    pub SpareBits1: UCHAR, // bitsize: 4
    pub SpareBits2: UCHAR, // bitsize: 8
    pub ProhibitedImageCharacteristics: UCHAR, // bitsize: 16
}
pub type PPS_CREATE_INFO_INIT_STATE_FLAGS = *mut PS_CREATE_INFO_INIT_STATE_FLAGS;
"""
union = """#[repr(C)]
pub union PS_ATTRIBUTE_UNION {
    pub Value: ULONG_PTR,
    pub ValuePtr: PVOID,
}
pub type PPS_ATTRIBUTE_UNION = *mut PS_ATTRIBUTE_UNION;
"""
pointer = "pub type PPVOID = *mut PVOID;\n"
standard = """pub type LANGID = WORD;
pub type PLANGID = *mut LANGID;
"""
enum = """#[repr(C)]
pub enum SECTION_INHERIT {
    ViewShare = 1,
    ViewUnmap = 2,
}
pub type PSECTION_INHERIT = *mut SECTION_INHERIT;
"""
debug = "const SPT_DEBUG: bool = true;"
seed = "const SPT_SEED: u32 = 0x1;"
stub = """global_asm!("NtOpenProcessToken:",
    "push 0x5b50179b",
    "call SPT_Syscall",
);
"""
definitions = """#[repr(C)]
pub struct KNORMAL_ROUTINE {
    pub NormalContext: PVOID,
    pub SystemArgument1: PVOID,
    pub SystemArgument2: PVOID,
}
pub type PKNORMAL_ROUTINE = *mut KNORMAL_ROUTINE;

unsafe extern "C" {
    pub fn NtQueueApcThread(
        ThreadHandle: HANDLE,
        ApcRoutine: PKNORMAL_ROUTINE,
        ApcArgument1: PVOID,
        ApcArgument2: PVOID,
        ApcArgument3: PVOID
    ) -> NTSTATUS;
}
"""
