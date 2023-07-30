#pragma once

// Code below is adapted from @modexpblog. Read linked article for more details.
// https://www.mdsec.co.uk/2020/12/bypassing-user-mode-hooks-and-direct-invocation-of-system-calls-for-red-teams

#ifndef SPT_HEADER_H_
#define SPT_HEADER_H_

#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <windows.h>

##__SPT_DEBUG__##

##__SPT_SEED__##
#define A 0x67452301
#define B 0xefcdab89
#define C 0x98badcfe
#define D 0x10325476
#define SPT_MAX_ENTRIES 500
#define SPT_RVA2VA(Type, DllBase, Rva) (Type)((ULONG_PTR) DllBase + Rva)

typedef struct{
    uint64_t size;        // Size of input in bytes
    uint32_t buffer[4];   // Current accumulation of hash
    uint8_t input[64];    // Input to be used in the next step
    uint8_t digest[16];   // Result of algorithm
}SPT_HashContext;

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

static uint32_t S[] = {7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
                       5,  9, 14, 20, 5,  9, 14, 20, 5,  9, 14, 20, 5,  9, 14, 20,
                       4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
                       6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21};

static uint32_t K[] = {0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee,
                       0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
                       0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be,
                       0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
                       0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa,
                       0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
                       0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed,
                       0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
                       0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c,
                       0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
                       0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05,
                       0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
                       0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039,
                       0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
                       0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1,
                       0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391};

/*
 * Padding used to make the size (in bits) of the input congruent to 448 mod 512
 */
static uint8_t PADDING[] = {0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};

/*
 * Bit-manipulation functions defined by the MD5 algorithm
 */
#define F(X, Y, Z) ((X & Y) | (~X & Z))
#define G(X, Y, Z) ((X & Z) | (Y & ~Z))
#define H(X, Y, Z) (X ^ Y ^ Z)
#define I(X, Y, Z) (Y ^ (X | ~Z))

/*
 * Rotates a 32-bit word left by n bits
 */
uint32_t rotateLeft(uint32_t x, uint32_t n){
    return (x << n) | (x >> (32 - n));
}

void SPT_HashInit(SPT_HashContext *ctx);
void SPT_HashUpdate(SPT_HashContext *ctx, uint8_t *input, size_t input_len);
void SPT_HashFinalize(SPT_HashContext *ctx);
void SPT_HashStep(uint32_t *buffer, uint32_t *input);
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

SPT_HashContext ctx;
SPT_SYSCALL_LIST SPT_SyscallList;

/*
* MD5 algorithm shamelessly stolen from https://github.com/Zunawe/md5-c 
*/
/*
 * Initialize a context
 */
void SPT_HashInit(SPT_HashContext *ctx){
    ctx->size = (uint64_t)0;

    ctx->buffer[0] = (uint32_t)A;
    ctx->buffer[1] = (uint32_t)B;
    ctx->buffer[2] = (uint32_t)C;
    ctx->buffer[3] = (uint32_t)D;
}

/*
 * Add some amount of input to the context
 *
 * If the input fills out a block of 512 bits, apply the algorithm (SPT_HashStep)
 * and save the result in the buffer. Also updates the overall size.
 */
void SPT_HashUpdate(SPT_HashContext *ctx, uint8_t *input_buffer, size_t input_len){
    uint32_t input[16];
    unsigned int offset = ctx->size % 64;
    ctx->size += (uint64_t)input_len;

    // Copy each byte in input_buffer into the next space in our context input
    for(unsigned int i = 0; i < input_len; ++i){
        ctx->input[offset++] = (uint8_t)*(input_buffer + i);
        if(offset % 64 == 0){
            for(unsigned int j = 0; j < 16; ++j){
                input[j] = (uint32_t)(ctx->input[(j * 4) + 3]) << 24 |
                           (uint32_t)(ctx->input[(j * 4) + 2]) << 16 |
                           (uint32_t)(ctx->input[(j * 4) + 1]) <<  8 |
                           (uint32_t)(ctx->input[(j * 4)]);
            }
            SPT_HashStep(ctx->buffer, input);
            offset = 0;
        }
    }
}

/*
 * Pad the current input to get to 448 bytes, append the size in bits to the very end,
 * and save the result of the final iteration into digest.
 */
