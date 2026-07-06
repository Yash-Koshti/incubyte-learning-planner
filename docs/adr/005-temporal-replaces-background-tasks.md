# ADR-006: Temporal Replaces FastAPI BackgroundTasks for Processing

## Context

Stage 1 used FastAPI BackgroundTasks to run `run_job` after the HTTP response.
This approach has three problems:

- Jobs are lost if the process crashes mid-execution
- No retry logic for failed steps
- No visibility into which step is currently running

## Decision

Replace BackgroundTasks + run_job with a Temporal workflow.
The FastAPI process starts workflows via a Temporal client.
A separate worker process executes the workflow and activities.

## Consequences

**Benefits:**

- Workflows survive process crashes and Temporal replays from Event History
- Per-activity retry policies with configurable backoff
- Full execution visibility in the Temporal Web UI

**Trade-offs:**

- Temporal server is now a required infrastructure dependency
- Worker process must be deployed and kept running alongside the API
- Local dev requires running three processes: API, worker, Temporal server
