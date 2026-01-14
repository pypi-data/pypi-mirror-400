# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Abilian DevTools (ADT) is a curated collection of Python development tools packaged as a single dependency. The project serves two purposes:
1. A dependency metapackage bundling 40+ development tools (formatters, linters, type checkers, security auditors)
2. A CLI tool (`adt`) that provides opinionated workflows for common development tasks

## Architecture

### CLI Framework
- Built on `cleez` (a command framework similar to Click)
- Entry point: `src/abilian_devtools/cli.py:main()`
- Commands auto-discovered via `cli.scan("abilian_devtools.commands")`
- Each command is a class inheriting from `cleez.command.Command` in `src/abilian_devtools/commands/`

### Command Pattern
Commands follow this structure:
- `name`: CLI command name
- `arguments`: List of `Argument` objects for CLI args
- `run()`: Main execution method
- Utilities in `_util.py` handle common patterns (e.g., `get_targets()` defaults to `src` and `tests` dirs)

### Shell Execution
All shell commands go through `src/abilian_devtools/shell.py:run()` which wraps subprocess execution.

## Development Commands

### Setup
```bash
# Install dependencies with uv
uv sync

# Install pre-commit hooks
pre-commit install
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_cli.py

# Run tests without random order
pytest -x -p no:randomly

# Via make
make test

# Via nox (tests across Python 3.10-3.13)
nox -s pytest
```

### Linting and Formatting
```bash
# Run linters
adt check src tests
# Or: make lint

# Format code
adt format src tests
# Or: make format

# The check command runs:
# - ruff check (with etc/ruff.toml if exists)
# - vulture (dead code detection)
```

### Type Checking
```bash
# Run type checker
adt typecheck src
# Or directly: ty check src
```

### Version Bumping
```bash
# Bump patch version, commit, and tag
adt bump-version patch

# Other options: major, minor, daily
adt bump-version minor
```

### Security Audit
```bash
adt audit
# Runs: pip-audit, bandit, reuse lint
```

### Cleanup
```bash
adt clean
# Or: make clean
```

### Publishing
```bash
# Update dependencies
make update-deps  # Uses uv sync -U

# Build and publish
make publish  # Builds with uv and uploads with twine
```

## Configuration Files

- `pyproject.toml`: Project metadata, dependencies, tool configs (bandit, deptry, scriv)
- `ruff.toml`: Ruff linter and formatter configuration (select ALL rules, then ignore specific ones)
- `noxfile.py`: Multi-Python testing (3.10-3.13)
- `Makefile`: Convenience targets wrapping adt commands

## CLI Commands

- `adt check` - Run ruff linter and vulture
- `adt typecheck` - Run ty type checker
- `adt format` - Format code with ruff
- `adt test` - Run pytest
- `adt audit` - Run security audits (pip-audit, bandit, reuse)
- `adt bump-version` - Bump version in pyproject.toml
- `adt clean` - Cleanup build artifacts and caches
- `adt cruft` - Check for standard project files

## Key Patterns

### Adding New Commands
1. Create `src/abilian_devtools/commands/yourcommand.py`
2. Define a class inheriting from `Command` with `name` and `run()` method
3. Auto-discovered via CLI scanner (no registration needed)

### Target Resolution
Commands that operate on files/dirs use `get_targets(args)` which:
- Returns args if provided (after validating existence)
- Defaults to `["src", "tests"]` if both exist
- Allows commands to work with or without explicit paths

## Testing

Tests are minimal but focus on:
- CLI help output (`test_invoke_help.py`)
- Basic command execution (`test_cli.py`)
- Tests run on source code AND test directory (`pytest tests src`)

---

## Coding Guidelines

### Package Management
- **ONLY use `uv`, NEVER `pip`**: `uv add package`, `uv run tool`
- **FORBIDDEN:** `uv pip install`, `@latest` syntax

### Code Quality
- Type hints required for all public functions
- Public APIs must have docstrings
- Line length: 88 chars maximum (Ruff default)
- Start modules with main functions/classes (top-down organization)

### Code Style
- `snake_case` for functions/variables
- `PascalCase` for classes
- `UPPER_SNAKE_CASE` for constants
- Use f-strings for formatting (but not for logging)
- Early returns to avoid deep nesting

### Data Structures
- **Prefer dataclasses over dicts/regular classes** for data containers
- Use `@dataclass(frozen=True)` for immutable data (configs, DTOs, value objects)
- Add `slots=True` for frequently instantiated objects (Python 3.10+)

### Design Principles

**The 4 Rules of Simple Design (in priority order):**
1. **Passes all tests** - Code correctness first
2. **Reveals intention** - Clear naming, small functions
3. **No duplication** - DRY, but avoid wrong abstractions
4. **Fewest elements** - YAGNI, remove dead code

**Architecture:**
- **Functional Core / Imperative Shell** - Isolate side effects (I/O, state changes) at edges, keep core logic pure
- **Nouns and Verbs** - Classes hold state, functions perform operations
- Prefer composition over inheritance
- Write a class only when necessary (stateful resources, naming behavior, reusable components)

### Testing Philosophy
- **AAA pattern**: Arrange, Act, Assert
- **No mocks, prefer stubs** - Verify state, not behavior
- **Async testing**: Use `anyio`, not `asyncio`
- Tests must be isolated and deterministic
- New features require tests; bug fixes require regression tests

### Error Messages
Write clear, actionable error messages:
```
[Component] can't [action], error [details]: [plain language], [next action]
```
Example: `Database can't execute query, error timeout: connection timed out after 30s, retrying`

### Commit Messages
- Never mention `co-authored-by` or AI tools
- Keep messages concise and descriptive
