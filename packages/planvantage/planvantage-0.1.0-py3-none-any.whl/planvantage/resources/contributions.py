"""Contribution resources."""

from typing import Any, Optional

from planvantage.models.contribution import (
    ContributionGroupData,
    ContributionOptionData,
    ContributionOptionImportItem,
    ContributionOptionItemsLists,
    ContributionTierData,
    ContributionTierEnrollmentUpdateData,
    ProposedContributionGroupData,
    ProposedContributionGroupInput,
    ProposedContributionOptionStatusData,
    ProposedContributionTierData,
    ProposedContributionTierEnrollmentUpdate,
    ProposedContributionTierInput,
)
from planvantage.resources.base import BaseResource


class CurrentContributionGroupsResource(BaseResource):
    """Resource for managing current contribution groups."""

    def create(self, **kwargs: Any) -> Any:
        """Create a current contribution group.

        Args:
            **kwargs: Group fields.

        Returns:
            Created group data.
        """
        return self._http.post("/currentcontributiongroup", json=kwargs)

    def update(
        self,
        guid: str,
        **kwargs: Any,
    ) -> Any:
        """Update a current contribution group.

        Args:
            guid: The group's unique identifier.
            **kwargs: Fields to update.

        Returns:
            Updated group data.
        """
        return self._http.patch(f"/currentcontributiongroup/{guid}", json=kwargs)

    def delete(self, guid: str) -> None:
        """Delete a current contribution group.

        Args:
            guid: The group's unique identifier.
        """
        self._http.delete(f"/currentcontributiongroup/{guid}")

    def add_rate_plan(
        self,
        guid: str,
        rate_plan_guid: str,
    ) -> None:
        """Add a rate plan to the contribution group.

        Args:
            guid: The group's unique identifier.
            rate_plan_guid: The rate plan's GUID.
        """
        self._http.post(
            f"/currentcontributiongroup/{guid}/rateplan",
            json={"ratePlanGuid": rate_plan_guid},
        )

    def remove_rate_plan(
        self,
        guid: str,
        rate_plan_guid: str,
    ) -> None:
        """Remove a rate plan from the contribution group.

        Args:
            guid: The group's unique identifier.
            rate_plan_guid: The rate plan's GUID.
        """
        self._http.delete(f"/currentcontributiongroup/{guid}/rateplan/{rate_plan_guid}")

    def copy_to_proposed(self, guid: str) -> None:
        """Copy current contribution setup to proposed options.

        Args:
            guid: The group's unique identifier.
        """
        self._http.post(f"/currentcontributiongroup/{guid}/copy")


class CurrentContributionTiersResource(BaseResource):
    """Resource for managing current contribution tiers."""

    def update(
        self,
        guid: str,
        **kwargs: Any,
    ) -> Any:
        """Update a current contribution tier.

        Args:
            guid: The tier's unique identifier.
            **kwargs: Fields to update.

        Returns:
            Updated tier data.
        """
        return self._http.patch(f"/currentcontributiontier/{guid}", json=kwargs)

    def update_multiple_enrollment(
        self,
        tiers: list[dict[str, Any]],
    ) -> None:
        """Update enrollment for multiple tiers.

        Args:
            tiers: List of dicts with guid and enrollment.
        """
        self._http.post("/currentcontributiontier/multiple", json=tiers)


