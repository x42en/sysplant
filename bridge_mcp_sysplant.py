#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SysPlant MCP Server
===================
Exposes the syscall factory as an MCP (Model Context Protocol) server,
allowing AI clients to generate Windows syscall hooking code for C, NIM
and Rust from any MCP-compatible host (Claude Code, Cursor, etc.).

Transports
----------
- **stdio**            (default) — for Claude Code, Cursor, etc.
- **sse**              — Server-Sent Events over HTTP
- **streamable-http**  — Streamable HTTP (bidirectional, recommended for web)

Usage
-----
    # stdio (default)
    python bridge_mcp_sysplant.py

    # SSE on custom host/port
    python bridge_mcp_sysplant.py --transport sse --host 0.0.0.0 --port 9090

    # Streamable HTTP
    python bridge_mcp_sysplant.py --transport streamable-http --host 0.0.0.0 --port 9090
"""

import os
import json
import argparse

import importlib.resources as pkg_resources

from mcp.server.fastmcp import FastMCP

from sysplant.sysplant import Sysplant
from sysplant.managers.templateManager import TemplateManager
from sysplant.constants.sysplantConstants import SysPlantConstants
from sysplant import data as pkg_data

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
VALID_LANGUAGES = {"nim", "c", "cpp", "rust"}
VALID_ARCHS = {"x86", "x64", "wow"}
VALID_ITERATORS = {
    "hell",
    "halo",
    "tartarus",
    "freshy",
    "syswhispers",
    "syswhispers3",
    "canterlot",
}
VALID_METHODS = {"direct", "indirect", "random", "egg_hunter"}
VALID_PRESETS = {"all", "common", "donut"}

ITERATOR_DESCRIPTIONS = {
    "hell": "Hell's Gate (2020) — Original technique by @RtlMateusz & @am0nsec. "
    "Reads syscall numbers directly from ntdll.dll in-memory stubs.",
    "halo": "Halo's Gate (2021) — By @Sektor7net. Extends Hell's Gate by walking "
    "neighbouring syscall stubs when the target stub is hooked.",
    "tartarus": "Tartarus' Gate (2021) — By @trickster0. Further improves Halo's Gate "
    "with deeper neighbour traversal to bypass more aggressive hooks.",
    "freshy": "FreshyCalls (2020) — By @crummie5. Uses exception directory parsing to "
    "resolve syscall numbers without reading stub bytes.",
    "syswhispers": "SysWhispers2 (2021) — By @Jackson_T. Sorts Zw* exports by address "
    "to derive syscall numbers. Uses indirect syscall stubs.",
    "syswhispers3": "SysWhispers3 (2022) — By @klezVirus. Adds egg_hunter / random "
    "jump techniques to SysWhispers2.",
    "canterlot": "Canterlot's Gate (2022) — By @MDSecLabs & @0x42en. Uses the PE "
    "exception directory (RUNTIME_FUNCTION) to resolve syscall numbers "
    "without touching ntdll stub bytes.",
}

METHOD_DESCRIPTIONS = {
    "direct": "Direct syscall — Executes the syscall instruction inline in your "
    "process. Simplest approach but leaves a syscall from outside ntdll.",
    "indirect": "Indirect syscall — Jumps into the real ntdll stub to execute the "
    "syscall instruction. Return address points inside ntdll, evading "
    "call-stack heuristics.",
    "random": "Random indirect — Same as indirect but selects a random ntdll syscall "
    "stub each time, adding variance to the return address.",
    "egg_hunter": "Egg hunter — Places a unique marker (egg) in the stub instead of "
    "syscall;ret. A sanitizer function patches all eggs with the real "
    "opcodes at runtime. Evades static signature scans.",
}


# ---------------------------------------------------------------------------
# Instructions (auto-sent to AI clients on session init)
# ---------------------------------------------------------------------------
SYSPLANT_INSTRUCTIONS = """\
SysPlant is a Syscall Factory that generates Windows syscall hooking code \
for C, C++, NIM and Rust. It supports 7 gate iterators (syscall resolution \
strategies) and 4 caller stub methods.

