# Document Processing Service

A FastAPI microservice for uploading documents and running async processing jobs (text extraction, summarization, keyword extraction).

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [uv](https://docs.astral.sh/uv/): Python package/project manager
- Python 3.13+

## Setup

```bash
# 1. Copy the environment template
cp .env.example .env

# 2. Install dependencies (needed to run tests locally)
uv sync

# 3. Start the app
docker compose up -d
```

The API is available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

> **How migrations work:** `scripts/migrate_and_start.sh` runs automatically when any container starts. It creates `docprocessor_test` if it does not exist, applies Alembic migrations to both the main and test databases, then hands off to the app or worker process. You never need to run migrations manually.

## Environment Variables

| Variable            | Default / Example                                                         | Description                          |
| ------------------- | ------------------------------------------------------------------------- | ------------------------------------ |
| `DATABASE_URL`      | `postgresql+asyncpg://postgres:postgres@localhost:5432/docprocessor`      | Main application database            |
| `TEST_DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/docprocessor_test` | Separate database used by test suite |
| `TEMPORAL_HOST`     | `localhost:7233`                                                          | Address of the Temporal server       |

## Running Tests

Tests are split into two categories:

### Unit tests

```bash
uv run pytest tests/unit
```

These test service logic in isolation using in-memory fake repositories. No database or Docker required.

### Integration tests

`docker compose up -d` sets up everything — including `docprocessor_test`. Once the containers are running, just run:

```bash
uv run pytest tests/test_documents.py tests/test_jobs.py tests/test_validation.py
```

### All tests with coverage

```bash
uv run pytest --cov=app --cov-report=term-missing
```

## Project Structure

```
app/
  api/v1/          # Route handlers (documents, jobs)
  core/            # Config, DB engine, errors, logging, middleware
  models/          # SQLAlchemy ORM models
  repositories/    # Data access layer (interfaces + implementations)
  schemas/         # Pydantic request/response schemas
  services/        # Business logic
scripts/
  migrate_and_start.sh  # Creates both DBs, runs all migrations, then starts the process
tests/
  fakes/           # In-memory repository implementations for unit tests
  unit/            # Service-level unit tests (no DB)
  test_documents.py, test_jobs.py, test_validation.py  # Integration tests
docs/adr/          # Architecture Decision Records
```

## API Endpoints

| Method | Path                             | Description                |
| ------ | -------------------------------- | -------------------------- |
| GET    | `/health`                        | Health check               |
| POST   | `/api/v1/documents`              | Upload a document          |
| GET    | `/api/v1/documents`              | List documents (paginated) |
| GET    | `/api/v1/documents/{id}`         | Get document details       |
| DELETE | `/api/v1/documents/{id}`         | Delete a document          |
| POST   | `/api/v1/documents/{id}/process` | Start a processing job     |
| GET    | `/api/v1/jobs/{job_id}`          | Get job status             |
| GET    | `/api/v1/jobs/{job_id}/results`  | Get job results            |
