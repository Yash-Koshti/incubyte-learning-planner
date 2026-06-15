import uuid

from fastapi import APIRouter, BackgroundTasks, Body, Depends, status

from app.dependencies.services import get_processing_service
from app.schemas.processing_job import (
    CreateJobRequest,
    JobResponse,
    ProcessingResultResponse,
)
from app.services.processing_engine import run_job
from app.services.processing_service import ProcessingService

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
    background_tasks: BackgroundTasks = BackgroundTasks(),
    service: ProcessingService = Depends(get_processing_service),
) -> JobResponse:
    job = await service.create_job(document_id, request.operations)

    background_tasks.add_task(run_job, job.id, document_id, request.operations)

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
