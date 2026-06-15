# Document Processing Service

## Overview

Build a backend system that allows users to upload documents and submit them for processing. The system stores document metadata, tracks processing jobs, exposes APIs for querying status and results, and maintains a complete history of processing operations.

The project should initially be implemented as a FastAPI-based microservice and later enhanced with Temporal to orchestrate long-running document processing workflows.

The objective is to learn:

- FastAPI fundamentals
- API design
- Pydantic validation
- Dependency Injection
- Testing
- Microservice architecture patterns
- Asynchronous programming
- Workflow orchestration with Temporal

---

# Business Problem

Organizations often receive large numbers of documents that require multiple processing steps before they become useful.

Examples:

- Extract text from uploaded PDFs
- Generate summaries
- Extract keywords
- Classify documents
- Generate metadata
- Notify users when processing completes

A single synchronous API request is not suitable for these operations because:

- Processing may take several minutes
- Some operations may fail and require retries
- Multiple steps must execute in sequence
- Processing status must survive service restarts

The system should therefore evolve from a simple API-driven architecture into a workflow-driven architecture.

---

# Stage 1: FastAPI Implementation

## Goal

Build a fully functional document processing backend using FastAPI without Temporal.

Processing may initially be simulated or performed synchronously.

---

# Functional Requirements

## Document Management

Users should be able to:

### Upload Document

```http
POST /documents
```

Request:

- File upload
- Optional title
- Optional description

Response:

```json
{
  "id": "uuid",
  "filename": "contract.pdf",
  "status": "uploaded"
}
```

---

### List Documents

```http
GET /documents
```

Support:

- Pagination
- Sorting
- Filtering by status

---

### Get Document Details

```http
GET /documents/{document_id}
```

Return:

- Metadata
- Upload timestamp
- Current status

---

### Delete Document

```http
DELETE /documents/{document_id}
```

---

## Processing Jobs

A document may have multiple processing jobs.

### Create Processing Job

```http
POST /documents/{document_id}/process
```

Request:

```json
{
  "operations": ["extract_text", "generate_summary", "extract_keywords"]
}
```

Response:

```json
{
  "job_id": "uuid",
  "status": "pending"
}
```

---

### Get Job Status

```http
GET /jobs/{job_id}
```

Response:

```json
{
  "job_id": "uuid",
  "status": "completed"
}
```

Possible statuses:

- pending
- running
- completed
- failed

---

### Get Processing Results

```http
GET /jobs/{job_id}/results
```

Response:

```json
{
  "summary": "...",
  "keywords": ["fastapi", "python"],
  "extracted_text": "..."
}
```

---

# Data Model

## Document

| Field       | Type     |
| ----------- | -------- |
| id          | UUID     |
| filename    | String   |
| title       | String   |
| description | String   |
| status      | Enum     |
| created_at  | Datetime |
| updated_at  | Datetime |

---

## ProcessingJob

| Field        | Type     |
| ------------ | -------- |
| id           | UUID     |
| document_id  | UUID     |
| status       | Enum     |
| created_at   | Datetime |
| completed_at | Datetime |

---

## ProcessingResult

| Field          | Type |
| -------------- | ---- |
| id             | UUID |
| job_id         | UUID |
| extracted_text | Text |
| summary        | Text |
| keywords       | JSON |

---

# Validation Requirements

Use Pydantic models for:

- Request validation
- Response validation
- Domain models

Examples:

- Empty title not allowed
- Unsupported file extensions rejected
- Invalid operation names rejected
- UUID validation

---

# Dependency Injection Requirements

Use FastAPI dependency injection for:

- Database sessions
- Service layer
- Logger
- Configuration

Example:

```python
Depends(get_db)
Depends(get_document_service)
```

---

# Error Handling Requirements

Implement structured error responses.

Example:

```json
{
  "error": {
    "code": "DOCUMENT_NOT_FOUND",
    "message": "Document does not exist"
  }
}
```

Handle:

- Validation failures
- Missing documents
- Missing jobs
- File upload errors
- Internal server errors

---

# Logging Requirements

Log:

- API requests
- Processing start
- Processing completion
- Processing failures

Include:

- Correlation ID
- Request path
- Processing job ID

---

# Testing Requirements

Write tests for:

## API Endpoints

- Upload document
- List documents
- Get document
- Delete document
- Create job
- Query job
- Query results

---

## Validation

- Invalid file type
- Invalid UUID
- Missing required fields

---

## Error Cases

- Missing document
- Missing job
- Internal exceptions

---

## Coverage Target

At least 80% coverage for:

- Services
- Routes
- Business logic

---

# Non-Functional Requirements

## Performance

Support:

- 1000+ documents
- Paginated retrieval

---

## Maintainability

Use layered architecture:

```text
app/
├── api/
├── services/
├── repositories/
├── models/
├── schemas/
├── dependencies/
├── tests/
└── main.py
```

---

## API Documentation

Expose:

```text
/docs
/redoc
```

Provide examples for all endpoints.

---

# Stage 1 Success Criteria

The system:

- Uploads documents
- Stores metadata
- Creates processing jobs
- Tracks job status
- Returns processing results
- Uses Pydantic validation
- Uses dependency injection
- Handles errors consistently
- Has automated tests
- Provides OpenAPI documentation

---

# Stage 2: Temporal Integration

## Goal

Replace the manual processing implementation with Temporal workflows.

The API layer should become responsible only for:

- Receiving requests
- Starting workflows
- Querying workflow state

Temporal should handle orchestration.

---

# Workflow Design

## Document Processing Workflow

Workflow:

```text
Upload Document
      |
      v
Extract Text
      |
      v
Generate Summary
      |
      v
Extract Keywords
      |
      v
Store Results
      |
      v
Mark Complete
```

---

# Temporal Activities

## Activity: Extract Text

Input:

```json
{
  "document_id": "uuid"
}
```

Output:

```json
{
  "text": "..."
}
```

---

## Activity: Generate Summary

Input:

```json
{
  "text": "..."
}
```

Output:

```json
{
  "summary": "..."
}
```

---

## Activity: Extract Keywords

Input:

```json
{
  "text": "..."
}
```

Output:

```json
{
  "keywords": ["python", "fastapi"]
}
```

---

## Activity: Store Results

Persists results to database.

---

# Temporal Requirements

Implement:

- Workflow retries
- Activity retries
- Activity timeouts
- Workflow IDs
- Workflow queries
- Workflow signals

---

# Additional API Endpoints

## Start Workflow

```http
POST /workflows/document-processing
```

Response:

```json
{
  "workflow_id": "workflow-123"
}
```

---

## Workflow Status

```http
GET /workflows/{workflow_id}
```

---

## Workflow Details

```http
GET /workflows/{workflow_id}/results
```

---

# Failure Scenarios

The workflow should survive:

- Service restart
- Worker restart
- Database restart
- Activity failure

Activities should retry automatically.

---

# Temporal Testing Requirements

Write tests for:

- Workflow execution
- Activity execution
- Retry behavior
- Failure handling
- Workflow completion

---

# Stretch Goals

After completion:

### Notification Service

Notify users when processing finishes.

### AI Integration

Use an LLM to:

- Summarize documents
- Generate tags
- Classify documents

### Event-Driven Architecture

Publish events:

```text
DocumentUploaded
JobStarted
JobCompleted
JobFailed
```

### Multi-Service Architecture

Split into:

```text
document-service
processing-service
notification-service
workflow-service
```

---

# Final Success Criteria

The completed system should demonstrate:

- Production-style FastAPI architecture
- Microservice-friendly design
- Strong test coverage
- Durable workflow orchestration
- Temporal integration
- Retry and recovery handling
- Separation of business logic from workflow logic
- Extensible architecture for future AI-powered document processing
  """

---

## Suggestions

- When you start implementing Stage 1, intentionally model ProcessingJob as if a workflow engine will exist later. That means having statuses (pending, running, completed, failed), timestamps, and operation definitions from day one. When you reach Temporal, you'll mostly replace the execution mechanism rather than redesign the data model.
