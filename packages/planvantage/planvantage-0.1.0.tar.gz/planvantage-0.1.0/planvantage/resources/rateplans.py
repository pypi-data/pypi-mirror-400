"""Rate plan resources."""

from typing import Any, Optional

from planvantage.models.rateplan import (
    CopyCurrentRatePlanRequest,
    RatePlanAdjustmentData,
    RatePlanAdjustmentInput,
    RatePlanData,
    RatePlanInput,
    RatePlanTierData,
    RatePlanTierInput,
    TierNameSetInput,
)
from planvantage.resources.base import BaseResource


class CurrentRatePlansResource(BaseResource):
    """Resource for managing current rate plans."""

    def get(self, guid: str) -> RatePlanData:
        """Get a specific current rate plan by GUID.

        Args:
            guid: The rate plan's unique identifier.

        Returns:
            Full rate plan data.

        Example:
            >>> rate_plan = client.current_rate_plans.get("rp_abc123")
        """
        data = self._http.get(f"/currentrateplan/{guid}")
        return RatePlanData.model_validate(data)

    def create(
        self,
        scenario_guid: str,
        plan_design_guid: Optional[str] = None,
        **kwargs: Any,
    ) -> RatePlanData:
        """Create a new current rate plan.

        Args:
            scenario_guid: The parent scenario's GUID.
            plan_design_guid: Optional associated plan design GUID.
            **kwargs: Additional rate plan fields.

        Returns:
            Created rate plan data.

        Example:
            >>> rate_plan = client.current_rate_plans.create(
            ...     scenario_guid="sc_abc123",
            ...     plan_design_guid="pd_xyz789"
            ... )
        """
        request = RatePlanInput(
            scenario_guid=scenario_guid,
            plan_design_guid=plan_design_guid,
            **kwargs,
        )
        data = self._http.post("/currentrateplan", json=self._serialize(request))
        return RatePlanData.model_validate(data)

    def update(
        self,
        guid: str,
        **kwargs: Any,
    ) -> RatePlanData:
        """Update a current rate plan.

        Args:
            guid: The rate plan's unique identifier.
            **kwargs: Fields to update.

        Returns:
            Updated rate plan data.
        """
        data = self._http.patch(f"/currentrateplan/{guid}", json=kwargs)
        return RatePlanData.model_validate(data)

    def delete(self, guid: str) -> None:
        """Delete a current rate plan.

        Args:
            guid: The rate plan's unique identifier.
        """
        self._http.delete(f"/currentrateplan/{guid}")

    def apply_tier_name_set(
        self,
        guid: str,
        tier_name_set_guid: str,
    ) -> None:
        """Apply a tier name set to the rate plan.

        Args:
            guid: The rate plan's unique identifier.
            tier_name_set_guid: The tier name set GUID.
        """
        self._http.patch(
            f"/currentrateplan/{guid}/tiernameset",
            json={"tierNameSetGuid": tier_name_set_guid},
        )


