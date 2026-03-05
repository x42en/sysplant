# Prerequisites

SysPlant requires **Python 3.10+**. The core library has no external runtime dependencies.

## Required

| Dependency   | Version | Purpose            |
| ------------ | ------- | ------------------ |
| Python       | >= 3.10 | Runtime            |
| pip / Poetry | latest  | Package management |

## Optional

| Dependency      | Version | Purpose                                                   |
| --------------- | ------- | --------------------------------------------------------- |
| `sysplant[mcp]` | -       | MCP server for AI coding assistants (installs `mcp[cli]`) |
| MinGW           | latest  | Cross-compile C / Rust output from Linux                  |
| Nim             | >= 2.0  | Compile NIM output                                        |
| Rust            | latest  | Compile Rust output (`x86_64-pc-windows-gnu` target)      |

!!! note
The MCP server dependency is **optional** and only needed if you plan to expose SysPlant through a Model Context Protocol server. See [MCP Server usage](../usage/mcp.md) for details.
