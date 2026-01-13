"""Pydantic models for GuruFocus personal/user data endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class APIUsageResponse(BaseModel):
    """Response from API usage endpoint."""

    api_usage: int = Field(default=0, description="Number of API requests made")
    api_requests_remaining: int = Field(default=0, description="Number of API requests remaining")

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> APIUsageResponse:
        """Parse API response into APIUsageResponse.

        Args:
            data: API response dictionary

        Returns:
            Parsed APIUsageResponse
        """
        return cls(
            api_usage=data.get("API Usage", 0),
            api_requests_remaining=data.get("API Requests Remaining", 0),
        )


class UserScreener(BaseModel):
    """User-defined stock screener."""

    id: int = Field(description="Screener ID")
    name: str = Field(default="", description="Screener name")
    short_description: str | None = Field(default=None, description="Short description")
    note: str | None = Field(default=None, description="User note")
    is_public: bool = Field(default=False, description="Whether screener is public")
    is_predefined: bool = Field(default=False, description="Whether screener is predefined")
    default_exchanges: list[str] = Field(
        default_factory=list, description="Default exchanges to search"
    )
    updated_at: str = Field(default="", description="Last update timestamp")
    created_at: str = Field(default="", description="Creation timestamp")


class UserScreenersResponse(BaseModel):
    """Response containing user's stock screeners."""

    screeners: list[UserScreener] = Field(
        default_factory=list, description="List of user screeners"
    )
    count: int = Field(default=0, description="Number of screeners")

    @classmethod
    def from_api_response(cls, data: list[dict[str, Any]]) -> UserScreenersResponse:
        """Parse API response into UserScreenersResponse.

        Args:
            data: API response list of screener dicts

        Returns:
            Parsed UserScreenersResponse
        """
        screeners = []
        for item in data:
            screener = UserScreener(
                id=item.get("id", 0),
                name=item.get("name", ""),
                short_description=item.get("short_description"),
                note=item.get("note"),
                is_public=item.get("is_public", False),
                is_predefined=item.get("is_predefined", False),
                default_exchanges=item.get("default_exchanges", []),
                updated_at=item.get("updated_at", ""),
                created_at=item.get("created_at", ""),
            )
            screeners.append(screener)
        return cls(screeners=screeners, count=len(screeners))


class ScreenerResultStock(BaseModel):
    """A stock result from a screener."""

    symbol: str = Field(description="Stock ticker symbol")
    exchange: str = Field(default="", description="Exchange code")
    company: str = Field(default="", description="Company name")
    sector: str = Field(default="", description="Sector classification")
    industry: str = Field(default="", description="Industry classification")


class UserScreenerResultsResponse(BaseModel):
    """Response containing screener results."""

    screener_id: int = Field(description="Screener ID")
    page: int = Field(default=1, description="Page number")
    stocks: list[ScreenerResultStock] = Field(
        default_factory=list, description="List of stocks matching screener"
    )
    count: int = Field(default=0, description="Number of stocks on this page")

    @classmethod
    def from_api_response(
        cls, data: list[dict[str, Any]], screener_id: int, page: int
    ) -> UserScreenerResultsResponse:
        """Parse API response into UserScreenerResultsResponse.

        Args:
            data: API response list of stock dicts
            screener_id: The screener ID
            page: The page number

        Returns:
            Parsed UserScreenerResultsResponse
        """
        stocks = [
            ScreenerResultStock(
                symbol=item.get("symbol", ""),
                exchange=item.get("exchange", ""),
                company=item.get("company", ""),
                sector=item.get("sector", ""),
                industry=item.get("industry", ""),
            )
            for item in data
        ]
        return cls(screener_id=screener_id, page=page, stocks=stocks, count=len(stocks))


class Portfolio(BaseModel):
    """User portfolio basic info."""

    id: int = Field(description="Portfolio ID")
    name: str = Field(default="", description="Portfolio name")
    currency: str = Field(default="USD", description="Portfolio currency")
    note: str = Field(default="", description="User notes")


class PortfoliosResponse(BaseModel):
    """Response containing user's portfolios list."""

    portfolios: list[Portfolio] = Field(default_factory=list, description="List of portfolios")
    count: int = Field(default=0, description="Number of portfolios")

    @classmethod
    def from_api_response(cls, data: list[dict[str, Any]]) -> PortfoliosResponse:
        """Parse API response into PortfoliosResponse.

        Args:
            data: API response list of portfolio dicts

        Returns:
            Parsed PortfoliosResponse
        """
        portfolios = [
            Portfolio(
                id=item.get("id", 0),
                name=item.get("name", ""),
                currency=item.get("currency", "USD"),
                note=item.get("note", ""),
            )
            for item in data
        ]
        return cls(portfolios=portfolios, count=len(portfolios))


class PortfolioHolding(BaseModel):
    """A holding in a portfolio."""

    symbol: str = Field(description="Stock ticker symbol")
    exchange: str = Field(default="", description="Exchange code")
    company: str = Field(default="", description="Company name")
    shares: float = Field(default=0.0, description="Number of shares")
    cost_basis: float = Field(default=0.0, description="Cost basis per share")
    current_price: float = Field(default=0.0, description="Current price")
    market_value: float = Field(default=0.0, description="Current market value")
    gain_loss: float = Field(default=0.0, description="Gain/loss amount")
    gain_loss_percent: float = Field(default=0.0, description="Gain/loss percentage")
    weight: float = Field(default=0.0, description="Weight in portfolio (%)")


class PortfolioDetailResponse(BaseModel):
    """Response containing portfolio detail with holdings."""

    portfolio_id: int = Field(description="Portfolio ID")
    name: str = Field(default="", description="Portfolio name")
    currency: str = Field(default="USD", description="Portfolio currency")
    total_value: float = Field(default=0.0, description="Total portfolio value")
    total_cost: float = Field(default=0.0, description="Total cost basis")
    total_gain_loss: float = Field(default=0.0, description="Total gain/loss")
    holdings: list[PortfolioHolding] = Field(default_factory=list, description="List of holdings")
    holdings_count: int = Field(default=0, description="Number of holdings")

    @classmethod
    def from_api_response(cls, data: dict[str, Any], portfolio_id: int) -> PortfolioDetailResponse:
        """Parse API response into PortfolioDetailResponse.

        Args:
            data: API response dict
            portfolio_id: The portfolio ID

        Returns:
            Parsed PortfolioDetailResponse
        """
        holdings_data = data.get("holdings", [])
        holdings = [
            PortfolioHolding(
                symbol=item.get("symbol", ""),
                exchange=item.get("exchange", ""),
                company=item.get("company", ""),
                shares=float(item.get("shares", 0)),
                cost_basis=float(item.get("cost_basis", 0)),
                current_price=float(item.get("current_price", 0)),
                market_value=float(item.get("market_value", 0)),
                gain_loss=float(item.get("gain_loss", 0)),
                gain_loss_percent=float(item.get("gain_loss_percent", 0)),
                weight=float(item.get("weight", 0)),
            )
            for item in holdings_data
        ]
        return cls(
            portfolio_id=portfolio_id,
            name=data.get("name", ""),
            currency=data.get("currency", "USD"),
            total_value=float(data.get("total_value", 0)),
            total_cost=float(data.get("total_cost", 0)),
            total_gain_loss=float(data.get("total_gain_loss", 0)),
            holdings=holdings,
            holdings_count=len(holdings),
        )
