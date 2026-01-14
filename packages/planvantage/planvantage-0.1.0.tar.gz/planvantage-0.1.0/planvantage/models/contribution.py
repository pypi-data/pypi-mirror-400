"""Contribution models."""

from datetime import datetime
from typing import Any, Optional

from planvantage.models.base import PlanVantageModel


class ContributionTierData(PlanVantageModel):
    """Contribution tier data."""

    guid: Optional[str] = None
    contribution_plan_guid: Optional[str] = None
    rate_plan_tier_guid: Optional[str] = None
    name: Optional[str] = None
    rate: Optional[float] = None
    employer_contribution: Optional[float] = None
    employer_contribution_percent: Optional[float] = None
    employee_contribution: Optional[float] = None
    enrollment: Optional[int] = None
    order: Optional[int] = None


class ContributionPlanData(PlanVantageModel):
    """Contribution plan data."""

    guid: Optional[str] = None
    contribution_group_guid: Optional[str] = None
    rate_plan_guid: Optional[str] = None
    name: Optional[str] = None
    tiers: Optional[list[ContributionTierData]] = None
    order: Optional[int] = None


class ContributionGroupData(PlanVantageModel):
    """Contribution group data."""

    guid: Optional[str] = None
    scenario_guid: Optional[str] = None
    name: Optional[str] = None
    plans: Optional[list[ContributionPlanData]] = None
    order: Optional[int] = None


class ContributionOptionData(PlanVantageModel):
    """Contribution option data."""

    guid: Optional[str] = None
    scenario_guid: Optional[str] = None
    name: Optional[str] = None
    prompt: Optional[str] = None
    contribution_strategy: Optional[str] = None
    contribution_value: Optional[float] = None
    groups: Optional[list[ContributionGroupData]] = None
    status: Optional[str] = None
    is_calculating: Optional[bool] = None
    calc_error: Optional[str] = None
    order: Optional[int] = None


class ContributionTierEnrollmentUpdateData(PlanVantageModel):
    """Data for updating contribution tier enrollment."""

    guid: str
    enrollment: int


class ContributionOptionItem(PlanVantageModel):
    """Contribution option item for import."""

    name: Optional[str] = None
    prompt: Optional[str] = None
    contribution_strategy: Optional[str] = None
    contribution_value: Optional[float] = None


class ContributionOptionImportItem(PlanVantageModel):
    """Item for bulk import of contribution options."""

    name: Optional[str] = None
    prompt: Optional[str] = None
    contribution_strategy: Optional[str] = None
    contribution_value: Optional[float] = None


class ScenarioOptionItems(PlanVantageModel):
    """Scenario options with contribution strategies."""

    contribution_strategies: Optional[list[str]] = None
    prompts: Optional[list[str]] = None


class PlanSponsorItems(PlanVantageModel):
    """Plan sponsor items."""

    prompts: Optional[list[str]] = None


class ContributionOptionItemsLists(PlanVantageModel):
    """Container for contribution option items lists."""

    scenario_items: Optional[ScenarioOptionItems] = None
    plan_sponsor_items: Optional[PlanSponsorItems] = None


class ProposedContributionGroupData(PlanVantageModel):
    """Proposed contribution group data."""

    guid: Optional[str] = None
    contribution_option_guid: Optional[str] = None
    name: Optional[str] = None
    plans: Optional[list[ContributionPlanData]] = None
    order: Optional[float] = None


class ProposedContributionGroupInput(PlanVantageModel):
    """Input for creating proposed contribution group."""

    contribution_option_guid: str
    name: Optional[str] = None
    order: Optional[float] = None


class ProposedContributionTierData(PlanVantageModel):
    """Proposed contribution tier data."""

    guid: Optional[str] = None
    contribution_plan_guid: Optional[str] = None
    rate_plan_tier_guid: Optional[str] = None
    name: Optional[str] = None
    rate: Optional[float] = None
    employer_contribution: Optional[float] = None
    employer_contribution_percent: Optional[float] = None
    employee_contribution: Optional[float] = None
    enrollment: Optional[int] = None
    order: Optional[int] = None


class ProposedContributionTierInput(PlanVantageModel):
    """Input for updating proposed contribution tier."""

    employer_contribution: Optional[float] = None
    employer_contribution_percent: Optional[float] = None
    enrollment: Optional[int] = None


class ProposedContributionTierEnrollmentUpdate(PlanVantageModel):
    """Enrollment update for proposed contribution tier."""

    guid: str
    enrollment: int


class ProposedContributionOptionStatusData(PlanVantageModel):
    """Status data for proposed contribution option."""

    guid: Optional[str] = None
    status: Optional[str] = None
    is_calculating: Optional[bool] = None
    calc_error: Optional[str] = None
    calc_warning: Optional[str] = None
    calc_hash: Optional[str] = None
    updated_at: Optional[datetime] = None
