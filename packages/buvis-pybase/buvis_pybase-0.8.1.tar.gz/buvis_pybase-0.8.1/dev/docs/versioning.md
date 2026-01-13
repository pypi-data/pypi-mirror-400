# Versioning

Uses [PEP 440](https://packaging.python.org/en/latest/discussions/versioning/) compliant versions.

`bmv` is a wrapper script at `dev/bin/bmv`.

## Format

`MAJOR.MINOR.PATCH[.devN|rcN]`

Examples: `0.5.7`, `0.5.8.dev0`, `0.5.8rc1`

## Direct Release

Default workflow - bumps go straight to final version:

```bash
bmv bump patch   # 0.5.7 → 0.5.8
bmv bump minor   # 0.5.7 → 0.6.0
bmv bump major   # 0.5.7 → 1.0.0
```

## Pre-release Workflow

For staged releases needing dev/rc phases:

```bash
# Start pre-release
bmv bump pre_patch   # 0.5.7 → 0.5.8.dev0
bmv bump pre_minor   # 0.5.7 → 0.6.0.dev0
bmv bump pre_major   # 0.5.7 → 1.0.0.dev0

# Advance stages
bmv bump pre_l       # 0.5.8.dev0 → 0.5.8rc0
bmv bump pre_l       # 0.5.8rc0 → 0.5.8

# Escape to final (skip remaining stages)
bmv bump --new-version "0.5.8"
```

## Tagging

All bumps create `v{version}` tags (configured in `pyproject.toml`).

## CI Behavior

Workflow triggers on `v*` tag push:

1. Checks if tagged commit is on master
2. If on master → builds, publishes to test.pypi.org + pypi.org, creates GitHub release
3. Tags containing `alpha`, `beta`, or `rc` → marked as prerelease on GitHub

## Useful Commands

```bash
bmv show-bump                    # Show available bumps
bmv show current_version         # Current version
bmv bump --dry-run patch         # Preview change
```
