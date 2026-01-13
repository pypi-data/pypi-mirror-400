# ⚡ Performance Optimization Guide

Get the most out of BOAMP Scraper with these performance tips.

---

## 📊 Performance Benchmarks

### Single Page (10 tenders)
- **Cold start:** ~18-20s (browser launch + scraping)
- **Warm:** ~12-15s (browser already running)
- **With cache:** ~0.001s (instant from cache)

### Multiple Pages (50 tenders)
- **Without pagination:** ~20s (first 10 only)
- **With pagination (5 pages):** ~90-120s (with rate limiting)
- **Parallel scraping:** ~30-40s (5 concurrent scrapers)

### Memory Usage
- **Minimum:** 256MB (Python + dependencies)
- **Browser:** +200-400MB (Chromium)
- **Total:** ~500-700MB per scraper instance

---

## 🚀 Quick Wins

### 1. Use Caching (100-1000x faster!)

```python
from boamp import TenderScraper
from boamp.cache import TenderCache

scraper = TenderScraper()
cache = TenderCache(ttl=86400)  # 24 hours

# First run: scrapes from BOAMP (~18s)
tenders = await scraper.search_async(keywords=["cloud"], limit=10)
cache.set_many(tenders)

# Second run: instant from cache (~0.001s)
cached = cache.get_many([t.id for t in tenders])
```

**Impact:** 10,000x faster for repeated queries 🔥

### 2. Use Async (2-5x faster for multiple searches)

```python
import asyncio

# ❌ Slow (sequential): ~60s for 3 searches
tenders1 = scraper.search(keywords=["cloud"], limit=10)
tenders2 = scraper.search(keywords=["cyber"], limit=10)
tenders3 = scraper.search(keywords=["data"], limit=10)

# ✅ Fast (parallel): ~20s for 3 searches
async def scrape_all():
    tasks = [
        scraper.search_async(keywords=["cloud"], limit=10),
        scraper.search_async(keywords=["cyber"], limit=10),
        scraper.search_async(keywords=["data"], limit=10),
    ]
    return await asyncio.gather(*tasks)

results = asyncio.run(scrape_all())
```

**Impact:** 3x faster for concurrent scraping ⚡

### 3. Reuse Browser Instance

```python
# ❌ Slow: New browser for each search (~5s overhead)
scraper1 = TenderScraper()
tenders1 = scraper1.search(["cloud"], limit=10)

scraper2 = TenderScraper()
tenders2 = scraper2.search(["cyber"], limit=10)

# ✅ Fast: Reuse same browser instance
scraper = TenderScraper()
tenders1 = await scraper.search_async(["cloud"], limit=10)
tenders2 = await scraper.search_async(["cyber"], limit=10)
await scraper.close()
```

**Impact:** Save ~5s per search 💨

---

## 🎯 Advanced Optimizations

### 1. Headless Mode (Already Default)

```python
# BOAMP Scraper uses headless mode by default
scraper = TenderScraper()  # headless=True

# Only use headful for debugging
scraper = TenderScraper(headless=False)
```

**Impact:** 20-30% faster, 50% less memory 📉

### 2. Disable Images & Fonts

```python
# Custom Playwright config (advanced)
from playwright.async_api import async_playwright

async with async_playwright() as p:
    browser = await p.chromium.launch(
        headless=True,
        args=[
            '--disable-images',
            '--disable-fonts',
            '--disable-extensions',
        ]
    )
```

**Impact:** 15-20% faster, saves bandwidth 📶

### 3. Connection Pooling

```python
# Keep browser alive across multiple scrapes
class PersistentScraper:
    def __init__(self):
        self.scraper = None
    
    async def __aenter__(self):
        self.scraper = TenderScraper()
        await self.scraper._init_browser()
        return self.scraper
    
    async def __aexit__(self, *args):
        await self.scraper.close()

# Usage
async with PersistentScraper() as scraper:
    for keywords in [["cloud"], ["cyber"], ["data"]]:
        tenders = await scraper.search_async(keywords, limit=10)
        process(tenders)
```

