"""Pydantic models for operating and segment data."""

from contextlib import suppress
from typing import Any

from pydantic import BaseModel, Field


def _parse_float(value: Any) -> float | None:
    """Parse a float value, handling None and string values."""
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        if value in ("", "N/A", "-"):
            return None
    with suppress(TypeError, ValueError):
        return float(value)
    return None


class OperatingMetricData(BaseModel):
    """Time series data for an operating metric."""

    annual: dict[str, float] = Field(
        default_factory=dict, description="Annual data keyed by period (YYYY-MM)"
    )
    quarterly: dict[str, float] = Field(
        default_factory=dict, description="Quarterly data keyed by period (YYYY-MM)"
    )


class OperatingMetric(BaseModel):
    """A single operating metric with time series data."""

    name: str = Field(description="Human-readable metric name")
    key: str = Field(description="API key for the metric")
    data: OperatingMetricData = Field(description="Time series data")


class OperatingData(BaseModel):
    """Operating data for a stock.

    Contains operational KPIs like unit sales, capacity utilization,
    average selling price, etc. with annual and quarterly time series.
    """

    symbol: str = Field(description="Stock ticker symbol")
    metrics: dict[str, OperatingMetric] = Field(
        default_factory=dict, description="Operating metrics keyed by metric key"
    )

    @classmethod
    def from_api_response(cls, data: dict[str, Any], symbol: str) -> "OperatingData":
        """Create OperatingData from raw API response.

        Args:
            data: Raw JSON response from the API
                  Format: {symbol: {metric_key: {name, key, data: {annual, quarter}}}}
            symbol: Stock ticker symbol

        Returns:
            Populated OperatingData instance
        """
        symbol = symbol.upper().strip()
        metrics: dict[str, OperatingMetric] = {}

        # API returns {symbol: {metrics...}}
        symbol_data = data.get(symbol, {})
        if not isinstance(symbol_data, dict):
            return cls(symbol=symbol, metrics={})

        for metric_key, metric_data in symbol_data.items():
            if not isinstance(metric_data, dict):
                continue

            # Parse annual data
            annual_raw = metric_data.get("data", {}).get("annual", {})
            annual: dict[str, float] = {}
            if isinstance(annual_raw, dict):
                for period, value in annual_raw.items():
                    parsed = _parse_float(value)
                    if parsed is not None:
                        annual[period] = parsed

            # Parse quarterly data (API uses "quarter" not "quarterly")
            quarterly_raw = metric_data.get("data", {}).get("quarter", {})
            quarterly: dict[str, float] = {}
            if isinstance(quarterly_raw, dict):
                for period, value in quarterly_raw.items():
                    parsed = _parse_float(value)
                    if parsed is not None:
                        quarterly[period] = parsed

            metrics[metric_key] = OperatingMetric(
                name=metric_data.get("name", metric_key),
                key=metric_data.get("key", metric_key),
                data=OperatingMetricData(annual=annual, quarterly=quarterly),
            )

        return cls(symbol=symbol, metrics=metrics)


class SegmentPeriodData(BaseModel):
    """Segment revenue/data for a single period."""

    date: str = Field(description="Period date (YYYY-MM)")
    segments: dict[str, float] = Field(default_factory=dict, description="Revenue by segment name")


class SegmentType(BaseModel):
    """A segment type (business or geographic) with time series."""

    annual: list[SegmentPeriodData] = Field(default_factory=list, description="Annual segment data")
    quarterly: list[SegmentPeriodData] = Field(
        default_factory=list, description="Quarterly segment data"
    )
    ttm: list[SegmentPeriodData] = Field(
        default_factory=list, description="Trailing twelve months data"
    )
    keys: list[str] = Field(default_factory=list, description="Segment names")


class SegmentData(BaseModel):
    """Segment data for a stock.

    Contains business and geographic segment breakdowns with
    revenue data by segment and time period.
    """

    symbol: str = Field(description="Stock ticker symbol")
    business: SegmentType = Field(
        default_factory=SegmentType, description="Business segment breakdown"
    )
    geographic: SegmentType = Field(
        default_factory=SegmentType, description="Geographic segment breakdown"
    )

    @classmethod
    def from_api_response(cls, data: dict[str, Any], symbol: str) -> "SegmentData":
        """Create SegmentData from raw API response.

        Args:
            data: Raw JSON response from the API
                  Format: {business: {annual, quarterly, ttm, keys}, geographic: {...}}
            symbol: Stock ticker symbol

        Returns:
            Populated SegmentData instance
        """
        symbol = symbol.upper().strip()

        def parse_segment_type(segment_data: dict[str, Any]) -> SegmentType:
            """Parse a segment type (business or geographic)."""
            if not isinstance(segment_data, dict):
                return SegmentType()

            keys = segment_data.get("keys", [])
            if not isinstance(keys, list):
                keys = []

            def parse_period_list(period_list: list[dict[str, Any]]) -> list[SegmentPeriodData]:
                """Parse a list of period data."""
                result: list[SegmentPeriodData] = []
                if not isinstance(period_list, list):
                    return result

                for item in period_list:
                    if not isinstance(item, dict):
                        continue
                    date = item.get("date", "")
                    segments: dict[str, float] = {}
                    for key in keys:
                        value = _parse_float(item.get(key))
                        if value is not None:
                            segments[key] = value
                    if date and segments:
                        result.append(SegmentPeriodData(date=date, segments=segments))

                return result

            return SegmentType(
                annual=parse_period_list(segment_data.get("annual", [])),
                quarterly=parse_period_list(segment_data.get("quarterly", [])),
                ttm=parse_period_list(segment_data.get("ttm", [])),
                keys=keys,
            )

        return cls(
            symbol=symbol,
            business=parse_segment_type(data.get("business", {})),
            geographic=parse_segment_type(data.get("geographic", {})),
        )
