"""Embedding providers — Gemini primary, sentence-transformers fallback (cached)."""

from app.config.logging_config import get_logger
from app.config.settings import get_settings

settings = get_settings()
logger = get_logger(__name__)

_local_model = None


def embed_texts(texts: list[str], *, task_type: str = "retrieval_document") -> list[list[float]]:
    if settings.embedding_provider == "gemini" and settings.gemini_api_key:
        return _embed_gemini(texts, task_type=task_type)
    if settings.embedding_provider == "openai" and settings.openai_api_key:
        return _embed_openai(texts)
    return _embed_local(texts)


def _embed_openai(texts: list[str]) -> list[list[float]]:
    from openai import OpenAI
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.embeddings.create(
        input=texts,
        model=settings.embedding_model or "text-embedding-3-small"
    )
    return [data.embedding for data in response.data]


def embed_query(text: str) -> list[float]:
    return embed_texts([text], task_type="retrieval_query")[0]


def _embed_gemini(texts: list[str], *, task_type: str = "retrieval_document") -> list[list[float]]:
    import google.generativeai as genai

    genai.configure(api_key=settings.gemini_api_key)
    vectors = []
    for text in texts:
        result = genai.embed_content(
            model=settings.gemini_embedding_model,
            content=text,
            task_type=task_type,
        )
        vectors.append(result["embedding"])
    return vectors


def _get_local_model():
    global _local_model
    if _local_model is None:
        logger.info("Loading local embedding model (first request may take 1–2 min)...")
        from sentence_transformers import SentenceTransformer

        _local_model = SentenceTransformer(settings.sentence_transformer_model)
    return _local_model


def _embed_local(texts: list[str]) -> list[list[float]]:
    model = _get_local_model()
    return model.encode(texts, normalize_embeddings=True).tolist()
