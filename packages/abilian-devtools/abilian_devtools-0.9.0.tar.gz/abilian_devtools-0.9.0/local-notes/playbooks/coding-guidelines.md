# Python Development Guidelines

**Section:** Generic Python | **See Also:** [4-rules-design.md](4-rules-design.md), [testing.md](testing.md)

This document provides essential Python coding practices for all projects (web, CLI, AI/ML, etc.).

---

## Core Development Rules

### 1. Package Management

- **ONLY use `uv`, NEVER `pip`**
- Installation: `uv add package`
- Running tools: `uv run tool`
- **FORBIDDEN:** `uv pip install`, `@latest` syntax

### 2. Code Quality

- Type hints required for all code
- Public APIs must have docstrings
- Functions must be focused and small
- Follow existing patterns exactly
- Line length: 88 chars maximum
- Start each module with main functions/classes (top-down), unless constrained otherwise

### 3. Testing Requirements

- Framework: `uv run pytest`
- Async testing: use `anyio`, not `asyncio`
- Coverage: test edge cases and errors
- New features require tests
- Bug fixes require regression tests

### 4. Code Style

- PEP 8 naming (`snake_case` for functions/variables)
- Class names in `PascalCase`
- Constants in `UPPER_SNAKE_CASE`
- Document with docstrings
- Use f-strings for formatting (but not for logging)

### 5. Commit Messages

- NEVER mention `co-authored-by` or similar aspects
- Never mention tools used to create commits or PRs

---

## Development Philosophy

- **Simplicity:** Write simple, straightforward code
- **Readability:** Make code easy to understand
- **Performance:** Consider performance without sacrificing readability
- **Maintainability:** Write code that's easy to update
- **Testability:** Ensure code is testable
- **Reusability:** Create reusable components and functions
- **Less Code = Less Debt:** Minimize code footprint
- **Functional Core / Imperative Shell:** Isolate side-effects (IO, state changes) at the application's edges, keeping core logic pure, immutable, and predictable

---

## Coding Best Practices

- **Early Returns:** Use to avoid nested conditions
- **Descriptive Names:** Use clear variable/function names (e.g., prefix handlers with `handle_`)
- **Minimal Changes:** Only modify code related to the task at hand
- **Function Ordering:** Define composing functions before their components
- **TODO Comments:** Mark issues in existing code with `TODO:` prefix
- **Build Iteratively:** Start with minimal functionality and verify it works before adding complexity
- **Clean Logic:** Keep core logic clean and push implementation details to the edges
- **File Organization:** Balance file organization with simplicity - use an appropriate number of files for the project scale
- **Explicit Error Handling:** Handle potential errors explicitly rather than letting them fail silently
- **Avoid Magic Values:** Use named constants instead of hardcoded strings or numbers

---

## Data Structures

### Prefer Dataclasses

Use `@dataclass` for data containers instead of regular classes:

```python
from dataclasses import dataclass

# Good - Clear, concise, immutable
@dataclass(frozen=True)
class User:
    id: int
    name: str
    email: str

# Bad - Verbose boilerplate
class User:
    def __init__(self, id: int, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email
```

### When to Use Frozen Dataclasses

**Use `frozen=True` whenever possible** for immutability benefits:

```python
# Good - Immutable, hashable, thread-safe
@dataclass(frozen=True)
class Config:
    host: str
    port: int
    timeout: int = 30

# Good - Can be used as dict keys or in sets
@dataclass(frozen=True)
class Point:
    x: float
    y: float

points = {Point(0, 0), Point(1, 1)}  # Works because frozen=True
```

**When to use frozen dataclasses:**
- Configuration objects
- DTOs (Data Transfer Objects)
- Value objects in domain models
- Request/Response models
- Any data that shouldn't change after creation

**When NOT to use frozen:**
- Database models (ORMs often need mutability)
- Objects that accumulate state over their lifetime
- When you need to cache computed properties with `@cached_property`

### Performance Optimization with Slots

For frequently instantiated objects, use `slots=True` (Python 3.10+):

```python
# Good - Lower memory footprint
@dataclass(frozen=True, slots=True)
class Point:
    x: float
    y: float

# Creates millions of points - slots reduce memory by ~40%
points = [Point(i, i*2) for i in range(1_000_000)]
```

### Guidelines

- **Default to frozen:** Use `@dataclass(frozen=True)` unless you have a specific reason not to
- **Use slots for scale:** Add `slots=True` when creating many instances
- **Regular classes for behavior:** Only use regular classes when you need:
  - Complex inheritance hierarchies
  - Custom `__init__` logic
  - Mutable internal state management
  - Methods that modify the object

