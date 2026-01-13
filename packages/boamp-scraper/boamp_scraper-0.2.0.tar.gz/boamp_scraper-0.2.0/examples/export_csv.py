"""
Export tenders to CSV example for BOAMP Scraper
"""

import csv
from datetime import datetime
from boamp import TenderScraper


def main():
    """Export to CSV example"""
    print("🇫🇷 BOAMP Scraper - Export to CSV Example\n")

    # Create scraper
    scraper = TenderScraper()

    # Search for tenders
    print("🔍 Searching for all IT tenders...")
    tenders = scraper.search(
        keywords=["informatique", "application", "cloud", "cybersécurité"], limit=50
    )

    print(f"✅ Found {len(tenders)} tenders\n")

    # Export to CSV
    output_file = f"boamp_tenders_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Header
        writer.writerow(
            ["Title", "Organization", "Budget (EUR)", "Category", "Publication Date", "URL"]
        )

        # Data
        for tender in tenders:
            writer.writerow(
                [
                    tender.title,
                    tender.organisme,
                    tender.budget,
                    tender.category.value,
                    tender.date_publication.strftime("%Y-%m-%d"),
                    tender.url,
                ]
            )

    print(f"✅ Exported {len(tenders)} tenders to: {output_file}")
    print("\n📊 You can now:")
    print(f"   - Open {output_file} in Excel")
    print("   - Import into Google Sheets")
    print("   - Analyze with pandas")
    print("   - Share with your team")


if __name__ == "__main__":
    main()
