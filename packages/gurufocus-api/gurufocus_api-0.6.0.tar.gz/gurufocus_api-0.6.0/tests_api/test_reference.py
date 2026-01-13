"""Tests for reference data endpoints (exchanges and indexes)."""

import json
from pathlib import Path

import pytest
import respx
from httpx import Response

from gurufocus_api import GuruFocusClient
from gurufocus_api.models.reference import (
    CountryCurrencyResponse,
    ExchangeListResponse,
    ExchangeStocksResponse,
    FundaUpdatedResponse,
    IndexListResponse,
    IndexStocksResponse,
)

# Load test fixtures
FIXTURES_DIR = Path(__file__).parent / "data"


def load_fixture(category: str, filename: str) -> dict | list:
    """Load a JSON fixture file."""
    filepath = FIXTURES_DIR / category / filename
    with open(filepath) as f:
        return json.load(f)


# Pre-load fixtures
EXCHANGE_LIST_DATA = load_fixture("exchange_list", "list.json")
EXCHANGE_STOCKS_DATA = load_fixture("exchange_stocks", "NYSE.json")
INDEX_LIST_DATA = load_fixture("index_list", "list.json")
INDEX_STOCKS_DATA = load_fixture("index_stocks", "GSPC.json")
COUNTRY_CURRENCY_DATA = load_fixture("country_currency", "list.json")
FUNDA_UPDATED_DATA = load_fixture("funda_updated", "2025-01-15.json")


