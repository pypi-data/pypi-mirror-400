"""Cache configuration with three-tier TTL strategy.

Financial data has different freshness requirements:
- Price-dependent data changes daily with stock prices
- Earnings-dependent data changes quarterly after earnings reports
- Static data rarely changes (company info, sector, etc.)

This module defines the cache tiers and TTL configuration for each
type of data to optimize API usage while keeping data fresh.
"""

from dataclasses import dataclass
from datetime import timedelta
from enum import Enum


class CacheTier(Enum):
    """Cache tier based on data freshness requirements.

    PRICE_DEPENDENT: Changes with stock price (P/E, market cap, etc.)
    EARNINGS_DEPENDENT: Changes quarterly after earnings reports
    STATIC: Rarely changes (company profile, sector, etc.)
    """

    PRICE_DEPENDENT = "price_dependent"
    EARNINGS_DEPENDENT = "earnings_dependent"
    STATIC = "static"


class CacheCategory(Enum):
    """Categories of cached data mapped to API endpoints."""

    # Price-dependent (refresh daily or more frequently)
    QUOTE = "quote"
    VALUATION_RATIOS = "valuation_ratios"
    MARKET_DATA = "market_data"
    PRICE_HISTORY = "price_history"
    PRICE_OHLC = "price_ohlc"
    VOLUME = "volume"
    UNADJUSTED_PRICE = "unadjusted_price"

    # Price-dependent (short TTL as it changes with stock price)
    CURRENT_DIVIDEND = "current_dividend"

    # Earnings-dependent (refresh quarterly or after earnings)
    SUMMARY = "summary"
    FINANCIALS = "financials"
    KEY_RATIOS = "key_ratios"
    FUNDAMENTAL_RATIOS = "fundamental_ratios"
    GROWTH_METRICS = "growth_metrics"
    ESTIMATES = "estimates"
    GF_SCORE = "gf_score"
    DIVIDENDS = "dividends"
    INSIDERS = "insiders"

    # Insider activity (refresh daily as new SEC filings arrive)
    INSIDER_UPDATES = "insider_updates"
    INSIDER_CEO_BUYS = "insider_ceo_buys"
    INSIDER_CFO_BUYS = "insider_cfo_buys"
    INSIDER_CLUSTER_BUY = "insider_cluster_buy"
    INSIDER_DOUBLE = "insider_double"
    INSIDER_TRIPLE = "insider_triple"
    INSIDER_LIST = "insider_list"

    # Operating & segment data (earnings-dependent, refresh quarterly)
    OPERATING_DATA = "operating_data"
    SEGMENTS_DATA = "segments_data"

    # Ownership & indicators
    OWNERSHIP = "ownership"
    INDICATOR_HISTORY = "indicator_history"
    INDICATORS_LIST = "indicators_list"
    INDICATOR_VALUE = "indicator_value"

    # Static (refresh monthly)
    PROFILE = "profile"
    GURUS = "gurus"
    GURU_LIST = "guru_list"
    GURU_PICKS = "guru_picks"
    GURU_AGGREGATED = "guru_aggregated"
    GURU_REALTIME_PICKS = "guru_realtime_picks"
    EXECUTIVES = "executives"
    TRADES_HISTORY = "trades_history"

    # Politician data
    POLITICIANS_LIST = "politicians_list"
    POLITICIAN_TRANSACTIONS = "politician_transactions"

    # Reference data (exchanges and indexes)
    EXCHANGE_LIST = "exchange_list"
    EXCHANGE_STOCKS = "exchange_stocks"
    INDEX_LIST = "index_list"
    INDEX_STOCKS = "index_stocks"

    # Economic data
    ECONOMIC_INDICATORS_LIST = "economic_indicators_list"
    ECONOMIC_INDICATOR_ITEM = "economic_indicator_item"
    CALENDAR = "calendar"

    # News feed
    NEWS_FEED = "news_feed"

    # Estimate history
    ESTIMATE_HISTORY = "estimate_history"

    # ETF data
    ETF_LIST = "etf_list"
    ETF_SECTOR_WEIGHTING = "etf_sector_weighting"

    # User/Personal data
    API_USAGE = "api_usage"
    USER_SCREENERS = "user_screeners"
    USER_SCREENER_RESULTS = "user_screener_results"
    PORTFOLIOS = "portfolios"
    PORTFOLIO_DETAIL = "portfolio_detail"

    # Misc reference data
    COUNTRY_CURRENCY = "country_currency"
    FUNDA_UPDATED = "funda_updated"


