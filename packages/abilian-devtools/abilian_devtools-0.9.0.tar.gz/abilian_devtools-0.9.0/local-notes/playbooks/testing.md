# Testing Best Practices

**Section:** Generic Python | **See Also:** [coding-guidelines.md](coding-guidelines.md), [4-rules-design.md](4-rules-design.md)

This document captures testing principles and best practices for Python projects.

---

## Testing Philosophy

### Core Principles

**From 4 Rules of Simple Design:**
1. **Passes all tests** - Code correctness proven by comprehensive test suite
2. **Reveals intention** - Tests as documentation of expected behavior
3. **No duplication** - DRY applies to tests too
4. **Fewest elements** - Minimal, focused tests without unnecessary complexity

**Testing Mindset:**
- **State over Behavior**: Verify tangible outcomes (state) rather than internal interactions (behavior)
- **No Mocks**: Prefer stubs. Tests that check final state are more robust and less coupled
- **Real Environments**: Create testing environments for components that are difficult to validate directly
- **Fast Feedback**: Tests should run quickly to enable frequent validation

### Test Pyramid

```
         /\
        /  \  E2E Tests (Few)
       /____\
      /      \  Integration Tests (Some)
     /________\
    /          \  Unit Tests (Many)
   /____________\
```

**Unit Tests (70%):**
- Test individual functions/classes in isolation
- Fast execution (<1ms per test)
- Focus on business logic without external dependencies
- Example: Model validation, utility functions

**Integration Tests (20%):**
- Test interactions between components
- Use real database (test instance)
- Verify repository/service layer operations
- Example: Database queries, ORM behavior

**End-to-End Tests (10%):**
- Test complete user workflows
- Include all layers (API → Service → Repository → Database)
- Example: Full API request/response cycle

---

## Test Organization

### Directory Structure

```
tests/
├── a_unit/              # Unit tests (isolated, fast)
│   ├── test_models.py   # Model structure tests
│   ├── test_services.py # Business logic tests
│   └── test_utils.py    # Utility function tests
├── b_integration/       # Integration tests (with DB)
│   ├── test_repositories.py
│   └── test_services_integration.py
├── c_e2e/              # End-to-end tests
│   └── test_api.py
└── conftest.py         # Shared fixtures
```

**Naming Convention:**
- Prefix with `a_`, `b_`, `c_` to control execution order
- Use descriptive test names: `test_<action>_<expected_result>`
- Group related tests in classes: `TestStudentService`

### Pytest Markers

```python
# Mark test types
@pytest.mark.unit          # Unit tests (no DB)
@pytest.mark.integration   # Integration tests (with DB)
@pytest.mark.e2e          # End-to-end tests

# Mark slow tests
@pytest.mark.slow

# Mark tests requiring specific setup
@pytest.mark.requires_redis
```

**Run specific test types:**
```bash
uv run pytest -m unit              # Run only unit tests
uv run pytest -m "not slow"        # Skip slow tests
uv run pytest tests/a_unit/        # Run specific directory
```

---

## General Testing Principles

### The AAA Pattern

Every test should follow **Arrange-Act-Assert**:

```python
def test_calculate_total():
    # ARRANGE: Set up test data and preconditions
    items = [
        {"name": "Widget", "price": 10.00, "quantity": 2},
        {"name": "Gadget", "price": 25.00, "quantity": 1},
    ]

    # ACT: Perform the operation being tested
    total = calculate_total(items)

    # ASSERT: Verify the outcome
    assert total == 45.00
```

**Why AAA?**
- Clear separation of concerns
- Easy to understand test intent
- Simple to maintain and modify
- Acts as executable documentation

### Test Isolation

**Each test must be independent:**

```python
# Good - Independent
def test_create_user():
    user = create_test_user()
    assert user.id is not None

def test_update_user():
    user = create_test_user()  # Own setup
    user.name = "Updated"
    assert user.name == "Updated"

# Bad - Dependent
user = None

def test_create_user():
    global user
    user = create_test_user()  # Shared state

def test_update_user():
    global user
    user.name = "Updated"  # Depends on previous test
```

**Isolation Benefits:**
- Tests can run in any order
- Parallel execution possible
- Failures don't cascade
- Easy debugging

### Test One Thing

**Focus each test on a single behavior:**

```python
# Good - Single focused assertion
def test_user_creation_generates_id():
    user = User(name="John")
    save(user)
    assert user.id is not None

def test_user_creation_sets_timestamp():
    user = User(name="John")
    save(user)
    assert user.created_at is not None

# Bad - Multiple assertions testing different things
def test_user_creation():
    user = User(name="John")
    save(user)
    assert user.id is not None
    assert user.created_at is not None
    assert user.name == "John"
    assert user.is_active is True
```

**Exception:** Related assertions that verify different aspects of the same outcome are acceptable:
```python
def test_create_order_with_all_items():
    order = create_order_with_items()
    # These all verify the same operation succeeded
    assert order.total == expected_total
    assert len(order.items) == 3
    assert order.status == "pending"
```

### Meaningful Test Names

```python
# Good - Describes what and why
def test_delete_user_removes_from_database():
    pass

def test_update_user_name_preserves_other_fields():
    pass

def test_create_order_fails_without_customer_id():
    pass

# Bad - Vague or implementation-focused
def test_user_1():
    pass

def test_repository_method():
    pass

def test_service_call():
    pass
```

