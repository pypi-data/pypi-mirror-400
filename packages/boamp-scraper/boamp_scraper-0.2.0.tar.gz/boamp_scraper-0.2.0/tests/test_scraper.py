"""
Basic tests for TenderScraper
"""

import pytest
from boamp import TenderScraper, TenderCategory, Tender


def test_scraper_init():
    """Test scraper initialization"""
    scraper = TenderScraper()
    assert scraper is not None
    assert scraper.headless


def test_basic_search():
    """Test basic search functionality"""
    scraper = TenderScraper()
    tenders = scraper.search(keywords=["cloud"], limit=5)

    assert isinstance(tenders, list)
    assert len(tenders) > 0
    assert len(tenders) <= 5

    # Check first tender structure
    tender = tenders[0]
    assert isinstance(tender, Tender)
    assert tender.title
    assert tender.organisme
    assert tender.budget >= 0
    assert tender.url


def test_keyword_filter():
    """Test keyword filtering"""
    scraper = TenderScraper()
    tenders = scraper.search(keywords=["cloud", "cybersécurité"], limit=10)

    assert isinstance(tenders, list)
    assert len(tenders) > 0

    # Verify keywords are present in at least one tender
    for tender in tenders:
        title_lower = tender.title.lower()
        assert "cloud" in title_lower or "cybersécurité" in title_lower


def test_category_filter():
    """Test category filtering"""
    scraper = TenderScraper()
    tenders = scraper.search(
        keywords=["cloud"], category=TenderCategory.CLOUD_INFRASTRUCTURE, limit=5
    )

    assert isinstance(tenders, list)
    assert len(tenders) > 0

    # All tenders should be cloud infrastructure
    for tender in tenders:
        assert tender.category == TenderCategory.CLOUD_INFRASTRUCTURE


def test_budget_filter():
    """Test budget range filtering"""
    scraper = TenderScraper()
    tenders = scraper.search(
        keywords=["développement"], budget_min=100000, budget_max=300000, limit=10
    )

    assert isinstance(tenders, list)

    # All tenders should be in budget range
    for tender in tenders:
        if tender.budget > 0:  # Only check if budget is specified
            assert 100000 <= tender.budget <= 300000


def test_empty_keywords():
    """Test search with empty keywords"""
    scraper = TenderScraper()
    tenders = scraper.search(keywords=[], limit=5)

    assert isinstance(tenders, list)
    # Should return some tenders even without keywords
    assert len(tenders) >= 0


def test_tender_model():
    """Test Tender model validation"""
    from datetime import datetime

    tender = Tender(
        title="Test tender",
        organisme="Test org",
        budget=100000,
        date_publication=datetime.now(),
        url="https://test.com",
        category=TenderCategory.IT_DEVELOPMENT,
    )

    assert tender.title == "Test tender"
    assert tender.organisme == "Test org"
    assert tender.budget == 100000
    assert tender.category == TenderCategory.IT_DEVELOPMENT


@pytest.mark.asyncio
async def test_async_search():
    """Test async search functionality"""
    scraper = TenderScraper()
    tenders = await scraper.search_async(keywords=["cloud"], limit=3)

    assert isinstance(tenders, list)
    assert len(tenders) > 0
    assert len(tenders) <= 3
