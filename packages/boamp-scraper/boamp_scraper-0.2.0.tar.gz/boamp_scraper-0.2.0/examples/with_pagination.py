"""
Example: Using pagination to scrape multiple pages

This example shows how to scrape multiple pages of BOAMP results
to get more than the default 10 tenders.

Usage:
    python examples/with_pagination.py
"""

import asyncio
from boamp import TenderScraper
from boamp.pagination import PaginationConfig


async def scrape_multiple_pages():
    """Example 1: Scrape multiple pages (up to 50 results)"""
    print("=" * 80)
    print("Example 1: Scrape Multiple Pages (up to 50 results)")
    print("=" * 80)
    
    scraper = TenderScraper()
    
    # Configure pagination: 5 pages max, 10 results per page = 50 results
    pagination = PaginationConfig(
        max_pages=5,
        page_delay=3.0,
        stop_on_empty=True
    )
    
    print(f"\n🔍 Searching for 'cloud' tenders...")
    print(f"   Max pages: {pagination.max_pages}")
    print(f"   Expected results: ~{pagination.max_pages * 10}")
    
    # Note: This is a conceptual example
    # Actual implementation would require scraper.search_paginated() method
    # For now, we demonstrate the pagination logic
    
    all_tenders = []
    current_page = 1
    
    while current_page <= pagination.max_pages:
        print(f"\n📄 Scraping page {current_page}...")
        
        # In reality, we would pass page parameter to scraper
        tenders = await scraper.search_async(
            keywords=["cloud"],
            limit=10  # Results per page
        )
        
        print(f"   ✅ Found {len(tenders)} tenders on page {current_page}")
        
        all_tenders.extend(tenders)
        
        # Check if we should continue
        if len(tenders) == 0 and pagination.stop_on_empty:
            print(f"   ✋ Page {current_page} was empty, stopping")
            break
        
        current_page += 1
        
        # Delay between pages (be polite!)
        if current_page <= pagination.max_pages:
            print(f"   ⏳ Waiting {pagination.page_delay}s before next page...")
            await asyncio.sleep(pagination.page_delay)
    
    print(f"\n✅ Total: {len(all_tenders)} tenders from {current_page-1} pages")
    print("=" * 80)


async def scrape_conservative():
    """Example 2: Conservative scraping (slow, polite)"""
    print("\n" * 2)
    print("=" * 80)
    print("Example 2: Conservative Scraping (3 pages, 10s delay)")
    print("=" * 80)
    
    scraper = TenderScraper()
    
    # Very conservative: only 3 pages, 10 second delay
    pagination = PaginationConfig(
        max_pages=3,
        page_delay=10.0,
        stop_on_empty=True
    )
    
    print(f"\n🐌 Slow and polite scraping...")
    print(f"   Max pages: {pagination.max_pages}")
    print(f"   Delay between pages: {pagination.page_delay}s")
    
    # For demonstration, we'll just show the first page
    tenders = await scraper.search_async(keywords=["informatique"], limit=10)
    
    print(f"\n✅ Found {len(tenders)} tenders on first page")
    print(f"   (In production, would scrape {pagination.max_pages} pages)")
    print("=" * 80)


async def scrape_until_exhausted():
    """Example 3: Scrape until no more results"""
    print("\n" * 2)
    print("=" * 80)
    print("Example 3: Scrape Until Exhausted (max 100 pages)")
    print("=" * 80)
    
    scraper = TenderScraper()
    
    # Scrape many pages but stop when empty
    pagination = PaginationConfig(
        max_pages=100,  # High limit
        page_delay=5.0,
        stop_on_empty=True  # Stop when page is empty
    )
    
    print(f"\n🔄 Will scrape until no more results...")
    print(f"   Max pages: {pagination.max_pages}")
    print(f"   Stop on empty: {pagination.stop_on_empty}")
    
    # For demonstration, just show config
    tenders = await scraper.search_async(keywords=["cybersécurité"], limit=10)
    
    print(f"\n✅ Found {len(tenders)} tenders on first page")
    print(f"   (In production, would continue until page is empty)")
    print("=" * 80)


async def main():
    """Run all examples"""
    print("\n🚀 BOAMP Scraper - Pagination Examples\n")
    
    print("⚠️  NOTE: These examples demonstrate pagination concepts.")
    print("    Full pagination support requires additional scraper methods.")
    print("    Coming soon in v0.3.0! 🚀\n")
    
    # Run example 1
    await scrape_multiple_pages()
    
    # Run example 2
    await scrape_conservative()
    
    # Run example 3
    await scrape_until_exhausted()
    
    print("\n✅ All pagination examples completed!\n")


if __name__ == "__main__":
    asyncio.run(main())

