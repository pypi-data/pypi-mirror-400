"""Pydantic models for stock ownership data."""

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
        # Remove percentage sign and parenthetical units
        value = value.replace("%", "").replace(",", "")
        # Extract numeric portion (remove units like "(Mil)")
        if "(" in value:
            value = value.split("(")[0].strip()
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


class OwnershipBreakdown(BaseModel):
    """Ownership percentage and value."""

    percentage: float | None = Field(default=None, description="Ownership percentage")
    value: float | None = Field(default=None, description="Number of shares (in millions)")


class StockOwnership(BaseModel):
    """Current stock ownership breakdown.

    Contains information about institutional vs insider ownership,
    shares outstanding, and float percentage.
    """

    symbol: str = Field(description="Stock ticker symbol")
    company: str | None = Field(default=None, description="Company name")
    exchange: str | None = Field(default=None, description="Stock exchange")

    shares_outstanding: float | None = Field(
        default=None, description="Total shares outstanding (in millions)"
    )
    institutional_ownership: OwnershipBreakdown | None = Field(
        default=None, description="Institutional ownership breakdown"
    )
    insider_ownership: OwnershipBreakdown | None = Field(
        default=None, description="Insider ownership breakdown"
    )
    float_percentage: OwnershipBreakdown | None = Field(
        default=None, description="Float percentage of total shares"
    )

    @classmethod
    def from_api_response(cls, data: dict[str, Any], symbol: str) -> "StockOwnership":
        """Parse raw API response into StockOwnership model.

        Args:
            data: Raw API response dictionary
            symbol: Stock ticker symbol

        Returns:
            StockOwnership instance with parsed data
        """
        symbol = symbol.upper().strip()

        # Parse shares outstanding
        shares_out_raw = data.get("Share_Outstanding", {})
        shares_outstanding = _parse_float(
            shares_out_raw.get("value") if isinstance(shares_out_raw, dict) else shares_out_raw
        )

        # Parse institutional ownership
        inst_raw = data.get("Institutional_Ownership", {})
        inst_ownership = None
        if isinstance(inst_raw, dict):
            inst_ownership = OwnershipBreakdown(
                percentage=_parse_float(inst_raw.get("percentage")),
                value=_parse_float(inst_raw.get("value")),
            )

        # Parse insider ownership
        insider_raw = data.get("Insider_Ownership", {})
        insider_ownership = None
        if isinstance(insider_raw, dict):
            insider_ownership = OwnershipBreakdown(
                percentage=_parse_float(insider_raw.get("percentage")),
                value=_parse_float(insider_raw.get("value")),
            )

        # Parse float percentage
        float_raw = data.get("Float_Percentage_of_TSO", {})
        float_pct = None
        if isinstance(float_raw, dict):
            float_pct = OwnershipBreakdown(
                percentage=_parse_float(float_raw.get("percentage")),
                value=_parse_float(float_raw.get("value")),
            )

        return cls(
            symbol=data.get("display_symbol", symbol),
            company=data.get("company"),
            exchange=data.get("exchange"),
            shares_outstanding=shares_outstanding,
            institutional_ownership=inst_ownership,
            insider_ownership=insider_ownership,
            float_percentage=float_pct,
        )


class OwnershipHistoryPoint(BaseModel):
    """A single point in ownership history time series."""

    date: str = Field(description="Date in YYYY-MM-DD format")
    percentage: float | None = Field(default=None, description="Ownership percentage")
    shares: float | None = Field(default=None, description="Number of shares (in millions)")


class OwnershipHistory(BaseModel):
    """Historical ownership data for a stock.

    Contains time series data for institutional ownership,
    shares outstanding, and institution shares held.
    """

    symbol: str = Field(description="Stock ticker symbol")
    institutional_ownership: list[OwnershipHistoryPoint] = Field(
        default_factory=list,
        description="Historical institutional ownership percentage and shares",
    )
    shares_outstanding: list[OwnershipHistoryPoint] = Field(
        default_factory=list,
        description="Historical shares outstanding",
    )
    institution_shares_held: list[OwnershipHistoryPoint] = Field(
        default_factory=list,
        description="Historical institution shares held",
    )

    @classmethod
    def from_api_response(cls, data: dict[str, Any], symbol: str) -> "OwnershipHistory":
        """Parse raw API response into OwnershipHistory model.

        Args:
            data: Raw API response dictionary
            symbol: Stock ticker symbol

        Returns:
            OwnershipHistory instance with parsed data
        """
        symbol = symbol.upper().strip()

        # Parse institutional ownership (format: [date, percentage, shares])
        inst_ownership = []
        for item in data.get("insti_owner", []):
            if isinstance(item, list) and len(item) >= 2:
                inst_ownership.append(
                    OwnershipHistoryPoint(
                        date=str(item[0]),
                        percentage=float(item[1]) if item[1] is not None else None,
                        shares=float(item[2]) if len(item) > 2 and item[2] is not None else None,
                    )
                )

        # Parse shares outstanding (format: [date, shares])
        shares_out = []
        for item in data.get("shares_outstanding", []):
            if isinstance(item, list) and len(item) >= 2:
                shares_out.append(
                    OwnershipHistoryPoint(
                        date=str(item[0]),
                        percentage=None,
                        shares=float(item[1]) if item[1] is not None else None,
                    )
                )

        # Parse institution shares held (format: [date, shares, shares])
        inst_shares = []
        for item in data.get("InstitutionSharesHeld", []):
            if isinstance(item, list) and len(item) >= 2:
                inst_shares.append(
                    OwnershipHistoryPoint(
                        date=str(item[0]),
                        percentage=None,
                        shares=float(item[1]) if item[1] is not None else None,
                    )
                )

        return cls(
            symbol=symbol,
            institutional_ownership=inst_ownership,
            shares_outstanding=shares_out,
            institution_shares_held=inst_shares,
        )
