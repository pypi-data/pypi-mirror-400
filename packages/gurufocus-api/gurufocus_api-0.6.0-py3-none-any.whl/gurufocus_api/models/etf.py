"""Pydantic models for GuruFocus ETF endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ETFInfo(BaseModel):
    """Basic information about an ETF."""

    name: str = Field(description="ETF name")


class ETFListResponse(BaseModel):
    """Paginated response containing list of ETFs."""

    current_page: int = Field(default=1, description="Current page number")
    per_page: int = Field(default=50, description="Items per page")
    last_page: int = Field(default=1, description="Last page number")
    total: int = Field(default=0, description="Total number of ETFs")
    etfs: list[ETFInfo] = Field(default_factory=list, description="List of ETFs")

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> ETFListResponse:
        """Parse API response into ETFListResponse.

        Args:
            data: API response dictionary

        Returns:
            Parsed ETFListResponse
        """
        etfs = [ETFInfo(name=item.get("name", "")) for item in data.get("data", [])]
        return cls(
            current_page=data.get("current_page", 1),
            per_page=data.get("per_page", 50),
            last_page=data.get("last_page", 1),
            total=data.get("total", 0),
            etfs=etfs,
        )


class IndustryWeighting(BaseModel):
    """Weighting data for an industry within a sector."""

    industry: str = Field(description="Industry name")
    weightings: dict[str, float] = Field(
        default_factory=dict,
        description="Date-keyed weightings (e.g., {'2025-09-30': 1.49})",
    )


class SectorWeighting(BaseModel):
    """Weighting data for a sector and its industries."""

    sector: str = Field(description="Sector name")
    weightings: dict[str, float] = Field(
        default_factory=dict,
        description="Date-keyed weightings (e.g., {'2025-09-30': 4.89})",
    )
    industries: list[IndustryWeighting] = Field(
        default_factory=list,
        description="List of industries within this sector",
    )


class ETFSectorWeightingResponse(BaseModel):
    """Response containing ETF sector and industry weightings."""

    name: str = Field(description="ETF name")
    sectors: list[SectorWeighting] = Field(
        default_factory=list,
        description="List of sectors with weightings",
    )

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> ETFSectorWeightingResponse:
        """Parse API response into ETFSectorWeightingResponse.

        Args:
            data: API response dictionary

        Returns:
            Parsed ETFSectorWeightingResponse
        """
        sectors = []
        for sector_data in data.get("data", []):
            industries = [
                IndustryWeighting(
                    industry=ind.get("industry", ""),
                    weightings=ind.get("weightings", {}),
                )
                for ind in sector_data.get("industries", [])
            ]
            sectors.append(
                SectorWeighting(
                    sector=sector_data.get("sector", ""),
                    weightings=sector_data.get("weightings", {}),
                    industries=industries,
                )
            )
        return cls(
            name=data.get("name", ""),
            sectors=sectors,
        )
