"""
Tests for Pydantic models
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from boamp import Tender, TenderCategory
from boamp.models import SearchFilters


def test_tender_model_valid():
    """Test Tender model with valid data"""
    tender = Tender(
        title="Test Tender",
        organisme="Test Organization",
        budget=100000,
        date_publication=datetime.now(),
        url="https://www.boamp.fr/test",
        category=TenderCategory.IT_DEVELOPMENT,
        region="Île-de-France",
        description="Test description",
    )

    assert tender.title == "Test Tender"
    assert tender.organisme == "Test Organization"
    assert tender.budget == 100000
    assert tender.category == TenderCategory.IT_DEVELOPMENT
    assert tender.region == "Île-de-France"


def test_tender_model_defaults():
    """Test Tender model with default values"""
    tender = Tender(
        title="Minimal Tender",
        organisme="Min Org",
        date_publication=datetime.now(),
        url="https://test.com",
    )

    assert tender.budget == 0
    assert tender.category == TenderCategory.OTHER
    assert tender.region is None
    assert tender.description is None


def test_tender_model_invalid_budget():
    """Test Tender model with invalid budget (negative)"""
    with pytest.raises(ValidationError):
        Tender(
            title="Test",
            organisme="Test",
            budget=-1000,  # Invalid: negative
            date_publication=datetime.now(),
            url="https://test.com",
        )


def test_search_filters_valid():
    """Test SearchFilters model with valid data"""
    filters = SearchFilters(
        keywords=["cloud", "aws"],
        category=TenderCategory.CLOUD_INFRASTRUCTURE,
        budget_min=50000,
        budget_max=500000,
        region="Île-de-France",
        limit=100,
    )

    assert filters.keywords == ["cloud", "aws"]
    assert filters.category == TenderCategory.CLOUD_INFRASTRUCTURE
    assert filters.budget_min == 50000
    assert filters.budget_max == 500000
    assert filters.limit == 100


def test_search_filters_defaults():
    """Test SearchFilters model with defaults"""
    filters = SearchFilters()

    assert filters.keywords == []
    assert filters.category is None
    assert filters.budget_min is None
    assert filters.budget_max is None
    assert filters.region is None
    assert filters.limit == 50


def test_search_filters_limit_bounds():
    """Test SearchFilters limit validation"""
    # Valid limits
    SearchFilters(limit=1)
    SearchFilters(limit=50)
    SearchFilters(limit=500)

    # Invalid: too low
    with pytest.raises(ValidationError):
        SearchFilters(limit=0)

    # Invalid: too high
    with pytest.raises(ValidationError):
        SearchFilters(limit=501)


def test_search_filters_negative_budget():
    """Test SearchFilters with negative budgets"""
    with pytest.raises(ValidationError):
        SearchFilters(budget_min=-1000)

    with pytest.raises(ValidationError):
        SearchFilters(budget_max=-5000)


def test_tender_category_enum():
    """Test TenderCategory enum values"""
    assert TenderCategory.IT_DEVELOPMENT.value == "Développement informatique"
    assert TenderCategory.CLOUD_INFRASTRUCTURE.value == "Cloud et infrastructure"
    assert TenderCategory.CYBERSECURITY.value == "Cybersécurité"
    assert TenderCategory.BI_DATA.value == "BI et Data"
    assert TenderCategory.MOBILE.value == "Applications mobiles"
    assert TenderCategory.WEB.value == "Développement web"
    assert TenderCategory.MAINTENANCE.value == "Maintenance et support"
    assert TenderCategory.CONSULTING.value == "Conseil IT"
    assert TenderCategory.OTHER.value == "Autre"


def test_tender_model_serialization():
    """Test Tender model serialization to dict"""
    tender = Tender(
        title="Test",
        organisme="Org",
        budget=100000,
        date_publication=datetime(2026, 1, 4, 10, 0, 0),
        url="https://test.com",
    )

    data = tender.model_dump()

    assert data["title"] == "Test"
    assert data["organisme"] == "Org"
    assert data["budget"] == 100000
    assert isinstance(data["date_publication"], datetime)

