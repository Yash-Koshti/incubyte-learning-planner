import uuid

from app.core.errors import (
    DocumentNotFoundError,
    InvalidTitleError,
    UnsupportedFileTypeError,
)
from app.models.document import Document, DocumentStatus
from app.repositories.interfaces import IDocumentRepository

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx", ".png", ".jpg"}


class DocumentService:
    def __init__(self, repository: IDocumentRepository) -> None:
        self.repository = repository

    async def upload(
        self, filename: str, title: str | None, description: str | None
    ) -> Document:
        suffix = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if suffix not in ALLOWED_EXTENSIONS:
            raise UnsupportedFileTypeError(suffix)
        if title is not None and not title.strip():
            raise InvalidTitleError()
        return await self.repository.create(filename, title, description)

    async def get(self, document_id: uuid.UUID) -> Document:
        document = await self.repository.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(document_id)
        return document

    async def list(
        self, page: int, page_size: int, status: DocumentStatus | None
    ) -> tuple[list[Document], int]:
        return await self.repository.list(page, page_size, status)

    async def delete(self, document_id: uuid.UUID) -> None:
        document = await self.get(document_id)
        await self.repository.delete(document)
