"""Tests for economic data endpoints (indicators and calendar)."""

import json
from pathlib import Path

import pytest
import respx
from httpx import Response

from gurufocus_api import GuruFocusClient
from gurufocus_api.models.economic import (
    CalendarResponse,
    EconomicIndicatorResponse,
    EconomicIndicatorsListResponse,
)

# Load test fixtures
FIXTURES_DIR = Path(__file__).parent / "data"


def load_fixture(category: str, filename: str) -> dict | list:
    """Load a JSON fixture file."""
    filepath = FIXTURES_DIR / category / filename
    with open(filepath) as f:
        return json.load(f)


# Pre-load fixtures
INDICATORS_LIST_DATA = load_fixture("economic_indicators", "list.json")
INDICATOR_ITEM_DATA = load_fixture("economic_indicator_item", "gdp.json")
CALENDAR_DATA = load_fixture("calendar", "events.json")


class TestEconomicIndicatorsListEndpoint:
    """Tests for GET /economicindicators endpoint."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_indicators_list_returns_response(self) -> None:
        """Test that get_indicators_list returns an EconomicIndicatorsListResponse."""
        respx.get("https://api.gurufocus.com/public/user/test-token/economicindicators").mock(
            return_value=Response(200, json=INDICATORS_LIST_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.economic.get_indicators_list()

        assert isinstance(result, EconomicIndicatorsListResponse)
        assert result.count == 5
        assert len(result.indicators) == 5

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_indicators_list_parses_data(self) -> None:
        """Test that indicator names are parsed correctly."""
        respx.get("https://api.gurufocus.com/public/user/test-token/economicindicators").mock(
            return_value=Response(200, json=INDICATORS_LIST_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.economic.get_indicators_list()

        assert "US GDP" in result.indicators
        assert "10 Year Treasury Yield" in result.indicators
        assert "S&P 500 Index" in result.indicators
        assert "Civilian Unemployment Rate" in result.indicators
        assert "Consumer Price Index" in result.indicators

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_indicators_list_raw_returns_list(self) -> None:
        """Test that get_indicators_list_raw returns raw list."""
        respx.get("https://api.gurufocus.com/public/user/test-token/economicindicators").mock(
            return_value=Response(200, json=INDICATORS_LIST_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.economic.get_indicators_list_raw()

        assert isinstance(result, list)
        assert len(result) == 5


class TestEconomicIndicatorItemEndpoint:
    """Tests for GET /economicindicators/item/{indicator} endpoint."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_indicator_returns_response(self) -> None:
        """Test that get_indicator returns an EconomicIndicatorResponse."""
        respx.get(
            "https://api.gurufocus.com/public/user/test-token/economicindicators/item/US%20GDP"
        ).mock(return_value=Response(200, json=INDICATOR_ITEM_DATA))

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.economic.get_indicator("US GDP")

        assert isinstance(result, EconomicIndicatorResponse)
        assert result.name == "Fake US GDP"
        assert result.unit == "Billions of Dollars"
        assert result.frequency == "Quarterly"
        assert result.source == "Fake Bureau of Economic Analysis"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_indicator_parses_time_series(self) -> None:
        """Test that time series data is parsed correctly."""
        respx.get(
            "https://api.gurufocus.com/public/user/test-token/economicindicators/item/US%20GDP"
        ).mock(return_value=Response(200, json=INDICATOR_ITEM_DATA))

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.economic.get_indicator("US GDP")

        assert len(result.data) == 5
        first = result.data[0]
        assert first.date == "2024-10-01"
        assert first.value == 28500.5

        last = result.data[-1]
        assert last.date == "2023-10-01"
        assert last.value == 27450.2

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_indicator_raw_returns_dict(self) -> None:
        """Test that get_indicator_raw returns raw dict."""
        respx.get(
            "https://api.gurufocus.com/public/user/test-token/economicindicators/item/US%20GDP"
        ).mock(return_value=Response(200, json=INDICATOR_ITEM_DATA))

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.economic.get_indicator_raw("US GDP")

        assert isinstance(result, dict)
        assert result["name"] == "Fake US GDP"
        assert "data" in result


