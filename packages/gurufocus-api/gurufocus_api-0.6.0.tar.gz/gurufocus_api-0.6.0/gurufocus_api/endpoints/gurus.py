"""Endpoints for guru/institutional investor data.

This module provides access to guru-related endpoints:
- GET /gurulist - List all tracked gurus
- GET /guru/{id}/picks/{start_date}/{page} - Guru's stock picks
- GET /guru/{id}/aggregated - Guru's aggregated portfolio
- GET /guru_realtime_picks - Real-time guru activity feed
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from gurufocus_api.cache.config import CacheCategory
from gurufocus_api.models.gurus import (
    GuruAggregatedPortfolio,
    GuruListResponse,
    GuruPicksResponse,
    GuruRealtimePicksResponse,
)

if TYPE_CHECKING:
    from gurufocus_api.client import GuruFocusClient


class GurusEndpoint:
    """Endpoints for guru/institutional investor data."""

    def __init__(self, client: GuruFocusClient) -> None:
        """Initialize the GurusEndpoint.

        Args:
            client: The GuruFocusClient instance
        """
        self._client = client

    # --- GET /gurulist ---

    async def get_gurulist(
        self,
        *,
        bypass_cache: bool = False,
    ) -> GuruListResponse:
        """Get list of all tracked institutional gurus.

        This is a large dataset (~2.6MB) containing all tracked gurus
        with their portfolio statistics.

        Args:
            bypass_cache: If True, skip cache lookup

        Returns:
            GuruListResponse with US and Plus gurus
        """
        data = await self.get_gurulist_raw(bypass_cache=bypass_cache)
        return GuruListResponse.from_api_response(data)

    async def get_gurulist_raw(
        self,
        *,
        bypass_cache: bool = False,
    ) -> dict[str, Any]:
        """Get raw list of all tracked institutional gurus.

        Args:
            bypass_cache: If True, skip cache lookup

        Returns:
            Raw API response dict
        """
        cache = self._client.cache
        cache_key = "all"

        if not bypass_cache:
            cached_data = await cache.get(CacheCategory.GURU_LIST, cache_key)
            if cached_data is not None:
                return cast(dict[str, Any], cached_data)

        data = await self._client.get("gurulist")
        await cache.set(CacheCategory.GURU_LIST, cache_key, value=data)
        return cast(dict[str, Any], data)

    # --- GET /guru/{id}/picks/{start_date}/{page} ---

    async def get_guru_picks(
        self,
        guru_id: str,
        start_date: str = "all",
        page: int = 1,
        *,
        bypass_cache: bool = False,
    ) -> GuruPicksResponse:
        """Get a guru's stock picks.

        Args:
            guru_id: Guru identifier (numeric ID)
            start_date: Start date filter (YYYY-MM-DD format) or "all" for all picks
            page: Page number for pagination (1-indexed)
            bypass_cache: If True, skip cache lookup

        Returns:
            GuruPicksResponse with the guru's stock picks
        """
        data = await self.get_guru_picks_raw(guru_id, start_date, page, bypass_cache=bypass_cache)
        return GuruPicksResponse.from_api_response(data, guru_id)

    async def get_guru_picks_raw(
        self,
        guru_id: str,
        start_date: str = "all",
        page: int = 1,
        *,
        bypass_cache: bool = False,
    ) -> dict[str, Any]:
        """Get raw guru stock picks data.

        Args:
            guru_id: Guru identifier (numeric ID)
            start_date: Start date filter (YYYY-MM-DD format) or "all" for all picks
            page: Page number for pagination (1-indexed)
            bypass_cache: If True, skip cache lookup

        Returns:
            Raw API response dict
        """
        guru_id = str(guru_id).strip()
        cache = self._client.cache
        cache_key = f"{guru_id}:{start_date}:{page}"

        if not bypass_cache:
            cached_data = await cache.get(CacheCategory.GURU_PICKS, cache_key)
            if cached_data is not None:
                return cast(dict[str, Any], cached_data)

        data = await self._client.get(f"guru/{guru_id}/picks/{start_date}/{page}")
        await cache.set(CacheCategory.GURU_PICKS, cache_key, value=data)
        return cast(dict[str, Any], data)

    # --- GET /guru/{id}/aggregated ---

    async def get_guru_aggregated(
        self,
        guru_id: str,
        *,
        bypass_cache: bool = False,
    ) -> GuruAggregatedPortfolio:
        """Get a guru's aggregated portfolio.

        Returns the full portfolio with summary statistics and all holdings.

        Args:
            guru_id: Guru identifier (numeric ID)
            bypass_cache: If True, skip cache lookup

        Returns:
            GuruAggregatedPortfolio with summary and holdings
        """
        data = await self.get_guru_aggregated_raw(guru_id, bypass_cache=bypass_cache)
        return GuruAggregatedPortfolio.from_api_response(data, guru_id)

    async def get_guru_aggregated_raw(
        self,
        guru_id: str,
        *,
        bypass_cache: bool = False,
    ) -> dict[str, Any]:
        """Get raw guru aggregated portfolio data.

        Args:
            guru_id: Guru identifier (numeric ID)
            bypass_cache: If True, skip cache lookup

        Returns:
            Raw API response dict
        """
        guru_id = str(guru_id).strip()
        cache = self._client.cache
        cache_key = guru_id

        if not bypass_cache:
            cached_data = await cache.get(CacheCategory.GURU_AGGREGATED, cache_key)
            if cached_data is not None:
                return cast(dict[str, Any], cached_data)

        data = await self._client.get(f"guru/{guru_id}/aggregated")
        await cache.set(CacheCategory.GURU_AGGREGATED, cache_key, value=data)
        return cast(dict[str, Any], data)

    # --- GET /guru_realtime_picks ---

    async def get_realtime_picks(
        self,
        page: int = 1,
        *,
        bypass_cache: bool = False,
    ) -> GuruRealtimePicksResponse:
        """Get real-time guru trading activity.

        Returns recent trading activity across all tracked gurus.

        Args:
            page: Page number for pagination (1-indexed)
            bypass_cache: If True, skip cache lookup

        Returns:
            GuruRealtimePicksResponse with paginated activity
        """
        data = await self.get_realtime_picks_raw(page, bypass_cache=bypass_cache)
        return GuruRealtimePicksResponse.from_api_response(data)

    async def get_realtime_picks_raw(
        self,
        page: int = 1,
        *,
        bypass_cache: bool = False,
    ) -> dict[str, Any]:
        """Get raw real-time guru picks data.

        Args:
            page: Page number for pagination (1-indexed)
            bypass_cache: If True, skip cache lookup

        Returns:
            Raw API response dict
        """
        cache = self._client.cache
        cache_key = f"page:{page}"

        if not bypass_cache:
            cached_data = await cache.get(CacheCategory.GURU_REALTIME_PICKS, cache_key)
            if cached_data is not None:
                return cast(dict[str, Any], cached_data)

        params = {"page": page} if page > 1 else {}
        data = await self._client.get("guru_realtime_picks", params=params)
        await cache.set(CacheCategory.GURU_REALTIME_PICKS, cache_key, value=data)
        return cast(dict[str, Any], data)
