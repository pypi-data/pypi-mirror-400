"""Pydantic models for GuruFocus economic data endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class EconomicIndicatorsListResponse(BaseModel):
    """Response containing list of available economic indicators."""

    indicators: list[str] = Field(
        default_factory=list, description="List of economic indicator names"
    )
    count: int = Field(default=0, description="Number of indicators")

    @classmethod
    def from_api_response(cls, data: list[str]) -> EconomicIndicatorsListResponse:
        """Parse API response into EconomicIndicatorsListResponse.

        Args:
            data: List of indicator names from API

        Returns:
            Parsed EconomicIndicatorsListResponse
        """
        return cls(indicators=data, count=len(data))


class EconomicDataPoint(BaseModel):
    """A single data point for an economic indicator."""

    date: str = Field(description="Date of the data point (YYYY-MM-DD)")
    value: float | None = Field(default=None, description="Value at this date")


class EconomicIndicatorResponse(BaseModel):
    """Response containing data for a specific economic indicator."""

    name: str = Field(description="Indicator name")
    unit: str = Field(default="", description="Unit of measurement")
    frequency: str = Field(
        default="", description="Data frequency (Daily, Monthly, Quarterly, etc.)"
    )
    source: str = Field(default="", description="Data source")
    data: list[EconomicDataPoint] = Field(
        default_factory=list, description="Time series data points"
    )

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> EconomicIndicatorResponse:
        """Parse API response into EconomicIndicatorResponse.

        Args:
            data: API response dictionary

        Returns:
            Parsed EconomicIndicatorResponse
        """
        data_points = [
            EconomicDataPoint(
                date=item.get("date", ""),
                value=item.get("value"),
            )
            for item in data.get("data", [])
        ]
        return cls(
            name=data.get("name", ""),
            unit=data.get("unit", ""),
            frequency=data.get("frequency", ""),
            source=data.get("source", ""),
            data=data_points,
        )


class EconomicEvent(BaseModel):
    """An economic event from the calendar."""

    date: str = Field(description="Event date")
    event: str = Field(description="Event name/description")
    actual: str | None = Field(default=None, description="Actual value")
    forecast: str | None = Field(default=None, description="Forecast value")
    previous: str | None = Field(default=None, description="Previous value")


class IPOEvent(BaseModel):
    """An IPO event from the calendar."""

    symbol: str = Field(description="Stock ticker symbol")
    company: str = Field(description="Company name")
    exchange: str = Field(default="", description="Exchange code")
    date: str = Field(description="IPO date")
    price_range: str = Field(default="", description="Expected price range")
    shares: str = Field(default="", description="Number of shares offered")


class EarningsEvent(BaseModel):
    """An earnings event from the calendar."""

    symbol: str = Field(description="Stock ticker symbol")
    company: str = Field(description="Company name")
    exchange: str = Field(default="", description="Exchange code")
    date: str = Field(description="Earnings date")
    time: str = Field(default="", description="Time of day (before_market, after_market)")
    eps_estimate: str | None = Field(default=None, description="EPS estimate")


class DividendEvent(BaseModel):
    """A dividend event from the calendar."""

    symbol: str = Field(description="Stock ticker symbol")
    company: str = Field(description="Company name")
    exchange: str = Field(default="", description="Exchange code")
    declaration_date: str = Field(default="", description="Declaration date")
    ex_date: str = Field(default="", description="Ex-dividend date")
    record_date: str = Field(default="", description="Record date")
    pay_date: str = Field(default="", description="Payment date")
    cash_amount: str = Field(default="", description="Dividend amount")
    currency: str = Field(default="USD", description="Currency")
    dividend_type: str = Field(default="", description="Dividend type")
    frequency: int = Field(default=0, description="Payment frequency per year")
    dividend_yield: str = Field(default="", description="Dividend yield percentage")


class SplitEvent(BaseModel):
    """A stock split event from the calendar."""

    symbol: str = Field(description="Stock ticker symbol")
    company: str = Field(description="Company name")
    exchange: str = Field(default="", description="Exchange code")
    date: str = Field(description="Split date")
    ratio: str = Field(default="", description="Split ratio (e.g., '4:1')")


class CalendarResponse(BaseModel):
    """Response containing financial calendar events."""

    economic: list[EconomicEvent] = Field(default_factory=list, description="Economic events")
    ipo: list[IPOEvent] = Field(default_factory=list, description="IPO events")
    earning: list[EarningsEvent] = Field(default_factory=list, description="Earnings events")
    dividend: list[DividendEvent] = Field(default_factory=list, description="Dividend events")
    split: list[SplitEvent] = Field(default_factory=list, description="Stock split events")

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> CalendarResponse:
        """Parse API response into CalendarResponse.

        Args:
            data: API response dictionary

        Returns:
            Parsed CalendarResponse
        """
        economic_events = [
            EconomicEvent(
                date=item.get("date", ""),
                event=item.get("event", ""),
                actual=item.get("actual"),
                forecast=item.get("forecast"),
                previous=item.get("previous"),
            )
            for item in data.get("economic", [])
        ]

        ipo_events = [
            IPOEvent(
                symbol=item.get("symbol", ""),
                company=item.get("company", ""),
                exchange=item.get("exchange", ""),
                date=item.get("date", ""),
                price_range=item.get("price_range", ""),
                shares=item.get("shares", ""),
            )
            for item in data.get("ipo", [])
        ]

        earnings_events = [
            EarningsEvent(
                symbol=item.get("symbol", ""),
                company=item.get("company", ""),
                exchange=item.get("exchange", ""),
                date=item.get("date", ""),
                time=item.get("time", ""),
                eps_estimate=item.get("eps_estimate"),
            )
            for item in data.get("earning", [])
        ]

        dividend_events = [
            DividendEvent(
                symbol=item.get("symbol", ""),
                company=item.get("company", ""),
                exchange=item.get("exchange", ""),
                declaration_date=item.get("DeclarationDate", ""),
                ex_date=item.get("ExDate", ""),
                record_date=item.get("RecordDate", ""),
                pay_date=item.get("PayDate", ""),
                cash_amount=item.get("CashAmount", ""),
                currency=item.get("PriceCurrency", "USD"),
                dividend_type=item.get("DividendType", ""),
                frequency=item.get("Frequency", 0),
                dividend_yield=item.get("yield", ""),
            )
            for item in data.get("dividend", [])
        ]

        split_events = [
            SplitEvent(
                symbol=item.get("symbol", ""),
                company=item.get("company", ""),
                exchange=item.get("exchange", ""),
                date=item.get("date", ""),
                ratio=item.get("ratio", ""),
            )
            for item in data.get("split", [])
        ]

        return cls(
            economic=economic_events,
            ipo=ipo_events,
            earning=earnings_events,
            dividend=dividend_events,
            split=split_events,
        )
