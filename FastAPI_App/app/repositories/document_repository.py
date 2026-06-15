import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentStatus


class DocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self, filename: str, title: str | None, description: str | None
    ) -> Document:
        document = Document(filename=filename, title=title, description=description)
        self.session.add(document)
        await self.session.commit()
        await self.session.refresh(document)
        return document

    async def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        result = await self.session.execute(
            select(Document).where(Document.id == document_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        page: int,
        page_size: int,
        status: DocumentStatus | None,
    ) -> tuple[list[Document], int]:
        query = select(Document)
        count_query = select(func.count(Document.id))

        if status:
            query = query.where(Document.status == status)
            count_query = count_query.where(Document.status == status)

        query = query.offset((page - 1) * page_size).limit(page_size)

        documents = (await self.session.execute(query)).scalars().all()
        total = (await self.session.execute(count_query)).scalar_one()
        return list(documents), total

    async def delete(self, document: Document) -> None:
        await self.session.delete(document)
        await self.session.commit()
