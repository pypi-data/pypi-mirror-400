"""PlanDesigns resource."""

from typing import Any, Optional

from planvantage.models.plandesign import (
    CopyPlanDesignRequest,
    PlanDesignData,
    PlanDesignTierData,
    PlanDesignUtilizationData,
    ServiceCostShareData,
)
from planvantage.resources.base import BaseResource


class PlanDesignsResource(BaseResource):
    """Resource for managing plan designs."""

    def get(self, guid: str) -> PlanDesignData:
        """Get a specific plan design by GUID.

        Args:
            guid: The plan design's unique identifier.

        Returns:
            Full plan design data.

        Example:
            >>> plan = client.plandesigns.get("pd_abc123")
            >>> print(plan.name)
        """
        data = self._http.get(f"/plandesign/{guid}")
        return PlanDesignData.model_validate(data)

    def create(
        self,
        scenario_guid: str,
        name: Optional[str] = None,
        **kwargs: Any,
    ) -> PlanDesignData:
        """Create a new plan design in a scenario.

        Args:
            scenario_guid: The parent scenario's GUID.
            name: Optional name for the plan design.
            **kwargs: Additional plan design fields.

        Returns:
            The created plan design data.

        Example:
            >>> plan = client.plandesigns.create(
            ...     scenario_guid="sc_abc123",
            ...     name="Gold PPO"
            ... )
        """
        request = {
            "scenario_guid": scenario_guid,
            "name": name,
            **kwargs,
        }
        data = self._http.post("/plandesign", json={k: v for k, v in request.items() if v is not None})
        return PlanDesignData.model_validate(data)

    def update(
        self,
        guid: str,
        **kwargs: Any,
    ) -> PlanDesignData:
        """Update a plan design.

        Args:
            guid: The plan design's unique identifier.
            **kwargs: Fields to update.

        Returns:
            The updated plan design data.

        Example:
            >>> plan = client.plandesigns.update("pd_abc123", name="Platinum PPO")
        """
        data = self._http.patch(f"/plandesign/{guid}", json=kwargs)
        return PlanDesignData.model_validate(data)

    def delete(self, guid: str) -> None:
        """Delete a plan design.

        Args:
            guid: The plan design's unique identifier.

        Example:
            >>> client.plandesigns.delete("pd_abc123")
        """
        self._http.delete(f"/plandesign/{guid}")

    def clone(self, guid: str) -> PlanDesignData:
        """Clone a plan design.

        Args:
            guid: The plan design's unique identifier.

        Returns:
            The cloned plan design data.

        Example:
            >>> cloned = client.plandesigns.clone("pd_abc123")
        """
        data = self._http.post(f"/plandesign/{guid}/clone")
        return PlanDesignData.model_validate(data)

    def copy_to_scenario(
        self,
        guid: str,
        target_scenario_guid: str,
    ) -> PlanDesignData:
        """Copy a plan design to another scenario.

        Args:
            guid: The plan design's unique identifier.
            target_scenario_guid: The destination scenario's GUID.

        Returns:
            The copied plan design data.

        Example:
            >>> copied = client.plandesigns.copy_to_scenario("pd_abc", "sc_xyz")
        """
        data = self._http.post(
            f"/scenario/{target_scenario_guid}/plandesign/copy",
            json={"source_plan_design_guid": guid},
        )
        return PlanDesignData.model_validate(data)

    def calculate_av(self, guid: str) -> PlanDesignData:
        """Calculate actuarial value for a plan design.

        Args:
            guid: The plan design's unique identifier.

        Returns:
            Updated plan design data with AV results.

        Example:
            >>> plan = client.plandesigns.calculate_av("pd_abc123")
            >>> print(plan.plan_av_result.av)
        """
        data = self._http.post(f"/plandesign/{guid}/calculate")
        return PlanDesignData.model_validate(data)

    def update_utilization(
        self,
        guid: str,
        tiers: list[dict[str, Any]],
    ) -> PlanDesignData:
        """Update tier utilization for a plan design.

        Args:
            guid: The plan design's unique identifier.
            tiers: List of tier utilization updates with guid and utilization_percent.

        Returns:
            Updated plan design data.

        Example:
            >>> client.plandesigns.update_utilization(
            ...     "pd_abc123",
            ...     tiers=[{"guid": "tier_1", "utilization_percent": 50.0}]
            ... )
        """
        data = self._http.patch(
            f"/plandesign/{guid}/utilization",
            json={"tiers": tiers},
        )
        return PlanDesignData.model_validate(data)


