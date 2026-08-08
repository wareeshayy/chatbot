"""FAISS (Facebook AI Similarity Search) in-memory vector store for RAG."""

import os
import pickle
import logging
from pathlib import Path
from typing import Any

import numpy as np
from app.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class FAISSStore:
    _instance: "FAISSStore | None" = None

    def __init__(self) -> None:
        import faiss

        self.faiss = faiss
        self.persist_dir = Path(settings.faiss_persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self.index_path = self.persist_dir / "index.faiss"
        self.store_path = self.persist_dir / "store.pkl"

        self.index: Any = None
        self.dimension: int | None = None
        # Data storage mapping index position (int) -> dict item
        # item format: {"id": str, "document": str, "metadata": dict, "embedding": list[float]}
        self.items: list[dict[str, Any]] = []

        self._load()

    @classmethod
    def get_instance(cls) -> "FAISSStore":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load(self) -> None:
        if self.index_path.exists() and self.store_path.exists():
            try:
                self.index = self.faiss.read_index(str(self.index_path))
                with open(self.store_path, "rb") as f:
                    store_data = pickle.load(f)
                    self.items = store_data.get("items", [])
                    self.dimension = store_data.get("dimension")
                logger.info("Loaded FAISS index with %d items from %s", len(self.items), self.persist_dir)
            except Exception as e:
                logger.error("Failed to load FAISS store from disk: %s. Creating new index.", e)
                self.index = None
                self.items = []
                self.dimension = None

    def _save(self) -> None:
        if self.index is not None:
            self.faiss.write_index(self.index, str(self.index_path))
            with open(self.store_path, "wb") as f:
                pickle.dump(
                    {
                        "items": self.items,
                        "dimension": self.dimension,
                    },
                    f,
                )
            logger.info("Saved FAISS index with %d items to %s", len(self.items), self.persist_dir)

    def _initialize_index(self, dimension: int) -> None:
        self.dimension = dimension
        # Inner Product index on L2-normalized vectors = Cosine Similarity
        self.index = self.faiss.IndexFlatIP(dimension)

    def _normalize(self, vectors: np.ndarray) -> np.ndarray:
        vectors_copy = np.array(vectors, dtype=np.float32)
        if len(vectors_copy.shape) == 1:
            vectors_copy = vectors_copy.reshape(1, -1)
        self.faiss.normalize_L2(vectors_copy)
        return vectors_copy

    async def add_chunks(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict[str, Any]],
    ) -> None:
        if not ids or not embeddings:
            return

        dim = len(embeddings[0])
        if self.index is None or self.dimension != dim:
            self._initialize_index(dim)

        vecs = np.array(embeddings, dtype=np.float32)
        normalized_vecs = self._normalize(vecs)

        self.index.add(normalized_vecs)

        for chunk_id, doc, meta, emb in zip(ids, documents, metadatas, embeddings):
            self.items.append({
                "id": chunk_id,
                "document": doc,
                "metadata": meta,
                "embedding": emb,
            })

        self._save()

    async def delete_by_document(self, document_id: str) -> None:
        if not self.items:
            return

        remaining_items = [
            item for item in self.items if item.get("metadata", {}).get("document_id") != document_id
        ]

        if len(remaining_items) == len(self.items):
            return

        self.items = remaining_items
        if not self.items:
            self.index = None
            self.dimension = None
            if self.index_path.exists():
                os.remove(self.index_path)
            if self.store_path.exists():
                os.remove(self.store_path)
            return

        dim = len(self.items[0]["embedding"])
        self._initialize_index(dim)

        embeddings = [item["embedding"] for item in self.items]
        vecs = np.array(embeddings, dtype=np.float32)
        normalized_vecs = self._normalize(vecs)
        self.index.add(normalized_vecs)
        self._save()

    async def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> dict[str, Any]:
        if self.index is None or not self.items:
            return {
                "ids": [[]],
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]],
                "embeddings": [[]],
            }

        q_vec = np.array([query_embedding], dtype=np.float32)
        normalized_q = self._normalize(q_vec)

        k = min(top_k, len(self.items))
        scores, indices = self.index.search(normalized_q, k)

        res_ids: list[str] = []
        res_docs: list[str] = []
        res_metas: list[dict[str, Any]] = []
        res_distances: list[float] = []
        res_embeddings: list[list[float]] = []

        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.items):
                continue
            item = self.items[idx]
            res_ids.append(item["id"])
            res_docs.append(item["document"])
            res_metas.append(item["metadata"])
            # Cosine similarity range [-1, 1], distance = 1.0 - similarity
            res_distances.append(max(0.0, 1.0 - float(score)))
            res_embeddings.append(item["embedding"])

        return {
            "ids": [res_ids],
            "documents": [res_docs],
            "metadatas": [res_metas],
            "distances": [res_distances],
            "embeddings": [res_embeddings],
        }

    async def count(self) -> int:
        return len(self.items)
