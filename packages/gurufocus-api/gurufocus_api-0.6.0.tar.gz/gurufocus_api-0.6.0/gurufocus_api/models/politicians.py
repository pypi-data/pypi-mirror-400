"""Pydantic models for GuruFocus politician data endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Politician(BaseModel):
    """A tracked politician."""

    id: int = Field(description="Unique identifier for the politician")
    full_name: str = Field(description="Full name of the politician")
    position: str = Field(description="Position (senator or representative)")
    district: str | None = Field(
        default=None, description="Congressional district (e.g., 'CA12', 'TX00')"
    )
    state: str = Field(description="State abbreviation (e.g., 'CA', 'TX')")
    party: str = Field(description="Political party (Democrat, Republican, Independent, etc.)")


class PoliticiansListResponse(BaseModel):
    """Response containing list of tracked politicians."""

    politicians: list[Politician] = Field(default_factory=list, description="List of politicians")
    count: int = Field(default=0, description="Number of politicians")

    @classmethod
    def from_api_response(cls, data: list[dict[str, Any]]) -> PoliticiansListResponse:
        """Parse API response into PoliticiansListResponse.

        Args:
            data: List of politician dictionaries from API

        Returns:
            Parsed PoliticiansListResponse
        """
        politicians = [
            Politician(
                id=item.get("id", 0),
                full_name=item.get("full_name", ""),
                position=item.get("position", ""),
                district=item.get("district"),
                state=item.get("state", ""),
                party=item.get("party", ""),
            )
            for item in data
        ]
        return cls(politicians=politicians, count=len(politicians))


class PoliticianTransaction(BaseModel):
    """A stock transaction by a politician."""

    # Stock information
    symbol: str = Field(description="Stock ticker symbol")
    company: str = Field(description="Company name")
    exchange: str = Field(description="Exchange (e.g., 'NAS', 'NYSE')")
    industry: int | None = Field(default=None, description="Industry code")
    asset_class: str = Field(default="", description="Asset class (e.g., 'Common Stock')")
    stock_id: str = Field(default="", description="GuruFocus stock ID")

    # Option information (if applicable)
    option_type: str | None = Field(
        default=None, description="Option type (call/put) if applicable"
    )
    strike_price: str | None = Field(default=None, description="Strike price if option")
    expiration_date: str | None = Field(default=None, description="Option expiration date")

    # Transaction details
    trans_type: str = Field(
        description="Transaction type (purchase, sale_full, sale_partial, exchange)"
    )
    amount: str = Field(description="Transaction amount range (e.g., '$15,001 - $50,000')")
    disclosure_date: str = Field(description="Date transaction was disclosed")
    transaction_date: str = Field(description="Date of transaction")

    # Politician information
    politician_id: int = Field(description="Politician ID")
    politician_name: str = Field(description="Politician name")
    official_full_name: str | None = Field(default=None, description="Official full name")
    position: str = Field(description="Position (senator or representative)")
    state: str = Field(description="State abbreviation")
    party: str = Field(description="Political party")


class PoliticianTransactionsResponse(BaseModel):
    """Paginated response containing politician transactions."""

    transactions: list[PoliticianTransaction] = Field(
        default_factory=list, description="List of transactions"
    )
    count: int = Field(default=0, description="Number of transactions in this page")
    current_page: int = Field(default=1, description="Current page number")
    last_page: int = Field(default=1, description="Last page number")
    total: int = Field(default=0, description="Total number of transactions")

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> PoliticianTransactionsResponse:
        """Parse API response into PoliticianTransactionsResponse.

        Args:
            data: API response dictionary

        Returns:
            Parsed PoliticianTransactionsResponse
        """
        transactions_data = data.get("data", [])
        transactions = []

        for item in transactions_data:
            transaction = PoliticianTransaction(
                symbol=item.get("symbol", ""),
                company=item.get("company", ""),
                exchange=item.get("exchange", ""),
                industry=item.get("industry"),
                asset_class=item.get("class", ""),
                stock_id=item.get("stockid", ""),
                option_type=item.get("option_type") or None,
                strike_price=item.get("strike_price") or None,
                expiration_date=item.get("expiration_date") or None,
                trans_type=item.get("trans_type", ""),
                amount=item.get("amount", ""),
                disclosure_date=item.get("disclosure_date", ""),
                transaction_date=item.get("transaction_date", ""),
                politician_id=item.get("id", 0),
                politician_name=item.get("full_name", ""),
                official_full_name=item.get("official_full"),
                position=item.get("position", ""),
                state=item.get("state", ""),
                party=item.get("party", ""),
            )
            transactions.append(transaction)

        return cls(
            transactions=transactions,
            count=data.get("count", len(transactions)),
            current_page=data.get("currentPage", 1),
            last_page=data.get("lastPage", 1),
            total=data.get("total", len(transactions)),
        )
