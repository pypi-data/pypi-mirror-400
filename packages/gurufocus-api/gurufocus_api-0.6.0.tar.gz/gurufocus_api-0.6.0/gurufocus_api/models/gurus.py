"""Pydantic models for guru/institutional investor data."""

from typing import Any

from pydantic import BaseModel, Field

# --- Models for GET /stock/{symbol}/gurus endpoint ---


class StockGuruPick(BaseModel):
    """A guru's recent trading activity in a stock (from picks array)."""

    guru: str = Field(description="Guru or firm name")
    guru_id: str = Field(description="Unique identifier for the guru")
    date: str = Field(description="Transaction date (YYYY-MM-DD)")
    action: str = Field(description="Trade action (Add, Reduce, New Buy, Sold Out)")
    impact: str = Field(description="Impact score on position")
    price_min: str = Field(description="Minimum price during period")
    price_max: str = Field(description="Maximum price during period")
    avg_price: str = Field(description="Average price during period")
    comment: str = Field(description="Action description (e.g., 'Add 12.5%')")
    current_shares: str = Field(description="Current shares held after action")


class StockGuruHolding(BaseModel):
    """A guru's current holding in a stock (from holdings array)."""

    guru: str = Field(description="Guru or firm name")
    guru_id: str = Field(description="Unique identifier for the guru")
    date: str = Field(description="Date of holding report (YYYY-MM-DD)")
    current_shares: str = Field(description="Current shares held (formatted with commas)")
    perc_shares: str = Field(description="Percentage of company shares held")
    perc_assets: str = Field(description="Percentage of guru's portfolio")
    change: str = Field(description="Percentage change in position")


class StockGurusResponse(BaseModel):
    """Guru holdings and trading activity for a stock.

    Response from GET /stock/{symbol}/gurus endpoint.
    Contains both recent trading activity (picks) and current holdings.
    """

    symbol: str = Field(description="Stock ticker symbol")
    picks: list[StockGuruPick] = Field(
        default_factory=list, description="Recent guru trading activity"
    )
    holdings: list[StockGuruHolding] = Field(
        default_factory=list, description="Current guru holdings"
    )

    @classmethod
    def from_api_response(cls, data: dict[str, Any], symbol: str) -> "StockGurusResponse":
        """Create StockGurusResponse from raw API response.

        Args:
            data: Raw JSON response from the API - dict with symbol as key
                  e.g., {"AAPL": {"picks": [...], "holdings": [...]}}
            symbol: Stock ticker symbol

        Returns:
            Populated StockGurusResponse instance
        """
        symbol = symbol.upper().strip()
        symbol_data = data.get(symbol, data)

        # Parse picks
        picks_raw = symbol_data.get("picks", [])
        picks = [_parse_stock_guru_pick(p) for p in picks_raw if isinstance(p, dict)]

        # Parse holdings
        holdings_raw = symbol_data.get("holdings", [])
        holdings = [_parse_stock_guru_holding(h) for h in holdings_raw if isinstance(h, dict)]

        return cls(
            symbol=symbol,
            picks=picks,
            holdings=holdings,
        )


def _parse_stock_guru_pick(data: dict[str, Any]) -> StockGuruPick:
    """Parse a single guru pick from API data."""
    return StockGuruPick(
        guru=data.get("guru", "Unknown"),
        guru_id=str(data.get("guru_id", "")),
        date=data.get("date", ""),
        action=data.get("action", ""),
        impact=str(data.get("impact", "0")),
        price_min=str(data.get("price_min", "0")),
        price_max=str(data.get("price_max", "0")),
        avg_price=str(data.get("Avg", data.get("avg_price", "0"))),
        comment=data.get("comment", ""),
        current_shares=str(data.get("current_shares", "0")),
    )


def _parse_stock_guru_holding(data: dict[str, Any]) -> StockGuruHolding:
    """Parse a single guru holding from API data."""
    return StockGuruHolding(
        guru=data.get("guru", "Unknown"),
        guru_id=str(data.get("guru_id", "")),
        date=data.get("date", ""),
        current_shares=str(data.get("current_shares", "0")),
        perc_shares=str(data.get("perc_shares", "0")),
        perc_assets=str(data.get("perc_assets", "0")),
        change=str(data.get("change", "0")),
    )


