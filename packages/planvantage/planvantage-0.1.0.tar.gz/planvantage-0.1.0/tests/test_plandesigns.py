"""Tests for PlanDesigns resource."""

from typing import Any

import pytest
import respx
from httpx import Response

from planvantage import PlanVantageClient
from planvantage.models.plandesign import PlanDesignData


class TestPlanDesignsResource:
    """Tests for PlanDesignsResource."""

    def test_get_plandesign(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
        sample_plandesign_data: dict[str, Any],
    ) -> None:
        """Test getting a single plan design."""
        mock_api.get("/plandesign/pd_test123").mock(
            return_value=Response(200, json=sample_plandesign_data)
        )

        plan = client.plandesigns.get("pd_test123")

        assert isinstance(plan, PlanDesignData)
        assert plan.guid == "pd_test123"
        assert plan.name == "Gold PPO"
        assert plan.carrier == "Blue Cross"

    def test_create_plandesign(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
        sample_plandesign_data: dict[str, Any],
    ) -> None:
        """Test creating a plan design."""
        mock_api.post("/plandesign").mock(
            return_value=Response(201, json=sample_plandesign_data)
        )

        plan = client.plandesigns.create(
            scenario_guid="sc_test123",
            name="Gold PPO",
        )

        assert isinstance(plan, PlanDesignData)
        assert plan.name == "Gold PPO"

    def test_update_plandesign(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test updating a plan design."""
        updated_data = {
            "guid": "pd_test123",
            "name": "Platinum PPO",
        }
        mock_api.patch("/plandesign/pd_test123").mock(
            return_value=Response(200, json=updated_data)
        )

        plan = client.plandesigns.update("pd_test123", name="Platinum PPO")

        assert isinstance(plan, PlanDesignData)
        assert plan.name == "Platinum PPO"

    def test_delete_plandesign(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test deleting a plan design."""
        mock_api.delete("/plandesign/pd_test123").mock(
            return_value=Response(204)
        )

        client.plandesigns.delete("pd_test123")

    def test_clone_plandesign(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
        sample_plandesign_data: dict[str, Any],
    ) -> None:
        """Test cloning a plan design."""
        cloned_data = {**sample_plandesign_data, "guid": "pd_cloned123"}
        mock_api.post("/plandesign/pd_test123/clone").mock(
            return_value=Response(201, json=cloned_data)
        )

        cloned = client.plandesigns.clone("pd_test123")

        assert isinstance(cloned, PlanDesignData)
        assert cloned.guid == "pd_cloned123"

    def test_calculate_av(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
        sample_plandesign_data: dict[str, Any],
    ) -> None:
        """Test calculating actuarial value."""
        data_with_av = {
            **sample_plandesign_data,
            "plan_av_result": {
                "AV": 0.85,
                "AVWithFund": 0.90,
            },
        }
        mock_api.post("/plandesign/pd_test123/calculate").mock(
            return_value=Response(200, json=data_with_av)
        )

        plan = client.plandesigns.calculate_av("pd_test123")

        assert isinstance(plan, PlanDesignData)
        assert plan.plan_av_result is not None