@dataclass(frozen=True)
class CacheConfig:
    """Configuration for a cache category."""

    tier: CacheTier
    ttl: timedelta
    invalidate_on_earnings: bool = False


# Default TTL configurations for each category
_CACHE_CONFIGS: dict[CacheCategory, CacheConfig] = {
    # TIER 1: Price-Dependent (daily refresh)
    CacheCategory.QUOTE: CacheConfig(
        tier=CacheTier.PRICE_DEPENDENT,
        ttl=timedelta(minutes=15),
    ),
    CacheCategory.VALUATION_RATIOS: CacheConfig(
        tier=CacheTier.PRICE_DEPENDENT,
        ttl=timedelta(days=1),
    ),
    CacheCategory.MARKET_DATA: CacheConfig(
        tier=CacheTier.PRICE_DEPENDENT,
        ttl=timedelta(days=1),
    ),
    # TIER 2: Earnings-Dependent (quarterly, invalidate after earnings)
    CacheCategory.SUMMARY: CacheConfig(
        tier=CacheTier.EARNINGS_DEPENDENT,
        ttl=timedelta(days=1),  # Summary includes price data, so daily
        invalidate_on_earnings=True,
    ),
    CacheCategory.FINANCIALS: CacheConfig(
        tier=CacheTier.EARNINGS_DEPENDENT,
        ttl=timedelta(days=95),  # ~quarterly
        invalidate_on_earnings=True,
    ),
    CacheCategory.KEY_RATIOS: CacheConfig(
        tier=CacheTier.EARNINGS_DEPENDENT,
        ttl=timedelta(days=95),
        invalidate_on_earnings=True,
    ),
    CacheCategory.FUNDAMENTAL_RATIOS: CacheConfig(
        tier=CacheTier.EARNINGS_DEPENDENT,
        ttl=timedelta(days=95),
        invalidate_on_earnings=True,
    ),
    CacheCategory.GROWTH_METRICS: CacheConfig(
        tier=CacheTier.EARNINGS_DEPENDENT,
        ttl=timedelta(days=95),
        invalidate_on_earnings=True,
    ),
    CacheCategory.ESTIMATES: CacheConfig(
        tier=CacheTier.EARNINGS_DEPENDENT,
        ttl=timedelta(days=7),
        invalidate_on_earnings=True,
    ),
    CacheCategory.GF_SCORE: CacheConfig(
        tier=CacheTier.EARNINGS_DEPENDENT,
        ttl=timedelta(days=1),  # GF Score can change with price
        invalidate_on_earnings=True,
    ),
    CacheCategory.DIVIDENDS: CacheConfig(
        tier=CacheTier.EARNINGS_DEPENDENT,
        ttl=timedelta(days=30),  # Dividend data changes infrequently
        invalidate_on_earnings=True,
    ),
    CacheCategory.INSIDERS: CacheConfig(
        tier=CacheTier.EARNINGS_DEPENDENT,
        ttl=timedelta(days=7),  # Insider trades filed within days
    ),
    # Insider activity endpoints (daily refresh for fresh SEC filings)
    CacheCategory.INSIDER_UPDATES: CacheConfig(
        tier=CacheTier.EARNINGS_DEPENDENT,
        ttl=timedelta(days=1),  # New updates arrive daily
    ),
    CacheCategory.INSIDER_CEO_BUYS: CacheConfig(
        tier=CacheTier.EARNINGS_DEPENDENT,
        ttl=timedelta(days=1),  # CEO buys are time-sensitive signals
    ),
    CacheCategory.INSIDER_CFO_BUYS: CacheConfig(
        tier=CacheTier.EARNINGS_DEPENDENT,
        ttl=timedelta(days=1),  # CFO buys are time-sensitive signals
    ),
    CacheCategory.INSIDER_CLUSTER_BUY: CacheConfig(
        tier=CacheTier.EARNINGS_DEPENDENT,
        ttl=timedelta(days=1),  # Cluster buys are time-sensitive signals
    ),
    CacheCategory.INSIDER_DOUBLE: CacheConfig(
        tier=CacheTier.EARNINGS_DEPENDENT,
        ttl=timedelta(days=1),  # Double-down buys are time-sensitive signals
    ),
    CacheCategory.INSIDER_TRIPLE: CacheConfig(
        tier=CacheTier.EARNINGS_DEPENDENT,
        ttl=timedelta(days=1),  # Triple-down buys are time-sensitive signals
    ),
    CacheCategory.INSIDER_LIST: CacheConfig(
        tier=CacheTier.STATIC,
        ttl=timedelta(days=7),  # Insider list changes infrequently
    ),
    CacheCategory.PRICE_HISTORY: CacheConfig(
        tier=CacheTier.PRICE_DEPENDENT,
        ttl=timedelta(days=1),  # Price data updates daily
    ),
    CacheCategory.PRICE_OHLC: CacheConfig(
        tier=CacheTier.PRICE_DEPENDENT,
        ttl=timedelta(days=1),  # OHLC data updates daily
    ),
    CacheCategory.VOLUME: CacheConfig(
        tier=CacheTier.PRICE_DEPENDENT,
        ttl=timedelta(days=1),  # Volume data updates daily
    ),
    CacheCategory.UNADJUSTED_PRICE: CacheConfig(
        tier=CacheTier.PRICE_DEPENDENT,
        ttl=timedelta(days=1),  # Unadjusted prices update daily
    ),
    CacheCategory.CURRENT_DIVIDEND: CacheConfig(
        tier=CacheTier.PRICE_DEPENDENT,
        ttl=timedelta(days=1),  # Yield changes with price
    ),
    # TIER 3: Static (monthly+)
    CacheCategory.PROFILE: CacheConfig(
        tier=CacheTier.STATIC,
        ttl=timedelta(days=30),
    ),
    CacheCategory.GURUS: CacheConfig(
        tier=CacheTier.STATIC,
        ttl=timedelta(days=14),
    ),
    CacheCategory.GURU_LIST: CacheConfig(
        tier=CacheTier.STATIC,
        ttl=timedelta(days=7),  # Large dataset, cache longer
    ),
    CacheCategory.GURU_PICKS: CacheConfig(
        tier=CacheTier.EARNINGS_DEPENDENT,
        ttl=timedelta(days=1),  # Guru picks update with SEC filings
    ),
    CacheCategory.GURU_AGGREGATED: CacheConfig(
        tier=CacheTier.EARNINGS_DEPENDENT,
        ttl=timedelta(days=1),  # Aggregated portfolio updates with filings
    ),
    CacheCategory.GURU_REALTIME_PICKS: CacheConfig(
        tier=CacheTier.PRICE_DEPENDENT,
        ttl=timedelta(minutes=15),  # Real-time activity, short TTL
    ),
    CacheCategory.EXECUTIVES: CacheConfig(
        tier=CacheTier.STATIC,
        ttl=timedelta(days=30),
    ),
    CacheCategory.TRADES_HISTORY: CacheConfig(
        tier=CacheTier.STATIC,
        ttl=timedelta(days=7),  # Guru trades update with SEC filings
    ),
    # Operating & segment data (earnings-dependent)
    CacheCategory.OPERATING_DATA: CacheConfig(
        tier=CacheTier.EARNINGS_DEPENDENT,
        ttl=timedelta(days=1),  # Refresh daily for operational metrics
        invalidate_on_earnings=True,
    ),
    CacheCategory.SEGMENTS_DATA: CacheConfig(
        tier=CacheTier.EARNINGS_DEPENDENT,
        ttl=timedelta(days=1),  # Refresh daily for segment data
        invalidate_on_earnings=True,
    ),
    # Ownership & indicators
    CacheCategory.OWNERSHIP: CacheConfig(
        tier=CacheTier.EARNINGS_DEPENDENT,
        ttl=timedelta(days=7),  # Ownership updates with SEC filings
    ),
    CacheCategory.INDICATOR_HISTORY: CacheConfig(
        tier=CacheTier.EARNINGS_DEPENDENT,
        ttl=timedelta(days=7),  # Historical ownership updates with SEC filings
    ),
    CacheCategory.INDICATORS_LIST: CacheConfig(
        tier=CacheTier.STATIC,
        ttl=timedelta(days=30),  # List of indicators rarely changes
    ),
    CacheCategory.INDICATOR_VALUE: CacheConfig(
        tier=CacheTier.EARNINGS_DEPENDENT,
        ttl=timedelta(days=1),  # Individual indicator values may change daily
        invalidate_on_earnings=True,
    ),
    # Politician data
    CacheCategory.POLITICIANS_LIST: CacheConfig(
        tier=CacheTier.STATIC,
        ttl=timedelta(days=7),  # Politicians list changes infrequently
    ),
    CacheCategory.POLITICIAN_TRANSACTIONS: CacheConfig(
        tier=CacheTier.EARNINGS_DEPENDENT,
        ttl=timedelta(days=1),  # Transactions update with SEC filings
    ),
    # Reference data (exchanges and indexes)
    CacheCategory.EXCHANGE_LIST: CacheConfig(
        tier=CacheTier.STATIC,
        ttl=timedelta(days=30),  # Exchange list rarely changes
    ),
    CacheCategory.EXCHANGE_STOCKS: CacheConfig(
        tier=CacheTier.STATIC,
        ttl=timedelta(days=7),  # Stock listings update occasionally
    ),
    CacheCategory.INDEX_LIST: CacheConfig(
        tier=CacheTier.STATIC,
        ttl=timedelta(days=30),  # Index list rarely changes
    ),
    CacheCategory.INDEX_STOCKS: CacheConfig(
        tier=CacheTier.STATIC,
        ttl=timedelta(days=7),  # Index constituents change occasionally
    ),
    # Economic data
    CacheCategory.ECONOMIC_INDICATORS_LIST: CacheConfig(
        tier=CacheTier.STATIC,
        ttl=timedelta(days=30),  # List of indicators rarely changes
    ),
    CacheCategory.ECONOMIC_INDICATOR_ITEM: CacheConfig(
        tier=CacheTier.EARNINGS_DEPENDENT,
        ttl=timedelta(days=1),  # Economic data updates regularly
    ),
    CacheCategory.CALENDAR: CacheConfig(
        tier=CacheTier.PRICE_DEPENDENT,
        ttl=timedelta(hours=1),  # Calendar data changes frequently
    ),
    # News feed
    CacheCategory.NEWS_FEED: CacheConfig(
        tier=CacheTier.PRICE_DEPENDENT,
        ttl=timedelta(minutes=15),  # News updates frequently
    ),
    # Estimate history
    CacheCategory.ESTIMATE_HISTORY: CacheConfig(
        tier=CacheTier.EARNINGS_DEPENDENT,
        ttl=timedelta(days=7),  # Estimates update with earnings
        invalidate_on_earnings=True,
    ),
    # ETF data
    CacheCategory.ETF_LIST: CacheConfig(
        tier=CacheTier.STATIC,
        ttl=timedelta(days=7),  # ETF list changes infrequently
    ),
    CacheCategory.ETF_SECTOR_WEIGHTING: CacheConfig(
        tier=CacheTier.STATIC,
        ttl=timedelta(days=7),  # Sector allocations change infrequently
    ),
    # User/Personal data
    CacheCategory.API_USAGE: CacheConfig(
        tier=CacheTier.PRICE_DEPENDENT,
        ttl=timedelta(minutes=5),  # Very short TTL for quota tracking
    ),
    CacheCategory.USER_SCREENERS: CacheConfig(
        tier=CacheTier.STATIC,
        ttl=timedelta(hours=1),  # Screeners update infrequently
    ),
    CacheCategory.USER_SCREENER_RESULTS: CacheConfig(
        tier=CacheTier.EARNINGS_DEPENDENT,
        ttl=timedelta(hours=1),  # Screener results change with market data
    ),
    CacheCategory.PORTFOLIOS: CacheConfig(
        tier=CacheTier.PRICE_DEPENDENT,
        ttl=timedelta(minutes=5),  # Portfolio values change with prices
    ),
    CacheCategory.PORTFOLIO_DETAIL: CacheConfig(
        tier=CacheTier.PRICE_DEPENDENT,
        ttl=timedelta(minutes=5),  # Portfolio holdings change with prices
    ),
    # Misc reference data
    CacheCategory.COUNTRY_CURRENCY: CacheConfig(
        tier=CacheTier.STATIC,
        ttl=timedelta(days=30),  # Currency codes rarely change
    ),
    CacheCategory.FUNDA_UPDATED: CacheConfig(
        tier=CacheTier.EARNINGS_DEPENDENT,
        ttl=timedelta(days=1),  # List of updated fundamentals for date
    ),
}