# --- Models for GET /gurulist endpoint ---


class GuruListItem(BaseModel):
    """A single guru from the guru list endpoint."""

    guru_id: str = Field(description="Unique identifier for the guru")
    name: str = Field(description="Guru or firm name")
    image_url: str | None = Field(default=None, description="URL to guru image")
    firm: str | None = Field(default=None, description="Investment firm name")
    num_stocks: int | None = Field(default=None, description="Number of stocks held")
    equity: float | None = Field(default=None, description="Portfolio equity value (millions USD)")
    turnover: int | None = Field(default=None, description="Portfolio turnover rate (%)")
    last_updated: str | None = Field(default=None, description="Date of last portfolio update")
    cik: str | None = Field(default=None, description="SEC CIK number")
    portfolio_date: str | None = Field(default=None, description="Date of portfolio snapshot")
    fund_ticker: str | None = Field(default=None, description="Fund ticker if applicable")


class GuruListResponse(BaseModel):
    """Response from GET /gurulist endpoint.

    Contains arrays of gurus in different categories (US and Plus).
    """

    us_gurus: list[GuruListItem] = Field(default_factory=list, description="US institutional gurus")
    plus_gurus: list[GuruListItem] = Field(default_factory=list, description="GuruFocus Plus gurus")
    total_count: int = Field(default=0, description="Total number of gurus")

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "GuruListResponse":
        """Create GuruListResponse from API response.

        Args:
            data: Raw JSON response - {"all": {"us": [[...], ...], "plus": [[...], ...]}}

        Returns:
            Populated GuruListResponse instance
        """
        all_data = data.get("all", {})
        us_raw = all_data.get("us", [])
        plus_raw = all_data.get("plus", [])

        us_gurus = [_parse_guru_list_item(item) for item in us_raw if isinstance(item, list)]
        plus_gurus = [_parse_guru_list_item(item) for item in plus_raw if isinstance(item, list)]

        return cls(
            us_gurus=us_gurus,
            plus_gurus=plus_gurus,
            total_count=len(us_gurus) + len(plus_gurus),
        )


def _parse_guru_list_item(item: list[Any]) -> GuruListItem:
    """Parse a guru list item from array format.

    Array format: [id, name, image, firm, num_stocks, equity, turnover, last_update, cik, port_date, fund_ticker]
    """
    return GuruListItem(
        guru_id=str(item[0]) if len(item) > 0 else "",
        name=str(item[1]) if len(item) > 1 and item[1] else "",
        image_url=item[2] if len(item) > 2 and item[2] else None,
        firm=item[3] if len(item) > 3 and item[3] else None,
        num_stocks=int(item[4]) if len(item) > 4 and item[4] else None,
        equity=float(item[5]) if len(item) > 5 and item[5] else None,
        turnover=int(item[6]) if len(item) > 6 and item[6] else None,
        last_updated=item[7] if len(item) > 7 and item[7] else None,
        cik=item[8] if len(item) > 8 and item[8] else None,
        portfolio_date=item[9] if len(item) > 9 and item[9] else None,
        fund_ticker=item[10] if len(item) > 10 and item[10] else None,
    )


# --- Models for GET /guru/{id}/aggregated endpoint ---


class GuruAggregatedSummary(BaseModel):
    """Summary data from guru aggregated portfolio."""

    firm: str | None = Field(default=None, description="Investment firm name")
    num_new: int | None = Field(default=None, description="Number of new positions")
    number_of_stocks: int | None = Field(default=None, description="Total number of stocks")
    equity: float | None = Field(default=None, description="Total equity value (millions USD)")
    turnover: int | None = Field(default=None, description="Portfolio turnover rate (%)")
    country: str | None = Field(default=None, description="Country of operation")
    date: str | None = Field(default=None, description="Date of portfolio snapshot")


