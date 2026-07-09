"""Document repositories."""

from uuid import UUID

from app.models.document import Document, DocumentChunk
from app.models.enums import DocumentCategory, DocumentStatus


class DocumentRepository:
    async def get_by_id(self, entity_id: UUID) -> Document | None:
        return await Document.get(entity_id)

    async def create(self, entity: Document) -> Document:
        await entity.insert()
        return entity

    async def get_with_chunks(self, document_id: UUID) -> Document | None:
        document = await Document.get(document_id)
        if not document or not document.is_active:
            return None
        chunks = (
            await DocumentChunk.find(DocumentChunk.document_id == document_id)
            .sort(+DocumentChunk.chunk_index)
            .to_list()
        )
        document.chunks = chunks
        return document

    async def list_documents(
        self,
        offset: int = 0,
        limit: int = 20,
        category: DocumentCategory | None = None,
        status: DocumentStatus | None = None,
        active_only: bool = True,
    ) -> tuple[list[Document], int]:
        filters = []
        if active_only:
            filters.append(Document.is_active == True)  # noqa: E712
        if category:
            filters.append(Document.category == category)
        if status:
            filters.append(Document.status == status)

        if filters:
            query = Document.find(*filters)
        else:
            query = Document.find_all()

        total = await query.count()
        docs = await query.sort(-Document.created_at).skip(offset).limit(limit).to_list()
        return docs, total

    async def count_by_status(self, status: DocumentStatus) -> int:
        return await Document.find(
            Document.status == status,
            Document.is_active == True,  # noqa: E712
        ).count()


class DocumentChunkRepository:
    async def create(self, entity: DocumentChunk) -> DocumentChunk:
        await entity.insert()
        return entity

    async def delete_by_document(self, document_id: UUID) -> None:
        await DocumentChunk.find(DocumentChunk.document_id == document_id).delete()
