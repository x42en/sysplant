{.passC:"-masm=intel".}

# Import internal libs
import std/md5
import std/bitops
import std/tables
import std/random
import std/sequtils
import std/strutils
import std/strformat
import std/algorithm

# Import external libs
import winim

type
    Syscall = object
        ssn: int
        address: int64

    IMAGE_RUNTIME_FUNCTION_ENTRY_UNION {.pure, union.} = object
        UnwindInfoAddress: DWORD
        UnwindData: DWORD
    IMAGE_RUNTIME_FUNCTION_ENTRY {.pure.} = object
        BeginAddress: DWORD
        EndAddress: DWORD
        u1: IMAGE_RUNTIME_FUNCTION_ENTRY_UNION
    PIMAGE_RUNTIME_FUNCTION_ENTRY = ptr IMAGE_RUNTIME_FUNCTION_ENTRY

##__TYPE_DEFINITIONS__##

##__SPT_DEBUG__##
##__SPT_SEED__##
var ssdt: Table[DWORD, Syscall]

## utils from https://github.com/khchen/memlib/blob/master/memlib.nim
template `++`[T](p: var ptr T) =
    ## syntax sugar for pointer increment
    p = cast[ptr T](p[int] +% sizeof(T))

template `--`[T](p: var ptr T) =
    ## syntax sugar for pointer increment
    p = cast[ptr T](p[int] -% sizeof(T))

proc `[]`[T](x: T, U: typedesc): U {.inline.} =
    ## syntax sugar for cast
    when sizeof(U) > sizeof(x):
        when sizeof(x) == 1: cast[U](cast[uint8](x).uint64)
        elif sizeof(x) == 2: cast[U](cast[uint16](x).uint64)
        elif sizeof(x) == 4: cast[U](cast[uint32](x).uint64)
        else: cast[U](cast[uint64](x))
    else:
        cast[U](x)

proc `{}`[T](x: T, U: typedesc): U {.inline.} =
    ## syntax sugar for zero extends cast
    when sizeof(x) == 1: x[uint8][U]
    elif sizeof(x) == 2: x[uint16][U]
    elif sizeof(x) == 4: x[uint32][U]
    elif sizeof(x) == 8: x[uint64][U]
    else: {.fatal.}
    
proc `{}`[T](p: T, x: SomeInteger): T {.inline.} =
    ## syntax sugar for pointer (or any other type) arithmetics
    (p[int] +% x{int})[T]
##

## Avoid ptr_math dependency from https://github.com/kaushalmodi/ptr_math/blob/main/src/ptr_math.nim
proc `-`*[T; S: SomeInteger](p: ptr T, offset: S): ptr T =
    return cast[ptr T](cast[ByteAddress](p) -% (int(offset) * sizeof(T)))

proc `-`*[S: SomeInteger](p: pointer, offset: S): pointer =
    return cast[pointer](cast[ByteAddress](p) -% int(offset))

proc `+`*[T; S: SomeInteger](p: ptr T, offset: S): ptr T =
    return cast[ptr T](cast[ByteAddress](p) +% (int(offset) * sizeof(T)))

proc `+`*[S: SomeInteger](p: pointer, offset: S): pointer =
    return cast[pointer](cast[ByteAddress](p) +% int(offset))

proc `[]=`*[T; S: SomeInteger](p: ptr T, offset: S, val: T) =
    (p + offset)[] = val

proc `[]`*[T; S: SomeInteger](p: ptr T, offset: S): var T =
    ## Retrieves the value from `p[offset]`.
    return (p + offset)[]
##

proc SPT_HashSyscallName(name: string): DWORD =
    let hash = getMD5(&"{SPT_SEED}{name[2 .. ^1]}")
    return cast[DWORD](parseHexInt(hash[0 .. ^25]))

##__SPT_ITERATOR__##

proc SPT_GetSyscallNumber(hash: DWORD): int =
    # Always generate table
    SPT_PopulateSyscalls()
    return ssdt[hash].ssn

##__SPT_RESOLVER__##

##__SPT_CALLER__##

##__SPT_STUBS__##