Quick start:
1. Use `list_iterators` and `list_methods` to see available options.
2. Use `generate_syscalls` to produce a complete syscall source file.
3. Use `list_supported_syscalls` to discover all ~300+ Nt functions.
4. Use `get_function_prototype` to inspect a specific function signature.
5. Use `scan_ntfunctions` to detect which Nt functions a source file uses.

Typical pentesting workflow:
    a) Pick a language: nim (default), c, cpp, or rust.
    b) Pick an iterator: canterlot (recommended), hell, halo, tartarus, \
freshy, syswhispers, syswhispers3.
    c) Pick a method: direct, indirect, random, or egg_hunter.
    d) Optionally enable scramble=True to randomize internal symbol names.
    e) Call generate_syscalls with these choices and either a preset \
(common, donut, all) or a custom list of NtFunction names.

The generated code is returned as a string — save it as syscall.h (C), \
syscall.hpp (C++), syscall.nim (NIM) or syscall.rs (Rust) next to your injection code.

For egg_hunter method: the generated file includes an auto-init mechanism \
that patches egg markers before main(). No manual call required.

Use the `sysplant://docs/guide` resource for a comprehensive reference.
"""


# ---------------------------------------------------------------------------
# FastMCP Server
# ---------------------------------------------------------------------------
mcp = FastMCP("sysplant", instructions=SYSPLANT_INSTRUCTIONS)


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------
def _validate_language(lang: str) -> None:
    if lang not in VALID_LANGUAGES:
        raise ValueError(
            f"Unsupported language '{lang}'. Choose from: {', '.join(sorted(VALID_LANGUAGES))}"
        )


def _validate_arch(arch: str) -> None:
    if arch not in VALID_ARCHS:
        raise ValueError(
            f"Unsupported architecture '{arch}'. Choose from: {', '.join(sorted(VALID_ARCHS))}"
        )


def _validate_iterator(name: str) -> None:
    if name not in VALID_ITERATORS:
        raise ValueError(
            f"Unknown iterator '{name}'. Choose from: {', '.join(sorted(VALID_ITERATORS))}"
        )


def _validate_method(name: str) -> None:
    if name not in VALID_METHODS:
        raise ValueError(
            f"Unknown method '{name}'. Choose from: {', '.join(sorted(VALID_METHODS))}"
        )


def _load_prototypes() -> dict:
    """Load NtFunction prototypes from the bundled prototypes.json."""
    proto_file = pkg_resources.files(pkg_data).joinpath("prototypes.json")
    return json.loads(proto_file.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# MCP Resource — comprehensive documentation
# ---------------------------------------------------------------------------
GUIDE_CONTENT = """\
# SysPlant — Syscall Factory Reference

## Overview

SysPlant generates **position-independent syscall hooking code** for Windows \
in three languages: **C** (.h), **NIM** (.nim), and **Rust** (.rs).

It resolves syscall numbers at runtime using one of 7 "gate" iterators, \
then invokes them via one of 4 caller stub methods. The result is a single \
self-contained source file you include alongside your injection code.

---

## Iterators (syscall resolution strategies)

Each iterator answers: *"What is the syscall number for NtXxx?"*

| Iterator       | Origin                 | Technique                                          |
| -------------- | ---------------------- | -------------------------------------------------- |
| `hell`         | Hell's Gate (2020)     | Reads syscall number from ntdll in-memory stubs    |
| `halo`         | Halo's Gate (2021)     | Walks neighbours when target stub is hooked        |
| `tartarus`     | Tartarus' Gate (2021)  | Deeper neighbour walk to bypass aggressive hooks   |
| `freshy`       | FreshyCalls (2020)     | Uses exception directory to resolve numbers        |
| `syswhispers`  | SysWhispers2 (2021)    | Sorts Zw exports by address for syscall numbers    |
| `syswhispers3` | SysWhispers3 (2022)    | SysWhispers2 + egg_hunter / random jump support    |
| `canterlot`    | Canterlot's Gate (2022)| PE exception directory (RUNTIME_FUNCTION) parsing  |

