import logging
import uuid
from dataclasses import dataclass

from temporalio import activity

from app.core.database import AsyncSessionFactory
from app.models.processing_job import JobStatus
from app.repositories.job_repository import JobRepository

logger = logging.getLogger(__name__)


@dataclass
class MarkJobInput:
    job_id: str


@dataclass
class ExtractTextInput:
    document_id: str


@dataclass
class ExtractTextOutput:
    text: str


@dataclass
class GenerateSummaryInput:
    text: str


@dataclass
class GenerateSummaryOutput:
    summary: str


@dataclass
class ExtractKeywordsInput:
    text: str


@dataclass
class ExtractKeywordsOutput:
    keywords: list[str]


@dataclass
class StoreResultsInput:
    job_id: str
    extracted_text: str
    summary: str
    keywords: list[str]


@activity.defn
async def mark_job_running(input: MarkJobInput) -> None:
    async with AsyncSessionFactory() as session:
        repo = JobRepository(session)
        job = await repo.get_by_id(uuid.UUID(input.job_id))
        if job:
            await repo.update_status(job, JobStatus.running)
    logger.info("job marked running", extra={"job_id": input.job_id})


@activity.defn
async def mark_job_failed(input: MarkJobInput) -> None:
    async with AsyncSessionFactory() as session:
        repo = JobRepository(session)
        job = await repo.get_by_id(uuid.UUID(input.job_id))
        if job:
            await repo.update_status(job, JobStatus.failed)
    logger.info("job marked failed", extra={"job_id": input.job_id})


@activity.defn
async def extract_text(input: ExtractTextInput) -> ExtractTextOutput:
    import asyncio

    await asyncio.sleep(0.1)
    text = f"Extracted text content from document {input.document_id}."
    logger.info("text extracted", extra={"document_id": input.document_id})
    return ExtractTextOutput(text=text)


@activity.defn
async def generate_summary(input: GenerateSummaryInput) -> GenerateSummaryOutput:
    import asyncio

    await asyncio.sleep(0.1)
    summary = f"Summary: {input.text[:60]}..."
    return GenerateSummaryOutput(summary=summary)


@activity.defn
async def extract_keywords(input: ExtractKeywordsInput) -> ExtractKeywordsOutput:
    import asyncio

    await asyncio.sleep(0.1)
    words = [w.lower() for w in input.text.split() if len(w) > 4]
    keywords = list(dict.fromkeys(words))[:10]
    return ExtractKeywordsOutput(keywords=keywords)


@activity.defn
async def store_results(input: StoreResultsInput) -> None:
    async with AsyncSessionFactory() as session:
        repo = JobRepository(session)
        job = await repo.get_by_id(uuid.UUID(input.job_id))
        if job:
            await repo.save_result(
                job,
                input.extracted_text,
                input.summary,
                input.keywords,
            )
    logger.info("results stored", extra={"job_id": input.job_id})
