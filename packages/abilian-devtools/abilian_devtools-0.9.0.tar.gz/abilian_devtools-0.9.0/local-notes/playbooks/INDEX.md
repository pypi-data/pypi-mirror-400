# Generic Python Playbooks

**Section:** Generic Python | **Back to:** [../INDEX.md](../INDEX.md)

Core Python development practices that apply to all Python projects, regardless of framework.

---

## Quick Start

1. Read [coding-guidelines.md](coding-guidelines.md) for core rules
2. Review [CHECKLISTS.md](CHECKLISTS.md) before committing code
3. Consult specific guides as needed

---

## Guides

### Core Practices

| Document | Description |
|----------|-------------|
| [coding-guidelines.md](coding-guidelines.md) | Essential rules: uv, type hints, code quality, dataclasses |
| [testing.md](testing.md) | Testing patterns: pytest, fixtures, AAA pattern, isolation |
| [error-messages.md](error-messages.md) | Writing helpful, actionable error messages |
| [monorepo.md](monorepo.md) | Python monorepo setup with uv workspaces |

### Design Philosophy

| Document | Description |
|----------|-------------|
| [4-rules-design.md](4-rules-design.md) | Kent Beck's Four Rules of Simple Design |
| [nouns-and-verbs.md](nouns-and-verbs.md) | Functional Core / Imperative Shell architecture |
| [design-patterns.md](design-patterns.md) | Modern design patterns for Python (2025 evaluation) |

### Reference

| Document | Description |
|----------|-------------|
| [CHECKLISTS.md](CHECKLISTS.md) | Pre-commit, code review, architecture checklists |

---

## Key Principles

### Package Management
- **Always use uv** (never pip): `uv add package`, `uv run tool`

### Code Quality
- Type hints required on all public functions
- 88-character line limit (Ruff default)
- Docstrings for public APIs

### Testing
- pytest with anyio for async
- Prefer stubs over mocks
- Verify state, not behavior

### Design
- Functional Core / Imperative Shell
- 4 Rules: Tests pass → Reveals intent → No duplication → Fewest elements
- Prefer dataclasses over dicts

---

## Related Sections

- [../generic-webdev/INDEX.md](../generic-webdev/INDEX.md) — Web development patterns
- [../litestar-dishka/INDEX.md](../litestar-dishka/INDEX.md) — Litestar + Dishka stack
- [../pluggy/INDEX.md](../pluggy/INDEX.md) — Plugin system with Pluggy

**Last Updated:** 2025-12-24
