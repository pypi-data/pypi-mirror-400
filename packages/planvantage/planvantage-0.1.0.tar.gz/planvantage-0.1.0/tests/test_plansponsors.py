"""Tests for PlanSponsors resource."""

from typing import Any

import pytest
import respx
from httpx import Response

from planvantage import PlanVantageClient
from planvantage.models.plansponsor import PlanSponsorData, PlanSponsorInfo


class TestPlanSponsorsResource:
    """Tests for PlanSponsorsResource."""

    def test_list_plansponsors(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
        sample_plansponsor_list: list[dict[str, Any]],
    ) -> None:
        """Test listing plan sponsors."""
        mock_api.get("/plansponsor").mock(
            return_value=Response(200, json=sample_plansponsor_list)
        )

        sponsors = client.plansponsors.list()

        assert len(sponsors) == 2
        assert isinstance(sponsors[0], PlanSponsorInfo)
        assert sponsors[0].guid == "ps_test123"
        assert sponsors[0].name == "Acme Corporation"
        assert sponsors[1].guid == "ps_test456"

    def test_get_plansponsor(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
        sample_plansponsor_data: dict[str, Any],
    ) -> None:
        """Test getting a single plan sponsor."""
        mock_api.get("/plansponsor/ps_test123").mock(
            return_value=Response(200, json=sample_plansponsor_data)
        )

        sponsor = client.plansponsors.get("ps_test123")

        assert isinstance(sponsor, PlanSponsorData)
        assert sponsor.guid == "ps_test123"
        assert sponsor.name == "Acme Corporation"

    def test_create_plansponsor(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
        sample_plansponsor_data: dict[str, Any],
    ) -> None:
        """Test creating a plan sponsor."""
        mock_api.post("/plansponsor").mock(
            return_value=Response(201, json=sample_plansponsor_data)
        )

        sponsor = client.plansponsors.create(name="Acme Corporation")

        assert isinstance(sponsor, PlanSponsorData)
        assert sponsor.name == "Acme Corporation"

    def test_update_plansponsor(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test updating a plan sponsor."""
        updated_data = {
            "guid": "ps_test123",
            "name": "Acme Corp Updated",
        }
        mock_api.patch("/plansponsor/ps_test123").mock(
            return_value=Response(200, json=updated_data)
        )

        sponsor = client.plansponsors.update("ps_test123", name="Acme Corp Updated")

        assert isinstance(sponsor, PlanSponsorData)
        assert sponsor.name == "Acme Corp Updated"

    def test_delete_plansponsor(
        self,
        client: PlanVantageClient,
        mock_api: respx.MockRouter,
    ) -> None:
        """Test deleting a plan sponsor."""
        mock_api.delete("/plansponsor/ps_test123").mock(
            return_value=Response(204)
        )

        # Should not raise
        client.plansponsors.delete("ps_test123")
