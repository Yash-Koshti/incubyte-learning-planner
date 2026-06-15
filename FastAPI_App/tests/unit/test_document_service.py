import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.core.errors import (
    DocumentNotFoundError,
    InvalidTitleError,
    UnsupportedFileTypeError,
)
from app.services.document_service import DocumentService


def make_service():
    repository = MagicMock()
    repository.create = AsyncMock()
    repository.get_by_id = AsyncMock()
    repository.list = AsyncMock()
    repository.delete = AsyncMock()
    return DocumentService(repository), repository


async def test_upload_rejects_unsupported_extension():
    service, _ = make_service()
    with pytest.raises(UnsupportedFileTypeError):
        await service.upload("malware.exe", None, None)


async def test_upload_rejects_whitespace_title():
    service, _ = make_service()
    with pytest.raises(InvalidTitleError):
        await service.upload("report.pdf", "   ", None)


async def test_upload_accepts_valid_extensions():
    service, repo = make_service()
    for ext in ["pdf", "txt", "docx", "png", "jpg"]:
        repo.create.reset_mock()
        await service.upload(f"file.{ext}", None, None)
        repo.create.assert_awaited_once()


async def test_upload_calls_repository_with_correct_args():
    service, repo = make_service()
    await service.upload("report.pdf", "Q4 Report", "Annual")
    repo.create.assert_awaited_once_with("report.pdf", "Q4 Report", "Annual")


async def test_get_raises_not_found_when_missing():
    service, repo = make_service()
    repo.get_by_id.return_value = None
    with pytest.raises(DocumentNotFoundError):
        await service.get(uuid.uuid4())


async def test_get_returns_document_when_found():
    service, repo = make_service()
    fake_doc = MagicMock()
    repo.get_by_id.return_value = fake_doc
    result = await service.get(uuid.uuid4())
    assert result is fake_doc


async def test_delete_raises_not_found_when_missing():
    service, repo = make_service()
    repo.get_by_id.return_value = None
    with pytest.raises(DocumentNotFoundError):
        await service.delete(uuid.uuid4())


async def test_delete_calls_repository():
    service, repo = make_service()
    fake_doc = MagicMock()
    repo.get_by_id.return_value = fake_doc
    await service.delete(uuid.uuid4())
    repo.delete.assert_awaited_once_with(fake_doc)
