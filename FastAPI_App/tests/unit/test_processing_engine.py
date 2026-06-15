import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.models.processing_job import JobStatus
from app.services.processing_engine import run_job


def make_repo():
    repo = MagicMock()
    repo.get_by_id = AsyncMock()
    repo.update_status = AsyncMock()
    repo.save_result = AsyncMock()
    return repo


async def test_run_job_completes_successfully():
    repo = make_repo()
    fake_job = MagicMock()
    fake_job.status = JobStatus.pending
    repo.get_by_id.return_value = fake_job

    doc_id = uuid.uuid4()
    job_id = uuid.uuid4()

    with patch("app.services.processing_engine.AsyncSessionFactory") as mock_factory:
        mock_session = AsyncMock()
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        with patch("app.services.processing_engine.JobRepository", return_value=repo):
            await run_job(
                job_id, doc_id, ["extract_text", "generate_summary", "extract_keywords"]
            )

    repo.update_status.assert_any_await(fake_job, JobStatus.running)
    repo.save_result.assert_awaited_once()


async def test_run_job_skips_when_job_not_found():
    repo = make_repo()
    repo.get_by_id.return_value = None

    doc_id = uuid.uuid4()
    job_id = uuid.uuid4()

    with patch("app.services.processing_engine.AsyncSessionFactory") as mock_factory:
        mock_session = AsyncMock()
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        with patch("app.services.processing_engine.JobRepository", return_value=repo):
            await run_job(job_id, doc_id, ["extract_text"])

    repo.update_status.assert_not_awaited()
    repo.save_result.assert_not_awaited()


async def test_run_job_marks_failed_on_exception():
    repo = make_repo()
    fake_job = MagicMock()
    fake_job.status = JobStatus.pending
    repo.get_by_id.return_value = fake_job
    repo.save_result.side_effect = Exception("DB error")

    doc_id = uuid.uuid4()
    job_id = uuid.uuid4()

    with patch("app.services.processing_engine.AsyncSessionFactory") as mock_factory:
        mock_session = AsyncMock()
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        with patch("app.services.processing_engine.JobRepository", return_value=repo):
            with pytest.raises(Exception, match="DB error"):
                await run_job(job_id, doc_id, ["extract_text"])

    repo.update_status.assert_any_await(fake_job, JobStatus.failed)
