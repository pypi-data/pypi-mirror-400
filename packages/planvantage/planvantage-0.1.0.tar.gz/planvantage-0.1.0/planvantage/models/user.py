"""User models."""

from typing import Optional

from planvantage.models.base import PlanVantageModel


class LimitedUserInput(PlanVantageModel):
    """Limited user input for invitations."""

    email: str
    name: Optional[str] = None
