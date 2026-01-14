"""PlanSponsors resource."""

from typing import Any, Optional, Union

from planvantage.models.plansponsor import (
    PlanSponsorCreateRequest,
    PlanSponsorData,
    PlanSponsorInfo,
    PlanSponsorUpdateRequest,
)
from planvantage.resources.base import BaseResource


class PlanSponsorsResource(BaseResource):
    """Resource for managing plan sponsors."""

    def list(self) -> list[PlanSponsorInfo]:
        """List all plan sponsors accessible to the current user.

        Returns:
            List of plan sponsor summary objects.

        Example:
            >>> sponsors = client.plansponsors.list()
            >>> for sponsor in sponsors:
            ...     print(sponsor.name)
        """
        data = self._http.get("/plansponsor")
        if isinstance(data, list):
            return [PlanSponsorInfo.model_validate(item) for item in data]
        return []

    def get(self, guid: str) -> PlanSponsorData:
        """Get a specific plan sponsor by GUID.

        Args:
            guid: The plan sponsor's unique identifier.

        Returns:
            Full plan sponsor data including related objects.

        Example:
            >>> sponsor = client.plansponsors.get("ps_abc123")
            >>> print(sponsor.name)
        """
        data = self._http.get(f"/plansponsor/{guid}")
        return PlanSponsorData.model_validate(data)

    def create(
        self,
        name: str,
        **kwargs: Any,
    ) -> PlanSponsorData:
        """Create a new plan sponsor.

        Args:
            name: The plan sponsor's name (typically company name).
            **kwargs: Additional fields to include in the request.

        Returns:
            The created plan sponsor data.

        Example:
            >>> sponsor = client.plansponsors.create(name="Acme Corporation")
            >>> print(sponsor.guid)
        """
        request = PlanSponsorCreateRequest(name=name, **kwargs)
        data = self._http.post("/plansponsor", json=self._serialize(request))
        return PlanSponsorData.model_validate(data)

    def update(
        self,
        guid: str,
        name: Optional[str] = None,
        **kwargs: Any,
    ) -> PlanSponsorData:
        """Update an existing plan sponsor.

        Args:
            guid: The plan sponsor's unique identifier.
            name: New name for the plan sponsor.
            **kwargs: Additional fields to update.

        Returns:
            The updated plan sponsor data.

        Example:
            >>> sponsor = client.plansponsors.update("ps_abc123", name="Acme Corp")
        """
        request = PlanSponsorUpdateRequest(name=name, **kwargs)
        data = self._http.patch(f"/plansponsor/{guid}", json=self._serialize(request))
        return PlanSponsorData.model_validate(data)

    def delete(self, guid: str) -> None:
        """Delete a plan sponsor.

        Args:
            guid: The plan sponsor's unique identifier.

        Example:
            >>> client.plansponsors.delete("ps_abc123")
        """
        self._http.delete(f"/plansponsor/{guid}")
