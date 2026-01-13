"""Endpoints for reference data (exchanges, indexes, currencies).

This module provides access to reference data endpoints:
- GET /exchange_list - List worldwide exchanges by country
- GET /exchange_stocks/{exchange} - Stocks listed on an exchange
- GET /index_list - List worldwide market indexes
- GET /index_stocks/{symbol} - Stocks in an index
- GET /country_currency - Country to currency mappings
- GET /funda_updated/{date} - Stocks with updated fundamentals
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from gurufocus_api.cache.config import CacheCategory
from gurufocus_api.models.reference import (
    CountryCurrencyResponse,
    ExchangeListResponse,
    ExchangeStocksResponse,
    FundaUpdatedResponse,
    IndexListResponse,
    IndexStocksResponse,
)

if TYPE_CHECKING:
    from gurufocus_api.client import GuruFocusClient


class ReferenceEndpoint:
    """Endpoints for reference data (exchanges and indexes)."""

    def __init__(self, client: GuruFocusClient) -> None:
        """Initialize the ReferenceEndpoint.

        Args:
            client: The GuruFocusClient instance
        """
        self._client = client

    # --- GET /exchange_list ---

    async def get_exchange_list(
        self,
        *,
        bypass_cache: bool = False,
    ) -> ExchangeListResponse:
        """Get list of worldwide stock exchanges by country.

        Returns a mapping of country names to their exchange codes.

        Args:
            bypass_cache: If True, skip cache lookup

        Returns:
            ExchangeListResponse with exchanges grouped by country
        """
        data = await self.get_exchange_list_raw(bypass_cache=bypass_cache)
        return ExchangeListResponse.from_api_response(data)

    async def get_exchange_list_raw(
        self,
        *,
        bypass_cache: bool = False,
    ) -> dict[str, Any]:
        """Get raw list of worldwide stock exchanges.

        Args:
            bypass_cache: If True, skip cache lookup

        Returns:
            Raw API response dict
        """
        cache = self._client.cache
        cache_key = "all"

        if not bypass_cache:
            cached_data = await cache.get(CacheCategory.EXCHANGE_LIST, cache_key)
            if cached_data is not None:
                return cast(dict[str, Any], cached_data)

        data = await self._client.get("exchange_list")
        await cache.set(CacheCategory.EXCHANGE_LIST, cache_key, value=data)
        return cast(dict[str, Any], data)

    # --- GET /exchange_stocks/{exchange} ---

    async def get_exchange_stocks(
        self,
        exchange: str,
        *,
        bypass_cache: bool = False,
    ) -> ExchangeStocksResponse:
        """Get stocks listed on a specific exchange.

        Args:
            exchange: Exchange code (e.g., 'NYSE', 'NAS', 'LSE')
            bypass_cache: If True, skip cache lookup

        Returns:
            ExchangeStocksResponse with list of stocks
        """
        normalized_exchange = exchange.upper().strip()
        data = await self.get_exchange_stocks_raw(exchange, bypass_cache=bypass_cache)
        return ExchangeStocksResponse.from_api_response(data, normalized_exchange)

    async def get_exchange_stocks_raw(
        self,
        exchange: str,
        *,
        bypass_cache: bool = False,
    ) -> list[dict[str, Any]]:
        """Get raw stocks listed on an exchange.

        Args:
            exchange: Exchange code (e.g., 'NYSE', 'NAS', 'LSE')
            bypass_cache: If True, skip cache lookup

        Returns:
            Raw API response list
        """
        exchange = exchange.upper().strip()
        cache = self._client.cache
        cache_key = exchange

        if not bypass_cache:
            cached_data = await cache.get(CacheCategory.EXCHANGE_STOCKS, cache_key)
            if cached_data is not None:
                return cast(list[dict[str, Any]], cached_data)

        data = await self._client.get(f"exchange_stocks/{exchange}")
        await cache.set(CacheCategory.EXCHANGE_STOCKS, cache_key, value=data)
        return cast(list[dict[str, Any]], data)

    # --- GET /index_list ---

    async def get_index_list(
        self,
        *,
        bypass_cache: bool = False,
    ) -> IndexListResponse:
        """Get list of worldwide market indexes.

        Returns a list of major market indexes with their names and symbols.

        Args:
            bypass_cache: If True, skip cache lookup

        Returns:
            IndexListResponse with list of indexes
        """
        data = await self.get_index_list_raw(bypass_cache=bypass_cache)
        return IndexListResponse.from_api_response(data)

    async def get_index_list_raw(
        self,
        *,
        bypass_cache: bool = False,
    ) -> list[dict[str, Any]]:
        """Get raw list of worldwide market indexes.

        Args:
            bypass_cache: If True, skip cache lookup

        Returns:
            Raw API response list
        """
        cache = self._client.cache
        cache_key = "all"

        if not bypass_cache:
            cached_data = await cache.get(CacheCategory.INDEX_LIST, cache_key)
            if cached_data is not None:
                return cast(list[dict[str, Any]], cached_data)

        data = await self._client.get("index_list")
        await cache.set(CacheCategory.INDEX_LIST, cache_key, value=data)
        return cast(list[dict[str, Any]], data)

    # --- GET /index_stocks/{symbol} ---

    async def get_index_stocks(
        self,
        index_symbol: str,
        page: int = 1,
        *,
        bypass_cache: bool = False,
    ) -> IndexStocksResponse:
        """Get stocks in a specific market index.

        Args:
            index_symbol: Index symbol (e.g., '^GSPC', '^DJI')
            page: Page number for paginated results
            bypass_cache: If True, skip cache lookup

        Returns:
            IndexStocksResponse with list of constituent stocks
        """
        data = await self.get_index_stocks_raw(index_symbol, page=page, bypass_cache=bypass_cache)
        return IndexStocksResponse.from_api_response(data, index_symbol)

    async def get_index_stocks_raw(
        self,
        index_symbol: str,
        page: int = 1,
        *,
        bypass_cache: bool = False,
    ) -> list[dict[str, Any]]:
        """Get raw stocks in a market index.

        Args:
            index_symbol: Index symbol (e.g., '^GSPC', '^DJI')
            page: Page number for paginated results
            bypass_cache: If True, skip cache lookup

        Returns:
            Raw API response list
        """
        index_symbol = index_symbol.strip()
        cache = self._client.cache
        cache_key = f"{index_symbol}:{page}"

        if not bypass_cache:
            cached_data = await cache.get(CacheCategory.INDEX_STOCKS, cache_key)
            if cached_data is not None:
                return cast(list[dict[str, Any]], cached_data)

        params: dict[str, Any] = {}
        if page > 1:
            params["page"] = page

        data = await self._client.get(f"index_stocks/{index_symbol}", params=params)
        await cache.set(CacheCategory.INDEX_STOCKS, cache_key, value=data)
        return cast(list[dict[str, Any]], data)

    # --- GET /country_currency ---

    async def get_country_currency(
        self,
        *,
        bypass_cache: bool = False,
    ) -> CountryCurrencyResponse:
        """Get list of country to currency mappings.

        Returns a list of countries with their ISO codes and currencies.

        Args:
            bypass_cache: If True, skip cache lookup

        Returns:
            CountryCurrencyResponse with list of country/currency mappings
        """
        data = await self.get_country_currency_raw(bypass_cache=bypass_cache)
        return CountryCurrencyResponse.from_api_response(data)

    async def get_country_currency_raw(
        self,
        *,
        bypass_cache: bool = False,
    ) -> list[dict[str, Any]]:
        """Get raw country to currency mappings.

        Args:
            bypass_cache: If True, skip cache lookup

        Returns:
            Raw API response list
        """
        cache = self._client.cache
        cache_key = "all"

        if not bypass_cache:
            cached_data = await cache.get(CacheCategory.COUNTRY_CURRENCY, cache_key)
            if cached_data is not None:
                return cast(list[dict[str, Any]], cached_data)

        data = await self._client.get("country_currency")
        await cache.set(CacheCategory.COUNTRY_CURRENCY, cache_key, value=data)
        return cast(list[dict[str, Any]], data)

    # --- GET /funda_updated/{date} ---

    async def get_funda_updated(
        self,
        date: str,
        *,
        bypass_cache: bool = False,
    ) -> FundaUpdatedResponse:
        """Get stocks with updated fundamentals on a specific date.

        Args:
            date: Date in YYYY-MM-DD format
            bypass_cache: If True, skip cache lookup

        Returns:
            FundaUpdatedResponse with list of stocks
        """
        data = await self.get_funda_updated_raw(date, bypass_cache=bypass_cache)
        return FundaUpdatedResponse.from_api_response(data, date)

    async def get_funda_updated_raw(
        self,
        date: str,
        *,
        bypass_cache: bool = False,
    ) -> list[dict[str, Any]]:
        """Get raw list of stocks with updated fundamentals.

        Args:
            date: Date in YYYY-MM-DD format
            bypass_cache: If True, skip cache lookup

        Returns:
            Raw API response list
        """
        date = date.strip()
        cache = self._client.cache
        cache_key = date

        if not bypass_cache:
            cached_data = await cache.get(CacheCategory.FUNDA_UPDATED, cache_key)
            if cached_data is not None:
                return cast(list[dict[str, Any]], cached_data)

        data = await self._client.get(f"funda_updated/{date}")
        await cache.set(CacheCategory.FUNDA_UPDATED, cache_key, value=data)
        return cast(list[dict[str, Any]], data)
