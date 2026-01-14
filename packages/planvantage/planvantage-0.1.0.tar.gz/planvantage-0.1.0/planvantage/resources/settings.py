"""Settings resources."""

from typing import Any

from planvantage.models.plandesign import PlanModelSettingsData
from planvantage.models.rateplan import (
    RateModelAssumptionsData,
    RateModelSettingsData,
    RatePlanTierNameData,
)
from planvantage.resources.base import BaseResource


class PlanModelSettingsResource(BaseResource):
    """Resource for managing plan model settings."""

    def get(self, guid: str) -> PlanModelSettingsData:
        """Get plan model settings.

        Args:
            guid: The settings' unique identifier.

        Returns:
            Plan model settings data.
        """
        data = self._http.get(f"/planmodelsettings/{guid}")
        return PlanModelSettingsData.model_validate(data)

    def update(
        self,
        guid: str,
        **kwargs: Any,
    ) -> PlanModelSettingsData:
        """Update plan model settings.

        Args:
            guid: The settings' unique identifier.
            **kwargs: Fields to update.

        Returns:
            Updated settings data.
        """
        data = self._http.patch(f"/planmodelsettings/{guid}", json=kwargs)
        return PlanModelSettingsData.model_validate(data)


class RateModelSettingsResource(BaseResource):
    """Resource for managing rate model settings."""

    def get(self, guid: str) -> RateModelSettingsData:
        """Get rate model settings.

        Args:
            guid: The settings' unique identifier.

        Returns:
            Rate model settings data.
        """
        data = self._http.get(f"/ratemodelsettings/{guid}")
        return RateModelSettingsData.model_validate(data)

    def update(
        self,
        guid: str,
        **kwargs: Any,
    ) -> RateModelSettingsData:
        """Update rate model settings.

        Args:
            guid: The settings' unique identifier.
            **kwargs: Fields to update.

        Returns:
            Updated settings data.
        """
        data = self._http.patch(f"/ratemodelsettings/{guid}", json=kwargs)
        return RateModelSettingsData.model_validate(data)


class RateModelAssumptionsResource(BaseResource):
    """Resource for managing rate model assumptions."""

    def get(self, guid: str) -> RateModelAssumptionsData:
        """Get rate model assumptions.

        Args:
            guid: The assumptions' unique identifier.

        Returns:
            Rate model assumptions data.
        """
        data = self._http.get(f"/ratemodelassumptions/{guid}")
        return RateModelAssumptionsData.model_validate(data)

    def update(
        self,
        guid: str,
        **kwargs: Any,
    ) -> RateModelAssumptionsData:
        """Update rate model assumptions.

        Args:
            guid: The assumptions' unique identifier.
            **kwargs: Fields to update.

        Returns:
            Updated assumptions data.
        """
        data = self._http.patch(f"/ratemodelassumptions/{guid}", json=kwargs)
        return RateModelAssumptionsData.model_validate(data)


class RatePlanTierNamesResource(BaseResource):
    """Resource for accessing standard tier names."""

    def list(self) -> list[RatePlanTierNameData]:
        """Get standard rate plan tier names.

        Returns:
            List of standard tier names.

        Example:
            >>> tier_names = client.tier_names.list()
        """
        data = self._http.get("/rateplantiernames")
        if isinstance(data, list):
            return [RatePlanTierNameData.model_validate(item) for item in data]
        return []
