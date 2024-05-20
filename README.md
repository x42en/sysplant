<!-- markdownlint-disable MD033 MD041 -->
<h1 align="center">
..:: SysPlant ::..
</h1>

<p align="center">
  <strong>Your Syscall Factory</strong> <i>(feat. Canterlot's Gate)</i>
</p>

<p align="center">
  <img src="http://sysplant.readthedocs.io/en/main/assets/canterlot.jpeg" alt="Canterlot's Gate"/>
</p>

[![PyPI version](https://img.shields.io/pypi/v/sysplant.svg?logo=pypi&logoColor=FFE873)](https://pypi.org/project/sysplant/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/sysplant.svg?logo=python&logoColor=FFE873)](https://pypi.org/project/sysplant/)
[![Build Status](https://github.com/x42en/sysplant/actions/workflows/build.yml/badge.svg)](https://github.com/x42en/sysplant)
[![Project Licence](https://img.shields.io/github/license/x42en/sysplant.svg)](https://github.com/x42en/sysplant/blob/main/LICENSE)
[![PyPI downloads](https://img.shields.io/pypi/dm/sysplant.svg)](https://pypistats.org/packages/sysplant)
[![Code Quality](https://www.codefactor.io/repository/github/x42en/sysplant/badge)](https://www.codefactor.io/repository/github/x42en/sysplant)
[![Code Coverage](https://codecov.io/gh/x42en/sysplant/branch/main/graph/badge.svg)](https://codecov.io/gh/x42en/sysplant)
[![Code style: Black](https://img.shields.io/badge/code%20style-Black-000000.svg)](https://github.com/psf/black)
[![Documentation Status](https://readthedocs.org/projects/sysplant/badge/?version=latest)](https://sysplant.readthedocs.io/en/latest/?badge=latest)


SysPlant is a python generation tool of the currently known syscall hooking methods. It currently supports following gates (aka: iterators):
  - [Hell's Gate](https://github.com/am0nsec/HellsGate) : Lookup syscall by first opcodes
  - [Halos's Gate](https://blog.sektor7.net/#!res/2021/halosgate.md) : Lookup syscall by first opcodes and search nearby if first instruction is a JMP
  - [Tartarus' Gate](https://github.com/trickster0/TartarusGate) : Lookup syscall by first opcodes and search nearby if first or third instruction is a JMP
  - [FreshyCalls](https://github.com/crummie5/FreshyCalls) : Lookup syscall by name (start with Nt and not Ntdll), sort addresses to retrieve syscall number
  - [SysWhispers2](https://github.com/jthuraisamy/SysWhispers2) : Lookup syscall by name (start with Zw), sort addresses to retrieve syscall number
  - [SysWhispers3](https://github.com/klezVirus/SysWhispers3) : SysWhispers2 style but introduce direct/indirect/random jump with static offset
  - **Canterlot's Gate ! :unicorn: :rainbow:** *(from an initial idea of [MDSEC article](https://www.mdsec.co.uk/2022/04/resolving-system-service-numbers-using-the-exception-directory/)) but who was missing a pony name* : Lookup syscall using Runtime Exception Table (sorted by syscall number) and detect offset to syscall instruction for random jumps.
  - **Custom** Allows you to choose an iterator and a syscall stub method (direct / indirect / random) which describe the way your NtFunctions will be effectively called.

> :warning: **DISCLAIMER**  
> Please only use this tool on systems you have permission to access.  
> Usage is restricted to Pentesting or Education only.  
> All credits are based on my own research, please feel free to claim any method if I made mistakes...

---

## Introduction
This personal project aims to be a simple tool to better understand & generate different syscall retrieval methods, and being able to play with direct / indirect syscall stub. The first goal was to get my hands into NIM and then it overflow :wink: ...  
SysPlant has been developped for Linux users, some stuff might be broken within Windows or Mac. PR are welcome if you found anything that does not work as expected.

## What is `iterator` option ?
Sysplant is based on existing mechanisms for syscall number and addresses retrieval. I do not claim any of their discovery, I just harmonize all this methods in a single tool to be able to generate them easily using templates. These mechanisms are called `iterator`, if you look at the code you'll probably understand why :wink:  
If you want to go further in the explanations of *what is a syscall ?* you should check [@Alice Climent blogpost about syscalls techniques](https://alice.climent-pommeret.red/posts/direct-syscalls-hells-halos-syswhispers2/)

## What is `method` option ?
One your `iterator` has been choosen you can then specify a `method` option based on the existing way to call syscalls. All the iterator are supported which let you select whatever you want as a final syscall stub.

  1. **Direct:** the syscall is made directly in the Sysplant ASM call. You only need the syscall number but AV/EDR might see you...
  2. **Indirect:** the Sysplant ASM call jump to the begining of Ntdll stub. You only need syscall address and no longer call syscall in your code but AV/EDR might hook these functions
  3. **Random:** the Sysplant ASM call jump to a random syscall instruction of Ntdll stubs. You need the syscall number and 1 syscall instruction address. You then no longer call syscall in your code and can avoid hooked functions.


[![Sysplant Stubs](http://sysplant.readthedocs.io/en/main/assets/sysplant_stubs.png)](http://sysplant.readthedocs.io/en/main/assets/sysplant_stubs.png)

## Documentation
I've tried to keep an up to date documentation, so please **[READ THE DOC](http://sysplant.readthedocs.io/en/main/)**. You will find there many information about the tool's usages and a complete description of the classes and methods.  

Some specifics usages are described:
  - [Sysplant as a CLI tool](http://sysplant.readthedocs.io/en/main/usage/cli)
  - [Sysplant as a Python's module](http://sysplant.readthedocs.io/en/main/usage/lib)

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
  - [x] Setup documentation
  - [x] Setup tests
  - [ ] Add x86 support
  - [ ] Add WoW64 support
  - [x] Setup NIM templates
  - [x] Setup C templates
  - [ ] Setup Go? / CPP? / C#? / Rust? / Whatever templates

## License
This project is licensed under the [GPLv3 License](https://www.gnu.org/licenses/quick-guide-gplv3.en.html), for individuals only. If you want to integrate this work in your commercial project please contact me through `0x42en[at]gmail.com`
