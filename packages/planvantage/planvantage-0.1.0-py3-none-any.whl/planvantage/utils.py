"""Utility functions for the PlanVantage SDK."""

from typing import Any, Iterator, Optional, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class PaginatedResponse(BaseModel):
    """Wrapper for paginated API responses."""

    items: list[Any]
    total: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None
    has_more: bool = False

    def __iter__(self) -> Iterator[Any]:
        """Iterate over items in the current page."""
        return iter(self.items)

    def __len__(self) -> int:
        """Return number of items in current page."""
        return len(self.items)


def remove_none_values(data: dict[str, Any]) -> dict[str, Any]:
    """Remove None values from a dictionary.

    Args:
        data: Dictionary potentially containing None values.

    Returns:
        New dictionary with None values removed.
    """
    return {k: v for k, v in data.items() if v is not None}


def snake_to_camel(name: str) -> str:
    """Convert snake_case to camelCase.

    Args:
        name: Snake case string.

    Returns:
        Camel case string.
    """
    components = name.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case.

    Args:
        name: Camel case string.

    Returns:
        Snake case string.
    """
    result = []
    for char in name:
        if char.isupper():
            result.append("_")
            result.append(char.lower())
        else:
            result.append(char)
    return "".join(result).lstrip("_")


def dict_to_camel_keys(data: dict[str, Any]) -> dict[str, Any]:
    """Convert all dictionary keys from snake_case to camelCase.

    Args:
        data: Dictionary with snake_case keys.

    Returns:
        Dictionary with camelCase keys.
    """
    result = {}
    for key, value in data.items():
        camel_key = snake_to_camel(key)
        if isinstance(value, dict):
            result[camel_key] = dict_to_camel_keys(value)
        elif isinstance(value, list):
            result[camel_key] = [
                dict_to_camel_keys(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[camel_key] = value
    return result


def dict_to_snake_keys(data: dict[str, Any]) -> dict[str, Any]:
    """Convert all dictionary keys from camelCase to snake_case.

    Args:
        data: Dictionary with camelCase keys.

    Returns:
        Dictionary with snake_case keys.
    """
    result = {}
    for key, value in data.items():
        snake_key = camel_to_snake(key)
        if isinstance(value, dict):
            result[snake_key] = dict_to_snake_keys(value)
        elif isinstance(value, list):
            result[snake_key] = [
                dict_to_snake_keys(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[snake_key] = value
    return result
