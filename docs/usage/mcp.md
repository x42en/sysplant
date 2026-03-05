## Using Sysplant as a MCP Server

SysPlant exposes its full syscall generation engine through a **[Model Context Protocol (MCP)](https://modelcontextprotocol.io/)** server. This allows AI coding assistants — Claude Code, Cursor, Windsurf, VS Code Copilot, and others — to generate, inspect and manipulate syscall code directly from their chat interface.

> :sparkles: No copy-paste, no CLI flags to remember — just ask your AI assistant to generate the syscalls you need.

---

### Installation

The MCP server requires the optional `mcp` dependency group:

```bash
# From a Poetry-managed clone
poetry install --with mcp

# Or via pip
pip install sysplant "mcp[cli]>=1.0"
```

---

### Quick Start

#### stdio (default)

Most AI clients (Claude Code, Cursor, VS Code Copilot Chat) communicate over **stdio**:

```bash
python bridge_mcp_sysplant.py
```

Configure your AI client to launch this command. For example, in Claude Code's `mcp.json`:

```json
{
  "mcpServers": {
    "sysplant": {
      "command": "python",
      "args": ["bridge_mcp_sysplant.py"],
      "cwd": "/path/to/sysplant"
    }
  }
}
```

#### SSE (Server-Sent Events)

For web-based clients or remote access:

```bash
python bridge_mcp_sysplant.py --transport sse --host 0.0.0.0 --port 9090
```

#### Streamable HTTP

Bidirectional HTTP transport (recommended for web integrations):

```bash
python bridge_mcp_sysplant.py --transport streamable-http --host 0.0.0.0 --port 9090
```

---

### Available Tools

The MCP server exposes **9 tools** that cover the full pentesting workflow:

| Tool                      | Description                                                                |
| ------------------------- | -------------------------------------------------------------------------- |
| `generate_syscalls`       | Generate a complete syscall source file (C / NIM / Rust)                   |
| `scan_ntfunctions`        | Scan source files to detect which Nt/Zw functions are referenced           |
| `list_supported_syscalls` | List all ~483 supported NtFunction names                                   |
| `list_common_syscalls`    | List the 31 most-used NtFunctions for injection / evasion                  |
| `list_donut_syscalls`     | List the 14 NtFunctions used by the Donut shellcode loader                 |
| `get_function_prototype`  | Look up the full prototype (params, types, direction) of any NtFunction    |
| `list_iterators`          | List all 7 syscall iterators with origin and technique description         |
| `list_methods`            | List all 4 caller stub methods with evasion trade-offs                     |
| `list_languages`          | List supported languages with file extensions and compilation instructions |

#### `generate_syscalls` — Main tool

This is the primary tool. It produces a self-contained source file with syscall stubs, resolver, iterator and caller.

**Parameters:**

| Parameter   | Type      | Default     | Description                                                  |
| ----------- | --------- | ----------- | ------------------------------------------------------------ |
| `language`  | string    | `nim`       | Target language: `nim`, `c`, or `rust`                       |
| `arch`      | string    | `x64`       | Architecture: `x64`, `x86`, or `wow`                         |
| `iterator`  | string    | `canterlot` | Syscall resolution strategy (see `list_iterators`)           |
| `method`    | string    | `direct`    | Caller stub type (see `list_methods`)                        |
| `preset`    | string    | `common`    | Predefined set: `common` (31), `donut` (14), or `all` (~483) |
| `functions` | list[str] | _None_      | Custom list of NtFunction names — overrides `preset`         |
| `scramble`  | bool      | `false`     | Randomize internal symbol names to evade static signatures   |

**Example conversation with your AI assistant:**

> _"Generate a C syscall file using Canterlot's Gate with egg_hunter method, common preset, and scramble enabled."_

The assistant will call `generate_syscalls(language="c", iterator="canterlot", method="egg_hunter", scramble=True)` and return the complete source code.

---

### Available Resource

The server also exposes one **MCP resource** for comprehensive documentation:

| URI                     | Description                                                      |
| ----------------------- | ---------------------------------------------------------------- |
| `sysplant://docs/guide` | Full reference: iterators, methods, languages, presets, workflow |

AI clients can read this resource to understand SysPlant capabilities without any tool call.

---

### Iterators

Each iterator implements a different strategy for resolving syscall numbers at runtime from the in-memory `ntdll.dll` image:

| Iterator       | Origin                  | Technique                                         |
| -------------- | ----------------------- | ------------------------------------------------- |
| `hell`         | Hell's Gate (2020)      | Reads syscall number from ntdll in-memory stubs   |
| `halo`         | Halo's Gate (2021)      | Walks neighbours when target stub is hooked       |
| `tartarus`     | Tartarus' Gate (2021)   | Deeper neighbour walk to bypass aggressive hooks  |
| `freshy`       | FreshyCalls (2020)      | Uses exception directory to resolve numbers       |
| `syswhispers`  | SysWhispers2 (2021)     | Sorts Zw exports by address for syscall numbers   |
| `syswhispers3` | SysWhispers3 (2022)     | SysWhispers2 + egg_hunter / random jump support   |
| `canterlot`    | Canterlot's Gate (2022) | PE exception directory (RUNTIME_FUNCTION) parsing |

> :bulb: **Recommendation:** `canterlot` is the most robust for modern environments.

---

### Methods

Each method defines how the resolved syscall is actually executed:

| Method       | Technique                                                                  |
| ------------ | -------------------------------------------------------------------------- |
| `direct`     | Inline `syscall` instruction — simple but visible from outside ntdll       |
| `indirect`   | Jump into real ntdll stub — return address inside ntdll, evades call-stack |
| `random`     | Like indirect, but picks a random ntdll stub each time                     |
| `egg_hunter` | Egg marker in stubs, patched at runtime by a sanitizer before `main()`     |

---

### Compilation Reference

Once you have the generated source file, compile with the recommended flags:

#### C

```bash
x86_64-w64-mingw32-gcc -Wall -s -static -masm=intel inject.c -o inject.exe
```

#### NIM

```bash
nim c -d=release -d=danger -d=strip --opt=size -d=mingw --cpu=amd64 --out=inject.exe inject.nim
```

#### Rust

Add a release profile to your `Cargo.toml`:

```toml
[profile.release]
strip = true             # Strip all symbols
lto = true               # Link-time optimization
codegen-units = 1        # Single codegen unit for better optimization
panic = "abort"          # No unwinding overhead
overflow-checks = false  # Disable runtime overflow checks
```

Then build:

```bash
cargo build --release --target x86_64-pc-windows-gnu
```

---

### Typical Workflow

1. **Discover** — Ask your AI assistant what iterators and methods are available (`list_iterators`, `list_methods`)
2. **Scan** — Point `scan_ntfunctions` at your existing injection code to detect which Nt functions you use
3. **Generate** — Call `generate_syscalls` with your choices (language, iterator, method, functions or preset)
4. **Inspect** — Use `get_function_prototype` to check parameter details for specific functions
5. **Compile** — Save the output and compile with the recommended flags above

---

### Troubleshooting

| Issue                            | Solution                                                                                 |
| -------------------------------- | ---------------------------------------------------------------------------------------- |
| `ModuleNotFoundError: mcp`       | Install the mcp dependency: `poetry install --with mcp` or `pip install "mcp[cli]>=1.0"` |
| SSE/HTTP transport fails to bind | Check that the port is available: `--port 9090`                                          |
| `DBusError` during install       | Set `PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring` before `poetry install`       |
| Generated code doesn't compile   | Verify you are using the recommended compilation flags for your language                 |
