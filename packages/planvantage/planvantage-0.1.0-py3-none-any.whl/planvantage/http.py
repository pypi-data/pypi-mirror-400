"""HTTP client for PlanVantage API with retry logic."""

from typing import Any, BinaryIO, Optional, Union

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from planvantage.auth import AuthConfig
from planvantage.exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    ConnectionError,
    NotFoundError,
    PlanVantageError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ValidationError,
)


# Exceptions that should trigger retry
RETRYABLE_EXCEPTIONS = (
    httpx.ConnectError,
    httpx.ReadTimeout,
    httpx.WriteTimeout,
    httpx.ConnectTimeout,
)


class HTTPClient:
    """HTTP client for making API requests with automatic retry."""

    def __init__(
        self,
        auth: AuthConfig,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        """Initialize HTTP client.

        Args:
            auth: Authentication configuration.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts for transient failures.
        """
        self.auth = auth
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: Optional[httpx.Client] = None

    @property
    def client(self) -> httpx.Client:
        """Get or create HTTP client instance."""
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.auth.base_url,
                headers=self.auth.get_headers(),
                timeout=self.timeout,
            )
        return self._client

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> "HTTPClient":
        """Enter context manager."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit context manager."""
        self.close()

    def _handle_response(self, response: httpx.Response) -> Any:
        """Handle API response and raise appropriate exceptions.

        Args:
            response: HTTP response object.

        Returns:
            Parsed JSON response data.

        Raises:
            Various PlanVantageError subclasses based on status code.
        """
        request_id = response.headers.get("X-Request-Id")

        if response.status_code >= 200 and response.status_code < 300:
            if response.status_code == 204 or not response.content:
                return None
            try:
                return response.json()
            except Exception:
                return response.text

        # Parse error response
        try:
            error_body = response.json()
            message = error_body.get("error", error_body.get("message", str(error_body)))
        except Exception:
            message = response.text or f"HTTP {response.status_code}"

        error_kwargs = {
            "status_code": response.status_code,
            "response_body": error_body if "error_body" in dir() else response.text,
            "request_id": request_id,
        }

        if response.status_code == 401:
            raise AuthenticationError(message, **error_kwargs)
        elif response.status_code == 403:
            raise AuthorizationError(message, **error_kwargs)
        elif response.status_code == 404:
            raise NotFoundError(message, **error_kwargs)
        elif response.status_code == 409:
            raise ConflictError(message, **error_kwargs)
        elif response.status_code == 422:
            errors = error_body.get("errors") if isinstance(error_body, dict) else None
            raise ValidationError(message, errors=errors, **error_kwargs)
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                message,
                retry_after=int(retry_after) if retry_after else None,
                **error_kwargs,
            )
        elif response.status_code >= 500:
            raise ServerError(message, **error_kwargs)
        else:
            raise APIError(message, **error_kwargs)

    def _make_request(
        self,
        method: str,
        path: str,
        params: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
        files: Optional[dict[str, BinaryIO]] = None,
    ) -> Any:
        """Make an HTTP request.

        Args:
            method: HTTP method.
            path: API endpoint path.
            params: Query parameters.
            json: JSON body data.
            data: Form data.
            files: Files to upload.

        Returns:
            Parsed response data.
        """
        try:
            # Remove Content-Type for file uploads
            headers = None
            if files:
                headers = {
                    k: v
                    for k, v in self.auth.get_headers().items()
                    if k.lower() != "content-type"
                }

            response = self.client.request(
                method=method,
                url=path,
                params=params,
                json=json,
                data=data,
                files=files,
                headers=headers,
            )
            return self._handle_response(response)

        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect: {e}") from e
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out: {e}") from e
        except PlanVantageError:
            raise
        except Exception as e:
            raise APIError(f"Unexpected error: {e}") from e

    @retry(
        retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    def request(
        self,
        method: str,
        path: str,
        params: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
        files: Optional[dict[str, BinaryIO]] = None,
    ) -> Any:
        """Make an HTTP request with automatic retry for transient failures.

        Args:
            method: HTTP method.
            path: API endpoint path.
            params: Query parameters.
            json: JSON body data.
            data: Form data.
            files: Files to upload.

        Returns:
            Parsed response data.
        """
        return self._make_request(method, path, params, json, data, files)

    def get(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
    ) -> Any:
        """Make a GET request.

        Args:
            path: API endpoint path.
            params: Query parameters.

        Returns:
            Parsed response data.
        """
        return self.request("GET", path, params=params)

    def post(
        self,
        path: str,
        json: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
        files: Optional[dict[str, BinaryIO]] = None,
    ) -> Any:
        """Make a POST request.

        Args:
            path: API endpoint path.
            json: JSON body data.
            data: Form data.
            files: Files to upload.

        Returns:
            Parsed response data.
        """
        return self.request("POST", path, json=json, data=data, files=files)

    def patch(
        self,
        path: str,
        json: Optional[dict[str, Any]] = None,
    ) -> Any:
        """Make a PATCH request.

        Args:
            path: API endpoint path.
            json: JSON body data.

        Returns:
            Parsed response data.
        """
        return self.request("PATCH", path, json=json)

    def put(
        self,
        path: str,
        json: Optional[dict[str, Any]] = None,
    ) -> Any:
        """Make a PUT request.

        Args:
            path: API endpoint path.
            json: JSON body data.

        Returns:
            Parsed response data.
        """
        return self.request("PUT", path, json=json)

    def delete(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
    ) -> Any:
        """Make a DELETE request.

        Args:
            path: API endpoint path.
            params: Query parameters.

        Returns:
            Parsed response data.
        """
        return self.request("DELETE", path, params=params)
