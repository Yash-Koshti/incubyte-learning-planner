import uuid

import app.temporal.activities as activities_module
import pytest
from app.temporal.activities import (
    extract_keywords,
    extract_text,
    generate_summary,
    mark_job_failed,
    mark_job_running,
    store_results,
)
from app.temporal.workflows import DocumentProcessingWorkflow, ProcessDocumentInput
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from tests.conftest import TestSessionFactory


@pytest.fixture(autouse=True)
def patch_session_factory():
    import unittest.mock as mock

    with mock.patch.object(
        activities_module, "AsyncSessionFactory", TestSessionFactory
    ):
        yield


async def test_full_workflow_completes(db_session):
    from app.models.processing_job import JobStatus
    from app.repositories.document_repository import DocumentRepository
    from app.repositories.job_repository import JobRepository

    doc_repo = DocumentRepository(db_session)
    job_repo = JobRepository(db_session)

    doc = await doc_repo.create("test.pdf", "Test", None)
    job = await job_repo.create(
        doc.id, ["extract_text", "generate_summary", "extract_keywords"]
    )

    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[DocumentProcessingWorkflow],
            activities=[
                mark_job_running,
                mark_job_failed,
                extract_text,
                generate_summary,
                extract_keywords,
                store_results,
            ],
        ):
            await env.client.execute_workflow(
                DocumentProcessingWorkflow.run,
                ProcessDocumentInput(
                    job_id=str(job.id),
                    document_id=str(doc.id),
                    operations=["extract_text", "generate_summary", "extract_keywords"],
                ),
                id=f"test-{uuid.uuid4()}",
                task_queue="test-queue",
            )

    await db_session.refresh(job)
    assert str(job.status) == JobStatus.completed

    result = await job_repo.get_result(job.id)
    assert result is not None
    assert result.extracted_text is not None
    assert result.summary is not None
    assert isinstance(result.keywords, list)