class PlanDesignTiersResource(BaseResource):
    """Resource for managing plan design tiers."""

    def get(self, guid: str) -> PlanDesignTierData:
        """Get a specific plan design tier by GUID.

        Args:
            guid: The tier's unique identifier.

        Returns:
            Tier data.
        """
        data = self._http.get(f"/plandesigntier/{guid}")
        return PlanDesignTierData.model_validate(data)

    def create(
        self,
        plan_design_guid: str,
        name: str,
        **kwargs: Any,
    ) -> PlanDesignTierData:
        """Create a new tier for a plan design.

        Args:
            plan_design_guid: The parent plan design's GUID.
            name: Name for the tier.
            **kwargs: Additional tier fields.

        Returns:
            Created tier data.
        """
        request = {
            "plan_design_guid": plan_design_guid,
            "name": name,
            **kwargs,
        }
        data = self._http.post(
            "/plandesigntier",
            json={k: v for k, v in request.items() if v is not None},
        )
        return PlanDesignTierData.model_validate(data)

    def update(
        self,
        guid: str,
        **kwargs: Any,
    ) -> PlanDesignTierData:
        """Update a plan design tier.

        Args:
            guid: The tier's unique identifier.
            **kwargs: Fields to update.

        Returns:
            Updated tier data.
        """
        data = self._http.patch(f"/plandesigntier/{guid}", json=kwargs)
        return PlanDesignTierData.model_validate(data)

    def delete(self, guid: str) -> None:
        """Delete a plan design tier.

        Args:
            guid: The tier's unique identifier.
        """
        self._http.delete(f"/plandesigntier/{guid}")


class ServiceCostSharesResource(BaseResource):
    """Resource for managing service cost sharing."""

    def get(self, guid: str) -> ServiceCostShareData:
        """Get a specific service cost share by GUID.

        Args:
            guid: The service cost share's unique identifier.

        Returns:
            Service cost share data.
        """
        data = self._http.get(f"/servicecostshare/{guid}")
        return ServiceCostShareData.model_validate(data)

    def create(
        self,
        plan_design_tier_guid: str,
        service: str,
        **kwargs: Any,
    ) -> ServiceCostShareData:
        """Create a service cost share.

        Args:
            plan_design_tier_guid: The parent tier's GUID.
            service: The service type.
            **kwargs: Additional fields (copay, coins, ded_applies, etc.).

        Returns:
            Created service cost share data.
        """
        request = {
            "PlanDesignTierGUID": plan_design_tier_guid,
            "Service": service,
            **kwargs,
        }
        data = self._http.post(
            "/servicecostshare",
            json={k: v for k, v in request.items() if v is not None},
        )
        return ServiceCostShareData.model_validate(data)

    def update(
        self,
        guid: str,
        **kwargs: Any,
    ) -> ServiceCostShareData:
        """Update a service cost share.

        Args:
            guid: The service cost share's unique identifier.
            **kwargs: Fields to update.

        Returns:
            Updated service cost share data.
        """
        data = self._http.patch(f"/servicecostshare/{guid}", json=kwargs)
        return ServiceCostShareData.model_validate(data)

    def delete(self, guid: str) -> None:
        """Delete a service cost share.

        Args:
            guid: The service cost share's unique identifier.
        """
        self._http.delete(f"/servicecostshare/{guid}")