**Recommendation:** `canterlot` is the most robust for modern environments.

---

## Methods (caller stub strategies)

Each method answers: *"How do we execute the resolved syscall?"*

| Method       | Technique                                                      |
| ------------ | -------------------------------------------------------------- |
| `direct`     | Inline `syscall` instruction in your code                      |
| `indirect`   | Jump into real ntdll stub — return address inside ntdll        |
| `random`     | Like indirect, but picks a random ntdll stub each time         |
| `egg_hunter` | Egg marker in stubs, patched at runtime by a sanitizer         |

**`egg_hunter` details:**
- A unique 8-byte marker (4 random bytes repeated twice) replaces `syscall; ret`
- `SPT_SanitizeSyscalls()` scans the PE .text section and patches all markers
- Auto-initialization runs before `main()` via CRT init (C/C++), module-scope call \
(NIM), or explicit call (Rust)

---

## Languages

| Language | Output file | Compiler / toolchain                                  |
| -------- | ----------- | --------------------------------------------------------------------------------- |
| `c`      | `.h`        | MinGW: `x86_64-w64-mingw32-gcc -Wall -s -static -masm=intel`                      |
| `cpp`    | `.hpp`      | MinGW: `x86_64-w64-mingw32-g++ -Wall -s -static -masm=intel`                      |
| `nim`    | `.nim`      | `nim c -d=release -d=mingw -d=danger -d=strip -d=static --opt=size --cpu=amd64`   |
| `rust`   | `.rs`       | `cargo build --release --target x86_64-pc-windows-gnu` |
**Rust release profile** — add to `Cargo.toml` for size-optimized, stripped PIC output:

```toml
[profile.release]
strip = true             # Strip all symbols
lto = true               # Link-time optimization
codegen-units = 1        # Single codegen unit for better optimization
panic = "abort"          # No unwinding overhead
overflow-checks = false  # Disable runtime overflow checks
```
---

## Architectures

| Arch   | Description                              |
| ------ | ---------------------------------------- |
| `x64`  | 64-bit (default)                         |
| `x86`  | 32-bit                                   |
| `wow`  | WoW64 — 32-bit process on 64-bit Windows|

---

## Presets

| Preset   | Count | Description                                  |
| -------- | ----- | -------------------------------------------- |
| `common` | 31    | Most-used Nt functions for injection/evasion |
| `donut`  | 14    | Functions used by the Donut shellcode loader |
| `all`    | ~300+ | Every known Nt function from prototypes.json |

You can also pass a custom list of function names (e.g. \
`["NtCreateThreadEx", "NtAllocateVirtualMemory"]`).

---

## Scramble

When `scramble=True`, all 23 internal symbol names (`SPT_Syscall`, \
`SPT_GetSyscallNumber`, etc.) are replaced with random strings. \
This defeats static signature matching on the generated code.

---

## Workflow Example