class GuruAggregatedHolding(BaseModel):
    """A single holding in a guru's aggregated portfolio."""

    symbol: str = Field(description="Stock ticker symbol")
    company: str | None = Field(default=None, description="Company name")
    exchange: str | None = Field(default=None, description="Stock exchange")
    industry: str | None = Field(default=None, description="Industry classification")
    sector: str | None = Field(default=None, description="Sector classification")

    # Position details
    shares: int | None = Field(default=None, description="Number of shares held")
    price: float | None = Field(default=None, description="Current stock price")
    value: float | None = Field(default=None, description="Position value (thousands USD)")
    position: float | None = Field(default=None, description="Portfolio weight (%)")
    pct: float | None = Field(default=None, description="Percentage of company owned")

    # Changes
    change: str | None = Field(default=None, description="Change description or percentage")
    share_change_pct: str | None = Field(default=None, description="Share change percentage")
    impact: float | None = Field(default=None, description="Impact on portfolio")

    # Additional data
    filing_date: str | None = Field(default=None, description="13F filing date")
    share_class: str | None = Field(default=None, description="Share class (com, cl a, etc.)")
    pe: str | None = Field(default=None, description="P/E ratio")
    dividend_yield: str | None = Field(default=None, description="Dividend yield")
    market_cap: str | None = Field(default=None, description="Market cap (millions USD)")


class GuruAggregatedPortfolio(BaseModel):
    """Aggregated portfolio for a guru from GET /guru/{id}/aggregated."""

    guru_id: str = Field(description="Unique identifier for the guru")
    summary: GuruAggregatedSummary = Field(
        default_factory=GuruAggregatedSummary, description="Portfolio summary"
    )
    holdings: list[GuruAggregatedHolding] = Field(
        default_factory=list, description="Portfolio holdings"
    )

    @classmethod
    def from_api_response(cls, data: dict[str, Any], guru_id: str) -> "GuruAggregatedPortfolio":
        """Create GuruAggregatedPortfolio from API response.

        Args:
            data: Raw JSON response - {"{guru_id}": {"summary": {...}, "port": [...]}}
            guru_id: Guru identifier

        Returns:
            Populated GuruAggregatedPortfolio instance
        """
        # Response is keyed by guru_id
        guru_data = data.get(str(guru_id), data)
        summary_raw = guru_data.get("summary", {})
        holdings_raw = guru_data.get("port", [])

        summary = GuruAggregatedSummary(
            firm=summary_raw.get("firm"),
            num_new=_get_int(summary_raw, "num_new"),
            number_of_stocks=_get_int(summary_raw, "number_of_stocks"),
            equity=_get_float(summary_raw, "equity"),
            turnover=_get_int(summary_raw, "turnover"),
            country=summary_raw.get("country"),
            date=summary_raw.get("date"),
        )

        holdings = [_parse_aggregated_holding(h) for h in holdings_raw if isinstance(h, dict)]

        return cls(
            guru_id=str(guru_id),
            summary=summary,
            holdings=holdings,
        )


def _parse_aggregated_holding(data: dict[str, Any]) -> GuruAggregatedHolding:
    """Parse a single aggregated holding from API data."""
    change = data.get("change", data.get("share_change_pct"))
    change_str = str(change) if change is not None else None

    return GuruAggregatedHolding(
        symbol=data.get("symbol", data.get("symbol_ori", "")),
        company=data.get("company"),
        exchange=data.get("exchange"),
        industry=data.get("industry"),
        sector=data.get("sector"),
        shares=_get_int(data, "share", "shares"),
        price=_get_float(data, "price"),
        value=_get_float(data, "value"),
        position=_get_float(data, "position"),
        pct=_get_float(data, "pct"),
        change=change_str,
        share_change_pct=str(data.get("share_change_pct"))
        if data.get("share_change_pct")
        else None,
        impact=_get_float(data, "impact"),
        filing_date=data.get("13f_date"),
        share_class=data.get("class"),
        pe=data.get("pe"),
        dividend_yield=data.get("yield"),
        market_cap=data.get("mktcap"),
    )


# --- Models for GET /guru/{id}/picks/{start_date}/{page} endpoint ---


