"""
Basic usage example for BOAMP Scraper
"""

from boamp import TenderScraper


def main():
    """Basic example"""
    print("🇫🇷 BOAMP Scraper - Basic Example\n")

    # Create scraper
    scraper = TenderScraper()

    # Search for tenders
    print("🔍 Searching for tenders with keywords: cloud, cybersécurité")
    tenders = scraper.search(keywords=["cloud", "cybersécurité"], limit=10)

    print(f"\n✅ Found {len(tenders)} tenders\n")

    # Display results
    for i, tender in enumerate(tenders, 1):
        print(f"{'=' * 60}")
        print(f"Tender #{i}")
        print(f"{'=' * 60}")
        print(f"Title: {tender.title}")
        print(f"Organization: {tender.organisme}")
        print(f"Budget: {tender.budget:,}€" if tender.budget > 0 else "Budget: N/A")
        print(f"Category: {tender.category.value}")
        print(f"URL: {tender.url}")
        print(f"Published: {tender.date_publication.strftime('%Y-%m-%d')}")
        print()


if __name__ == "__main__":
    main()
