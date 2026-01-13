"""Model factories for generating test data.

Uses polyfactory to generate realistic test data from Pydantic models.
This eliminates the need for static JSON fixtures that require maintenance.

Usage:
    from tests_api.factories import StockSummaryFactory, KeyRatiosFactory

    # Generate a single instance
    summary = StockSummaryFactory.build()

    # Generate with specific overrides
    summary = StockSummaryFactory.build(symbol="AAPL")

    # Generate as dict (for mocking API responses)
    data = StockSummaryFactory.build().model_dump(mode="json", exclude_none=True)

    # Use specialized factories for specific scenarios
    distressed = DistressedCompanyKeyRatiosFactory.build()
    healthy = HealthyCompanyKeyRatiosFactory.build()
"""

from __future__ import annotations

import random

from polyfactory.factories.pydantic_factory import ModelFactory

from gurufocus_api.models.etf import (
    ETFInfo,
    ETFListResponse,
    ETFSectorWeightingResponse,
    IndustryWeighting,
    SectorWeighting,
)
from gurufocus_api.models.gurus import (
    GuruListItem,
    GuruListResponse,
    StockGuruHolding,
    StockGuruPick,
    StockGurusResponse,
)
from gurufocus_api.models.keyratios import (
    GrowthRatios,
    KeyRatios,
    LiquidityRatios,
    PriceMetrics,
    ProfitabilityRatios,
    SolvencyRatios,
    ValuationRatios,
)
from gurufocus_api.models.quote import StockQuote
from gurufocus_api.models.summary import (
    FinancialRatios,
    GeneralInfo,
    InstitutionalActivity,
    PriceInfo,
    QualityScores,
    RatioHistory,
    RatioIndustry,
    RatioValue,
    StockSummary,
    ValuationMetrics,
)

# =============================================================================
# Helper functions for realistic fake data
# =============================================================================


def fake_company_name() -> str:
    """Generate a fake company name."""
    prefixes = ["Fake", "Test", "Mock", "Sample", "Demo"]
    suffixes = ["Corp", "Industries", "Holdings", "Technologies", "Inc"]
    types = ["Alpha", "Beta", "Gamma", "Delta", "Omega"]
    return f"{random.choice(prefixes)}{random.choice(types)} {random.choice(suffixes)}"


def fake_sector() -> str:
    """Generate a fake sector name."""
    sectors = [
        "Technology",
        "Healthcare",
        "Financial Services",
        "Consumer Cyclical",
        "Communication Services",
        "Industrials",
        "Consumer Defensive",
        "Energy",
        "Utilities",
        "Real Estate",
        "Basic Materials",
    ]
    return random.choice(sectors)


def fake_industry() -> str:
    """Generate a fake industry name."""
    industries = [
        "Software - Application",
        "Semiconductors",
        "Biotechnology",
        "Banks - Regional",
        "Internet Content & Information",
        "Aerospace & Defense",
        "Drug Manufacturers",
        "Auto Manufacturers",
        "Oil & Gas E&P",
        "REIT - Diversified",
    ]
    return random.choice(industries)


def fake_exchange() -> str:
    """Generate a fake exchange code."""
    return random.choice(["NYSE", "NAS", "AMEX", "OTC"])


def fake_date() -> str:
    """Generate a fake date string."""
    year = random.randint(2023, 2025)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year}-{month:02d}-{day:02d}"


# =============================================================================
# Summary Model Factories
# =============================================================================


class GeneralInfoFactory(ModelFactory):
    """Factory for GeneralInfo model."""

    __model__ = GeneralInfo

    @classmethod
    def company_name(cls) -> str:
        return fake_company_name()

    @classmethod
    def current_price(cls) -> float:
        return round(random.uniform(10.0, 500.0), 2)

    @classmethod
    def currency(cls) -> str:
        return "$"

    @classmethod
    def country(cls) -> str:
        return random.choice(["USA", "CAN", "GBR", "DEU", "JPN"])

    @classmethod
    def exchange(cls) -> str:
        return fake_exchange()

    @classmethod
    def sector(cls) -> str:
        return fake_sector()

    @classmethod
    def industry(cls) -> str:
        return fake_industry()

    @classmethod
    def market_cap(cls) -> float:
        # Market cap in millions
        return round(random.uniform(1000.0, 500000.0), 2)

    @classmethod
    def description(cls) -> str:
        return "A fictional company used for testing purposes."

    @classmethod
    def short_description(cls) -> str:
        return "Fictional test company"


