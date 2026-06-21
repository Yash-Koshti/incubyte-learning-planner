# ADR-001: Repository Pattern with Protocol Interfaces

## Context

Services need to read and write data. The options were:

- **Direct session access**: services call `session.execute(select(...))` directly
- **Repository classes**: services call `repository.get_by_id(id)`, repository owns the query
- **Active Record**: models expose `Document.find(id)` class methods (SQLAlchemy supports this via mixins)

## Decision

Use repository classes (`DocumentRepository`, `JobRepository`) that wrap an `AsyncSession`.  
Define `IDocumentRepository` and `IJobRepository` as `typing.Protocol` interfaces in `app/repositories/interfaces.py`.  
Services depend on the interfaces, not the concrete classes.

## Consequences

**Benefits:**

- Unit tests inject `FakeDocumentRepository` (in-memory dict) instead of a real session, no database required
- The Protocol defines a contract: if the fake satisfies the interface, the service will work with the real implementation too
- SQLAlchemy session management stays entirely in the repository layer

**Trade-offs:**

- Two extra files per aggregate (interface + implementation)
- Protocol-based duck typing doesn't enforce implementation at definition time. A missing method is only caught when the type checker runs or the method is called

## Why Protocol over ABC?

`typing.Protocol` enables structural subtyping: `FakeDocumentRepository` satisfies `IDocumentRepository` without explicitly inheriting from it. This keeps the fake and the real implementation independent — neither needs to know the other exists.
