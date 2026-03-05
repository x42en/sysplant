// Egg hunter sanitizer: patches egg markers with real syscall opcodes at runtime

// Sanitizer-specific imports
use windows_sys::Win32::System::Diagnostics::Debug::IMAGE_SECTION_HEADER;
use windows_sys::Win32::System::Memory::{VirtualProtect, PAGE_EXECUTE_READWRITE};

unsafe extern "system" {
    fn GetModuleHandleA(lpModuleName: *const u8) -> isize;
}

static SPT_EGG_PATTERN: [u8; 8] = [ ##__EGG_BYTES__## ];

#[cfg(target_arch = "x86_64")]
// syscall (0F 05) + nop (90) + nop (90) + ret (C3) + nop (90) + int3 (CC) + int3 (CC)
static SPT_EGG_REPLACE: [u8; 8] = [0x0f, 0x05, 0x90, 0x90, 0xC3, 0x90, 0xCC, 0xCC];

#[cfg(target_arch = "x86")]
// sysenter (0F 34) + nop (90) + nop (90) + ret (C3) + nop (90) + int3 (CC) + int3 (CC)
static SPT_EGG_REPLACE: [u8; 8] = [0x0f, 0x34, 0x90, 0x90, 0xC3, 0x90, 0xCC, 0xCC];

pub unsafe fn spt_sanitize_syscalls() -> bool {
    let mut dw_old_protect: u32 = 0;

    // Get base address of the current module
    let h_module = GetModuleHandleA(core::ptr::null());
    if h_module == 0 {
        return false;
    }
    let p_base = h_module as *const u8;

    // Parse PE headers to find .text section
    let p_dos = p_base as *const IMAGE_DOS_HEADER;
    let p_nt = p_base.offset((*p_dos).e_lfanew as isize) as *const IMAGE_NT_HEADERS64;
    let p_first_section = (p_nt as *const u8).offset(core::mem::size_of::<IMAGE_NT_HEADERS64>() as isize) as *const IMAGE_SECTION_HEADER;

    let mut p_text: *const u8 = core::ptr::null();
    let mut sz_text: usize = 0;

    for i in 0..(*p_nt).FileHeader.NumberOfSections as isize {
        let p_section = p_first_section.offset(i);
        let section_name = *((*p_section).Name.as_ptr() as *const u32);
        if section_name == 0x7865742E || section_name == 0x444F432E {
            p_text = p_base.offset((*p_section).VirtualAddress as isize);
            sz_text = (*p_section).Misc.VirtualSize as usize;
            break;
        }
    }

    if p_text.is_null() || sz_text == 0 {
        return false;
    }

    let egg_size = SPT_EGG_PATTERN.len();

    // Make .text section writable
    if VirtualProtect(
        p_text as *const _,
        sz_text,
        PAGE_EXECUTE_READWRITE,
        &mut dw_old_protect,
    ) == 0 {
        return false;
    }

    let mut patched: u32 = 0;

    // Scan for egg pattern and replace
    let mut i: usize = 0;
    while i <= sz_text - egg_size {
        let mut found = true;
        for j in 0..egg_size {
            if *p_text.offset((i + j) as isize) != SPT_EGG_PATTERN[j] {
                found = false;
                break;
            }
        }

        if found {
            let p_write = p_text as *mut u8;
            for j in 0..egg_size {
                *p_write.offset((i + j) as isize) = SPT_EGG_REPLACE[j];
            }
            patched += 1;
            i += egg_size;
        } else {
            i += 1;
        }
    }

    // Restore original protection
    VirtualProtect(
        p_text as *const _,
        sz_text,
        dw_old_protect,
        &mut dw_old_protect,
    );

    patched > 0
}
