#pragma once

// Code below is adapted from @modexpblog. Read linked article for more details.
// https://www.mdsec.co.uk/2020/12/bypassing-user-mode-hooks-and-direct-invocation-of-system-calls-for-red-teams

#ifndef SPT_HEADER_H_
#define SPT_HEADER_H_

#include <cstdio>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <malloc.h>
#include <windows.h>
#include <wincrypt.h>

##__SPT_DEBUG__##

    ##__SPT_SEED__##
#define SPT_MAX_ENTRIES 500
#define SPT_RVA2VA(Type, DllBase, Rva) (Type)((ULONG_PTR)DllBase + Rva)

    // Typedefs are prefixed to avoid pollution.
    typedef struct _SPT_SYSCALL_ENTRY
{
    DWORD Hash;
    PVOID Address;
    PVOID SyscallAddress;
} SPT_SYSCALL_ENTRY, *PSPT_SYSCALL_ENTRY;

typedef struct _SPT_SYSCALL_LIST
{
    DWORD Count;
    SPT_SYSCALL_ENTRY Entries[SPT_MAX_ENTRIES];
} SPT_SYSCALL_LIST, *PSPT_SYSCALL_LIST;

typedef struct _SPT_PEB_LDR_DATA
{
    BYTE Reserved1[8];
    PVOID Reserved2[3];
    LIST_ENTRY InMemoryOrderModuleList;
} SPT_PEB_LDR_DATA, *PSPT_PEB_LDR_DATA;

typedef struct _SPT_LDR_DATA_TABLE_ENTRY
{
    PVOID Reserved1[2];
    LIST_ENTRY InMemoryOrderLinks;
    PVOID Reserved2[2];
    PVOID DllBase;
} SPT_LDR_DATA_TABLE_ENTRY, *PSPT_LDR_DATA_TABLE_ENTRY;

typedef struct _SPT_PEB
{
    BYTE Reserved1[2];
    BYTE BeingDebugged;
    BYTE Reserved2[1];
    PVOID Reserved3[2];
    PSPT_PEB_LDR_DATA Ldr;
} SPT_PEB, *PSPT_PEB;

DWORD SPT_HashSyscallName(PCSTR FunctionName);
EXTERN_C DWORD SPT_GetSyscallNumber(DWORD FunctionHash);

#ifndef InitializeObjectAttributes
#define InitializeObjectAttributes(p, n, a, r, s) \
    {                                             \
        (p)->Length = sizeof(OBJECT_ATTRIBUTES);  \
        (p)->RootDirectory = r;                   \
        (p)->Attributes = a;                      \
        (p)->ObjectName = n;                      \
        (p)->SecurityDescriptor = s;              \
        (p)->SecurityQualityOfService = NULL;     \
    }
#endif
##__TYPE_DEFINITIONS__##
#endif

    SPT_SYSCALL_LIST SPT_SyscallList;

DWORD SPT_HashSyscallName(PCSTR name)
{
    DWORD Hash;
    SIZE_T name_len = strlen(&name[2]);
    // Use alloca() instead of VLA (not standard in C++)
    char *string_to_hash = (char *)alloca(sizeof(SPT_SEED) + name_len);
    BYTE md5_hash[16] = {0};
    DWORD md5_len = 16;

    sprintf(string_to_hash, "%u%s", SPT_SEED, &name[2]);

    // Use Windows CryptoAPI for MD5 (advapi32 — auto-linked by mingw)
    HCRYPTPROV hProv = 0;
    HCRYPTHASH hHash = 0;
    CryptAcquireContextA(&hProv, NULL, NULL, PROV_RSA_FULL, CRYPT_VERIFYCONTEXT);
    CryptCreateHash(hProv, CALG_MD5, 0, 0, &hHash);
    CryptHashData(hHash, (const BYTE *)string_to_hash, (DWORD)strlen(string_to_hash), 0);
    CryptGetHashParam(hHash, HP_HASHVAL, md5_hash, &md5_len, 0);
    CryptDestroyHash(hHash);
    CryptReleaseContext(hProv, 0);

    Hash = ((DWORD)md5_hash[3] << 0) | ((DWORD)md5_hash[2] << 8) | ((DWORD)md5_hash[1] << 16) | ((DWORD)md5_hash[0] << 24);
    return Hash;
}

WORD SPT_DetectPadding(PVOID address)
{
#if defined(_WIN64)
    // If the process is 64-bit on a 64-bit OS, we need to search for syscall
    BYTE syscall_code[] = {0x0f, 0x05, 0xc3};
#else
    // If the process is 32-bit on a 32-bit OS, we need to search for sysenter
    BYTE syscall_code[] = {0x0f, 0x34, 0xc3};
#endif

    WORD padding = 0x0;
    // Search padding size until next syscall instruction
    while (memcmp((PVOID)syscall_code, SPT_RVA2VA(PVOID, address, padding), sizeof(syscall_code)))
    {
        padding++;
        // Windows stubs are quite small, don't waste time
        if (padding > 0x22)
        {
            return 0x0;
        };
    }

    return padding;
}

##__SPT_ITERATOR__##

    ##__SPT_RESOLVER__##

    ##__SPT_SANITIZER__##

    ##__SPT_CALLER__##

#if defined(__GNUC__)
    ##__SPT_STUBS__##
#endif
