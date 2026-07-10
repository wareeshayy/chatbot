"""ChromaDB or MongoDB Atlas vector store for RAG."""

from typing import Any
from app.config.settings import get_settings

settings = get_settings()


class ChromaStore:
    _instance: "ChromaStore | None" = None

    def __init__(self) -> None:
        self.store_type = settings.vector_store
        if self.store_type == "chroma":
            import chromadb
            from chromadb.config import Settings as ChromaSettings

            self.client = chromadb.PersistentClient(
                path=settings.chroma_persist_dir,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            self.collection = self.client.get_or_create_collection(
                name=settings.chroma_collection_name,
                metadata={"hnsw:space": "cosine"},
            )

    @classmethod
    def get_instance(cls) -> "ChromaStore":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def add_chunks(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict[str, Any]],
    ) -> None:
        if self.store_type == "chroma":
            self.collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )
        elif self.store_type == "mongodb":
            from app.models.document import DocumentChunk
            from pymongo import UpdateOne

            operations = []
            for chroma_id, embedding in zip(ids, embeddings):
                operations.append(
                    UpdateOne(
                        {"chroma_id": chroma_id},
                        {"$set": {"embedding": embedding}}
                    )
                )
            if operations:
                await DocumentChunk.get_motor_collection().bulk_write(operations)

    async def delete_by_document(self, document_id: str) -> None:
        if self.store_type == "chroma":
            existing = self.collection.get(where={"document_id": document_id})
            if existing and existing["ids"]:
                self.collection.delete(ids=existing["ids"])
        # For MongoDB, chunk deletion is already handled by repository delete_by_document in ingest_service.py

    async def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> dict[str, Any]:
        if self.store_type == "chroma":
            return self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances", "embeddings"],
            )

        # MongoDB Atlas Vector Search
        from app.models.document import DocumentChunk

        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": max(100, top_k * 10),
                    "limit": top_k
                }
            },
            {
                "$lookup": {
                    "from": "documents",
                    "localField": "document_id",
                    "foreignField": "_id",
                    "as": "doc"
                }
            },
            {
                "$project": {
                    "chroma_id": 1,
                    "content": 1,
                    "page_number": 1,
                    "section_title": 1,
                    "document_id": 1,
                    "score": {"$meta": "vectorSearchScore"},
                    "document_title": {"$arrayElemAt": ["$doc.title", 0]},
                    "category": {"$arrayElemAt": ["$doc.category", 0]}
                }
            }
        ]

        cursor = DocumentChunk.get_motor_collection().aggregate(pipeline)
        rows = await cursor.to_list(length=top_k)

        ids = []
        documents = []
        metadatas = []
        distances = []

        for row in rows:
            ids.append(row["chroma_id"])
            documents.append(row["content"])

            score = row.get("score", 0.0)
            # Map relevance score to distance (cosine distance = 1.0 - similarity)
            distances.append(1.0 - score)

            metadatas.append({
                "document_id": str(row["document_id"]),
                "document_title": row.get("document_title") or "Unknown",
                "category": row.get("category") or "",
                "page_number": row.get("page_number") or 0,
                "section_title": row.get("section_title") or "",
            })

        return {
            "ids": [ids],
            "documents": [documents],
            "metadatas": [metadatas],
            "distances": [distances],
            "embeddings": [None] * len(ids)
        }

    async def count(self) -> int:
        if self.store_type == "chroma":
            return self.collection.count()
        elif self.store_type == "mongodb":
            from app.models.document import DocumentChunk
            return await DocumentChunk.count()
