import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.core.errors import (
    DocumentNotFoundError,
    JobNotCompletedError,
    JobNotFoundError,
    UnsupportedOperationError,
)
from app.models.processing_job import JobStatus
from app.services.processing_service import ProcessingService


def make_service():
    job_repo = MagicMock()
    job_repo.create = AsyncMock()
    job_repo.get_by_id = AsyncMock()
    job_repo.get_result = AsyncMock()

    doc_repo = MagicMock()
    doc_repo.get_by_id = AsyncMock()

    return ProcessingService(job_repo, doc_repo), job_repo, doc_repo


async def test_create_job_raises_when_document_missing():
    service, _, doc_repo = make_service()
    doc_repo.get_by_id.return_value = None
    with pytest.raises(DocumentNotFoundError):
        await service.create_job(uuid.uuid4(), ["extract_text"])


async def test_create_job_raises_on_invalid_operation():
    service, _, doc_repo = make_service()
    doc_repo.get_by_id.return_value = MagicMock()
    with pytest.raises(UnsupportedOperationError):
        await service.create_job(uuid.uuid4(), ["invalid_op"])


async def test_create_job_succeeds_with_valid_operations():
    service, job_repo, doc_repo = make_service()
    doc_repo.get_by_id.return_value = MagicMock()
    fake_job = MagicMock()
    job_repo.create.return_value = fake_job

    result = await service.create_job(uuid.uuid4(), ["extract_text"])
    assert result is fake_job
    job_repo.create.assert_awaited_once()


async def test_get_job_raises_when_missing():
    service, job_repo, _ = make_service()
    job_repo.get_by_id.return_value = None
    with pytest.raises(JobNotFoundError):
        await service.get_job(uuid.uuid4())


async def test_get_job_result_raises_when_not_completed():
    service, job_repo, _ = make_service()
    fake_job = MagicMock()
    fake_job.status = JobStatus.pending
    job_repo.get_by_id.return_value = fake_job
    with pytest.raises(JobNotCompletedError):
        await service.get_job_result(uuid.uuid4())


async def test_get_job_result_raises_when_result_missing():
    service, job_repo, _ = make_service()
    fake_job = MagicMock()
    fake_job.status = JobStatus.completed
    job_repo.get_by_id.return_value = fake_job
    job_repo.get_result.return_value = None
    with pytest.raises(JobNotFoundError):
        await service.get_job_result(uuid.uuid4())


async def test_get_job_result_returns_result():
    service, job_repo, _ = make_service()
    fake_job = MagicMock()
    fake_job.status = JobStatus.completed
    fake_result = MagicMock()
    job_repo.get_by_id.return_value = fake_job
    job_repo.get_result.return_value = fake_result
    result = await service.get_job_result(uuid.uuid4())
    assert result is fake_result
