"""Tests for additional stock endpoints (estimates, dividends, price history, insider trades).

Note: Model parsing with real API responses is tested in test_models_with_fixtures.py.
These tests focus on endpoint behavior.
"""

import json
import tempfile
from pathlib import Path

import pytest
import respx
from httpx import Response

from gurufocus_api import (
    AnalystEstimates,
    CurrentDividend,
    DividendHistory,
    EstimateHistoryResponse,
    ExecutiveList,
    GuruFocusClient,
    GuruTradesHistory,
    IndicatorsList,
    IndicatorTimeSeries,
    InsiderTrades,
    NewsFeedResponse,
    OHLCHistory,
    OperatingData,
    OwnershipHistory,
    PriceHistory,
    SegmentData,
    StockGurusResponse,
    StockOwnership,
    StockQuote,
    UnadjustedPriceHistory,
    VolumeHistory,
)

# Load sample responses from fixtures
FIXTURES_DIR = Path(__file__).parent / "data"


def load_fixture(category: str, symbol: str = "FAKE1") -> dict | list:
    """Load a fixture file."""
    path = FIXTURES_DIR / category / f"{symbol}.json"
    with open(path) as f:
        return json.load(f)


SAMPLE_ESTIMATES_RESPONSE = load_fixture("analyst_estimate")
SAMPLE_DIVIDENDS_RESPONSE = load_fixture("dividend")
SAMPLE_PRICE_RESPONSE = load_fixture("price")
SAMPLE_INSIDERS_RESPONSE = load_fixture("insider")
SAMPLE_GURUS_RESPONSE = load_fixture("gurus")
SAMPLE_EXECUTIVES_RESPONSE = load_fixture("executives")
SAMPLE_TRADES_HISTORY_RESPONSE = load_fixture("trades_history")
SAMPLE_QUOTE_RESPONSE = load_fixture("quote")
SAMPLE_CURRENT_DIVIDEND_RESPONSE = load_fixture("current_dividend")
SAMPLE_PRICE_OHLC_RESPONSE = load_fixture("price_ohlc")
SAMPLE_VOLUME_RESPONSE = load_fixture("volume")
SAMPLE_UNADJUSTED_PRICE_RESPONSE = load_fixture("unadjusted_price")
SAMPLE_OPERATING_DATA_RESPONSE = load_fixture("operating_data")
SAMPLE_SEGMENTS_DATA_RESPONSE = load_fixture("segments_data")
SAMPLE_OWNERSHIP_RESPONSE = load_fixture("ownership")
SAMPLE_INDICATOR_HISTORY_RESPONSE = load_fixture("indicator_history")


def load_indicators_list() -> list:
    """Load indicators list fixture."""
    path = FIXTURES_DIR / "indicators" / "list.json"
    with open(path) as f:
        return json.load(f)


def load_indicator_fixture(symbol: str, indicator: str) -> list:
    """Load indicator fixture."""
    path = FIXTURES_DIR / "indicator" / f"{symbol}_{indicator}.json"
    with open(path) as f:
        return json.load(f)


SAMPLE_INDICATORS_LIST_RESPONSE = load_indicators_list()
SAMPLE_INDICATOR_NET_INCOME_RESPONSE = load_indicator_fixture("FAKE1", "net_income")


def load_news_feed_fixture() -> list:
    """Load news feed fixture."""
    path = FIXTURES_DIR / "news_feed" / "latest.json"
    with open(path) as f:
        return json.load(f)


def load_estimate_history_fixture(symbol: str) -> dict:
    """Load estimate history fixture."""
    path = FIXTURES_DIR / "estimate_history" / f"{symbol}.json"
    with open(path) as f:
        return json.load(f)


SAMPLE_NEWS_FEED_RESPONSE = load_news_feed_fixture()
SAMPLE_ESTIMATE_HISTORY_RESPONSE = load_estimate_history_fixture("AAPL")


