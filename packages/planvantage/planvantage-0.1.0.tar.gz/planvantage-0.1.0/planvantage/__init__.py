"""PlanVantage Python SDK.

A Python SDK for interacting with the PlanVantage API for health benefits
plan design and actuarial value calculations.

Example:
    >>> from planvantage import PlanVantageClient
    >>>
    >>> # Initialize with API key
    >>> client = PlanVantageClient(api_key="pk_...")
    >>>
    >>> # Or use environment variable PLANVANTAGE_API_KEY
    >>> client = PlanVantageClient()
    >>>
    >>> # List all plan sponsors
    >>> sponsors = client.plansponsors.list()
    >>> for sponsor in sponsors:
    ...     print(sponsor.name)
    >>>
    >>> # Get a specific scenario
    >>> scenario = client.scenarios.get("sc_abc123")
    >>>
    >>> # Create a new plan design
    >>> plan = client.plandesigns.create(
    ...     scenario_guid="sc_abc123",
    ...     name="Gold PPO"
    ... )
    >>>
    >>> # Close the client when done
    >>> client.close()
    >>>
    >>> # Or use as context manager
    >>> with PlanVantageClient(api_key="pk_...") as client:
    ...     sponsors = client.plansponsors.list()
"""

from planvantage.client import PlanVantageClient
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

__version__ = "0.1.0"

__all__ = [
    # Main client
    "PlanVantageClient",
    # Exceptions
    "PlanVantageError",
    "APIError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ConflictError",
    "ServerError",
    "ConnectionError",
    "TimeoutError",
]