def get_cache_config(category: CacheCategory) -> CacheConfig:
    """Get cache configuration for a category.

    Args:
        category: The cache category to look up

    Returns:
        CacheConfig with tier, TTL, and invalidation settings
    """
    return _CACHE_CONFIGS[category]


def get_ttl_seconds(category: CacheCategory) -> int:
    """Get TTL in seconds for a cache category.

    Args:
        category: The cache category

    Returns:
        TTL in seconds
    """
    config = get_cache_config(category)
    return int(config.ttl.total_seconds())


def build_cache_key(category: CacheCategory, *parts: str) -> str:
    """Build a cache key from category and parts.

    Args:
        category: The cache category
        *parts: Additional key parts (e.g., symbol)

    Returns:
        Cache key string like "summary:AAPL"

    Example:
        >>> build_cache_key(CacheCategory.SUMMARY, "AAPL")
        "summary:AAPL"
        >>> build_cache_key(CacheCategory.FINANCIALS, "AAPL", "annual")
        "financials:AAPL:annual"
    """
    return ":".join([category.value, *parts])


# Metrics classification for reference
PRICE_DEPENDENT_METRICS = {
    "pe_ratio",
    "ps_ratio",
    "pb_ratio",
    "peg_ratio",
    "ev_ebitda",
    "ev_sales",
    "ev_fcf",
    "market_cap",
    "enterprise_value",
    "dividend_yield",
    "discount_to_gf_value",
    "discount_to_dcf",
    "momentum_score",
    "valuation_rank",
    "current_price",
}

EARNINGS_DEPENDENT_METRICS = {
    "eps",
    "revenue_per_share",
    "fcf_per_share",
    "book_value_per_share",
    "roe",
    "roic",
    "roa",
    "roce",
    "gross_margin",
    "operating_margin",
    "net_margin",
    "fcf_margin",
    "revenue_growth_yoy",
    "eps_growth_yoy",
    "debt_to_equity",
    "current_ratio",
    "piotroski_score",
}

STATIC_METRICS = {
    "company_name",
    "sector",
    "industry",
    "exchange",
    "currency",
    "description",
}
