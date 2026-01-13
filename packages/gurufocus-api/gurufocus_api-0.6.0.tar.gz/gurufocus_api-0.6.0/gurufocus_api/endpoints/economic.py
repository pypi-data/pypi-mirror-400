"""Endpoints for economic data and financial calendar.

This module provides access to economic data endpoints:
- GET /economicindicators - List available economic indicators
- GET /economicindicators/item/{indicator} - Data for a specific indicator
- GET /calendar - Financial calendar events
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, cast

from gurufocus_api.cache.config import CacheCategory
from gurufocus_api.models.economic import (
    CalendarResponse,
    EconomicIndicatorResponse,
    EconomicIndicatorsListResponse,
)

if TYPE_CHECKING:
    from gurufocus_api.client import GuruFocusClient


class EconomicEndpoint:
    """Endpoints for economic data and financial calendar."""

    def __init__(self, client: GuruFocusClient) -> None:
        """Initialize the EconomicEndpoint.

        Args:
            client: The GuruFocusClient instance
        """
        self._client = client

    # --- GET /economicindicators ---

    async def get_indicators_list(
        self,
        *,
        bypass_cache: bool = False,
    ) -> EconomicIndicatorsListResponse:
        """Get list of available economic indicators.

        Returns a list of economic indicator names that can be queried
        with get_indicator().

        Args:
            bypass_cache: If True, skip cache lookup

        Returns:
            EconomicIndicatorsListResponse with list of indicator names
        """
        data = await self.get_indicators_list_raw(bypass_cache=bypass_cache)
        return EconomicIndicatorsListResponse.from_api_response(data)

    async def get_indicators_list_raw(
        self,
        *,
        bypass_cache: bool = False,
    ) -> list[str]:
        """Get raw list of available economic indicators.

        Args:
            bypass_cache: If True, skip cache lookup

        Returns:
            Raw API response list of indicator names
        """
        cache = self._client.cache
        cache_key = "all"

        if not bypass_cache:
            cached_data = await cache.get(CacheCategory.ECONOMIC_INDICATORS_LIST, cache_key)
            if cached_data is not None:
                return cast(list[str], cached_data)

        data = await self._client.get("economicindicators")
        await cache.set(CacheCategory.ECONOMIC_INDICATORS_LIST, cache_key, value=data)
        return cast(list[str], data)

    # --- GET /economicindicators/item/{indicator} ---

    async def get_indicator(
        self,
        indicator: str,
        *,
        bypass_cache: bool = False,
    ) -> EconomicIndicatorResponse:
        """Get data for a specific economic indicator.

        Args:
            indicator: Name of the economic indicator
            bypass_cache: If True, skip cache lookup

        Returns:
            EconomicIndicatorResponse with time series data
        """
        data = await self.get_indicator_raw(indicator, bypass_cache=bypass_cache)
        return EconomicIndicatorResponse.from_api_response(data)

    async def get_indicator_raw(
        self,
        indicator: str,
        *,
        bypass_cache: bool = False,
    ) -> dict[str, Any]:
        """Get raw data for a specific economic indicator.

        Args:
            indicator: Name of the economic indicator
            bypass_cache: If True, skip cache lookup

        Returns:
            Raw API response dict
        """
        cache = self._client.cache
        cache_key = indicator

        if not bypass_cache:
            cached_data = await cache.get(CacheCategory.ECONOMIC_INDICATOR_ITEM, cache_key)
            if cached_data is not None:
                return cast(dict[str, Any], cached_data)

        data = await self._client.get(f"economicindicators/item/{indicator}")
        await cache.set(CacheCategory.ECONOMIC_INDICATOR_ITEM, cache_key, value=data)
        return cast(dict[str, Any], data)

    # --- GET /calendar ---

    async def get_calendar(
        self,
        date: str,
        event_type: Literal["all", "economic", "ipo", "earning", "dividend", "split"] = "all",
        *,
        bypass_cache: bool = False,
    ) -> CalendarResponse:
        """Get financial calendar events for a specific date.

        Args:
            date: Date in YYYY-MM-DD format
            event_type: Type of events to include (default: all)
            bypass_cache: If True, skip cache lookup

        Returns:
            CalendarResponse with events by category
        """
        data = await self.get_calendar_raw(date, event_type, bypass_cache=bypass_cache)
        return CalendarResponse.from_api_response(data)

    async def get_calendar_raw(
        self,
        date: str,
        event_type: Literal["all", "economic", "ipo", "earning", "dividend", "split"] = "all",
        *,
        bypass_cache: bool = False,
    ) -> dict[str, Any]:
        """Get raw financial calendar events.

        Args:
            date: Date in YYYY-MM-DD format
            event_type: Type of events to include (default: all)
            bypass_cache: If True, skip cache lookup

        Returns:
            Raw API response dict
        """
        cache = self._client.cache
        cache_key = f"{date}:{event_type}"

        if not bypass_cache:
            cached_data = await cache.get(CacheCategory.CALENDAR, cache_key)
            if cached_data is not None:
                return cast(dict[str, Any], cached_data)

        params: dict[str, Any] = {"date": date}
        if event_type != "all":
            params["type"] = event_type

        data = await self._client.get("calendar", params=params)
        await cache.set(CacheCategory.CALENDAR, cache_key, value=data)
        return cast(dict[str, Any], data)
