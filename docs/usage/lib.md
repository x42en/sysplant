## Using Sysplant as a Python Library
This project has been designed so it can be embedded in your project as a simple external module.

### Installation
If you are using standard pip3 package manager
```bash
pip3 install sysplant
```
If you are more likely to use virtual environments *(you should!)* this project is based on [Poetry](https://python-poetry.org/) virtual env.
```bash
poetry add sysplant
```

### Usage
```python
from sysplant import Sysplant

if __name__ == "__main__":
    # Initialize the class
    bot = Sysplant(
        arch="x64",
        syscall="syscall",
        language="nim"
    )
    # Generate code
    bot.generate(
        iterator="canterlot",
        method="random",
        syscalls="common"
    )
    # Optionally randomize internal names
    bot.scramble()
    # Generate file
    bot.output("/tmp/syscall")
```

### Documentation
A more precise documentation and associated options is available [here](https://x42en.github.io/sysplant/documentation/)
