"""Tests for PlanVantage client."""

import os
from unittest.mock import patch

import pytest

from planvantage import PlanVantageClient
from planvantage.auth import AuthConfig, ENV_API_KEY, ENV_BASE_URL
from planvantage.exceptions import AuthenticationError


class TestAuthConfig:
    """Tests for AuthConfig."""

    def test_init_with_api_key(self) -> None:
        """Test creating auth config with explicit API key."""
        config = AuthConfig(api_key="pk_test", base_url="https://api.test.com")
        assert config.api_key == "pk_test"
        assert config.base_url == "https://api.test.com"

    def test_init_strips_trailing_slash(self) -> None:
        """Test that trailing slash is stripped from base URL."""
        config = AuthConfig(api_key="pk_test", base_url="https://api.test.com/")
        assert config.base_url == "https://api.test.com"

    def test_init_raises_without_api_key(self) -> None:
        """Test that AuthenticationError is raised without API key."""
        with pytest.raises(AuthenticationError):
            AuthConfig(api_key="", base_url="https://api.test.com")

    def test_from_env_with_explicit_values(self) -> None:
        """Test creating auth config with explicit values."""
        config = AuthConfig.from_env(api_key="pk_test", base_url="https://api.test.com")
        assert config.api_key == "pk_test"
        assert config.base_url == "https://api.test.com"

    def test_from_env_with_env_vars(self) -> None:
        """Test creating auth config from environment variables."""
        with patch.dict(
            os.environ,
            {
                ENV_API_KEY: "pk_env_test",
                ENV_BASE_URL: "https://env.test.com",
            },
        ):
            config = AuthConfig.from_env()
            assert config.api_key == "pk_env_test"
            assert config.base_url == "https://env.test.com"

    def test_get_headers(self) -> None:
        """Test getting authentication headers."""
        config = AuthConfig(api_key="pk_test", base_url="https://api.test.com")
        headers = config.get_headers()

        assert headers["Authorization"] == "Bearer pk_test"
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"


class TestPlanVantageClient:
    """Tests for PlanVantageClient."""

    def test_init_with_api_key(self) -> None:
        """Test creating client with explicit API key."""
        client = PlanVantageClient(api_key="pk_test", base_url="https://api.test.com")
        assert client._auth.api_key == "pk_test"
        client.close()

    def test_context_manager(self) -> None:
        """Test using client as context manager."""
        with PlanVantageClient(api_key="pk_test", base_url="https://api.test.com") as client:
            assert client._auth.api_key == "pk_test"

    def test_resource_properties_are_lazy(self) -> None:
        """Test that resource properties are lazily initialized."""
        with PlanVantageClient(api_key="pk_test", base_url="https://api.test.com") as client:
            # Resources should not be initialized yet
            assert client._plansponsors is None
            assert client._scenarios is None

            # Access triggers initialization
            _ = client.plansponsors
            _ = client.scenarios

            assert client._plansponsors is not None
            assert client._scenarios is not None

    def test_all_resource_properties_accessible(self) -> None:
        """Test that all resource properties are accessible."""
        with PlanVantageClient(api_key="pk_test", base_url="https://api.test.com") as client:
            # Verify all resources can be accessed
            assert client.plansponsors is not None
            assert client.scenarios is not None
            assert client.plandesigns is not None
            assert client.plandesign_tiers is not None
            assert client.service_cost_shares is not None
            assert client.current_rate_plans is not None
            assert client.proposed_rate_plans is not None
            assert client.current_rate_plan_tiers is not None
            assert client.proposed_rate_plan_tiers is not None
            assert client.current_rate_plan_adjustments is not None
            assert client.proposed_rate_plan_adjustments is not None
            assert client.current_contribution_groups is not None
            assert client.current_contribution_tiers is not None
            assert client.proposed_contribution_options is not None
            assert client.proposed_contribution_groups is not None
            assert client.proposed_contribution_tiers is not None
            assert client.plandocuments is not None
            assert client.chats is not None
            assert client.chat_messages is not None
            assert client.benchmarks is not None
            assert client.plan_model_settings is not None
            assert client.rate_model_settings is not None
            assert client.rate_model_assumptions is not None
            assert client.tier_names is not None
