# ADR-002: Async SQLAlchemy 2.0 with asyncpg Driver

## Context

FastAPI is an async framework. The choices for database access were:

- **Synchronous SQLAlchemy**: works but blocks the event loop on every query, negating FastAPI's concurrency benefits
- **Raw asyncpg**: fully async, but requires hand-writing SQL and result mapping
- **SQLAlchemy 2.0 async**: async ORM on top of asyncpg, supports the same `select()` / `mapped_column` API

## Decision

Use `sqlalchemy[asyncio]` with the `asyncpg` driver (`postgresql+asyncpg://`).  
Engine is created once at startup via `create_async_engine`. Sessions are created per-request via `async_sessionmaker` and injected through FastAPI's `Depends(get_db)`.

## Consequences

**Benefits:**

- All DB I/O is non-blocking, requests don't queue behind each other waiting for Postgres
- Full ORM mapping: relationships, `Mapped` type annotations, Alembic migrations
- SQLAlchemy 2.0 style (`select(Model)` instead of `session.query(Model)`) is explicit and type-safe

**Trade-offs:**

- Async SQLAlchemy requires `NullPool` in tests to avoid `Event loop is closed` errors (see ADR-005)
- Lazy-loaded relationships are disabled in async mode. All related data must be eagerly loaded or explicitly queried

## Why not raw asyncpg?

ORMs provide migrations (Alembic), Python-level validation, and relationship management. The productivity cost of hand-rolling SQL + result mapping is not justified for a service with a small, stable schema.
