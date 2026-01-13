"""
Example: Using rate limiting for respectful scraping

This example shows how to use the RateLimiter to be respectful to BOAMP servers
by limiting the number of requests per minute.

Usage:
    python examples/with_rate_limiting.py
"""

import asyncio
from boamp import TenderScraper
from boamp.rate_limiter import RateLimiter, AdaptiveRateLimiter


async def scrape_with_basic_rate_limiting():
    """Example 1: Basic rate limiting (10 requests/minute)"""
    print("=" * 80)
    print("Example 1: Basic Rate Limiting (10 req/min)")
    print("=" * 80)
    
    scraper = TenderScraper()
    limiter = RateLimiter(requests_per_minute=10)
    
    keywords_list = [
        ["cloud"],
        ["cybersécurité"],
        ["informatique"],
    ]
    
    all_tenders = []
    
    for keywords in keywords_list:
        print(f"\n🔍 Searching for: {keywords}")
        
        # Wait for rate limit before each request
        async with limiter:
            tenders = await scraper.search_async(keywords=keywords, limit=3)
            all_tenders.extend(tenders)
            print(f"   ✅ Found {len(tenders)} tenders")
    
    print(f"\n✅ Total: {len(all_tenders)} tenders scraped respectfully!")
    print("=" * 80)


async def scrape_with_adaptive_rate_limiting():
    """Example 2: Adaptive rate limiting (slows down on errors)"""
    print("\n" * 2)
    print("=" * 80)
    print("Example 2: Adaptive Rate Limiting (auto-adjusts speed)")
    print("=" * 80)
    
    scraper = TenderScraper()
    limiter = AdaptiveRateLimiter(
        requests_per_minute=10,
        slowdown_factor=2.0,
        recovery_threshold=3
    )
    
    keywords_list = [
        ["cloud"],
        ["data"],
        ["service"],
        ["développement"],
    ]
    
    all_tenders = []
    
    for keywords in keywords_list:
        print(f"\n🔍 Searching for: {keywords}")
        
        try:
            async with limiter:
                tenders = await scraper.search_async(keywords=keywords, limit=2)
                all_tenders.extend(tenders)
                
                # Record successful scrape
                limiter.record_success()
                print(f"   ✅ Found {len(tenders)} tenders")
        
        except Exception as e:
            # Record error (limiter will slow down automatically)
            limiter.record_error()
            print(f"   ❌ Error: {e}")
            print(f"   ⚠️  Limiter will slow down automatically")
    
    print(f"\n✅ Total: {len(all_tenders)} tenders scraped!")
    print("=" * 80)


async def scrape_with_custom_rate():
    """Example 3: Custom rate limiting (slower, more polite)"""
    print("\n" * 2)
    print("=" * 80)
    print("Example 3: Very Polite Scraping (5 req/min = 12s delay)")
    print("=" * 80)
    
    scraper = TenderScraper()
    
    # Very polite: only 5 requests per minute (12 seconds between requests)
    limiter = RateLimiter(requests_per_minute=5)
    
    keywords_list = [["cloud"], ["informatique"]]
    
    all_tenders = []
    
    for keywords in keywords_list:
        print(f"\n🔍 Searching for: {keywords}")
        
        async with limiter:
            tenders = await scraper.search_async(keywords=keywords, limit=2)
            all_tenders.extend(tenders)
            print(f"   ✅ Found {len(tenders)} tenders")
    
    print(f"\n✅ Total: {len(all_tenders)} tenders (with maximum politeness!)")
    print("=" * 80)


async def main():
    """Run all examples"""
    print("\n🚀 BOAMP Scraper - Rate Limiting Examples\n")
    
    # Run example 1
    await scrape_with_basic_rate_limiting()
    
    # Run example 2
    await scrape_with_adaptive_rate_limiting()
    
    # Run example 3
    await scrape_with_custom_rate()
    
    print("\n✅ All examples completed!\n")


if __name__ == "__main__":
    asyncio.run(main())

