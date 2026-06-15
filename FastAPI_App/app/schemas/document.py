import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.document import DocumentStatus


class DocumentUploadRequest(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Q4 Contract",
                "description": "Vendor agreement for Q4",
            }
        }
    }


class DocumentResponse(BaseModel):
    id: uuid.UUID
    filename: str
    title: str | None
    description: str | None
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "filename": "contract.pdf",
                "title": "Q4 Contract",
                "description": "Vendor agreement",
                "status": "uploaded",
                "created_at": "2026-01-01T10:00:00Z",
                "updated_at": "2026-01-01T10:00:00Z",
            }
        },
    }


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int
    page: int
    page_size: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "items": [
                    {
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "filename": "contract.pdf",
                        "title": "Q4 Contract",
                        "description": "Vendor agreement",
                        "status": "uploaded",
                        "created_at": "2026-01-01T10:00:00Z",
                        "updated_at": "2026-01-01T10:00:00Z",
                    }
                ],
                "total": 1,
                "page": 1,
                "page_size": 20,
            }
        }
    }