class TestCalendarEndpoint:
    """Tests for GET /calendar endpoint."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_calendar_returns_response(self) -> None:
        """Test that get_calendar returns a CalendarResponse."""
        respx.get(
            "https://api.gurufocus.com/public/user/test-token/calendar",
            params={"date": "2025-01-10"},
        ).mock(return_value=Response(200, json=CALENDAR_DATA))

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.economic.get_calendar("2025-01-10")

        assert isinstance(result, CalendarResponse)
        assert len(result.economic) == 1
        assert len(result.ipo) == 1
        assert len(result.earning) == 1
        assert len(result.dividend) == 1
        assert len(result.split) == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_calendar_parses_economic_events(self) -> None:
        """Test that economic events are parsed correctly."""
        respx.get(
            "https://api.gurufocus.com/public/user/test-token/calendar",
            params={"date": "2025-01-10"},
        ).mock(return_value=Response(200, json=CALENDAR_DATA))

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.economic.get_calendar("2025-01-10")

        event = result.economic[0]
        assert event.date == "2025-01-10"
        assert event.event == "Fake Employment Report"
        assert event.actual == "215K"
        assert event.forecast == "200K"
        assert event.previous == "195K"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_calendar_parses_ipo_events(self) -> None:
        """Test that IPO events are parsed correctly."""
        respx.get(
            "https://api.gurufocus.com/public/user/test-token/calendar",
            params={"date": "2025-01-10"},
        ).mock(return_value=Response(200, json=CALENDAR_DATA))

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.economic.get_calendar("2025-01-10")

        ipo = result.ipo[0]
        assert ipo.symbol == "FAKE"
        assert ipo.company == "FakeCorp Inc"
        assert ipo.exchange == "NAS"
        assert ipo.date == "2025-01-15"
        assert ipo.price_range == "$18-$22"
        assert ipo.shares == "10M"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_calendar_parses_earnings_events(self) -> None:
        """Test that earnings events are parsed correctly."""
        respx.get(
            "https://api.gurufocus.com/public/user/test-token/calendar",
            params={"date": "2025-01-10"},
        ).mock(return_value=Response(200, json=CALENDAR_DATA))

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.economic.get_calendar("2025-01-10")

        earning = result.earning[0]
        assert earning.symbol == "AAPL"
        assert earning.company == "Fake Apple Inc"
        assert earning.exchange == "NAS"
        assert earning.date == "2025-01-30"
        assert earning.time == "after_market"
        assert earning.eps_estimate == "2.35"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_calendar_parses_dividend_events(self) -> None:
        """Test that dividend events are parsed correctly."""
        respx.get(
            "https://api.gurufocus.com/public/user/test-token/calendar",
            params={"date": "2025-01-10"},
        ).mock(return_value=Response(200, json=CALENDAR_DATA))

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.economic.get_calendar("2025-01-10")

        dividend = result.dividend[0]
        assert dividend.symbol == "MSFT"
        assert dividend.company == "Fake Microsoft Corp"
        assert dividend.exchange == "NAS"
        assert dividend.declaration_date == "2024-12-15"
        assert dividend.ex_date == "2025-01-10"
        assert dividend.record_date == "2025-01-11"
        assert dividend.pay_date == "2025-01-25"
        assert dividend.cash_amount == "0.83"
        assert dividend.currency == "USD"
        assert dividend.dividend_type == "CD"
        assert dividend.frequency == 4
        assert dividend.dividend_yield == "0.72"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_calendar_parses_split_events(self) -> None:
        """Test that split events are parsed correctly."""
        respx.get(
            "https://api.gurufocus.com/public/user/test-token/calendar",
            params={"date": "2025-01-10"},
        ).mock(return_value=Response(200, json=CALENDAR_DATA))

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.economic.get_calendar("2025-01-10")

        split = result.split[0]
        assert split.symbol == "NVDA"
        assert split.company == "Fake NVIDIA Corp"
        assert split.exchange == "NAS"
        assert split.date == "2025-02-01"
        assert split.ratio == "4:1"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_calendar_with_event_type_filter(self) -> None:
        """Test that event_type parameter filters results."""
        respx.get(
            "https://api.gurufocus.com/public/user/test-token/calendar",
            params={"date": "2025-01-10", "type": "earning"},
        ).mock(return_value=Response(200, json=CALENDAR_DATA))

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.economic.get_calendar("2025-01-10", event_type="earning")

        assert isinstance(result, CalendarResponse)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_calendar_raw_returns_dict(self) -> None:
        """Test that get_calendar_raw returns raw dict."""
        respx.get(
            "https://api.gurufocus.com/public/user/test-token/calendar",
            params={"date": "2025-01-10"},
        ).mock(return_value=Response(200, json=CALENDAR_DATA))

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.economic.get_calendar_raw("2025-01-10")

        assert isinstance(result, dict)
        assert "economic" in result
        assert "ipo" in result
        assert "earning" in result
        assert "dividend" in result
        assert "split" in result


class TestEconomicModelsEdgeCases:
    """Test edge cases in economic model parsing."""

    def test_indicators_list_empty_response(self) -> None:
        """Test handling of empty indicators list."""
        result = EconomicIndicatorsListResponse.from_api_response([])
        assert result.count == 0
        assert len(result.indicators) == 0

    def test_indicator_empty_data(self) -> None:
        """Test handling of indicator with no data points."""
        result = EconomicIndicatorResponse.from_api_response(
            {"name": "Test", "unit": "Test Unit", "frequency": "Monthly", "source": "Test Source"}
        )
        assert result.name == "Test"
        assert len(result.data) == 0

    def test_indicator_missing_optional_fields(self) -> None:
        """Test handling of indicator with missing optional fields."""
        result = EconomicIndicatorResponse.from_api_response(
            {"name": "Test", "data": [{"date": "2024-01-01", "value": 100.0}]}
        )
        assert result.name == "Test"
        assert result.unit == ""
        assert result.frequency == ""
        assert result.source == ""
        assert len(result.data) == 1

    def test_calendar_empty_response(self) -> None:
        """Test handling of empty calendar response."""
        result = CalendarResponse.from_api_response({})
        assert len(result.economic) == 0
        assert len(result.ipo) == 0
        assert len(result.earning) == 0
        assert len(result.dividend) == 0
        assert len(result.split) == 0

    def test_calendar_partial_response(self) -> None:
        """Test handling of calendar with only some event types."""
        result = CalendarResponse.from_api_response(
            {
                "economic": [{"date": "2025-01-01", "event": "Test Event"}],
                "ipo": [],
            }
        )
        assert len(result.economic) == 1
        assert len(result.ipo) == 0
        assert len(result.earning) == 0

    def test_economic_event_missing_forecast(self) -> None:
        """Test economic event with missing forecast values."""
        result = CalendarResponse.from_api_response(
            {"economic": [{"date": "2025-01-01", "event": "Test Event", "actual": "100"}]}
        )
        event = result.economic[0]
        assert event.actual == "100"
        assert event.forecast is None
        assert event.previous is None

    def test_dividend_event_default_currency(self) -> None:
        """Test dividend event uses USD as default currency."""
        result = CalendarResponse.from_api_response(
            {"dividend": [{"symbol": "TEST", "company": "Test Corp"}]}
        )
        dividend = result.dividend[0]
        assert dividend.currency == "USD"
