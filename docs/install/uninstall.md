# Uninstall

To remove SysPlant, follow the procedure matching your original installation method.

## Installed as a pip dependency

```bash
pip3 uninstall sysplant
```

## Installed as a standalone tool

```bash
rm -rf /path/to/sysplant
```

## Installed with Poetry

Simply delete the project directory — Poetry's virtual environment lives inside the project (or in Poetry's cache):

```bash
# Remove the virtual environment
cd /path/to/sysplant
poetry env remove --all

# Delete the project
rm -rf /path/to/sysplant
```
