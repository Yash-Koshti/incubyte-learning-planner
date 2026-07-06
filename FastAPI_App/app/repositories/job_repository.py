import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.processing_job import JobStatus, ProcessingJob
from app.models.processing_result import ProcessingResult


class JobRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self, document_id: uuid.UUID, operations: list[str]
    ) -> ProcessingJob:
        job = ProcessingJob(document_id=document_id, operations=operations)
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def get_by_id(self, job_id: uuid.UUID) -> ProcessingJob | None:
        result = await self.session.execute(
            select(ProcessingJob).where(ProcessingJob.id == job_id)
        )
        return result.scalar_one_or_none()

    async def get_result(self, job_id: uuid.UUID) -> ProcessingResult | None:
        result = await self.session.execute(
            select(ProcessingResult).where(ProcessingResult.job_id == job_id)
        )
        return result.scalar_one_or_none()

    async def update_status(
        self, job: ProcessingJob, status: JobStatus
    ) -> ProcessingJob:
        job.status = status
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def save_result(
        self,
        job: ProcessingJob,
        extracted_text: str,
        summary: str,
        keywords: list[str],
    ) -> ProcessingJob:
        from datetime import datetime, timezone

        result = ProcessingResult(
            job_id=job.id,
            extracted_text=extracted_text,
            summary=summary,
            keywords=keywords,
        )
        job.status = JobStatus.completed
        job.completed_at = datetime.now(timezone.utc)
        self.session.add(result)
        await self.session.commit()
        await self.session.refresh(job)
        return job
