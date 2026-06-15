import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.processing_job import JobStatus

VALID_OPERATIONS = {"extract_text", "generate_summary", "extract_keywords"}


class CreateJobRequest(BaseModel):
    operations: list[str] = Field(min_length=1)


class JobResponse(BaseModel):
    job_id: uuid.UUID
    status: JobStatus
    created_at: datetime
    completed_at: datetime | None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "job_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                "status": "completed",
                "created_at": "2026-01-01T10:00:00Z",
                "completed_at": "2026-01-01T10:00:01Z",
            }
        },
    }


class ProcessingResultResponse(BaseModel):
    summary: str | None
    keywords: list[str] | None
    extracted_text: str | None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "extracted_text": "This agreement is entered into as of January 1, 2026...",
                "summary": "Summary: This agreement is entered into as of January...",
                "keywords": ["agreement", "entered", "january", "vendor"],
            }
        },
    }
