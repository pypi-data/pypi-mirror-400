"""Tests for Scenarios resource."""

from typing import Any

import pytest
import respx
from httpx import Response

from planvantage import PlanVantageClient
from planvantage.models.scenario import ScenarioData, ScenarioUpdateResponse


class TestScenariosResource:
    """Tests for ScenariosResource."""

    def test_get_scenario(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
        sample_scenario_data: dict[str, Any],
    ) -> None:
        """Test getting a single scenario."""
        mock_api.get("/scenario/sc_test123").mock(
            return_value=Response(200, json=sample_scenario_data)
        )

        scenario = client.scenarios.get("sc_test123")

        assert isinstance(scenario, ScenarioData)
        assert scenario.guid == "sc_test123"
        assert scenario.name == "2024 Renewal Analysis"

    def test_create_scenario(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
        sample_scenario_data: dict[str, Any],
    ) -> None:
        """Test creating a scenario."""
        mock_api.post("/scenario").mock(
            return_value=Response(201, json=sample_scenario_data)
        )

        scenario = client.scenarios.create(
            plan_sponsor_guid="ps_test123",
            name="2024 Renewal Analysis",
        )

        assert isinstance(scenario, ScenarioData)
        assert scenario.name == "2024 Renewal Analysis"

    def test_update_scenario(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test updating a scenario."""
        updated_data = {
            "guid": "sc_test123",
            "name": "Updated Analysis",
        }
        mock_api.patch("/scenario/sc_test123").mock(
            return_value=Response(200, json=updated_data)
        )

        scenario = client.scenarios.update("sc_test123", name="Updated Analysis")

        assert isinstance(scenario, ScenarioUpdateResponse)
        assert scenario.name == "Updated Analysis"

    def test_delete_scenario(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test deleting a scenario."""
        mock_api.delete("/scenario/sc_test123").mock(
            return_value=Response(204)
        )

        client.scenarios.delete("sc_test123")

    def test_clone_scenario(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
        sample_scenario_data: dict[str, Any],
    ) -> None:
        """Test cloning a scenario."""
        cloned_data = {**sample_scenario_data, "guid": "sc_cloned123"}
        mock_api.post("/scenario/sc_test123/clone").mock(
            return_value=Response(201, json=cloned_data)
        )

        cloned = client.scenarios.clone("sc_test123")

        assert isinstance(cloned, ScenarioData)
        assert cloned.guid == "sc_cloned123"

    def test_calculate_all_options(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test calculating all contribution options."""
        mock_api.post("/scenario/sc_test123/calculatealloptions").mock(
            return_value=Response(200)
        )

        client.scenarios.calculate_all_options("sc_test123")

    def test_sync_enrollment(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test syncing enrollment data."""
        mock_api.post("/scenario/sc_test123/syncenrollment").mock(
            return_value=Response(200)
        )

        client.scenarios.sync_enrollment("sc_test123")
