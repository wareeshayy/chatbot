"""Health check routes."""

from fastapi import APIRouter

from app.database.mongodb import ping_mongo

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check() -> dict:
    return {"status": "healthy", "service": "ijaike-chatbot-api", "database": "mongodb"}


@router.get("/health/ready")
async def readiness_check() -> dict:
    if await ping_mongo():
        return {"status": "ready", "database": "connected"}
    return {"status": "not_ready", "database": "disconnected"}