class GuruPickItem(BaseModel):
    """A single stock pick from a guru."""

    symbol: str = Field(description="Stock ticker symbol")
    company: str | None = Field(default=None, description="Company name")
    exchange: str | None = Field(default=None, description="Stock exchange")
    industry: str | None = Field(default=None, description="Industry classification")
    sector: str | None = Field(default=None, description="Sector classification")

    # Trade details
    guru_name: str | None = Field(default=None, description="Guru name")
    trade_type: str | None = Field(default=None, description="Type: realtime or quarterly")
    action: str | None = Field(default=None, description="Trade action (Buy, Sell, Add, Reduce)")
    comment: str | None = Field(default=None, description="Action description")
    date: str | None = Field(default=None, description="Recommendation/trade date")

    # Position details
    current_shares: int | None = Field(default=None, description="Current shares held")
    share_change: int | None = Field(default=None, description="Change in shares")
    trans_share: float | None = Field(
        default=None, description="Transaction impact on portfolio (%)"
    )

    # Prices
    price: float | None = Field(default=None, description="Current stock price")
    rec_price: float | None = Field(default=None, description="Recommendation price")
    price_min: float | None = Field(default=None, description="Minimum price during period")
    price_max: float | None = Field(default=None, description="Maximum price during period")
    change_pct: float | None = Field(default=None, description="Price change percentage")


class GuruPicksResponse(BaseModel):
    """Response from GET /guru/{id}/picks/{start_date}/{page} endpoint."""

    guru_id: str = Field(description="Unique identifier for the guru")
    guru_name: str = Field(description="Guru or firm name")
    picks: list[GuruPickItem] = Field(default_factory=list, description="List of stock picks")

    @classmethod
    def from_api_response(cls, data: dict[str, Any], guru_id: str) -> "GuruPicksResponse":
        """Create GuruPicksResponse from API response.

        Args:
            data: Raw JSON response - {"{guru_name}": {"port": [...]}}
            guru_id: Guru identifier

        Returns:
            Populated GuruPicksResponse instance
        """
        # Response is keyed by guru name
        guru_name = next(iter(data.keys())) if data else guru_id
        guru_data = data.get(guru_name, data)
        picks_raw = guru_data.get("port", [])

        picks = [_parse_guru_pick_item(p) for p in picks_raw if isinstance(p, dict)]

        return cls(
            guru_id=str(guru_id),
            guru_name=str(guru_name),
            picks=picks,
        )


def _parse_guru_pick_item(data: dict[str, Any]) -> GuruPickItem:
    """Parse a single guru pick item from API data."""
    return GuruPickItem(
        symbol=data.get("symbol", data.get("symbol_ori", "")),
        company=data.get("company"),
        exchange=data.get("exchange"),
        industry=data.get("industry"),
        sector=data.get("sector"),
        guru_name=data.get("GuruName"),
        trade_type=data.get("type"),
        action=data.get("RecmAction"),
        comment=data.get("comment"),
        date=data.get("RecmDate"),
        current_shares=_get_int(data, "share_current"),
        share_change=_get_int(data, "share_change"),
        trans_share=_get_float(data, "trans_share"),
        price=_get_float(data, "price"),
        rec_price=_get_float(data, "RecmPrice"),
        price_min=_get_float(data, "price_min"),
        price_max=_get_float(data, "price_max"),
        change_pct=_get_float(data, "change"),
    )


# --- Models for GET /guru_realtime_picks endpoint ---


class GuruRealtimePickItem(BaseModel):
    """A single realtime pick from the guru realtime picks endpoint."""

    symbol: str = Field(description="Stock ticker symbol")
    company: str | None = Field(default=None, description="Company name")
    exchange: str | None = Field(default=None, description="Stock exchange")
    guru_name: str | None = Field(default=None, description="Guru name")

    # Trade details
    action: str | None = Field(default=None, description="Trade action (Add, Reduce, Buy, Sell)")
    comment: str | None = Field(default=None, description="Action description")
    date: str | None = Field(default=None, description="Portfolio date")

    # Position details
    shares: int | None = Field(default=None, description="Current shares held")
    price: float | None = Field(default=None, description="Current stock price")
    price_avg: float | None = Field(default=None, description="Average purchase price")
    change_pct: float | None = Field(default=None, description="Position change percentage")
    impact: float | None = Field(default=None, description="Portfolio impact (%)")
    currency: str | None = Field(default=None, description="Currency (e.g., 'USD')")


