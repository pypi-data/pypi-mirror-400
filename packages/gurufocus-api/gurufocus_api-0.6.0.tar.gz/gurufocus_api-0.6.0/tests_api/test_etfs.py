"""Tests for ETF endpoints."""

import json
from pathlib import Path

import pytest
import respx
from httpx import Response

from gurufocus_api import GuruFocusClient
from gurufocus_api.models.etf import ETFListResponse

# Load test fixtures
FIXTURES_DIR = Path(__file__).parent / "data"


def load_fixture(category: str, filename: str) -> dict | list:
    """Load a JSON fixture file."""
    filepath = FIXTURES_DIR / category / filename
    with open(filepath) as f:
        return json.load(f)


# Pre-load fixtures
ETF_LIST_DATA = load_fixture("etf_list", "page1.json")


class TestETFListEndpoint:
    """Tests for GET /etf/etf_list endpoint."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_etf_list_returns_response(self) -> None:
        """Test that get_etf_list returns an ETFListResponse."""
        respx.get("https://api.gurufocus.com/public/user/test-token/etf/etf_list").mock(
            return_value=Response(200, json=ETF_LIST_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.etfs.get_etf_list()

        assert isinstance(result, ETFListResponse)
        assert result.current_page == 1
        assert result.per_page == 50
        assert result.last_page == 127
        assert result.total == 6344

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_etf_list_parses_etfs(self) -> None:
        """Test that ETF data is parsed correctly."""
        respx.get("https://api.gurufocus.com/public/user/test-token/etf/etf_list").mock(
            return_value=Response(200, json=ETF_LIST_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.etfs.get_etf_list()

        assert len(result.etfs) == 5
        assert result.etfs[0].name == "Fake Alpha Growth ETF"
        assert result.etfs[1].name == "Fake Beta Value ETF"
        assert result.etfs[2].name == "Fake Gamma Income ETF"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_etf_list_with_pagination(self) -> None:
        """Test that pagination parameters are passed correctly."""
        respx.get(
            "https://api.gurufocus.com/public/user/test-token/etf/etf_list",
            params={"page": "2", "per_page": "100"},
        ).mock(return_value=Response(200, json=ETF_LIST_DATA))

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.etfs.get_etf_list(page=2, per_page=100)

        assert isinstance(result, ETFListResponse)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_etf_list_raw_returns_dict(self) -> None:
        """Test that get_etf_list_raw returns raw dict."""
        respx.get("https://api.gurufocus.com/public/user/test-token/etf/etf_list").mock(
            return_value=Response(200, json=ETF_LIST_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.etfs.get_etf_list_raw()

        assert isinstance(result, dict)
        assert "data" in result
        assert "current_page" in result


class TestETFModelsEdgeCases:
    """Test edge cases in ETF model parsing."""

    def test_etf_list_empty_response(self) -> None:
        """Test handling of empty ETF list."""
        result = ETFListResponse.from_api_response({"data": []})
        assert result.current_page == 1
        assert result.per_page == 50
        assert result.last_page == 1
        assert result.total == 0
        assert len(result.etfs) == 0

    def test_etf_list_missing_pagination(self) -> None:
        """Test handling of response missing pagination fields."""
        result = ETFListResponse.from_api_response({"data": [{"name": "Test ETF"}]})
        assert result.current_page == 1
        assert result.per_page == 50
        assert result.last_page == 1
        assert len(result.etfs) == 1
        assert result.etfs[0].name == "Test ETF"

    def test_etf_list_etf_missing_name(self) -> None:
        """Test handling of ETF with missing name."""
        result = ETFListResponse.from_api_response({"data": [{}]})
        assert len(result.etfs) == 1
        assert result.etfs[0].name == ""
