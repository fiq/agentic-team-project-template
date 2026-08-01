---
name: runtime-python
description: Specialise Python runtime, package, framework and test conventions; evolvable, acknowledges unknown tools.
---

# Runtime: Python

Detect `pyproject.toml`, uv, Poetry, pip-tools, requirements, pytest, FastAPI,
Flask, Django, LangChain, LangGraph, direct SDK use, Pydantic, SQLAlchemy,
Alembic, Celery, Kafka clients and data or ML shape.

Preserve existing package management. Separate deterministic application logic,
provider contracts and opt-in live model tests.

## Build and tooling

- `pyproject.toml` is the modern canonical manifest; detect the build backend
  (setuptools, hatchling, poetry-core, flit, maturin).
- Detect the package manager from lock files first: `uv.lock`, `poetry.lock`,
  `requirements*.txt` with pip-tools headers, `Pipfile.lock`.
- Respect the existing dependency workflow; do not migrate uv to Poetry (or
  the reverse) without evidence and a recorded decision.
- Nix owns the developer toolchain; do not introduce pyenv, asdf or a
  system-wide `pip install` on NixOS.
- Virtual environments are still used inside a Nix shell for project
  dependencies; detect `.venv` and respect the existing convention.

## Static analysis (see specialise/static-analysis)

Python's analysis ecosystem has consolidated significantly around ruff. The
per-runtime defaults are evolvable.

| Category | Default tool | Notes |
|---|---|---|
| lint | ruff | fast; replaces flake8, isort, pyupgrade and more |
| type_check | mypy or pyright | pick what the project uses; do not run both |
| sast | bandit | security linter; ruff's `S` rules cover much of it |
| dependency_scan | pip-audit | `pip-audit` against the resolved environment |
| complexity | ruff | `C901` and the `mccabe` rules; radon for reporting |
| dast | n/a | only when the project has a running service |

These are starting points, not a closed list. If the project uses a tool not
listed here (e.g. pylint, flake8, vulture, deptry, ty), record it in
`PROJECT_PROFILE.toon.static_analysis` with a `revisit_trigger`.

## Language smells (for review-loop)

Mutable default arguments; bare `except`; broad `except Exception` swallowing
errors; import-time side effects; missing type hints on public boundaries;
`*args/**kwargs` hiding a real interface; god modules; overuse of dicts where a
dataclass fits; blocking calls in async code.

## Testing

- pytest is the dominant framework; unittest is also common in older code.
- Respect the existing test layout (`tests/` alongside the package, or
  `src/`-adjacent) rather than imposing one.
- Fixtures over setup/teardown classes; `pytest.mark.parametrize` for table
  cases.
- Property testing: Hypothesis when invariants matter.
- Snapshot testing: syrupy when output stability matters.
- Real dependencies: Testcontainers for lifecycle-managed integration tests.
- Keep live-model or paid-API tests opt-in behind a marker, never in the
  default run.

## Ecosystem openness

Python's packaging and tooling ecosystem moves quickly. This skill provides
defaults, not a closed list. When encountering a tool or convention not
covered here:

- inspect the project's `pyproject.toml`, `setup.cfg`, `tox.ini`,
  `noxfile.py`, `ruff.toml` and `.python-version` for evidence;
- respect the existing convention;
- record the tool in `PROJECT_PROFILE.toon` if it is material;
- do not impose a tool the project does not already use unless evidence
  justifies it.
