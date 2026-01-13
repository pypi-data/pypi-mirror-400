"""Endpoints for personal/user data.

This module provides access to personal data endpoints:
- GET /api_usage - API usage statistics
- GET /user_screeners - User's saved screeners
- GET /user_screeners/{id}/{page} - Screener results (paginated)
- GET /v2/{token}/portfolios - User portfolios
- POST /v2/{token}/portfolios/{id} - Portfolio detail with holdings
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from gurufocus_api.cache.config import CacheCategory
from gurufocus_api.models.personal import (
    APIUsageResponse,
    # NOTE: Portfolio imports commented out as of 2025-12-29 (API not returning valid response)
    # PortfolioDetailResponse,
    # PortfoliosResponse,
    UserScreenerResultsResponse,
    UserScreenersResponse,
)

if TYPE_CHECKING:
    from gurufocus_api.client import GuruFocusClient


class PersonalEndpoint:
    """Endpoints for personal/user data."""

    def __init__(self, client: GuruFocusClient) -> None:
        """Initialize the PersonalEndpoint.

        Args:
            client: The GuruFocusClient instance
        """
        self._client = client

    # --- GET /api_usage ---

    async def get_api_usage(
        self,
        *,
        bypass_cache: bool = False,
    ) -> APIUsageResponse:
        """Get API usage statistics.

        This method also syncs the usage tracker with the actual API quota.

        Args:
            bypass_cache: If True, skip cache lookup

        Returns:
            APIUsageResponse with usage and remaining requests
        """
        data = await self.get_api_usage_raw(bypass_cache=bypass_cache)
        result = APIUsageResponse.from_api_response(data)

        # Sync the usage tracker with actual API data
        if self._client._usage_tracker is not None:
            await self._client._usage_tracker.sync(result.api_requests_remaining)

        return result

    async def get_api_usage_raw(
        self,
        *,
        bypass_cache: bool = False,
    ) -> dict[str, Any]:
        """Get raw API usage statistics.

        Args:
            bypass_cache: If True, skip cache lookup

        Returns:
            Raw API response dict
        """
        cache = self._client.cache
        cache_key = "usage"

        if not bypass_cache:
            cached_data = await cache.get(CacheCategory.API_USAGE, cache_key)
            if cached_data is not None:
                return cast(dict[str, Any], cached_data)

        data = await self._client.get("api_usage")
        await cache.set(CacheCategory.API_USAGE, cache_key, value=data)
        return cast(dict[str, Any], data)

    # --- GET /user_screeners ---

    async def get_user_screeners(
        self,
        *,
        bypass_cache: bool = False,
    ) -> UserScreenersResponse:
        """Get user's saved screeners.

        Args:
            bypass_cache: If True, skip cache lookup

        Returns:
            UserScreenersResponse with list of screeners
        """
        data = await self.get_user_screeners_raw(bypass_cache=bypass_cache)
        return UserScreenersResponse.from_api_response(data)

    async def get_user_screeners_raw(
        self,
        *,
        bypass_cache: bool = False,
    ) -> list[dict[str, Any]]:
        """Get raw user screeners list.

        Args:
            bypass_cache: If True, skip cache lookup

        Returns:
            Raw API response list
        """
        cache = self._client.cache
        cache_key = "screeners"

        if not bypass_cache:
            cached_data = await cache.get(CacheCategory.USER_SCREENERS, cache_key)
            if cached_data is not None:
                return cast(list[dict[str, Any]], cached_data)

        data = await self._client.get("user_screeners")
        await cache.set(CacheCategory.USER_SCREENERS, cache_key, value=data)
        return cast(list[dict[str, Any]], data)

    # --- GET /user_screeners/{screener_id}/{page} ---

    async def get_user_screener_results(
        self,
        screener_id: int,
        page: int = 1,
        *,
        bypass_cache: bool = False,
    ) -> UserScreenerResultsResponse:
        """Get results from a user screener.

        Args:
            screener_id: The screener ID
            page: Page number (1-indexed)
            bypass_cache: If True, skip cache lookup

        Returns:
            UserScreenerResultsResponse with matching stocks
        """
        data = await self.get_user_screener_results_raw(
            screener_id, page, bypass_cache=bypass_cache
        )
        return UserScreenerResultsResponse.from_api_response(data, screener_id, page)

    async def get_user_screener_results_raw(
        self,
        screener_id: int,
        page: int = 1,
        *,
        bypass_cache: bool = False,
    ) -> list[dict[str, Any]]:
        """Get raw results from a user screener.

        Args:
            screener_id: The screener ID
            page: Page number (1-indexed)
            bypass_cache: If True, skip cache lookup

        Returns:
            Raw API response list
        """
        cache = self._client.cache
        cache_key = f"{screener_id}:{page}"

        if not bypass_cache:
            cached_data = await cache.get(CacheCategory.USER_SCREENER_RESULTS, cache_key)
            if cached_data is not None:
                return cast(list[dict[str, Any]], cached_data)

        data = await self._client.get(f"user_screeners/{screener_id}/{page}")
        await cache.set(CacheCategory.USER_SCREENER_RESULTS, cache_key, value=data)
        return cast(list[dict[str, Any]], data)

    # NOTE: Portfolio endpoints commented out as of 2025-12-29.
    # The V2 API endpoint (https://api.gurufocus.com/v2/{token}/portfolios) is not
    # returning a valid response. Re-enable when the API is fixed.
    #
    # # --- GET /v2/{token}/portfolios (V2 API) ---
    #
    # async def get_portfolios(
    #     self,
    #     *,
    #     bypass_cache: bool = False,
    # ) -> PortfoliosResponse:
    #     """Get user's portfolios.
    #
    #     This uses the V2 API endpoint.
    #
    #     Args:
    #         bypass_cache: If True, skip cache lookup
    #
    #     Returns:
    #         PortfoliosResponse with list of portfolios
    #     """
    #     data = await self.get_portfolios_raw(bypass_cache=bypass_cache)
    #     return PortfoliosResponse.from_api_response(data)
    #
    # async def get_portfolios_raw(
    #     self,
    #     *,
    #     bypass_cache: bool = False,
    # ) -> list[dict[str, Any]]:
    #     """Get raw user portfolios list.
    #
    #     This uses the V2 API endpoint.
    #
    #     Args:
    #         bypass_cache: If True, skip cache lookup
    #
    #     Returns:
    #         Raw API response list
    #     """
    #     cache = self._client.cache
    #     cache_key = "portfolios"
    #
    #     if not bypass_cache:
    #         cached_data = await cache.get(CacheCategory.PORTFOLIOS, cache_key)
    #         if cached_data is not None:
    #             return cast(list[dict[str, Any]], cached_data)
    #
    #     data = await self._client.get_v2("portfolios")
    #     await cache.set(CacheCategory.PORTFOLIOS, cache_key, value=data)
    #     return cast(list[dict[str, Any]], data)
    #
    # # --- POST /v2/{token}/portfolios/{id} (V2 API) ---
    #
    # async def get_portfolio_detail(
    #     self,
    #     portfolio_id: int,
    #     *,
    #     bypass_cache: bool = False,
    # ) -> PortfolioDetailResponse:
    #     """Get portfolio detail with holdings.
    #
    #     This uses the V2 API endpoint with POST method.
    #
    #     Args:
    #         portfolio_id: The portfolio ID
    #         bypass_cache: If True, skip cache lookup
    #
    #     Returns:
    #         PortfolioDetailResponse with holdings
    #     """
    #     data = await self.get_portfolio_detail_raw(portfolio_id, bypass_cache=bypass_cache)
    #     return PortfolioDetailResponse.from_api_response(data, portfolio_id)
    #
    # async def get_portfolio_detail_raw(
    #     self,
    #     portfolio_id: int,
    #     *,
    #     bypass_cache: bool = False,
    # ) -> dict[str, Any]:
    #     """Get raw portfolio detail.
    #
    #     This uses the V2 API endpoint with POST method.
    #
    #     Args:
    #         portfolio_id: The portfolio ID
    #         bypass_cache: If True, skip cache lookup
    #
    #     Returns:
    #         Raw API response dict
    #     """
    #     cache = self._client.cache
    #     cache_key = f"portfolio:{portfolio_id}"
    #
    #     if not bypass_cache:
    #         cached_data = await cache.get(CacheCategory.PORTFOLIO_DETAIL, cache_key)
    #         if cached_data is not None:
    #             return cast(dict[str, Any], cached_data)
    #
    #     data = await self._client.post_v2(f"portfolios/{portfolio_id}")
    #     await cache.set(CacheCategory.PORTFOLIO_DETAIL, cache_key, value=data)
    #     return cast(dict[str, Any], data)
