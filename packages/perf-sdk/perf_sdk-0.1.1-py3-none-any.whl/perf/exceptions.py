"""Exception classes for Perf SDK."""

from typing import Optional


class PerfError(Exception):
    """Base exception for Perf API errors."""

    def __init__(
        self,
        message: str,
        code: str,
        error_type: str,
        status_code: int,
        request_id: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.error_type = error_type
        self.status_code = status_code
        self.request_id = request_id

    @property
    def is_retryable(self) -> bool:
        """Whether this error should be retried."""
        return self.code in {
            "rate_limit_exceeded",
            "internal_error",
            "provider_error",
            "service_unavailable",
        }

    def __str__(self) -> str:
        return f"PerfError({self.code}): {self.message}"

    def __repr__(self) -> str:
        return f"PerfError(code={self.code!r}, message={self.message!r}, status_code={self.status_code})"


class RateLimitError(PerfError):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str,
        request_id: Optional[str] = None,
        retry_after: Optional[int] = None,
    ):
        super().__init__(
            message=message,
            code="rate_limit_exceeded",
            error_type="rate_limit_error",
            status_code=429,
            request_id=request_id,
        )
        self.retry_after = retry_after


class UsageLimitError(PerfError):
    """Raised when usage limit is exceeded."""

    def __init__(self, message: str, request_id: Optional[str] = None):
        super().__init__(
            message=message,
            code="usage_limit_exceeded",
            error_type="usage_limit_error",
            status_code=429,
            request_id=request_id,
        )


class AuthenticationError(PerfError):
    """Raised when API key is invalid."""

    def __init__(self, message: str, request_id: Optional[str] = None):
        super().__init__(
            message=message,
            code="invalid_api_key",
            error_type="authentication_error",
            status_code=401,
            request_id=request_id,
        )


class NetworkError(Exception):
    """Raised when a network error occurs."""

    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(message)
        self.cause = cause


class PerfTimeoutError(Exception):
    """Raised when a request times out."""

    def __init__(self, timeout: float):
        super().__init__(f"Request timed out after {timeout} seconds")
        self.timeout = timeout
