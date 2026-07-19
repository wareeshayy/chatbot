"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "IJAIKE Chatbot"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    secret_key: str = Field(..., min_length=16)
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # MongoDB
    mongodb_url: str = Field(default="mongodb://localhost:27017")
    mongodb_db_name: str = Field(default="ijaike_chatbot")

    # JWT
    jwt_secret_key: str = Field(..., min_length=16)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # LLM provider: gemini (dev), openai, azure (production), openrouter, groq, grok
    llm_provider: Literal["gemini", "openai", "azure", "openrouter", "groq", "grok"] = "groq"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    gemini_embedding_model: str = "models/text-embedding-004"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"

    # OpenRouter
    openrouter_api_key: str = ""
    openrouter_model: str = "openai/gpt-4o"

    # Groq
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # Grok
    grok_api_key: str = Field(default="", validation_alias=AliasChoices("grok_api_key", "xai_api_key"))
    grok_model: str = "grok-2"

    # Azure OpenAI (production)
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = "gpt-4o-mini"
    azure_openai_embedding_deployment: str = "text-embedding-3-small"
    azure_openai_api_version: str = "2024-02-15-preview"

    # Embeddings fallback
    embedding_provider: Literal["gemini", "openai", "sentence_transformer"] = "gemini"
    sentence_transformer_model: str = "all-MiniLM-L6-v2"

    # Vector store: chroma (local) or mongodb (Atlas Vector Search for production)
    vector_store: Literal["chroma", "mongodb"] = "chroma"

    # ChromaDB
    chroma_persist_dir: str = str(Path(__file__).resolve().parents[2] / "data" / "chroma")
    chroma_collection_name: str = "ijaike_kb"

    # Storage
    storage_backend: Literal["local", "azure", "s3"] = "local"
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 50

    # RAG
    rag_top_k: int = 5
    rag_score_threshold: float = 0.3
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # Logging
    log_level: str = "INFO"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str) -> str:
        return value

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
