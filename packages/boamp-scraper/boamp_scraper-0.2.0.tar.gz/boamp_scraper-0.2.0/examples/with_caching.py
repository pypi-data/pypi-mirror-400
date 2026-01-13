"""
Example: Using cache to avoid re-scraping

This example shows how to use the TenderCache to store scraped tenders
and avoid re-scraping the same data multiple times.

Usage:
    python examples/with_caching.py
"""

import asyncio
import time
from boamp import TenderScraper
from boamp.cache import TenderCache


async def scrape_with_cache():
    """Example: Scraping with cache (much faster on second run!)"""
    print("=" * 80)
    print("BOAMP Scraper - Caching Example")
    print("=" * 80)
    
    scraper = TenderScraper()
    
    # Initialize cache with 1 hour TTL
    cache = TenderCache(ttl=3600)
    
    # Show cache stats before
    stats_before = cache.stats()
    print(f"\n📊 Cache stats before:")
    print(f"   Entries: {stats_before['count']}")
    print(f"   Size: {stats_before['size_mb']:.2f} MB")
    
    # First search
    print(f"\n{'='*80}")
    print("🔍 FIRST SEARCH (will scrape from BOAMP)")
    print(f"{'='*80}")
    
    start = time.time()
    tenders = await scraper.search_async(keywords=["cloud"], limit=5)
    first_duration = time.time() - start
    
    print(f"✅ Found {len(tenders)} tenders in {first_duration:.2f}s")
    
    # Cache the tenders
    cache.set_many(tenders)
    print(f"💾 Cached {len(tenders)} tenders")
    
    # Second search (from cache)
    print(f"\n{'='*80}")
    print("🔍 SECOND SEARCH (will use cache)")
    print(f"{'='*80}")
    
    # Simulate checking cache before scraping
    cached_tenders = {}
    tender_ids = [t.id for t in tenders]
    
    start = time.time()
    for tender_id in tender_ids:
        if cache.is_cached(tender_id):
            tender = cache.get(tender_id)
            if tender:
                cached_tenders[tender_id] = tender
    
    second_duration = time.time() - start
    
    print(f"✅ Retrieved {len(cached_tenders)} tenders from cache in {second_duration:.4f}s")
    
    # Show stats after
    stats_after = cache.stats()
    print(f"\n📊 Cache stats after:")
    print(f"   Entries: {stats_after['count']}")
    print(f"   Size: {stats_after['size_mb']:.2f} MB")
    
    # Performance comparison
    print(f"\n⚡ Performance Comparison:")
    print(f"   Scraping: {first_duration:.2f}s")
    print(f"   Cache:    {second_duration:.4f}s")
    print(f"   Speedup:  {first_duration/second_duration:.0f}x faster! 🚀")
    
    print("=" * 80)


async def cache_management_example():
    """Example: Cache management (cleanup, clear, stats)"""
    print("\n" * 2)
    print("=" * 80)
    print("Cache Management Example")
    print("=" * 80)
    
    cache = TenderCache(ttl=3600)
    
    # 1. Show current stats
    print("\n1️⃣  Current cache stats:")
    stats = cache.stats()
    print(f"   Entries: {stats['count']}")
    print(f"   Size: {stats['size_mb']:.2f} MB")
    if stats['oldest']:
        print(f"   Oldest entry: {stats['oldest']}")
        print(f"   Newest entry: {stats['newest']}")
    
    # 2. Cleanup old entries
    print("\n2️⃣  Cleaning up entries older than 1 hour...")
    cache.cleanup(older_than=3600)
    
    # 3. Show stats after cleanup
    stats_after = cache.stats()
    print(f"   Entries after cleanup: {stats_after['count']}")
    
    # 4. Option to clear all
    print("\n3️⃣  Cache management options:")
    print("   - cache.cleanup(): Remove expired entries")
    print("   - cache.clear(): Remove ALL entries")
    print("   - cache.delete(tender_id): Remove specific entry")
    
    print("=" * 80)


async def main():
    """Run all examples"""
    print("\n🚀 BOAMP Scraper - Caching Examples\n")
    
    # Run scraping with cache
    await scrape_with_cache()
    
    # Run cache management example
    await cache_management_example()
    
    print("\n✅ All examples completed!\n")
    print("💡 Tip: Run this script again to see the cache in action!")
    print("        The second run will be much faster! 🚀\n")


if __name__ == "__main__":
    asyncio.run(main())

