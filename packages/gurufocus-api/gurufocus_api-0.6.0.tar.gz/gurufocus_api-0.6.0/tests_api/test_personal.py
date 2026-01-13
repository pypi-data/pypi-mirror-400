"""Tests for personal/user data endpoints."""

import json
from pathlib import Path

import pytest
import respx
from httpx import Response

from gurufocus_api import GuruFocusClient
from gurufocus_api.models.personal import (
    APIUsageResponse,
    PortfolioDetailResponse,
    PortfoliosResponse,
    UserScreenerResultsResponse,
    UserScreenersResponse,
)

# Load test fixtures
FIXTURES_DIR = Path(__file__).parent / "data"


def load_fixture(category: str, filename: str) -> dict | list:
    """Load a JSON fixture file."""
    filepath = FIXTURES_DIR / category / filename
    with open(filepath) as f:
        return json.load(f)


# Pre-load fixtures
API_USAGE_DATA = load_fixture("api_usage", "usage.json")
USER_SCREENERS_DATA = load_fixture("user_screeners", "list.json")
USER_SCREENER_RESULTS_DATA = load_fixture("user_screener_results", "FAKE1.json")
PORTFOLIOS_DATA = load_fixture("portfolios", "FAKE1.json")
PORTFOLIO_DETAIL_DATA = load_fixture("portfolio_detail", "FAKE1.json")


