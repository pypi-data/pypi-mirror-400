"""RatePlan models."""

from enum import Enum
from typing import Any, Optional

from pydantic import Field

from planvantage.models.base import PlanVantageModel


class RateMethod(str, Enum):
    """Rate calculation method."""

    TIER_RATES = "tierRates"
    SINGLE_EE_RATE = "singleEERateWithRatios"


class TierNameSetData(PlanVantageModel):
    """Tier name set configuration."""

    id: Optional[int] = None
    name: Optional[str] = None
    tier_names: Optional[list[str]] = None


class RatePlanTierData(PlanVantageModel):
    """Rate plan tier with rate and enrollment."""

    guid: Optional[str] = None
    rate_plan_guid: Optional[str] = None
    name: Optional[str] = None
    rate: Optional[float] = None
    ratio: Optional[float] = None
    enrollment: Optional[int] = None
    salary_percent: Optional[float] = None
    order: Optional[int] = None
    is_custom: Optional[bool] = None


class RatePlanAdjustmentData(PlanVantageModel):
    """Rate plan adjustment."""

    guid: Optional[str] = None
    rate_plan_guid: Optional[str] = None
    rate_tier_guid: Optional[str] = None
    name: Optional[str] = None
    value: Optional[float] = None
    value_type: Optional[str] = None
    calc_type: Optional[str] = None
    is_credit: Optional[bool] = None
    is_taxable: Optional[bool] = None
    is_contributable: Optional[bool] = None
    order: Optional[int] = None


class RatePlanData(PlanVantageModel):
    """Full rate plan data."""

    guid: Optional[str] = None
    scenario_guid: Optional[str] = None
    plan_design_guid: Optional[str] = None
    name: Optional[str] = None
    rate_method: Optional[RateMethod] = None
    rate: Optional[float] = None
    rate_increase: Optional[float] = None
    rate_basis: Optional[str] = None
    order: Optional[int] = None
    tiers: Optional[list[RatePlanTierData]] = None
    adjustments: Optional[list[RatePlanAdjustmentData]] = None


class RatePlanInput(PlanVantageModel):
    """Input for creating rate plan."""

    scenario_guid: str
    plan_design_guid: Optional[str] = None
    name: Optional[str] = None
    rate_method: Optional[RateMethod] = None
    rate_basis: Optional[str] = None


class RatePlanTierInput(PlanVantageModel):
    """Input for creating rate plan tier."""

    rate_plan_guid: str
    name: Optional[str] = None
    rate: Optional[float] = None
    ratio: Optional[float] = None
    enrollment: Optional[int] = None


class RatePlanAdjustmentInput(PlanVantageModel):
    """Input for creating rate plan adjustment."""

    rate_plan_guid: str
    rate_tier_guid: Optional[str] = None
    name: Optional[str] = None
    value: Optional[float] = None
    value_type: Optional[str] = None
    calc_type: Optional[str] = None
    is_credit: Optional[bool] = None
    is_taxable: Optional[bool] = None
    is_contributable: Optional[bool] = None


class RateModelSettingsData(PlanVantageModel):
    """Rate model display settings."""

    guid: Optional[str] = None
    scenario_guid: Optional[str] = None
    show_tier_ratios: Optional[bool] = None
    show_current_tier_enrollment: Optional[bool] = None
    show_proposed_tier_enrollment: Optional[bool] = None
    show_current_adjustments: Optional[bool] = None
    show_proposed_adjustments: Optional[bool] = None


class RateModelAssumptionsData(PlanVantageModel):
    """Rate model assumptions."""

    guid: Optional[str] = None
    scenario_guid: Optional[str] = None
    rate_increase: Optional[float] = None
    salary_increase: Optional[float] = None
    months: Optional[int] = None


class RatePlanTierNameData(PlanVantageModel):
    """Standard tier name configuration."""

    id: Optional[int] = None
    name: Optional[str] = None


class TierNameSetInput(PlanVantageModel):
    """Input for applying tier name set."""

    tier_name_set_guid: Optional[str] = Field(None, alias="tierNameSetGuid")


class CopyCurrentRatePlanRequest(PlanVantageModel):
    """Request to copy current rate plan to proposed."""

    current_rate_plan_guid: str
