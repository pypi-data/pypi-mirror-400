# CLAUDE.md

This file provides context for Claude Code when working on this project.

## Project Overview

**releasio** is an automated release tool for Python projects, inspired by [release-plz](https://github.com/MarcoIeni/release-plz). It analyzes conventional commits to automatically determine version bumps, generate changelogs, and publish to PyPI.

### Configuration File Support

releasio supports multiple configuration file formats with a precedence order:

1. `.releasio.toml` (dotfile, highest precedence)
2. `releasio.toml` (visible file)
3. `pyproject.toml` under `[tool.releasio]` section (lowest precedence, backward compatible)

**Key differences:**

- Custom config files (`.releasio.toml`, `releasio.toml`) use **top-level keys** (no `[tool.releasio]` wrapper)
- `pyproject.toml` configs use the `[tool.releasio]` wrapper (existing behavior)
- Custom configs are searched in the current directory only
- `pyproject.toml` is always required for project metadata (name, version), even when using custom config files
- The configuration loader auto-discovers which file to use based on precedence

## Tech Stack

- **Python 3.11+** - Modern Python with full type annotations
- **uv** - Fast Python package manager (preferred over pip/poetry)
- **Pydantic v2** - Configuration validation and models
- **Typer** - CLI framework with rich output
- **git-cliff** - Changelog generation (with native fallback)
- **pytest** - Testing framework

## Quick Commands

```bash
# Install dependencies
uv sync --all-extras

# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/releasio --cov-report=term-missing

# Lint and format
uv run ruff check src/ tests/
uv run ruff format src/ tests/

# Type checking
uv run mypy src/

# Run the CLI
uv run releasio --help
```

## Code Conventions

### Python Style

Follow modern, idiomatic Python practices:

```python
# Use type annotations everywhere
def calculate_bump(commits: list[ParsedCommit], config: CommitsConfig) -> BumpType:
    ...

# Use dataclasses or Pydantic models for data structures
@dataclass(frozen=True, slots=True)
class ParsedCommit:
    commit: Commit
    commit_type: str | None
    description: str
    is_breaking: bool

# Use Path objects, not strings, for file paths
from pathlib import Path
config_path: Path = repo_path / "pyproject.toml"

# Use f-strings for formatting
message = f"Bumping version from {old_version} to {new_version}"

# Use walrus operator where it improves readability
if (match := pattern.match(subject)):
    return match.group("type")

# Prefer list/dict comprehensions over loops
types = [c.commit_type for c in commits if c.is_conventional]

# Use contextlib.suppress for expected exceptions
with contextlib.suppress(IndexError):
    scope = match.group(parser.scope_group)
```

### Clean Code Principles

1. **Single Responsibility**: Each function/class does one thing well
2. **DRY**: Extract common patterns into reusable functions
3. **KISS**: Prefer simple, obvious solutions over clever ones
4. **Early Returns**: Fail fast, return early to reduce nesting

```python
# Good: Early return
def get_version(path: Path) -> Version | None:
    if not path.exists():
        return None
    content = path.read_text()
    if not content.strip():
        return None
    return parse_version(content)

# Avoid: Deep nesting
def get_version(path: Path) -> Version | None:
    if path.exists():
        content = path.read_text()
        if content.strip():
            return parse_version(content)
    return None
```

### Error Handling

Use custom exceptions with meaningful messages:

```python
# Define specific exceptions
class GitCliffError(ReleaseError):
    """Raised when git-cliff command fails."""
    def __init__(self, message: str, stderr: str | None = None):
        super().__init__(message)
        self.stderr = stderr

# Raise with context
raise ChangelogError(
    f"Failed to generate changelog for {version}: {e}",
) from e

# Handle expected errors gracefully
try:
    result = subprocess.run(args, check=True, capture_output=True, text=True)
except subprocess.CalledProcessError as e:
    if "no commits" in e.stderr.lower():
        return BumpType.NONE  # Expected case
    raise GitCliffError(f"git-cliff failed: {e.returncode}", stderr=e.stderr) from e
```

### Type Annotations

Always use type annotations. Use `TYPE_CHECKING` for import-only types:

```python
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from releasio.config.models import ReleasePyConfig
    from releasio.vcs.git import GitRepository

def generate_changelog(
    repo: GitRepository,
    version: Version,
    config: ReleasePyConfig,
    *,
    unreleased_only: bool = True,
) -> str:
    ...
```

### Configuration Models

Use Pydantic v2 with `Field` for documentation:

```python
class ChangelogConfig(BaseModel):
    """Configuration for changelog generation."""

    enabled: bool = Field(
        default=True,
        description="Whether to generate changelog",
    )
    path: Path = Field(
        default=Path("CHANGELOG.md"),
        description="Path to the changelog file",
    )

    model_config = {"extra": "forbid"}  # Catch typos in config
```

## Architecture

```
src/releasio/
├── cli/              # Typer CLI commands
│   ├── main.py       # Entry point and app setup
│   ├── check.py      # releasio check command
│   ├── update.py     # releasio update command
│   ├── release.py    # releasio release command
│   └── release_pr.py # releasio release-pr command
├── config/           # Configuration handling
│   ├── loader.py     # Load config from pyproject.toml
│   └── models.py     # Pydantic configuration models
├── core/             # Core business logic
│   ├── changelog.py  # Changelog generation
│   ├── commits.py    # Commit parsing
│   ├── version.py    # Version handling and bumping
│   └── version_files.py # Version file detection/updates
├── vcs/              # Version control
│   └── git.py        # Git operations
├── github/           # GitHub integration
│   └── client.py     # GitHub API client
└── exceptions.py     # Custom exceptions
```

### Key Design Decisions

1. **Immutable Data**: Use `frozen=True` dataclasses for commit/version data
2. **Dependency Injection**: Pass dependencies (repo, config) to functions
3. **Separation of Concerns**: CLI handles I/O, core handles logic
4. **Fail-Safe Defaults**: All config has sensible defaults for zero-config usage

## Testing Guidelines

### Test Structure

```
tests/
├── unit/           # Fast, isolated tests
│   ├── test_version.py
│   ├── test_commits.py
│   └── test_changelog.py
├── integration/    # Tests with real Git repos
│   ├── test_cli.py
│   ├── test_update.py
│   └── test_release.py
└── conftest.py     # Shared fixtures
```

### Writing Tests

Always add tests when making changes. Aim for high coverage:

```python
class TestParseCommit:
    """Tests for commit parsing."""

    def test_parse_conventional_feat(self):
        """Parse a conventional feat commit."""
        commit = make_commit("feat: add new feature")
        result = ParsedCommit.from_commit(commit, breaking_pattern="BREAKING")

        assert result.commit_type == "feat"
        assert result.description == "add new feature"
        assert result.is_conventional is True

    def test_parse_with_scope(self):
        """Parse commit with scope."""
        commit = make_commit("fix(api): handle null response")
        result = ParsedCommit.from_commit(commit, breaking_pattern="BREAKING")

        assert result.scope == "api"
        assert result.commit_type == "fix"

    def test_parse_breaking_with_exclamation(self):
        """Detect breaking change from ! indicator."""
        commit = make_commit("feat!: redesign API")
        result = ParsedCommit.from_commit(commit, breaking_pattern="BREAKING")

        assert result.is_breaking is True

    @pytest.mark.parametrize("message,expected_type", [
        ("feat: add feature", "feat"),
        ("fix: fix bug", "fix"),
        ("docs: update readme", "docs"),
        ("chore: update deps", "chore"),
    ])
    def test_parse_various_types(self, message: str, expected_type: str):
        """Parse various commit types."""
        commit = make_commit(message)
        result = ParsedCommit.from_commit(commit, breaking_pattern="BREAKING")

        assert result.commit_type == expected_type
```

### Test Fixtures

Use pytest fixtures for common setup:

```python
@pytest.fixture
def git_repo(tmp_path: Path) -> GitRepository:
    """Create a temporary Git repository."""
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmp_path)
    return GitRepository(tmp_path)

@pytest.fixture
def sample_config() -> ReleasePyConfig:
    """Create a sample configuration."""
    return ReleasePyConfig(
        default_branch="main",
        changelog=ChangelogConfig(enabled=True),
    )
```

### Mocking External Dependencies

Mock external calls (Git, GitHub API, subprocess):

```python
def test_generate_changelog_git_cliff_unavailable(self, mock_repo):
    """Fall back to native generation when git-cliff unavailable."""
    with patch("shutil.which", return_value=None):
        with patch("releasio.core.changelog.generate_native_changelog") as mock_native:
            mock_native.return_value = "## [1.0.0]\n\n- Feature"

            result = generate_changelog_with_fallback(mock_repo, Version(1, 0, 0), config)

            mock_native.assert_called_once()
```

## Common Patterns

### CLI Commands

```python
@app.command()
def update(
    path: Annotated[Path, typer.Argument(help="Project path")] = Path("."),
    execute: Annotated[bool, typer.Option("--execute", help="Apply changes")] = False,
    version: Annotated[str | None, typer.Option(help="Force version")] = None,
) -> None:
    """Update version and changelog."""
    config = load_config(path)
    repo = GitRepository(path)

    # Dry-run by default
    if not execute:
        console.print("[yellow]Dry run mode. Use --execute to apply changes.[/]")
        return

    # Perform update...
```

### Working with Git

```python
def get_commits_since_tag(self, tag: str | None = None) -> list[Commit]:
    """Get commits since the given tag."""
    if tag:
        range_spec = f"{tag}..HEAD"
    else:
        range_spec = "HEAD"

    result = self._run_git(
        "log",
        "--format=%H%x00%s%x00%an%x00%ae%x00%aI%x00%b%x1e",
        range_spec,
    )
    return self._parse_log_output(result.stdout)
```

### Version Bumping

```python
def bump(self, bump_type: BumpType, *, pre_release: str | None = None) -> Version:
    """Return a new version with the specified bump applied."""
    match bump_type:
        case BumpType.MAJOR:
            return Version(self.major + 1, 0, 0, pre_release)
        case BumpType.MINOR:
            return Version(self.major, self.minor + 1, 0, pre_release)
        case BumpType.PATCH:
            return Version(self.major, self.minor, self.patch + 1, pre_release)
        case BumpType.NONE:
            return self
```

## Pre-commit Checks

Before committing, ensure:

1. `uv run ruff check src/ tests/` passes
2. `uv run ruff format --check src/ tests/` passes
3. `uv run mypy src/` passes
4. `uv run pytest` passes

## Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add custom commit parser support
fix(changelog): handle empty commit list
docs: update README with new features
refactor(core): simplify version parsing logic
test: add tests for Gitmoji parsing
chore: update dependencies
```

## Key Files

- `pyproject.toml` - Project configuration and dependencies
- `src/releasio/config/models.py` - All configuration options
- `src/releasio/core/version.py` - Version parsing and bumping
- `src/releasio/core/commits.py` - Commit parsing logic
- `src/releasio/core/changelog.py` - Changelog generation
