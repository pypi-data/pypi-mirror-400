"""
Data models for BOAMP Scraper
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class TenderCategory(str, Enum):
    """Tender categories"""

    IT_DEVELOPMENT = "Développement informatique"
    CLOUD_INFRASTRUCTURE = "Cloud et infrastructure"
    CYBERSECURITY = "Cybersécurité"
    BI_DATA = "BI et Data"
    MOBILE = "Applications mobiles"
    WEB = "Développement web"
    MAINTENANCE = "Maintenance et support"
    CONSULTING = "Conseil IT"
    OTHER = "Autre"


class Tender(BaseModel):
    """
    Tender model

    Attributes:
        title: Tender title
        organisme: Organization name
        budget: Estimated budget in EUR (0 if unknown)
        date_publication: Publication date
        url: Tender URL on BOAMP
        category: Tender category
        region: Region (if specified)
        description: Short description (if available)
    """

    title: str = Field(..., description="Tender title")
    organisme: str = Field(..., description="Organization name")
    budget: int = Field(default=0, ge=0, description="Budget in EUR (0 if unknown)")
    date_publication: datetime = Field(..., description="Publication date")
    url: str = Field(..., description="BOAMP URL")
    category: TenderCategory = Field(default=TenderCategory.OTHER, description="Tender category")
    region: Optional[str] = Field(default=None, description="Region")
    description: Optional[str] = Field(default=None, description="Short description")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Développement d'une application web de gestion",
                "organisme": "Ministère de l'Intérieur",
                "budget": 125000,
                "date_publication": "2026-01-04T10:00:00",
                "url": "https://www.boamp.fr/avis/detail/xxx",
                "category": "Développement informatique",
                "region": "Île-de-France",
                "description": "Développement d'une application web pour la gestion...",
            }
        }
    )


class SearchFilters(BaseModel):
    """
    Search filters for tender queries

    Attributes:
        keywords: List of keywords to search for
        category: Filter by tender category
        budget_min: Minimum budget in EUR
        budget_max: Maximum budget in EUR
        region: Filter by region
        limit: Maximum number of results
    """

    keywords: List[str] = Field(default_factory=list, description="Keywords to search for")
    category: Optional[TenderCategory] = Field(default=None, description="Tender category filter")
    budget_min: Optional[int] = Field(default=None, ge=0, description="Minimum budget in EUR")
    budget_max: Optional[int] = Field(default=None, ge=0, description="Maximum budget in EUR")
    region: Optional[str] = Field(default=None, description="Region filter")
    limit: int = Field(default=50, ge=1, le=500, description="Maximum results (1-500)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "keywords": ["cloud", "aws", "azure"],
                "category": "Cloud et infrastructure",
                "budget_min": 50000,
                "budget_max": 500000,
                "region": "Île-de-France",
                "limit": 50,
            }
        }
    )