class GuruRealtimePicksResponse(BaseModel):
    """Response from GET /guru_realtime_picks endpoint.

    Contains paginated realtime guru trading activity.
    """

    picks: list[GuruRealtimePickItem] = Field(
        default_factory=list, description="List of realtime picks"
    )
    total: int = Field(default=0, description="Total number of picks")
    current_page: int = Field(default=1, description="Current page number")
    last_page: int = Field(default=1, description="Last page number")

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "GuruRealtimePicksResponse":
        """Create GuruRealtimePicksResponse from API response.

        Args:
            data: Raw JSON response - {"data": [...], "total": N, "currentPage": "1", "lastPage": N}

        Returns:
            Populated GuruRealtimePicksResponse instance
        """
        picks_raw = data.get("data", [])
        picks = [_parse_realtime_pick_item(p) for p in picks_raw if isinstance(p, dict)]

        return cls(
            picks=picks,
            total=int(data.get("total", len(picks))),
            current_page=int(data.get("currentPage", 1)),
            last_page=int(data.get("lastPage", 1)),
        )


def _parse_realtime_pick_item(data: dict[str, Any]) -> GuruRealtimePickItem:
    """Parse a single realtime pick item from API data."""
    return GuruRealtimePickItem(
        symbol=data.get("symbol", ""),
        company=data.get("company"),
        exchange=data.get("exchange"),
        guru_name=data.get("guru_name"),
        action=data.get("action"),
        comment=data.get("comment"),
        date=data.get("portdate"),
        shares=_get_int(data, "shares"),
        price=_get_float(data, "price"),
        price_avg=_get_float(data, "price_avg"),
        change_pct=_get_float(data, "change"),
        impact=_get_float(data, "impact"),
        currency=data.get("currency"),
    )


# --- Models for other guru endpoints (guru portfolios, etc.) ---


class GuruInfo(BaseModel):
    """Information about a guru/institutional investor."""

    guru_id: str = Field(description="Unique identifier for the guru")
    name: str = Field(description="Guru or firm name")
    firm: str | None = Field(default=None, description="Investment firm name")

    # Portfolio statistics
    portfolio_value: float | None = Field(default=None, description="Total portfolio value in USD")
    num_holdings: int | None = Field(default=None, description="Number of holdings")
    turnover: float | None = Field(default=None, description="Portfolio turnover rate (%)")

    # Performance
    avg_return: float | None = Field(default=None, description="Average annual return (%)")

    # Metadata
    last_updated: str | None = Field(default=None, description="Date of last portfolio update")
    profile_url: str | None = Field(default=None, description="URL to guru profile on GuruFocus")


class GuruList(BaseModel):
    """List of tracked gurus."""

    gurus: list[GuruInfo] = Field(default_factory=list, description="List of gurus")
    total_count: int = Field(default=0, description="Total number of gurus")

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "GuruList":
        """Create GuruList from API response.

        Args:
            data: Raw JSON response from the API

        Returns:
            Populated GuruList instance
        """
        gurus_data = data.get("gurus", data.get("data", []))
        if isinstance(gurus_data, dict):
            gurus_data = [gurus_data]

        gurus = [_parse_guru_info(g) for g in gurus_data]

        return cls(
            gurus=gurus,
            total_count=len(gurus),
        )


class GuruHolding(BaseModel):
    """A single stock holding in a guru's portfolio."""

    symbol: str = Field(description="Stock ticker symbol")
    company_name: str | None = Field(default=None, description="Company name")

    # Position details
    shares: int | None = Field(default=None, description="Number of shares held")
    value: float | None = Field(default=None, description="Position value in USD")
    weight: float | None = Field(default=None, description="Position weight in portfolio (%)")
    price: float | None = Field(default=None, description="Current stock price")
    avg_price: float | None = Field(default=None, description="Average purchase price")

    # Changes
    change_shares: int | None = Field(
        default=None, description="Change in shares from last quarter"
    )
    change_pct: float | None = Field(default=None, description="Percentage change in position (%)")

    # Timing
    quarter_first_bought: str | None = Field(
        default=None, description="Quarter first purchased (e.g., 'Q1 2020')"
    )
    quarters_held: int | None = Field(default=None, description="Number of quarters held")

    # Valuation
    pe_ratio: float | None = Field(default=None, description="P/E ratio")
    gf_value: float | None = Field(default=None, description="GF Value estimate")