class TestAPIUsageEndpoint:
    """Tests for GET /api_usage endpoint."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_api_usage_returns_response(self) -> None:
        """Test that get_api_usage returns an APIUsageResponse."""
        respx.get("https://api.gurufocus.com/public/user/test-token/api_usage").mock(
            return_value=Response(200, json=API_USAGE_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.personal.get_api_usage()

        assert isinstance(result, APIUsageResponse)
        assert result.api_usage == 158
        assert result.api_requests_remaining == 3842

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_api_usage_raw_returns_dict(self) -> None:
        """Test that get_api_usage_raw returns raw dict."""
        respx.get("https://api.gurufocus.com/public/user/test-token/api_usage").mock(
            return_value=Response(200, json=API_USAGE_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.personal.get_api_usage_raw()

        assert isinstance(result, dict)
        assert "API Usage" in result
        assert "API Requests Remaining" in result


class TestUserScreenersEndpoint:
    """Tests for GET /user_screeners endpoint."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_user_screeners_returns_response(self) -> None:
        """Test that get_user_screeners returns an UserScreenersResponse."""
        respx.get("https://api.gurufocus.com/public/user/test-token/user_screeners").mock(
            return_value=Response(200, json=USER_SCREENERS_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.personal.get_user_screeners()

        assert isinstance(result, UserScreenersResponse)
        assert result.count == 3
        assert len(result.screeners) == 3

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_user_screeners_parses_data(self) -> None:
        """Test that screener data is parsed correctly."""
        respx.get("https://api.gurufocus.com/public/user/test-token/user_screeners").mock(
            return_value=Response(200, json=USER_SCREENERS_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.personal.get_user_screeners()

        first = result.screeners[0]
        assert first.id == 100001
        assert first.name == "Fake Value Screener"
        assert first.short_description == "Finds undervalued stocks"
        assert first.note == "My custom value screen"
        assert first.is_public is False
        assert first.is_predefined is False
        assert "NAS" in first.default_exchanges
        assert "NYSE" in first.default_exchanges

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_user_screeners_raw_returns_list(self) -> None:
        """Test that get_user_screeners_raw returns raw list."""
        respx.get("https://api.gurufocus.com/public/user/test-token/user_screeners").mock(
            return_value=Response(200, json=USER_SCREENERS_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.personal.get_user_screeners_raw()

        assert isinstance(result, list)
        assert len(result) == 3


class TestPersonalModelsEdgeCases:
    """Test edge cases in personal model parsing."""

    def test_api_usage_empty_response(self) -> None:
        """Test handling of empty API usage response."""
        result = APIUsageResponse.from_api_response({})
        assert result.api_usage == 0
        assert result.api_requests_remaining == 0

    def test_user_screeners_empty_response(self) -> None:
        """Test handling of empty screeners list."""
        result = UserScreenersResponse.from_api_response([])
        assert result.count == 0
        assert len(result.screeners) == 0

    def test_user_screener_missing_optional_fields(self) -> None:
        """Test handling of screener with missing optional fields."""
        result = UserScreenersResponse.from_api_response([{"id": 1, "name": "Test"}])
        assert len(result.screeners) == 1
        screener = result.screeners[0]
        assert screener.id == 1
        assert screener.name == "Test"
        assert screener.short_description is None
        assert screener.note is None
        assert screener.is_public is False
        assert screener.default_exchanges == []


class TestUserScreenerResultsEndpoint:
    """Tests for GET /user_screeners/{id}/{page} endpoint."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_user_screener_results_returns_response(self) -> None:
        """Test that get_user_screener_results returns a UserScreenerResultsResponse."""
        respx.get("https://api.gurufocus.com/public/user/test-token/user_screeners/123/1").mock(
            return_value=Response(200, json=USER_SCREENER_RESULTS_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.personal.get_user_screener_results(123, page=1)

        assert isinstance(result, UserScreenerResultsResponse)
        assert result.screener_id == 123
        assert result.page == 1
        assert result.count == 3
        assert len(result.stocks) == 3

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_user_screener_results_parses_stocks(self) -> None:
        """Test that screener result stocks are parsed correctly."""
        respx.get("https://api.gurufocus.com/public/user/test-token/user_screeners/123/1").mock(
            return_value=Response(200, json=USER_SCREENER_RESULTS_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.personal.get_user_screener_results(123)

        first = result.stocks[0]
        assert first.symbol == "AAPL"
        assert first.exchange == "NAS"
        assert first.company == "Apple Inc"
        assert first.sector == "Technology"
        assert first.industry == "Consumer Electronics"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_user_screener_results_raw_returns_list(self) -> None:
        """Test that get_user_screener_results_raw returns raw list."""
        respx.get("https://api.gurufocus.com/public/user/test-token/user_screeners/123/2").mock(
            return_value=Response(200, json=USER_SCREENER_RESULTS_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.personal.get_user_screener_results_raw(123, page=2)

        assert isinstance(result, list)
        assert len(result) == 3


@pytest.mark.skip(
    reason="Portfolio endpoints disabled as of 2025-12-29 - API not returning valid response"
)
class TestPortfoliosEndpoint:
    """Tests for GET /v2/{token}/portfolios endpoint."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_portfolios_returns_response(self) -> None:
        """Test that get_portfolios returns a PortfoliosResponse."""
        respx.get("https://api.gurufocus.com/public/v2/test-token/portfolios").mock(
            return_value=Response(200, json=PORTFOLIOS_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.personal.get_portfolios()

        assert isinstance(result, PortfoliosResponse)
        assert result.count == 2
        assert len(result.portfolios) == 2

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_portfolios_parses_data(self) -> None:
        """Test that portfolio data is parsed correctly."""
        respx.get("https://api.gurufocus.com/public/v2/test-token/portfolios").mock(
            return_value=Response(200, json=PORTFOLIOS_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.personal.get_portfolios()

        first = result.portfolios[0]
        assert first.id == 12345
        assert first.name == "My Tech Portfolio"
        assert first.currency == "USD"
        assert first.note == "Long-term tech investments"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_portfolios_raw_returns_list(self) -> None:
        """Test that get_portfolios_raw returns raw list."""
        respx.get("https://api.gurufocus.com/public/v2/test-token/portfolios").mock(
            return_value=Response(200, json=PORTFOLIOS_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.personal.get_portfolios_raw()

        assert isinstance(result, list)
        assert len(result) == 2


@pytest.mark.skip(
    reason="Portfolio endpoints disabled as of 2025-12-29 - API not returning valid response"
)
class TestPortfolioDetailEndpoint:
    """Tests for POST /v2/{token}/portfolios/{id} endpoint."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_portfolio_detail_returns_response(self) -> None:
        """Test that get_portfolio_detail returns a PortfolioDetailResponse."""
        respx.post("https://api.gurufocus.com/public/v2/test-token/portfolios/12345").mock(
            return_value=Response(200, json=PORTFOLIO_DETAIL_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.personal.get_portfolio_detail(12345)

        assert isinstance(result, PortfolioDetailResponse)
        assert result.portfolio_id == 12345
        assert result.name == "My Tech Portfolio"
        assert result.currency == "USD"
        assert result.total_value == 150000.00
        assert result.total_cost == 120000.00
        assert result.total_gain_loss == 30000.00
        assert result.holdings_count == 3

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_portfolio_detail_parses_holdings(self) -> None:
        """Test that portfolio holdings are parsed correctly."""
        respx.post("https://api.gurufocus.com/public/v2/test-token/portfolios/12345").mock(
            return_value=Response(200, json=PORTFOLIO_DETAIL_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.personal.get_portfolio_detail(12345)

        first = result.holdings[0]
        assert first.symbol == "AAPL"
        assert first.exchange == "NAS"
        assert first.company == "Apple Inc"
        assert first.shares == 100.0
        assert first.cost_basis == 150.00
        assert first.current_price == 195.00
        assert first.market_value == 19500.00
        assert first.gain_loss == 4500.00
        assert first.gain_loss_percent == 30.0
        assert first.weight == 13.0

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_portfolio_detail_raw_returns_dict(self) -> None:
        """Test that get_portfolio_detail_raw returns raw dict."""
        respx.post("https://api.gurufocus.com/public/v2/test-token/portfolios/12345").mock(
            return_value=Response(200, json=PORTFOLIO_DETAIL_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.personal.get_portfolio_detail_raw(12345)

        assert isinstance(result, dict)
        assert "holdings" in result
        assert len(result["holdings"]) == 3


class TestNewPersonalModelsEdgeCases:
    """Test edge cases in new personal model parsing."""

    def test_screener_results_empty_response(self) -> None:
        """Test handling of empty screener results."""
        result = UserScreenerResultsResponse.from_api_response([], 123, 1)
        assert result.screener_id == 123
        assert result.page == 1
        assert result.count == 0
        assert len(result.stocks) == 0

    def test_portfolios_empty_response(self) -> None:
        """Test handling of empty portfolios list."""
        result = PortfoliosResponse.from_api_response([])
        assert result.count == 0
        assert len(result.portfolios) == 0

    def test_portfolio_detail_empty_holdings(self) -> None:
        """Test handling of portfolio with no holdings."""
        result = PortfolioDetailResponse.from_api_response(
            {"name": "Empty", "currency": "USD", "holdings": []}, 123
        )
        assert result.portfolio_id == 123
        assert result.name == "Empty"
        assert result.holdings_count == 0
        assert len(result.holdings) == 0

    def test_portfolio_detail_missing_fields(self) -> None:
        """Test handling of portfolio with missing optional fields."""
        result = PortfolioDetailResponse.from_api_response({}, 123)
        assert result.portfolio_id == 123
        assert result.name == ""
        assert result.currency == "USD"
        assert result.total_value == 0.0
        assert result.total_cost == 0.0
        assert result.total_gain_loss == 0.0
        assert result.holdings_count == 0
