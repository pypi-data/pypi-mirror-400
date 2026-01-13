# Versioning and Releases

This project uses [Semantic Versioning](https://semver.org/) and
[Conventional Commits](https://www.conventionalcommits.org/) to automatically
determine version numbers and generate changelogs.

## How It Works (The Big Picture)

```
You write code → You commit with conventional message → You merge PR to master
                                                                ↓
                                            (nothing happens automatically)
                                                                ↓
                            When ready → Trigger release manually via GitHub Actions
                                                                ↓
                                    Tool reads your commits → Decides version bump
                                                                ↓
                                        Creates tag, changelog, publishes to PyPI
```

**Key point**: Merging to master does NOT automatically release. You control when
releases happen by manually triggering the workflow.

## Version Format

`MAJOR.MINOR.PATCH` (e.g., `1.2.3`)

- **MAJOR**: Breaking changes (rare, be careful)
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes

Pre-releases add a suffix: `1.2.3.dev5` (development/testing version)

## Commit Messages (This Is Important!)

Your commit messages determine the next version. Use this format:

```
type(scope): description
```

### Types That Affect Version

| Type | Version Bump | Example |
|------|--------------|---------|
| `feat` | MINOR (0.1.0 → 0.2.0) | `feat(api): add user authentication` |
| `fix` | PATCH (0.1.0 → 0.1.1) | `fix(parser): handle empty input` |
| `perf` | PATCH | `perf(db): optimize query performance` |

### Types That DON'T Bump Version

These are valid but won't trigger a release on their own:

- `docs`: Documentation changes
- `style`: Formatting, whitespace
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes
- `build`: Build system changes

### Breaking Changes

Add `!` before the colon for breaking changes (bumps MAJOR version):

```
feat!: remove deprecated API endpoints
fix!: change return type of parse()
```

Or add a footer:

```
feat(api): redesign authentication

BREAKING CHANGE: The auth token format has changed
```

## How To Release

### Step 1: Make Sure Your Code Is Ready

1. All PRs merged to `master`
2. Tests passing
3. You've reviewed the commits since last release

### Step 2: Go to GitHub Actions

1. Go to repository → Actions tab
2. Click "Release" workflow in the left sidebar
3. Click "Run workflow" button (right side)

### Step 3: Choose Release Type

- **prerelease**: Creates a `.devN` version, publishes to test.pypi.org only
  - Use this to test the package before real release
  - Safe to run multiple times
  - Does NOT create a git tag

- **release**: Creates the actual version, publishes everywhere
  - Bumps version based on commits
  - Creates git tag
  - Publishes to test.pypi.org AND pypi.org
  - Creates GitHub Release with changelog

### Step 4: Wait and Verify

The workflow will:
1. Run tests
2. Calculate next version from commits
3. Build package
4. Publish to PyPI(s)
5. Create GitHub release (for full releases)

## Example Workflow

```bash
# Day 1: You fix a bug
git commit -m "fix(parser): handle unicode correctly"

# Day 2: You add a feature
git commit -m "feat(cli): add --verbose flag"

# Day 3: Ready to release
# Go to GitHub Actions → Release → Run workflow → "release"
# Tool sees: 1 feat + 1 fix → bumps MINOR version
# 0.8.1 → 0.9.0
```

## Local Commands (Optional)

You can preview what would happen without releasing:

```bash
# See what version would be created
uv run semantic-release version --print --noop

# See the changelog that would be generated
uv run semantic-release changelog --noop
```

## FAQ

### Q: I merged my PR but nothing was released?

That's correct! Releases are manual. Go to GitHub Actions and trigger the
Release workflow when you're ready.

### Q: My commits don't follow conventional format, what happens?

They'll be ignored for version calculation. If ALL commits since last release
are non-conventional (like `chore:`, `docs:`), the release will fail with
"no releasable commits found."

### Q: Can I release from a feature branch?

No. Releases only work from `master`. Merge your feature branch first.

### Q: What if I want to test my package before real release?

Use the "prerelease" option. It publishes to test.pypi.org with a `.devN`
suffix. Install it with:

```bash
pip install --index-url https://test.pypi.org/simple/ buvis-pybase==0.9.0.dev3
```

### Q: How do I see what changed since last release?

```bash
# See commits since last tag
git log $(git describe --tags --abbrev=0)..HEAD --oneline
```

### Q: I made a mistake in my commit message, can I fix it?

Before pushing: `git commit --amend`

After pushing: You can't change history, but your next commit can still trigger
the correct version bump.

## Changelog

The changelog (`CHANGELOG.md`) is auto-generated from commit messages. Only
`feat`, `fix`, and `perf` commits appear in it. Other types are filtered out
to keep it readable.

## Configuration

All settings are in `pyproject.toml` under `[tool.semantic_release]`. The key
settings:

- `tag_format`: How tags are named (`v{version}` → `v1.2.3`)
- `commit_parser_options`: Which commit types trigger which bumps
- `changelog.exclude_commit_patterns`: What to hide from changelog
