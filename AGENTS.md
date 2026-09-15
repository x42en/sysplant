---
owner: x42en
repo: sysplant
language: python
production_branch: main
work_branch: develop
package_manager: poetry
test_framework: pytest
---

# SysPlant Agent Contract

## Branches
- `main`: protected production branch. All releases cut from here.
- `develop`: work branch. All feature work lands here first.

## Environment
- Python >=3.10, <4
- Package manager: Poetry (poetry.lock is authoritative)

## Commands
- Setup: `poetry install --no-interaction`
- Tests: `poetry run pytest --cov=sysplant`
  - Coverage gate: 80% (`--cov-fail-under=80`)
  - `sysplant/mcp_server.py` is excluded from the coverage gate (requires optional `mcp` extra)

## Quality Gates (all must pass)
1. `poetry install --no-interaction` — no dependency resolution errors
2. `poetry run pytest --cov=sysplant` — all tests pass AND coverage >= 80%

## Architecture
- `sysplant/` — library source
- `tests/` — test suite with fixtures
- `example/` — example inputs
- `docs-site/` — documentation site (deployed via docs.yml workflow)

## CI Workflows
- `build.yml` — tests on every push (Python 3.10–3.13 matrix)
- `docs.yml` — builds docs Docker image on docs-site changes to main
- `publish.yml` — PyPI publish on GitHub release

## Engineering Profiles
- python

## Offensive Development Baseline
- Validate at trust boundaries; fail loudly on invalid state
- Strongest practical typing and static analysis available
- No duplicate, dead, or speculative compatibility code
- Files target <=500 lines, hard ceiling 1000
- Preserve explicit error handling and diagnostic context
- No secrets in source, prompts, logs, or artifacts