class QualityScoresFactory(ModelFactory):
    """Factory for QualityScores model."""

    __model__ = QualityScores

    @classmethod
    def gf_score(cls) -> int:
        return random.randint(30, 95)

    @classmethod
    def financial_strength(cls) -> int:
        return random.randint(3, 10)

    @classmethod
    def profitability_rank(cls) -> int:
        return random.randint(3, 10)

    @classmethod
    def growth_rank(cls) -> int:
        return random.randint(3, 10)

    @classmethod
    def gf_value_rank(cls) -> int:
        return random.randint(3, 10)

    @classmethod
    def momentum_rank(cls) -> int:
        return random.randint(3, 10)

    @classmethod
    def risk_assessment(cls) -> str:
        return random.choice(["Low Risk", "Medium Risk", "High Risk"])

    @classmethod
    def valuation_status(cls) -> str:
        return random.choice(
            [
                "Significantly Undervalued",
                "Modestly Undervalued",
                "Fairly Valued",
                "Modestly Overvalued",
            ]
        )


class ValuationMetricsFactory(ModelFactory):
    """Factory for ValuationMetrics model."""

    __model__ = ValuationMetrics

    @classmethod
    def gf_value(cls) -> float:
        return round(random.uniform(50.0, 300.0), 2)

    @classmethod
    def pe_ratio(cls) -> float:
        return round(random.uniform(10.0, 40.0), 2)

    @classmethod
    def pb_ratio(cls) -> float:
        return round(random.uniform(1.0, 8.0), 2)

    @classmethod
    def ps_ratio(cls) -> float:
        return round(random.uniform(1.0, 15.0), 2)

    @classmethod
    def peg_ratio(cls) -> float:
        return round(random.uniform(0.5, 3.0), 2)


class RatioHistoryFactory(ModelFactory):
    """Factory for RatioHistory model."""

    __model__ = RatioHistory

    @classmethod
    def low(cls) -> float:
        return round(random.uniform(5.0, 15.0), 2)

    @classmethod
    def high(cls) -> float:
        return round(random.uniform(25.0, 50.0), 2)

    @classmethod
    def med(cls) -> float:
        return round(random.uniform(15.0, 25.0), 2)


class RatioIndustryFactory(ModelFactory):
    """Factory for RatioIndustry model."""

    __model__ = RatioIndustry

    @classmethod
    def global_rank(cls) -> int:
        return random.randint(1, 500)

    @classmethod
    def indu_med(cls) -> float:
        return round(random.uniform(10.0, 30.0), 2)

    @classmethod
    def indu_tot(cls) -> int:
        return random.randint(100, 1000)


class RatioValueFactory(ModelFactory):
    """Factory for RatioValue model."""

    __model__ = RatioValue
    __set_as_default_factory_for_type__ = True

    @classmethod
    def value(cls) -> float:
        return round(random.uniform(5.0, 35.0), 2)

    @classmethod
    def status(cls) -> int:
        return random.randint(0, 2)

    his = RatioHistoryFactory
    indu = RatioIndustryFactory


class FinancialRatiosFactory(ModelFactory):
    """Factory for FinancialRatios model."""

    __model__ = FinancialRatios

    pe_ttm = RatioValueFactory
    pb_ratio = RatioValueFactory
    ps_ratio = RatioValueFactory
    current_ratio = RatioValueFactory
    roe = RatioValueFactory


class InstitutionalActivityFactory(ModelFactory):
    """Factory for InstitutionalActivity model."""

    __model__ = InstitutionalActivity

    @classmethod
    def guru_buys_pct(cls) -> float:
        return round(random.uniform(0, 50), 1)

    @classmethod
    def guru_sells_pct(cls) -> float:
        return round(random.uniform(0, 30), 1)

    @classmethod
    def guru_holds_pct(cls) -> float:
        return round(random.uniform(20, 70), 1)


