"""PlanSponsor models."""

from datetime import datetime
from typing import Optional

from planvantage.models.base import PlanVantageModel


class PlanSponsorInfo(PlanVantageModel):
    """Summary information about a plan sponsor."""

    guid: str
    name: str
    updated_at: datetime


class PlanSponsorData(PlanVantageModel):
    """Full plan sponsor data including related objects."""

    guid: str
    name: str
    scenarios: Optional[list["ScenarioInfo"]] = None
    plan_documents: Optional[list["PlanDocumentInfo"]] = None


class PlanSponsorCreateRequest(PlanVantageModel):
    """Request to create a new plan sponsor."""

    name: str


class PlanSponsorUpdateRequest(PlanVantageModel):
    """Request to update a plan sponsor."""

    name: Optional[str] = None


# Forward references
from planvantage.models.scenario import ScenarioInfo  # noqa: E402
from planvantage.models.plandocument import PlanDocumentInfo  # noqa: E402

PlanSponsorData.model_rebuild()
