"""
Tests for pagination module

Tests the pagination configuration and helper classes.
"""

import pytest
from boamp.pagination import (
    PaginationConfig,
    PaginationHelper,
    get_pagination_url,
    default_pagination
)


class TestPaginationConfig:
    """Test PaginationConfig dataclass"""
    
    def test_default_values(self):
        """Test default configuration values"""
        config = PaginationConfig()
        
        assert config.max_pages == 5
        assert config.page_delay == 3.0
        assert config.stop_on_empty is True
        assert config.results_per_page == 10
    
    def test_custom_values(self):
        """Test custom configuration"""
        config = PaginationConfig(
            max_pages=10,
            page_delay=5.0,
            stop_on_empty=False,
            results_per_page=20
        )
        
        assert config.max_pages == 10
        assert config.page_delay == 5.0
        assert config.stop_on_empty is False
        assert config.results_per_page == 20
    
    def test_validation_max_pages(self):
        """Test validation of max_pages"""
        with pytest.raises(ValueError, match="max_pages must be >= 1"):
            PaginationConfig(max_pages=0)
        
        with pytest.raises(ValueError, match="max_pages must be >= 1"):
            PaginationConfig(max_pages=-1)
    
    def test_validation_page_delay(self):
        """Test validation of page_delay"""
        with pytest.raises(ValueError, match="page_delay must be >= 0"):
            PaginationConfig(page_delay=-1.0)
        
        # Zero delay is valid (for testing)
        config = PaginationConfig(page_delay=0.0)
        assert config.page_delay == 0.0
    
    def test_validation_results_per_page(self):
        """Test validation of results_per_page"""
        with pytest.raises(ValueError, match="results_per_page must be >= 1"):
            PaginationConfig(results_per_page=0)


class TestPaginationHelper:
    """Test PaginationHelper class"""
    
    def test_initialization(self):
        """Test helper initialization"""
        config = PaginationConfig(max_pages=3)
        helper = PaginationHelper(config)
        
        assert helper.current_page == 1
        assert helper.total_results == 0
        assert helper.pages_scraped == 0
        assert helper.empty_pages == 0
    
    def test_should_continue_normal(self):
        """Test should_continue with normal results"""
        config = PaginationConfig(max_pages=3, results_per_page=10)
        helper = PaginationHelper(config)
        
        # Page 1: 10 results → continue
        assert helper.should_continue(10) is True
        helper.next_page(10)
        
        # Page 2: 10 results → continue
        assert helper.should_continue(10) is True
        helper.next_page(10)
        
        # Page 3: 10 results → stop (max pages reached)
        assert helper.should_continue(10) is False
    
    def test_should_continue_empty_page(self):
        """Test should_continue with empty page"""
        config = PaginationConfig(max_pages=5, stop_on_empty=True)
        helper = PaginationHelper(config)
        
        # Page 1: 10 results → continue
        assert helper.should_continue(10) is True
        helper.next_page(10)
        
        # Page 2: 0 results → stop (empty page)
        assert helper.should_continue(0) is False
        assert helper.empty_pages == 1
    
    def test_should_continue_empty_page_no_stop(self):
        """Test should_continue with empty page but stop_on_empty=False"""
        config = PaginationConfig(max_pages=5, stop_on_empty=False)
        helper = PaginationHelper(config)
        
        # Page 1: 0 results → continue (stop_on_empty is False)
        assert helper.should_continue(0) is True
        helper.next_page(0)
        
        # Page 2: 0 results → continue
        assert helper.should_continue(0) is True
    
    def test_next_page(self):
        """Test next_page method"""
        config = PaginationConfig()
        helper = PaginationHelper(config)
        
        assert helper.current_page == 1
        assert helper.pages_scraped == 0
        assert helper.total_results == 0
        
        # Move to page 2
        helper.next_page(10)
        assert helper.current_page == 2
        assert helper.pages_scraped == 1
        assert helper.total_results == 10
        
        # Move to page 3
        helper.next_page(8)
        assert helper.current_page == 3
        assert helper.pages_scraped == 2
        assert helper.total_results == 18
    
    def test_get_stats(self):
        """Test get_stats method"""
        config = PaginationConfig()
        helper = PaginationHelper(config)
        
        # Initial stats
        stats = helper.get_stats()
        assert stats["pages_scraped"] == 0
        assert stats["total_results"] == 0
        assert stats["empty_pages"] == 0
        assert stats["avg_results_per_page"] == 0
        
        # After scraping 2 pages
        helper.next_page(10)
        helper.next_page(8)
        
        stats = helper.get_stats()
        assert stats["pages_scraped"] == 2
        assert stats["total_results"] == 18
        assert stats["avg_results_per_page"] == 9.0


class TestGetPaginationUrl:
    """Test get_pagination_url function"""
    
    def test_basic_pagination(self):
        """Test basic URL pagination"""
        base_url = "https://www.boamp.fr/pages/recherche/?texte=cloud"
        
        # Page 1 (BOAMP uses 0-indexed pages)
        url1 = get_pagination_url(base_url, 1)
        assert url1 == "https://www.boamp.fr/pages/recherche/?texte=cloud&page=0"
        
        # Page 2
        url2 = get_pagination_url(base_url, 2)
        assert url2 == "https://www.boamp.fr/pages/recherche/?texte=cloud&page=1"
        
        # Page 10
        url10 = get_pagination_url(base_url, 10)
        assert url10 == "https://www.boamp.fr/pages/recherche/?texte=cloud&page=9"
    
    def test_pagination_without_query(self):
        """Test pagination on URL without existing query params"""
        base_url = "https://www.boamp.fr/pages/recherche"
        
        url = get_pagination_url(base_url, 2)
        assert url == "https://www.boamp.fr/pages/recherche?page=1"
    
    def test_pagination_with_multiple_params(self):
        """Test pagination with multiple existing parameters"""
        base_url = "https://www.boamp.fr/pages/recherche/?texte=cloud&famille=F17"
        
        url = get_pagination_url(base_url, 3)
        assert url == "https://www.boamp.fr/pages/recherche/?texte=cloud&famille=F17&page=2"


class TestDefaultPagination:
    """Test default pagination config"""
    
    def test_default_config_exists(self):
        """Test that default config exists and has reasonable values"""
        assert default_pagination.max_pages == 5
        assert default_pagination.page_delay == 3.0
        assert default_pagination.stop_on_empty is True
    
    def test_default_config_is_conservative(self):
        """Test that default config is conservative (polite)"""
        # Conservative means: not too many pages, reasonable delay
        assert default_pagination.max_pages <= 10
        assert default_pagination.page_delay >= 2.0

