# Writing Good Error Messages

**Section:** Generic Python | **See Also:** [coding-guidelines.md](coding-guidelines.md), [testing.md](testing.md)

---

## General Principles

- **Prioritize clarity and usefulness**: Assume errors will happen, and design messages to help users resolve issues quickly.
- **Avoid vague or generic messages**: Always provide specific, actionable information.

---

## Purpose-Driven Design

- **For operators**: Ensure messages guide them in configuring or troubleshooting software.
- **For system administrators**: Clearly indicate external issues (e.g., disk full, network down) that require intervention.
- **For developers**: Include details that help diagnose crashes or bugs, as error messages are often the only clues available.

---

## Error Message Taxonomy

### 1. Configuration Problems
Focus on educating the user about the system's requirements and what needs fixing.
- Example: "Can't start [component] because [dependency] is not running."
- Avoid: "Connection refused."

### 2. Unavailable Resources
Specify what resource is unavailable and where.
- Example: "Disk full writing to [path]."
- Include IP addresses or server names for connectivity issues to highlight potential DNS errors.

### 3. "Should Never Happen" Errors
Avoid dismissive language (e.g., "should never happen!").
- Example: "Unexpected address family accepting connection."

---

## Guidelines for Effective Error Messages

- **Identify the source**: State which subsystem, program, or module is reporting the error.
- **Describe the failed action**: Clearly explain what action could not be completed.
- **Specify the subject**: Include relevant details (e.g., file path, server IP, port number).
- **Explain the error**: Convert error codes into plain language (e.g., "Permission denied" instead of "errno = 13").
- **Optional**: State what the program will do next (e.g., "reporting HTTP 404 error").

**Example of an excellent error message**:
```
Webserver can't serve page, error opening file '/var/www/index.html':
Permission denied, reporting HTTP 404 error.
```

---

## Avoid Common Pitfalls

- **Technical jargon**: Skip filenames, function names, or line numbers unless they are meaningful to the user.
- **Overly technical details**: Focus on what the user can act on, not internal code references.

---

## Practical Examples

### Bad vs Good Error Messages

| Bad | Good | Why It's Better |
|-----|------|-----------------|
| "Error" | "Database connection failed: timeout connecting to db.example.com:5432" | Specific, actionable, includes context |
| "Invalid input" | "Email format invalid: missing '@' symbol" | Explains what's wrong |
| "Permission denied" | "Cannot write to /var/log/app.log: permission denied (check file ownership)" | Suggests fix |
| "Connection refused" | "Cannot connect to Redis at localhost:6379: connection refused (is Redis running?)" | Identifies service, suggests action |
| "File not found" | "Config file not found: expected at /etc/app/config.yaml" | Shows expected location |
| "Update failed" | "Cannot update user #123: email 'test@example.com' already registered" | Identifies conflict |

---

## Python Exception Examples

### Configuration Errors

```python
# Bad
raise ValueError("Invalid config")

# Good
raise ValueError(
    f"Database URL missing in environment: expected 'DATABASE_URL', "
    f"got {list(os.environ.keys())}"
)
```

### Resource Errors

```python
# Bad
raise FileNotFoundError("File not found")

# Good
raise FileNotFoundError(
    f"Template file not found: expected 'email_welcome.html' in "
    f"{templates_dir} (checked: {searched_paths})"
)
```

### Validation Errors

```python
# Bad
raise ValidationError("Invalid data")

# Good
raise ValidationError(
    f"User age must be between 0 and 150, got {age}. "
    f"Check field 'date_of_birth' in request."
)
```

### External Service Errors

```python
# Bad
raise ConnectionError("Connection failed")

# Good
raise ConnectionError(
    f"Payment gateway timeout: no response from {gateway_url} after "
    f"{timeout}s (transaction ID: {txn_id}, retry #{retry_count})"
)
```

---

## HTTP API Error Responses

```python
# Bad
{
    "error": "Not found"
}

# Good
{
    "error": "User not found",
    "detail": "No user with ID '550e8400-e29b-41d4-a716-446655440000'",
    "suggestion": "Check the user ID or use GET /users to list available users",
    "request_id": "req_abc123"
}
```

---

## Logging Errors

```python
# Bad
logger.error("Failed to process")

# Good
logger.error(
    "Failed to process payment",
    exc_info=exc,
    extra={
        "user_id": user.id,
        "amount": payment.amount,
        "payment_method": payment.method,
        "error_code": exc.code,
        "transaction_id": txn_id,
    }
)
```

---

## Error Message Template

**Standard structure:**

```
[Component] can't [action], error [details]: [plain language explanation], [next action]
```

**Examples applying template:**

- `Database can't execute query, error timeout: connection to db.example.com:5432 timed out after 30s, retrying (attempt 2/3)`
- `Email service can't send welcome email, error authentication failed: SMTP credentials rejected by smtp.gmail.com, check EMAIL_PASSWORD environment variable`
- `File storage can't save upload, error disk full: /uploads partition has 0 bytes free, contact system administrator`

---

## Related Documents

- [coding-guidelines.md](coding-guidelines.md) — Error handling best practices
- [../generic-webdev/api-design.md](../generic-webdev/api-design.md) — HTTP error response formats
- [../generic-webdev/production-patterns.md](../generic-webdev/production-patterns.md) — Error handling and logging

**Last Updated:** 2025-12-24
