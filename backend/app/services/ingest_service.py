"""Document ingestion — parse, chunk, embed, index in ChromaDB."""

from datetime import datetime, timezone
from uuid import UUID

from app.config.logging_config import get_logger
from app.config.settings import get_settings
from app.database.repositories.document_repo import DocumentChunkRepository, DocumentRepository
from app.embeddings.factory import embed_texts
from app.models.document import DocumentChunk
from app.models.enums import DocumentStatus
from app.storage.local_storage import get_storage_backend
from app.utils.exceptions import NotFoundError
from app.vectorstore.chroma_store import ChromaStore

logger = get_logger(__name__)
settings = get_settings()


class IngestService:
    def __init__(self) -> None:
        self.document_repo = DocumentRepository()
        self.chunk_repo = DocumentChunkRepository()
        self.storage = get_storage_backend()
        self.chroma = ChromaStore.get_instance()

    async def process_document(self, document_id: UUID) -> None:
        document = await self.document_repo.get_by_id(document_id)
        if not document:
            raise NotFoundError("Document", document_id)

        document.status = DocumentStatus.PROCESSING
        document.error_message = None
        await document.save()

        try:
            file_path = await self.storage.get_absolute_path(document.file_path)
            pages = await self._parse_document(file_path, document.file_type)
            chunks = self._chunk_pages(pages, settings.chunk_size, settings.chunk_overlap)

            await self.chunk_repo.delete_by_document(document.id)
            self.chroma.delete_by_document(str(document.id))

            if not chunks:
                raise ValueError("No text content extracted from document")

            chroma_ids: list[str] = []
            chroma_texts: list[str] = []
            chroma_metas: list[dict] = []

            for index, chunk_data in enumerate(chunks):
                chroma_id = f"{document.id}_{index}"
                chunk = DocumentChunk(
                    document_id=document.id,
                    chroma_id=chroma_id,
                    chunk_index=index,
                    content=chunk_data["content"],
                    page_number=chunk_data.get("page_number"),
                    section_title=chunk_data.get("section_title"),
                    token_count=len(chunk_data["content"].split()),
                )
                await self.chunk_repo.create(chunk)

                chroma_ids.append(chroma_id)
                chroma_texts.append(chunk_data["content"])
                chroma_metas.append({
                    "document_id": str(document.id),
                    "document_title": document.title,
                    "category": document.category.value,
                    "page_number": chunk_data.get("page_number") or 0,
                    "section_title": chunk_data.get("section_title") or "",
                    "chunk_index": index,
                })

            embeddings = embed_texts(chroma_texts)
            self.chroma.add_chunks(chroma_ids, embeddings, chroma_texts, chroma_metas)

            document.chunk_count = len(chunks)
            document.status = DocumentStatus.INDEXED
            document.indexed_at = datetime.now(timezone.utc)
            await document.save()

            logger.info("Indexed document %s: %d chunks in ChromaDB", document.id, len(chunks))

        except Exception as exc:
            logger.exception("Failed to ingest document %s", document.id)
            document.status = DocumentStatus.FAILED
            document.error_message = str(exc)[:1000]
            await document.save()
            raise

    async def _parse_document(self, file_path, file_type: str) -> list[dict]:
        if file_type == "pdf":
            return await self._parse_pdf(file_path)
        if file_type == "docx":
            return await self._parse_docx(file_path)
        if file_type == "txt":
            return await self._parse_txt(file_path)
        raise ValueError(f"Unsupported file type: {file_type}")

    async def _parse_pdf(self, file_path) -> list[dict]:
        import fitz

        pages = []
        with fitz.open(file_path) as doc:
            for page_num, page in enumerate(doc, start=1):
                text = page.get_text("text").strip()
                if text:
                    pages.append({"page_number": page_num, "content": text})
        return pages

    async def _parse_docx(self, file_path) -> list[dict]:
        from docx import Document as DocxDocument

        doc = DocxDocument(file_path)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        content = "\n\n".join(paragraphs)
        return [{"page_number": 1, "content": content}] if content else []

    async def _parse_txt(self, file_path) -> list[dict]:
        import aiofiles

        async with aiofiles.open(file_path, encoding="utf-8", errors="ignore") as f:
            content = (await f.read()).strip()
        return [{"page_number": 1, "content": content}] if content else []

    def _chunk_pages(
        self,
        pages: list[dict],
        chunk_size: int = 1000,
        overlap: int = 200,
    ) -> list[dict]:
        if not pages:
            return []

        chunks: list[dict] = []
        for page in pages:
            text = page["content"]
            page_number = page.get("page_number")
            start = 0
            while start < len(text):
                end = start + chunk_size
                chunk_text = text[start:end].strip()
                if chunk_text:
                    chunks.append({
                        "content": chunk_text,
                        "page_number": page_number,
                        "section_title": None,
                    })
                if end >= len(text):
                    break
                start = end - overlap
        return chunks
