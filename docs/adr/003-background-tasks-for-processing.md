# ADR-003: FastAPI BackgroundTasks for Processing (Temporary)

## Context

Processing jobs (text extraction, summarization, keyword extraction) are too slow to run synchronously in the request/response cycle.
Options:

- **Synchronous**: process inline, block the response until done (poor UX, ties up the worker)
- **FastAPI BackgroundTasks**: run a coroutine after the response is sent, within the same process
- **Celery / RQ**: external task queue, requires Redis/broker infrastructure
- **Temporal**: durable workflow orchestration, handles retries, state persistence, and visibility

## Decision

Use FastAPI's `BackgroundTasks` for Stage 1. The `POST /documents/{id}/process` endpoint returns immediately with `202 Accepted`, and `run_job` runs after the response is sent.

`run_job` opens its own `AsyncSessionFactory` session because the request session is closed before background tasks execute.

## Consequences

**Benefits:**

- Zero additional infrastructure
- Simple to reason about for learning purposes

**Trade-offs:**

- Jobs are lost if the process crashes mid-execution (no durability)
- No retry logic
- No visibility into running jobs beyond polling the status endpoint
- `run_job` owns its own session, making it harder to test without patching `AsyncSessionFactory`

## Planned replacement (Stage 2)

BackgroundTasks will be replaced by Temporal workflows. The `ProcessingJob` status model (`pending → running → completed/failed`) and the operations list were designed from day one to map directly to a Temporal workflow with activity functions.