void SPT_HashFinalize(SPT_HashContext *ctx){
    uint32_t input[16];
    unsigned int offset = ctx->size % 64;
    unsigned int padding_length = offset < 56 ? 56 - offset : (56 + 64) - offset;

    // Fill in the padding and undo the changes to size that resulted from the update
    SPT_HashUpdate(ctx, PADDING, padding_length);
    ctx->size -= (uint64_t)padding_length;

    // Do a final update (internal to this function)
    // Last two 32-bit words are the two halves of the size (converted from bytes to bits)
    for(unsigned int j = 0; j < 14; ++j){
        input[j] = (uint32_t)(ctx->input[(j * 4) + 3]) << 24 |
                   (uint32_t)(ctx->input[(j * 4) + 2]) << 16 |
                   (uint32_t)(ctx->input[(j * 4) + 1]) <<  8 |
                   (uint32_t)(ctx->input[(j * 4)]);
    }
    input[14] = (uint32_t)(ctx->size * 8);
    input[15] = (uint32_t)((ctx->size * 8) >> 32);

    SPT_HashStep(ctx->buffer, input);

    // Move the result into digest (convert from little-endian)
    for(unsigned int i = 0; i < 4; ++i){
        ctx->digest[(i * 4) + 0] = (uint8_t)((ctx->buffer[i] & 0x000000FF));
        ctx->digest[(i * 4) + 1] = (uint8_t)((ctx->buffer[i] & 0x0000FF00) >>  8);
        ctx->digest[(i * 4) + 2] = (uint8_t)((ctx->buffer[i] & 0x00FF0000) >> 16);
        ctx->digest[(i * 4) + 3] = (uint8_t)((ctx->buffer[i] & 0xFF000000) >> 24);
    }
}

/*
 * Step on 512 bits of input with the main MD5 algorithm.
 */
void SPT_HashStep(uint32_t *buffer, uint32_t *input){
    uint32_t AA = buffer[0];
    uint32_t BB = buffer[1];
    uint32_t CC = buffer[2];
    uint32_t DD = buffer[3];

    uint32_t E;

    unsigned int j;

    for(unsigned int i = 0; i < 64; ++i){
        switch(i / 16){
            case 0:
                E = F(BB, CC, DD);
                j = i;
                break;
            case 1:
                E = G(BB, CC, DD);
                j = ((i * 5) + 1) % 16;
                break;
            case 2:
                E = H(BB, CC, DD);
                j = ((i * 3) + 5) % 16;
                break;
            default:
                E = I(BB, CC, DD);
                j = (i * 7) % 16;
                break;
        }

        uint32_t temp = DD;
        DD = CC;
        CC = BB;
        BB = BB + rotateLeft(AA + E + K[i] + input[j], S[i]);
        AA = temp;
    }

    buffer[0] += AA;
    buffer[1] += BB;
    buffer[2] += CC;
    buffer[3] += DD;
}

DWORD SPT_HashSyscallName(PCSTR name)
{
    DWORD Hash;
    SIZE_T name_len = strlen(&name[2]);
    char string_to_hash[sizeof(SPT_SEED) + name_len];
    uint8_t md5_hash[16] = {0};

    sprintf(string_to_hash, "%u%s", SPT_SEED, &name[2]);

    SPT_HashInit(&ctx);
    SPT_HashUpdate(&ctx, (uint8_t *)string_to_hash, strlen(string_to_hash));
    SPT_HashFinalize(&ctx);

    memcpy(md5_hash, ctx.digest, 16);

    Hash = ((DWORD) md5_hash[3] << 0)
        | ((DWORD) md5_hash[2] << 8)
        | ((DWORD) md5_hash[1] << 16)
        | ((DWORD) md5_hash[0] << 24);
    return Hash;
}

WORD SPT_DetectPadding(PVOID address) {
#if defined(_WIN64)
    // If the process is 64-bit on a 64-bit OS, we need to search for syscall
    BYTE syscall_code[] = {0x0f, 0x05, 0xc3};
#else
    // If the process is 32-bit on a 32-bit OS, we need to search for sysenter
    BYTE syscall_code[] = {0x0f, 0x34, 0xc3};
#endif

    WORD padding = 0x0;
    // Search padding size until next syscall instruction
    while (memcmp((PVOID)syscall_code, SPT_RVA2VA(PVOID, address, padding), sizeof(syscall_code))) {
        padding++;
        // Windows stubs are quite small, don't waste time
        if(padding > 0x22){
            return 0x0;
        };
    }
    
    return padding;
}

##__SPT_ITERATOR__##

##__SPT_RESOLVER__##

##__SPT_CALLER__##

#if defined(__GNUC__)
##__SPT_STUBS__##
#endif