class GuruPicks(BaseModel):
    """A guru's portfolio holdings."""

    guru_id: str = Field(description="Unique identifier for the guru")
    guru_name: str = Field(description="Guru or firm name")

    # Portfolio summary
    portfolio_date: str | None = Field(default=None, description="Date of portfolio snapshot")
    total_value: float | None = Field(default=None, description="Total portfolio value in USD")
    num_holdings: int | None = Field(default=None, description="Number of holdings")

    # Holdings
    holdings: list[GuruHolding] = Field(
        default_factory=list, description="List of holdings (largest positions first)"
    )

    @classmethod
    def from_api_response(cls, data: dict[str, Any], guru_id: str) -> "GuruPicks":
        """Create GuruPicks from API response.

        Args:
            data: Raw JSON response from the API
            guru_id: Guru identifier

        Returns:
            Populated GuruPicks instance
        """
        portfolio_data = data.get("portfolio", data)

        # Parse holdings
        holdings_raw = portfolio_data.get("holdings", portfolio_data.get("picks", []))
        if isinstance(holdings_raw, dict):
            holdings_raw = list(holdings_raw.values()) if holdings_raw else []

        holdings = [_parse_guru_holding(h) for h in holdings_raw]

        return cls(
            guru_id=guru_id,
            guru_name=portfolio_data.get("guru_name", portfolio_data.get("name", guru_id)),
            portfolio_date=portfolio_data.get("portfolio_date", portfolio_data.get("date")),
            total_value=_get_float(portfolio_data, "total_value", "portfolioValue", "value"),
            num_holdings=len(holdings),
            holdings=holdings,
        )


class GuruTrade(BaseModel):
    """A single trade by a guru."""

    symbol: str = Field(description="Stock ticker symbol")
    company_name: str | None = Field(default=None, description="Company name")

    # Trade details
    action: str = Field(description="Trade action (Buy, Sell, Add, Reduce)")
    shares: int | None = Field(default=None, description="Number of shares traded")
    value: float | None = Field(default=None, description="Trade value in USD")
    price: float | None = Field(default=None, description="Trade price per share")

    # Position impact
    change_pct: float | None = Field(default=None, description="Position change percentage (%)")
    current_shares: int | None = Field(default=None, description="Shares held after trade")
    portfolio_weight: float | None = Field(default=None, description="New portfolio weight (%)")

    # Timing
    trade_date: str | None = Field(default=None, description="Date of trade")
    quarter: str | None = Field(default=None, description="Quarter of trade")
    filing_date: str | None = Field(default=None, description="SEC filing date")


class GuruTrades(BaseModel):
    """Recent trades by a guru."""

    guru_id: str = Field(description="Unique identifier for the guru")
    guru_name: str = Field(description="Guru or firm name")

    # Trade summary
    total_buys: int = Field(default=0, description="Number of buy transactions")
    total_sells: int = Field(default=0, description="Number of sell transactions")

    # Trades list
    trades: list[GuruTrade] = Field(default_factory=list, description="List of recent trades")

    @classmethod
    def from_api_response(cls, data: dict[str, Any], guru_id: str) -> "GuruTrades":
        """Create GuruTrades from API response.

        Args:
            data: Raw JSON response from the API
            guru_id: Guru identifier

        Returns:
            Populated GuruTrades instance
        """
        trades_data = data.get("trades", data.get("transactions", data))

        # Parse trades list
        trades_raw = trades_data if isinstance(trades_data, list) else trades_data.get("trades", [])
        trades = [_parse_guru_trade(t) for t in trades_raw]

        # Count buys and sells
        buys = sum(1 for t in trades if t.action.lower() in ("buy", "add", "new"))
        sells = sum(1 for t in trades if t.action.lower() in ("sell", "reduce", "sold"))

        return cls(
            guru_id=guru_id,
            guru_name=data.get("guru_name", data.get("name", guru_id)),
            total_buys=buys,
            total_sells=sells,
            trades=trades,
        )


