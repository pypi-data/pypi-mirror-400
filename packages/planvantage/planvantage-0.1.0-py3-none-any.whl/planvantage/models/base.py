"""Base model for all PlanVantage models."""

from pydantic import BaseModel, ConfigDict


class PlanVantageModel(BaseModel):
    """Base model with common configuration for all PlanVantage models."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        extra="allow",  # Allow extra fields for forward compatibility
    )
