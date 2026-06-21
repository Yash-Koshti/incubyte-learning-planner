import uuid
from datetime import datetime, timezone

from app.models.document import Document, DocumentStatus
from app.repositories.interfaces import IDocumentRepository


class FakeDocumentRepository(IDocumentRepository):
    def __init__(self) -> None:
        self._store: dict[uuid.UUID, Document] = {}

    async def create(
        self, filename: str, title: str | None, description: str | None
    ) -> Document:
        now = datetime.now(timezone.utc)
        doc = Document(
            id=uuid.uuid4(),
            filename=filename,
            title=title,
            description=description,
            status=DocumentStatus.uploaded,
            created_at=now,
            updated_at=now,
        )
        self._store[doc.id] = doc
        return doc

    async def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        return self._store.get(document_id)

    async def list(
        self, page: int, page_size: int, status: DocumentStatus | None
    ) -> tuple[list[Document], int]:
        docs = list(self._store.values())
        if status is not None:
            docs = [d for d in docs if d.status == status]
        total = len(docs)
        start = (page - 1) * page_size
        return docs[start : start + page_size], total

    async def delete(self, document: Document) -> None:
        self._store.pop(document.id, None)
