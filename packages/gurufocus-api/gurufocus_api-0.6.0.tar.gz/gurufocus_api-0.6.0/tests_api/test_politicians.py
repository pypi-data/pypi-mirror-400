"""Tests for politician-related endpoints."""

import json
from pathlib import Path

import pytest
import respx
from httpx import Response

from gurufocus_api import GuruFocusClient
from gurufocus_api.models.politicians import (
    PoliticiansListResponse,
    PoliticianTransactionsResponse,
)

# Load test fixtures
FIXTURES_DIR = Path(__file__).parent / "data"


def load_fixture(category: str, filename: str) -> dict | list:
    """Load a JSON fixture file."""
    filepath = FIXTURES_DIR / category / filename
    with open(filepath) as f:
        return json.load(f)


# Pre-load fixtures
POLITICIANS_LIST_DATA = load_fixture("politicians", "list.json")
TRANSACTIONS_PAGE1_DATA = load_fixture("politician_transactions", "page1.json")
TRANSACTIONS_PAGE2_DATA = load_fixture("politician_transactions", "page2.json")


class TestPoliticiansListEndpoint:
    """Tests for GET /politicians endpoint."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_politicians_returns_response(self) -> None:
        """Test that get_politicians returns a PoliticiansListResponse."""
        respx.get("https://api.gurufocus.com/public/user/test-token/politicians").mock(
            return_value=Response(200, json=POLITICIANS_LIST_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.politicians.get_politicians()

        assert isinstance(result, PoliticiansListResponse)
        assert result.count == 5
        assert len(result.politicians) == 5

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_politicians_parses_politician_data(self) -> None:
        """Test that politician data is parsed correctly."""
        respx.get("https://api.gurufocus.com/public/user/test-token/politicians").mock(
            return_value=Response(200, json=POLITICIANS_LIST_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.politicians.get_politicians()

        first = result.politicians[0]
        assert first.id == 1
        assert first.full_name == "Jane Smith"
        assert first.position == "senator"
        assert first.district == "CA00"
        assert first.state == "CA"
        assert first.party == "Democrat"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_politicians_includes_all_parties(self) -> None:
        """Test that politicians from all parties are included."""
        respx.get("https://api.gurufocus.com/public/user/test-token/politicians").mock(
            return_value=Response(200, json=POLITICIANS_LIST_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.politicians.get_politicians()

        parties = {p.party for p in result.politicians}
        assert "Democrat" in parties
        assert "Republican" in parties
        assert "Independent" in parties

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_politicians_raw_returns_list(self) -> None:
        """Test that get_politicians_raw returns raw list."""
        respx.get("https://api.gurufocus.com/public/user/test-token/politicians").mock(
            return_value=Response(200, json=POLITICIANS_LIST_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.politicians.get_politicians_raw()

        assert isinstance(result, list)
        assert len(result) == 5


class TestPoliticianTransactionsEndpoint:
    """Tests for GET /politicians/transactions endpoint."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_transactions_returns_response(self) -> None:
        """Test that get_transactions returns a PoliticianTransactionsResponse."""
        respx.get("https://api.gurufocus.com/public/user/test-token/politicians/transactions").mock(
            return_value=Response(200, json=TRANSACTIONS_PAGE1_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.politicians.get_transactions()

        assert isinstance(result, PoliticianTransactionsResponse)
        assert result.count == 300
        assert result.current_page == 1
        assert result.last_page == 5
        assert result.total == 1250

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_transactions_parses_transaction_data(self) -> None:
        """Test that transaction data is parsed correctly."""
        respx.get("https://api.gurufocus.com/public/user/test-token/politicians/transactions").mock(
            return_value=Response(200, json=TRANSACTIONS_PAGE1_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.politicians.get_transactions()

        assert len(result.transactions) == 5

        first = result.transactions[0]
        assert first.symbol == "AAPL"
        assert first.company == "Fake Apple Corp"
        assert first.exchange == "NAS"
        assert first.trans_type == "purchase"
        assert first.amount == "$15,001 - $50,000"
        assert first.disclosure_date == "2025-12-19"
        assert first.transaction_date == "2025-12-16"
        assert first.politician_id == 1
        assert first.politician_name == "Jane Smith"
        assert first.position == "senator"
        assert first.state == "CA"
        assert first.party == "Democrat"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_transactions_with_pagination(self) -> None:
        """Test that pagination works correctly."""
        respx.get("https://api.gurufocus.com/public/user/test-token/politicians/transactions").mock(
            return_value=Response(200, json=TRANSACTIONS_PAGE2_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.politicians.get_transactions(page=2)

        assert result.current_page == 2
        assert len(result.transactions) == 2

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_transactions_with_politician_filter(self) -> None:
        """Test filtering by politician ID."""
        respx.get("https://api.gurufocus.com/public/user/test-token/politicians/transactions").mock(
            return_value=Response(200, json=TRANSACTIONS_PAGE1_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.politicians.get_transactions(politician_id=1)

        assert isinstance(result, PoliticianTransactionsResponse)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_transactions_with_sort_order(self) -> None:
        """Test sorting options."""
        respx.get("https://api.gurufocus.com/public/user/test-token/politicians/transactions").mock(
            return_value=Response(200, json=TRANSACTIONS_PAGE1_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.politicians.get_transactions(
                sort="transaction_date", order="desc"
            )

        assert isinstance(result, PoliticianTransactionsResponse)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_transactions_parses_option_transactions(self) -> None:
        """Test that option transactions are parsed correctly."""
        respx.get("https://api.gurufocus.com/public/user/test-token/politicians/transactions").mock(
            return_value=Response(200, json=TRANSACTIONS_PAGE1_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.politicians.get_transactions()

        # Find the option transaction (NVDA with call option)
        option_txn = next((t for t in result.transactions if t.symbol == "NVDA"), None)
        assert option_txn is not None
        assert option_txn.option_type == "call"
        assert option_txn.strike_price == "$150"
        assert option_txn.expiration_date == "2026-01-15"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_transactions_raw_returns_dict(self) -> None:
        """Test that get_transactions_raw returns raw dict."""
        respx.get("https://api.gurufocus.com/public/user/test-token/politicians/transactions").mock(
            return_value=Response(200, json=TRANSACTIONS_PAGE1_DATA)
        )

        async with GuruFocusClient(api_token="test-token", cache_enabled=False) as client:
            result = await client.politicians.get_transactions_raw()

        assert isinstance(result, dict)
        assert "data" in result
        assert "total" in result


class TestPoliticianModelsEdgeCases:
    """Test edge cases in politician model parsing."""

    def test_politicians_list_empty_response(self) -> None:
        """Test handling of empty politicians list."""
        result = PoliticiansListResponse.from_api_response([])
        assert result.count == 0
        assert len(result.politicians) == 0

    def test_transactions_empty_data(self) -> None:
        """Test handling of empty transactions response."""
        result = PoliticianTransactionsResponse.from_api_response(
            {"data": [], "count": 0, "currentPage": 1, "lastPage": 1, "total": 0}
        )
        assert len(result.transactions) == 0
        assert result.total == 0

    def test_transactions_missing_optional_fields(self) -> None:
        """Test handling of transactions with missing optional fields."""
        result = PoliticianTransactionsResponse.from_api_response(
            {
                "data": [
                    {
                        "symbol": "AAPL",
                        "company": "Apple Inc",
                        "exchange": "NAS",
                        "industry": None,
                        "class": "Common Stock",
                        "stockid": "US0001",
                        "option_type": "",
                        "strike_price": "",
                        "trans_type": "purchase",
                        "amount": "$1,001 - $15,000",
                        "disclosure_date": "2025-01-01",
                        "transaction_date": "2024-12-30",
                        "expiration_date": "",
                        "id": 1,
                        "full_name": "Test Person",
                        "official_full": None,
                        "position": "senator",
                        "state": "CA",
                        "party": "Democrat",
                    }
                ],
                "count": 1,
                "currentPage": 1,
                "lastPage": 1,
                "total": 1,
            }
        )
        assert len(result.transactions) == 1
        txn = result.transactions[0]
        assert txn.option_type is None
        assert txn.strike_price is None
        assert txn.expiration_date is None
        assert txn.official_full_name is None

    def test_politician_with_null_district(self) -> None:
        """Test handling of politician with null district."""
        result = PoliticiansListResponse.from_api_response(
            [
                {
                    "id": 1,
                    "full_name": "Former Senator",
                    "position": "senator",
                    "district": None,
                    "state": "PA",
                    "party": "Republican",
                }
            ]
        )
        assert len(result.politicians) == 1
        assert result.politicians[0].district is None
