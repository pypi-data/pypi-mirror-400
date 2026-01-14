"""PlanDesign models."""

from typing import Any, Optional

from pydantic import Field

from planvantage.models.base import PlanVantageModel


class ServiceCostShareData(PlanVantageModel):
    """Service cost sharing configuration."""

    guid: Optional[str] = Field(None, alias="GUID")
    plan_design_tier_guid: Optional[str] = Field(None, alias="PlanDesignTierGUID")
    service: Optional[str] = Field(None, alias="Service")
    copay: Optional[float] = Field(None, alias="Copay")
    coins: Optional[float] = Field(None, alias="Coins")
    ded_applies: Optional[bool] = Field(None, alias="DedApplies")
    per_diem: Optional[bool] = Field(None, alias="PerDiem")
    min_amt: Optional[float] = Field(None, alias="MinAmt")
    max_amt: Optional[float] = Field(None, alias="MaxAmt")


class PlanDesignTierData(PlanVantageModel):
    """Plan design tier configuration."""

    guid: Optional[str] = None
    plan_design_guid: Optional[str] = None
    name: Optional[str] = None
    discount_percent: Optional[float] = None
    utilization_percent: Optional[float] = None
    ind_ded: Optional[float] = None
    fam_ded: Optional[float] = None
    ind_oopm: Optional[float] = None
    fam_oopm: Optional[float] = None
    ded_type_family: Optional[bool] = None
    oopm_type_family: Optional[bool] = None
    fam_embd_ind_ded: Optional[float] = None
    fam_embd_ind_oopm: Optional[float] = None
    rx_ded_applies: Optional[bool] = None
    rx_ind_ded: Optional[float] = None
    rx_fam_ded: Optional[float] = None
    rx_oopm_applies: Optional[bool] = None
    rx_ind_oopm: Optional[float] = None
    rx_fam_oopm: Optional[float] = None
    rx_embd_ind_ded: Optional[float] = None
    rx_embd_ind_oopm: Optional[float] = None
    coinsurance: Optional[float] = None
    service_cost_sharing: Optional[dict[str, ServiceCostShareData]] = None


class PlanAvResultData(PlanVantageModel):
    """Actuarial value calculation result."""

    guid: Optional[str] = None
    av: Optional[float] = Field(None, alias="AV")
    av_with_fund: Optional[float] = Field(None, alias="AVWithFund")
    paid_amt: Optional[float] = Field(None, alias="PaidAmt")
    paid_amt_with_fund: Optional[float] = Field(None, alias="PaidAmtWithFund")
    allowed_amt: Optional[float] = Field(None, alias="AllowedAmt")
    av_version: Optional[str] = Field(None, alias="AVVersion")


class PlanDesignData(PlanVantageModel):
    """Full plan design data."""

    guid: Optional[str] = None
    scenario_guid: Optional[str] = None
    benchmark_guid: Optional[str] = None
    name: Optional[str] = None
    carrier: Optional[str] = None
    order: Optional[float] = None
    color: Optional[str] = None
    tiers: Optional[list[PlanDesignTierData]] = None
    plan_av_result: Optional[PlanAvResultData] = None
    hsa_seed_ind: Optional[float] = None
    hsa_seed_fam: Optional[float] = None
    hra_fund_ind: Optional[float] = None
    hra_fund_fam: Optional[float] = None
    hra_first_dollar: Optional[bool] = None
    hra_forfeiture_pct: Optional[float] = None


class PlanModelSettingsData(PlanVantageModel):
    """Plan model display settings."""

    guid: Optional[str] = None
    scenario_guid: Optional[str] = None
    show_deductible_type: Optional[bool] = None
    show_rx_deductible: Optional[bool] = None
    show_network_discount: Optional[bool] = None
    show_hra_funding: Optional[bool] = None
    show_hra_forfeiture: Optional[bool] = None
    show_oopm_type: Optional[bool] = None
    show_rx_oopm: Optional[bool] = None
    show_tier_utilization: Optional[bool] = None
    show_hsa_funding: Optional[bool] = None
    show_additional_services: Optional[bool] = None
    hide_compliance_checks: Optional[bool] = None
    compliance_year: Optional[int] = None


class PlanDesignTierUtilizationData(PlanVantageModel):
    """Tier utilization data."""

    guid: Optional[str] = None
    utilization_percent: Optional[float] = None


class PlanDesignUtilizationData(PlanVantageModel):
    """Plan design utilization update."""

    tiers: Optional[list[PlanDesignTierUtilizationData]] = None


class CopyPlanDesignRequest(PlanVantageModel):
    """Request to copy a plan design."""

    source_plan_design_guid: str
