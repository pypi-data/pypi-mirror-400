"""
Test real BOAMP scraping with different keywords

This script tests the scraper with various keywords to verify
that real BOAMP scraping works correctly.

Usage:
    python examples/test_real_scraping.py
"""

import asyncio
from datetime import datetime
from boamp import TenderScraper, TenderCategory


async def test_keywords():
    """Test scraping with different keywords"""
    
    scraper = TenderScraper()
    
    test_cases = [
        {
            "name": "Cloud Infrastructure",
            "keywords": ["cloud"],
            "limit": 3,
        },
        {
            "name": "Cybersecurity",
            "keywords": ["cybersécurité"],
            "limit": 3,
        },
        {
            "name": "IT Development",
            "keywords": ["développement", "informatique"],
            "limit": 3,
        },
        {
            "name": "Multiple Keywords",
            "keywords": ["site", "web"],
            "limit": 3,
        },
    ]
    
    print("=" * 80)
    print("BOAMP SCRAPER - REAL SCRAPING TESTS")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📝 Test #{i}: {test['name']}")
        print(f"   Keywords: {test['keywords']}")
        print(f"   Limit: {test['limit']}")
        print("-" * 80)
        
        try:
            tenders = await scraper.search_async(
                keywords=test['keywords'],
                limit=test['limit']
            )
            
            print(f"✅ Success! Found {len(tenders)} tenders\n")
            
            if tenders:
                for j, tender in enumerate(tenders, 1):
                    print(f"   {j}. {tender.title[:70]}...")
                    print(f"      Organisme: {tender.organisme[:50]}")
                    print(f"      URL: {tender.url}")
                    print()
            else:
                print("   (No tenders found for these keywords)")
                print()
                
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    print("=" * 80)
    print("TESTS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    print("\n🚀 Starting real scraping tests...\n")
    asyncio.run(test_keywords())
    print("\n✅ All tests completed!\n")

