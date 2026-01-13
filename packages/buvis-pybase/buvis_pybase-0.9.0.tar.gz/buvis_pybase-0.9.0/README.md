# buvis-pybase

Foundation library for BUVIS Python projects. Provides configuration management, filesystem utilities, adapters for external tools, and string manipulation.

## Install

```bash
pip install buvis-pybase
```

## Features

- **Configuration** - Pydantic settings with Click helpers (`buvis_options`, `get_settings`)
- **Adapters** - Shell, UV, Poetry, JIRA, Console wrappers
- **Filesystem** - Cross-platform file metadata, directory operations
- **Formatting** - String slugify, abbreviations, case conversion

## Usage

```python
import click
from buvis.pybase.configuration import buvis_options, get_settings, GlobalSettings
from buvis.pybase.adapters import ShellAdapter, ConsoleAdapter
from buvis.pybase.filesystem import DirTree
from buvis.pybase.formatting import StringOperator

# Config via Click (adds --debug/--log-level/--config-dir/--config)
@click.command()
@buvis_options  # Use settings_class=CustomSettings for tool-specific models
@click.pass_context
def main(ctx: click.Context) -> None:
    settings = get_settings(ctx)  # GlobalSettings by default
    click.echo(f"Debug: {settings.debug}")

# Shell commands
shell = ShellAdapter()
stderr, stdout = shell.exe("ls -la")

# Console output
console = ConsoleAdapter()
console.success("Done")

# Filesystem
DirTree.remove_empty_directories("/path/to/clean")

# Strings
slug = StringOperator.slugify("Hello World!")  # "hello-world"
```

## Development

```bash
uv sync --all-groups                        # install deps
pre-commit install --hook-type pre-commit --hook-type post-commit  # setup hooks
uv run pytest                               # run tests
```

## Release

```bash
./dev/bin/bmv bump patch  # bumps version, tags, pushes
```

Tags trigger PyPI publish via GitHub Actions.

## License

MIT
