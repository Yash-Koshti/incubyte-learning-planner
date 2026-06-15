# Document Processing Service — Curriculum

## Tech Stack
FastAPI + PostgreSQL + SQLAlchemy + Alembic + Docker + pytest

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
