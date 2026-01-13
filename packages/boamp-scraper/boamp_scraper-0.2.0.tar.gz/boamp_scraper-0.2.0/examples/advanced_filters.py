"""
Advanced filters example for BOAMP Scraper
"""

from boamp import TenderScraper, TenderCategory


def main():
    """Advanced filters example"""
    print("🇫🇷 BOAMP Scraper - Advanced Filters Example\n")

    # Create scraper
    scraper = TenderScraper()

    # Example 1: Filter by category
    print("=" * 60)
    print("EXAMPLE 1: Filter by category (Cloud)")
    print("=" * 60)
    tenders = scraper.search(
        keywords=["cloud", "aws", "azure"], category=TenderCategory.CLOUD_INFRASTRUCTURE, limit=5
    )

    print(f"\n✅ Found {len(tenders)} cloud infrastructure tenders\n")
    for i, tender in enumerate(tenders, 1):
        print(f"{i}. {tender.title}")
        print(f"   Organization: {tender.organisme}")
        print(f"   Budget: {tender.budget:,}€")
        print()

    # Example 2: Filter by budget range
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Filter by budget (100k - 300k€)")
    print("=" * 60)
    tenders = scraper.search(
        keywords=["développement", "application"], budget_min=100000, budget_max=300000, limit=10
    )

    print(f"\n✅ Found {len(tenders)} tenders in budget range\n")
    for i, tender in enumerate(tenders, 1):
        print(f"{i}. {tender.title}")
        print(f"   Budget: {tender.budget:,}€")
        print()

    # Example 3: Cybersecurity only
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Cybersecurity tenders")
    print("=" * 60)
    tenders = scraper.search(
        keywords=["cybersécurité", "sécurité", "audit"],
        category=TenderCategory.CYBERSECURITY,
        limit=10,
    )

    print(f"\n✅ Found {len(tenders)} cybersecurity tenders\n")
    for i, tender in enumerate(tenders, 1):
        print(f"{i}. {tender.title}")
        print(f"   Organization: {tender.organisme}")
        print(f"   Budget: {tender.budget:,}€" if tender.budget > 0 else "   Budget: N/A")
        print()


if __name__ == "__main__":
    main()
