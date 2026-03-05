# Installation

Here are all the steps needed to install the SysPlant project.
For usage instructions see: [CLI usage](../usage/cli.md), [Python library](../usage/lib.md) or [MCP server](../usage/mcp.md).

---

## Install as a pip dependency

```bash
pip3 install sysplant
```

To also install the optional [MCP server](../usage/mcp.md) support:

```bash
pip3 install sysplant[mcp]
```

## Install with Poetry (recommended for development)

```bash
git clone https://github.com/x42en/sysplant && cd sysplant
poetry install

# Optional: include MCP server dependencies
poetry install --with mcp
```

## Install as a standalone tool

=== "Linux / macOS"

    ```bash
    git clone https://github.com/x42en/sysplant
    cd sysplant
    python3 ./main.py -h
    ```

=== "Windows"

    ```cmd
    git clone https://github.com/x42en/sysplant.git
    cd sysplant
    python .\main.py --help
    ```
