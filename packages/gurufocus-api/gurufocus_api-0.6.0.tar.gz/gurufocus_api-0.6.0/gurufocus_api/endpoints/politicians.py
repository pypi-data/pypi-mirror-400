"""Endpoints for politician trading data.

This module provides access to politician-related endpoints:
- GET /politicians - List all tracked politicians
- GET /politicians/transactions - Politician stock transactions
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, cast

from gurufocus_api.cache.config import CacheCategory
from gurufocus_api.models.politicians import (
    PoliticiansListResponse,
    PoliticianTransactionsResponse,
)

if TYPE_CHECKING:
    from gurufocus_api.client import GuruFocusClient


class PoliticiansEndpoint:
    """Endpoints for politician trading data."""

    def __init__(self, client: GuruFocusClient) -> None:
        """Initialize the PoliticiansEndpoint.

        Args:
            client: The GuruFocusClient instance
        """
        self._client = client

    # --- GET /politicians ---

    async def get_politicians(
        self,
        *,
        bypass_cache: bool = False,
    ) -> PoliticiansListResponse:
        """Get list of all tracked politicians.

        Returns list of senators and representatives with their party
        affiliation and state information.

        Args:
            bypass_cache: If True, skip cache lookup

        Returns:
            PoliticiansListResponse with list of politicians
        """
        data = await self.get_politicians_raw(bypass_cache=bypass_cache)
        return PoliticiansListResponse.from_api_response(data)

    async def get_politicians_raw(
        self,
        *,
        bypass_cache: bool = False,
    ) -> list[dict[str, Any]]:
        """Get raw list of all tracked politicians.

        Args:
            bypass_cache: If True, skip cache lookup

        Returns:
            Raw API response list
        """
        cache = self._client.cache
        cache_key = "all"

        if not bypass_cache:
            cached_data = await cache.get(CacheCategory.POLITICIANS_LIST, cache_key)
            if cached_data is not None:
                return cast(list[dict[str, Any]], cached_data)

        data = await self._client.get("politicians")
        await cache.set(CacheCategory.POLITICIANS_LIST, cache_key, value=data)
        return cast(list[dict[str, Any]], data)

    # --- GET /politicians/transactions ---

    async def get_transactions(
        self,
        page: int = 1,
        politician_id: int | None = None,
        asset_type: str | None = None,
        sort: str | None = None,
        order: Literal["asc", "desc"] | None = None,
        *,
        bypass_cache: bool = False,
    ) -> PoliticianTransactionsResponse:
        """Get politician stock transactions.

        Args:
            page: Page number for pagination (1-indexed)
            politician_id: Filter by specific politician ID
            asset_type: Filter by asset type
            sort: Field to sort by
            order: Sort order ("asc" or "desc")
            bypass_cache: If True, skip cache lookup

        Returns:
            PoliticianTransactionsResponse with paginated transactions
        """
        data = await self.get_transactions_raw(
            page=page,
            politician_id=politician_id,
            asset_type=asset_type,
            sort=sort,
            order=order,
            bypass_cache=bypass_cache,
        )
        return PoliticianTransactionsResponse.from_api_response(data)

    async def get_transactions_raw(
        self,
        page: int = 1,
        politician_id: int | None = None,
        asset_type: str | None = None,
        sort: str | None = None,
        order: Literal["asc", "desc"] | None = None,
        *,
        bypass_cache: bool = False,
    ) -> dict[str, Any]:
        """Get raw politician transactions data.

        Args:
            page: Page number for pagination (1-indexed)
            politician_id: Filter by specific politician ID
            asset_type: Filter by asset type
            sort: Field to sort by
            order: Sort order ("asc" or "desc")
            bypass_cache: If True, skip cache lookup

        Returns:
            Raw API response dict
        """
        cache = self._client.cache

        # Build cache key from all parameters
        key_parts = [f"page:{page}"]
        if politician_id is not None:
            key_parts.append(f"id:{politician_id}")
        if asset_type:
            key_parts.append(f"asset:{asset_type}")
        if sort:
            key_parts.append(f"sort:{sort}")
        if order:
            key_parts.append(f"order:{order}")
        cache_key = ":".join(key_parts)

        if not bypass_cache:
            cached_data = await cache.get(CacheCategory.POLITICIAN_TRANSACTIONS, cache_key)
            if cached_data is not None:
                return cast(dict[str, Any], cached_data)

        # Build query parameters
        params: dict[str, Any] = {}
        if page > 1:
            params["page"] = page
        if politician_id is not None:
            params["id"] = politician_id
        if asset_type:
            params["asset_type"] = asset_type
        if sort:
            params["sort"] = sort
        if order:
            params["order"] = order

        data = await self._client.get("politicians/transactions", params=params)
        await cache.set(CacheCategory.POLITICIAN_TRANSACTIONS, cache_key, value=data)
        return cast(dict[str, Any], data)
