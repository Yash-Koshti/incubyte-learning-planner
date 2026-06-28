# Document Processing Service — Curriculum

## Tech Stack
FastAPI + PostgreSQL + SQLAlchemy + Alembic + Docker + pytest + Temporal

## Skill Level
Intermediate

---

## Module 1: Project Setup
Goal: A running FastAPI service in Docker with PostgreSQL connected
- [x] Step 1.1: Scaffold the layered project structure
- [x] Step 1.2: Create `pyproject.toml` / `requirements.txt` with dependencies
- [x] Step 1.3: Write `main.py` — FastAPI app with a health-check endpoint
- [x] Step 1.4: Write `Dockerfile` and `docker-compose.yml`
- [x] Step 1.5: Verify the service starts and `/health` returns 200

---

## Module 2: Data Models
Goal: Document and ProcessingJob tables in PostgreSQL, migrated with Alembic
- [x] Step 2.1: Configure SQLAlchemy async engine and session factory
- [x] Step 2.2: Define `Document` SQLAlchemy model
- [x] Step 2.3: Define `ProcessingJob` and `ProcessingResult` models
- [x] Step 2.4: Initialise Alembic and generate first migration
- [x] Step 2.5: Write Pydantic schemas for request/response shapes
- [x] Step 2.6: Verify tables exist in PostgreSQL

---

## Module 3: Document CRUD
Goal: Upload, list, retrieve, and delete documents via REST
- [x] Step 3.1: `POST /documents` — file upload + metadata storage
- [x] Step 3.2: `GET /documents` — paginated list with status filter
- [x] Step 3.3: `GET /documents/{document_id}` — single document detail
- [x] Step 3.4: `DELETE /documents/{document_id}` — soft or hard delete
- [x] Step 3.5: Checkpoint — test all four endpoints manually via `/docs`

---

## Module 4: Processing Jobs
Goal: Create jobs, simulate processing, expose status and results
- [x] Step 4.1: `POST /documents/{document_id}/process` — create a job
- [x] Step 4.2: Simulated processing service (extract_text, summarize, keywords)
- [x] Step 4.3: `GET /jobs/{job_id}` — job status
- [x] Step 4.4: `GET /jobs/{job_id}/results` — processing results
- [x] Step 4.5: Background task execution (FastAPI BackgroundTasks)

---

## Module 5: Error Handling & Logging
Goal: Structured error responses and correlated request logs across all endpoints
- [x] Step 5.1: Global exception handlers and structured error schema
- [x] Step 5.2: Domain-specific exceptions (DocumentNotFound, JobNotFound, etc.)
- [x] Step 5.3: Request logging middleware with correlation ID
- [x] Step 5.4: Log processing lifecycle events (start, complete, fail)

---

## Module 6: Dependency Injection
Goal: All shared resources (DB, services, config) wired via FastAPI `Depends`
- [x] Step 6.1: `get_db` dependency — async DB session per request
- [x] Step 6.2: Repository layer — DocumentRepository, JobRepository
- [x] Step 6.3: Service layer injected via `Depends`
- [x] Step 6.4: Configuration object loaded from environment variables

---

## Module 7: API Versioning & Documentation
Goal: Versioned routes, OpenAPI examples on every endpoint
- [x] Step 7.1: Route versioning under `/api/v1/`
- [x] Step 7.2: Add OpenAPI request/response examples to all endpoints
- [x] Step 7.3: Verify `/docs` and `/redoc` look complete

---

## Module 8: Testing
Goal: pytest suite covering happy path, validation, and error cases — 80%+ coverage
- [x] Step 8.1: Test setup — pytest config, async TestClient, test DB
- [x] Step 8.2: Tests for Document CRUD endpoints
- [x] Step 8.3: Tests for Processing Job endpoints
- [x] Step 8.4: Tests for validation failures and error cases
- [x] Step 8.5: Unit tests for services and processing engine
- [x] Step 8.6: Measure coverage and close gaps

---

## Module 9: Temporal Fundamentals & Local Setup
Goal: Understand what Temporal is, run a dev server, and execute your first workflow end-to-end
- [x] Step 9.1: Mental model — Event History, replay, and why Temporal beats BackgroundTasks
- [x] Step 9.2: Temporal architecture — Server, Worker, Client, Task Queue
- [x] Step 9.3: Install Temporal CLI and start the dev server
- [x] Step 9.4: Add `temporalio` to the project with `uv`
- [x] Step 9.5: Write first activity and workflow ("Hello Temporal")
- [x] Step 9.6: Run the worker and trigger the workflow — see it complete

---

## Module 10: Activities & Workflows In Depth
Goal: Design robust activities and workflows with proper timeouts, retries, and lifecycle control
- [x] Step 10.1: Activity design — input/output with dataclasses, what belongs in an activity
- [x] Step 10.2: Timeouts — `start_to_close_timeout` vs `schedule_to_close_timeout`
- [x] Step 10.3: RetryPolicy — configuring retries, backoff, and non-retryable errors
- [x] Step 10.4: Handling activity failures in workflows (`try/except ActivityError`)
- [x] Step 10.5: Workflow signals — `@workflow.signal` for mutating workflow state
- [x] Step 10.6: Workflow queries — `@workflow.query` for reading state without side effects
- [x] Step 10.7: The Python sandbox — determinism rules and the `imports_passed_through` gotcha

---

## Module 11: Testing Temporal Code
Goal: Write reliable tests for activities and workflows without a production Temporal server
- [x] Step 11.1: Testing activities in isolation with `ActivityEnvironment`
- [x] Step 11.2: Testing workflows with `WorkflowEnvironment` (time-skipping test server)
- [x] Step 11.3: Mocking activities for workflow tests
- [x] Step 11.4: Simulating activity failures and verifying workflow error handling

---

## Module 12: FastAPI Integration
Goal: Replace BackgroundTasks + run_job with a durable Temporal workflow
- [x] Step 12.1: Architecture design — what changes, what stays (new ADR)
- [x] Step 12.2: Design the Document Processing Workflow and its four activities
- [x] Step 12.3: Create the Temporal worker module
- [x] Step 12.4: Connect a Temporal client to FastAPI via lifespan
- [ ] Step 12.5: Start a workflow from `POST /documents/{id}/process`
- [ ] Step 12.6: Query workflow status for `GET /jobs/{job_id}`
- [ ] Step 12.7: Add Temporal server to `docker-compose.yml`
- [ ] Step 12.8: End-to-end test — upload a document, start a job, poll for completion
