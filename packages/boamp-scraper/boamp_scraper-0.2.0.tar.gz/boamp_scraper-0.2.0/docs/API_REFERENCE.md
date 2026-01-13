# API Reference

Complete API documentation for BOAMP Scraper.

---

## Table of Contents

- [TenderScraper](#tenderscraper)
- [Models](#models)
  - [Tender](#tender)
  - [TenderCategory](#tendercategory)
  - [SearchFilters](#searchfilters)
- [Examples](#examples)

---

## TenderScraper

### Constructor

```python
TenderScraper(headless: bool = True)
```

Creates a new scraper instance.

**Parameters:**
- `headless` (bool, optional): Run browser in headless mode. Default: `True`

**Example:**
```python
scraper = TenderScraper()  # Headless mode
scraper = TenderScraper(headless=False)  # Show browser
```

---

### Methods

#### `search`

```python
def search(
    keywords: List[str] = [],
    category: Optional[TenderCategory] = None,
    budget_min: Optional[int] = None,
    budget_max: Optional[int] = None,
    region: Optional[str] = None,
    limit: int = 50
) -> List[Tender]
```

Search for tenders (synchronous wrapper around `search_async`).

**Parameters:**
- `keywords` (List[str], optional): Keywords to search for. Default: `[]`
- `category` (TenderCategory, optional): Filter by category. Default: `None` (all)
- `budget_min` (int, optional): Minimum budget in EUR. Default: `None`
- `budget_max` (int, optional): Maximum budget in EUR. Default: `None`
- `region` (str, optional): Filter by region. Default: `None`
- `limit` (int, optional): Maximum number of results (1-500). Default: `50`

**Returns:**
- `List[Tender]`: List of tender objects

**Raises:**
- `ValueError`: If limit is out of bounds (1-500)
- `TimeoutError`: If BOAMP doesn't respond
- `ConnectionError`: If network issues

**Example:**
```python
tenders = scraper.search(keywords=["cloud"], limit=10)
```

---

#### `search_async`

```python
async def search_async(
    keywords: List[str] = [],
    category: Optional[TenderCategory] = None,
    budget_min: Optional[int] = None,
    budget_max: Optional[int] = None,
    region: Optional[str] = None,
    limit: int = 50
) -> List[Tender]
```

Search for tenders (asynchronous version, recommended for performance).

**Parameters:** Same as `search()`

**Returns:** Same as `search()`

**Example:**
```python
tenders = await scraper.search_async(keywords=["cloud"], limit=10)
```

---

## Models

### Tender

Represents a single tender from BOAMP.

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `title` | `str` | Tender title |
| `organisme` | `str` | Organization name |
| `budget` | `int` | Budget in EUR (0 if unknown) |
| `date_publication` | `datetime` | Publication date |
| `url` | `str` | Tender URL on BOAMP |
| `category` | `TenderCategory` | Tender category |
| `region` | `Optional[str]` | Region (if specified) |
| `description` | `Optional[str]` | Short description (if available) |

**Methods:**

```python
def model_dump() -> dict
```

Serialize to dictionary.

```python
def model_dump_json() -> str
```

Serialize to JSON string.

**Example:**
```python
tender = Tender(
    title="Cloud infrastructure",
    organisme="Ministère",
    budget=150000,
    date_publication=datetime.now(),
    url="https://...",
)

# Access attributes
print(tender.title)
print(tender.budget)

# Serialize
data = tender.model_dump()
json_str = tender.model_dump_json()
```

---

### TenderCategory

Enum of tender categories.

**Values:**

| Value | Description (French) |
|-------|---------------------|
| `IT_DEVELOPMENT` | Développement informatique |
| `CLOUD_INFRASTRUCTURE` | Cloud et infrastructure |
| `CYBERSECURITY` | Cybersécurité |
| `BI_DATA` | BI et Data |
| `MOBILE` | Applications mobiles |
| `WEB` | Développement web |
| `MAINTENANCE` | Maintenance et support |
| `CONSULTING` | Conseil IT |
| `OTHER` | Autre |

**Example:**
```python
from boamp import TenderCategory

category = TenderCategory.CLOUD_INFRASTRUCTURE
print(category.value)  # "Cloud et infrastructure"
```

---

### SearchFilters

Type-safe search filters (used internally, can also be passed as kwargs).

**Attributes:**

| Attribute | Type | Default | Validation |
|-----------|------|---------|------------|
| `keywords` | `List[str]` | `[]` | - |
| `category` | `Optional[TenderCategory]` | `None` | - |
| `budget_min` | `Optional[int]` | `None` | >= 0 |
| `budget_max` | `Optional[int]` | `None` | >= 0 |
| `region` | `Optional[str]` | `None` | - |
| `limit` | `int` | `50` | 1-500 |

**Example:**
```python
from boamp.models import SearchFilters, TenderCategory

filters = SearchFilters(
    keywords=["cloud"],
    category=TenderCategory.CLOUD_INFRASTRUCTURE,
    budget_min=50000,
    budget_max=500000,
    limit=100
)
```

---

## Examples

### Basic Search

```python
from boamp import TenderScraper

scraper = TenderScraper()
tenders = scraper.search(keywords=["cloud"], limit=10)

for tender in tenders:
    print(f"{tender.title} - {tender.budget:,}€")
```

---

### Advanced Filtering

```python
from boamp import TenderScraper, TenderCategory

scraper = TenderScraper()

tenders = scraper.search(
    keywords=["cloud", "aws"],
    category=TenderCategory.CLOUD_INFRASTRUCTURE,
    budget_min=100000,
    budget_max=500000,
    limit=50
)
```

---

### Async (Recommended)

```python
import asyncio
from boamp import TenderScraper

async def main():
    scraper = TenderScraper()
    tenders = await scraper.search_async(keywords=["cloud"], limit=10)
    print(f"Found {len(tenders)} tenders")

asyncio.run(main())
```

---

### Export to CSV

```python
import csv
from boamp import TenderScraper

scraper = TenderScraper()
tenders = scraper.search(keywords=["cloud"], limit=50)

with open("tenders.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Title", "Organization", "Budget", "URL"])
    
    for tender in tenders:
        writer.writerow([
            tender.title,
            tender.organisme,
            tender.budget,
            tender.url
        ])
```

---

### Error Handling

```python
from boamp import TenderScraper

scraper = TenderScraper()

try:
    tenders = scraper.search(keywords=["cloud"], limit=10)
except ValueError as e:
    print(f"Invalid parameters: {e}")
except TimeoutError:
    print("BOAMP didn't respond in time")
except ConnectionError:
    print("Network error")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

### Multiple Searches (Parallel)

```python
import asyncio
from boamp import TenderScraper

async def main():
    scraper = TenderScraper()
    
    # Run multiple searches in parallel
    results = await asyncio.gather(
        scraper.search_async(keywords=["cloud"], limit=10),
        scraper.search_async(keywords=["cybersécurité"], limit=10),
        scraper.search_async(keywords=["mobile"], limit=10),
    )
    
    cloud_tenders, cyber_tenders, mobile_tenders = results
    
    print(f"Cloud: {len(cloud_tenders)}")
    print(f"Cyber: {len(cyber_tenders)}")
    print(f"Mobile: {len(mobile_tenders)}")

asyncio.run(main())
```

---

## Configuration

### Environment Variables

None required (scraper is zero-config).

### Browser Settings

By default, the scraper uses:
- Chromium (via Playwright)
- Headless mode
- Stealth mode (evades detection)
- 30s page timeout

---

## Performance

### Benchmarks (Mock Data)

| Query Size | Duration | Throughput |
|------------|----------|------------|
| 10 tenders | ~5s | 0.2/sec |
| 50 tenders | ~5s | 0.6/sec |
| 100 tenders | ~5s | Variable |

**Note:** Real scraping will be slower (network latency, BOAMP response time).

### Tips

1. **Use async for large queries** (50+ tenders)
2. **Batch multiple searches** with `asyncio.gather()`
3. **Set reasonable limits** (avoid 500+ in one call)
4. **Use filters** to reduce result set

---

## Support

- **GitHub Issues:** https://github.com/Ouailleme/boamp-scraper/issues
- **Docs:** https://github.com/Ouailleme/boamp-scraper
- **Email:** contact@algora.fr

---

**Last Updated:** January 4, 2026  
**Version:** 0.1.0

