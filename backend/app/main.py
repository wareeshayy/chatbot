"""IJAIKE Journal AI Chatbot — FastAPI application."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.config.logging_config import setup_logging
from app.config.settings import get_settings
from app.database.mongodb import close_mongo_connection, connect_to_mongo
from app.utils.exceptions import AppException

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    await connect_to_mongo()
    yield
    await close_mongo_connection()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="RAG-powered AI chatbot for the IJAIKE Journal",
        version="1.0.0",
        docs_url="/docs" if settings.debug else "/docs",
        redoc_url="/redoc" if settings.debug else "/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        request_id = request.headers.get("X-Request-ID", "-")
        origin = request.headers.get("origin")
        headers = {}
        if origin:
            headers["Access-Control-Allow-Origin"] = origin
            headers["Access-Control-Allow-Credentials"] = "true"
            headers["Access-Control-Allow-Methods"] = "*"
            headers["Access-Control-Allow-Headers"] = "*"

        return JSONResponse(
            status_code=exc.status_code,
            headers=headers,
            content={
                "detail": exc.message,
                "code": exc.code,
                "request_id": request_id,
                "details": exc.details,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = request.headers.get("X-Request-ID", "-")
        message = str(exc)
        code = "INTERNAL_SERVER_ERROR"
        status_code = 500
        
        # Detect Gemini quota limit error
        if "quota exceeded" in message.lower() or "resource_exhausted" in message.lower() or "429" in message:
            message = "Gemini API quota exceeded (20 requests/day limit on Free Tier). Please try again later or add a paid API key."
            code = "QUOTA_EXCEEDED"
            status_code = 429

        origin = request.headers.get("origin")
        headers = {}
        if origin:
            headers["Access-Control-Allow-Origin"] = origin
            headers["Access-Control-Allow-Credentials"] = "true"
            headers["Access-Control-Allow-Methods"] = "*"
            headers["Access-Control-Allow-Headers"] = "*"

        return JSONResponse(
            status_code=status_code,
            headers=headers,
            content={
                "detail": message,
                "code": code,
                "request_id": request_id,
            },
        )

    app.include_router(api_router)

    @app.get("/")
    async def root() -> dict:
        return {
            "service": settings.app_name,
            "version": "1.0.0",
            "docs": "/docs",
            "api": "/api/v1",
            "database": "mongodb",
        }

    return app


app = create_app()
