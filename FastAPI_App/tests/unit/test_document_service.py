import uuid

import pytest
from app.core.errors import (
    DocumentNotFoundError,
    InvalidTitleError,
    UnsupportedFileTypeError,
)
from app.models.document import DocumentStatus
from app.services.document_service import DocumentService

from tests.fakes.fake_document_repository import FakeDocumentRepository


def make_service() -> tuple[DocumentService, FakeDocumentRepository]:
    repo = FakeDocumentRepository()
    return DocumentService(repo), repo


async def test_upload_rejects_unsupported_extension():
    service, _ = make_service()
    with pytest.raises(UnsupportedFileTypeError):
        await service.upload("malware.exe", None, None)


async def test_upload_rejects_whitespace_title():
    service, _ = make_service()
    with pytest.raises(InvalidTitleError):
        await service.upload("report.pdf", "   ", None)


async def test_upload_accepts_valid_extensions():
    service, _ = make_service()
    for ext in ["pdf", "txt", "docx", "png", "jpg"]:
        doc = await service.upload(f"file.{ext}", None, None)
        assert doc.filename == f"file.{ext}"


async def test_upload_stores_document_with_correct_fields():
    service, repo = make_service()
    doc = await service.upload("report.pdf", "Q4 Report", "Annual summary")
    assert doc.filename == "report.pdf"
    assert doc.title == "Q4 Report"
    assert doc.description == "Annual summary"
    assert doc.status == DocumentStatus.uploaded
    assert await repo.get_by_id(doc.id) is doc


async def test_get_raises_not_found_when_missing():
    service, _ = make_service()
    with pytest.raises(DocumentNotFoundError):
        await service.get(uuid.uuid4())


async def test_get_returns_document_when_found():
    service, _ = make_service()
    created = await service.upload("report.pdf", None, None)
    fetched = await service.get(created.id)
    assert fetched is created


async def test_delete_raises_not_found_when_missing():
    service, _ = make_service()
    with pytest.raises(DocumentNotFoundError):
        await service.delete(uuid.uuid4())


async def test_delete_removes_document_from_store():
    service, repo = make_service()
    doc = await service.upload("report.pdf", None, None)
    await service.delete(doc.id)
    assert await repo.get_by_id(doc.id) is None