class ProposedContributionOptionsResource(BaseResource):
    """Resource for managing proposed contribution options."""

    def create(self, **kwargs: Any) -> Any:
        """Create a proposed contribution option.

        Args:
            **kwargs: Option fields.

        Returns:
            Created option data.
        """
        return self._http.post("/proposedcontributionoption", json=kwargs)

    def update(
        self,
        guid: str,
        **kwargs: Any,
    ) -> Any:
        """Update a proposed contribution option.

        Args:
            guid: The option's unique identifier.
            **kwargs: Fields to update.

        Returns:
            Updated option data.
        """
        return self._http.patch(f"/proposedcontributionoption/{guid}", json=kwargs)

    def delete(self, guid: str) -> None:
        """Delete a proposed contribution option.

        Args:
            guid: The option's unique identifier.
        """
        self._http.delete(f"/proposedcontributionoption/{guid}")

    def get_status(self, guid: str) -> ProposedContributionOptionStatusData:
        """Get processing status for a contribution option.

        Args:
            guid: The option's unique identifier.

        Returns:
            Status data.
        """
        data = self._http.get(f"/proposedcontributionoption/{guid}/status")
        return ProposedContributionOptionStatusData.model_validate(data)

    def ignore_warning(self, guid: str) -> None:
        """Ignore warning on a contribution option.

        Args:
            guid: The option's unique identifier.
        """
        self._http.post(f"/proposedcontributionoption/{guid}/ignorewarning")

    def update_prompt(
        self,
        guid: str,
        prompt: str,
    ) -> None:
        """Update the prompt for a contribution option.

        Args:
            guid: The option's unique identifier.
            prompt: New prompt text.
        """
        self._http.post(
            f"/proposedcontributionoption/{guid}/updateprompt",
            json={"prompt": prompt},
        )

    def recalculate(self, guid: str) -> None:
        """Recalculate a contribution option.

        Args:
            guid: The option's unique identifier.
        """
        self._http.post(f"/proposedcontributionoption/{guid}/recalculate")

    def cancel(self, guid: str) -> None:
        """Cancel processing of a contribution option.

        Args:
            guid: The option's unique identifier.
        """
        self._http.post(f"/proposedcontributionoption/{guid}/cancel")

    def get_items(self) -> ContributionOptionItemsLists:
        """Get available contribution option items.

        Returns:
            Lists of available strategies and prompts.
        """
        data = self._http.get("/proposedcontributionoption/items")
        return ContributionOptionItemsLists.model_validate(data)

    def bulk_add(
        self,
        guid: str,
        items: list[dict[str, Any]],
    ) -> None:
        """Bulk add contribution options.

        Args:
            guid: The base option's unique identifier.
            items: List of option configurations.
        """
        self._http.post(
            f"/proposedcontributionoption/{guid}/bulkadd",
            json={"items": items},
        )

    def copy_current_enrollment(self, guid: str) -> None:
        """Copy current enrollment to the option.

        Args:
            guid: The option's unique identifier.
        """
        self._http.post(f"/proposedcontributionoption/{guid}/copycurrentenrollment")

    def copy_rate_enrollment(self, guid: str) -> None:
        """Copy rate enrollment to the option.

        Args:
            guid: The option's unique identifier.
        """
        self._http.post(f"/proposedcontributionoption/{guid}/copyrateenrollment")

    def copy_option_enrollment(self, guid: str) -> None:
        """Copy enrollment from another option.

        Args:
            guid: The option's unique identifier.
        """
        self._http.post(f"/proposedcontributionoption/{guid}/copyoptionenrollment")


class ProposedContributionGroupsResource(BaseResource):
    """Resource for managing proposed contribution groups."""

    def create(
        self,
        contribution_option_guid: str,
        name: Optional[str] = None,
        **kwargs: Any,
    ) -> ProposedContributionGroupData:
        """Create a proposed contribution group.

        Args:
            contribution_option_guid: Parent option's GUID.
            name: Optional group name.
            **kwargs: Additional fields.

        Returns:
            Created group data.
        """
        request = ProposedContributionGroupInput(
            contribution_option_guid=contribution_option_guid,
            name=name,
            **kwargs,
        )
        data = self._http.post("/proposedcontributiongroup", json=self._serialize(request))
        return ProposedContributionGroupData.model_validate(data)

    def update(
        self,
        guid: str,
        **kwargs: Any,
    ) -> ProposedContributionGroupData:
        """Update a proposed contribution group.

        Args:
            guid: The group's unique identifier.
            **kwargs: Fields to update.

        Returns:
            Updated group data.
        """
        data = self._http.patch(f"/proposedcontributiongroup/{guid}", json=kwargs)
        return ProposedContributionGroupData.model_validate(data)

    def delete(self, guid: str) -> None:
        """Delete a proposed contribution group.

        Args:
            guid: The group's unique identifier.
        """
        self._http.delete(f"/proposedcontributiongroup/{guid}")

    def add_rate_plan(
        self,
        guid: str,
        rate_plan_guid: str,
    ) -> None:
        """Add a rate plan to the contribution group.

        Args:
            guid: The group's unique identifier.
            rate_plan_guid: The rate plan's GUID.
        """
        self._http.post(
            f"/proposedcontributiongroup/{guid}/rateplan",
            json={"rate_plan_guid": rate_plan_guid},
        )

    def remove_rate_plan(
        self,
        guid: str,
        rate_plan_guid: str,
    ) -> None:
        """Remove a rate plan from the contribution group.

        Args:
            guid: The group's unique identifier.
            rate_plan_guid: The rate plan's GUID.
        """
        self._http.delete(f"/proposedcontributiongroup/{guid}/rateplan/{rate_plan_guid}")


class ProposedContributionTiersResource(BaseResource):
    """Resource for managing proposed contribution tiers."""

    def update(
        self,
        guid: str,
        **kwargs: Any,
    ) -> ProposedContributionTierData:
        """Update a proposed contribution tier.

        Args:
            guid: The tier's unique identifier.
            **kwargs: Fields to update.

        Returns:
            Updated tier data.
        """
        data = self._http.patch(f"/proposedcontributiontier/{guid}", json=kwargs)
        return ProposedContributionTierData.model_validate(data)

    def update_multiple_enrollment(
        self,
        tiers: list[dict[str, Any]],
    ) -> None:
        """Update enrollment for multiple tiers.

        Args:
            tiers: List of dicts with guid and enrollment.
        """
        self._http.post("/proposedcontributiontier/multiple", json=tiers)
