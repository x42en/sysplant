# AGENTS.md — x42en/sysplant

## Project identity

- Repository: x42en/sysplant
- Type: Python CLI tool for system architecture diagramming (PlantUML generation)
- Production branch: main (protected)
- Work branch: develop
- Package manager: poetry
- Entry point: main.py (sysplant CLI)

## Engineering profiles

- python

## Branch model

- main: production branch, protected. No direct pushes. Release commits land here.
- develop: active development branch. All work PRs target develop.

## Quality gates

Run all of these before requesting merge. A change is not complete while any gate is red.

- Type checking: mypy
- Linting: ruff
- Tests: pytest
- Formatting: black

Prefer the commands that CI actually executes. If the repository has a CI workflow, mirror those exact invocations.

## Development workflow

1. Branch from develop.
2. Implement change with focused responsibilities.
3. Add or update tests for behavior changes.
4. Run all quality gates locally.
5. Open a PR targeting develop with a clear title and description.
6. State the active engineering profiles and exact gates executed in the PR description.

## Code standards

### File size

- Target: 500 lines or fewer per file.
- Hard ceiling: 1000 lines unless repository rules are stricter or a documented exception exists.

### Error handling

- Fail loudly and early. Do not mask invalid state.
- Preserve explicit error handling and diagnostic context.
- Do not convert failures into silent success or fallback behavior.
- Validate untrusted values at trust boundaries.

### Safety

- Do not weaken type checking, linting, or tests merely to land a change.
- Never introduce dead code, commented-out code, or speculative compatibility shims.
- Keep secrets out of source, logs, patches, artifacts, and test output.

### Exception documentation

An exception to any rule must be documented in the same change with:
- Reason
- Risk/impact
- Mitigation
- Rejected alternatives
- Removal or revisit condition

Compatibility work is an exception, not a default.

## Project structure

- sysplant/ — Python package source
- tests/ — test suite
- main.py — CLI entry point
- pyproject.toml — project configuration, dependencies
- poetry.lock — dependency lockfile
- docs-site/ — documentation site
- example/ — example diagrams

## Delivery gates

Before requesting merge, verify:

1. Repository-specific rules from AGENTS.md and nested context have been followed.
2. Deterministic compile/typecheck/lint/static-analysis/test/build gates have been run.
3. Tests cover behavior changes.
4. Documentation and changelog are updated for user-visible changes.
5. All required local gates that can be reproduced have been executed.
6. Required CI gates are green.
7. Breaking behavior has explicit versioning/migration treatment consistent with the project.

## Historical context files consulted

- README.md
- pyproject.toml
- main.py
- CONTRIBUTING.md (if present)
