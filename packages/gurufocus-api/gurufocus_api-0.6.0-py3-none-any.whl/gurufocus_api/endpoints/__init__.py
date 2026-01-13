"""API endpoint implementations."""

from .economic import EconomicEndpoint
from .etfs import ETFsEndpoint
from .gurus import GurusEndpoint
from .insiders import InsidersEndpoint
from .personal import PersonalEndpoint
from .politicians import PoliticiansEndpoint
from .reference import ReferenceEndpoint
from .stocks import StocksEndpoint

__all__ = [
    "ETFsEndpoint",
    "EconomicEndpoint",
    "GurusEndpoint",
    "InsidersEndpoint",
    "PersonalEndpoint",
    "PoliticiansEndpoint",
    "ReferenceEndpoint",
    "StocksEndpoint",
]
