---
title: Contributing
description: How to contribute to Sysplant.
---

# Contributing

Contributions to Sysplant are welcome. Please review the [CONTRIBUTING.md](https://github.com/x42en/sysplant/blob/main/CONTRIBUTING.md) in the repository for full guidelines.

## Quick checklist

- Fork the repository and create a feature branch.
- Follow existing code style — Python 3.10+, type hints where practical.
- Add or update tests in `tests/` for any changed behaviour.
- Run tests before opening a PR:

```bash
poetry run pytest tests/
```

## Adding a new iterator

New gate iterators belong in `sysplant/templates/` and must be registered in `sysplant/managers/templateManager.py`. See an existing generator (e.g., `CGenerator`) as a reference.

## Adding a new language

Language support requires:
1. A new generator class in `sysplant/templates/`
2. Registration in `templateManager.py`
3. Extension mappings in `LANG_EXT` and `OUTPUT_EXT` in `sysplant/constants/sysplantConstants.py`

## Reporting issues

Open an issue at [github.com/x42en/sysplant/issues](https://github.com/x42en/sysplant/issues) with:
- Sysplant version (`sysplant --version`)
- Python version
- The exact command or code that produced the issue
- Expected vs actual behaviour
