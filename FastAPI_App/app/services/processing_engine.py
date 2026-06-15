import asyncio
import logging
import uuid

from app.core.database import AsyncSessionFactory
from app.models.processing_job import JobStatus
from app.repositories.job_repository import JobRepository

logger = logging.getLogger(__name__)


async def _extract_text(document_id: uuid.UUID) -> str:
    await asyncio.sleep(0.1)
    return f"Extracted text content from document {document_id}."


async def _generate_summary(text: str) -> str:
    await asyncio.sleep(0.1)
    return f"Summary: {text[:60]}..."


async def _extract_keywords(text: str) -> list[str]:
    await asyncio.sleep(0.1)
    words = [w.lower() for w in text.split() if len(w) > 4]
    return list(dict.fromkeys(words))[:10]


async def run_job(
    job_id: uuid.UUID, document_id: uuid.UUID, operations: list[str]
) -> None:
    async with AsyncSessionFactory() as session:
        repository = JobRepository(session)
        job = await repository.get_by_id(job_id)
        if job is None:
            logger.warning("job not found, skipping", extra={"job_id": str(job_id)})
            return

        logger.info(
            "processing started",
            extra={
                "job_id": str(job_id),
                "document_id": str(document_id),
                "operations": operations,
            },
        )
        await repository.update_status(job, JobStatus.running)

        try:
            extracted_text = ""
            summary = ""
            keywords: list[str] = []

            if "extract_text" in operations:
                extracted_text = await _extract_text(document_id)

            if "generate_summary" in operations:
                text_to_summarize = extracted_text or f"Document {document_id}"
                summary = await _generate_summary(text_to_summarize)

            if "extract_keywords" in operations:
                text_for_keywords = extracted_text or f"Document {document_id}"
                keywords = await _extract_keywords(text_for_keywords)

            await repository.save_result(job, extracted_text, summary, keywords)

            logger.info(
                "processing completed",
                extra={"job_id": str(job_id), "document_id": str(document_id)},
            )

        except Exception as exc:
            logger.error(
                "processing failed",
                extra={
                    "job_id": str(job_id),
                    "document_id": str(document_id),
                    "error": str(exc),
                },
            )
            await repository.update_status(job, JobStatus.failed)
            raise
