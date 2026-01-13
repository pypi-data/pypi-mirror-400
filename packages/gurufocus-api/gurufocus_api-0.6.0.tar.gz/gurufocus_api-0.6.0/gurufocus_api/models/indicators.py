"""Pydantic models for stock indicators data."""

import contextlib
from typing import Any

from pydantic import BaseModel, Field


class IndicatorDefinition(BaseModel):
    """Definition of an available stock indicator.

    Represents a single indicator from the indicators list endpoint,
    with its key (for API calls) and human-readable name.
    """

    key: str = Field(description="Indicator key for API calls (e.g., 'net_income', 'roe')")
    name: str = Field(description="Human-readable indicator name")


class IndicatorsList(BaseModel):
    """List of available stock indicators.

    Contains all indicators that can be queried via the indicator endpoint.
    """

    indicators: list[IndicatorDefinition] = Field(
        default_factory=list,
        description="List of available indicators",
    )

    @classmethod
    def from_api_response(cls, data: list[dict[str, Any]]) -> "IndicatorsList":
        """Parse raw API response into IndicatorsList model.

        Args:
            data: Raw API response list of indicator definitions

        Returns:
            IndicatorsList instance with parsed data
        """
        indicators = []
        for item in data:
            if isinstance(item, dict) and "key" in item:
                indicators.append(
                    IndicatorDefinition(
                        key=item.get("key", ""),
                        name=item.get("name", ""),
                    )
                )
        return cls(indicators=indicators)

    def get_by_key(self, key: str) -> IndicatorDefinition | None:
        """Get an indicator definition by its key.

        Args:
            key: The indicator key to look up

        Returns:
            IndicatorDefinition if found, None otherwise
        """
        for indicator in self.indicators:
            if indicator.key == key:
                return indicator
        return None

    def search(self, query: str) -> list[IndicatorDefinition]:
        """Search indicators by name or key.

        Args:
            query: Search query string (case-insensitive)

        Returns:
            List of matching indicator definitions
        """
        query = query.lower()
        return [
            ind for ind in self.indicators if query in ind.key.lower() or query in ind.name.lower()
        ]


class IndicatorDataPoint(BaseModel):
    """A single data point in an indicator time series."""

    date: str = Field(description="Date in YYYY-MM-DD format")
    value: float | None = Field(default=None, description="Indicator value")


class IndicatorTimeSeries(BaseModel):
    """Time series data for a specific indicator.

    Contains historical values for an indicator key.
    """

    symbol: str = Field(description="Stock ticker symbol")
    indicator_key: str = Field(description="Indicator key (e.g., 'net_income')")
    data: list[IndicatorDataPoint] = Field(
        default_factory=list,
        description="Time series data points",
    )

    @classmethod
    def from_api_response(
        cls, data: list[list[Any]], symbol: str, indicator_key: str
    ) -> "IndicatorTimeSeries":
        """Parse raw API response into IndicatorTimeSeries model.

        Args:
            data: Raw API response list of [date, value] arrays
            symbol: Stock ticker symbol
            indicator_key: The indicator key used in the query

        Returns:
            IndicatorTimeSeries instance with parsed data
        """
        symbol = symbol.upper().strip()
        points = []

        for item in data:
            if isinstance(item, list) and len(item) >= 2:
                date_str = str(item[0])
                value = None
                if item[1] is not None:
                    with contextlib.suppress(TypeError, ValueError):
                        value = float(item[1])
                points.append(IndicatorDataPoint(date=date_str, value=value))

        return cls(
            symbol=symbol,
            indicator_key=indicator_key,
            data=points,
        )

    @property
    def latest(self) -> IndicatorDataPoint | None:
        """Get the most recent data point.

        Returns:
            The latest IndicatorDataPoint if data exists, None otherwise
        """
        return self.data[-1] if self.data else None

    @property
    def earliest(self) -> IndicatorDataPoint | None:
        """Get the earliest data point.

        Returns:
            The earliest IndicatorDataPoint if data exists, None otherwise
        """
        return self.data[0] if self.data else None