class ProposedRatePlansResource(BaseResource):
    """Resource for managing proposed rate plans."""

    def get(self, guid: str) -> RatePlanData:
        """Get a specific proposed rate plan by GUID.

        Args:
            guid: The rate plan's unique identifier.

        Returns:
            Full rate plan data.
        """
        data = self._http.get(f"/proposedrateplan/{guid}")
        return RatePlanData.model_validate(data)

    def create(
        self,
        scenario_guid: str,
        plan_design_guid: Optional[str] = None,
        **kwargs: Any,
    ) -> RatePlanData:
        """Create a new proposed rate plan.

        Args:
            scenario_guid: The parent scenario's GUID.
            plan_design_guid: Optional associated plan design GUID.
            **kwargs: Additional rate plan fields.

        Returns:
            Created rate plan data.
        """
        request = RatePlanInput(
            scenario_guid=scenario_guid,
            plan_design_guid=plan_design_guid,
            **kwargs,
        )
        data = self._http.post("/proposedrateplan", json=self._serialize(request))
        return RatePlanData.model_validate(data)

    def update(
        self,
        guid: str,
        **kwargs: Any,
    ) -> RatePlanData:
        """Update a proposed rate plan.

        Args:
            guid: The rate plan's unique identifier.
            **kwargs: Fields to update.

        Returns:
            Updated rate plan data.
        """
        data = self._http.patch(f"/proposedrateplan/{guid}", json=kwargs)
        return RatePlanData.model_validate(data)

    def delete(self, guid: str) -> None:
        """Delete a proposed rate plan.

        Args:
            guid: The rate plan's unique identifier.
        """
        self._http.delete(f"/proposedrateplan/{guid}")

    def apply_tier_name_set(
        self,
        guid: str,
        tier_name_set_guid: str,
    ) -> None:
        """Apply a tier name set to the proposed rate plan.

        Args:
            guid: The rate plan's unique identifier.
            tier_name_set_guid: The tier name set GUID.
        """
        self._http.patch(
            f"/proposedrateplan/{guid}/tiernameset",
            json={"tierNameSetGuid": tier_name_set_guid},
        )

    def reset_tier_ratios_to_default(self, guid: str) -> None:
        """Reset tier ratios to default values.

        Args:
            guid: The rate plan's unique identifier.
        """
        self._http.post(f"/proposedrateplan/{guid}/resettierratios/default")

    def reset_tier_ratios_to_current(self, guid: str) -> None:
        """Reset tier ratios to match current rate plan.

        Args:
            guid: The rate plan's unique identifier.
        """
        self._http.post(f"/proposedrateplan/{guid}/resettierratios/current")

    def copy_from_current(
        self,
        current_rate_plan_guid: str,
    ) -> RatePlanData:
        """Copy a current rate plan to create a proposed rate plan.

        Args:
            current_rate_plan_guid: The current rate plan's GUID.

        Returns:
            Created proposed rate plan data.
        """
        request = CopyCurrentRatePlanRequest(current_rate_plan_guid=current_rate_plan_guid)
        data = self._http.post("/proposedrateplan/copycurrent", json=self._serialize(request))
        return RatePlanData.model_validate(data)


class CurrentRatePlanTiersResource(BaseResource):
    """Resource for managing current rate plan tiers."""

    def get(self, guid: str) -> RatePlanTierData:
        """Get a specific current rate plan tier.

        Args:
            guid: The tier's unique identifier.

        Returns:
            Tier data.
        """
        data = self._http.get(f"/currentrateplantier/{guid}")
        return RatePlanTierData.model_validate(data)

    def create(
        self,
        rate_plan_guid: str,
        **kwargs: Any,
    ) -> RatePlanTierData:
        """Create a new current rate plan tier.

        Args:
            rate_plan_guid: The parent rate plan's GUID.
            **kwargs: Tier fields (name, rate, ratio, enrollment).

        Returns:
            Created tier data.
        """
        request = RatePlanTierInput(rate_plan_guid=rate_plan_guid, **kwargs)
        data = self._http.post("/currentrateplantier", json=self._serialize(request))
        return RatePlanTierData.model_validate(data)

    def update(
        self,
        guid: str,
        **kwargs: Any,
    ) -> RatePlanTierData:
        """Update a current rate plan tier.

        Args:
            guid: The tier's unique identifier.
            **kwargs: Fields to update.

        Returns:
            Updated tier data.
        """
        data = self._http.patch(f"/currentrateplantier/{guid}", json=kwargs)
        return RatePlanTierData.model_validate(data)

    def delete(self, guid: str) -> None:
        """Delete a current rate plan tier.

        Args:
            guid: The tier's unique identifier.
        """
        self._http.delete(f"/currentrateplantier/{guid}")


class ProposedRatePlanTiersResource(BaseResource):
    """Resource for managing proposed rate plan tiers."""

    def get(self, guid: str) -> RatePlanTierData:
        """Get a specific proposed rate plan tier.

        Args:
            guid: The tier's unique identifier.

        Returns:
            Tier data.
        """
        data = self._http.get(f"/proposedrateplantier/{guid}")
        return RatePlanTierData.model_validate(data)

    def create(
        self,
        rate_plan_guid: str,
        **kwargs: Any,
    ) -> RatePlanTierData:
        """Create a new proposed rate plan tier.

        Args:
            rate_plan_guid: The parent rate plan's GUID.
            **kwargs: Tier fields (name, rate, ratio, enrollment).

        Returns:
            Created tier data.
        """
        request = RatePlanTierInput(rate_plan_guid=rate_plan_guid, **kwargs)
        data = self._http.post("/proposedrateplantier", json=self._serialize(request))
        return RatePlanTierData.model_validate(data)

    def update(
        self,
        guid: str,
        **kwargs: Any,
    ) -> RatePlanTierData:
        """Update a proposed rate plan tier.

        Args:
            guid: The tier's unique identifier.
            **kwargs: Fields to update.

        Returns:
            Updated tier data.
        """
        data = self._http.patch(f"/proposedrateplantier/{guid}", json=kwargs)
        return RatePlanTierData.model_validate(data)

    def delete(self, guid: str) -> None:
        """Delete a proposed rate plan tier.

        Args:
            guid: The tier's unique identifier.
        """
        self._http.delete(f"/proposedrateplantier/{guid}")


