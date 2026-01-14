# Python Development Checklists

**Section:** Generic Python | **See Also:** [coding-guidelines.md](coding-guidelines.md), [testing.md](testing.md)

Practical checklists for Python development that apply regardless of the web framework you use.

---

## Pre-Commit Checklist

Use this before committing Python code.

### Code Quality
- [ ] All new code has type hints
- [ ] Public functions/classes have docstrings
- [ ] Line length ≤ 88 characters
- [ ] No debug `print()` statements
- [ ] No commented-out code
- [ ] No `TODO` comments without issue numbers

### Code Style
- [ ] Ran `uv run ruff format .`
- [ ] Ran `uv run ruff check . --fix`
- [ ] All imports are sorted (I001)
- [ ] No unused imports
- [ ] Function names use `snake_case`
- [ ] Class names use `PascalCase`
- [ ] Constants use `UPPER_SNAKE_CASE`

### Type Checking
- [ ] Ran `uv run pyrefly`
- [ ] Fixed all type errors
- [ ] Added explicit `None` checks for `Optional` types

### Testing
- [ ] All tests pass (`uv run pytest`)
- [ ] New features have tests
- [ ] Bug fixes have regression tests
- [ ] Test coverage for edge cases

### Git
- [ ] Checked `git status` for untracked files
- [ ] Commit message is clear and descriptive
- [ ] Commit message doesn't mention AI tools

---

## Code Review Checklist

Use this when reviewing Python code.

### Architecture & Design
- [ ] Follows existing patterns
- [ ] No unnecessary abstraction
- [ ] Single Responsibility Principle followed
- [ ] DRY - no code duplication
- [ ] Appropriate use of dataclasses vs classes

### Code Quality
- [ ] Type hints present and correct
- [ ] Docstrings for public APIs
- [ ] Clear variable and function names
- [ ] Early returns to avoid nesting
- [ ] Error handling is explicit
- [ ] No magic values (uses named constants)

### Testing
- [ ] Tests follow AAA pattern (Arrange, Act, Assert)
- [ ] Tests are isolated and independent
- [ ] Descriptive test names
- [ ] Edge cases covered

### Documentation
- [ ] README updated if needed
- [ ] Inline comments explain "why", not "what"

---

## Architecture Checklist

Use this when planning system structure.

### System Structure
- [ ] Architecture follows "Functional Core / Imperative Shell" pattern
- [ ] Side effects isolated at system edges
- [ ] Core business logic is pure and predictable
- [ ] Dependencies point inward

### Nouns and Verbs
- [ ] **Nouns (state)** as classes/dataclasses
- [ ] **Verbs (logic)** as functions
- [ ] Clear separation: classes hold state, functions perform operations
- [ ] Functions are stateless and composable

### Design Principles
- [ ] Reviewed [4-rules-design.md](4-rules-design.md)
- [ ] Reviewed [nouns-and-verbs.md](nouns-and-verbs.md)
- [ ] Reviewed [design-patterns.md](design-patterns.md)

---

## Design Checklist

Use this when designing a feature before coding.

### 4 Rules of Simple Design

**Rule 1: Passes All Tests**
- [ ] Test requirements identified
- [ ] Testability considered in design

**Rule 2: Reveals Intention**
- [ ] Names clearly express purpose
- [ ] No cryptic abbreviations

**Rule 3: No Duplication**
- [ ] DRY principle applied
- [ ] Business rules centralized

**Rule 4: Fewest Elements**
- [ ] Minimal design that solves the problem
- [ ] No speculative features

### Class vs Function Decision

**Use a Class when:**
- [ ] Grouping data (use dataclass)
- [ ] Managing resources
- [ ] Maintaining state across operations

**Use a Function when:**
- [ ] Performing transformation
- [ ] Validating data
- [ ] Operation is stateless

### YAGNI Check
- [ ] No "future-proofing" features
- [ ] No abstraction without multiple use cases
- [ ] Simple, direct solution to current problem

---

## Testing Checklist

Use this for comprehensive test coverage.

### Test Quality
- [ ] Follows AAA pattern (Arrange, Act, Assert)
- [ ] One assertion per test (or related assertions)
- [ ] Descriptive test names
- [ ] Tests are isolated (no dependencies)
- [ ] Tests are deterministic

### Coverage
- [ ] Happy path covered
- [ ] Error cases covered
- [ ] Edge cases (empty inputs, boundaries)
- [ ] Validation errors tested

### Anti-Patterns Avoided
- [ ] No over-mocking
- [ ] Verify state, not behavior
- [ ] Use stubs over mocks

---

## Related Documents

- [coding-guidelines.md](coding-guidelines.md) — Core Python practices
- [testing.md](testing.md) — Testing best practices
- [4-rules-design.md](4-rules-design.md) — Design principles

**Last Updated:** 2025-12-24
