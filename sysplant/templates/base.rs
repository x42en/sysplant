#![allow(non_snake_case, non_camel_case_types, non_upper_case_globals, dead_code, unsafe_op_in_unsafe_fn, static_mut_refs)]

// Code below is adapted from @modexpblog. Read linked article for more details.
// https://www.mdsec.co.uk/2020/12/bypassing-user-mode-hooks-and-direct-invocation-of-system-calls-for-red-teams

use core::arch::global_asm;
use std::ffi::c_void;
use std::ptr;

use md5;
use windows_sys::Win32::System::Diagnostics::Debug::{
    IMAGE_NT_HEADERS64, IMAGE_RUNTIME_FUNCTION_ENTRY,
};
use windows_sys::Win32::System::Kernel::LIST_ENTRY;
use windows_sys::Win32::System::SystemServices::{IMAGE_DOS_HEADER, IMAGE_EXPORT_DIRECTORY};

// ==================== Windows Type Definitions ====================
pub type DWORD = u32;
pub type WORD = u16;
pub type BYTE = u8;
pub type USHORT = u16;
pub type ULONG = u32;
pub type ULONG_PTR = usize;
pub type LONG = i32;
pub type NTSTATUS = LONG;
pub type BOOL = i32;
pub type PVOID = *mut c_void;
pub type PBYTE = *mut u8;
pub type PCHAR = *mut i8;
pub type PCSTR = *const i8;
pub type HANDLE = *mut c_void;
pub type SIZE_T = usize;
pub type ACCESS_MASK = DWORD;
pub type BOOLEAN = u8;
pub type ULONGLONG = u64;
pub type PWSTR = *mut u16;
pub type PHANDLE = *mut HANDLE;
pub type PULONG = *mut ULONG;
pub type PSIZE_T = *mut SIZE_T;
pub type PLARGE_INTEGER = *mut i64;
pub type PCONTEXT = PVOID;
pub type PTOKEN_PRIVILEGES = PVOID;

pub const TRUE: BOOL = 1;
pub const FALSE: BOOL = 0;
pub const IMAGE_DIRECTORY_ENTRY_EXPORT: usize = 0;
pub const IMAGE_DIRECTORY_ENTRY_EXCEPTION: usize = 3;

##__SPT_DEBUG__##

##__SPT_SEED__##
const SPT_MAX_ENTRIES: usize = 500;

macro_rules! SPT_RVA2VA {
    ($t:ty, $base:expr, $rva:expr) => {
        ($base as usize + $rva as usize) as $t
    };
}

// ==================== Internal Structures ====================
#[repr(C)]
pub struct SPT_SYSCALL_ENTRY {
    pub Hash: DWORD,
    pub Address: PVOID,
    pub SyscallAddress: PVOID,
}

#[repr(C)]
pub struct SPT_SYSCALL_LIST {
    pub Count: DWORD,
    pub Entries: [SPT_SYSCALL_ENTRY; SPT_MAX_ENTRIES],
}

#[repr(C)]
struct SPT_PEB_LDR_DATA {
    Reserved1: [u8; 8],
    Reserved2: [PVOID; 3],
    InMemoryOrderModuleList: LIST_ENTRY,
}

#[repr(C)]
struct SPT_LDR_DATA_TABLE_ENTRY {
    Reserved1: [PVOID; 2],
    InMemoryOrderLinks: LIST_ENTRY,
    Reserved2: [PVOID; 2],
    DllBase: PVOID,
}

#[repr(C)]
struct SPT_PEB {
    Reserved1: [u8; 2],
    BeingDebugged: u8,
    Reserved2: [u8; 1],
    Reserved3: [PVOID; 2],
    Ldr: *mut SPT_PEB_LDR_DATA,
}

#[macro_export]
macro_rules! InitializeObjectAttributes {
    ($p:expr, $n:expr, $a:expr, $r:expr, $s:expr) => {
        (*$p).Length = core::mem::size_of::<OBJECT_ATTRIBUTES>() as ULONG;
        (*$p).RootDirectory = $r;
        (*$p).Attributes = $a;
        (*$p).ObjectName = $n;
        (*$p).SecurityDescriptor = $s;
        (*$p).SecurityQualityOfService = ptr::null_mut();
    };
}

##__TYPE_DEFINITIONS__##

// ==================== Global State ====================
static mut SPT_SyscallList: SPT_SYSCALL_LIST = SPT_SYSCALL_LIST {
    Count: 0,
    Entries: unsafe { core::mem::zeroed() },
};

// ==================== Hash Implementation ====================
#[unsafe(no_mangle)]
unsafe fn SPT_HashSyscallName(name: PCSTR) -> DWORD {
    let name_ptr = name.add(2);
    let name_suffix_len = {
        let mut len = 0usize;
        while *name_ptr.add(len) != 0 { len += 1; }
        len
    };
    let suffix = core::slice::from_raw_parts(name_ptr as *const u8, name_suffix_len);
    let input = format!("{}{}", SPT_SEED, core::str::from_utf8_unchecked(suffix));
    let digest = md5::compute(input.as_bytes());

    ((digest[3] as u32) << 0)
        | ((digest[2] as u32) << 8)
        | ((digest[1] as u32) << 16)
        | ((digest[0] as u32) << 24)
}

#[unsafe(no_mangle)]
unsafe fn SPT_DetectPadding(address: PVOID) -> u16 {
    #[cfg(target_arch = "x86_64")]
    let syscall_code: [u8; 3] = [0x0f, 0x05, 0xc3];
    #[cfg(target_arch = "x86")]
    let syscall_code: [u8; 3] = [0x0f, 0x34, 0xc3];

    let mut padding: u16 = 0;
    while core::slice::from_raw_parts((address as usize + padding as usize) as *const u8, 3) != syscall_code {
        padding += 1;
        if padding > 0x22 {
            return 0;
        }
    }
    padding
}

// ==================== PEB Access ====================
#[cfg(target_arch = "x86_64")]
unsafe fn get_peb() -> *mut SPT_PEB {
    let peb: *mut SPT_PEB;
    core::arch::asm!("mov {}, gs:[0x60]", out(reg) peb, options(nostack, pure, readonly));
    peb
}

#[cfg(target_arch = "x86")]
unsafe fn get_peb() -> *mut SPT_PEB {
    let peb: *mut SPT_PEB;
    core::arch::asm!("mov {}, fs:[0x30]", out(reg) peb, options(nostack, pure, readonly));
    peb
}

##__SPT_ITERATOR__##

##__SPT_RESOLVER__##

##__SPT_SANITIZER__##

##__SPT_CALLER__##

##__SPT_STUBS__##