class TestExchangeListEndpoint:
    """Tests for GET /exchange_list endpoint."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_exchange_list_returns_response(self) -> None:
        """Test that get_exchange_list returns an ExchangeListResponse."""
        respx.get("https://api.gurufocus.com/public/user/test-token/exchange_list").mock(
            return_value=Response(200, json=EXCHANGE_LIST_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.reference.get_exchange_list()

        assert isinstance(result, ExchangeListResponse)
        assert result.total_countries == 5
        assert result.total_exchanges == 9

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_exchange_list_parses_data(self) -> None:
        """Test that exchange data is parsed correctly."""
        respx.get("https://api.gurufocus.com/public/user/test-token/exchange_list").mock(
            return_value=Response(200, json=EXCHANGE_LIST_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.reference.get_exchange_list()

        # Check USA exchanges
        assert "USA" in result.exchanges_by_country
        us_exchanges = result.exchanges_by_country["USA"]
        assert "NAS" in us_exchanges
        assert "NYSE" in us_exchanges
        assert "AMEX" in us_exchanges

        # Check UK exchanges
        assert "UK" in result.exchanges_by_country
        assert "LSE" in result.exchanges_by_country["UK"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_exchange_list_raw_returns_dict(self) -> None:
        """Test that get_exchange_list_raw returns raw dict."""
        respx.get("https://api.gurufocus.com/public/user/test-token/exchange_list").mock(
            return_value=Response(200, json=EXCHANGE_LIST_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.reference.get_exchange_list_raw()

        assert isinstance(result, dict)
        assert "USA" in result


class TestExchangeStocksEndpoint:
    """Tests for GET /exchange_stocks/{exchange} endpoint."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_exchange_stocks_returns_response(self) -> None:
        """Test that get_exchange_stocks returns an ExchangeStocksResponse."""
        respx.get("https://api.gurufocus.com/public/user/test-token/exchange_stocks/NYSE").mock(
            return_value=Response(200, json=EXCHANGE_STOCKS_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.reference.get_exchange_stocks("NYSE")

        assert isinstance(result, ExchangeStocksResponse)
        assert result.exchange == "NYSE"
        assert result.count == 5
        assert len(result.stocks) == 5

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_exchange_stocks_parses_stock_data(self) -> None:
        """Test that stock data is parsed correctly."""
        respx.get("https://api.gurufocus.com/public/user/test-token/exchange_stocks/NYSE").mock(
            return_value=Response(200, json=EXCHANGE_STOCKS_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.reference.get_exchange_stocks("NYSE")

        first = result.stocks[0]
        assert first.symbol == "FAKEA"
        assert first.exchange == "NYSE"
        assert first.company == "FakeAlpha Corp"
        assert first.currency == "USD"
        assert first.industry == "Technology"
        assert first.sector == "Information Technology"
        assert first.subindustry == "Software"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_exchange_stocks_normalizes_exchange(self) -> None:
        """Test that exchange code is normalized to uppercase."""
        respx.get("https://api.gurufocus.com/public/user/test-token/exchange_stocks/NYSE").mock(
            return_value=Response(200, json=EXCHANGE_STOCKS_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.reference.get_exchange_stocks("nyse")

        assert result.exchange == "NYSE"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_exchange_stocks_raw_returns_list(self) -> None:
        """Test that get_exchange_stocks_raw returns raw list."""
        respx.get("https://api.gurufocus.com/public/user/test-token/exchange_stocks/NYSE").mock(
            return_value=Response(200, json=EXCHANGE_STOCKS_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.reference.get_exchange_stocks_raw("NYSE")

        assert isinstance(result, list)
        assert len(result) == 5


class TestIndexListEndpoint:
    """Tests for GET /index_list endpoint."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_index_list_returns_response(self) -> None:
        """Test that get_index_list returns an IndexListResponse."""
        respx.get("https://api.gurufocus.com/public/user/test-token/index_list").mock(
            return_value=Response(200, json=INDEX_LIST_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.reference.get_index_list()

        assert isinstance(result, IndexListResponse)
        assert result.count == 5
        assert len(result.indexes) == 5

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_index_list_parses_index_data(self) -> None:
        """Test that index data is parsed correctly."""
        respx.get("https://api.gurufocus.com/public/user/test-token/index_list").mock(
            return_value=Response(200, json=INDEX_LIST_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.reference.get_index_list()

        # Find S&P 500
        sp500 = next((idx for idx in result.indexes if idx.symbol == "^GSPC"), None)
        assert sp500 is not None
        assert sp500.name == "S&P 500"

        # Find Dow 30
        dow = next((idx for idx in result.indexes if idx.symbol == "^DJI"), None)
        assert dow is not None
        assert dow.name == "Dow 30"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_index_list_raw_returns_list(self) -> None:
        """Test that get_index_list_raw returns raw list."""
        respx.get("https://api.gurufocus.com/public/user/test-token/index_list").mock(
            return_value=Response(200, json=INDEX_LIST_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.reference.get_index_list_raw()

        assert isinstance(result, list)
        assert len(result) == 5


class TestIndexStocksEndpoint:
    """Tests for GET /index_stocks/{symbol} endpoint."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_index_stocks_returns_response(self) -> None:
        """Test that get_index_stocks returns an IndexStocksResponse."""
        respx.get("https://api.gurufocus.com/public/user/test-token/index_stocks/^GSPC").mock(
            return_value=Response(200, json=INDEX_STOCKS_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.reference.get_index_stocks("^GSPC")

        assert isinstance(result, IndexStocksResponse)
        assert result.index_symbol == "^GSPC"
        assert result.count == 5
        assert len(result.stocks) == 5

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_index_stocks_parses_stock_data(self) -> None:
        """Test that constituent stock data is parsed correctly."""
        respx.get("https://api.gurufocus.com/public/user/test-token/index_stocks/^GSPC").mock(
            return_value=Response(200, json=INDEX_STOCKS_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.reference.get_index_stocks("^GSPC")

        # Find Apple
        aapl = next((s for s in result.stocks if s.symbol == "AAPL"), None)
        assert aapl is not None
        assert aapl.exchange == "NAS"
        assert aapl.company == "Fake Apple Inc"
        assert aapl.currency == "USD"
        assert aapl.sector == "Technology"
        assert aapl.industry == "Consumer Electronics"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_index_stocks_with_pagination(self) -> None:
        """Test that pagination parameter is passed correctly."""
        respx.get(
            "https://api.gurufocus.com/public/user/test-token/index_stocks/^GSPC",
            params={"page": "2"},
        ).mock(return_value=Response(200, json=INDEX_STOCKS_DATA))

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.reference.get_index_stocks("^GSPC", page=2)

        assert isinstance(result, IndexStocksResponse)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_index_stocks_raw_returns_list(self) -> None:
        """Test that get_index_stocks_raw returns raw list."""
        respx.get("https://api.gurufocus.com/public/user/test-token/index_stocks/^GSPC").mock(
            return_value=Response(200, json=INDEX_STOCKS_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.reference.get_index_stocks_raw("^GSPC")

        assert isinstance(result, list)
        assert len(result) == 5


class TestReferenceModelsEdgeCases:
    """Test edge cases in reference model parsing."""

    def test_exchange_list_empty_response(self) -> None:
        """Test handling of empty exchange list."""
        result = ExchangeListResponse.from_api_response({})
        assert result.total_countries == 0
        assert result.total_exchanges == 0
        assert result.exchanges_by_country == {}

    def test_exchange_stocks_empty_list(self) -> None:
        """Test handling of empty stocks list."""
        result = ExchangeStocksResponse.from_api_response([], "NYSE")
        assert result.exchange == "NYSE"
        assert result.count == 0
        assert len(result.stocks) == 0

    def test_index_list_empty_response(self) -> None:
        """Test handling of empty index list."""
        result = IndexListResponse.from_api_response([])
        assert result.count == 0
        assert len(result.indexes) == 0

    def test_index_stocks_empty_list(self) -> None:
        """Test handling of empty constituent list."""
        result = IndexStocksResponse.from_api_response([], "^GSPC")
        assert result.index_symbol == "^GSPC"
        assert result.count == 0
        assert len(result.stocks) == 0

    def test_exchange_stocks_missing_optional_fields(self) -> None:
        """Test handling of stocks with missing optional fields."""
        result = ExchangeStocksResponse.from_api_response(
            [
                {
                    "symbol": "TEST",
                    "exchange": "NYSE",
                    "company": "Test Corp",
                }
            ],
            "NYSE",
        )
        assert len(result.stocks) == 1
        stock = result.stocks[0]
        assert stock.symbol == "TEST"
        assert stock.currency == ""
        assert stock.industry == ""
        assert stock.sector == ""
        assert stock.subindustry == ""

    def test_index_stocks_missing_optional_fields(self) -> None:
        """Test handling of constituent stocks with missing optional fields."""
        result = IndexStocksResponse.from_api_response(
            [
                {
                    "symbol": "TEST",
                }
            ],
            "^DJI",
        )
        assert len(result.stocks) == 1
        stock = result.stocks[0]
        assert stock.symbol == "TEST"
        assert stock.exchange == ""
        assert stock.company == ""
        assert stock.currency == ""

    def test_index_info_parsing(self) -> None:
        """Test IndexInfo model parsing."""
        result = IndexListResponse.from_api_response(
            [
                {"name": "Test Index", "symbol": "^TEST"},
            ]
        )
        assert result.count == 1
        assert result.indexes[0].name == "Test Index"
        assert result.indexes[0].symbol == "^TEST"


class TestCountryCurrencyEndpoint:
    """Tests for GET /country_currency endpoint."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_country_currency_returns_response(self) -> None:
        """Test that get_country_currency returns a CountryCurrencyResponse."""
        respx.get("https://api.gurufocus.com/public/user/test-token/country_currency").mock(
            return_value=Response(200, json=COUNTRY_CURRENCY_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.reference.get_country_currency()

        assert isinstance(result, CountryCurrencyResponse)
        assert result.count == 5
        assert len(result.currencies) == 5

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_country_currency_parses_data(self) -> None:
        """Test that country/currency data is parsed correctly."""
        respx.get("https://api.gurufocus.com/public/user/test-token/country_currency").mock(
            return_value=Response(200, json=COUNTRY_CURRENCY_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.reference.get_country_currency()

        # Find USA
        usa = next((c for c in result.currencies if c.country == "USA"), None)
        assert usa is not None
        assert usa.country_iso == "USA"
        assert usa.currency == "USD"

        # Find UK
        uk = next((c for c in result.currencies if c.country == "UK"), None)
        assert uk is not None
        assert uk.country_iso == "GBR"
        assert uk.currency == "GBP"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_country_currency_raw_returns_list(self) -> None:
        """Test that get_country_currency_raw returns raw list."""
        respx.get("https://api.gurufocus.com/public/user/test-token/country_currency").mock(
            return_value=Response(200, json=COUNTRY_CURRENCY_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.reference.get_country_currency_raw()

        assert isinstance(result, list)
        assert len(result) == 5


class TestFundaUpdatedEndpoint:
    """Tests for GET /funda_updated/{date} endpoint."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_funda_updated_returns_response(self) -> None:
        """Test that get_funda_updated returns a FundaUpdatedResponse."""
        respx.get("https://api.gurufocus.com/public/user/test-token/funda_updated/2025-01-15").mock(
            return_value=Response(200, json=FUNDA_UPDATED_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.reference.get_funda_updated("2025-01-15")

        assert isinstance(result, FundaUpdatedResponse)
        assert result.date == "2025-01-15"
        assert result.count == 3
        assert len(result.stocks) == 3

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_funda_updated_parses_stocks(self) -> None:
        """Test that stock data is parsed correctly."""
        respx.get("https://api.gurufocus.com/public/user/test-token/funda_updated/2025-01-15").mock(
            return_value=Response(200, json=FUNDA_UPDATED_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.reference.get_funda_updated("2025-01-15")

        first = result.stocks[0]
        assert first.symbol == "FAKEA"
        assert first.exchange == "NYSE"
        assert first.company == "FakeAlpha Corp"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_funda_updated_empty_result(self) -> None:
        """Test handling of empty result (no updates on date)."""
        respx.get("https://api.gurufocus.com/public/user/test-token/funda_updated/2025-01-01").mock(
            return_value=Response(200, json=[])
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.reference.get_funda_updated("2025-01-01")

        assert result.date == "2025-01-01"
        assert result.count == 0
        assert len(result.stocks) == 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_funda_updated_raw_returns_list(self) -> None:
        """Test that get_funda_updated_raw returns raw list."""
        respx.get("https://api.gurufocus.com/public/user/test-token/funda_updated/2025-01-15").mock(
            return_value=Response(200, json=FUNDA_UPDATED_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.reference.get_funda_updated_raw("2025-01-15")

        assert isinstance(result, list)
        assert len(result) == 3


class TestMiscReferenceModelsEdgeCases:
    """Test edge cases in misc reference model parsing."""

    def test_country_currency_empty_response(self) -> None:
        """Test handling of empty country/currency list."""
        result = CountryCurrencyResponse.from_api_response([])
        assert result.count == 0
        assert len(result.currencies) == 0

    def test_funda_updated_empty_response(self) -> None:
        """Test handling of empty fundamentals update list."""
        result = FundaUpdatedResponse.from_api_response([], "2025-01-01")
        assert result.date == "2025-01-01"
        assert result.count == 0
        assert len(result.stocks) == 0

    def test_funda_updated_missing_optional_fields(self) -> None:
        """Test handling of stock with missing optional fields."""
        result = FundaUpdatedResponse.from_api_response([{"symbol": "TEST"}], "2025-01-15")
        assert len(result.stocks) == 1
        stock = result.stocks[0]
        assert stock.symbol == "TEST"
        assert stock.exchange == ""
        assert stock.company == ""
