"""Tests for RatePlans resources."""

from typing import Any

import pytest
import respx
from httpx import Response

from planvantage import PlanVantageClient
from planvantage.models.rateplan import (
    RatePlanAdjustmentData,
    RatePlanData,
    RatePlanTierData,
)


class TestCurrentRatePlansResource:
    """Tests for CurrentRatePlansResource."""

    def test_get_current_rate_plan(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
        sample_rateplan_data: dict[str, Any],
    ) -> None:
        """Test getting a single current rate plan."""
        mock_api.get("/currentrateplan/rp_test123").mock(
            return_value=Response(200, json=sample_rateplan_data)
        )

        rate_plan = client.current_rate_plans.get("rp_test123")

        assert isinstance(rate_plan, RatePlanData)
        assert rate_plan.guid == "rp_test123"
        assert rate_plan.name == "Gold PPO Rates"

    def test_create_current_rate_plan(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
        sample_rateplan_data: dict[str, Any],
    ) -> None:
        """Test creating a current rate plan."""
        mock_api.post("/currentrateplan").mock(
            return_value=Response(201, json=sample_rateplan_data)
        )

        rate_plan = client.current_rate_plans.create(
            scenario_guid="sc_test123",
            plan_design_guid="pd_test123",
        )

        assert isinstance(rate_plan, RatePlanData)
        assert rate_plan.plan_design_guid == "pd_test123"

    def test_update_current_rate_plan(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test updating a current rate plan."""
        updated_data = {
            "guid": "rp_test123",
            "name": "Updated Rates",
        }
        mock_api.patch("/currentrateplan/rp_test123").mock(
            return_value=Response(200, json=updated_data)
        )

        rate_plan = client.current_rate_plans.update("rp_test123", name="Updated Rates")

        assert isinstance(rate_plan, RatePlanData)
        assert rate_plan.name == "Updated Rates"

    def test_delete_current_rate_plan(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test deleting a current rate plan."""
        mock_api.delete("/currentrateplan/rp_test123").mock(
            return_value=Response(204)
        )

        client.current_rate_plans.delete("rp_test123")

    def test_apply_tier_name_set(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test applying tier name set to current rate plan."""
        mock_api.patch("/currentrateplan/rp_test123/tiernameset").mock(
            return_value=Response(200)
        )

        client.current_rate_plans.apply_tier_name_set("rp_test123", "tns_test123")


class TestProposedRatePlansResource:
    """Tests for ProposedRatePlansResource."""

    def test_get_proposed_rate_plan(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
        sample_rateplan_data: dict[str, Any],
    ) -> None:
        """Test getting a single proposed rate plan."""
        mock_api.get("/proposedrateplan/rp_test123").mock(
            return_value=Response(200, json=sample_rateplan_data)
        )

        rate_plan = client.proposed_rate_plans.get("rp_test123")

        assert isinstance(rate_plan, RatePlanData)
        assert rate_plan.guid == "rp_test123"

    def test_create_proposed_rate_plan(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
        sample_rateplan_data: dict[str, Any],
    ) -> None:
        """Test creating a proposed rate plan."""
        mock_api.post("/proposedrateplan").mock(
            return_value=Response(201, json=sample_rateplan_data)
        )

        rate_plan = client.proposed_rate_plans.create(
            scenario_guid="sc_test123",
        )

        assert isinstance(rate_plan, RatePlanData)

    def test_update_proposed_rate_plan(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test updating a proposed rate plan."""
        updated_data = {
            "guid": "rp_test123",
            "rate_increase": 0.05,
        }
        mock_api.patch("/proposedrateplan/rp_test123").mock(
            return_value=Response(200, json=updated_data)
        )

        rate_plan = client.proposed_rate_plans.update("rp_test123", rate_increase=0.05)

        assert isinstance(rate_plan, RatePlanData)

    def test_delete_proposed_rate_plan(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test deleting a proposed rate plan."""
        mock_api.delete("/proposedrateplan/rp_test123").mock(
            return_value=Response(204)
        )

        client.proposed_rate_plans.delete("rp_test123")

    def test_reset_tier_ratios_to_default(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test resetting tier ratios to default."""
        mock_api.post("/proposedrateplan/rp_test123/resettierratios/default").mock(
            return_value=Response(200)
        )

        client.proposed_rate_plans.reset_tier_ratios_to_default("rp_test123")

    def test_reset_tier_ratios_to_current(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test resetting tier ratios to current."""
        mock_api.post("/proposedrateplan/rp_test123/resettierratios/current").mock(
            return_value=Response(200)
        )

        client.proposed_rate_plans.reset_tier_ratios_to_current("rp_test123")

    def test_copy_from_current(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
        sample_rateplan_data: dict[str, Any],
    ) -> None:
        """Test copying from current rate plan."""
        mock_api.post("/proposedrateplan/copycurrent").mock(
            return_value=Response(201, json=sample_rateplan_data)
        )

        rate_plan = client.proposed_rate_plans.copy_from_current("rp_current123")

        assert isinstance(rate_plan, RatePlanData)


class TestCurrentRatePlanTiersResource:
    """Tests for CurrentRatePlanTiersResource."""

    def test_get_tier(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test getting a current rate plan tier."""
        tier_data = {
            "guid": "rpt_test123",
            "rate_plan_guid": "rp_test123",
            "name": "Employee Only",
            "rate": 450.00,
            "enrollment": 50,
        }
        mock_api.get("/currentrateplantier/rpt_test123").mock(
            return_value=Response(200, json=tier_data)
        )

        tier = client.current_rate_plan_tiers.get("rpt_test123")

        assert isinstance(tier, RatePlanTierData)
        assert tier.rate == 450.00

    def test_create_tier(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test creating a current rate plan tier."""
        tier_data = {
            "guid": "rpt_test123",
            "rate_plan_guid": "rp_test123",
            "name": "Employee Only",
            "rate": 500.00,
        }
        mock_api.post("/currentrateplantier").mock(
            return_value=Response(201, json=tier_data)
        )

        tier = client.current_rate_plan_tiers.create(
            rate_plan_guid="rp_test123",
            name="Employee Only",
            rate=500.00,
        )

        assert isinstance(tier, RatePlanTierData)
        assert tier.name == "Employee Only"

    def test_update_tier(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test updating a current rate plan tier."""
        tier_data = {
            "guid": "rpt_test123",
            "rate": 475.00,
        }
        mock_api.patch("/currentrateplantier/rpt_test123").mock(
            return_value=Response(200, json=tier_data)
        )

        tier = client.current_rate_plan_tiers.update("rpt_test123", rate=475.00)

        assert isinstance(tier, RatePlanTierData)

    def test_delete_tier(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test deleting a current rate plan tier."""
        mock_api.delete("/currentrateplantier/rpt_test123").mock(
            return_value=Response(204)
        )

        client.current_rate_plan_tiers.delete("rpt_test123")


class TestProposedRatePlanTiersResource:
    """Tests for ProposedRatePlanTiersResource."""

    def test_get_tier(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test getting a proposed rate plan tier."""
        tier_data = {
            "guid": "rpt_test123",
            "rate_plan_guid": "rp_test123",
            "name": "Employee Only",
            "rate": 475.00,
        }
        mock_api.get("/proposedrateplantier/rpt_test123").mock(
            return_value=Response(200, json=tier_data)
        )

        tier = client.proposed_rate_plan_tiers.get("rpt_test123")

        assert isinstance(tier, RatePlanTierData)

    def test_create_tier(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test creating a proposed rate plan tier."""
        tier_data = {
            "guid": "rpt_test123",
            "rate_plan_guid": "rp_test123",
            "name": "Employee + Family",
            "rate": 1200.00,
        }
        mock_api.post("/proposedrateplantier").mock(
            return_value=Response(201, json=tier_data)
        )

        tier = client.proposed_rate_plan_tiers.create(
            rate_plan_guid="rp_test123",
            name="Employee + Family",
            rate=1200.00,
        )

        assert isinstance(tier, RatePlanTierData)

    def test_update_tier(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test updating a proposed rate plan tier."""
        tier_data = {
            "guid": "rpt_test123",
            "enrollment": 25,
        }
        mock_api.patch("/proposedrateplantier/rpt_test123").mock(
            return_value=Response(200, json=tier_data)
        )

        tier = client.proposed_rate_plan_tiers.update("rpt_test123", enrollment=25)

        assert isinstance(tier, RatePlanTierData)

    def test_delete_tier(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test deleting a proposed rate plan tier."""
        mock_api.delete("/proposedrateplantier/rpt_test123").mock(
            return_value=Response(204)
        )

        client.proposed_rate_plan_tiers.delete("rpt_test123")


class TestCurrentRatePlanAdjustmentsResource:
    """Tests for CurrentRatePlanAdjustmentsResource."""

    def test_get_adjustment(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test getting a current rate plan adjustment."""
        adj_data = {
            "guid": "adj_test123",
            "rate_plan_guid": "rp_test123",
            "name": "Admin Fee",
            "value": 25.00,
        }
        mock_api.get("/currentrateplanadjustment/adj_test123").mock(
            return_value=Response(200, json=adj_data)
        )

        adj = client.current_rate_plan_adjustments.get("adj_test123")

        assert isinstance(adj, RatePlanAdjustmentData)
        assert adj.name == "Admin Fee"

    def test_create_adjustment(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test creating a current rate plan adjustment."""
        adj_data = {
            "guid": "adj_test123",
            "rate_plan_guid": "rp_test123",
            "name": "HSA Contribution",
            "value": 50.00,
            "is_credit": True,
        }
        mock_api.post("/currentrateplanadjustment").mock(
            return_value=Response(201, json=adj_data)
        )

        adj = client.current_rate_plan_adjustments.create(
            rate_plan_guid="rp_test123",
            name="HSA Contribution",
            value=50.00,
            is_credit=True,
        )

        assert isinstance(adj, RatePlanAdjustmentData)

    def test_update_adjustment(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test updating a current rate plan adjustment."""
        adj_data = {
            "guid": "adj_test123",
            "value": 30.00,
        }
        mock_api.patch("/currentrateplanadjustment/adj_test123").mock(
            return_value=Response(200, json=adj_data)
        )

        adj = client.current_rate_plan_adjustments.update("adj_test123", value=30.00)

        assert isinstance(adj, RatePlanAdjustmentData)

    def test_delete_adjustment(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test deleting a current rate plan adjustment."""
        mock_api.delete("/currentrateplanadjustment/adj_test123").mock(
            return_value=Response(204)
        )

        client.current_rate_plan_adjustments.delete("adj_test123")


class TestProposedRatePlanAdjustmentsResource:
    """Tests for ProposedRatePlanAdjustmentsResource."""

    def test_get_adjustment(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test getting a proposed rate plan adjustment."""
        adj_data = {
            "guid": "adj_test123",
            "rate_plan_guid": "rp_test123",
            "name": "Wellness Credit",
            "value": 15.00,
        }
        mock_api.get("/proposedrateplanadjustment/adj_test123").mock(
            return_value=Response(200, json=adj_data)
        )

        adj = client.proposed_rate_plan_adjustments.get("adj_test123")

        assert isinstance(adj, RatePlanAdjustmentData)

    def test_create_adjustment(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test creating a proposed rate plan adjustment."""
        adj_data = {
            "guid": "adj_test123",
            "rate_plan_guid": "rp_test123",
            "name": "Wellness Credit",
            "value": 15.00,
        }
        mock_api.post("/proposedrateplanadjustment").mock(
            return_value=Response(201, json=adj_data)
        )

        adj = client.proposed_rate_plan_adjustments.create(
            rate_plan_guid="rp_test123",
            name="Wellness Credit",
            value=15.00,
        )

        assert isinstance(adj, RatePlanAdjustmentData)

    def test_update_adjustment(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test updating a proposed rate plan adjustment."""
        adj_data = {
            "guid": "adj_test123",
            "is_taxable": False,
        }
        mock_api.patch("/proposedrateplanadjustment/adj_test123").mock(
            return_value=Response(200, json=adj_data)
        )

        adj = client.proposed_rate_plan_adjustments.update("adj_test123", is_taxable=False)

        assert isinstance(adj, RatePlanAdjustmentData)

    def test_delete_adjustment(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test deleting a proposed rate plan adjustment."""
        mock_api.delete("/proposedrateplanadjustment/adj_test123").mock(
            return_value=Response(204)
        )

        client.proposed_rate_plan_adjustments.delete("adj_test123")