---

## Design: The 4 Rules of Simple Design

1. **Passes all tests:** First, ensure the code is correct and works as proven by a comprehensive test suite
2. **Reveals intention:** Write expressive code that is clear and easy to understand through good naming and small functions
3. **No duplication:** Eliminate redundancy by ensuring every piece of knowledge has a single, unambiguous representation (DRY)
4. **Fewest elements:** Keep the design minimal by removing any unnecessary code, classes, or complexity

Also:

- **DRY Code:** Don't repeat yourself
- **Functional Style:** Prefer functional, immutable approaches when not verbose
- **Simplicity:** Prioritize simplicity and readability over clever solutions
- **Single Responsibility:** Ensure functions and classes have a single, well-defined purpose

For detailed guidance, see [4-rules-design.md](4-rules-design.md).

---

## Testing

- Python tests use pytest with fixtures in `tests/`
- **Run Tests:** Test your code frequently with realistic inputs and validate outputs
- **Build Test Environments:** Create testing environments for components that are difficult to validate directly
- **Don't use mocks.** Prefer stubs. Whenever possible, verify a tangible outcome (state) rather than an internal interaction (behavior). Tests that check final state are generally more robust and less coupled to the implementation.
- **Leverage the pytest framework:** Let the framework do the work; no need to `print()` anything or provide a `main()` function

For comprehensive testing guidance, see [testing.md](testing.md).

---

## Python Tools

### Why These Tools?

- **uv:** Fast, modern replacement for pip with better dependency resolution
- **Ruff:** Single tool for formatting + linting (fast, replaces black + flake8)
- **pyrefly:** Fast type checker (alternative to mypy/pyright)
- **anyio:** Portable async/await patterns (works with asyncio and trio)

### Tool Usage

**1. Ruff**
- Format: `uv run ruff format .`
- Check: `uv run ruff check .`
- Fix: `uv run ruff check . --fix`
- Critical issues:
  - Line length (88 chars)
  - Import sorting (I001)
  - Unused imports
- Line wrapping:
  - Strings: use parentheses
  - Function calls: multi-line with proper indent
  - Imports: split into multiple lines

**2. Type Checking**
- Tool: `uv run pyrefly`
- Requirements:
  - Explicit None checks for Optional
  - Type narrowing for strings
  - Version warnings can be ignored if checks pass

**3. Pre-commit**
- Config: `.pre-commit-config.yaml`
- Runs: on git commit
- Tools: Prettier (YAML/JSON/JavaScript), Ruff (Python)

---

## Error Resolution

### Common Issues

**Type errors:**
- Get full line context
- Check Optional types
- Add type narrowing
- Verify function signatures

**Line length:**
- Break strings with parentheses
- Multi-line function calls
- Split imports

**Types:**
- Add None checks
- Narrow string types
- Match existing patterns

### Best Practices

- Check git status before commits
- Run formatters before type checks
- Keep changes minimal
- Follow existing patterns
- Document public APIs
- Test thoroughly

---

## Error Messages

Write clear, actionable error messages that help users resolve issues quickly.

**Key principles:**
- **Be specific:** "Disk full writing to /var/log/app.log" not "Write failed"
- **Identify source:** State which component is reporting the error
- **Explain the failure:** Convert error codes to plain language
- **Provide context:** Include relevant details (file paths, IDs, server names)

**Structure of good error messages:**
```
[Component] can't [action], error [details]: [plain language], [next action]
```

**Example:**
```
Webserver can't serve page, error opening file '/var/www/index.html':
Permission denied, reporting HTTP 404 error
```

For comprehensive error message guidelines, see [error-messages.md](error-messages.md).

---

## Related Documents

**In this section:**
- [4-rules-design.md](4-rules-design.md) — Kent Beck's Four Rules of Simple Design
- [nouns-and-verbs.md](nouns-and-verbs.md) — Functional architecture patterns
- [design-patterns.md](design-patterns.md) — GoF patterns for Python
- [error-messages.md](error-messages.md) — Writing effective error messages
- [testing.md](testing.md) — Testing best practices
- [CHECKLISTS.md](CHECKLISTS.md) — Pre-commit, code review, design checklists

**Other sections:**
- [../generic-webdev/](../generic-webdev/) — Web development patterns
- [../litestar-dishka/](../litestar-dishka/) — Litestar + Dishka stack guide
- [../pluggy/](../pluggy/) — Plugin system patterns

**Last Updated:** 2025-12-24
