import uuid
from datetime import datetime, timezone

from app.models.processing_job import JobStatus, ProcessingJob
from app.models.processing_result import ProcessingResult
from app.repositories.interfaces import IJobRepository


class FakeJobRepository(IJobRepository):
    def __init__(self) -> None:
        self._jobs: dict[uuid.UUID, ProcessingJob] = {}
        self._results: dict[uuid.UUID, ProcessingResult] = {}  # keyed by job_id

    async def create(
        self, document_id: uuid.UUID, operations: list[str]
    ) -> ProcessingJob:
        job = ProcessingJob(
            id=uuid.uuid4(),
            document_id=document_id,
            status=JobStatus.pending,
            operations=operations,
            created_at=datetime.now(timezone.utc),
        )
        self._jobs[job.id] = job
        return job

    async def get_by_id(self, job_id: uuid.UUID) -> ProcessingJob | None:
        return self._jobs.get(job_id)

    async def get_result(self, job_id: uuid.UUID) -> ProcessingResult | None:
        return self._results.get(job_id)

    async def update_status(
        self, job: ProcessingJob, status: JobStatus
    ) -> ProcessingJob:
        job.status = status
        return job

    async def save_result(
        self,
        job: ProcessingJob,
        extracted_text: str,
        summary: str,
        keywords: list[str],
    ) -> ProcessingJob:
        result = ProcessingResult(
            id=uuid.uuid4(),
            job_id=job.id,
            extracted_text=extracted_text,
            summary=summary,
            keywords=keywords,
        )
        job.status = JobStatus.completed
        job.completed_at = datetime.now(timezone.utc)
        self._results[job.id] = result
        return job
