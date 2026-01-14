"""Scenario models."""

from datetime import datetime
from typing import Any, Optional

from pydantic import Field

from planvantage.models.base import PlanVantageModel


class ScenarioInfo(PlanVantageModel):
    """Summary information about a scenario."""

    guid: str
    name: str
    order: Optional[float] = None
    updated_at: Optional[datetime] = None


class ScenarioData(PlanVantageModel):
    """Full scenario data - uses additionalProperties so we accept any fields."""

    guid: Optional[str] = None
    name: Optional[str] = None
    order: Optional[float] = None
    # Additional fields will be accepted via extra="allow" in base config


class ScenarioCreateRequest(PlanVantageModel):
    """Request to create a new scenario."""

    name: Optional[str] = None
    plan_sponsor: dict[str, str]  # {"guid": "..."}


class ScenarioUpdateRequest(PlanVantageModel):
    """Request to update a scenario. Accepts any fields."""

    pass  # additionalProperties: true


class ScenarioUpdateResponse(PlanVantageModel):
    """Response from updating a scenario."""

    name: Optional[str] = None
    guid: Optional[str] = None
    order: Optional[float] = None
    current_section_name: Optional[str] = None
    proposed_section_name: Optional[str] = None
    selected_contribution_option_guid: Optional[str] = None


class ScenarioTierNameSetInput(PlanVantageModel):
    """Input for applying tier name set to scenario."""

    proposed: Optional[bool] = None
    set_id: Optional[int] = None


class ScenarioHistoryInput(PlanVantageModel):
    """Input for undo/redo operations."""

    scenario_guid: str
    model_type: str


class SyncEnrollmentRequest(PlanVantageModel):
    """Request to sync enrollment data."""

    proposed: Optional[bool] = None


class CalculateAllOptionsRequest(PlanVantageModel):
    """Request to calculate all contribution options."""

    skip_matching_hashes: Optional[bool] = None


class ImportScenarioRequest(PlanVantageModel):
    """Request to import a scenario."""

    scenario_guid: str


class CreateScenarioFromPlanDocumentRequest(PlanVantageModel):
    """Request to create scenario from plan document."""

    plan_document_guid: str
    name: Optional[str] = None


class CreateScenarioFromPlanDocumentResponse(PlanVantageModel):
    """Response from creating scenario from plan document."""

    scenario_guid: Optional[str] = None


class ShareScenarioRequest(PlanVantageModel):
    """Request to share a scenario."""

    recipient_emails: list[str]


class ShareScenarioEmailResult(PlanVantageModel):
    """Result of sharing scenario with a single recipient."""

    email: Optional[str] = None
    success: Optional[bool] = None
    message: Optional[str] = None


class ShareScenarioResponse(PlanVantageModel):
    """Response from sharing a scenario."""

    results: Optional[list[ShareScenarioEmailResult]] = None
    summary: Optional[dict[str, int]] = None


class SharedScenarioPreview(PlanVantageModel):
    """Preview information for a shared scenario."""

    user_email: Optional[str] = None
    user_guid: Optional[str] = None
    plan_sponsor_name: Optional[str] = None
    scenario_name: Optional[str] = None
    current_plan_names: Optional[list[str]] = None
    proposed_plan_names: Optional[list[str]] = None
    recipient_email: Optional[str] = None
    expiration_date: Optional[datetime] = None
    last_used_date: Optional[datetime] = None


class ClaimScenarioRequest(PlanVantageModel):
    """Request to claim a shared scenario."""

    plan_sponsor_name: str


class ClaimScenarioResponse(PlanVantageModel):
    """Response from claiming a scenario."""

    message: Optional[str] = None
    plan_sponsor_guid: Optional[str] = None
    scenario_guid: Optional[str] = None