class CurrentRatePlanAdjustmentsResource(BaseResource):
    """Resource for managing current rate plan adjustments."""

    def get(self, guid: str) -> RatePlanAdjustmentData:
        """Get a specific current rate plan adjustment.

        Args:
            guid: The adjustment's unique identifier.

        Returns:
            Adjustment data.
        """
        data = self._http.get(f"/currentrateplanadjustment/{guid}")
        return RatePlanAdjustmentData.model_validate(data)

    def create(
        self,
        rate_plan_guid: str,
        **kwargs: Any,
    ) -> RatePlanAdjustmentData:
        """Create a new current rate plan adjustment.

        Args:
            rate_plan_guid: The parent rate plan's GUID.
            **kwargs: Adjustment fields.

        Returns:
            Created adjustment data.
        """
        request = RatePlanAdjustmentInput(rate_plan_guid=rate_plan_guid, **kwargs)
        data = self._http.post("/currentrateplanadjustment", json=self._serialize(request))
        return RatePlanAdjustmentData.model_validate(data)

    def update(
        self,
        guid: str,
        **kwargs: Any,
    ) -> RatePlanAdjustmentData:
        """Update a current rate plan adjustment.

        Args:
            guid: The adjustment's unique identifier.
            **kwargs: Fields to update.

        Returns:
            Updated adjustment data.
        """
        data = self._http.patch(f"/currentrateplanadjustment/{guid}", json=kwargs)
        return RatePlanAdjustmentData.model_validate(data)

    def delete(self, guid: str) -> None:
        """Delete a current rate plan adjustment.

        Args:
            guid: The adjustment's unique identifier.
        """
        self._http.delete(f"/currentrateplanadjustment/{guid}")


class ProposedRatePlanAdjustmentsResource(BaseResource):
    """Resource for managing proposed rate plan adjustments."""

    def get(self, guid: str) -> RatePlanAdjustmentData:
        """Get a specific proposed rate plan adjustment.

        Args:
            guid: The adjustment's unique identifier.

        Returns:
            Adjustment data.
        """
        data = self._http.get(f"/proposedrateplanadjustment/{guid}")
        return RatePlanAdjustmentData.model_validate(data)

    def create(
        self,
        rate_plan_guid: str,
        **kwargs: Any,
    ) -> RatePlanAdjustmentData:
        """Create a new proposed rate plan adjustment.

        Args:
            rate_plan_guid: The parent rate plan's GUID.
            **kwargs: Adjustment fields.

        Returns:
            Created adjustment data.
        """
        request = RatePlanAdjustmentInput(rate_plan_guid=rate_plan_guid, **kwargs)
        data = self._http.post("/proposedrateplanadjustment", json=self._serialize(request))
        return RatePlanAdjustmentData.model_validate(data)

    def update(
        self,
        guid: str,
        **kwargs: Any,
    ) -> RatePlanAdjustmentData:
        """Update a proposed rate plan adjustment.

        Args:
            guid: The adjustment's unique identifier.
            **kwargs: Fields to update.

        Returns:
            Updated adjustment data.
        """
        data = self._http.patch(f"/proposedrateplanadjustment/{guid}", json=kwargs)
        return RatePlanAdjustmentData.model_validate(data)

    def delete(self, guid: str) -> None:
        """Delete a proposed rate plan adjustment.

        Args:
            guid: The adjustment's unique identifier.
        """
        self._http.delete(f"/proposedrateplanadjustment/{guid}")
