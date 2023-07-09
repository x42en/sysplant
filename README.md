# SysPlant
"Your Syscall Factory" *(feat. Canterlot's Gate)*

![Canterlot's Gate](pictures/canterlot.jpeg)

SysPlant is a small implementation in NIM of the currently known syscall hooking methods. It currently supports following gates:
- Heaven
- Hell
- Halos
- Tartarus

And publish an idea from [MDSEC](https://www.mdsec.co.uk/2022/04/resolving-system-service-numbers-using-the-exception-directory/) that was missing a pony name...  So here it is: **Canterlot's Gate** ! :unicorn: :rainbow:  
*Note: You can further more generate your own combinations using the proper options...*

## Installation
This is a python project that will generate NIM source code (bit weird hu ?! :joy:). So you can use it inside your project as an external module or directly on your device as a tool.

### Python module
If you are using standard pip3 package manager
```sh
pip3 install sysplant
```

If you are more inclined to use virtual environments *(you should!)* this project is based on [Poetry](https://python-poetry.org/) virtual env.
```sh
poetry add sysplant
```

### Single tool
Install the project as you would do for any GitHub project
```sh
git clone xxxxxxxxxx/sysplant.git
cd sysplant
poetry shell
poetry install
./main.py -h
```

## Help
This tool comes with various options that should be self-explanatory using the standard `-h` flag
```sh
$ ./main.py -h
usage: main.py [-h] [--debug | --verbose] [-i {freshy,heaven,hell,halos,tartarus,exceptions}] [-r {basic,random}] [-s {direct,indirect}] [-p {all,donut,common} | -f FUNCTIONS] [-o OUTPUT]

..:: SysPlant - Your Syscall Factory ::..

optional arguments:
  -h, --help            show this help message and exit
  --debug               Display all DEBUG messages upon execution
  --verbose             Display all INFO messages upon execution
  -i {freshy,heaven,hell,halos,tartarus,exceptions}, --iterator {freshy,heaven,hell,halos,tartarus,exceptions}
                        Select syscall iterator (Default: exceptions)
  -r {basic,random}, --resolver {basic,random}
                        Select syscall resolver (Default: random)
  -s {direct,indirect}, --stub {direct,indirect}
                        Select syscall stub (Default: indirect)
  -p {all,donut,common}, --preset {all,donut,common}
                        Preset functions ("all", "donut", "common")
  -f FUNCTIONS, --functions FUNCTIONS
                        Comma-separated functions
  -o OUTPUT, --output OUTPUT
                        Define where to output file (Default print to cli)
```

## ShoutOut
Massive shoutout to these usefull projects that help during this journey, or individuals for their reviews
- [@alice blogpost](https://alice.climent-pommeret.red/posts/direct-syscalls-hells-halos-syswhispers2/)
- [@redops blogpost](https://redops.at/en/blog/direct-syscalls-a-journey-from-high-to-low)
- [@klezvirus](https://github.com/klezVirus/)