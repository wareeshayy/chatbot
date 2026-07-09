"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1 import admin, apc, auth, chat, documents, faqs, health, notifications, users

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(chat.router)
api_router.include_router(documents.router)
api_router.include_router(apc.router)
api_router.include_router(faqs.router)
api_router.include_router(notifications.router)
api_router.include_router(users.router)
api_router.include_router(admin.router)
api_router.include_router(health.router)
