from typing import Optional


class FourbyfourError(Exception):
    """Base exception for all Fourbyfour SDK errors."""

    def __init__(self, message: str, code: str, status: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status


class ValidationError(FourbyfourError):
    """Raised when request validation fails."""

    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR", 400)


class AuthenticationError(FourbyfourError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Invalid or missing API key"):
        super().__init__(message, "UNAUTHORIZED", 401)


class ForbiddenError(FourbyfourError):
    """Raised when access is forbidden."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, "FORBIDDEN", 403)


class NotFoundError(FourbyfourError):
    """Raised when a resource is not found."""

    def __init__(self, message: str):
        super().__init__(message, "NOT_FOUND", 404)


class ConflictError(FourbyfourError):
    """Raised when there is a conflict (e.g., resource already exists)."""

    def __init__(self, message: str):
        super().__init__(message, "CONFLICT", 409)


class RateLimitError(FourbyfourError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, "RATE_LIMIT_EXCEEDED", 429)


class InternalError(FourbyfourError):
    """Raised when an internal server error occurs."""

    def __init__(self, message: str = "Internal server error"):
        super().__init__(message, "INTERNAL_ERROR", 500)
