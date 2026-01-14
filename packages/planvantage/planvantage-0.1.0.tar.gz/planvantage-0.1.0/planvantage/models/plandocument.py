"""PlanDocument models."""

from datetime import datetime
from typing import Any, Optional

from planvantage.models.base import PlanVantageModel


class PlanDocumentInfo(PlanVantageModel):
    """Summary information about a plan document."""

    guid: str
    filename: str
    status: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    plan_sponsor_guid: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PlanDocumentData(PlanVantageModel):
    """Full plan document data."""

    guid: Optional[str] = None
    filename: Optional[str] = None
    status: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    plan_sponsor_guid: Optional[str] = None
    extracted_data: Optional[dict[str, Any]] = None
    extraction_status: Optional[str] = None
    extraction_error: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PlanDocumentInput(PlanVantageModel):
    """Input for creating plan document."""

    plan_sponsor_guid: str
    filename: Optional[str] = None
