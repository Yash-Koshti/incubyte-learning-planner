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

# 2. Start PostgreSQL
docker compose up -d db

# 3. Install dependencies
uv sync

# 4. Run migrations
uv run alembic upgrade head

# 5. Start the app
docker compose up app
```

The API is available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

## Environment Variables

| Variable       | Default                                                              | Description          |
| -------------- | -------------------------------------------------------------------- | -------------------- |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/docprocessor` | Async PostgreSQL URL |

## Running Tests

Tests are split into two categories:

### Unit tests

```bash
uv run pytest tests/unit
```

These test service logic in isolation using in-memory fake repositories.

### Integration tests

```bash
# Ensure the test DB exists first
docker compose up -d db
uv run alembic upgrade head

uv run pytest tests/test_documents.py tests/test_jobs.py tests/test_validation.py
```

These test the full HTTP stack against a real `docprocessor_test` database.

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
