## Using Sysplant as a Python Library

This project has been designed so it can be embedded in your project as a simple external module.

### Installation

Using pip:

```bash
pip3 install sysplant
```

Using Poetry:

```bash
poetry add sysplant
```

### Usage

#### NIM (default)

```python
#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from sysplant.sysplant import Sysplant

# Initialize the class
bot = Sysplant(arch="x64", language="nim")

# Generate code
bot.generate(
    iterator="canterlot",
    method="random",
    syscalls="common"
)

# Optionally randomize internal names
bot.scramble()

# Write to file
bot.output("/tmp/syscall")
```

#### C

```python
from sysplant.sysplant import Sysplant

bot = Sysplant(arch="x64", language="c")
bot.generate(iterator="canterlot", method="random", syscalls="common")
bot.scramble()
bot.output("/tmp/syscall")
```

#### C++

```python
from sysplant.sysplant import Sysplant

bot = Sysplant(arch="x64", language="cpp")
bot.generate(iterator="canterlot", method="random", syscalls="common")
bot.scramble()
bot.output("/tmp/syscall")
```

#### Rust

```python
from sysplant.sysplant import Sysplant

bot = Sysplant(arch="x64", language="rust")
bot.generate(iterator="canterlot", method="random", syscalls="common")
bot.scramble()
bot.output("/tmp/syscall")
```

#### Egg Hunter (any language)

The `egg_hunter` method replaces inline `syscall` instructions with random marker bytes.
At runtime, a sanitizer auto-patches them back before `main()` is called.

```python
from sysplant.sysplant import Sysplant

bot = Sysplant(arch="x64", language="c")
bot.generate(iterator="canterlot", method="egg_hunter", syscalls="common")
bot.scramble(True)  # Returns the generated code as a string
bot.output("/tmp/syscall")
```

#### Custom function list

```python
from sysplant.sysplant import Sysplant

bot = Sysplant(arch="x64", language="nim")
bot.generate(
    iterator="canterlot",
    method="indirect",
    syscalls=["NtCreateThreadEx", "NtAllocateVirtualMemory", "NtWriteVirtualMemory"]
)
bot.scramble()
bot.output("/tmp/syscall")
```

#### Scan for NtFunction usage

```python
from sysplant.sysplant import Sysplant

bot = Sysplant()
found = bot.list("/path/to/your/inject.c")
print(f"Found {len(found)} NtFunctions: {', '.join(sorted(found))}")
```

### Available Parameters

| Parameter  | Values                                                                           | Default    |
| ---------- | -------------------------------------------------------------------------------- | ---------- |
| `arch`     | `x64`, `x86`, `wow`                                                              | `x64`      |
| `language` | `nim`, `c`, `cpp`, `rust`                                                        | `nim`      |
| `iterator` | `hell`, `halo`, `tartarus`, `freshy`, `syswhispers`, `syswhispers3`, `canterlot` | —          |
| `method`   | `direct`, `indirect`, `random`, `egg_hunter`                                     | —          |
| `syscalls` | `"common"`, `"donut"`, `"all"`, or a list of NtFunction names                    | `"common"` |

### Documentation

The full API documentation is available in the [API Reference](../documentation/README.md) section.
