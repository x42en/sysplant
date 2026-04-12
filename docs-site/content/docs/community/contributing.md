---
title: Contributing
description: How to contribute to Sysplant.
---

# Contributing

Contributions to Sysplant are welcome. Please review the [CONTRIBUTING.md](https://github.com/x42en/sysplant/blob/main/CONTRIBUTING.md) in the repository for full guidelines.

## Supported OS

- Debian 12 / 13
- Ubuntu 22.04 / 24.04

## Prerequisites

### Python 3.10+ on Debian/Ubuntu

```bash
apt install python3 python3-pip
```

### Poetry

```bash
# Linux / macOS / WSL
curl -sSL https://install.python-poetry.org | python3 -

# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

## Set up the development environment

```bash
git clone https://github.com/x42en/sysplant.git
cd sysplant
poetry shell
poetry install
```

To also install MCP server dependencies:

```bash
poetry install --with mcp
```

::callout{type="tip"}
If you encounter a `DBusError` during install, set: `export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring`
::

## Code style

This project uses [Black](https://github.com/psf/black). All code must be formatted before opening a PR.

```bash
poetry run black .
```

## Running tests

```bash
poetry run pytest
```

For verbose output:

```bash
poetry run pytest tests/ -v --tb=short
```

The test suite covers abstract base classes, NIM/C/Rust code generation for all iterators × all methods, scramble mode, and file output verification.

The coverage threshold enforced by CI is **80%**.

## Adding a new iterator

New gate iterators belong in `sysplant/templates/` and must be registered in `sysplant/managers/templateManager.py`. See an existing generator (e.g., `CGenerator`) as a reference.

## Adding a new language

Language support requires:
1. A new generator class in `sysplant/templates/`
2. Registration in `templateManager.py`
3. Extension mappings in `LANG_EXT` and `OUTPUT_EXT` in `sysplant/constants/sysplantConstants.py`

## Poetry cheat-sheet

```bash
poetry add <library>             # Add a runtime dependency
poetry add <library> -G dev      # Add a dev dependency
poetry remove <library>          # Remove a dependency
poetry update <library>          # Update a dependency
poetry show                      # List all installed packages
poetry run which python          # Show venv Python path
poetry run python app.py         # Run a script in the venv
poetry config virtualenvs.create false   # Disable venv creation
```

## Publishing to test PyPI

```bash
# Configure the repository once
poetry config repositories.test-pypi https://test.pypi.org/legacy/

# Store your token (from https://test.pypi.org/manage/account/token/)
poetry config pypi-token.test-pypi pypi-YYYYYYYY

# Publish
poetry publish -r test-pypi
```

## Reporting issues

Open an issue at [github.com/x42en/sysplant/issues](https://github.com/x42en/sysplant/issues) with:
- Sysplant version (`sysplant --version`)
- Python version
- The exact command or code that produced the issue
- Expected vs actual behaviour
