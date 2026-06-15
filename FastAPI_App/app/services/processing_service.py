import uuid

from app.core.errors import (
    DocumentNotFoundError,
    JobNotCompletedError,
    JobNotFoundError,
    UnsupportedOperationError,
)
from app.models.processing_job import JobStatus, ProcessingJob
from app.models.processing_result import ProcessingResult
from app.repositories.document_repository import DocumentRepository
from app.repositories.job_repository import JobRepository
from app.schemas.processing_job import VALID_OPERATIONS


class ProcessingService:
    def __init__(
        self,
        job_repository: JobRepository,
        document_repository: DocumentRepository,
    ) -> None:
        self.job_repository = job_repository
        self.document_repository = document_repository

    async def create_job(
        self, document_id: uuid.UUID, operations: list[str]
    ) -> ProcessingJob:
        document = await self.document_repository.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(document_id)

        invalid = set(operations) - VALID_OPERATIONS
        if invalid:
            raise UnsupportedOperationError(invalid)

        return await self.job_repository.create(document_id, operations)

    async def get_job(self, job_id: uuid.UUID) -> ProcessingJob:
        job = await self.job_repository.get_by_id(job_id)
        if job is None:
            raise JobNotFoundError(job_id)
        return job

    async def get_job_result(self, job_id: uuid.UUID) -> ProcessingResult:
        job = await self.get_job(job_id)

        if job.status != JobStatus.completed:
            raise JobNotCompletedError(job_id, str(job.status))

        result = await self.job_repository.get_result(job_id)
        if result is None:
            raise JobNotFoundError(job_id)
        return result
