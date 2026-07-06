from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.db import get_db
from app.repositories.document_repository import DocumentRepository
from app.repositories.job_repository import JobRepository
from app.services.document_service import DocumentService
from app.services.processing_service import ProcessingService


def get_document_service(session: AsyncSession = Depends(get_db)) -> DocumentService:
    return DocumentService(DocumentRepository(session))


def get_processing_service(
    session: AsyncSession = Depends(get_db),
) -> ProcessingService:
    return ProcessingService(JobRepository(session), DocumentRepository(session))