class PriceInfoFactory(ModelFactory):
    """Factory for PriceInfo model."""

    __model__ = PriceInfo

    @classmethod
    def current(cls) -> float:
        return round(random.uniform(10.0, 500.0), 2)

    @classmethod
    def change(cls) -> float:
        return round(random.uniform(-10.0, 10.0), 2)

    @classmethod
    def change_pct(cls) -> float:
        return round(random.uniform(-5.0, 5.0), 2)


class StockSummaryFactory(ModelFactory):
    """Factory for StockSummary model - the main summary factory."""

    __model__ = StockSummary

    @classmethod
    def symbol(cls) -> str:
        return f"FAKE{random.randint(1, 99)}"

    general = GeneralInfoFactory
    quality = QualityScoresFactory
    valuation = ValuationMetricsFactory
    ratios = FinancialRatiosFactory
    institutional = InstitutionalActivityFactory
    price = PriceInfoFactory


# =============================================================================
# KeyRatios Model Factories
# =============================================================================


class ProfitabilityRatiosFactory(ModelFactory):
    """Factory for ProfitabilityRatios model."""

    __model__ = ProfitabilityRatios

    @classmethod
    def roe(cls) -> float:
        return round(random.uniform(5.0, 35.0), 2)

    @classmethod
    def roa(cls) -> float:
        return round(random.uniform(2.0, 20.0), 2)

    @classmethod
    def roic(cls) -> float:
        return round(random.uniform(5.0, 25.0), 2)

    @classmethod
    def gross_margin(cls) -> float:
        return round(random.uniform(20.0, 70.0), 2)

    @classmethod
    def operating_margin(cls) -> float:
        return round(random.uniform(5.0, 40.0), 2)

    @classmethod
    def net_margin(cls) -> float:
        return round(random.uniform(3.0, 30.0), 2)


class LiquidityRatiosFactory(ModelFactory):
    """Factory for LiquidityRatios model."""

    __model__ = LiquidityRatios

    @classmethod
    def current_ratio(cls) -> float:
        return round(random.uniform(0.8, 3.0), 2)

    @classmethod
    def quick_ratio(cls) -> float:
        return round(random.uniform(0.5, 2.5), 2)

    @classmethod
    def cash_ratio(cls) -> float:
        return round(random.uniform(0.1, 1.5), 2)


class SolvencyRatiosFactory(ModelFactory):
    """Factory for SolvencyRatios model."""

    __model__ = SolvencyRatios

    @classmethod
    def debt_to_equity(cls) -> float:
        return round(random.uniform(0.1, 2.0), 2)

    @classmethod
    def debt_to_asset(cls) -> float:
        return round(random.uniform(0.1, 0.6), 2)

    @classmethod
    def debt_to_ebitda(cls) -> float:
        return round(random.uniform(0.5, 4.0), 2)

    @classmethod
    def interest_coverage(cls) -> float:
        return round(random.uniform(2.0, 30.0), 2)


class GrowthRatiosFactory(ModelFactory):
    """Factory for GrowthRatios model."""

    __model__ = GrowthRatios

    @classmethod
    def revenue_growth_1y(cls) -> float:
        return round(random.uniform(-10.0, 30.0), 2)

    @classmethod
    def revenue_growth_3y(cls) -> float:
        return round(random.uniform(-5.0, 25.0), 2)

    @classmethod
    def revenue_growth_5y(cls) -> float:
        return round(random.uniform(-3.0, 20.0), 2)

    @classmethod
    def eps_growth_1y(cls) -> float:
        return round(random.uniform(-20.0, 40.0), 2)

    @classmethod
    def eps_growth_3y(cls) -> float:
        return round(random.uniform(-10.0, 30.0), 2)

    @classmethod
    def fcf_growth_3y(cls) -> float:
        return round(random.uniform(-15.0, 35.0), 2)


class PriceMetricsFactory(ModelFactory):
    """Factory for PriceMetrics model."""

    __model__ = PriceMetrics

    @classmethod
    def current_price(cls) -> float:
        return round(random.uniform(10.0, 500.0), 2)

    @classmethod
    def high_52week(cls) -> float:
        return round(random.uniform(100.0, 600.0), 2)

    @classmethod
    def low_52week(cls) -> float:
        return round(random.uniform(50.0, 200.0), 2)

    @classmethod
    def beta(cls) -> float:
        return round(random.uniform(0.5, 2.0), 2)

    @classmethod
    def volatility_1y(cls) -> float:
        return round(random.uniform(15.0, 50.0), 2)


