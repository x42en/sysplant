# SysPlant
#### "Your Syscall Factory" *(feat. Canterlot's Gate)*

![Canterlot's Gate](pictures/canterlot.jpeg)

SysPlant is a small implementation in NIM of the currently known syscall hooking methods. It currently supports following gates:
- [Hell's gate](https://github.com/am0nsec/HellsGate)
- [Halos / Tartarus gate](https://github.com/trickster0/TartarusGate)
- [FreshyCalls](https://github.com/crummie5/FreshyCalls)
- [SysWhispers2](https://github.com/jthuraisamy/SysWhispers2)
- **Canterlot's Gate ! :unicorn: :rainbow:** *(from an initial idea of [MDSEC article](https://www.mdsec.co.uk/2022/04/resolving-system-service-numbers-using-the-exception-directory/)) but who was missing a pony name*
  
It then allows you to generate direct or indirect syscall stubs.  

*Note: You can also generate your own combinations using the proper options...*

## Introduction
This personal project aims to be a simple tool to better understand & generate different syscall retrieval methods, and being able to play with direct / indirect syscall stub. The first goal was to get my hands into NIM and then it overflow :wink: ...

## Installation
This is a python project that will generate NIM source code (bit weird hu ?! :grin:). So you can use it inside your python project as an external module or directly on your device as a tool.

### As a Python module
If you are using standard pip3 package manager
```sh
pip3 install sysplant
```

If you are more inclined to use virtual environments *(you should!)* this project is based on [Poetry](https://python-poetry.org/) virtual env.
```sh
poetry add sysplant
```

### As a single tool
Install the project as you would do for any GitHub project
```sh
git clone https://github.com/x42en/sysplant && cd sysplant
poetry shell
poetry install
./main.py -h
```

## Help
This tool comes with various options that should be self-explanatory using the standard `-h` flag
```bash
$ ./main.py -h
usage: main.py [-h] [--debug | --verbose | --quiet] [-i {syswhisper,freshy,hell,halo,canterlot}] [-r {basic,random}] [-s {direct,indirect}] [-p {all,donut,common} | -f FUNCTIONS] -o OUTPUT [-x]

..:: SysPlant - Your Syscall Factory ::..

optional arguments:
  -h, --help            show this help message and exit
  --debug               Display all DEBUG messages upon execution
  --verbose             Display all INFO messages upon execution
  --quiet               Remove all messages upon execution
  -i {syswhisper,freshy,hell,halo,canterlot}, --iterator {syswhisper,freshy,hell,halo,canterlot}
                        Select syscall iterator (Default: canterlot)
  -r {basic,random}, --resolver {basic,random}
                        Select syscall resolver (Default: basic)
  -s {direct,indirect}, --stub {direct,indirect}
                        Select syscall stub (Default: indirect)
  -p {all,donut,common}, --preset {all,donut,common}
                        Preset functions to generate (Default: common)
  -f FUNCTIONS, --functions FUNCTIONS
                        Comma-separated functions
  -o OUTPUT, --output OUTPUT
                        Output path for NIM generated file
  -x, --scramble        Randomize internal function names to evade static analysis
```

## Example
A simple example (launching calc.exe) is accessible using `inject.nim`.  
1. Be sure to install [winim](https://github.com/khchen/winim) library first: `nimble install winim`
2. Generate the `syscall.nim` file with `./main.py -o example/syscall.nim`
3. Compile the injection template file with `nim c -d=release -d=danger -d=strip --opt=size -d=mingw --app=console --cpu=amd64 --out=app.exe example/inject.nim` on Linux (be sure to have mingw installed)
4. Copy the `app.exe` generated on your Windows device.

Happy Hacking :beach: !

## Credits
Massive shout-out to these useful projects that helps me during this journey, or individuals for their reviews
- [@alice blogpost about syscalls techniques](https://alice.climent-pommeret.red/posts/direct-syscalls-hells-halos-syswhispers2/)
- [@redops blogpost about direct vs indirect syscalls](https://redops.at/en/blog/direct-syscalls-a-journey-from-high-to-low)
- [@Jackson_T & @modexpblog for Syswhispers2](https://github.com/jthuraisamy/SysWhispers2)
- [@klezvirus for syswhispers3](https://github.com/klezVirus/SysWhispers3)

## :construction: TODO
This project is really in WIP state...  
Some PR & reviews are more than welcome :tada: !
- [x] Add internal names randomization
- [ ] Add x86 support
- [ ] Add WoW64 support
- [ ] Add some tests
- [ ] Setup documentation

## License
This project is licensed under the [MIT License](https://www.tldrlegal.com/license/mit-license), for individuals only. If you want to integrate this work in your commercial project please contact me through `0x42en[at]gmail.com`