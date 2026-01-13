"""Endpoints for ETF data.

This module provides access to ETF data endpoints:
- GET /etf/etf_list - List all ETFs
- GET /etf/{ETF}/sector_weighting - Get sector/industry weightings
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
from urllib.parse import quote

from gurufocus_api.cache.config import CacheCategory
from gurufocus_api.models.etf import ETFListResponse, ETFSectorWeightingResponse

if TYPE_CHECKING:
    from gurufocus_api.client import GuruFocusClient


class ETFsEndpoint:
    """Endpoints for ETF data."""

    def __init__(self, client: GuruFocusClient) -> None:
        """Initialize the ETFsEndpoint.

        Args:
            client: The GuruFocusClient instance
        """
        self._client = client

    # --- GET /etf/etf_list ---

    async def get_etf_list(
        self,
        page: int = 1,
        per_page: int = 50,
        *,
        bypass_cache: bool = False,
    ) -> ETFListResponse:
        """Get paginated list of ETFs.

        Args:
            page: Page number (default: 1)
            per_page: Items per page (default: 50)
            bypass_cache: If True, skip cache lookup

        Returns:
            ETFListResponse with list of ETFs and pagination info
        """
        data = await self.get_etf_list_raw(page, per_page, bypass_cache=bypass_cache)
        return ETFListResponse.from_api_response(data)

    async def get_etf_list_raw(
        self,
        page: int = 1,
        per_page: int = 50,
        *,
        bypass_cache: bool = False,
    ) -> dict[str, Any]:
        """Get raw paginated list of ETFs.

        Args:
            page: Page number (default: 1)
            per_page: Items per page (default: 50)
            bypass_cache: If True, skip cache lookup

        Returns:
            Raw API response dict
        """
        cache = self._client.cache
        cache_key = f"list:{page}:{per_page}"

        if not bypass_cache:
            cached_data = await cache.get(CacheCategory.ETF_LIST, cache_key)
            if cached_data is not None:
                return cast(dict[str, Any], cached_data)

        params: dict[str, Any] = {}
        if page != 1:
            params["page"] = page
        if per_page != 50:
            params["per_page"] = per_page

        data = await self._client.get("etf/etf_list", params=params if params else None)
        await cache.set(CacheCategory.ETF_LIST, cache_key, value=data)
        return cast(dict[str, Any], data)

    # --- GET /etf/{ETF}/sector_weighting ---

    async def get_sector_weighting(
        self,
        etf_name: str,
        *,
        bypass_cache: bool = False,
    ) -> ETFSectorWeightingResponse:
        """Get sector and industry weightings for an ETF.

        Returns the allocation breakdown of the ETF by sector and industry,
        with historical weighting percentages keyed by date.

        Args:
            etf_name: Full ETF name (e.g., "Vanguard 500 Index Fund")
            bypass_cache: If True, skip cache lookup

        Returns:
            ETFSectorWeightingResponse with sectors and industry breakdowns

        Example:
            weighting = await client.etfs.get_sector_weighting("Vanguard 500 Index Fund")
            for sector in weighting.sectors:
                print(f"{sector.sector}: {sector.weightings}")
        """
        data = await self.get_sector_weighting_raw(etf_name, bypass_cache=bypass_cache)
        return ETFSectorWeightingResponse.from_api_response(data)

    async def get_sector_weighting_raw(
        self,
        etf_name: str,
        *,
        bypass_cache: bool = False,
    ) -> dict[str, Any]:
        """Get raw sector weighting data for an ETF.

        Args:
            etf_name: Full ETF name (e.g., "Vanguard 500 Index Fund")
            bypass_cache: If True, skip cache lookup

        Returns:
            Raw API response dict
        """
        cache = self._client.cache
        cache_key = f"sector:{etf_name}"

        if not bypass_cache:
            cached_data = await cache.get(CacheCategory.ETF_SECTOR_WEIGHTING, cache_key)
            if cached_data is not None:
                return cast(dict[str, Any], cached_data)

        # URL-encode the ETF name (spaces -> %20)
        encoded_name = quote(etf_name, safe="")
        endpoint = f"etf/{encoded_name}/sector_weighting"

        data = await self._client.get(endpoint)
        await cache.set(CacheCategory.ETF_SECTOR_WEIGHTING, cache_key, value=data)
        return cast(dict[str, Any], data)