class ValuationRatiosFactory(ModelFactory):
    """Factory for ValuationRatios (keyratios version)."""

    __model__ = ValuationRatios

    @classmethod
    def pe_ratio(cls) -> float:
        return round(random.uniform(10.0, 40.0), 2)

    @classmethod
    def pb_ratio(cls) -> float:
        return round(random.uniform(1.0, 8.0), 2)

    @classmethod
    def ps_ratio(cls) -> float:
        return round(random.uniform(1.0, 15.0), 2)

    @classmethod
    def peg_ratio(cls) -> float:
        return round(random.uniform(0.5, 3.0), 2)

    @classmethod
    def gf_value(cls) -> float:
        return round(random.uniform(50.0, 300.0), 2)


class KeyRatiosFactory(ModelFactory):
    """Factory for KeyRatios model - comprehensive financial ratios."""

    __model__ = KeyRatios

    @classmethod
    def symbol(cls) -> str:
        return f"FAKE{random.randint(1, 99)}"

    @classmethod
    def company_name(cls) -> str:
        return fake_company_name()

    @classmethod
    def currency(cls) -> str:
        return "USD"

    @classmethod
    def piotroski_score(cls) -> int:
        return random.randint(3, 9)

    @classmethod
    def altman_z_score(cls) -> float:
        return round(random.uniform(1.5, 5.0), 2)

    @classmethod
    def beneish_m_score(cls) -> float:
        return round(random.uniform(-3.5, -1.5), 2)

    @classmethod
    def gf_score(cls) -> int:
        return random.randint(40, 95)

    @classmethod
    def financial_strength(cls) -> int:
        return random.randint(4, 10)

    @classmethod
    def profitability_rank(cls) -> int:
        return random.randint(4, 10)

    @classmethod
    def growth_rank(cls) -> int:
        return random.randint(3, 10)

    profitability = ProfitabilityRatiosFactory
    liquidity = LiquidityRatiosFactory
    solvency = SolvencyRatiosFactory
    growth = GrowthRatiosFactory
    price = PriceMetricsFactory
    valuation = ValuationRatiosFactory


# =============================================================================
# Specialized Scenario Factories
# =============================================================================


class DistressedCompanyKeyRatiosFactory(KeyRatiosFactory):
    """Factory for a financially distressed company.

    Use this to test risk analysis edge cases for companies in trouble.
    """

    @classmethod
    def altman_z_score(cls) -> float:
        return round(random.uniform(0.5, 1.7), 2)  # Below 1.81 = distress

    @classmethod
    def piotroski_score(cls) -> int:
        return random.randint(0, 3)  # Weak

    @classmethod
    def beneish_m_score(cls) -> float:
        return round(random.uniform(-1.5, -0.5), 2)  # Possible manipulation

    @classmethod
    def financial_strength(cls) -> int:
        return random.randint(1, 3)  # Weak


class DistressedSolvencyFactory(SolvencyRatiosFactory):
    """Solvency ratios for distressed company."""

    @classmethod
    def debt_to_equity(cls) -> float:
        return round(random.uniform(2.5, 5.0), 2)  # High leverage

    @classmethod
    def interest_coverage(cls) -> float:
        return round(random.uniform(0.3, 1.5), 2)  # Can't cover interest

    @classmethod
    def debt_to_ebitda(cls) -> float:
        return round(random.uniform(5.0, 10.0), 2)  # Very high


class DistressedLiquidityFactory(LiquidityRatiosFactory):
    """Liquidity ratios for distressed company."""

    @classmethod
    def current_ratio(cls) -> float:
        return round(random.uniform(0.3, 0.8), 2)  # Below 1 = liquidity issues

    @classmethod
    def quick_ratio(cls) -> float:
        return round(random.uniform(0.2, 0.5), 2)

    @classmethod
    def cash_ratio(cls) -> float:
        return round(random.uniform(0.05, 0.2), 2)


