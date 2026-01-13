"""
BOAMP Scraper - Scrape French public tenders in 3 lines of Python
"""

from .scraper import TenderScraper
from .models import Tender, TenderCategory, SearchFilters
from .cache import TenderCache
from .rate_limiter import RateLimiter, AdaptiveRateLimiter

__version__ = "0.2.0"
__all__ = [
    "TenderScraper",
    "Tender",
    "TenderCategory",
    "SearchFilters",
    "TenderCache",
    "RateLimiter",
    "AdaptiveRateLimiter",
]
