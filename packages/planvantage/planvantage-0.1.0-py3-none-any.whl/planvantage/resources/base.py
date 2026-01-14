"""Base resource class for API resources."""

from typing import TYPE_CHECKING, Any, Optional, TypeVar, Generic

from pydantic import BaseModel

if TYPE_CHECKING:
    from planvantage.http import HTTPClient


T = TypeVar("T", bound=BaseModel)


class BaseResource:
    """Base class for API resources."""

    def __init__(self, http: "HTTPClient") -> None:
        """Initialize resource with HTTP client.

        Args:
            http: HTTP client for making API requests.
        """
        self._http = http

    def _serialize(self, data: Any) -> dict[str, Any]:
        """Serialize data for API request.

        Args:
            data: Data to serialize (dict or Pydantic model).

        Returns:
            Dictionary suitable for JSON serialization.
        """
        if data is None:
            return {}
        if isinstance(data, BaseModel):
            return data.model_dump(exclude_none=True, by_alias=True)
        if isinstance(data, dict):
            return {k: v for k, v in data.items() if v is not None}
        return data
