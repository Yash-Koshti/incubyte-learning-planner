import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker

from app.core.config import settings
from app.core.logging import configure_logging
from app.temporal.activities import (
    extract_keywords,
    extract_text,
    generate_summary,
    mark_job_failed,
    mark_job_running,
    store_results,
)
from app.temporal.workflows import DocumentProcessingWorkflow

logger = logging.getLogger(__name__)

TASK_QUEUE = "document-processing"


async def run_worker() -> None:
    configure_logging()
    client = await Client.connect(settings.temporal_host)
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[DocumentProcessingWorkflow],
        activities=[
            mark_job_running,
            mark_job_failed,
            extract_text,
            generate_summary,
            extract_keywords,
            store_results,
        ],
    )
    logger.info("worker started", extra={"task_queue": TASK_QUEUE})
    await worker.run()


if __name__ == "__main__":
    asyncio.run(run_worker())