```python
# Generate C code with Canterlot iterator, egg_hunter method, common preset
code = generate_syscalls(
    language="c",
    iterator="canterlot",
    method="egg_hunter",
    preset="common",
    scramble=True,
)
# Save as syscall.h next to your inject.c, compile with MinGW
```
"""


@mcp.resource("sysplant://docs/guide")
def sysplant_guide() -> str:
    """Comprehensive reference for SysPlant: iterators, methods, languages,
    architectures, presets, scramble option, and usage workflow."""
    return GUIDE_CONTENT


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------
@mcp.tool()
def generate_syscalls(
    language: str = "nim",
    arch: str = "x64",
    iterator: str = "canterlot",
    method: str = "direct",
    preset: str = "common",
    functions: list[str] | None = None,
    scramble: bool = False,
) -> str:
    """Generate a complete syscall source file for Windows.

    This is the main tool — it produces a self-contained source file with
    syscall stubs, resolver, iterator and caller for the specified language.

    Args:
        language: Target language — nim (default), c, cpp, or rust.
        arch: Target architecture — x64 (default), x86, or wow.
        iterator: Syscall resolution strategy — canterlot (default), hell,
            halo, tartarus, freshy, syswhispers, syswhispers3.
        method: Caller stub type — direct (default), indirect, random,
            or egg_hunter.
        preset: Predefined function set — common (31 functions, default),
            donut (14 functions), or all (~300+ functions).
            Ignored when 'functions' is provided.
        functions: Explicit list of NtFunction names to include (e.g.
            ["NtCreateThreadEx", "NtAllocateVirtualMemory"]).
            When provided, overrides 'preset'.
        scramble: Randomize internal symbol names to evade static signatures.

    Returns:
        Complete source code as a string (C header, C++ header, NIM module, or Rust module).
    """
    _validate_language(language)
    _validate_arch(arch)
    _validate_iterator(iterator)
    _validate_method(method)

    # Determine syscall list
    if functions and len(functions) > 0:
        syscalls = functions
    elif preset in VALID_PRESETS:
        syscalls = preset
    else:
        raise ValueError(
            f"Invalid preset '{preset}'. Choose from: {', '.join(sorted(VALID_PRESETS))}"
        )

    try:
        engine = Sysplant(arch=arch, language=language)
        engine.generate(iterator=iterator, method=method, syscalls=syscalls)
        result = engine.scramble(scramble)
        return result
    except Exception as e:
        return f"Error generating syscalls: {e}"


@mcp.tool()
def scan_ntfunctions(search_path: str) -> str:
    """Scan source files for NtFunction / ZwFunction usage.

    Walks the given file or directory and detects which Nt/Zw functions are
    referenced. Useful for determining which syscalls your injection code needs.

    Supported file extensions: .h, .c, .cpp, .nim, .rs

    Args:
        search_path: Absolute path to a file or directory to scan.

    Returns:
        Comma-separated list of detected NtFunction names, or a message
        if none are found.
    """
    if not os.path.exists(search_path):
        return f"Error: path '{search_path}' does not exist."

    try:
        engine = Sysplant()
        found = engine.list(search_path)
        if found:
            return ", ".join(sorted(found))
        return "No NtFunctions found in the specified path."
    except Exception as e:
        return f"Error scanning: {e}"


@mcp.tool()
def list_supported_syscalls() -> str:
    """List all ~300+ supported NtFunction names.

    Returns every NtFunction that SysPlant knows how to generate a stub for,
    loaded from the built-in prototypes database.

    Returns:
        Newline-separated list of all NtFunction names (sorted).
    """
    try:
        tm = TemplateManager()
        names = sorted(tm.list_supported_syscalls())
        return f"{len(names)} supported functions:\n" + "\n".join(names)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def list_common_syscalls() -> str:
    """List the 31 most common NtFunctions used in offensive tooling.

    These cover process/thread creation, memory operations, section mapping,
    and other essential injection primitives.

    Returns:
        Newline-separated list of common NtFunction names.
    """
    names = sorted(SysPlantConstants.COMMON_SYSCALLS)
    return f"{len(names)} common functions:\n" + "\n".join(names)


@mcp.tool()
def list_donut_syscalls() -> str:
    """List the 14 NtFunctions used by the Donut shellcode loader project.

    Useful when generating stubs specifically for Donut-based payloads.

    Returns:
        Newline-separated list of Donut NtFunction names.
    """
    names = sorted(SysPlantConstants.DONUT_SYSCALLS)
    return f"{len(names)} donut functions:\n" + "\n".join(names)


@mcp.tool()
def get_function_prototype(function_name: str) -> str:
    """Look up the full prototype of a specific NtFunction.

    Returns the return type, library, and all parameters with their types,
    direction (in/out) and optional flag.

    Args:
        function_name: Exact NtFunction name (e.g. NtCreateThreadEx).

    Returns:
        Formatted prototype with parameter details.
    """
    prototypes = _load_prototypes()

    if function_name not in prototypes:
        # Try case-insensitive match
        matches = [k for k in prototypes if k.lower() == function_name.lower()]
        if matches:
            function_name = matches[0]
        else:
            return (
                f"Error: '{function_name}' not found. "
                f"Use list_supported_syscalls to see all available functions."
            )

    proto = prototypes[function_name]
    lines = [
        f"## {function_name}",
        f"Return type: {proto['type']}",
        f"Library: {proto['lib']}",
        f"Parameters ({len(proto['params'])}):",
    ]
    for p in proto["params"]:
        direction = []
        if p.get("in"):
            direction.append("IN")
        if p.get("out"):
            direction.append("OUT")
        opt = ", optional" if p.get("optional") else ""
        dir_str = "/".join(direction) if direction else "—"
        lines.append(f"  - {p['name']}: {p['type']} [{dir_str}{opt}]")

    return "\n".join(lines)


@mcp.tool()
def list_iterators() -> str:
    """List all 7 available syscall iterators with descriptions.

    Each iterator implements a different strategy for resolving syscall
    numbers at runtime from the in-memory ntdll.dll image.

    Returns:
        Formatted list of iterators with their descriptions.
    """
    lines = []
    for name in sorted(ITERATOR_DESCRIPTIONS):
        lines.append(f"## {name}")
        lines.append(ITERATOR_DESCRIPTIONS[name])
        lines.append("")
    return "\n".join(lines)


@mcp.tool()
def list_methods() -> str:
    """List all 4 available syscall caller stub methods with descriptions.

    Each method defines how the resolved syscall is actually executed,
    trading off between simplicity and evasion capability.

    Returns:
        Formatted list of methods with their descriptions.
    """
    lines = []
    for name in sorted(METHOD_DESCRIPTIONS):
        lines.append(f"## {name}")
        lines.append(METHOD_DESCRIPTIONS[name])
        lines.append("")
    return "\n".join(lines)


@mcp.tool()
def list_languages() -> str:
    """List the 4 supported output languages with file extensions and toolchains.

    Returns:
        Formatted list of languages with compilation instructions.
    """
    info = {
        "c": {
            "ext": ".h",
            "compiler": "x86_64-w64-mingw32-gcc -Wall -s -static -masm=intel",
            "note": "Include the generated .h file in your C injection code.",
        },
        "cpp": {
            "ext": ".hpp",
            "compiler": "x86_64-w64-mingw32-g++ -Wall -s -static -masm=intel",
            "note": "Include the generated .hpp file in your C++ injection code.",
        },
        "nim": {
            "ext": ".nim",
            "compiler": "nim c -d=release -d=danger -d=strip --opt=size -d=mingw --cpu=amd64",
            "note": "Import the generated .nim module. Requires winim library.",
        },
        "rust": {
            "ext": ".rs",
            "compiler": "cargo build --release --target x86_64-pc-windows-gnu",
            "note": "Place in src/ of a Cargo project. Requires windows-sys and md5 crates. "
            "Add [profile.release] to Cargo.toml: strip=true, lto=true, "
            'codegen-units=1, panic="abort", overflow-checks=false.',
        },
    }
    lines = []
    for lang, data in info.items():
        lines.append(f"## {lang}")
        lines.append(f"Output extension: {data['ext']}")
        lines.append(f"Compiler: `{data['compiler']}`")
        lines.append(data["note"])
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="SysPlant MCP Server — Syscall factory for AI clients"
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="MCP transport protocol (default: stdio)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind for SSE / streamable-http (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for SSE / streamable-http (default: 8080)",
    )
    args = parser.parse_args()

    if args.transport in ("sse", "streamable-http"):
        mcp.settings.host = args.host
        mcp.settings.port = args.port

    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
