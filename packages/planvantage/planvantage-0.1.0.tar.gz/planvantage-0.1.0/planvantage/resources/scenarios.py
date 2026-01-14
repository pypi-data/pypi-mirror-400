"""Scenarios resource."""

from typing import Any, Optional

from planvantage.models.scenario import (
    CalculateAllOptionsRequest,
    ClaimScenarioRequest,
    ClaimScenarioResponse,
    CreateScenarioFromPlanDocumentRequest,
    CreateScenarioFromPlanDocumentResponse,
    ImportScenarioRequest,
    ScenarioCreateRequest,
    ScenarioData,
    ScenarioHistoryInput,
    ScenarioTierNameSetInput,
    ScenarioUpdateRequest,
    ScenarioUpdateResponse,
    ShareScenarioRequest,
    ShareScenarioResponse,
    SyncEnrollmentRequest,
)
from planvantage.resources.base import BaseResource


class ScenariosResource(BaseResource):
    """Resource for managing scenarios."""

    def get(self, guid: str) -> ScenarioData:
        """Get a specific scenario by GUID.

        Args:
            guid: The scenario's unique identifier.

        Returns:
            Full scenario data.

        Example:
            >>> scenario = client.scenarios.get("sc_abc123")
            >>> print(scenario.name)
        """
        data = self._http.get(f"/scenario/{guid}")
        return ScenarioData.model_validate(data)

    def create(
        self,
        plan_sponsor_guid: str,
        name: Optional[str] = None,
        **kwargs: Any,
    ) -> ScenarioData:
        """Create a new scenario for a plan sponsor.

        Args:
            plan_sponsor_guid: The plan sponsor's GUID.
            name: Optional name for the scenario.
            **kwargs: Additional fields.

        Returns:
            The created scenario data.

        Example:
            >>> scenario = client.scenarios.create(
            ...     plan_sponsor_guid="ps_abc123",
            ...     name="2024 Renewal Analysis"
            ... )
        """
        request = ScenarioCreateRequest(
            name=name,
            plan_sponsor={"guid": plan_sponsor_guid},
            **kwargs,
        )
        data = self._http.post("/scenario", json=self._serialize(request))
        return ScenarioData.model_validate(data)

    def update(
        self,
        guid: str,
        **kwargs: Any,
    ) -> ScenarioUpdateResponse:
        """Update a scenario.

        Args:
            guid: The scenario's unique identifier.
            **kwargs: Fields to update.

        Returns:
            The updated scenario data.

        Example:
            >>> scenario = client.scenarios.update("sc_abc123", name="New Name")
        """
        data = self._http.patch(f"/scenario/{guid}", json=kwargs)
        return ScenarioUpdateResponse.model_validate(data)

    def delete(self, guid: str) -> None:
        """Delete a scenario.

        Args:
            guid: The scenario's unique identifier.

        Example:
            >>> client.scenarios.delete("sc_abc123")
        """
        self._http.delete(f"/scenario/{guid}")

    def clone(self, guid: str) -> ScenarioData:
        """Clone a scenario.

        Args:
            guid: The scenario's unique identifier.

        Returns:
            The cloned scenario data.

        Example:
            >>> cloned = client.scenarios.clone("sc_abc123")
        """
        data = self._http.post(f"/scenario/{guid}/clone")
        return ScenarioData.model_validate(data)

    def apply_tier_name_set(
        self,
        guid: str,
        set_id: int,
        proposed: bool = False,
    ) -> None:
        """Apply a tier name set to the scenario.

        Args:
            guid: The scenario's unique identifier.
            set_id: The tier name set ID.
            proposed: Whether to apply to proposed plans.

        Example:
            >>> client.scenarios.apply_tier_name_set("sc_abc123", set_id=1)
        """
        request = ScenarioTierNameSetInput(set_id=set_id, proposed=proposed)
        self._http.patch(f"/scenario/{guid}/tiernameset", json=self._serialize(request))

    def undo(self, guid: str, model_type: str) -> Any:
        """Undo the last change to a model within the scenario.

        Args:
            guid: The scenario's unique identifier.
            model_type: The type of model to undo changes for.

        Returns:
            The result of the undo operation.

        Example:
            >>> client.scenarios.undo("sc_abc123", "plandesign")
        """
        request = ScenarioHistoryInput(scenario_guid=guid, model_type=model_type)
        return self._http.post("/scenariohistory/undo", json=self._serialize(request))

    def redo(self, guid: str, model_type: str) -> Any:
        """Redo a previously undone change.

        Args:
            guid: The scenario's unique identifier.
            model_type: The type of model to redo changes for.

        Returns:
            The result of the redo operation.

        Example:
            >>> client.scenarios.redo("sc_abc123", "plandesign")
        """
        request = ScenarioHistoryInput(scenario_guid=guid, model_type=model_type)
        return self._http.post("/scenariohistory/redo", json=self._serialize(request))

    def sync_enrollment(
        self,
        guid: str,
        proposed: bool = False,
    ) -> None:
        """Sync enrollment data across rate plans.

        Args:
            guid: The scenario's unique identifier.
            proposed: Whether to sync proposed enrollment.

        Example:
            >>> client.scenarios.sync_enrollment("sc_abc123")
        """
        request = SyncEnrollmentRequest(proposed=proposed)
        self._http.post(f"/scenario/{guid}/syncenrollment", json=self._serialize(request))

    def calculate_all_options(
        self,
        guid: str,
        skip_matching_hashes: bool = True,
    ) -> None:
        """Calculate all contribution options for the scenario.

        Args:
            guid: The scenario's unique identifier.
            skip_matching_hashes: Skip recalculating unchanged options.

        Example:
            >>> client.scenarios.calculate_all_options("sc_abc123")
        """
        request = CalculateAllOptionsRequest(skip_matching_hashes=skip_matching_hashes)
        self._http.post(f"/scenario/{guid}/calculatealloptions", json=self._serialize(request))

    def import_from(
        self,
        plan_sponsor_guid: str,
        source_scenario_guid: str,
    ) -> ScenarioData:
        """Import a scenario from another plan sponsor.

        Args:
            plan_sponsor_guid: The destination plan sponsor's GUID.
            source_scenario_guid: The source scenario's GUID.

        Returns:
            The imported scenario data.

        Example:
            >>> client.scenarios.import_from("ps_dest", "sc_source")
        """
        request = ImportScenarioRequest(scenario_guid=source_scenario_guid)
        data = self._http.post(
            f"/plansponsor/{plan_sponsor_guid}/importscenario",
            json=self._serialize(request),
        )
        return ScenarioData.model_validate(data)

    def create_from_plan_document(
        self,
        plan_sponsor_guid: str,
        plan_document_guid: str,
        name: Optional[str] = None,
    ) -> CreateScenarioFromPlanDocumentResponse:
        """Create a scenario from a plan document.

        Args:
            plan_sponsor_guid: The plan sponsor's GUID.
            plan_document_guid: The plan document's GUID.
            name: Optional name for the scenario.

        Returns:
            Response containing the new scenario GUID.

        Example:
            >>> result = client.scenarios.create_from_plan_document(
            ...     plan_sponsor_guid="ps_abc",
            ...     plan_document_guid="pd_xyz"
            ... )
        """
        request = CreateScenarioFromPlanDocumentRequest(
            plan_document_guid=plan_document_guid,
            name=name,
        )
        data = self._http.post(
            f"/plansponsor/{plan_sponsor_guid}/createscenariofromplandocument",
            json=self._serialize(request),
        )
        return CreateScenarioFromPlanDocumentResponse.model_validate(data)

    def share(
        self,
        guid: str,
        recipient_emails: list[str],
    ) -> ShareScenarioResponse:
        """Share a scenario with other users via email.

        Args:
            guid: The scenario's unique identifier.
            recipient_emails: List of email addresses to share with.

        Returns:
            Response with sharing results for each recipient.

        Example:
            >>> result = client.scenarios.share(
            ...     "sc_abc123",
            ...     recipient_emails=["user@example.com"]
            ... )
        """
        request = ShareScenarioRequest(recipient_emails=recipient_emails)
        data = self._http.post(f"/scenario/{guid}/share", json=self._serialize(request))
        return ShareScenarioResponse.model_validate(data)

    def get_shared(self, token: str) -> Any:
        """Get information about a shared scenario.

        Args:
            token: The share token (scenario GUID).

        Returns:
            Shared scenario information.

        Example:
            >>> info = client.scenarios.get_shared("share_token_xyz")
        """
        return self._http.get(f"/shared/scenario/{token}")

    def claim_shared(
        self,
        token: str,
        plan_sponsor_name: str,
    ) -> ClaimScenarioResponse:
        """Claim a shared scenario and create a copy.

        Args:
            token: The share token (scenario GUID).
            plan_sponsor_name: Name for the new plan sponsor.

        Returns:
            Response with new plan sponsor and scenario GUIDs.

        Example:
            >>> result = client.scenarios.claim_shared(
            ...     "share_token_xyz",
            ...     plan_sponsor_name="My Company"
            ... )
        """
        request = ClaimScenarioRequest(plan_sponsor_name=plan_sponsor_name)
        data = self._http.post(f"/shared/scenario/{token}/claim", json=self._serialize(request))
        return ClaimScenarioResponse.model_validate(data)

    def export(self, guid: str) -> Any:
        """Export a scenario.

        Args:
            guid: The scenario's unique identifier.

        Returns:
            The exported scenario data.

        Example:
            >>> data = client.scenarios.export("sc_abc123")
        """
        return self._http.get(f"/scenario/{guid}/export")
