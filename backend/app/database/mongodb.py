"""MongoDB connection and Beanie ODM initialization."""

import certifi
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.config.settings import get_settings
from app.models import ALL_DOCUMENT_MODELS

settings = get_settings()
_client: AsyncIOMotorClient | None = None


def _mongo_client_kwargs() -> dict:
    url = settings.mongodb_url
    if url.startswith("mongodb+srv://"):
        return {"tlsCAFile": certifi.where()}
    return {}


async def connect_to_mongo() -> None:
    global _client
    _client = AsyncIOMotorClient(
        settings.mongodb_url,
        serverSelectionTimeoutMS=8000,
        connectTimeoutMS=8000,
        **_mongo_client_kwargs(),
    )
    await init_beanie(
        database=_client[settings.mongodb_db_name],
        document_models=ALL_DOCUMENT_MODELS,
    )


async def close_mongo_connection() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None


async def ping_mongo() -> bool:
    if _client is None:
        return False
    await _client.admin.command("ping")
    return True
