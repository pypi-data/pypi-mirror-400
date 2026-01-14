"""Resource classes for PlanVantage API."""

from planvantage.resources.base import BaseResource
from planvantage.resources.plansponsors import PlanSponsorsResource
from planvantage.resources.scenarios import ScenariosResource
from planvantage.resources.plandesigns import PlanDesignsResource
from planvantage.resources.rateplans import (
    CurrentRatePlansResource,
    ProposedRatePlansResource,
    CurrentRatePlanTiersResource,
    ProposedRatePlanTiersResource,
    CurrentRatePlanAdjustmentsResource,
    ProposedRatePlanAdjustmentsResource,
)
from planvantage.resources.contributions import (
    CurrentContributionGroupsResource,
    CurrentContributionTiersResource,
    ProposedContributionOptionsResource,
    ProposedContributionGroupsResource,
    ProposedContributionTiersResource,
)
from planvantage.resources.plandocuments import PlanDocumentsResource
from planvantage.resources.chat import ChatsResource, ChatMessagesResource
from planvantage.resources.benchmarks import BenchmarksResource
from planvantage.resources.settings import (
    PlanModelSettingsResource,
    RateModelSettingsResource,
    RateModelAssumptionsResource,
    RatePlanTierNamesResource,
)

__all__ = [
    "BaseResource",
    "PlanSponsorsResource",
    "ScenariosResource",
    "PlanDesignsResource",
    "CurrentRatePlansResource",
    "ProposedRatePlansResource",
    "CurrentRatePlanTiersResource",
    "ProposedRatePlanTiersResource",
    "CurrentRatePlanAdjustmentsResource",
    "ProposedRatePlanAdjustmentsResource",
    "CurrentContributionGroupsResource",
    "CurrentContributionTiersResource",
    "ProposedContributionOptionsResource",
    "ProposedContributionGroupsResource",
    "ProposedContributionTiersResource",
    "PlanDocumentsResource",
    "ChatsResource",
    "ChatMessagesResource",
    "BenchmarksResource",
    "PlanModelSettingsResource",
    "RateModelSettingsResource",
    "RateModelAssumptionsResource",
    "RatePlanTierNamesResource",
]
