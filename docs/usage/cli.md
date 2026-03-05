## Using Sysplant as a CLI tool

This project can be used as a simple command line tool.

### Installation

> _Requirements: Python 3.10+_

SysPlant is a Python project that generates NIM, C and Rust source code for Windows syscall hooking. You can use it inside your Python project as an external module or directly as a standalone tool.

```sh
git clone https://github.com/x42en/sysplant && cd sysplant
poetry shell
./main.py -h
```

### Usage

This tool comes with various options that should be self-explanatory using the standard `-h` flag.

```bash
$ ./main.py -h
usage: main.py [-h] [--debug | --verbose | --quiet] {list,generate} ...

..:: SysPlant - Your Syscall Factory ::..

positional arguments:
  {list,generate}

options:
  -h, --help       show this help message and exit

Output options:
  --debug          Display all DEBUG messages upon execution
  --verbose        Display all INFO messages upon execution
  --quiet          Remove all messages upon execution
```

Two actions are supported:

- **`list`** — Parse a file or directory to find NtFunction usage
- **`generate`** — Generate a syscall hooking source file to import into your project

Supported output languages are **NIM** (default), **C** and **Rust**.

#### List action

```bash
$ ./main.py list -h
usage: main.py list [-h] path

positional arguments:
  path        Path to search for NtFunction, could be a file or a directory

options:
  -h, --help  show this help message and exit
```

#### Generate action

```bash
$ ./main.py generate -h
usage: main.py generate [-h] [-x86 | -wow | -x64] [-nim | -c | -rust]
                        [-p {all,donut,common} | -f FUNCTIONS] [-x] -o OUTPUT
                        {hell,halo,tartarus,freshy,syswhispers,syswhispers3,canterlot,custom}
                        ...

options:
  -h, --help            show this help message and exit
  -x, --scramble        Randomize internal function names to evade static analysis
  -o OUTPUT, --output OUTPUT
                        Output path for generated file

Architecture options:
  -x86                  Set mode to 32bits
  -wow                  Set mode to WoW64 (execution of 32bits on 64bits)
  -x64                  Set mode to 64bits (Default True)

Language options:
  -nim                  Generate NIM code (Default: true)
  -c                    Generate C code
  -rust                 Generate Rust code

Syscall options:
  -p {all,donut,common}, --preset {all,donut,common}
                        Preset functions to generate (Default: common)
  -f FUNCTIONS, --functions FUNCTIONS
                        Comma-separated functions
```

### Examples

All examples below generate the **common** NtFunction preset by default.

#### Iterator examples

```bash
# Hell's Gate
$ ./main.py generate -o syscall hell

# Halo's Gate
$ ./main.py generate -o syscall halo

# Tartarus' Gate
$ ./main.py generate -o syscall tartarus

# FreshyCalls
$ ./main.py generate -o syscall freshy

# SysWhispers2
$ ./main.py generate -o syscall syswhispers

# SysWhispers3
$ ./main.py generate -o syscall syswhispers3

# Canterlot's Gate (recommended)
$ ./main.py generate -o syscall canterlot
```

#### Custom iterator + method

```bash
# Direct syscall with Canterlot resolver
$ ./main.py generate -o syscall custom -i canterlot -m direct

# Indirect syscall
$ ./main.py generate -o syscall custom -i canterlot -m indirect

# Random indirect syscall
$ ./main.py generate -o syscall custom -i canterlot -m random
```

#### Egg Hunter method

The `egg_hunter` method replaces inline `syscall` instructions with random marker bytes.
At runtime, a sanitizer function patches them back before `main()` is called.

```bash
$ ./main.py generate -c -o syscall custom -i canterlot -m egg_hunter
```

#### Language-specific examples

```bash
# Generate C code for Donut shellcode functions
$ ./main.py generate -c -o syscall -p donut canterlot

# Generate Rust code
$ ./main.py generate -rust -o syscall.rs canterlot

# Generate Rust code with scramble and specific functions
$ ./main.py generate -rust -x -o syscall.rs -f NtCreateSection,NtMapViewOfSection,NtUnmapViewOfSection,NtCreateThreadEx canterlot
```

### Real World Injection Examples

Working injection examples (launching `calc.exe` as proof of concept) are provided in the `example/` directory.
See the [examples README](https://github.com/x42en/sysplant/tree/main/example) for detailed compilation instructions.

#### NIM

1. Install [winim](https://github.com/khchen/winim) and [checksums](https://github.com/nim-lang/checksums): `nimble install winim checksums`
2. Generate: `./main.py generate -o example/syscall canterlot`
3. Compile: `nim c -d=release -d=danger -d=strip --opt=size -d=mingw --app=console --cpu=amd64 --out=inject.exe example/inject.nim`
4. Transfer `inject.exe` to your Windows target.

#### C

1. Install `mingw-w64`: `sudo apt install mingw-w64`
2. Generate: `./main.py generate -c -o example/syscall canterlot`
3. Compile: `x86_64-w64-mingw32-gcc -Wall -s -static -masm=intel example/inject.c -o inject.exe`
4. Transfer `inject.exe` to your Windows target.

#### Rust

1. Install cross-compilation toolchain: `rustup target add x86_64-pc-windows-gnu` + `sudo apt install mingw-w64`
2. Generate: `./main.py generate -rust -o example/rust-inject/src/syscall.rs canterlot`
3. Compile: `cd example/rust-inject && cargo build --release --target x86_64-pc-windows-gnu`
4. Transfer the `.exe` from `target/x86_64-pc-windows-gnu/release/` to your Windows target.

### Documentation

The full API documentation is available in the [API Reference](../documentation/README.md) section.

Happy Hacking :beach: !
