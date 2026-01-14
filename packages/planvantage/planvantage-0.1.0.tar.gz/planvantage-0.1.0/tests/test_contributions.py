"""Tests for Contributions resources."""

from typing import Any

import pytest
import respx
from httpx import Response

from planvantage import PlanVantageClient
from planvantage.models.contribution import (
    ContributionOptionItemsLists,
    ProposedContributionGroupData,
    ProposedContributionOptionStatusData,
    ProposedContributionTierData,
)


class TestCurrentContributionGroupsResource:
    """Tests for CurrentContributionGroupsResource."""

    def test_create_group(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test creating a current contribution group."""
        group_data = {
            "guid": "ccg_test123",
            "name": "Default Group",
        }
        mock_api.post("/currentcontributiongroup").mock(
            return_value=Response(201, json=group_data)
        )

        result = client.current_contribution_groups.create(name="Default Group")

        assert result["guid"] == "ccg_test123"

    def test_update_group(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test updating a current contribution group."""
        group_data = {
            "guid": "ccg_test123",
            "name": "Renamed Group",
        }
        mock_api.patch("/currentcontributiongroup/ccg_test123").mock(
            return_value=Response(200, json=group_data)
        )

        result = client.current_contribution_groups.update(
            "ccg_test123", name="Renamed Group"
        )

        assert result["name"] == "Renamed Group"

    def test_delete_group(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test deleting a current contribution group."""
        mock_api.delete("/currentcontributiongroup/ccg_test123").mock(
            return_value=Response(204)
        )

        client.current_contribution_groups.delete("ccg_test123")

    def test_add_rate_plan(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test adding a rate plan to contribution group."""
        mock_api.post("/currentcontributiongroup/ccg_test123/rateplan").mock(
            return_value=Response(200)
        )

        client.current_contribution_groups.add_rate_plan("ccg_test123", "rp_test123")

    def test_remove_rate_plan(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test removing a rate plan from contribution group."""
        mock_api.delete(
            "/currentcontributiongroup/ccg_test123/rateplan/rp_test123"
        ).mock(return_value=Response(204))

        client.current_contribution_groups.remove_rate_plan("ccg_test123", "rp_test123")

    def test_copy_to_proposed(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test copying current contribution setup to proposed."""
        mock_api.post("/currentcontributiongroup/ccg_test123/copy").mock(
            return_value=Response(200)
        )

        client.current_contribution_groups.copy_to_proposed("ccg_test123")


class TestCurrentContributionTiersResource:
    """Tests for CurrentContributionTiersResource."""

    def test_update_tier(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test updating a current contribution tier."""
        tier_data = {
            "guid": "cct_test123",
            "enrollment": 100,
        }
        mock_api.patch("/currentcontributiontier/cct_test123").mock(
            return_value=Response(200, json=tier_data)
        )

        result = client.current_contribution_tiers.update("cct_test123", enrollment=100)

        assert result["enrollment"] == 100

    def test_update_multiple_enrollment(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test updating enrollment for multiple tiers."""
        mock_api.post("/currentcontributiontier/multiple").mock(
            return_value=Response(200)
        )

        tiers = [
            {"guid": "cct_test1", "enrollment": 50},
            {"guid": "cct_test2", "enrollment": 30},
        ]
        client.current_contribution_tiers.update_multiple_enrollment(tiers)


class TestProposedContributionOptionsResource:
    """Tests for ProposedContributionOptionsResource."""

    def test_create_option(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test creating a proposed contribution option."""
        option_data = {
            "guid": "pco_test123",
            "name": "Option 1",
        }
        mock_api.post("/proposedcontributionoption").mock(
            return_value=Response(201, json=option_data)
        )

        result = client.proposed_contribution_options.create(name="Option 1")

        assert result["guid"] == "pco_test123"

    def test_update_option(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test updating a proposed contribution option."""
        option_data = {
            "guid": "pco_test123",
            "name": "Updated Option",
        }
        mock_api.patch("/proposedcontributionoption/pco_test123").mock(
            return_value=Response(200, json=option_data)
        )

        result = client.proposed_contribution_options.update(
            "pco_test123", name="Updated Option"
        )

        assert result["name"] == "Updated Option"

    def test_delete_option(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test deleting a proposed contribution option."""
        mock_api.delete("/proposedcontributionoption/pco_test123").mock(
            return_value=Response(204)
        )

        client.proposed_contribution_options.delete("pco_test123")

    def test_get_status(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test getting status of a contribution option."""
        status_data = {
            "status": "complete",
            "progress": 100,
        }
        mock_api.get("/proposedcontributionoption/pco_test123/status").mock(
            return_value=Response(200, json=status_data)
        )

        status = client.proposed_contribution_options.get_status("pco_test123")

        assert isinstance(status, ProposedContributionOptionStatusData)
        assert status.status == "complete"

    def test_ignore_warning(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test ignoring warning on contribution option."""
        mock_api.post("/proposedcontributionoption/pco_test123/ignorewarning").mock(
            return_value=Response(200)
        )

        client.proposed_contribution_options.ignore_warning("pco_test123")

    def test_update_prompt(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test updating prompt on contribution option."""
        mock_api.post("/proposedcontributionoption/pco_test123/updateprompt").mock(
            return_value=Response(200)
        )

        client.proposed_contribution_options.update_prompt(
            "pco_test123", "Match current contributions"
        )

    def test_recalculate(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test recalculating a contribution option."""
        mock_api.post("/proposedcontributionoption/pco_test123/recalculate").mock(
            return_value=Response(200)
        )

        client.proposed_contribution_options.recalculate("pco_test123")

    def test_cancel(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test canceling a contribution option calculation."""
        mock_api.post("/proposedcontributionoption/pco_test123/cancel").mock(
            return_value=Response(200)
        )

        client.proposed_contribution_options.cancel("pco_test123")

    def test_get_items(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test getting available contribution option items."""
        items_data = {
            "strategies": ["flat", "percentage"],
            "prompts": ["Match current", "Reduce costs"],
        }
        mock_api.get("/proposedcontributionoption/items").mock(
            return_value=Response(200, json=items_data)
        )

        items = client.proposed_contribution_options.get_items()

        assert isinstance(items, ContributionOptionItemsLists)

    def test_bulk_add(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test bulk adding contribution options."""
        mock_api.post("/proposedcontributionoption/pco_test123/bulkadd").mock(
            return_value=Response(200)
        )

        items = [
            {"strategy": "flat", "value": 100},
            {"strategy": "percentage", "value": 80},
        ]
        client.proposed_contribution_options.bulk_add("pco_test123", items)

    def test_copy_current_enrollment(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test copying current enrollment to option."""
        mock_api.post(
            "/proposedcontributionoption/pco_test123/copycurrentenrollment"
        ).mock(return_value=Response(200))

        client.proposed_contribution_options.copy_current_enrollment("pco_test123")

    def test_copy_rate_enrollment(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test copying rate enrollment to option."""
        mock_api.post(
            "/proposedcontributionoption/pco_test123/copyrateenrollment"
        ).mock(return_value=Response(200))

        client.proposed_contribution_options.copy_rate_enrollment("pco_test123")

    def test_copy_option_enrollment(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test copying enrollment from another option."""
        mock_api.post(
            "/proposedcontributionoption/pco_test123/copyoptionenrollment"
        ).mock(return_value=Response(200))

        client.proposed_contribution_options.copy_option_enrollment("pco_test123")


class TestProposedContributionGroupsResource:
    """Tests for ProposedContributionGroupsResource."""

    def test_create_group(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test creating a proposed contribution group."""
        group_data = {
            "guid": "pcg_test123",
            "contribution_option_guid": "pco_test123",
            "name": "Full-Time",
        }
        mock_api.post("/proposedcontributiongroup").mock(
            return_value=Response(201, json=group_data)
        )

        group = client.proposed_contribution_groups.create(
            contribution_option_guid="pco_test123",
            name="Full-Time",
        )

        assert isinstance(group, ProposedContributionGroupData)
        assert group.name == "Full-Time"

    def test_update_group(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test updating a proposed contribution group."""
        group_data = {
            "guid": "pcg_test123",
            "name": "Part-Time",
        }
        mock_api.patch("/proposedcontributiongroup/pcg_test123").mock(
            return_value=Response(200, json=group_data)
        )

        group = client.proposed_contribution_groups.update(
            "pcg_test123", name="Part-Time"
        )

        assert isinstance(group, ProposedContributionGroupData)

    def test_delete_group(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test deleting a proposed contribution group."""
        mock_api.delete("/proposedcontributiongroup/pcg_test123").mock(
            return_value=Response(204)
        )

        client.proposed_contribution_groups.delete("pcg_test123")

    def test_add_rate_plan(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test adding a rate plan to proposed contribution group."""
        mock_api.post("/proposedcontributiongroup/pcg_test123/rateplan").mock(
            return_value=Response(200)
        )

        client.proposed_contribution_groups.add_rate_plan("pcg_test123", "rp_test123")

    def test_remove_rate_plan(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test removing a rate plan from proposed contribution group."""
        mock_api.delete(
            "/proposedcontributiongroup/pcg_test123/rateplan/rp_test123"
        ).mock(return_value=Response(204))

        client.proposed_contribution_groups.remove_rate_plan("pcg_test123", "rp_test123")


class TestProposedContributionTiersResource:
    """Tests for ProposedContributionTiersResource."""

    def test_update_tier(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test updating a proposed contribution tier."""
        tier_data = {
            "guid": "pct_test123",
            "enrollment": 75,
        }
        mock_api.patch("/proposedcontributiontier/pct_test123").mock(
            return_value=Response(200, json=tier_data)
        )

        tier = client.proposed_contribution_tiers.update("pct_test123", enrollment=75)

        assert isinstance(tier, ProposedContributionTierData)

    def test_update_multiple_enrollment(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test updating enrollment for multiple proposed tiers."""
        mock_api.post("/proposedcontributiontier/multiple").mock(
            return_value=Response(200)
        )

        tiers = [
            {"guid": "pct_test1", "enrollment": 40},
            {"guid": "pct_test2", "enrollment": 60},
        ]
        client.proposed_contribution_tiers.update_multiple_enrollment(tiers)