class TestQuoteEndpoint:
    """Tests for quote endpoint."""

    @pytest.fixture
    def cache_dir(self) -> Path:
        """Create a temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_quote(self, cache_dir: Path) -> None:
        """Test fetching quote returns typed model."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/quote").mock(
            return_value=Response(200, json=SAMPLE_QUOTE_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            quote = await client.stocks.get_quote("FAKE1")

            assert isinstance(quote, StockQuote)
            assert quote.symbol == "FAKE1"
            assert quote.current_price is not None
            assert quote.current_price > 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_quote_cached(self, cache_dir: Path) -> None:
        """Test that quote is cached."""
        api_token = "test-token"
        route = respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/quote"
        ).mock(return_value=Response(200, json=SAMPLE_QUOTE_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            await client.stocks.get_quote("FAKE1")
            await client.stocks.get_quote("FAKE1")
            assert route.call_count == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_quote_raw(self, cache_dir: Path) -> None:
        """Test fetching raw quote data."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/quote").mock(
            return_value=Response(200, json=SAMPLE_QUOTE_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            raw = await client.stocks.get_quote_raw("FAKE1")
            assert isinstance(raw, dict)
            assert "Current Price" in raw or "Price" in raw

    @pytest.mark.asyncio
    @respx.mock
    async def test_quote_ohlv_data(self, cache_dir: Path) -> None:
        """Test that quote contains OHLV data."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/quote").mock(
            return_value=Response(200, json=SAMPLE_QUOTE_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            quote = await client.stocks.get_quote("FAKE1")

            assert quote.open is not None
            assert quote.high is not None
            assert quote.low is not None
            assert quote.volume is not None
            assert quote.volume > 0


class TestAnalystEstimatesEndpoint:
    """Tests for analyst estimates endpoint."""

    @pytest.fixture
    def cache_dir(self) -> Path:
        """Create a temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_analyst_estimates(self, cache_dir: Path) -> None:
        """Test fetching analyst estimates returns typed model."""
        api_token = "test-token"
        respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/analyst_estimate"
        ).mock(return_value=Response(200, json=SAMPLE_ESTIMATES_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            estimates = await client.stocks.get_analyst_estimates("FAKE1")

            assert isinstance(estimates, AnalystEstimates)
            assert estimates.symbol == "FAKE1"
            # Annual estimates should be parsed from column-oriented data
            assert len(estimates.annual_estimates) > 0
            # First annual estimate should have revenue
            assert estimates.annual_estimates[0].revenue_estimate is not None

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_analyst_estimates_cached(self, cache_dir: Path) -> None:
        """Test that estimates are cached."""
        api_token = "test-token"
        route = respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/analyst_estimate"
        ).mock(return_value=Response(200, json=SAMPLE_ESTIMATES_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            await client.stocks.get_analyst_estimates("FAKE1")
            await client.stocks.get_analyst_estimates("FAKE1")
            assert route.call_count == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_analyst_estimates_raw(self, cache_dir: Path) -> None:
        """Test fetching raw estimates data."""
        api_token = "test-token"
        respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/analyst_estimate"
        ).mock(return_value=Response(200, json=SAMPLE_ESTIMATES_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            raw = await client.stocks.get_analyst_estimates_raw("FAKE1")
            assert isinstance(raw, dict)
            # Real API returns annual/quarterly at top level
            assert "annual" in raw or "quarterly" in raw


class TestDividendsEndpoint:
    """Tests for dividends endpoint."""

    @pytest.fixture
    def cache_dir(self) -> Path:
        """Create a temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_dividends(self, cache_dir: Path) -> None:
        """Test fetching dividends returns typed model."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/dividend").mock(
            return_value=Response(200, json=SAMPLE_DIVIDENDS_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            dividends = await client.stocks.get_dividends("FAKE1")

            assert isinstance(dividends, DividendHistory)
            assert dividends.symbol == "FAKE1"
            # Real API returns array of dividend objects directly
            assert len(dividends.payments) > 0
            # First payment should have amount
            assert dividends.payments[0].amount is not None

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_dividends_cached(self, cache_dir: Path) -> None:
        """Test that dividends are cached."""
        api_token = "test-token"
        route = respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/dividend"
        ).mock(return_value=Response(200, json=SAMPLE_DIVIDENDS_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            await client.stocks.get_dividends("FAKE1")
            await client.stocks.get_dividends("FAKE1")
            assert route.call_count == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_dividends_raw(self, cache_dir: Path) -> None:
        """Test fetching raw dividend data."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/dividend").mock(
            return_value=Response(200, json=SAMPLE_DIVIDENDS_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            raw = await client.stocks.get_dividends_raw("FAKE1")
            # Real API returns array directly
            assert isinstance(raw, list)


class TestCurrentDividendEndpoint:
    """Tests for current dividend endpoint."""

    @pytest.fixture
    def cache_dir(self) -> Path:
        """Create a temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_current_dividend(self, cache_dir: Path) -> None:
        """Test fetching current dividend returns typed model."""
        api_token = "test-token"
        respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/current_dividend"
        ).mock(return_value=Response(200, json=SAMPLE_CURRENT_DIVIDEND_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            current_div = await client.stocks.get_current_dividend("FAKE1")

            assert isinstance(current_div, CurrentDividend)
            assert current_div.symbol == "FAKE1"
            assert current_div.dividend_yield is not None
            assert current_div.dividend_yield > 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_current_dividend_cached(self, cache_dir: Path) -> None:
        """Test that current dividend is cached."""
        api_token = "test-token"
        route = respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/current_dividend"
        ).mock(return_value=Response(200, json=SAMPLE_CURRENT_DIVIDEND_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            await client.stocks.get_current_dividend("FAKE1")
            await client.stocks.get_current_dividend("FAKE1")
            assert route.call_count == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_current_dividend_raw(self, cache_dir: Path) -> None:
        """Test fetching raw current dividend data."""
        api_token = "test-token"
        respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/current_dividend"
        ).mock(return_value=Response(200, json=SAMPLE_CURRENT_DIVIDEND_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            raw = await client.stocks.get_current_dividend_raw("FAKE1")
            assert isinstance(raw, dict)
            assert "Dividend Yield %" in raw

    @pytest.mark.asyncio
    @respx.mock
    async def test_current_dividend_details(self, cache_dir: Path) -> None:
        """Test that current dividend contains expected details."""
        api_token = "test-token"
        respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/current_dividend"
        ).mock(return_value=Response(200, json=SAMPLE_CURRENT_DIVIDEND_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            current_div = await client.stocks.get_current_dividend("FAKE1")

            assert current_div.dividends_per_share_ttm is not None
            assert current_div.frequency is not None
            assert current_div.next_payment_date is not None


class TestPriceHistoryEndpoint:
    """Tests for price history endpoint."""

    @pytest.fixture
    def cache_dir(self) -> Path:
        """Create a temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_price_history(self, cache_dir: Path) -> None:
        """Test fetching price history returns typed model."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/price").mock(
            return_value=Response(200, json=SAMPLE_PRICE_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            prices = await client.stocks.get_price_history("FAKE1")

            assert isinstance(prices, PriceHistory)
            assert prices.symbol == "FAKE1"
            # Real API returns array of [date, price] tuples
            assert len(prices.prices) > 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_price_history_cached(self, cache_dir: Path) -> None:
        """Test that price history is cached."""
        api_token = "test-token"
        route = respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/price"
        ).mock(return_value=Response(200, json=SAMPLE_PRICE_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            await client.stocks.get_price_history("FAKE1")
            await client.stocks.get_price_history("FAKE1")
            assert route.call_count == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_price_history_raw(self, cache_dir: Path) -> None:
        """Test fetching raw price data."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/price").mock(
            return_value=Response(200, json=SAMPLE_PRICE_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            raw = await client.stocks.get_price_history_raw("FAKE1")
            # Real API returns array of [date, price] tuples
            assert isinstance(raw, list)

    @pytest.mark.asyncio
    @respx.mock
    async def test_price_point_data(self, cache_dir: Path) -> None:
        """Test that price points contain date and price."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/price").mock(
            return_value=Response(200, json=SAMPLE_PRICE_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            prices = await client.stocks.get_price_history("FAKE1")

            point = prices.prices[0]
            # Date should be converted to YYYY-MM-DD format
            assert point.date is not None
            assert point.price is not None


class TestInsiderTradesEndpoint:
    """Tests for insider trades endpoint."""

    @pytest.fixture
    def cache_dir(self) -> Path:
        """Create a temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_insider_trades(self, cache_dir: Path) -> None:
        """Test fetching insider trades returns typed model."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/insider").mock(
            return_value=Response(200, json=SAMPLE_INSIDERS_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            insiders = await client.stocks.get_insider_trades("FAKE1")

            assert isinstance(insiders, InsiderTrades)
            assert insiders.symbol == "FAKE1"
            # Real API returns {symbol: [trades]}
            assert len(insiders.trades) > 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_insider_trades_cached(self, cache_dir: Path) -> None:
        """Test that insider trades are cached."""
        api_token = "test-token"
        route = respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/insider"
        ).mock(return_value=Response(200, json=SAMPLE_INSIDERS_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            await client.stocks.get_insider_trades("FAKE1")
            await client.stocks.get_insider_trades("FAKE1")
            assert route.call_count == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_insider_trades_raw(self, cache_dir: Path) -> None:
        """Test fetching raw insider trades data."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/insider").mock(
            return_value=Response(200, json=SAMPLE_INSIDERS_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            raw = await client.stocks.get_insider_trades_raw("FAKE1")
            assert isinstance(raw, dict)
            # Real API returns {symbol: [trades]}
            assert "FAKE1" in raw

    @pytest.mark.asyncio
    @respx.mock
    async def test_insider_trade_details(self, cache_dir: Path) -> None:
        """Test that individual trades contain expected details."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/insider").mock(
            return_value=Response(200, json=SAMPLE_INSIDERS_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            insiders = await client.stocks.get_insider_trades("FAKE1")

            trade = insiders.trades[0]
            # Real API has: insider, position, date, type, trans_share, price
            assert trade.insider_name is not None
            assert trade.insider_title is not None
            assert trade.trade_date is not None


class TestModelsEdgeCases:
    """Tests for edge cases in model parsing."""

    def test_quote_empty_response(self) -> None:
        """Test parsing empty quote response."""
        quote = StockQuote.from_api_response({}, "TEST")
        assert quote.symbol == "TEST"
        assert quote.current_price is None

    def test_estimates_empty_response(self) -> None:
        """Test parsing empty estimates response."""
        estimates = AnalystEstimates.from_api_response({}, "TEST")
        assert estimates.symbol == "TEST"
        assert len(estimates.annual_estimates) == 0

    def test_dividends_empty_response(self) -> None:
        """Test parsing empty dividends response."""
        dividends = DividendHistory.from_api_response([], "TEST")
        assert dividends.symbol == "TEST"
        assert len(dividends.payments) == 0

    def test_current_dividend_empty_response(self) -> None:
        """Test parsing empty current dividend response."""
        current_div = CurrentDividend.from_api_response({}, "TEST")
        assert current_div.symbol == "TEST"
        assert current_div.dividend_yield is None

    def test_price_history_empty_response(self) -> None:
        """Test parsing empty price history response."""
        prices = PriceHistory.from_api_response([], "TEST")
        assert prices.symbol == "TEST"
        assert len(prices.prices) == 0

    def test_insider_trades_empty_response(self) -> None:
        """Test parsing empty insider trades response."""
        insiders = InsiderTrades.from_api_response({}, "TEST")
        assert insiders.symbol == "TEST"
        assert len(insiders.trades) == 0

    def test_gurus_empty_response(self) -> None:
        """Test parsing empty gurus response."""
        gurus = StockGurusResponse.from_api_response({}, "TEST")
        assert gurus.symbol == "TEST"
        assert len(gurus.picks) == 0
        assert len(gurus.holdings) == 0

    def test_executives_empty_response(self) -> None:
        """Test parsing empty executives response."""
        execs = ExecutiveList.from_api_response([], "TEST")
        assert execs.symbol == "TEST"
        assert len(execs.executives) == 0

    def test_trades_history_empty_response(self) -> None:
        """Test parsing empty trades history response."""
        trades = GuruTradesHistory.from_api_response([], "TEST")
        assert trades.symbol == "TEST"
        assert len(trades.periods) == 0


class TestGurusEndpoint:
    """Tests for gurus endpoint."""

    @pytest.fixture
    def cache_dir(self) -> Path:
        """Create a temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_gurus(self, cache_dir: Path) -> None:
        """Test fetching gurus returns typed model."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/gurus").mock(
            return_value=Response(200, json=SAMPLE_GURUS_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            gurus = await client.stocks.get_gurus("FAKE1")

            assert isinstance(gurus, StockGurusResponse)
            assert gurus.symbol == "FAKE1"
            # Response should have picks and holdings
            assert len(gurus.picks) > 0
            assert len(gurus.holdings) > 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_gurus_cached(self, cache_dir: Path) -> None:
        """Test that gurus are cached."""
        api_token = "test-token"
        route = respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/gurus"
        ).mock(return_value=Response(200, json=SAMPLE_GURUS_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            await client.stocks.get_gurus("FAKE1")
            await client.stocks.get_gurus("FAKE1")
            assert route.call_count == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_gurus_raw(self, cache_dir: Path) -> None:
        """Test fetching raw gurus data."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/gurus").mock(
            return_value=Response(200, json=SAMPLE_GURUS_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            raw = await client.stocks.get_gurus_raw("FAKE1")
            assert isinstance(raw, dict)
            # API returns {symbol: {picks: [], holdings: []}}
            assert "FAKE1" in raw

    @pytest.mark.asyncio
    @respx.mock
    async def test_guru_pick_details(self, cache_dir: Path) -> None:
        """Test that individual picks contain expected details."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/gurus").mock(
            return_value=Response(200, json=SAMPLE_GURUS_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            gurus = await client.stocks.get_gurus("FAKE1")

            pick = gurus.picks[0]
            assert pick.guru is not None
            assert pick.action is not None
            assert pick.date is not None

    @pytest.mark.asyncio
    @respx.mock
    async def test_guru_holding_details(self, cache_dir: Path) -> None:
        """Test that individual holdings contain expected details."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/gurus").mock(
            return_value=Response(200, json=SAMPLE_GURUS_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            gurus = await client.stocks.get_gurus("FAKE1")

            holding = gurus.holdings[0]
            assert holding.guru is not None
            assert holding.current_shares is not None
            assert holding.perc_assets is not None


class TestExecutivesEndpoint:
    """Tests for executives endpoint."""

    @pytest.fixture
    def cache_dir(self) -> Path:
        """Create a temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_executives(self, cache_dir: Path) -> None:
        """Test fetching executives returns typed model."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/executives").mock(
            return_value=Response(200, json=SAMPLE_EXECUTIVES_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            execs = await client.stocks.get_executives("FAKE1")

            assert isinstance(execs, ExecutiveList)
            assert execs.symbol == "FAKE1"
            assert len(execs.executives) > 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_executives_cached(self, cache_dir: Path) -> None:
        """Test that executives are cached."""
        api_token = "test-token"
        route = respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/executives"
        ).mock(return_value=Response(200, json=SAMPLE_EXECUTIVES_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            await client.stocks.get_executives("FAKE1")
            await client.stocks.get_executives("FAKE1")
            assert route.call_count == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_executives_raw(self, cache_dir: Path) -> None:
        """Test fetching raw executives data."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/executives").mock(
            return_value=Response(200, json=SAMPLE_EXECUTIVES_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            raw = await client.stocks.get_executives_raw("FAKE1")
            # API returns array directly
            assert isinstance(raw, list)

    @pytest.mark.asyncio
    @respx.mock
    async def test_executive_details(self, cache_dir: Path) -> None:
        """Test that individual executives contain expected details."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/executives").mock(
            return_value=Response(200, json=SAMPLE_EXECUTIVES_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            execs = await client.stocks.get_executives("FAKE1")

            exec = execs.executives[0]
            assert exec.name is not None
            assert exec.position is not None
            assert exec.transaction_date is not None


class TestTradesHistoryEndpoint:
    """Tests for trades history endpoint."""

    @pytest.fixture
    def cache_dir(self) -> Path:
        """Create a temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_trades_history(self, cache_dir: Path) -> None:
        """Test fetching trades history returns typed model."""
        api_token = "test-token"
        respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/trades/history"
        ).mock(return_value=Response(200, json=SAMPLE_TRADES_HISTORY_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            trades = await client.stocks.get_trades_history("FAKE1")

            assert isinstance(trades, GuruTradesHistory)
            assert trades.symbol == "FAKE1"
            assert len(trades.periods) > 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_trades_history_cached(self, cache_dir: Path) -> None:
        """Test that trades history is cached."""
        api_token = "test-token"
        route = respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/trades/history"
        ).mock(return_value=Response(200, json=SAMPLE_TRADES_HISTORY_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            await client.stocks.get_trades_history("FAKE1")
            await client.stocks.get_trades_history("FAKE1")
            assert route.call_count == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_trades_history_raw(self, cache_dir: Path) -> None:
        """Test fetching raw trades history data."""
        api_token = "test-token"
        respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/trades/history"
        ).mock(return_value=Response(200, json=SAMPLE_TRADES_HISTORY_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            raw = await client.stocks.get_trades_history_raw("FAKE1")
            # API returns array directly
            assert isinstance(raw, list)

    @pytest.mark.asyncio
    @respx.mock
    async def test_trades_history_period_details(self, cache_dir: Path) -> None:
        """Test that individual periods contain expected details."""
        api_token = "test-token"
        respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/trades/history"
        ).mock(return_value=Response(200, json=SAMPLE_TRADES_HISTORY_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            trades = await client.stocks.get_trades_history("FAKE1")

            period = trades.periods[0]
            assert period.symbol is not None
            assert period.portdate is not None
            assert period.buy_count >= 0
            assert period.sell_count >= 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_trades_history_guru_actions(self, cache_dir: Path) -> None:
        """Test that guru buy/sell actions are parsed correctly."""
        api_token = "test-token"
        respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/trades/history"
        ).mock(return_value=Response(200, json=SAMPLE_TRADES_HISTORY_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            trades = await client.stocks.get_trades_history("FAKE1")

            # First period should have buy_gurus
            period = trades.periods[0]
            assert len(period.buy_gurus) > 0
            buyer = period.buy_gurus[0]
            assert buyer.guru_id > 0
            assert buyer.guru_name is not None
            assert buyer.share_change > 0  # Positive for buys


class TestPriceOHLCEndpoint:
    """Tests for OHLC price endpoint."""

    @pytest.fixture
    def cache_dir(self) -> Path:
        """Create a temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_price_ohlc(self, cache_dir: Path) -> None:
        """Test fetching OHLC price returns typed model."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/price_ohlc").mock(
            return_value=Response(200, json=SAMPLE_PRICE_OHLC_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            ohlc = await client.stocks.get_price_ohlc("FAKE1")

            assert isinstance(ohlc, OHLCHistory)
            assert ohlc.symbol == "FAKE1"
            assert len(ohlc.bars) > 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_price_ohlc_with_dates(self, cache_dir: Path) -> None:
        """Test fetching OHLC with date parameters."""
        api_token = "test-token"
        route = respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/price_ohlc",
            params={"start_date": "20250101", "end_date": "20250131"},
        ).mock(return_value=Response(200, json=SAMPLE_PRICE_OHLC_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            ohlc = await client.stocks.get_price_ohlc(
                "FAKE1", start_date="20250101", end_date="20250131"
            )
            assert isinstance(ohlc, OHLCHistory)
            assert route.called

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_price_ohlc_cached(self, cache_dir: Path) -> None:
        """Test that OHLC is cached."""
        api_token = "test-token"
        route = respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/price_ohlc"
        ).mock(return_value=Response(200, json=SAMPLE_PRICE_OHLC_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            await client.stocks.get_price_ohlc("FAKE1")
            await client.stocks.get_price_ohlc("FAKE1")
            assert route.call_count == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_price_ohlc_raw(self, cache_dir: Path) -> None:
        """Test fetching raw OHLC data."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/price_ohlc").mock(
            return_value=Response(200, json=SAMPLE_PRICE_OHLC_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            raw = await client.stocks.get_price_ohlc_raw("FAKE1")
            assert isinstance(raw, list)

    @pytest.mark.asyncio
    @respx.mock
    async def test_ohlc_bar_details(self, cache_dir: Path) -> None:
        """Test that OHLC bars contain expected details."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/price_ohlc").mock(
            return_value=Response(200, json=SAMPLE_PRICE_OHLC_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            ohlc = await client.stocks.get_price_ohlc("FAKE1")

            bar = ohlc.bars[0]
            assert bar.date is not None
            assert bar.open is not None
            assert bar.high is not None
            assert bar.low is not None
            assert bar.close is not None
            assert bar.volume is not None


class TestVolumeEndpoint:
    """Tests for volume endpoint."""

    @pytest.fixture
    def cache_dir(self) -> Path:
        """Create a temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_volume(self, cache_dir: Path) -> None:
        """Test fetching volume returns typed model."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/volume").mock(
            return_value=Response(200, json=SAMPLE_VOLUME_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            volume = await client.stocks.get_volume("FAKE1")

            assert isinstance(volume, VolumeHistory)
            assert volume.symbol == "FAKE1"
            assert len(volume.data) > 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_volume_with_dates(self, cache_dir: Path) -> None:
        """Test fetching volume with date parameters."""
        api_token = "test-token"
        route = respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/volume",
            params={"start_date": "20250101", "end_date": "20250131"},
        ).mock(return_value=Response(200, json=SAMPLE_VOLUME_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            volume = await client.stocks.get_volume(
                "FAKE1", start_date="20250101", end_date="20250131"
            )
            assert isinstance(volume, VolumeHistory)
            assert route.called

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_volume_cached(self, cache_dir: Path) -> None:
        """Test that volume is cached."""
        api_token = "test-token"
        route = respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/volume"
        ).mock(return_value=Response(200, json=SAMPLE_VOLUME_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            await client.stocks.get_volume("FAKE1")
            await client.stocks.get_volume("FAKE1")
            assert route.call_count == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_volume_raw(self, cache_dir: Path) -> None:
        """Test fetching raw volume data."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/volume").mock(
            return_value=Response(200, json=SAMPLE_VOLUME_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            raw = await client.stocks.get_volume_raw("FAKE1")
            assert isinstance(raw, list)

    @pytest.mark.asyncio
    @respx.mock
    async def test_volume_point_details(self, cache_dir: Path) -> None:
        """Test that volume points contain expected details."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/volume").mock(
            return_value=Response(200, json=SAMPLE_VOLUME_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            volume = await client.stocks.get_volume("FAKE1")

            point = volume.data[0]
            assert point.date is not None
            assert point.volume > 0


class TestUnadjustedPriceEndpoint:
    """Tests for unadjusted price endpoint."""

    @pytest.fixture
    def cache_dir(self) -> Path:
        """Create a temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_unadjusted_price(self, cache_dir: Path) -> None:
        """Test fetching unadjusted price returns typed model."""
        api_token = "test-token"
        respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/unadjusted_price"
        ).mock(return_value=Response(200, json=SAMPLE_UNADJUSTED_PRICE_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            prices = await client.stocks.get_unadjusted_price("FAKE1")

            assert isinstance(prices, UnadjustedPriceHistory)
            assert prices.symbol == "FAKE1"
            assert len(prices.prices) > 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_unadjusted_price_with_dates(self, cache_dir: Path) -> None:
        """Test fetching unadjusted price with date parameters."""
        api_token = "test-token"
        route = respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/unadjusted_price",
            params={"start_date": "20250101", "end_date": "20250131"},
        ).mock(return_value=Response(200, json=SAMPLE_UNADJUSTED_PRICE_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            prices = await client.stocks.get_unadjusted_price(
                "FAKE1", start_date="20250101", end_date="20250131"
            )
            assert isinstance(prices, UnadjustedPriceHistory)
            assert route.called

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_unadjusted_price_cached(self, cache_dir: Path) -> None:
        """Test that unadjusted price is cached."""
        api_token = "test-token"
        route = respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/unadjusted_price"
        ).mock(return_value=Response(200, json=SAMPLE_UNADJUSTED_PRICE_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            await client.stocks.get_unadjusted_price("FAKE1")
            await client.stocks.get_unadjusted_price("FAKE1")
            assert route.call_count == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_unadjusted_price_raw(self, cache_dir: Path) -> None:
        """Test fetching raw unadjusted price data."""
        api_token = "test-token"
        respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/unadjusted_price"
        ).mock(return_value=Response(200, json=SAMPLE_UNADJUSTED_PRICE_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            raw = await client.stocks.get_unadjusted_price_raw("FAKE1")
            assert isinstance(raw, list)

    @pytest.mark.asyncio
    @respx.mock
    async def test_unadjusted_price_point_details(self, cache_dir: Path) -> None:
        """Test that unadjusted price points contain expected details."""
        api_token = "test-token"
        respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/unadjusted_price"
        ).mock(return_value=Response(200, json=SAMPLE_UNADJUSTED_PRICE_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            prices = await client.stocks.get_unadjusted_price("FAKE1")

            point = prices.prices[0]
            assert point.date is not None
            assert point.price > 0


class TestOHLCModelsEdgeCases:
    """Tests for edge cases in OHLC model parsing."""

    def test_ohlc_history_empty_response(self) -> None:
        """Test parsing empty OHLC response."""
        ohlc = OHLCHistory.from_api_response([], "TEST")
        assert ohlc.symbol == "TEST"
        assert len(ohlc.bars) == 0

    def test_volume_history_empty_response(self) -> None:
        """Test parsing empty volume response."""
        volume = VolumeHistory.from_api_response([], "TEST")
        assert volume.symbol == "TEST"
        assert len(volume.data) == 0

    def test_unadjusted_price_history_empty_response(self) -> None:
        """Test parsing empty unadjusted price response."""
        prices = UnadjustedPriceHistory.from_api_response([], "TEST")
        assert prices.symbol == "TEST"
        assert len(prices.prices) == 0


class TestOperatingDataEndpoint:
    """Tests for operating data endpoint."""

    @pytest.fixture
    def cache_dir(self) -> Path:
        """Create a temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_operating_data(self, cache_dir: Path) -> None:
        """Test fetching operating data returns typed model."""
        api_token = "test-token"
        respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/operating_data"
        ).mock(return_value=Response(200, json=SAMPLE_OPERATING_DATA_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            ops = await client.stocks.get_operating_data("FAKE1")

            assert isinstance(ops, OperatingData)
            assert ops.symbol == "FAKE1"
            assert len(ops.metrics) > 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_operating_data_cached(self, cache_dir: Path) -> None:
        """Test that operating data is cached."""
        api_token = "test-token"
        route = respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/operating_data"
        ).mock(return_value=Response(200, json=SAMPLE_OPERATING_DATA_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            await client.stocks.get_operating_data("FAKE1")
            await client.stocks.get_operating_data("FAKE1")
            assert route.call_count == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_operating_data_raw(self, cache_dir: Path) -> None:
        """Test fetching raw operating data."""
        api_token = "test-token"
        respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/operating_data"
        ).mock(return_value=Response(200, json=SAMPLE_OPERATING_DATA_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            raw = await client.stocks.get_operating_data_raw("FAKE1")
            assert isinstance(raw, dict)
            assert "FAKE1" in raw

    @pytest.mark.asyncio
    @respx.mock
    async def test_operating_data_metric_details(self, cache_dir: Path) -> None:
        """Test that operating data metrics contain expected details."""
        api_token = "test-token"
        respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/operating_data"
        ).mock(return_value=Response(200, json=SAMPLE_OPERATING_DATA_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            ops = await client.stocks.get_operating_data("FAKE1")

            # Check first metric has expected structure
            first_key = next(iter(ops.metrics.keys()))
            metric = ops.metrics[first_key]
            assert metric.name is not None
            assert metric.key is not None
            assert len(metric.data.annual) > 0


class TestSegmentsDataEndpoint:
    """Tests for segments data endpoint."""

    @pytest.fixture
    def cache_dir(self) -> Path:
        """Create a temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_segments_data(self, cache_dir: Path) -> None:
        """Test fetching segments data returns typed model."""
        api_token = "test-token"
        respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/segments_data"
        ).mock(return_value=Response(200, json=SAMPLE_SEGMENTS_DATA_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            segments = await client.stocks.get_segments_data("FAKE1")

            assert isinstance(segments, SegmentData)
            assert segments.symbol == "FAKE1"
            assert len(segments.business.keys) > 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_segments_data_cached(self, cache_dir: Path) -> None:
        """Test that segments data is cached."""
        api_token = "test-token"
        route = respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/segments_data"
        ).mock(return_value=Response(200, json=SAMPLE_SEGMENTS_DATA_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            await client.stocks.get_segments_data("FAKE1")
            await client.stocks.get_segments_data("FAKE1")
            assert route.call_count == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_segments_data_raw(self, cache_dir: Path) -> None:
        """Test fetching raw segments data."""
        api_token = "test-token"
        respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/segments_data"
        ).mock(return_value=Response(200, json=SAMPLE_SEGMENTS_DATA_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            raw = await client.stocks.get_segments_data_raw("FAKE1")
            assert isinstance(raw, dict)
            assert "business" in raw

    @pytest.mark.asyncio
    @respx.mock
    async def test_segments_data_business_details(self, cache_dir: Path) -> None:
        """Test that segment data contains expected business details."""
        api_token = "test-token"
        respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/segments_data"
        ).mock(return_value=Response(200, json=SAMPLE_SEGMENTS_DATA_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            segments = await client.stocks.get_segments_data("FAKE1")

            # Check business segments have expected structure
            assert len(segments.business.annual) > 0
            period = segments.business.annual[0]
            assert period.date is not None
            assert len(period.segments) > 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_segments_data_geographic_details(self, cache_dir: Path) -> None:
        """Test that segment data contains expected geographic details."""
        api_token = "test-token"
        respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/segments_data"
        ).mock(return_value=Response(200, json=SAMPLE_SEGMENTS_DATA_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            segments = await client.stocks.get_segments_data("FAKE1")

            # Check geographic segments have expected structure
            assert len(segments.geographic.keys) > 0
            assert len(segments.geographic.annual) > 0


class TestOperatingModelsEdgeCases:
    """Tests for edge cases in operating/segment model parsing."""

    def test_operating_data_empty_response(self) -> None:
        """Test parsing empty operating data response."""
        ops = OperatingData.from_api_response({}, "TEST")
        assert ops.symbol == "TEST"
        assert len(ops.metrics) == 0

    def test_operating_data_wrong_symbol(self) -> None:
        """Test parsing operating data with different symbol key."""
        ops = OperatingData.from_api_response({"OTHER": {}}, "TEST")
        assert ops.symbol == "TEST"
        assert len(ops.metrics) == 0

    def test_segment_data_empty_response(self) -> None:
        """Test parsing empty segment data response."""
        segments = SegmentData.from_api_response({}, "TEST")
        assert segments.symbol == "TEST"
        assert len(segments.business.keys) == 0
        assert len(segments.geographic.keys) == 0


class TestOwnershipEndpoint:
    """Tests for ownership endpoint."""

    @pytest.fixture
    def cache_dir(self) -> Path:
        """Create a temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_ownership(self, cache_dir: Path) -> None:
        """Test fetching ownership returns typed model."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/ownership").mock(
            return_value=Response(200, json=SAMPLE_OWNERSHIP_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            ownership = await client.stocks.get_ownership("FAKE1")

            assert isinstance(ownership, StockOwnership)
            assert ownership.symbol == "FAKE1"
            assert ownership.institutional_ownership is not None
            assert ownership.insider_ownership is not None

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_ownership_cached(self, cache_dir: Path) -> None:
        """Test that ownership is cached."""
        api_token = "test-token"
        route = respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/ownership"
        ).mock(return_value=Response(200, json=SAMPLE_OWNERSHIP_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            await client.stocks.get_ownership("FAKE1")
            await client.stocks.get_ownership("FAKE1")
            assert route.call_count == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_ownership_raw(self, cache_dir: Path) -> None:
        """Test fetching raw ownership data."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/ownership").mock(
            return_value=Response(200, json=SAMPLE_OWNERSHIP_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            raw = await client.stocks.get_ownership_raw("FAKE1")
            assert isinstance(raw, dict)
            assert "Institutional_Ownership" in raw

    @pytest.mark.asyncio
    @respx.mock
    async def test_ownership_details(self, cache_dir: Path) -> None:
        """Test that ownership contains expected details."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/ownership").mock(
            return_value=Response(200, json=SAMPLE_OWNERSHIP_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            ownership = await client.stocks.get_ownership("FAKE1")

            assert ownership.institutional_ownership.percentage is not None
            assert ownership.institutional_ownership.value is not None
            assert ownership.insider_ownership.percentage is not None
            assert ownership.shares_outstanding is not None


class TestIndicatorHistoryEndpoint:
    """Tests for indicator history endpoint."""

    @pytest.fixture
    def cache_dir(self) -> Path:
        """Create a temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_indicator_history(self, cache_dir: Path) -> None:
        """Test fetching indicator history returns typed model."""
        api_token = "test-token"
        respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/indicator_history"
        ).mock(return_value=Response(200, json=SAMPLE_INDICATOR_HISTORY_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            history = await client.stocks.get_indicator_history("FAKE1")

            assert isinstance(history, OwnershipHistory)
            assert history.symbol == "FAKE1"
            assert len(history.institutional_ownership) > 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_indicator_history_cached(self, cache_dir: Path) -> None:
        """Test that indicator history is cached."""
        api_token = "test-token"
        route = respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/indicator_history"
        ).mock(return_value=Response(200, json=SAMPLE_INDICATOR_HISTORY_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            await client.stocks.get_indicator_history("FAKE1")
            await client.stocks.get_indicator_history("FAKE1")
            assert route.call_count == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_indicator_history_raw(self, cache_dir: Path) -> None:
        """Test fetching raw indicator history data."""
        api_token = "test-token"
        respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/indicator_history"
        ).mock(return_value=Response(200, json=SAMPLE_INDICATOR_HISTORY_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            raw = await client.stocks.get_indicator_history_raw("FAKE1")
            assert isinstance(raw, dict)
            assert "insti_owner" in raw

    @pytest.mark.asyncio
    @respx.mock
    async def test_indicator_history_details(self, cache_dir: Path) -> None:
        """Test that indicator history contains expected details."""
        api_token = "test-token"
        respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/indicator_history"
        ).mock(return_value=Response(200, json=SAMPLE_INDICATOR_HISTORY_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            history = await client.stocks.get_indicator_history("FAKE1")

            # Check institutional ownership has expected structure
            point = history.institutional_ownership[0]
            assert point.date is not None
            assert point.percentage is not None
            assert point.shares is not None

            # Check shares outstanding series exists
            assert len(history.shares_outstanding) > 0


class TestIndicatorsListEndpoint:
    """Tests for indicators list endpoint."""

    @pytest.fixture
    def cache_dir(self) -> Path:
        """Create a temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_indicators(self, cache_dir: Path) -> None:
        """Test fetching indicators list returns typed model."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/indicators").mock(
            return_value=Response(200, json=SAMPLE_INDICATORS_LIST_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            indicators = await client.stocks.get_indicators()

            assert isinstance(indicators, IndicatorsList)
            assert len(indicators.indicators) > 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_indicators_cached(self, cache_dir: Path) -> None:
        """Test that indicators list is cached."""
        api_token = "test-token"
        route = respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/indicators"
        ).mock(return_value=Response(200, json=SAMPLE_INDICATORS_LIST_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            await client.stocks.get_indicators()
            await client.stocks.get_indicators()
            assert route.call_count == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_indicators_raw(self, cache_dir: Path) -> None:
        """Test fetching raw indicators list data."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/indicators").mock(
            return_value=Response(200, json=SAMPLE_INDICATORS_LIST_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            raw = await client.stocks.get_indicators_raw()
            assert isinstance(raw, list)
            assert len(raw) > 0
            assert "key" in raw[0]
            assert "name" in raw[0]

    @pytest.mark.asyncio
    @respx.mock
    async def test_indicators_search(self, cache_dir: Path) -> None:
        """Test searching indicators by name or key."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/indicators").mock(
            return_value=Response(200, json=SAMPLE_INDICATORS_LIST_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            indicators = await client.stocks.get_indicators()

            # Search for indicators containing "margin"
            results = indicators.search("margin")
            assert len(results) > 0
            for ind in results:
                assert "margin" in ind.key.lower() or "margin" in ind.name.lower()

    @pytest.mark.asyncio
    @respx.mock
    async def test_indicators_get_by_key(self, cache_dir: Path) -> None:
        """Test getting an indicator by key."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/indicators").mock(
            return_value=Response(200, json=SAMPLE_INDICATORS_LIST_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            indicators = await client.stocks.get_indicators()

            # Get specific indicator
            ind = indicators.get_by_key("net_income")
            assert ind is not None
            assert ind.key == "net_income"
            assert ind.name == "Net Income"


class TestIndicatorEndpoint:
    """Tests for single indicator endpoint."""

    @pytest.fixture
    def cache_dir(self) -> Path:
        """Create a temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_indicator(self, cache_dir: Path) -> None:
        """Test fetching indicator returns typed model."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/net_income").mock(
            return_value=Response(200, json=SAMPLE_INDICATOR_NET_INCOME_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            indicator = await client.stocks.get_indicator("FAKE1", "net_income")

            assert isinstance(indicator, IndicatorTimeSeries)
            assert indicator.symbol == "FAKE1"
            assert indicator.indicator_key == "net_income"
            assert len(indicator.data) > 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_indicator_cached(self, cache_dir: Path) -> None:
        """Test that indicator is cached."""
        api_token = "test-token"
        route = respx.get(
            f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/net_income"
        ).mock(return_value=Response(200, json=SAMPLE_INDICATOR_NET_INCOME_RESPONSE))

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            await client.stocks.get_indicator("FAKE1", "net_income")
            await client.stocks.get_indicator("FAKE1", "net_income")
            assert route.call_count == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_indicator_raw(self, cache_dir: Path) -> None:
        """Test fetching raw indicator data."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/net_income").mock(
            return_value=Response(200, json=SAMPLE_INDICATOR_NET_INCOME_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            raw = await client.stocks.get_indicator_raw("FAKE1", "net_income")
            assert isinstance(raw, list)
            assert len(raw) > 0
            # Each item should be [date, value]
            assert len(raw[0]) == 2

    @pytest.mark.asyncio
    @respx.mock
    async def test_indicator_data_points(self, cache_dir: Path) -> None:
        """Test that indicator data points contain expected details."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/net_income").mock(
            return_value=Response(200, json=SAMPLE_INDICATOR_NET_INCOME_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            indicator = await client.stocks.get_indicator("FAKE1", "net_income")

            point = indicator.data[0]
            assert point.date is not None
            assert point.value is not None
            assert point.value > 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_indicator_latest_earliest(self, cache_dir: Path) -> None:
        """Test getting latest and earliest data points."""
        api_token = "test-token"
        respx.get(f"https://api.gurufocus.com/public/user/{api_token}/stock/FAKE1/net_income").mock(
            return_value=Response(200, json=SAMPLE_INDICATOR_NET_INCOME_RESPONSE)
        )

        async with GuruFocusClient(
            api_token=api_token,
            cache_dir=str(cache_dir),
        ) as client:
            indicator = await client.stocks.get_indicator("FAKE1", "net_income")

            latest = indicator.latest
            earliest = indicator.earliest
            assert latest is not None
            assert earliest is not None
            assert latest.date >= earliest.date


class TestOwnershipModelsEdgeCases:
    """Tests for edge cases in ownership/indicator model parsing."""

    def test_ownership_empty_response(self) -> None:
        """Test parsing empty ownership response."""
        ownership = StockOwnership.from_api_response({}, "TEST")
        assert ownership.symbol == "TEST"
        # Empty dicts still parse to OwnershipBreakdown but with None values
        assert ownership.shares_outstanding is None
        assert ownership.company is None

    def test_ownership_history_empty_response(self) -> None:
        """Test parsing empty ownership history response."""
        history = OwnershipHistory.from_api_response({}, "TEST")
        assert history.symbol == "TEST"
        assert len(history.institutional_ownership) == 0
        assert len(history.shares_outstanding) == 0

    def test_indicators_list_empty_response(self) -> None:
        """Test parsing empty indicators list response."""
        indicators = IndicatorsList.from_api_response([])
        assert len(indicators.indicators) == 0

    def test_indicator_time_series_empty_response(self) -> None:
        """Test parsing empty indicator time series response."""
        indicator = IndicatorTimeSeries.from_api_response([], "TEST", "net_income")
        assert indicator.symbol == "TEST"
        assert indicator.indicator_key == "net_income"
        assert len(indicator.data) == 0
        assert indicator.latest is None
        assert indicator.earliest is None


class TestNewsFeedEndpoint:
    """Tests for news feed endpoint."""

    @pytest.fixture
    def cache_dir(self) -> Path:
        """Create a temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_news_feed_returns_response(self, cache_dir: Path) -> None:
        """Test that get_news_feed returns a NewsFeedResponse."""
        respx.get("https://api.gurufocus.com/public/user/test-token/stock/news_feed").mock(
            return_value=Response(200, json=SAMPLE_NEWS_FEED_RESPONSE)
        )

        async with GuruFocusClient(
            api_token="test-token",
            cache_enabled=True,
            cache_dir=cache_dir,
        ) as client:
            result = await client.stocks.get_news_feed()

        assert isinstance(result, NewsFeedResponse)
        assert result.count == 5
        assert len(result.items) == 5

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_news_feed_parses_items(self, cache_dir: Path) -> None:
        """Test that news items are parsed correctly."""
        respx.get("https://api.gurufocus.com/public/user/test-token/stock/news_feed").mock(
            return_value=Response(200, json=SAMPLE_NEWS_FEED_RESPONSE)
        )

        async with GuruFocusClient(
            api_token="test-token",
            cache_enabled=True,
            cache_dir=cache_dir,
        ) as client:
            result = await client.stocks.get_news_feed()

        first = result.items[0]
        assert first.date == "2025-01-10 11:44:57"
        assert first.headline == "Fake Corp Announces Record Q4 Earnings"
        assert "gurufocus.com" in first.url

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_news_feed_raw_returns_list(self, cache_dir: Path) -> None:
        """Test that get_news_feed_raw returns raw list."""
        respx.get("https://api.gurufocus.com/public/user/test-token/stock/news_feed").mock(
            return_value=Response(200, json=SAMPLE_NEWS_FEED_RESPONSE)
        )

        async with GuruFocusClient(
            api_token="test-token",
            cache_enabled=True,
            cache_dir=cache_dir,
        ) as client:
            result = await client.stocks.get_news_feed_raw()

        assert isinstance(result, list)
        assert len(result) == 5


class TestEstimateHistoryEndpoint:
    """Tests for estimate history endpoint."""

    @pytest.fixture
    def cache_dir(self) -> Path:
        """Create a temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_estimate_history_returns_response(self, cache_dir: Path) -> None:
        """Test that get_estimate_history returns an EstimateHistoryResponse."""
        respx.get(
            "https://api.gurufocus.com/public/user/test-token/stock/AAPL/estimate_history"
        ).mock(return_value=Response(200, json=SAMPLE_ESTIMATE_HISTORY_RESPONSE))

        async with GuruFocusClient(
            api_token="test-token",
            cache_enabled=True,
            cache_dir=cache_dir,
        ) as client:
            result = await client.stocks.get_estimate_history("AAPL")

        assert isinstance(result, EstimateHistoryResponse)
        assert result.symbol == "AAPL"
        assert len(result.annual) > 0
        assert len(result.quarterly) > 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_estimate_history_parses_metrics(self, cache_dir: Path) -> None:
        """Test that estimate metrics are parsed correctly."""
        respx.get(
            "https://api.gurufocus.com/public/user/test-token/stock/AAPL/estimate_history"
        ).mock(return_value=Response(200, json=SAMPLE_ESTIMATE_HISTORY_RESPONSE))

        async with GuruFocusClient(
            api_token="test-token",
            cache_enabled=True,
            cache_dir=cache_dir,
        ) as client:
            result = await client.stocks.get_estimate_history("AAPL")

        # Find EPS estimate metric
        eps_metric = next((m for m in result.annual if m.metric_name == "eps_estimate"), None)
        assert eps_metric is not None
        assert len(eps_metric.periods) > 0

        # Check first period
        first_period = eps_metric.periods[0]
        assert first_period.period == "202509"
        assert first_period.actual == 7.25
        assert first_period.estimate_mean == 7.10

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_estimate_history_raw_returns_dict(self, cache_dir: Path) -> None:
        """Test that get_estimate_history_raw returns raw dict."""
        respx.get(
            "https://api.gurufocus.com/public/user/test-token/stock/AAPL/estimate_history"
        ).mock(return_value=Response(200, json=SAMPLE_ESTIMATE_HISTORY_RESPONSE))

        async with GuruFocusClient(
            api_token="test-token",
            cache_enabled=True,
            cache_dir=cache_dir,
        ) as client:
            result = await client.stocks.get_estimate_history_raw("AAPL")

        assert isinstance(result, dict)
        assert "annual" in result
        assert "quarterly" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_estimate_history_normalizes_symbol(self, cache_dir: Path) -> None:
        """Test that symbol is normalized to uppercase."""
        respx.get(
            "https://api.gurufocus.com/public/user/test-token/stock/AAPL/estimate_history"
        ).mock(return_value=Response(200, json=SAMPLE_ESTIMATE_HISTORY_RESPONSE))

        async with GuruFocusClient(
            api_token="test-token",
            cache_enabled=True,
            cache_dir=cache_dir,
        ) as client:
            result = await client.stocks.get_estimate_history("aapl")

        assert result.symbol == "AAPL"


class TestNewsFeedModelsEdgeCases:
    """Tests for edge cases in news feed model parsing."""

    def test_news_feed_empty_response(self) -> None:
        """Test parsing empty news feed response."""
        news = NewsFeedResponse.from_api_response([])
        assert news.count == 0
        assert len(news.items) == 0

    def test_news_feed_missing_fields(self) -> None:
        """Test parsing news item with missing optional fields."""
        news = NewsFeedResponse.from_api_response([{"date": "2025-01-01", "headline": "Test"}])
        assert len(news.items) == 1
        assert news.items[0].url == ""


class TestEstimateHistoryModelsEdgeCases:
    """Tests for edge cases in estimate history model parsing."""

    def test_estimate_history_empty_response(self) -> None:
        """Test parsing empty estimate history response."""
        history = EstimateHistoryResponse.from_api_response({}, "TEST")
        assert history.symbol == "TEST"
        assert len(history.annual) == 0
        assert len(history.quarterly) == 0

    def test_estimate_history_partial_response(self) -> None:
        """Test parsing estimate history with only annual data."""
        history = EstimateHistoryResponse.from_api_response(
            {"annual": {"eps_estimate": {"202509": {"actual": 5.0}}}}, "TEST"
        )
        assert history.symbol == "TEST"
        assert len(history.annual) == 1
        assert len(history.quarterly) == 0