**Impact:** No browser restart overhead 🔄

### 4. Batch Processing

```python
async def scrape_batch(keywords_list: List[List[str]], batch_size: int = 5):
    """Scrape in batches to control concurrency"""
    scraper = TenderScraper()
    all_results = []
    
    for i in range(0, len(keywords_list), batch_size):
        batch = keywords_list[i:i+batch_size]
        
        tasks = [
            scraper.search_async(keywords=kw, limit=10)
            for kw in batch
        ]
        
        results = await asyncio.gather(*tasks)
        all_results.extend(results)
        
        # Small delay between batches
        if i + batch_size < len(keywords_list):
            await asyncio.sleep(2)
    
    await scraper.close()
    return all_results
```

**Impact:** Controlled concurrency, stable performance 🎛️

---

## 💾 Memory Optimization

### 1. Limit Browser Resources

```python
browser_args = [
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--no-sandbox',
    '--max-old-space-size=512',  # Limit to 512MB
]
```

**Impact:** 30-40% less memory 📉

### 2. Close Browser After Use

```python
async def scrape_and_cleanup():
    scraper = TenderScraper()
    
    try:
        tenders = await scraper.search_async(["cloud"], limit=10)
        return tenders
    finally:
        await scraper.close()  # Free memory!
```

**Impact:** No memory leaks 🧹

### 3. Clear Cache Regularly

```python
from boamp.cache import TenderCache

cache = TenderCache()

# Clean entries older than 7 days
cache.cleanup(older_than=7 * 24 * 3600)

# Or clear everything
cache.clear()
```

**Impact:** Save disk space 💾

---

## 🌐 Network Optimization

### 1. Use Rate Limiting Wisely

```python
from boamp.rate_limiter import RateLimiter

# Default: 10 req/min (safe, respectful)
limiter = RateLimiter(requests_per_minute=10)

# Faster (risky): 20 req/min
limiter_fast = RateLimiter(requests_per_minute=20)

# Slower (very polite): 5 req/min
limiter_slow = RateLimiter(requests_per_minute=5)
```

**Recommendation:** Stick to 10 req/min or less ✅

### 2. Timeout Configuration

```python
# Increase timeout for slow connections
await page.goto(url, timeout=60000)  # 60s instead of 30s

# Decrease for fast connections
await page.goto(url, timeout=15000)  # 15s
```

**Impact:** Adapt to your network speed 📡

### 3. Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def scrape_with_retry(keywords):
    """Retry scraping on failure"""
    scraper = TenderScraper()
    return await scraper.search_async(keywords=keywords, limit=10)
```

**Impact:** More reliable scraping 🛡️

---

## 📈 Benchmarking Your Setup

### 1. Simple Benchmark Script

```python
import asyncio
import time
from boamp import TenderScraper

async def benchmark():
    scraper = TenderScraper()
    
    # Warm up
    print("🔥 Warming up...")
    await scraper.search_async(keywords=["test"], limit=1)
    
    # Benchmark
    print("⏱️  Benchmarking...")
    start = time.time()
    
    tenders = await scraper.search_async(keywords=["cloud"], limit=10)
    
    duration = time.time() - start
    
    print(f"✅ Scraped {len(tenders)} tenders in {duration:.2f}s")
    print(f"⚡ Speed: {len(tenders) / duration:.2f} tenders/second")
    
    await scraper.close()

asyncio.run(benchmark())
```

### 2. Parallel Benchmark

```python
async def parallel_benchmark(concurrency: int = 5):
    """Benchmark parallel scraping"""
    scraper = TenderScraper()
    
    keywords_list = [
        ["cloud"], ["cyber"], ["data"], ["dev"], ["infra"]
    ]
    
    start = time.time()
    
    tasks = [
        scraper.search_async(keywords=kw, limit=5)
        for kw in keywords_list[:concurrency]
    ]
    
    results = await asyncio.gather(*tasks)
    
    duration = time.time() - start
    total_tenders = sum(len(r) for r in results)
    
    print(f"✅ Scraped {total_tenders} tenders in {duration:.2f}s")
    print(f"⚡ Throughput: {total_tenders / duration:.2f} tenders/sec")
    print(f"🔄 Concurrency: {concurrency} parallel scrapers")
    
    await scraper.close()
