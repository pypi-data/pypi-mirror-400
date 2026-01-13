# CLAUDE.md

Foundation library for BUVIS Python projects. Provides configuration, filesystem utils, adapters for external tools, and string manipulation.

## Quick Start

```bash
uv sync --all-groups                        # install deps
pre-commit install --hook-type pre-commit --hook-type post-commit  # setup hooks
uv run pytest                               # run tests
./dev/bin/refresh-docs                      # rebuild docs (strict)
# release: trigger via GitHub Actions → Release workflow
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
- **No unused imports/variables**: don't add `noqa: F401` or `noqa: F841` - either use the import/variable or remove it
- If a test creates an object just for side effects (e.g., testing `__init__`), add an assertion to use it: `assert issubclass(Foo, Base)`

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

Releases via GitHub Actions (manual trigger):
1. Go to Actions → Release workflow → Run workflow
2. Choose `prerelease` (test.pypi only) or `release` (both pypis + GitHub release)

Version determined from conventional commits (`feat:` → minor, `fix:` → patch).

Local preview:
```bash
uv run semantic-release version --print --noop  # see next version
```

See `dev/docs/versioning.md` for details.
