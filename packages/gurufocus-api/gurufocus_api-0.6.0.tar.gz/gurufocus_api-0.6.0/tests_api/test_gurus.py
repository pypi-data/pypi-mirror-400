"""Tests for guru-related endpoints."""

import json
from pathlib import Path

import pytest
import respx
from httpx import Response

from gurufocus_api import GuruFocusClient
from gurufocus_api.models.gurus import (
    GuruAggregatedPortfolio,
    GuruListResponse,
    GuruPicksResponse,
    GuruRealtimePicksResponse,
)

# Load test fixtures
FIXTURES_DIR = Path(__file__).parent / "data"


def load_fixture(category: str, filename: str) -> dict:
    """Load a JSON fixture file."""
    filepath = FIXTURES_DIR / category / filename
    with open(filepath) as f:
        return json.load(f)


# Pre-load fixtures
GURULIST_DATA = load_fixture("gurulist", "list.json")
GURU_AGGREGATED_DATA = load_fixture("guru_aggregated", "FAKEGURU1.json")
GURU_PICKS_DATA = load_fixture("guru_picks", "FAKEGURU1_2025-01-01_1.json")
GURU_REALTIME_PICKS_DATA = load_fixture("guru_realtime_picks", "page1.json")


class TestGurulistEndpoint:
    """Tests for GET /gurulist endpoint."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_gurulist_returns_response(self) -> None:
        """Test that get_gurulist returns a GuruListResponse."""
        respx.get("https://api.gurufocus.com/public/user/test-token/gurulist").mock(
            return_value=Response(200, json=GURULIST_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.gurus.get_gurulist()

        assert isinstance(result, GuruListResponse)
        assert len(result.us_gurus) == 5
        assert len(result.plus_gurus) == 2
        assert result.total_count == 7

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_gurulist_parses_us_gurus(self) -> None:
        """Test that US gurus are parsed correctly."""
        respx.get("https://api.gurufocus.com/public/user/test-token/gurulist").mock(
            return_value=Response(200, json=GURULIST_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.gurus.get_gurulist()

        first_guru = result.us_gurus[0]
        assert first_guru.guru_id == "1"
        assert first_guru.name == "Fake Guru One"
        assert first_guru.firm == "Fake Capital Management"
        assert first_guru.num_stocks == 25
        assert first_guru.equity == 5000
        assert first_guru.turnover == 3
        assert first_guru.cik == "0001234567"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_gurulist_raw_returns_dict(self) -> None:
        """Test that get_gurulist_raw returns raw dict."""
        respx.get("https://api.gurufocus.com/public/user/test-token/gurulist").mock(
            return_value=Response(200, json=GURULIST_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.gurus.get_gurulist_raw()

        assert isinstance(result, dict)
        assert "all" in result
        assert "us" in result["all"]


class TestGuruAggregatedEndpoint:
    """Tests for GET /guru/{id}/aggregated endpoint."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_guru_aggregated_returns_response(self) -> None:
        """Test that get_guru_aggregated returns a GuruAggregatedPortfolio."""
        respx.get("https://api.gurufocus.com/public/user/test-token/guru/1/aggregated").mock(
            return_value=Response(200, json=GURU_AGGREGATED_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.gurus.get_guru_aggregated("1")

        assert isinstance(result, GuruAggregatedPortfolio)
        assert result.guru_id == "1"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_guru_aggregated_parses_summary(self) -> None:
        """Test that summary is parsed correctly."""
        respx.get("https://api.gurufocus.com/public/user/test-token/guru/1/aggregated").mock(
            return_value=Response(200, json=GURU_AGGREGATED_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.gurus.get_guru_aggregated("1")

        assert result.summary.firm == "Fake Capital Management"
        assert result.summary.num_new == 3
        assert result.summary.number_of_stocks == 25
        assert result.summary.equity == 5000
        assert result.summary.turnover == 3
        assert result.summary.country == "USA"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_guru_aggregated_parses_holdings(self) -> None:
        """Test that holdings are parsed correctly."""
        respx.get("https://api.gurufocus.com/public/user/test-token/guru/1/aggregated").mock(
            return_value=Response(200, json=GURU_AGGREGATED_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.gurus.get_guru_aggregated("1")

        assert len(result.holdings) == 4

        first_holding = result.holdings[0]
        assert first_holding.symbol == "FAKEA"
        assert first_holding.company == "FakeAlpha Corp"
        assert first_holding.exchange == "NYSE"
        assert first_holding.shares == 1500000
        assert first_holding.price == 125.50

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_guru_aggregated_handles_sold_out(self) -> None:
        """Test that sold out positions are handled."""
        respx.get("https://api.gurufocus.com/public/user/test-token/guru/1/aggregated").mock(
            return_value=Response(200, json=GURU_AGGREGATED_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.gurus.get_guru_aggregated("1")

        # Find the sold out position
        sold_out = next((h for h in result.holdings if h.symbol == "FAKED"), None)
        assert sold_out is not None
        assert sold_out.shares == 0
        assert sold_out.change == "Sold Out"


class TestGuruPicksEndpoint:
    """Tests for GET /guru/{id}/picks/{start_date}/{page} endpoint."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_guru_picks_returns_response(self) -> None:
        """Test that get_guru_picks returns a GuruPicksResponse."""
        respx.get(
            "https://api.gurufocus.com/public/user/test-token/guru/1/picks/2025-01-01/1"
        ).mock(return_value=Response(200, json=GURU_PICKS_DATA))

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.gurus.get_guru_picks("1", "2025-01-01", 1)

        assert isinstance(result, GuruPicksResponse)
        assert result.guru_id == "1"
        assert result.guru_name == "Fake Guru One"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_guru_picks_parses_picks(self) -> None:
        """Test that picks are parsed correctly."""
        respx.get("https://api.gurufocus.com/public/user/test-token/guru/1/picks/all/1").mock(
            return_value=Response(200, json=GURU_PICKS_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.gurus.get_guru_picks("1")

        assert len(result.picks) == 5

        first_pick = result.picks[0]
        assert first_pick.symbol == "FAKEA"
        assert first_pick.action == "Add"
        assert first_pick.trade_type == "quarterly"
        assert first_pick.price == 125.50

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_guru_picks_with_date_filter(self) -> None:
        """Test that date filter is applied."""
        respx.get(
            "https://api.gurufocus.com/public/user/test-token/guru/1/picks/2024-01-01/1"
        ).mock(return_value=Response(200, json=GURU_PICKS_DATA))

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.gurus.get_guru_picks("1", "2024-01-01")

        assert isinstance(result, GuruPicksResponse)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_guru_picks_raw_returns_dict(self) -> None:
        """Test that get_guru_picks_raw returns raw dict."""
        respx.get("https://api.gurufocus.com/public/user/test-token/guru/1/picks/all/1").mock(
            return_value=Response(200, json=GURU_PICKS_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.gurus.get_guru_picks_raw("1")

        assert isinstance(result, dict)


class TestGuruRealtimePicksEndpoint:
    """Tests for GET /guru_realtime_picks endpoint."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_realtime_picks_returns_response(self) -> None:
        """Test that get_realtime_picks returns a GuruRealtimePicksResponse."""
        respx.get("https://api.gurufocus.com/public/user/test-token/guru_realtime_picks").mock(
            return_value=Response(200, json=GURU_REALTIME_PICKS_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.gurus.get_realtime_picks()

        assert isinstance(result, GuruRealtimePicksResponse)
        assert result.total == 125
        assert result.current_page == 1
        assert result.last_page == 7

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_realtime_picks_parses_picks(self) -> None:
        """Test that realtime picks are parsed correctly."""
        respx.get("https://api.gurufocus.com/public/user/test-token/guru_realtime_picks").mock(
            return_value=Response(200, json=GURU_REALTIME_PICKS_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.gurus.get_realtime_picks()

        assert len(result.picks) == 5

        first_pick = result.picks[0]
        assert first_pick.symbol == "FAKEA"
        assert first_pick.guru_name == "Fake Guru One"
        assert first_pick.action == "Add"
        assert first_pick.price == 125.50
        assert first_pick.impact == 1.25

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_realtime_picks_with_pagination(self) -> None:
        """Test that pagination works correctly."""
        respx.get("https://api.gurufocus.com/public/user/test-token/guru_realtime_picks").mock(
            return_value=Response(200, json=GURU_REALTIME_PICKS_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.gurus.get_realtime_picks(page=2)

        assert isinstance(result, GuruRealtimePicksResponse)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_realtime_picks_raw_returns_dict(self) -> None:
        """Test that get_realtime_picks_raw returns raw dict."""
        respx.get("https://api.gurufocus.com/public/user/test-token/guru_realtime_picks").mock(
            return_value=Response(200, json=GURU_REALTIME_PICKS_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.gurus.get_realtime_picks_raw()

        assert isinstance(result, dict)
        assert "data" in result


class TestGuruModelsEdgeCases:
    """Test edge cases in guru model parsing."""

    def test_gurulist_empty_response(self) -> None:
        """Test handling of empty gurulist response."""
        result = GuruListResponse.from_api_response({"all": {"us": [], "plus": []}})
        assert len(result.us_gurus) == 0
        assert len(result.plus_gurus) == 0
        assert result.total_count == 0

    def test_gurulist_missing_all_key(self) -> None:
        """Test handling of response missing 'all' key."""
        result = GuruListResponse.from_api_response({})
        assert len(result.us_gurus) == 0
        assert len(result.plus_gurus) == 0

    def test_guru_aggregated_empty_portfolio(self) -> None:
        """Test handling of empty aggregated portfolio."""
        result = GuruAggregatedPortfolio.from_api_response({"1": {"summary": {}, "port": []}}, "1")
        assert result.guru_id == "1"
        assert len(result.holdings) == 0

    def test_guru_picks_empty_port(self) -> None:
        """Test handling of empty picks response."""
        result = GuruPicksResponse.from_api_response({"Test Guru": {"port": []}}, "1")
        assert result.guru_id == "1"
        assert result.guru_name == "Test Guru"
        assert len(result.picks) == 0

    def test_guru_realtime_picks_empty_data(self) -> None:
        """Test handling of empty realtime picks."""
        result = GuruRealtimePicksResponse.from_api_response(
            {"data": [], "total": 0, "currentPage": "1", "lastPage": 1}
        )
        assert len(result.picks) == 0
        assert result.total == 0

    def test_gurulist_item_with_null_image(self) -> None:
        """Test that null image is handled correctly."""
        result = GuruListResponse.from_api_response(
            {
                "all": {
                    "us": [
                        [
                            "1",
                            "Test Guru",
                            None,
                            "Test Firm",
                            "10",
                            "1000",
                            "5",
                            "2025-01-01",
                            "",
                            "",
                            "",
                        ]
                    ],
                    "plus": [],
                }
            }
        )
        assert result.us_gurus[0].image_url is None