---

## Pytest Patterns

### Fixtures

**Fixtures provide reusable test setup:**

```python
import pytest
from collections.abc import Generator

@pytest.fixture
def sample_user() -> User:
    """Create a sample user for tests."""
    return User(
        name="Test User",
        email="test@example.com",
        is_active=True,
    )

@pytest.fixture
def sample_products() -> list[Product]:
    """Create sample products for tests."""
    return [
        Product(name="Widget", price=10.00),
        Product(name="Gadget", price=25.00),
    ]

# Fixtures with cleanup
@pytest.fixture
def temp_file() -> Generator[Path, None, None]:
    """Create a temporary file that's cleaned up after test."""
    path = Path("/tmp/test_file.txt")
    path.write_text("test content")
    yield path
    path.unlink(missing_ok=True)  # Cleanup
```

**Fixture Scopes:**
- `function` (default): New instance per test
- `class`: Shared within test class
- `module`: Shared within module
- `session`: Shared across entire test session

**When to Use Fixtures:**
- Common test data setup
- Resource management (DB connections, files)
- Expensive setup operations
- Dependency injection in tests

### Async Testing with anyio

**Use anyio for async tests, not asyncio:**

```python
# Good - anyio
import pytest

@pytest.mark.anyio
async def test_async_operation():
    result = await async_function()
    assert result == expected

# Bad - asyncio (less portable)
import asyncio

@pytest.mark.asyncio
async def test_async_operation():
    result = await async_function()
    assert result == expected
```

**Why anyio?**
- More portable (works with asyncio, trio, curio)
- Better debugging support
- Recommended by modern async frameworks

### Parametrized Tests

**Test multiple inputs efficiently:**

```python
@pytest.mark.parametrize("input_value,expected", [
    ("hello", "HELLO"),
    ("World", "WORLD"),
    ("", ""),
    ("123", "123"),
])
def test_uppercase_conversion(input_value: str, expected: str):
    assert input_value.upper() == expected


@pytest.mark.parametrize("age,is_adult", [
    (17, False),
    (18, True),
    (21, True),
    (0, False),
])
def test_is_adult(age: int, is_adult: bool):
    user = User(age=age)
    assert user.is_adult == is_adult
```

---

## Testing Anti-Patterns

### Over-Mocking

**Problem:** Mocking too much makes tests brittle and coupled to implementation.

```python
# Bad - Over-mocked
def test_create_user_over_mocked(mocker):
    mock_repo = mocker.Mock()
    mock_repo.save.return_value = User(id=1, name="John")
    mock_validator = mocker.Mock()
    mock_validator.validate.return_value = True
    mock_notifier = mocker.Mock()

    service = UserService(mock_repo, mock_validator, mock_notifier)
    result = service.create_user("John")

    mock_repo.save.assert_called_once()
    mock_validator.validate.assert_called_once()
    mock_notifier.notify.assert_called_once()

# Good - Use stubs and verify state
def test_create_user_with_stub():
    stub_repo = InMemoryUserRepository()
    service = UserService(stub_repo)

    result = service.create_user("John")

    assert result.name == "John"
    assert stub_repo.get(result.id) is not None
```

### Testing Implementation Details

**Problem:** Tests break when implementation changes but behavior stays the same.

```python
# Bad - Tests implementation
def test_cache_stores_in_dict():
    cache = Cache()
    cache.set("key", "value")
    assert cache._internal_dict["key"] == "value"  # Implementation detail!

# Good - Tests behavior
def test_cache_retrieves_stored_value():
    cache = Cache()
    cache.set("key", "value")
    assert cache.get("key") == "value"
```

### Test Data Pollution

**Problem:** Tests share state and affect each other.

```python
# Bad - Shared state
test_users = []

def test_add_user():
    test_users.append(User(name="Alice"))
    assert len(test_users) == 1  # Fails if another test added users!

# Good - Isolated state
def test_add_user():
    users = []
    users.append(User(name="Alice"))
    assert len(users) == 1
```

---

## Quick Reference Checklist

### Before Writing Tests
- [ ] Understand what behavior to test
- [ ] Plan test structure (unit/integration/e2e)
- [ ] Identify dependencies and how to isolate them

### Writing Tests
- [ ] Follow AAA pattern (Arrange-Act-Assert)
- [ ] One assertion per test (or related assertions)
- [ ] Use descriptive test names
- [ ] Tests are isolated and independent
- [ ] Use fixtures for common setup

### Test Quality
- [ ] Tests are fast (< 5s for full suite)
- [ ] Tests are deterministic (no flaky tests)
- [ ] Tests verify state, not behavior
- [ ] No excessive mocking
- [ ] Edge cases covered

---

## Related Documents

- [coding-guidelines.md](coding-guidelines.md) — Core testing requirements
- [4-rules-design.md](4-rules-design.md) — "Passes all tests" principle
- [CHECKLISTS.md](CHECKLISTS.md) — Testing checklist

**For framework-specific testing:**
- [../litestar-dishka/stack-guide.md](../litestar-dishka/stack-guide.md) (Part 8) — SQLAlchemy and service testing patterns
- [../litestar-dishka/COMMON-GOTCHAS.md](../litestar-dishka/COMMON-GOTCHAS.md) — Testing gotchas (flush vs commit, etc.)

**Last Updated:** 2025-12-24
