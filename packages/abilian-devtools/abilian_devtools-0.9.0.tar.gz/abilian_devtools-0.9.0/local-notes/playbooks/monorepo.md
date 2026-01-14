# Python Monorepo with uv Workspaces

**Section:** Generic Python | **See Also:** [coding-guidelines.md](coding-guidelines.md), [testing.md](testing.md)

This playbook describes how to set up and manage a Python monorepo using **uv workspaces**. This pattern works well for 2-3 packages up to dozens, with a single lockfile keeping everything in sync.

---

## When to Use a Monorepo

**Good candidates:**
- Multiple related packages sharing code (core, api, cli, plugins)
- Projects where packages evolve together
- Teams wanting unified tooling and dependency management

**Consider alternatives when:**
- Packages have completely independent lifecycles
- Different teams own different packages with different release schedules
- Packages have conflicting dependency requirements

---

## Directory Structure

### Standard Layout

```
my-project/
├── pyproject.toml          # Root workspace configuration
├── uv.lock                 # Single lockfile for entire workspace
├── packages/
│   ├── myproject-core/     # Core package
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   └── myproject_core/
│   │   │       └── __init__.py
│   │   └── tests/
│   ├── myproject-api/      # API package (depends on core)
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   └── myproject_api/
│   │   │       └── __init__.py
│   │   └── tests/
│   └── myproject-cli/      # CLI package
│       └── ...
├── tests/                  # Cross-package integration tests
└── .venv/                  # Shared virtual environment
```

### Namespace Package Layout (PEP 420)

Use this when you want unified imports like `from myproject.domain import User`:

```
my-project/
├── pyproject.toml
├── uv.lock
├── packages/
│   ├── myproject-core/
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   └── myproject/      # NO __init__.py here!
│   │   │       ├── domain/
│   │   │       │   ├── __init__.py
│   │   │       │   └── models.py
│   │   │       └── services/
│   │   │           └── __init__.py
│   │   └── tests/
│   └── myproject-api/
│       ├── pyproject.toml
│       ├── src/
│       │   └── myproject/      # NO __init__.py here either!
│       │       └── api/
│       │           ├── __init__.py
│       │           └── routes.py
│       └── tests/
└── tests/
```

**Critical rule for namespace packages:** The shared namespace directory (`myproject/`) must NOT have `__init__.py`. Subdirectories (`domain/`, `api/`) should have `__init__.py`.

---

## Configuration

### Root pyproject.toml

```toml
[project]
name = "my-project"
version = "1.0.0"
requires-python = ">=3.12"

# List workspace packages as dependencies
dependencies = [
    "myproject-core",
    "myproject-api",
]

# Dev dependencies in dependency-groups (not extras)
[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.8",
    "mypy>=1.0",
]
doc = [
    "mkdocs",
    "mkdocs-material",
]

# UV WORKSPACE CONFIGURATION
[tool.uv]
package = false  # Root is not a package itself

[tool.uv.workspace]
members = ["packages/*"]

[tool.uv.sources]
myproject-core = { workspace = true }
myproject-api = { workspace = true }

[build-system]
requires = ["uv-build>=0.8.4,<0.9.0"]
build-backend = "uv_build"

# Shared tool configuration
[tool.pytest.ini_options]
addopts = "-ra --import-mode=importlib"
testpaths = [
    "packages/myproject-core/tests",
    "packages/myproject-api/tests",
    "tests",
]
markers = [
    "slow: marks tests as slow",
    "e2e: end-to-end tests",
]

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]
```

**Key settings:**
- `package = false` - Root is a virtual package (not installable)
- `members = ["packages/*"]` - Glob pattern to discover workspace packages
- `workspace = true` - Resolve from workspace, not PyPI

### Package pyproject.toml

#### Core package (no internal dependencies)

```toml
# packages/myproject-core/pyproject.toml
[project]
name = "myproject-core"
version = "1.0.0"
requires-python = ">=3.12"
dependencies = [
    "pydantic>=2.0",
    "sqlalchemy>=2.0",
]

[build-system]
requires = ["uv-build>=0.8.4,<0.9.0"]
build-backend = "uv_build"

# For src/ layout
[tool.uv.build-backend]
module-name = "myproject_core"
module-root = "src"
```

#### Dependent package

```toml
# packages/myproject-api/pyproject.toml
[project]
name = "myproject-api"
version = "1.0.0"
requires-python = ">=3.12"
dependencies = [
    "myproject-core",  # Internal dependency - resolved via workspace
    "litestar>=2.0",
]

[project.scripts]
myproject-api = "myproject_api.cli:main"

[build-system]
requires = ["uv-build>=0.8.4,<0.9.0"]
build-backend = "uv_build"

[tool.uv.build-backend]
module-name = "myproject_api"
module-root = "src"
```

#### Namespace package (setuptools)

For namespace packages using PEP 420:

```toml
# packages/myproject-core/pyproject.toml
[project]
name = "myproject-core"
version = "1.0.0"
requires-python = ">=3.12"
dependencies = [
    "pydantic>=2.0",
]

[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]
namespaces = true
```

---

## Commands

### Initial Setup

```bash
# Sync all dependencies and create lockfile
uv sync

# Verify installation
uv run python -c "import myproject_core; print('OK')"
```

### Adding Dependencies

