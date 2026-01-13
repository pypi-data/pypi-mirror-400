"""
BOAMP Scraper - Main scraper class
"""

import asyncio
import logging
from typing import List, Optional
from datetime import datetime
import re
from playwright.async_api import async_playwright, Browser, BrowserContext
from fake_useragent import UserAgent

from .models import Tender, TenderCategory, SearchFilters

logger = logging.getLogger("boamp-scraper")

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class TenderScraper:
    """
    Main scraper class for BOAMP (French public tenders)

    Example:
        >>> scraper = TenderScraper()
        >>> tenders = scraper.search(keywords=["cloud"], limit=10)
        >>> print(f"Found {len(tenders)} tenders")
    """

    BASE_URL = "https://www.boamp.fr/pages/recherche/"

    def __init__(self, headless: bool = True):
        """
        Initialize scraper

        Args:
            headless: Run browser in headless mode (default: True)
        """
        self.headless = headless
        self.ua = UserAgent()
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._playwright = None

    async def _init_browser(self):
        """Initialize Playwright browser (stealth mode)"""
        if self._browser:
            return

        logger.info("🌐 Initializing Playwright browser...")

        self._playwright = await async_playwright().start()

        # Stealth args (anti-detection)
        args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--disable-setuid-sandbox",
        ]

        self._browser = await self._playwright.chromium.launch(headless=self.headless, args=args)

        self._context = await self._browser.new_context(
            user_agent=self.ua.random,
            viewport={"width": 1920, "height": 1080},
            locale="fr-FR",
            timezone_id="Europe/Paris",
        )

        logger.info("✅ Browser initialized successfully")

    async def _close_browser(self):
        """Close browser"""
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

        self._browser = None
        self._context = None
        self._playwright = None

    def _build_url(self, filters: SearchFilters) -> str:
        """Build BOAMP search URL with filters"""
        params = {
            "disposition": "chronologique",
            "nature": "marché",
            "famille": "F17",  # F17 = IT & Telecom
        }

        # Add keywords to URL if provided
        if filters.keywords:
            params["texte"] = " ".join(filters.keywords)

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.BASE_URL}?{query_string}"

    async def _scrape_page(self, filters: SearchFilters) -> List[Tender]:
        """Scrape one page of BOAMP"""
        await self._init_browser()

        page = await self._context.new_page()

        try:
            url = self._build_url(filters)
            logger.info(f"📍 Scraping: {url}")

            # Navigate
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2)  # Wait for JS rendering

            # Human-like behavior (scroll)
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
            await asyncio.sleep(1)

            # Extract tenders
            tenders = await self._extract_tenders(page, filters)

            logger.info(f"✅ Found {len(tenders)} tenders")
            return tenders

        except Exception as e:
            logger.error(f"❌ Scraping error: {e}")
            return []

        finally:
            await page.close()

    async def _extract_tenders(self, page, filters: SearchFilters) -> List[Tender]:
        """Extract tender data from page using real BOAMP selectors"""
        tenders = []

        try:
            # Wait for Angular to render and show results
            logger.info("⏳ Waiting for BOAMP results to load...")
            
            # Give Angular time to load data and render
            await asyncio.sleep(5)
            
            # Wait for tender cards to be in DOM (they exist but may not be "visible" per CSS)
            await page.wait_for_selector(".card-notification", state="attached", timeout=25000)
            
            # Give extra time for all cards to render
            await asyncio.sleep(2)
            
            # Get all tender cards
            elements = await page.query_selector_all(".card-notification.fr-callout.fr-callout--boamp")
            logger.info(f"✅ Found {len(elements)} tenders")

            if len(elements) == 0:
                logger.warning("⚠️  No tenders found - check if search returned results")
                return tenders

            # Parse each tender
            for i, element in enumerate(elements):
                try:
                    tender = await self._parse_tender_element(element)
                    if tender:
                        # Apply filters
                        if self._matches_filters(tender, filters):
                            tenders.append(tender)
                            logger.debug(f"  ✓ Tender #{i+1}: {tender.title[:60]}...")

                            if len(tenders) >= filters.limit:
                                logger.info(f"🎯 Reached limit of {filters.limit} tenders")
                                break
                    else:
                        logger.debug(f"  ⚠️  Could not parse tender #{i+1}")
                        
                except Exception as e:
                    logger.warning(f"  ⚠️  Error parsing tender #{i+1}: {e}")
                    continue

        except TimeoutError:
            logger.error("❌ Timeout waiting for BOAMP results to load")
            logger.error("   This might mean:")
            logger.error("   1. BOAMP is down or slow")
            logger.error("   2. Your search returned no results")
            logger.error("   3. Network issues")
        except Exception as e:
            logger.error(f"❌ Error extracting tenders: {e}")

        return tenders

    async def _parse_tender_element(self, element) -> Optional[Tender]:
        """Parse single tender element using real BOAMP structure"""
        try:
            # Extract title (from h2 > span with ng-bind-html)
            title = "N/A"
            title_elem = await element.query_selector("h2 span[ng-bind-html]")
            if title_elem:
                title = await title_elem.inner_text()
            else:
                # Fallback: try h2 > a > span
                title_elem = await element.query_selector("h2 a span")
                if title_elem:
                    title = await title_elem.inner_text()

            # Extract organisme (from span with ng-bind-html containing 'nomacheteur')
            organisme = "N/A"
            org_elem = await element.query_selector("span[ng-bind-html*='nomacheteur']")
            if org_elem:
                organisme = await org_elem.inner_text()

            # Extract tender ID (from label for checkbox)
            tender_id = None
            id_elem = await element.query_selector("label[for^='checkboxes-select-avis-']")
            if id_elem:
                id_text = await id_elem.inner_text()
                # Format: "Avis n° 26-12"
                if "°" in id_text:
                    tender_id = id_text.split("°")[1].strip()

            # Extract URL (from h2 > a)
            url = ""
            link_elem = await element.query_selector("h2 a")
            if link_elem:
                url = await link_elem.get_attribute("href")
                if url and not url.startswith("http"):
                    url = f"https://www.boamp.fr{url}"
            elif tender_id:
                # Construct URL from tender ID
                url = f"https://www.boamp.fr/pages/avis?q=idweb:\"{tender_id}\""

            # Extract date (from span containing "Publié le")
            date_pub = datetime.now()  # Default to now
            date_elems = await element.query_selector_all("span")
            for date_elem in date_elems:
                text = await date_elem.inner_text()
                if "Publié le" in text:
                    # Parse French date format (e.g. "4 janvier 2026")
                    try:
                        date_str = text.replace("Publié le", "").strip()
                        # For now, use current date (full parsing would need French locale)
                        date_pub = datetime.now()
                    except:
                        pass
                    break

            # Budget is NOT available in the list (would need to visit detail page)
            budget = 0

            # Extract department/region
            region = None
            dept_elem = await element.query_selector("span[ng-repeat*='dept']")
            if dept_elem:
                region = await dept_elem.inner_text()

            # Create tender object
            return Tender(
                title=title.strip(),
                organisme=organisme.strip(),
                budget=budget,
                date_publication=date_pub,
                url=url,
                category=TenderCategory.OTHER,  # Would need NLP/keywords to categorize
                region=region.strip() if region else None,
                description=None,
            )

        except Exception as e:
            logger.debug(f"⚠️  Error parsing tender element: {e}")
            return None

    def _parse_budget(self, text: str) -> int:
        """Parse budget from text"""
        try:
            # Extract numbers
            numbers = re.findall(r"\d+[\s,.]?\d*", text.replace(" ", ""))
            if numbers:
                # Convert to int
                num_str = numbers[0].replace(",", "").replace(".", "")
                return int(num_str)
        except (ValueError, IndexError):
            pass
        return 0

    def _matches_filters(self, tender: Tender, filters: SearchFilters) -> bool:
        """Check if tender matches filters"""
        # Budget filters
        if filters.budget_min and tender.budget < filters.budget_min:
            return False
        if filters.budget_max and tender.budget > filters.budget_max:
            return False

        # Region filter
        if filters.region and tender.region != filters.region:
            return False

        # Category filter
        if filters.category and tender.category != filters.category:
            return False

        return True

    async def search_async(
        self,
        keywords: Optional[List[str]] = None,
        category: Optional[TenderCategory] = None,
        budget_min: Optional[int] = None,
        budget_max: Optional[int] = None,
        region: Optional[str] = None,
        limit: int = 50,
    ) -> List[Tender]:
        """
        Search for tenders (async)

        Args:
            keywords: List of keywords to search for
            category: Filter by tender category
            budget_min: Minimum budget in EUR
            budget_max: Maximum budget in EUR
            region: Filter by region
            limit: Maximum number of results (default: 50)

        Returns:
            List of Tender objects

        Example:
            >>> tenders = await scraper.search_async(
            ...     keywords=["cloud", "aws"],
            ...     budget_min=50000,
            ...     limit=10
            ... )
        """
        logger.info("🔍 Starting tender search...")
        logger.info(f"   Keywords: {keywords or 'all'}")
        logger.info(f"   Category: {category.value if category else 'all'}")
        logger.info(f"   Budget range: {budget_min or 0} - {budget_max or '∞'} EUR")
        logger.info(f"   Limit: {limit}")

        filters = SearchFilters(
            keywords=keywords or [],
            category=category,
            budget_min=budget_min,
            budget_max=budget_max,
            region=region,
            limit=limit,
        )

        try:
            tenders = await self._scrape_page(filters)
            logger.info(f"✅ Search complete: {len(tenders)} tenders found")
            return tenders

        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            raise

        finally:
            await self._close_browser()
            logger.info("🔒 Browser closed")

    def search(
        self,
        keywords: Optional[List[str]] = None,
        category: Optional[TenderCategory] = None,
        budget_min: Optional[int] = None,
        budget_max: Optional[int] = None,
        region: Optional[str] = None,
        limit: int = 50,
    ) -> List[Tender]:
        """
        Search for tenders (sync wrapper)

        Args:
            keywords: List of keywords to search for
            category: Filter by tender category
            budget_min: Minimum budget in EUR
            budget_max: Maximum budget in EUR
            region: Filter by region
            limit: Maximum number of results (default: 50)

        Returns:
            List of Tender objects

        Example:
            >>> scraper = TenderScraper()
            >>> tenders = scraper.search(keywords=["cloud"], limit=10)
            >>> print(f"Found {len(tenders)} tenders")
        """
        return asyncio.run(
            self.search_async(
                keywords=keywords,
                category=category,
                budget_min=budget_min,
                budget_max=budget_max,
                region=region,
                limit=limit,
            )
        )
