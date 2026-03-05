## Using Sysplant as a CLI tool

This project can be used as a simple command line tool.

### Installation

> _Requirements: Pyton 3.8+_

This is a python project that will generate NIM/C/etc... source code (bit weird hu ?! :grin:). So you can use it inside your python project as an external module or directly on your device as a tool.  
Install the project as you would do for any GitHub project.

```sh
git clone https://github.com/x42en/sysplant && cd sysplant
poetry shell
./main.py -h
```

### Usage

This tool comes with various options that should be self-explanatory using the standard `-h` flag

```bash
$ ./main.py -h
usage: main.py [-h] [--debug | --verbose | --quiet] {list,generate} ...

..:: SysPlant - Your Syscall Factory ::..

positional arguments:
  {list,generate}

optional arguments:
  -h, --help       show this help message and exit

Output options:
  --debug          Display all DEBUG messages upon execution
  --verbose        Display all INFO messages upon execution
  --quiet          Remove all messages upon execution
```

By now only two actions are supported `list` (that will parse file or directory to find NtFunction usage) and `generate` that will generate a syscall hooking file to import into your project.

Supported output languages are **NIM** (default), **C** and **Rust**.

#### List action

In order to use the list action you could check the associated help `./main.py list -h`

```bash
$ ./main.py list -h
usage: main.py list [-h] path

positional arguments:
  path        Path to search for NtFunction, could be a file or a directory

optional arguments:
  -h, --help  show this help message and exit
```

#### Generate action

In order to use the generate action you could check the associated help `./main.py generate -h`

```bash
$ ./main.py generate -h
usage: main.py generate [-h] [-x86 | -wow | -x64] [-nim | -c] [-p {all,donut,common} | -f FUNCTIONS] [-x] -o OUTPUT {hell,halo,tartarus,freshy,syswhispers,syswhispers3,canterlot,custom} ...

positional arguments:
  {hell,halo,tartarus,freshy,syswhispers,syswhispers3,canterlot,custom}

optional arguments:
  -h, --help            show this help message and exit
  -x, --scramble        Randomize internal function names to evade static analysis
  -o OUTPUT, --output OUTPUT
                        Output path for NIM generated file

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

Here are some usage examples that will generate common NtFunctions only.  
This tool is not restricted to them, please **[READ THE DOC](https://x42en.github.io/sysplant/)**

#### Hell's Gate generation

```bash
$ ./main.py generate -o syscall hell
```

#### Halo's Gate generation

```bash
$ ./main.py generate -o syscall halo
```

#### Tartarus's Gate generation

```bash
$ ./main.py generate -o syscall tartarus
```

#### FreshyCall generation

```bash
$ ./main.py generate -o syscall freshy
```

#### Syswhispers2 like generation

```bash
$ ./main.py generate -o syscall syswhispers
```

#### Syswhispers3 like generation

```bash
$ ./main.py generate -o syscall syswhispers3
```

#### Canterlot's Gate generation

```bash
$ ./main.py generate -o syscall canterlot
```

#### Custom generation

```bash
$ ./main.py generate -o syscall custom -i canterlot -m direct
```

#### Generate C Code using Canterlot's Gate for [Donut](https://github.com/TheWover/donut) functions

```bash
$ ./main.py generate -c -o syscall -p donut canterlot
```

#### Generate Rust Code using Canterlot's Gate

```bash
$ ./main.py generate -rust -o syscall.rs canterlot
```

#### Generate Rust Code with scramble and specific functions

```bash
$ ./main.py generate -rust -x -o syscall.rs -f NtCreateSection,NtMapViewOfSection,NtUnmapViewOfSection,NtCreateThreadEx canterlot
```

#### Real world Injection

##### NIM Example

A simple example (launching calc.exe) is accessible using `inject.nim`.

1. Be sure to install [winim](https://github.com/khchen/winim) and [checksums](https://github.com/nim-lang/checksums) libraries first: `nimble install winim checksums`
2. Generate the `syscall.nim` file with `./main.py generate -o example/syscall canterlot`
3. Compile the injection template file with `nim c -d=release -d=danger -d=strip --opt=size -d=mingw --app=console --cpu=amd64 --out=app.exe example/inject.nim` on Linux (be sure to have mingw installed)
4. Copy the `app.exe` generated on your Windows device.

##### Rust Example

A simple example (launching calc.exe) is accessible using `inject.rs`.

1. Be sure to install the Rust cross-compilation toolchain: `rustup target add x86_64-pc-windows-gnu` and have `mingw-w64` installed
2. Generate the `syscall.rs` file with `./main.py generate -rust -x -o example/rust-inject/src/syscall.rs canterlot`
3. Compile the injection template with `cd example/rust-inject && cargo build --release --target x86_64-pc-windows-gnu`
4. Copy the `.exe` generated in `target/x86_64-pc-windows-gnu/release/` on your Windows device.

##### C Example

A simple example (launching calc.exe) is accessible using `inject.c`.

1. Be sure to have `mingw-w64` installed
2. Generate the `syscall.c` file with `./main.py generate -c -o example/syscall canterlot`
3. Compile: `x86_64-w64-mingw32-gcc -O2 -s example/inject.c -o inject.exe`
4. Copy the `inject.exe` generated on your Windows device.

### Documentation

The API documentation and associated options is available [here](https://x42en.github.io/sysplant/documentation/)

Happy Hacking :beach: !
