from typing import List
from .base import BaseScraper
from .insomnia import InsomniaScraper
from .vendora import VendoraScraper
from .zer import ZerScraper
from .ebyte import EByteScraper
from .pcarena import PCArenaScraper
from .facebook import FacebookMarketplaceHandler

def get_all_scrapers() -> List[BaseScraper]:
    return [
        InsomniaScraper(),
        VendoraScraper(),
        ZerScraper(),
        EByteScraper(),
        PCArenaScraper(),
        FacebookMarketplaceHandler(),
    ]

__all__ = [
    "BaseScraper",
    "InsomniaScraper",
    "VendoraScraper",
    "ZerScraper",
    "EByteScraper",
    "PCArenaScraper",
    "FacebookMarketplaceHandler",
    "get_all_scrapers",
]