class StockGuruHolder(BaseModel):
    """A guru who holds a specific stock."""

    guru_id: str = Field(description="Unique identifier for the guru")
    guru_name: str = Field(description="Guru or firm name")

    # Position details
    shares: int | None = Field(default=None, description="Number of shares held")
    value: float | None = Field(default=None, description="Position value in USD")
    portfolio_weight: float | None = Field(
        default=None, description="Weight in guru's portfolio (%)"
    )

    # Changes
    change_shares: int | None = Field(
        default=None, description="Change in shares from last quarter"
    )
    change_pct: float | None = Field(default=None, description="Percentage change in position (%)")
    action: str | None = Field(
        default=None, description="Recent action (Buy, Sell, Hold, New, Sold Out)"
    )

    # Timing
    quarter_first_bought: str | None = Field(default=None, description="Quarter first purchased")
    quarters_held: int | None = Field(default=None, description="Number of quarters held")


class StockGurus(BaseModel):
    """Gurus who hold a specific stock."""

    symbol: str = Field(description="Stock ticker symbol")
    company_name: str | None = Field(default=None, description="Company name")

    # Summary
    total_guru_holders: int = Field(default=0, description="Number of guru holders")
    total_shares_held: int | None = Field(default=None, description="Total shares held by gurus")
    total_value: float | None = Field(default=None, description="Total value held by gurus")

    # Recent activity
    new_positions: int = Field(default=0, description="New positions this quarter")
    increased_positions: int = Field(default=0, description="Increased positions this quarter")
    decreased_positions: int = Field(default=0, description="Decreased positions this quarter")
    sold_out: int = Field(default=0, description="Sold out positions this quarter")

    # Holders list
    holders: list[StockGuruHolder] = Field(default_factory=list, description="List of guru holders")

    @classmethod
    def from_api_response(cls, data: dict[str, Any], symbol: str) -> "StockGurus":
        """Create StockGurus from API response.

        Args:
            data: Raw JSON response from the API
            symbol: Stock ticker symbol

        Returns:
            Populated StockGurus instance
        """
        gurus_data = data.get("gurus", data.get("holders", data))

        # Parse holders list
        holders_raw = gurus_data if isinstance(gurus_data, list) else gurus_data.get("holders", [])
        holders = [_parse_stock_guru_holder(h) for h in holders_raw]

        # Count activity
        new_positions = sum(1 for h in holders if h.action and h.action.lower() == "new")
        increased = sum(1 for h in holders if h.action and h.action.lower() in ("buy", "add"))
        decreased = sum(1 for h in holders if h.action and h.action.lower() in ("sell", "reduce"))
        sold_out = sum(1 for h in holders if h.action and h.action.lower() in ("sold out", "sold"))

        # Calculate totals
        total_shares = sum(h.shares or 0 for h in holders)
        total_value = sum(h.value or 0 for h in holders)

        return cls(
            symbol=symbol,
            company_name=data.get("company_name", data.get("company")),
            total_guru_holders=len(holders),
            total_shares_held=total_shares if total_shares > 0 else None,
            total_value=total_value if total_value > 0 else None,
            new_positions=new_positions,
            increased_positions=increased,
            decreased_positions=decreased,
            sold_out=sold_out,
            holders=holders,
        )


# --- Helper Functions ---


def _parse_guru_info(data: dict[str, Any]) -> GuruInfo:
    """Parse a single guru info from API data."""
    return GuruInfo(
        guru_id=str(data.get("guru_id", data.get("id", data.get("guruId", "")))),
        name=data.get("name", data.get("guru_name", data.get("guruName", "Unknown"))),
        firm=data.get("firm", data.get("company")),
        portfolio_value=_get_float(data, "portfolio_value", "portfolioValue", "value"),
        num_holdings=_get_int(data, "num_holdings", "numHoldings", "holdings_count"),
        turnover=_get_float(data, "turnover", "turnoverRate"),
        avg_return=_get_float(data, "avg_return", "avgReturn", "return"),
        last_updated=data.get("last_updated", data.get("lastUpdated", data.get("date"))),
        profile_url=data.get("profile_url", data.get("url")),
    )


