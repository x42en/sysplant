# Contributor Installation

You want to contribute to this project? :tada:  
You are more than welcome! Please read the instructions below before getting started.

---

## Supported OS

- Debian 13 / 12
- Ubuntu 24.04 / 22.04

## Setup a Virtual Environment

A Python virtual environment is **strongly** recommended to avoid dependency conflicts. This project uses [Poetry](https://python-poetry.org/) for development.

## Code Style

This project follows [Black code rules](code_rules.md). Please respect this convention.

If you are using VS Code with Poetry, some Black exclusions are defined in `pyproject.toml`. To add more, see the [pydocstyle error codes](http://www.pydocstyle.org/en/6.2.2/error_codes.html).

## Documentation Tooling

The documentation stack is:

- **[mkdocstrings](https://mkdocstrings.github.io/)** — Auto-generates API docs from Python docstrings (Google-style)
- **[mkdocs-material](https://squidfunk.github.io/mkdocs-material/)** — Material theme for mkdocs
- **[awesome-pages](https://github.com/lukasgeiter/mkdocs-awesome-pages-plugin)** — Navigation ordering via `.pages` files

See [Tests & Documentation](tests.md) for the full workflow.

## Install the Project

Once your [prerequisites](prerequise.md) are met:

```bash
cd /path/to/sysplant
poetry shell
poetry install
```

To also install MCP server dependencies for development:

```bash
poetry install --with mcp
```

!!! tip
If you encounter a `DBusError` during install, set:
`bash
    export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
    `

## Test Publication

### Configure test PyPI

```bash
poetry config repositories.test-pypi https://test.pypi.org/legacy/
```

### Store your token

Get a token from [https://test.pypi.org/manage/account/token/](https://test.pypi.org/manage/account/token/) then:

```bash
poetry config pypi-token.test-pypi pypi-YYYYYYYY
```

### Publish

```bash
poetry publish -r test-pypi
```
