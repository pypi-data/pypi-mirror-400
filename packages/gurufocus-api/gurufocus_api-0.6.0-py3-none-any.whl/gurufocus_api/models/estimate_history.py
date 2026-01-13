"""Pydantic models for GuruFocus estimate history endpoint."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class EstimatePeriodData(BaseModel):
    """Data for a single estimate period (fiscal year or quarter)."""

    period: str = Field(description="Fiscal period (YYYYMM format, e.g., '202509')")
    earnings_release_date: str = Field(default="", description="Date earnings were released")
    price_change: float | None = Field(default=None, description="Stock price change on release")
    actual: float | None = Field(default=None, description="Actual reported value")
    estimate_mean: float | None = Field(default=None, description="Mean analyst estimate")
    difference: float | None = Field(default=None, description="Actual minus estimate")
    surprise_pct: float | None = Field(default=None, description="Surprise percentage")


class EstimateMetric(BaseModel):
    """A single estimate metric with historical periods."""

    metric_name: str = Field(description="Name of the metric (e.g., 'eps_estimate')")
    periods: list[EstimatePeriodData] = Field(
        default_factory=list, description="Historical period data"
    )


class EstimateHistoryResponse(BaseModel):
    """Response containing estimate history for a stock."""

    symbol: str = Field(description="Stock ticker symbol")
    annual: list[EstimateMetric] = Field(
        default_factory=list, description="Annual estimate metrics"
    )
    quarterly: list[EstimateMetric] = Field(
        default_factory=list, description="Quarterly estimate metrics"
    )

    @classmethod
    def from_api_response(cls, data: dict[str, Any], symbol: str) -> EstimateHistoryResponse:
        """Parse API response into EstimateHistoryResponse.

        Args:
            data: API response dictionary
            symbol: Stock ticker symbol

        Returns:
            Parsed EstimateHistoryResponse
        """

        def parse_metrics(
            metrics_data: dict[str, Any] | None,
        ) -> list[EstimateMetric]:
            """Parse metrics from API data."""
            if not metrics_data:
                return []

            result = []
            for metric_name, periods_data in metrics_data.items():
                periods = []
                if isinstance(periods_data, dict):
                    for period_key, period_values in periods_data.items():
                        if isinstance(period_values, dict):
                            periods.append(
                                EstimatePeriodData(
                                    period=period_key,
                                    earnings_release_date=period_values.get(
                                        "earnings_release_date", ""
                                    ),
                                    price_change=period_values.get("price_change"),
                                    actual=period_values.get("actual"),
                                    estimate_mean=period_values.get("surprisemean"),
                                    difference=period_values.get("difference"),
                                    surprise_pct=period_values.get("surprise_pct"),
                                )
                            )
                # Sort by period descending (most recent first)
                periods.sort(key=lambda x: x.period, reverse=True)
                result.append(EstimateMetric(metric_name=metric_name, periods=periods))
            return result

        return cls(
            symbol=symbol.upper(),
            annual=parse_metrics(data.get("annual")),
            quarterly=parse_metrics(data.get("quarterly")),
        )
