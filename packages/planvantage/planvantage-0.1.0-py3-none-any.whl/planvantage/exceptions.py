"""Custom exceptions for the PlanVantage SDK."""

from typing import Any, Optional


class PlanVantageError(Exception):
    """Base exception for all PlanVantage SDK errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[Any] = None,
        request_id: Optional[str] = None,
    ) -> None:
        """Initialize PlanVantageError.

        Args:
            message: Human-readable error message.
            status_code: HTTP status code if from API response.
            response_body: Raw response body from API.
            request_id: Request ID for debugging with support.
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body
        self.request_id = request_id

    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code:
            parts.append(f"(status: {self.status_code})")
        if self.request_id:
            parts.append(f"[request_id: {self.request_id}]")
        return " ".join(parts)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"status_code={self.status_code!r}, "
            f"request_id={self.request_id!r})"
        )


class APIError(PlanVantageError):
    """Error returned by the PlanVantage API."""

    pass


class AuthenticationError(PlanVantageError):
    """Authentication failed - invalid or missing API key."""

    def __init__(
        self,
        message: str = "Authentication failed. Check your API key.",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class AuthorizationError(PlanVantageError):
    """Authorization failed - insufficient permissions."""

    def __init__(
        self,
        message: str = "Authorization failed. Insufficient permissions.",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class NotFoundError(PlanVantageError):
    """Requested resource was not found."""

    def __init__(
        self,
        message: str = "The requested resource was not found.",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        if resource_type and resource_id:
            message = f"{resource_type} with id '{resource_id}' was not found."
        super().__init__(message, **kwargs)
        self.resource_type = resource_type
        self.resource_id = resource_id


class ValidationError(PlanVantageError):
    """Request validation failed."""

    def __init__(
        self,
        message: str = "Request validation failed.",
        errors: Optional[list[dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.errors = errors or []


class RateLimitError(PlanVantageError):
    """Rate limit exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded. Please retry after some time.",
        retry_after: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class ConflictError(PlanVantageError):
    """Resource conflict - e.g., duplicate creation."""

    def __init__(
        self,
        message: str = "Resource conflict.",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class ServerError(PlanVantageError):
    """Server-side error."""

    def __init__(
        self,
        message: str = "An internal server error occurred. Please try again later.",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class ConnectionError(PlanVantageError):
    """Network connection error."""

    def __init__(
        self,
        message: str = "Failed to connect to the PlanVantage API.",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class TimeoutError(PlanVantageError):
    """Request timed out."""

    def __init__(
        self,
        message: str = "Request timed out.",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
