"""File storage abstraction — local implementation with cloud-ready interface."""

from abc import ABC, abstractmethod
from pathlib import Path

import aiofiles
from fastapi import UploadFile

from app.config.settings import get_settings


class StorageBackend(ABC):
    @abstractmethod
    async def save(self, file: UploadFile, path: str) -> str:
        """Save file and return storage path/key."""

    @abstractmethod
    async def delete(self, path: str) -> None:
        """Delete file at path/key."""

    @abstractmethod
    async def exists(self, path: str) -> bool:
        """Check if file exists."""

    @abstractmethod
    async def get_absolute_path(self, path: str) -> Path:
        """Resolve storage path for local file access (parsing)."""


class LocalStorageBackend(StorageBackend):
    def __init__(self, upload_dir: str) -> None:
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save(self, file: UploadFile, path: str) -> str:
        full_path = self.upload_dir / path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(full_path, "wb") as out_file:
            while chunk := await file.read(1024 * 1024):
                await out_file.write(chunk)

        await file.seek(0)
        return path

    async def delete(self, path: str) -> None:
        full_path = self.upload_dir / path
        if full_path.exists():
            full_path.unlink()

    async def exists(self, path: str) -> bool:
        return (self.upload_dir / path).exists()

    async def get_absolute_path(self, path: str) -> Path:
        return self.upload_dir / path


def get_storage_backend() -> StorageBackend:
    settings = get_settings()
    if settings.storage_backend == "local":
        return LocalStorageBackend(settings.upload_dir)
    raise NotImplementedError(
        f"Storage backend '{settings.storage_backend}' will be implemented in Phase 9"
    )
