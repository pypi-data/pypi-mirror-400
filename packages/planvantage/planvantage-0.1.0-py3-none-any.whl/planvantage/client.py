"""Main PlanVantage client."""

from typing import Optional

from planvantage.auth import AuthConfig
from planvantage.http import HTTPClient
from planvantage.resources.plansponsors import PlanSponsorsResource
from planvantage.resources.scenarios import ScenariosResource
from planvantage.resources.plandesigns import (
    PlanDesignsResource,
    PlanDesignTiersResource,
    ServiceCostSharesResource,
)
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


class PlanVantageClient:
    """Client for interacting with the PlanVantage API.

    The client provides access to all PlanVantage API resources through
    intuitive, namespaced properties.

    Example:
        >>> from planvantage import PlanVantageClient
        >>>
        >>> # Initialize with API key
        >>> client = PlanVantageClient(api_key="pv_live_...")
        >>>
        >>> # Or use environment variable PLANVANTAGE_API_KEY
        >>> client = PlanVantageClient()
        >>>
        >>> # List all plan sponsors
        >>> sponsors = client.plansponsors.list()
        >>> for sponsor in sponsors:
        ...     print(sponsor.name)
        >>>
        >>> # Get a specific scenario
        >>> scenario = client.scenarios.get("sc_abc123")
        >>>
        >>> # Create a new plan design
        >>> plan = client.plandesigns.create(
        ...     scenario_guid="sc_abc123",
        ...     name="Gold PPO"
        ... )

    Args:
        api_key: Your PlanVantage API key. Falls back to PLANVANTAGE_API_KEY
            environment variable if not provided.
        base_url: API base URL. Falls back to PLANVANTAGE_BASE_URL environment
            variable, then to https://api.planvantage.ai
        timeout: Request timeout in seconds. Defaults to 30.
        max_retries: Maximum retry attempts for transient failures. Defaults to 3.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        """Initialize the PlanVantage client."""
        self._auth = AuthConfig.from_env(api_key=api_key, base_url=base_url)
        self._http = HTTPClient(
            auth=self._auth,
            timeout=timeout,
            max_retries=max_retries,
        )

        # Initialize resource instances
        self._plansponsors: Optional[PlanSponsorsResource] = None
        self._scenarios: Optional[ScenariosResource] = None
        self._plandesigns: Optional[PlanDesignsResource] = None
        self._plandesign_tiers: Optional[PlanDesignTiersResource] = None
        self._service_cost_shares: Optional[ServiceCostSharesResource] = None
        self._current_rate_plans: Optional[CurrentRatePlansResource] = None
        self._proposed_rate_plans: Optional[ProposedRatePlansResource] = None
        self._current_rate_plan_tiers: Optional[CurrentRatePlanTiersResource] = None
        self._proposed_rate_plan_tiers: Optional[ProposedRatePlanTiersResource] = None
        self._current_rate_plan_adjustments: Optional[CurrentRatePlanAdjustmentsResource] = None
        self._proposed_rate_plan_adjustments: Optional[ProposedRatePlanAdjustmentsResource] = None
        self._current_contribution_groups: Optional[CurrentContributionGroupsResource] = None
        self._current_contribution_tiers: Optional[CurrentContributionTiersResource] = None
        self._proposed_contribution_options: Optional[ProposedContributionOptionsResource] = None
        self._proposed_contribution_groups: Optional[ProposedContributionGroupsResource] = None
        self._proposed_contribution_tiers: Optional[ProposedContributionTiersResource] = None
        self._plandocuments: Optional[PlanDocumentsResource] = None
        self._chats: Optional[ChatsResource] = None
        self._chat_messages: Optional[ChatMessagesResource] = None
        self._benchmarks: Optional[BenchmarksResource] = None
        self._plan_model_settings: Optional[PlanModelSettingsResource] = None
        self._rate_model_settings: Optional[RateModelSettingsResource] = None
        self._rate_model_assumptions: Optional[RateModelAssumptionsResource] = None
        self._tier_names: Optional[RatePlanTierNamesResource] = None

    def close(self) -> None:
        """Close the client and release resources."""
        self._http.close()

    def __enter__(self) -> "PlanVantageClient":
        """Enter context manager."""
        return self

    def __exit__(self, *args: object) -> None:
        """Exit context manager."""
        self.close()

    # Resource properties with lazy initialization

    @property
    def plansponsors(self) -> PlanSponsorsResource:
        """Access plan sponsors resource.

        Example:
            >>> sponsors = client.plansponsors.list()
            >>> sponsor = client.plansponsors.get("ps_abc123")
        """
        if self._plansponsors is None:
            self._plansponsors = PlanSponsorsResource(self._http)
        return self._plansponsors

    @property
    def scenarios(self) -> ScenariosResource:
        """Access scenarios resource.

        Example:
            >>> scenario = client.scenarios.get("sc_abc123")
            >>> scenario = client.scenarios.create(
            ...     plan_sponsor_guid="ps_abc123",
            ...     name="2024 Renewal"
            ... )
        """
        if self._scenarios is None:
            self._scenarios = ScenariosResource(self._http)
        return self._scenarios

    @property
    def plandesigns(self) -> PlanDesignsResource:
        """Access plan designs resource.

        Example:
            >>> plan = client.plandesigns.get("pd_abc123")
            >>> plan = client.plandesigns.create(
            ...     scenario_guid="sc_abc123",
            ...     name="Gold PPO"
            ... )
        """
        if self._plandesigns is None:
            self._plandesigns = PlanDesignsResource(self._http)
        return self._plandesigns

    @property
    def plandesign_tiers(self) -> PlanDesignTiersResource:
        """Access plan design tiers resource."""
        if self._plandesign_tiers is None:
            self._plandesign_tiers = PlanDesignTiersResource(self._http)
        return self._plandesign_tiers

    @property
    def service_cost_shares(self) -> ServiceCostSharesResource:
        """Access service cost shares resource."""
        if self._service_cost_shares is None:
            self._service_cost_shares = ServiceCostSharesResource(self._http)
        return self._service_cost_shares

    @property
    def current_rate_plans(self) -> CurrentRatePlansResource:
        """Access current rate plans resource."""
        if self._current_rate_plans is None:
            self._current_rate_plans = CurrentRatePlansResource(self._http)
        return self._current_rate_plans

    @property
    def proposed_rate_plans(self) -> ProposedRatePlansResource:
        """Access proposed rate plans resource."""
        if self._proposed_rate_plans is None:
            self._proposed_rate_plans = ProposedRatePlansResource(self._http)
        return self._proposed_rate_plans

    @property
    def current_rate_plan_tiers(self) -> CurrentRatePlanTiersResource:
        """Access current rate plan tiers resource."""
        if self._current_rate_plan_tiers is None:
            self._current_rate_plan_tiers = CurrentRatePlanTiersResource(self._http)
        return self._current_rate_plan_tiers

    @property
    def proposed_rate_plan_tiers(self) -> ProposedRatePlanTiersResource:
        """Access proposed rate plan tiers resource."""
        if self._proposed_rate_plan_tiers is None:
            self._proposed_rate_plan_tiers = ProposedRatePlanTiersResource(self._http)
        return self._proposed_rate_plan_tiers

    @property
    def current_rate_plan_adjustments(self) -> CurrentRatePlanAdjustmentsResource:
        """Access current rate plan adjustments resource."""
        if self._current_rate_plan_adjustments is None:
            self._current_rate_plan_adjustments = CurrentRatePlanAdjustmentsResource(self._http)
        return self._current_rate_plan_adjustments

    @property
    def proposed_rate_plan_adjustments(self) -> ProposedRatePlanAdjustmentsResource:
        """Access proposed rate plan adjustments resource."""
        if self._proposed_rate_plan_adjustments is None:
            self._proposed_rate_plan_adjustments = ProposedRatePlanAdjustmentsResource(self._http)
        return self._proposed_rate_plan_adjustments

    @property
    def current_contribution_groups(self) -> CurrentContributionGroupsResource:
        """Access current contribution groups resource."""
        if self._current_contribution_groups is None:
            self._current_contribution_groups = CurrentContributionGroupsResource(self._http)
        return self._current_contribution_groups

    @property
    def current_contribution_tiers(self) -> CurrentContributionTiersResource:
        """Access current contribution tiers resource."""
        if self._current_contribution_tiers is None:
            self._current_contribution_tiers = CurrentContributionTiersResource(self._http)
        return self._current_contribution_tiers

    @property
    def proposed_contribution_options(self) -> ProposedContributionOptionsResource:
        """Access proposed contribution options resource."""
        if self._proposed_contribution_options is None:
            self._proposed_contribution_options = ProposedContributionOptionsResource(self._http)
        return self._proposed_contribution_options

    @property
    def proposed_contribution_groups(self) -> ProposedContributionGroupsResource:
        """Access proposed contribution groups resource."""
        if self._proposed_contribution_groups is None:
            self._proposed_contribution_groups = ProposedContributionGroupsResource(self._http)
        return self._proposed_contribution_groups

    @property
    def proposed_contribution_tiers(self) -> ProposedContributionTiersResource:
        """Access proposed contribution tiers resource."""
        if self._proposed_contribution_tiers is None:
            self._proposed_contribution_tiers = ProposedContributionTiersResource(self._http)
        return self._proposed_contribution_tiers

    @property
    def plandocuments(self) -> PlanDocumentsResource:
        """Access plan documents resource.

        Example:
            >>> doc = client.plandocuments.get("doc_abc123")
            >>> with open("plan.pdf", "rb") as f:
            ...     doc = client.plandocuments.upload(
            ...         plan_sponsor_guid="ps_abc123",
            ...         file=f
            ...     )
        """
        if self._plandocuments is None:
            self._plandocuments = PlanDocumentsResource(self._http)
        return self._plandocuments

    @property
    def chats(self) -> ChatsResource:
        """Access chats resource."""
        if self._chats is None:
            self._chats = ChatsResource(self._http)
        return self._chats

    @property
    def chat_messages(self) -> ChatMessagesResource:
        """Access chat messages resource."""
        if self._chat_messages is None:
            self._chat_messages = ChatMessagesResource(self._http)
        return self._chat_messages

    @property
    def benchmarks(self) -> BenchmarksResource:
        """Access benchmarks resource.

        Example:
            >>> hierarchy = client.benchmarks.get_hierarchy()
            >>> benchmark = client.benchmarks.get("bm_abc123")
        """
        if self._benchmarks is None:
            self._benchmarks = BenchmarksResource(self._http)
        return self._benchmarks

    @property
    def plan_model_settings(self) -> PlanModelSettingsResource:
        """Access plan model settings resource."""
        if self._plan_model_settings is None:
            self._plan_model_settings = PlanModelSettingsResource(self._http)
        return self._plan_model_settings

    @property
    def rate_model_settings(self) -> RateModelSettingsResource:
        """Access rate model settings resource."""
        if self._rate_model_settings is None:
            self._rate_model_settings = RateModelSettingsResource(self._http)
        return self._rate_model_settings

    @property
    def rate_model_assumptions(self) -> RateModelAssumptionsResource:
        """Access rate model assumptions resource."""
        if self._rate_model_assumptions is None:
            self._rate_model_assumptions = RateModelAssumptionsResource(self._http)
        return self._rate_model_assumptions

    @property
    def tier_names(self) -> RatePlanTierNamesResource:
        """Access tier names resource.

        Example:
            >>> tier_names = client.tier_names.list()
        """
        if self._tier_names is None:
            self._tier_names = RatePlanTierNamesResource(self._http)
        return self._tier_names
