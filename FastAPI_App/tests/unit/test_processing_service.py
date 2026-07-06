import uuid

import pytest
from app.core.errors import (
    DocumentNotFoundError,
    JobNotCompletedError,
    JobNotFoundError,
    UnsupportedOperationError,
)
from app.models.processing_job import JobStatus
from app.services.processing_service import ProcessingService

from tests.fakes.fake_document_repository import FakeDocumentRepository
from tests.fakes.fake_job_repository import FakeJobRepository


def make_service() -> tuple[
    ProcessingService, FakeJobRepository, FakeDocumentRepository
]:
    doc_repo = FakeDocumentRepository()
    job_repo = FakeJobRepository()
    return ProcessingService(job_repo, doc_repo), job_repo, doc_repo


async def test_create_job_raises_when_document_missing():
    service, _, _ = make_service()
    with pytest.raises(DocumentNotFoundError):
        await service.create_job(uuid.uuid4(), ["extract_text"])


async def test_create_job_raises_on_invalid_operation():
    service, _, doc_repo = make_service()
    doc = await doc_repo.create("test.pdf", None, None)
    with pytest.raises(UnsupportedOperationError):
        await service.create_job(doc.id, ["invalid_op"])


async def test_create_job_stores_job_with_pending_status():
    service, job_repo, doc_repo = make_service()
    doc = await doc_repo.create("test.pdf", None, None)
    job = await service.create_job(doc.id, ["extract_text"])
    assert job.document_id == doc.id
    assert job.status == JobStatus.pending
    assert job.operations == ["extract_text"]
    assert await job_repo.get_by_id(job.id) is job


async def test_get_job_raises_when_missing():
    service, _, _ = make_service()
    with pytest.raises(JobNotFoundError):
        await service.get_job(uuid.uuid4())


async def test_get_job_returns_job_when_found():
    service, job_repo, doc_repo = make_service()
    doc = await doc_repo.create("test.pdf", None, None)
    created = await job_repo.create(doc.id, ["extract_text"])
    fetched = await service.get_job(created.id)
    assert fetched is created


async def test_get_job_result_raises_when_not_completed():
    service, job_repo, doc_repo = make_service()
    doc = await doc_repo.create("test.pdf", None, None)
    job = await job_repo.create(doc.id, ["extract_text"])
    with pytest.raises(JobNotCompletedError):
        await service.get_job_result(job.id)


async def test_get_job_result_returns_result_when_completed():
    service, job_repo, doc_repo = make_service()
    doc = await doc_repo.create("test.pdf", None, None)
    job = await job_repo.create(doc.id, ["extract_text"])
    await job_repo.save_result(job, "extracted text", "a summary", ["kw1", "kw2"])
    result = await service.get_job_result(job.id)
    assert result.extracted_text == "extracted text"
    assert result.summary == "a summary"
    assert result.keywords == ["kw1", "kw2"]
