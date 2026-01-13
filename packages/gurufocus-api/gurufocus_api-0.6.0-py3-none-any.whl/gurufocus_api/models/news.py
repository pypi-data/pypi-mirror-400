"""Pydantic models for GuruFocus news feed endpoint."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class NewsItem(BaseModel):
    """A single news item from the news feed."""

    date: str = Field(description="Publication date/time")
    headline: str = Field(description="News headline")
    url: str = Field(default="", description="URL to the full article")


class NewsFeedResponse(BaseModel):
    """Response containing news feed items."""

    items: list[NewsItem] = Field(default_factory=list, description="List of news items")
    count: int = Field(default=0, description="Number of news items")

    @classmethod
    def from_api_response(cls, data: list[dict[str, Any]]) -> NewsFeedResponse:
        """Parse API response into NewsFeedResponse.

        Args:
            data: List of news items from API

        Returns:
            Parsed NewsFeedResponse
        """
        items = [
            NewsItem(
                date=item.get("date", ""),
                headline=item.get("headline", ""),
                url=item.get("url", ""),
            )
            for item in data
        ]
        return cls(items=items, count=len(items))
