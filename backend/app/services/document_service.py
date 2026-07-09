"""Document upload and management service."""

from typing import Any
from uuid import UUID, uuid4

from fastapi import UploadFile

from app.config.settings import get_settings
from app.database.repositories.document_repo import DocumentRepository
from app.models.document import Document
from app.models.enums import DocumentCategory, DocumentStatus
from app.models.user import User
from app.schemas.document import DocumentUpdateRequest
from app.services.ingest_service import IngestService
from app.storage.local_storage import get_storage_backend
from app.utils.exceptions import NotFoundError
from app.utils.file_validation import validate_file_size, validate_upload_file
from app.utils.pagination import ServicePage

settings = get_settings()


class DocumentService:
    def __init__(self) -> None:
        self.document_repo = DocumentRepository()
        self.storage = get_storage_backend()
        self.ingest_service = IngestService()

    async def upload_document(
        self,
        file: UploadFile,
        title: str,
        category: DocumentCategory,
        admin: User,
        metadata: dict[str, Any] | None = None,
    ) -> Document:
        file_type = validate_upload_file(file, settings)
        file_size = await validate_file_size(file, settings)

        doc_id = uuid4()
        storage_path = f"{category.value}/{doc_id}/{file.filename}"

        await self.storage.save(file, storage_path)

        document = Document(
            id=doc_id,
            title=title,
            filename=file.filename or "unknown",
            file_path=storage_path,
            file_type=file_type,
            file_size_bytes=file_size,
            category=category,
            status=DocumentStatus.PENDING,
            doc_metadata=metadata,
            uploaded_by=admin.id,
        )
        document = await self.document_repo.create(document)
        await self.ingest_service.process_document(document.id)
        return await self.document_repo.get_by_id(document.id)  # type: ignore[return-value]

    async def list_documents(
        self,
        page: int = 1,
        page_size: int = 20,
        category: DocumentCategory | None = None,
        status: DocumentStatus | None = None,
    ) -> ServicePage[Document]:
        offset = (page - 1) * page_size
        docs, total = await self.document_repo.list_documents(
            offset, page_size, category, status
        )
        return ServicePage.create(docs, total, page, page_size)

    async def get_document(self, document_id: UUID, with_chunks: bool = False) -> Document:
        if with_chunks:
            document = await self.document_repo.get_with_chunks(document_id)
        else:
            document = await self.document_repo.get_by_id(document_id)

        if not document or not document.is_active:
            raise NotFoundError("Document", document_id)
        return document

    async def update_document(self, document_id: UUID, data: DocumentUpdateRequest) -> Document:
        document = await self.get_document(document_id)

        if data.title is not None:
            document.title = data.title
        if data.category is not None:
            document.category = data.category
        if data.metadata is not None:
            document.doc_metadata = data.metadata

        await document.save()
        return document

    async def delete_document(self, document_id: UUID) -> None:
        document = await self.get_document(document_id)
        document.is_active = False
        await document.save()

        if await self.storage.exists(document.file_path):
            await self.storage.delete(document.file_path)

    async def reindex_document(self, document_id: UUID) -> Document:
        document = await self.get_document(document_id)
        document.status = DocumentStatus.PENDING
        document.error_message = None
        await document.save()
        await self.ingest_service.process_document(document.id)
        refreshed = await self.document_repo.get_by_id(document.id)
        return refreshed  # type: ignore[return-value]

    def get_categories(self) -> list[dict]:
        return [
            {"value": cat.value, "label": cat.value.replace("_", " ").title()}
            for cat in DocumentCategory
        ]
