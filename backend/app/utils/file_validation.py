"""File upload validation utilities."""

import mimetypes
from pathlib import Path

from fastapi import UploadFile

from app.config.settings import Settings
from app.utils.exceptions import ValidationError

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}


def get_file_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def validate_upload_file(file: UploadFile, settings: Settings) -> str:
    if not file.filename:
        raise ValidationError("Filename is required")

    extension = get_file_extension(file.filename)
    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"Unsupported file type '{extension}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    content_type = file.content_type or mimetypes.guess_type(file.filename)[0]
    if content_type and content_type not in ALLOWED_MIME_TYPES:
        raise ValidationError(f"Unsupported MIME type: {content_type}")

    return extension.lstrip(".")


async def validate_file_size(file: UploadFile, settings: Settings) -> int:
    content = await file.read()
    size = len(content)
    await file.seek(0)

    if size == 0:
        raise ValidationError("Uploaded file is empty")

    if size > settings.max_upload_size_bytes:
        raise ValidationError(
            f"File exceeds maximum size of {settings.max_upload_size_mb} MB"
        )

    return size
