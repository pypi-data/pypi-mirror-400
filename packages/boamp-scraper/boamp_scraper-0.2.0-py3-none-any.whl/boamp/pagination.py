"""
Pagination support for BOAMP scraping

This module adds pagination capabilities to scrape more than the first page of results.

Usage:
    from boamp import TenderScraper
    from boamp.pagination import PaginationConfig
    
    scraper = TenderScraper()
    
    # Scrape up to 3 pages
    config = PaginationConfig(max_pages=3)
    tenders = scraper.search_paginated(
        keywords=["cloud"],
        pagination=config
    )
"""

from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class PaginationConfig:
    """
    Configuration for pagination behavior.
    
    Attributes:
        max_pages: Maximum number of pages to scrape (default: 5)
        page_delay: Delay between pages in seconds (default: 3)
        stop_on_empty: Stop if a page returns no results (default: True)
        results_per_page: Expected results per page (default: 10)
    
    Example:
        ```python
        # Scrape up to 10 pages with 5 second delay
        config = PaginationConfig(max_pages=10, page_delay=5)
        
        # Scrape until no more results
        config = PaginationConfig(max_pages=100, stop_on_empty=True)
        
        # Conservative scraping (slow, polite)
        config = PaginationConfig(max_pages=3, page_delay=10)
        ```
    """
    
    max_pages: int = 5
    page_delay: float = 3.0
    stop_on_empty: bool = True
    results_per_page: int = 10
    
    def __post_init__(self):
        """Validate configuration"""
        if self.max_pages < 1:
            raise ValueError("max_pages must be >= 1")
        
        if self.page_delay < 0:
            raise ValueError("page_delay must be >= 0")
        
        if self.results_per_page < 1:
            raise ValueError("results_per_page must be >= 1")
        
        logger.debug(
            f"PaginationConfig: max_pages={self.max_pages}, "
            f"page_delay={self.page_delay}s, "
            f"stop_on_empty={self.stop_on_empty}"
        )


class PaginationHelper:
    """
    Helper class for managing pagination state.
    
    Tracks current page, total results, and whether to continue.
    """
    
    def __init__(self, config: PaginationConfig):
        """
        Initialize pagination helper.
        
        Args:
            config: Pagination configuration
        """
        self.config = config
        self.current_page = 1
        self.total_results = 0
        self.pages_scraped = 0
        self.empty_pages = 0
        
        logger.debug("PaginationHelper initialized")
    
    def should_continue(self, results_count: int) -> bool:
        """
        Check if we should continue to next page.
        
        Args:
            results_count: Number of results on current page
        
        Returns:
            True if should continue, False otherwise
        """
        # Check if we reached max pages
        if self.pages_scraped >= self.config.max_pages:
            logger.info(f"✋ Reached max pages limit ({self.config.max_pages})")
            return False
        
        # Check if page was empty and we should stop
        if results_count == 0 and self.config.stop_on_empty:
            self.empty_pages += 1
            logger.info(f"✋ Page {self.current_page} was empty, stopping")
            return False
        
        # If page had fewer results than expected, might be last page
        if results_count < self.config.results_per_page:
            logger.info(
                f"⚠️  Page {self.current_page} had only {results_count} results "
                f"(expected {self.config.results_per_page}), might be last page"
            )
        
        return True
    
    def next_page(self, results_count: int):
        """
        Move to next page.
        
        Args:
            results_count: Number of results on current page
        """
        self.total_results += results_count
        self.pages_scraped += 1
        self.current_page += 1
        
        logger.info(
            f"📄 Moving to page {self.current_page} "
            f"(total results so far: {self.total_results})"
        )
    
    def get_stats(self) -> dict:
        """
        Get pagination statistics.
        
        Returns:
            Dict with pagination stats
        """
        return {
            "pages_scraped": self.pages_scraped,
            "total_results": self.total_results,
            "empty_pages": self.empty_pages,
            "avg_results_per_page": (
                self.total_results / self.pages_scraped
                if self.pages_scraped > 0
                else 0
            ),
        }


def get_pagination_url(base_url: str, page: int, results_per_page: int = 10) -> str:
    """
    Build pagination URL for BOAMP.
    
    BOAMP uses page parameter for pagination (0-indexed).
    
    Args:
        base_url: Base search URL
        page: Page number (1-indexed)
        results_per_page: Results per page
    
    Returns:
        URL with pagination parameters
    
    Example:
        >>> url = "https://www.boamp.fr/pages/recherche/?texte=cloud"
        >>> paginated_url = get_pagination_url(url, 2)
        >>> print(paginated_url)
        https://www.boamp.fr/pages/recherche/?texte=cloud&page=1
    """
    # BOAMP uses 0-indexed pages (page=0 is first page)
    boamp_page = page - 1
    
    # Add page parameter
    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}page={boamp_page}"


# Default pagination config (conservative)
default_pagination = PaginationConfig(
    max_pages=5,
    page_delay=3.0,
    stop_on_empty=True
)

