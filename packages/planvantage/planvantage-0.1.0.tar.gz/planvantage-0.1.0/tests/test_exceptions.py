"""Tests for exceptions."""

import pytest
import respx
from httpx import Response

from planvantage import PlanVantageClient
from planvantage.exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)


class TestExceptions:
    """Tests for exception handling."""

    def test_authentication_error_on_401(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test AuthenticationError on 401 response."""
        mock_api.get("/plansponsor/ps_test").mock(
            return_value=Response(401, json={"error": "Invalid token"})
        )

        with pytest.raises(AuthenticationError) as exc_info:
            client.plansponsors.get("ps_test")

        assert exc_info.value.status_code == 401

    def test_authorization_error_on_403(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test AuthorizationError on 403 response."""
        mock_api.get("/plansponsor/ps_test").mock(
            return_value=Response(403, json={"error": "Forbidden"})
        )

        with pytest.raises(AuthorizationError) as exc_info:
            client.plansponsors.get("ps_test")

        assert exc_info.value.status_code == 403

    def test_not_found_error_on_404(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test NotFoundError on 404 response."""
        mock_api.get("/plansponsor/ps_nonexistent").mock(
            return_value=Response(404, json={"error": "Not found"})
        )

        with pytest.raises(NotFoundError) as exc_info:
            client.plansponsors.get("ps_nonexistent")

        assert exc_info.value.status_code == 404

    def test_validation_error_on_422(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test ValidationError on 422 response."""
        mock_api.post("/plansponsor").mock(
            return_value=Response(
                422,
                json={
                    "error": "Validation failed",
                    "errors": [{"field": "name", "message": "required"}],
                },
            )
        )

        with pytest.raises(ValidationError) as exc_info:
            client.plansponsors.create(name="")

        assert exc_info.value.status_code == 422

    def test_rate_limit_error_on_429(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test RateLimitError on 429 response."""
        mock_api.get("/plansponsor").mock(
            return_value=Response(
                429,
                json={"error": "Rate limit exceeded"},
                headers={"Retry-After": "60"},
            )
        )

        with pytest.raises(RateLimitError) as exc_info:
            client.plansponsors.list()

        assert exc_info.value.status_code == 429
        assert exc_info.value.retry_after == 60

    def test_server_error_on_500(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test ServerError on 500 response."""
        mock_api.get("/plansponsor").mock(
            return_value=Response(500, json={"error": "Internal server error"})
        )

        with pytest.raises(ServerError) as exc_info:
            client.plansponsors.list()

        assert exc_info.value.status_code == 500

    def test_exception_str_representation(self) -> None:
        """Test exception string representation."""
        exc = APIError(
            message="Test error",
            status_code=400,
            request_id="req_123",
        )

        str_repr = str(exc)
        assert "Test error" in str_repr
        assert "400" in str_repr
        assert "req_123" in str_repr

    def test_exception_repr(self) -> None:
        """Test exception repr."""
        exc = NotFoundError(
            resource_type="PlanSponsor",
            resource_id="ps_test",
            status_code=404,
        )

        repr_str = repr(exc)
        assert "NotFoundError" in repr_str
