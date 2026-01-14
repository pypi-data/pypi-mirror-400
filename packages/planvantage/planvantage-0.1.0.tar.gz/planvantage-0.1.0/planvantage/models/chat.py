"""Chat models."""

from datetime import datetime
from typing import Any, Optional

from planvantage.models.base import PlanVantageModel


class ChatInfo(PlanVantageModel):
    """Summary information about a chat."""

    guid: str
    name: Optional[str] = None
    plan_sponsor_guid: Optional[str] = None
    scenario_guid: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
