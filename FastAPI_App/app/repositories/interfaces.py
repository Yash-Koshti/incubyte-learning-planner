import uuid
from typing import Protocol

from app.models.document import Document, DocumentStatus
from app.models.processing_job import JobStatus, ProcessingJob
from app.models.processing_result import ProcessingResult


class IDocumentRepository(Protocol):
    async def create(
        self, filename: str, title: str | None, description: str | None
    ) -> Document: ...

    async def get_by_id(self, document_id: uuid.UUID) -> Document | None: ...

    async def list(
        self, page: int, page_size: int, status: DocumentStatus | None
    ) -> tuple[list[Document], int]: ...

    async def delete(self, document: Document) -> None: ...


class IJobRepository(Protocol):
    async def create(
        self, document_id: uuid.UUID, operations: list[str]
    ) -> ProcessingJob: ...

    async def get_by_id(self, job_id: uuid.UUID) -> ProcessingJob | None: ...

    async def get_result(self, job_id: uuid.UUID) -> ProcessingResult | None: ...

    async def update_status(
        self, job: ProcessingJob, status: JobStatus
    ) -> ProcessingJob: ...

    async def save_result(
        self,
        job: ProcessingJob,
        extracted_text: str,
        summary: str,
        keywords: list[str],
    ) -> ProcessingJob: ...
