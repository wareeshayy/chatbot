"""Custom application exceptions."""

from typing import Any, Optional


class AppException(Exception):
    """Base exception for application errors."""

    def __init__(
        self,
        message: str,
        code: str = "APP_ERROR",
        status_code: int = 400,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class NotFoundError(AppException):
    def __init__(self, resource: str, identifier: Any = None) -> None:
        msg = f"{resource} not found"
        if identifier is not None:
            msg = f"{resource} '{identifier}' not found"
        super().__init__(message=msg, code="NOT_FOUND", status_code=404)


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Not authenticated") -> None:
        super().__init__(message=message, code="UNAUTHORIZED", status_code=401)


class ForbiddenError(AppException):
    def __init__(self, message: str = "Insufficient permissions") -> None:
        super().__init__(message=message, code="FORBIDDEN", status_code=403)


class ConflictError(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, code="CONFLICT", status_code=409)


class ValidationError(AppException):
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details=details,
        )
