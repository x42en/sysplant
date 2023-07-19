#pragma once

// Code below is adapted from @modexpblog. Read linked article for more details.
// https://www.mdsec.co.uk/2020/12/bypassing-user-mode-hooks-and-direct-invocation-of-system-calls-for-red-teams

#include <stdio.h>
#include <windows.h>

#define SPT_RVA2VA(Type, DllBase, Rva) (Type)((ULONG_PTR) DllBase + Rva)

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

##__TYPE_DEFINITIONS__##

##__SPT_DEBUG__##
##__SPT_SEED__##

##__SPT_ITERATOR__##

DWORD SPT_HashSyscallName(PCSTR FunctionName);
DWORD SPT_HashSyscallName(PCSTR FunctionName)
{
    DWORD i = 2;
    DWORD Hash = SPT_SEED;
    char *hash
    char unsigned md5[MD5_DIGEST_LENGTH] = {0};
    
    MD5((const unsigned char *)FunctionName, strlen(FunctionName), md5);

    for (i=0; i < 8; i++) {
        sprintf(hash + 2*i, "%02x", md5[i]);
    }

    while (FunctionName[i])
    {
        WORD PartialName = *(WORD*)((ULONG_PTR)FunctionName + i++);
        Hash ^= PartialName + SW3_ROR8(Hash);
    }

    return Hash;
}

EXTERN_C DWORD SPT_GetSyscallNumber(DWORD FunctionHash);
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