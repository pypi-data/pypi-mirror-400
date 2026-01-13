# CLAUDE.md

Foundation library for BUVIS Python projects. Provides configuration, filesystem utils, adapters for external tools, and string manipulation.

## Quick Start

```bash
uv sync --all-groups                        # install deps
pre-commit install --hook-type pre-commit --hook-type post-commit  # setup hooks
uv run pytest                               # run tests
./dev/bin/refresh-docs                      # rebuild docs (strict)
./dev/bin/bmv bump patch                    # release (tests run automatically)
```

## Architecture

```
src/buvis/pybase/
├── configuration/   # YAML config, pydantic-settings based
├── adapters/        # Shell, UV, Poetry, JIRA, Console wrappers
├── filesystem/      # DirTree utils, FileMetadataReader
├── formatting/      # StringOperator (slugify, abbreviations, case)
└── command/         # BuvisCommand base class
```

**Key patterns:**
- **Adapters**: wrap external tools (subprocess, APIs). Return `(stderr, stdout)` tuples
- **Static utility classes**: no instance state (DirTree, StringOperator)
- **Configuration**: use Click decorators (`@buvis_options`) and `get_settings()` to resolve typed settings classes

## Code Conventions

**Type hints** - modern style, no `Optional`:
```python
from __future__ import annotations
def foo(path: Path | None = None) -> list[str]: ...
```

**Imports**:
- Explicit `__all__` in `__init__.py`
- `TYPE_CHECKING` guards for type-only imports
- Platform-specific conditional imports in adapters

**Docstrings**: Google format

## Testing

- pytest + pytest-mock
- Tests in `tests/` mirror `src/` structure
- Mock subprocess calls heavily
- Class-based test organization

```python
@pytest.fixture
def shell_adapter() -> ShellAdapter:
    return ShellAdapter()

class TestShellAdapter:
    def test_exe_returns_tuple(self, shell_adapter): ...
```

## Adding New Adapters

1. Create `src/buvis/pybase/adapters/{name}/{name}.py`
2. Follow existing pattern:
   ```python
   class FooAdapter:
       def __init__(self) -> None:
           self.logger = logging.getLogger(__name__)

       def some_operation(self, arg: str) -> tuple[str, str]:
           # Return (stderr, stdout) for shell ops
           ...
   ```
3. Export in `adapters/__init__.py`:
   ```python
   from .foo.foo import FooAdapter
   __all__.append("FooAdapter")
   ```
4. Add tests in `tests/adapters/test_foo_adapter.py`

## Commit Messages

Conventional commits format: `<type>(<scope>): <description>`

| Type     | When                                        |
|----------|---------------------------------------------|
| fix      | Bug fix                                     |
| feat     | New or changed feature                      |
| perf     | Performance improvement                     |
| refactor | Code restructuring, no behavior change      |
| style    | Formatting only                             |
| test     | Tests added/corrected                       |
| docs     | Documentation only                          |
| build    | Build tools, dependencies, versions         |
| ops      | DevOps, infrastructure                      |
| chore    | Anything else                               |

Rules: imperative present tense, no capital, no period, `!` before `:` for breaking changes.

## Release

Tags trigger PyPI publish via GitHub Actions:
```bash
./dev/bin/bmv bump patch      # 0.7.3 → 0.7.4
./dev/bin/bmv bump pre_patch  # → 0.7.4.dev0 (Test PyPI only)
```

Pre-commit runs pytest before version bump. CI verifies tag is on master.
