"""Pydantic models for GuruFocus reference data endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ExchangeListResponse(BaseModel):
    """Response containing list of worldwide exchanges by country."""

    exchanges_by_country: dict[str, list[str]] = Field(
        default_factory=dict, description="Map of country names to exchange codes"
    )
    total_countries: int = Field(default=0, description="Number of countries with exchanges")
    total_exchanges: int = Field(default=0, description="Total number of exchanges")

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> ExchangeListResponse:
        """Parse API response into ExchangeListResponse.

        Args:
            data: API response dictionary mapping country to exchange codes

        Returns:
            Parsed ExchangeListResponse
        """
        total_exchanges = sum(len(exchanges) for exchanges in data.values())
        return cls(
            exchanges_by_country=data,
            total_countries=len(data),
            total_exchanges=total_exchanges,
        )


class ExchangeStock(BaseModel):
    """A stock listed on an exchange."""

    symbol: str = Field(description="Stock ticker symbol")
    exchange: str = Field(description="Exchange code")
    company: str = Field(description="Company name")
    currency: str = Field(default="", description="Trading currency (USD, EUR, etc.)")
    industry: str = Field(default="", description="Industry classification")
    sector: str = Field(default="", description="Sector classification")
    subindustry: str = Field(default="", description="Sub-industry classification")


class ExchangeStocksResponse(BaseModel):
    """Response containing stocks listed on an exchange."""

    exchange: str = Field(description="Exchange code")
    stocks: list[ExchangeStock] = Field(default_factory=list, description="List of stocks")
    count: int = Field(default=0, description="Number of stocks")

    @classmethod
    def from_api_response(cls, data: list[dict[str, Any]], exchange: str) -> ExchangeStocksResponse:
        """Parse API response into ExchangeStocksResponse.

        Args:
            data: List of stock dictionaries from API
            exchange: Exchange code

        Returns:
            Parsed ExchangeStocksResponse
        """
        stocks = [
            ExchangeStock(
                symbol=item.get("symbol", ""),
                exchange=item.get("exchange", exchange),
                company=item.get("company", ""),
                currency=item.get("currency", ""),
                industry=item.get("industry", ""),
                sector=item.get("sector", ""),
                subindustry=item.get("subindustry", ""),
            )
            for item in data
        ]
        return cls(exchange=exchange, stocks=stocks, count=len(stocks))


class IndexInfo(BaseModel):
    """Basic information about a market index."""

    name: str = Field(description="Index name (e.g., 'S&P 500')")
    symbol: str = Field(description="Index symbol (e.g., '^GSPC')")


class IndexListResponse(BaseModel):
    """Response containing list of worldwide market indexes."""

    indexes: list[IndexInfo] = Field(default_factory=list, description="List of indexes")
    count: int = Field(default=0, description="Number of indexes")

    @classmethod
    def from_api_response(cls, data: list[dict[str, Any]]) -> IndexListResponse:
        """Parse API response into IndexListResponse.

        Args:
            data: List of index dictionaries from API

        Returns:
            Parsed IndexListResponse
        """
        indexes = [
            IndexInfo(
                name=item.get("name", ""),
                symbol=item.get("symbol", ""),
            )
            for item in data
        ]
        return cls(indexes=indexes, count=len(indexes))


class IndexStock(BaseModel):
    """A stock that is a constituent of an index."""

    symbol: str = Field(description="Stock ticker symbol")
    exchange: str = Field(default="", description="Exchange code")
    company: str = Field(default="", description="Company name")
    currency: str = Field(default="", description="Trading currency")
    industry: str = Field(default="", description="Industry classification")
    sector: str = Field(default="", description="Sector classification")
    subindustry: str = Field(default="", description="Sub-industry classification")


class IndexStocksResponse(BaseModel):
    """Response containing stocks in an index."""

    index_symbol: str = Field(description="Index symbol")
    stocks: list[IndexStock] = Field(default_factory=list, description="List of constituent stocks")
    count: int = Field(default=0, description="Number of stocks")

    @classmethod
    def from_api_response(
        cls, data: list[dict[str, Any]], index_symbol: str
    ) -> IndexStocksResponse:
        """Parse API response into IndexStocksResponse.

        Args:
            data: List of stock dictionaries from API
            index_symbol: Index symbol

        Returns:
            Parsed IndexStocksResponse
        """
        stocks = [
            IndexStock(
                symbol=item.get("symbol", ""),
                exchange=item.get("exchange", ""),
                company=item.get("company", ""),
                currency=item.get("currency", ""),
                industry=item.get("industry", ""),
                sector=item.get("sector", ""),
                subindustry=item.get("subindustry", ""),
            )
            for item in data
        ]
        return cls(index_symbol=index_symbol, stocks=stocks, count=len(stocks))


class CountryCurrency(BaseModel):
    """Country and currency mapping."""

    country: str = Field(description="Country name")
    country_iso: str = Field(description="ISO country code (3-letter)")
    currency: str = Field(description="Currency code (3-letter)")


class CountryCurrencyResponse(BaseModel):
    """Response containing list of country/currency mappings."""

    currencies: list[CountryCurrency] = Field(
        default_factory=list, description="List of country/currency mappings"
    )
    count: int = Field(default=0, description="Number of countries")

    @classmethod
    def from_api_response(cls, data: list[dict[str, Any]]) -> CountryCurrencyResponse:
        """Parse API response into CountryCurrencyResponse.

        Args:
            data: List of country/currency dictionaries from API

        Returns:
            Parsed CountryCurrencyResponse
        """
        currencies = [
            CountryCurrency(
                country=item.get("country", ""),
                country_iso=item.get("country_ISO", ""),
                currency=item.get("currency", ""),
            )
            for item in data
        ]
        return cls(currencies=currencies, count=len(currencies))


class FundaUpdatedStock(BaseModel):
    """A stock that had fundamentals updated on a specific date."""

    symbol: str = Field(description="Stock ticker symbol")
    exchange: str = Field(default="", description="Exchange code")
    company: str = Field(default="", description="Company name")


class FundaUpdatedResponse(BaseModel):
    """Response containing stocks with updated fundamentals on a date."""

    date: str = Field(description="Date of fundamental updates (YYYY-MM-DD)")
    stocks: list[FundaUpdatedStock] = Field(
        default_factory=list, description="List of stocks with updated fundamentals"
    )
    count: int = Field(default=0, description="Number of stocks")

    @classmethod
    def from_api_response(cls, data: list[dict[str, Any]], date: str) -> FundaUpdatedResponse:
        """Parse API response into FundaUpdatedResponse.

        Args:
            data: List of stock dictionaries from API
            date: The date for which fundamentals were updated

        Returns:
            Parsed FundaUpdatedResponse
        """
        stocks = [
            FundaUpdatedStock(
                symbol=item.get("symbol", ""),
                exchange=item.get("exchange", ""),
                company=item.get("company", ""),
            )
            for item in data
        ]
        return cls(date=date, stocks=stocks, count=len(stocks))
