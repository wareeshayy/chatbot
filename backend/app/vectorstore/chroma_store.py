"""ChromaDB vector store for RAG."""

from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config.settings import get_settings

settings = get_settings()


class ChromaStore:
    _instance: "ChromaStore | None" = None

    def __init__(self) -> None:
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

    def add_chunks(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict[str, Any]],
    ) -> None:
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def delete_by_document(self, document_id: str) -> None:
        existing = self.collection.get(where={"document_id": document_id})
        if existing and existing["ids"]:
            self.collection.delete(ids=existing["ids"])

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> dict[str, Any]:
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances", "embeddings"],
        )