# Wire up distressed sub-factories
DistressedCompanyKeyRatiosFactory.solvency = DistressedSolvencyFactory
DistressedCompanyKeyRatiosFactory.liquidity = DistressedLiquidityFactory


class HealthyCompanyKeyRatiosFactory(KeyRatiosFactory):
    """Factory for a financially healthy company.

    Use this to test risk analysis for companies with strong fundamentals.
    """

    @classmethod
    def altman_z_score(cls) -> float:
        return round(random.uniform(3.5, 6.0), 2)  # Above 2.99 = safe

    @classmethod
    def piotroski_score(cls) -> int:
        return random.randint(7, 9)  # Strong

    @classmethod
    def beneish_m_score(cls) -> float:
        return round(random.uniform(-3.5, -2.5), 2)  # No manipulation

    @classmethod
    def financial_strength(cls) -> int:
        return random.randint(7, 10)  # Strong


class HealthySolvencyFactory(SolvencyRatiosFactory):
    """Solvency ratios for healthy company."""

    @classmethod
    def debt_to_equity(cls) -> float:
        return round(random.uniform(0.1, 0.5), 2)  # Low leverage

    @classmethod
    def interest_coverage(cls) -> float:
        return round(random.uniform(15.0, 50.0), 2)  # Strong coverage

    @classmethod
    def debt_to_ebitda(cls) -> float:
        return round(random.uniform(0.3, 1.5), 2)  # Low


class HealthyLiquidityFactory(LiquidityRatiosFactory):
    """Liquidity ratios for healthy company."""

    @classmethod
    def current_ratio(cls) -> float:
        return round(random.uniform(1.8, 3.5), 2)  # Strong liquidity

    @classmethod
    def quick_ratio(cls) -> float:
        return round(random.uniform(1.2, 2.5), 2)

    @classmethod
    def cash_ratio(cls) -> float:
        return round(random.uniform(0.5, 1.5), 2)


class HealthyGrowthFactory(GrowthRatiosFactory):
    """Growth ratios for healthy company."""

    @classmethod
    def revenue_growth_1y(cls) -> float:
        return round(random.uniform(10.0, 30.0), 2)

    @classmethod
    def revenue_growth_3y(cls) -> float:
        return round(random.uniform(12.0, 25.0), 2)

    @classmethod
    def eps_growth_3y(cls) -> float:
        return round(random.uniform(15.0, 35.0), 2)


# Wire up healthy sub-factories
HealthyCompanyKeyRatiosFactory.solvency = HealthySolvencyFactory
HealthyCompanyKeyRatiosFactory.liquidity = HealthyLiquidityFactory
HealthyCompanyKeyRatiosFactory.growth = HealthyGrowthFactory


# =============================================================================
# Quote Factory
# =============================================================================


class StockQuoteFactory(ModelFactory):
    """Factory for StockQuote model."""

    __model__ = StockQuote

    @classmethod
    def symbol(cls) -> str:
        return f"FAKE{random.randint(1, 99)}"

    @classmethod
    def exchange(cls) -> str:
        return fake_exchange()

    @classmethod
    def currency(cls) -> str:
        return "USD"

    @classmethod
    def timestamp(cls) -> int:
        return 1735500000 + random.randint(0, 100000)

    @classmethod
    def current_price(cls) -> float:
        return round(random.uniform(10.0, 500.0), 2)

    @classmethod
    def price_change(cls) -> float:
        return round(random.uniform(-10.0, 10.0), 2)

    @classmethod
    def price_change_pct(cls) -> float:
        return round(random.uniform(-5.0, 5.0), 2)

    @classmethod
    def open(cls) -> float:
        return round(random.uniform(10.0, 500.0), 2)

    @classmethod
    def high(cls) -> float:
        return round(random.uniform(10.0, 550.0), 2)

    @classmethod
    def low(cls) -> float:
        return round(random.uniform(10.0, 450.0), 2)

    @classmethod
    def volume(cls) -> int:
        return random.randint(100000, 50000000)


# =============================================================================
# ETF Factories
# =============================================================================