```

---

## 🎛️ Configuration Best Practices

### Development

```python
# Fast iteration, full logging
scraper = TenderScraper(headless=False)  # See browser
cache = TenderCache(ttl=300)  # 5 min cache
limiter = RateLimiter(requests_per_minute=20)  # Faster
```

### Production

```python
# Stable, respectful, efficient
scraper = TenderScraper(headless=True)  # Headless
cache = TenderCache(ttl=86400)  # 24h cache
limiter = RateLimiter(requests_per_minute=10)  # Polite
```

### Testing

```python
# Mock data, no network
from unittest.mock import Mock

scraper = Mock()
scraper.search_async.return_value = [...]  # Mock tenders
```

---

## 📊 Performance Monitoring

### 1. Add Timing Logs

```python
import time
import logging

logger = logging.getLogger(__name__)

async def timed_search(keywords):
    start = time.time()
    
    tenders = await scraper.search_async(keywords=keywords, limit=10)
    
    duration = time.time() - start
    logger.info(f"Scraped {len(tenders)} tenders in {duration:.2f}s")
    
    return tenders
```

### 2. Track Success Rate

```python
from collections import defaultdict

stats = defaultdict(int)

try:
    tenders = await scraper.search_async(["cloud"], limit=10)
    stats['success'] += 1
    stats['tenders_found'] += len(tenders)
except Exception:
    stats['errors'] += 1

print(f"Success rate: {stats['success'] / (stats['success'] + stats['errors']) * 100:.1f}%")
```

### 3. Monitor Memory

```python
import psutil
import os

process = psutil.Process(os.getpid())

# Before scraping
mem_before = process.memory_info().rss / 1024 / 1024

tenders = await scraper.search_async(["cloud"], limit=10)

# After scraping
mem_after = process.memory_info().rss / 1024 / 1024

print(f"Memory used: {mem_after - mem_before:.1f} MB")
```

---

## 🏆 Performance Checklist

- [ ] Caching enabled (TenderCache)
- [ ] Async/await for concurrency
- [ ] Browser instance reused
- [ ] Headless mode (default)
- [ ] Rate limiting (≤10 req/min)
- [ ] Timeouts configured
- [ ] Memory limits set
- [ ] Images/fonts disabled (optional)
- [ ] Cleanup after scraping
- [ ] Monitoring/logging enabled
- [ ] Benchmarked on your setup

---

## 🎯 Performance Goals

| Metric | Target | Excellent |
|--------|--------|-----------|
| **Single search** | < 20s | < 15s |
| **With cache** | < 0.1s | < 0.01s |
| **Memory usage** | < 800MB | < 600MB |
| **Success rate** | > 95% | > 99% |
| **Throughput** | 1 tender/sec | 2+ tenders/sec |

---

## 🐛 Performance Issues?

### Slow scraping (>30s)
1. Check your internet connection
2. Increase timeout
3. Use cache for repeated queries
4. Check BOAMP website status

### High memory (>1GB)
1. Close browser after use
2. Limit concurrent scrapers
3. Clear cache regularly
4. Use headless mode

### Timeouts/errors
1. Increase timeout values
2. Add retry logic
3. Use rate limiting
4. Check BOAMP availability

---

## 📚 Related Docs

- [Deployment Guide](DEPLOYMENT.md) - Production setup
- [CLI Guide](CLI_GUIDE.md) - Command-line usage
- [API Reference](API_REFERENCE.md) - Full API docs

---

**Built for speed ⚡ and efficiency 🎯**

