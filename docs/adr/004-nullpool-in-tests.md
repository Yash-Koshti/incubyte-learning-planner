# ADR-004: NullPool for SQLAlchemy in Integration Tests

## Context

Integration tests use `pytest-asyncio` with a session-scoped event loop. SQLAlchemy's default connection pool (`QueuePool`) holds connections open across the pool's lifetime. When the event loop is torn down between tests (or between the session-scoped setup fixture and individual test functions), pooled connections become invalid; SQLAlchemy raises `Event loop is closed`.

## Decision

Create the test engine with `poolclass=NullPool`:

```python
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
```

`NullPool` disables pooling entirely: every `async with session:` opens a fresh connection and closes it when the context exits.

## Consequences

**Benefits:**

- No stale connections across event loop boundaries and the error disappears entirely
- Each test gets a clean connection with no state leakage from pool internals

**Trade-offs:**

- Slightly higher connection overhead per test (open + close per session instead of reuse)
- `NullPool` is test-only; production uses the default `QueuePool` for connection reuse

## Why not use a single connection with nested transactions?

SQLAlchemy 1.x supported `session.bind = conn` for wrapping tests in a transaction that rolls back. This pattern is broken in SQLAlchemy 2.0's async mode. `NullPool` + explicit table truncation in a `clean_tables` fixture is the idiomatic 2.0 replacement.