def _parse_guru_holding(data: dict[str, Any]) -> GuruHolding:
    """Parse a single guru holding from API data."""
    return GuruHolding(
        symbol=data.get("symbol", data.get("ticker", "")),
        company_name=data.get("company_name", data.get("company", data.get("name"))),
        shares=_get_int(data, "shares", "current_shares", "currentShares"),
        value=_get_float(data, "value", "market_value", "marketValue"),
        weight=_get_float(data, "weight", "portfolio_weight", "portfolioWeight", "pct"),
        price=_get_float(data, "price", "current_price", "currentPrice"),
        avg_price=_get_float(data, "avg_price", "avgPrice", "average_price"),
        change_shares=_get_int(data, "change_shares", "changeShares", "shares_change"),
        change_pct=_get_float(data, "change_pct", "changePct", "change_percent"),
        quarter_first_bought=data.get("quarter_first_bought", data.get("firstBought")),
        quarters_held=_get_int(data, "quarters_held", "quartersHeld"),
        pe_ratio=_get_float(data, "pe_ratio", "pe", "peRatio"),
        gf_value=_get_float(data, "gf_value", "gfValue"),
    )


def _parse_guru_trade(data: dict[str, Any]) -> GuruTrade:
    """Parse a single guru trade from API data."""
    # Determine action
    action = data.get("action", data.get("type", data.get("transaction_type", "Unknown")))
    if not action or action == "Unknown":
        # Infer from shares change
        change = _get_int(data, "change_shares", "shares")
        if change is not None:
            action = "Buy" if change > 0 else "Sell" if change < 0 else "Hold"

    return GuruTrade(
        symbol=data.get("symbol", data.get("ticker", "")),
        company_name=data.get("company_name", data.get("company", data.get("name"))),
        action=action,
        shares=abs(_get_int(data, "shares", "change_shares", "tradeShares") or 0) or None,
        value=_get_float(data, "value", "trade_value", "tradeValue"),
        price=_get_float(data, "price", "trade_price", "tradePrice"),
        change_pct=_get_float(data, "change_pct", "changePct", "impact"),
        current_shares=_get_int(data, "current_shares", "currentShares", "shares_after"),
        portfolio_weight=_get_float(data, "portfolio_weight", "weight", "portfolioWeight"),
        trade_date=data.get("trade_date", data.get("date", data.get("tradeDate"))),
        quarter=data.get("quarter", data.get("period")),
        filing_date=data.get("filing_date", data.get("filingDate")),
    )


def _parse_stock_guru_holder(data: dict[str, Any]) -> StockGuruHolder:
    """Parse a single stock guru holder from API data."""
    return StockGuruHolder(
        guru_id=str(data.get("guru_id", data.get("id", data.get("guruId", "")))),
        guru_name=data.get("guru_name", data.get("name", data.get("guruName", "Unknown"))),
        shares=_get_int(data, "shares", "current_shares", "currentShares"),
        value=_get_float(data, "value", "market_value", "marketValue"),
        portfolio_weight=_get_float(data, "portfolio_weight", "weight", "portfolioWeight"),
        change_shares=_get_int(data, "change_shares", "changeShares", "shares_change"),
        change_pct=_get_float(data, "change_pct", "changePct", "change_percent"),
        action=data.get("action", data.get("activity", data.get("change_type"))),
        quarter_first_bought=data.get("quarter_first_bought", data.get("firstBought")),
        quarters_held=_get_int(data, "quarters_held", "quartersHeld"),
    )


def _get_float(data: dict[str, Any], *keys: str) -> float | None:
    """Get a float value from dict, trying multiple possible keys."""
    for key in keys:
        value = data.get(key)
        if value is not None:
            try:
                return float(value)
            except (TypeError, ValueError):
                continue
    return None


def _get_int(data: dict[str, Any], *keys: str) -> int | None:
    """Get an int value from dict, trying multiple possible keys."""
    for key in keys:
        value = data.get(key)
        if value is not None:
            try:
                return int(float(value))
            except (TypeError, ValueError):
                continue
    return None