```bash
# Add to root (dev tools, shared deps)
uv add --dev pytest-cov

# Add to specific package
uv add --package myproject-core sqlalchemy
uv add --package myproject-api litestar

# Add dev dependency to package
uv add --package myproject-core --dev pytest-asyncio
```

### Running Commands

```bash
# Run tests (all packages)
uv run pytest

# Run tests for specific package
uv run pytest packages/myproject-core/tests

# Run entry points
uv run myproject-api

# Run module
uv run python -m myproject_api
```

### Building and Publishing

```bash
# Build single package
uv build --package myproject-core

# Build all packages
uv build --all

# Publish (after building)
uv publish --package myproject-core
```

---

## Type Checking

### Mypy Configuration

For namespace packages, run mypy from **within each package directory** to avoid "module found twice" errors:

```bash
cd packages/myproject-core && uv run mypy src/myproject
cd packages/myproject-api && uv run mypy src/myproject
```

Package-level mypy config:

```toml
# packages/myproject-core/pyproject.toml
[tool.mypy]
mypy_path = "src"
packages = ["myproject"]
namespace_packages = true
explicit_package_bases = true
strict = true
```

### Pyrefly (Alternative)

For faster type checking across the entire workspace:

```bash
uv run pyrefly check
```

---

## Testing Strategy

### Test Organization

```
my-project/
├── packages/
│   ├── myproject-core/
│   │   └── tests/
│   │       ├── unit/           # Unit tests for this package
│   │       └── integration/    # Integration tests (database, etc.)
│   └── myproject-api/
│       └── tests/
│           ├── unit/
│           └── integration/
└── tests/                      # Cross-package E2E tests
    └── e2e/
```

### Running Tests

```bash
# All tests
uv run pytest

# Single package
uv run pytest packages/myproject-core/tests

# Only unit tests
uv run pytest -m "not slow and not e2e"

# Only E2E tests
uv run pytest tests/e2e -m e2e
```

### Pytest Configuration

Centralize in root `pyproject.toml`:

```toml
[tool.pytest.ini_options]
addopts = "-ra --import-mode=importlib"
testpaths = [
    "packages/myproject-core/tests/unit",
    "packages/myproject-core/tests/integration",
    "packages/myproject-api/tests",
    "tests",
]
markers = [
    "slow: marks tests as slow",
    "e2e: end-to-end tests requiring full stack",
]
filterwarnings = [
    "ignore::DeprecationWarning",
]
```

---

## Makefile Shortcuts

```makefile
.PHONY: install test lint format typecheck build clean

install:
	uv sync

test:
	uv run pytest

test-unit:
	uv run pytest -m "not slow and not e2e"

lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run pyrefly check

build:
	uv build --all

clean:
	rm -rf dist/ .venv/ .pytest_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} +
```

---

## Key Principles

### 1. Single Lockfile

`uv.lock` at root ensures consistent versions across all packages. Never create package-level lockfiles.

### 2. Shared Virtual Environment

One `.venv/` at root contains all packages in editable mode. All packages see each other immediately.

### 3. Use src/ Layout

Prevents import issues during development:
```
packages/myproject-core/src/myproject_core/
```

This ensures you're importing the installed package, not the source directory.

### 4. Dependency Groups Over Extras

Use `[dependency-groups]` for dev/doc/test deps:

```toml
# CORRECT - Dependency groups
[dependency-groups]
dev = ["pytest", "ruff"]

# AVOID - Optional dependencies for dev tools
[project.optional-dependencies]
dev = ["pytest", "ruff"]
```

### 5. workspace = true

Always use `{ workspace = true }` in `[tool.uv.sources]` for inter-package dependencies:

```toml
[tool.uv.sources]
myproject-core = { workspace = true }  # Resolved from workspace
```

### 6. Root is Virtual

Set `package = false` if the root shouldn't be installable:

```toml
[tool.uv]
package = false
```

---

## Common Gotchas

| Problem | Symptom | Solution |
|---------|---------|----------|
| Module not found | `ImportError` after setup | Run `uv sync` |
| Module found twice | Mypy errors about duplicate | Run mypy from package dir, not root |
| Namespace broken | Can't import across packages | Remove `__init__.py` from namespace root |
| Wrong version used | Getting PyPI version not local | Add `workspace = true` to `[tool.uv.sources]` |
| Changes not visible | Old code still running | Delete `.venv/` and run `uv sync` |
| Circular dependency | Import errors at startup | Restructure: extract shared code to core package |
| Build fails | Missing module in wheel | Check `[tool.uv.build-backend]` settings |

---

## Migration from Single Package

1. **Create structure:**
   ```bash
   mkdir -p packages/myproject-core/src
   ```

2. **Move code:**
   ```bash
   mv src/myproject packages/myproject-core/src/
   mv tests packages/myproject-core/
   ```

3. **Create package pyproject.toml** with package-specific deps

4. **Update root pyproject.toml** with workspace configuration

5. **Sync:**
   ```bash
   rm -rf .venv uv.lock
   uv sync
   ```

6. **Verify:**
   ```bash
   uv run pytest
   ```

---

## Related Documents

- **Coding Guidelines:** [coding-guidelines.md](coding-guidelines.md) - Core development rules
- **Testing:** [testing.md](testing.md) - Test patterns and best practices
- **Design Patterns:** [design-patterns.md](design-patterns.md) - When to use patterns

**Last Updated:** 2025-12-24
