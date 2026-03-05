# Tests & Documentation

SysPlant uses **pytest** for testing and **mkdocs** + **mkdocstrings** for documentation generation.

---

## Running Tests

With Poetry (recommended):

```bash
poetry run pytest
```

Or without Poetry:

```bash
python3 -m pytest
```

For verbose output with short tracebacks:

```bash
poetry run pytest tests/ -v --tb=short
```

## Test Coverage

The project currently has **68 tests** covering:

- Abstract base classes
- NIM code generation (all iterators × all methods)
- C code generation (all iterators × all methods)
- Rust code generation (all iterators × all methods)
- Scramble mode for each language
- File output verification

---

## Documentation

This project uses [mkdocs](https://www.mkdocs.org/) with:

- [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) — Material theme
- [mkdocstrings](https://mkdocstrings.github.io/) — Auto-generates API docs from Python docstrings
- [awesome-pages](https://github.com/lukasgeiter/mkdocs-awesome-pages-plugin) — Navigation ordering via `.pages` files

### Writing Docstrings

1. Use **Google-style** docstrings (`Args:`, `Returns:`, `Raises:`).
2. Optionally use [AutoDocString](https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring) in VS Code to scaffold them.

### API Reference

The API reference in `docs/documentation/README.md` uses mkdocstrings `::: module.path` directives.
They automatically render class and method docs from the source code — no manual generation step needed.

### Local Preview

Install doc dependencies and serve locally:

```bash
pip install -r docs/requirements.txt
mkdocs serve
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000).

### Build for Production

```bash
mkdocs build
```

The generated site will be in the `public/` directory.
