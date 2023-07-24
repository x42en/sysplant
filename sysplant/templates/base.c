#pragma once

// Code below is adapted from @modexpblog. Read linked article for more details.
// https://www.mdsec.co.uk/2020/12/bypassing-user-mode-hooks-and-direct-invocation-of-system-calls-for-red-teams

#ifndef SPT_HEADER_H_
#define SPT_HEADER_H_

#include <windows.h>

##__SPT_DEBUG__##

##__SPT_SEED__##
#define SPT_ROR8(v) (v >> 8 | v << 24)
#define SPT_MAX_ENTRIES 200
#define SPT_RVA2VA(Type, DllBase, Rva) (Type)((ULONG_PTR) DllBase + Rva)

// Typedefs are prefixed to avoid pollution.
typedef struct _SPT_SYSCALL_ENTRY
{
    DWORD Hash;
    DWORD Address;
    PVOID SyscallAddress;
} SPT_SYSCALL_ENTRY, *PSPT_SYSCALL_ENTRY;

typedef struct _SPT_SYSCALL_LIST
{
    DWORD Count;
    SPT_SYSCALL_ENTRY Entries[SPT_MAX_ENTRIES];
} SPT_SYSCALL_LIST, *PSPT_SYSCALL_LIST;

typedef struct _SPT_PEB_LDR_DATA {
	BYTE Reserved1[8];
	PVOID Reserved2[3];
	LIST_ENTRY InMemoryOrderModuleList;
} SPT_PEB_LDR_DATA, *PSPT_PEB_LDR_DATA;

typedef struct _SPT_LDR_DATA_TABLE_ENTRY {
	PVOID Reserved1[2];
	LIST_ENTRY InMemoryOrderLinks;
	PVOID Reserved2[2];
	PVOID DllBase;
} SPT_LDR_DATA_TABLE_ENTRY, *PSPT_LDR_DATA_TABLE_ENTRY;

typedef struct _SPT_PEB {
	BYTE Reserved1[2];
	BYTE BeingDebugged;
	BYTE Reserved2[1];
	PVOID Reserved3[2];
	PSPT_PEB_LDR_DATA Ldr;
} SPT_PEB, *PSPT_PEB;

DWORD SPT_HashSyscallName(PCSTR FunctionName);
EXTERN_C DWORD SPT_GetSyscallNumber(DWORD FunctionHash);

#ifndef InitializeObjectAttributes
#define InitializeObjectAttributes( p, n, a, r, s ) { \
	(p)->Length = sizeof( OBJECT_ATTRIBUTES );        \
	(p)->RootDirectory = r;                           \
	(p)->Attributes = a;                              \
	(p)->ObjectName = n;                              \
	(p)->SecurityDescriptor = s;                      \
	(p)->SecurityQualityOfService = NULL;             \
}
#endif
##__TYPE_DEFINITIONS__##
#endif

SPT_SYSCALL_LIST SPT_SyscallList;

##__SPT_ITERATOR__##

// DWORD SPT_HashSyscallName(PCSTR name)
// {
//     DWORD res;
//     MD5_CTX md5_ctx;
//     char string_to_hash[12];
//     unsigned char md5_hash[MD5_DIGEST_LENGTH] = {0};

//     MD5_Init(&md5_ctx);

//     sprintf(string_to_hash, "%u", SPT_SEED);
//     MD5_Update(&md5_ctx, string_to_hash, strlen(string_to_hash));
//     MD5_Update(&md5_ctx, &name[2], strlen(&name[2]));
//     MD5_Final(md5_hash, &md5_ctx);

//     // Avoid inet include
//     res = ((DWORD) md5_hash[3] << 0)
//         | ((DWORD) md5_hash[2] << 8)
//         | ((DWORD) md5_hash[1] << 16)
//         | ((DWORD) md5_hash[0] << 24);

//     return res;
// }
DWORD SPT_HashSyscallName(PCSTR FunctionName)
{
    DWORD i = 0;
    DWORD Hash = SPT_SEED;

    while (FunctionName[i])
    {
        WORD PartialName = *(WORD *)((ULONG_PTR)FunctionName + i++);
        Hash ^= PartialName + SPT_ROR8(Hash);
    }

    return Hash;
}

EXTERN_C DWORD SPT_GetSyscallNumber(DWORD FunctionHash)
{
    // Ensure SPT_SyscallList is populated.
    if (!SPT_PopulateSyscallList())
        return -1;

    for (DWORD i = 0; i < SPT_SyscallList.Count; i++)
    {
        if (FunctionHash == SPT_SyscallList.Entries[i].Hash)
        {
            return i;
        }
    }

    return -1;
}

##__SPT_RESOLVER__##

##__SPT_CALLER__##

#if defined(__GNUC__)
##__SPT_STUBS__##
#endif