import uuid

from fastapi import APIRouter, Body, Depends, status
from temporalio.client import Client

from app.dependencies.services import get_processing_service
from app.dependencies.temporal import get_temporal_client
from app.schemas.processing_job import (
    CreateJobRequest,
    JobResponse,
    ProcessingResultResponse,
)
from app.services.processing_service import ProcessingService
from app.temporal.worker import TASK_QUEUE
from app.temporal.workflows import DocumentProcessingWorkflow, ProcessDocumentInput

router = APIRouter(tags=["jobs"])


@router.post(
    "/documents/{document_id}/process",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_processing_job(
    document_id: uuid.UUID,
    request: CreateJobRequest = Body(
        examples=[
            {
                "all_operations": {
                    "summary": "All operations",
                    "value": {
                        "operations": [
                            "extract_text",
                            "generate_summary",
                            "extract_keywords",
                        ]
                    },
                },
                "text_only": {
                    "summary": "Text extraction only",
                    "value": {"operations": ["extract_text"]},
                },
            }
        ]
    ),
    service: ProcessingService = Depends(get_processing_service),
    temporal_client: Client = Depends(get_temporal_client),
) -> JobResponse:
    job = await service.create_job(document_id, request.operations)

    await temporal_client.start_workflow(
        DocumentProcessingWorkflow.run,
        ProcessDocumentInput(
            job_id=str(job.id),
            document_id=str(document_id),
            operations=request.operations,
        ),
        id=f"doc-processing-{job.id}",
        task_queue=TASK_QUEUE,
    )

    return JobResponse(
        job_id=job.id,
        status=job.status,
        created_at=job.created_at,
        completed_at=job.completed_at,
    )


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: uuid.UUID,
    service: ProcessingService = Depends(get_processing_service),
) -> JobResponse:
    job = await service.get_job(job_id)
    return JobResponse(
        job_id=job.id,
        status=job.status,
        created_at=job.created_at,
        completed_at=job.completed_at,
    )


@router.get("/jobs/{job_id}/results", response_model=ProcessingResultResponse)
async def get_job_results(
    job_id: uuid.UUID,
    service: ProcessingService = Depends(get_processing_service),
) -> ProcessingResultResponse:
    result = await service.get_job_result(job_id)
    return ProcessingResultResponse.model_validate(result)