class ETFInfoFactory(ModelFactory):
    """Factory for ETFInfo model."""

    __model__ = ETFInfo

    @classmethod
    def name(cls) -> str:
        prefixes = ["Fake", "Test", "Mock"]
        types = ["Total Market", "S&P 500", "Growth", "Value", "Dividend"]
        return f"{random.choice(prefixes)} {random.choice(types)} ETF"


class ETFListResponseFactory(ModelFactory):
    """Factory for ETFListResponse model."""

    __model__ = ETFListResponse

    @classmethod
    def current_page(cls) -> int:
        return 1

    @classmethod
    def per_page(cls) -> int:
        return 50

    @classmethod
    def last_page(cls) -> int:
        return random.randint(1, 10)

    @classmethod
    def total(cls) -> int:
        return random.randint(50, 500)

    @classmethod
    def etfs(cls) -> list[ETFInfo]:
        return [ETFInfoFactory.build() for _ in range(random.randint(3, 10))]


class IndustryWeightingFactory(ModelFactory):
    """Factory for IndustryWeighting model."""

    __model__ = IndustryWeighting

    @classmethod
    def industry(cls) -> str:
        return fake_industry()

    @classmethod
    def weightings(cls) -> dict[str, float]:
        return {
            "2025-09-30": round(random.uniform(1.0, 15.0), 2),
            "2025-06-30": round(random.uniform(1.0, 15.0), 2),
        }


class SectorWeightingFactory(ModelFactory):
    """Factory for SectorWeighting model."""

    __model__ = SectorWeighting

    @classmethod
    def sector(cls) -> str:
        return fake_sector()

    @classmethod
    def weightings(cls) -> dict[str, float]:
        return {
            "2025-09-30": round(random.uniform(5.0, 30.0), 2),
            "2025-06-30": round(random.uniform(5.0, 30.0), 2),
        }

    @classmethod
    def industries(cls) -> list[IndustryWeighting]:
        return [IndustryWeightingFactory.build() for _ in range(random.randint(2, 5))]


class ETFSectorWeightingResponseFactory(ModelFactory):
    """Factory for ETFSectorWeightingResponse model."""

    __model__ = ETFSectorWeightingResponse

    @classmethod
    def name(cls) -> str:
        return f"Fake {random.choice(['Total Market', 'S&P 500', 'Growth'])} ETF"

    @classmethod
    def sectors(cls) -> list[SectorWeighting]:
        return [SectorWeightingFactory.build() for _ in range(random.randint(3, 8))]


# =============================================================================
# Guru Factories
# =============================================================================


class GuruListItemFactory(ModelFactory):
    """Factory for GuruListItem model."""

    __model__ = GuruListItem

    @classmethod
    def guru_id(cls) -> str:
        return str(random.randint(1, 1000))

    @classmethod
    def name(cls) -> str:
        first = random.choice(["Warren", "Charlie", "Bill", "Ray", "Carl", "David"])
        last = random.choice(["Fakeman", "Testson", "Mockley", "Sampleworth"])
        return f"{first} {last}"

    @classmethod
    def firm(cls) -> str:
        return f"Fake {random.choice(['Capital', 'Partners', 'Management', 'Investments'])}"

    @classmethod
    def num_stocks(cls) -> int:
        return random.randint(10, 200)

    @classmethod
    def equity(cls) -> float:
        return round(random.uniform(100.0, 50000.0), 2)

    @classmethod
    def turnover(cls) -> int:
        return random.randint(1, 20)

    @classmethod
    def last_updated(cls) -> str:
        return fake_date()

    @classmethod
    def cik(cls) -> str:
        return f"000{random.randint(1000000, 9999999)}"


class GuruListResponseFactory(ModelFactory):
    """Factory for GuruListResponse model."""

    __model__ = GuruListResponse

    @classmethod
    def us_gurus(cls) -> list[GuruListItem]:
        return [GuruListItemFactory.build() for _ in range(random.randint(3, 10))]

    @classmethod
    def plus_gurus(cls) -> list[GuruListItem]:
        return [GuruListItemFactory.build() for _ in range(random.randint(1, 5))]

    @classmethod
    def total_count(cls) -> int:
        return random.randint(50, 200)


class StockGuruPickFactory(ModelFactory):
    """Factory for StockGuruPick model."""

    __model__ = StockGuruPick

    @classmethod
    def guru(cls) -> str:
        return f"Fake {random.choice(['Capital', 'Partners', 'Management'])}"

    @classmethod
    def guru_id(cls) -> str:
        return str(random.randint(1, 1000))

    @classmethod
    def date(cls) -> str:
        return fake_date()

    @classmethod
    def action(cls) -> str:
        return random.choice(["Add", "Reduce", "New Buy", "Sold Out"])

    @classmethod
    def impact(cls) -> str:
        return str(round(random.uniform(0.1, 5.0), 2))

    @classmethod
    def price_min(cls) -> str:
        return str(round(random.uniform(50.0, 200.0), 2))

    @classmethod
    def price_max(cls) -> str:
        return str(round(random.uniform(200.0, 400.0), 2))

    @classmethod
    def avg_price(cls) -> str:
        return str(round(random.uniform(100.0, 300.0), 2))

    @classmethod
    def comment(cls) -> str:
        action = random.choice(["Add", "Reduce"])
        pct = random.randint(5, 50)
        return f"{action} {pct}%"

    @classmethod
    def current_shares(cls) -> str:
        return f"{random.randint(10000, 1000000):,}"


class StockGuruHoldingFactory(ModelFactory):
    """Factory for StockGuruHolding model."""

    __model__ = StockGuruHolding

    @classmethod
    def guru(cls) -> str:
        return f"Fake {random.choice(['Capital', 'Partners', 'Management'])}"

    @classmethod
    def guru_id(cls) -> str:
        return str(random.randint(1, 1000))

    @classmethod
    def date(cls) -> str:
        return fake_date()

    @classmethod
    def current_shares(cls) -> str:
        return f"{random.randint(10000, 1000000):,}"

    @classmethod
    def perc_shares(cls) -> str:
        return str(round(random.uniform(0.01, 5.0), 2))

    @classmethod
    def perc_assets(cls) -> str:
        return str(round(random.uniform(0.1, 10.0), 2))

    @classmethod
    def change(cls) -> str:
        return str(round(random.uniform(-20.0, 50.0), 2))


class StockGurusResponseFactory(ModelFactory):
    """Factory for StockGurusResponse model."""

    __model__ = StockGurusResponse

    @classmethod
    def symbol(cls) -> str:
        return f"FAKE{random.randint(1, 99)}"

    @classmethod
    def picks(cls) -> list[StockGuruPick]:
        return [StockGuruPickFactory.build() for _ in range(random.randint(2, 8))]

    @classmethod
    def holdings(cls) -> list[StockGuruHolding]:
        return [StockGuruHoldingFactory.build() for _ in range(random.randint(3, 10))]


# =============================================================================
# Sparse/Empty Data Factories (for edge case testing)
# =============================================================================


class SparseStockSummaryFactory(StockSummaryFactory):
    """Factory that produces minimal/sparse data.

    Use this to test handling of partial API responses.
    """

    @classmethod
    def general(cls) -> GeneralInfo:
        return GeneralInfo(company_name="Sparse Test Corp")

    @classmethod
    def quality(cls) -> None:
        return None

    @classmethod
    def valuation(cls) -> None:
        return None

    @classmethod
    def ratios(cls) -> None:
        return None

    @classmethod
    def institutional(cls) -> None:
        return None

    @classmethod
    def price(cls) -> None:
        return None


class EmptyKeyRatiosFactory(KeyRatiosFactory):
    """Factory that produces KeyRatios with all None values.

    Use this to test handling of completely missing data.
    """

    @classmethod
    def piotroski_score(cls) -> None:
        return None

    @classmethod
    def altman_z_score(cls) -> None:
        return None

    @classmethod
    def beneish_m_score(cls) -> None:
        return None

    @classmethod
    def gf_score(cls) -> None:
        return None

    @classmethod
    def financial_strength(cls) -> None:
        return None

    @classmethod
    def profitability(cls) -> None:
        return None

    @classmethod
    def liquidity(cls) -> None:
        return None

    @classmethod
    def solvency(cls) -> None:
        return None

    @classmethod
    def growth(cls) -> None:
        return None

    @classmethod
    def price(cls) -> None:
        return None

    @classmethod
    def valuation(cls) -> None:
        return None
