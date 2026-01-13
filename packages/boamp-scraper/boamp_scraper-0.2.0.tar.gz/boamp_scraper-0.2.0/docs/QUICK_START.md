# ⚡ Quick Start Guide

> Get started with BOAMP Scraper in 5 minutes

---

## 📦 Installation

### Option 1: pip (Recommended)

```bash
pip install boamp-scraper
```

### Option 2: From source

```bash
git clone https://github.com/Ouailleme/boamp-scraper.git
cd boamp-scraper
pip install -e .
```

### Option 3: Poetry

```bash
poetry add boamp-scraper
```

---

## 🚀 First Steps

### 1. Basic Search

Create a file `my_scraper.py`:

```python
from boamp import TenderScraper

# Create scraper
scraper = TenderScraper()

# Search for tenders
tenders = scraper.search(
    keywords=["cloud", "cybersécurité"],
    limit=10
)

# Display results
for tender in tenders:
    print(f"📋 {tender.title}")
    print(f"🏢 {tender.organisme}")
    print(f"💰 {tender.budget:,}€")
    print(f"🔗 {tender.url}")
    print("---")
```

Run it:

```bash
python my_scraper.py
```

**Output:**
```
📋 Développement d'une plateforme Cloud Azure
🏢 Ministère de l'Intérieur
💰 250,000€
🔗 https://www.boamp.fr/...
---
```

---

### 2. Filter by Budget

```python
from boamp import TenderScraper

scraper = TenderScraper()

# Only tenders between 100k and 500k€
tenders = scraper.search(
    keywords=["développement"],
    budget_min=100000,
    budget_max=500000,
    limit=20
)

print(f"Found {len(tenders)} tenders in budget range")
```

---

### 3. Filter by Category

```python
from boamp import TenderScraper, TenderCategory

scraper = TenderScraper()

# Only cloud tenders
tenders = scraper.search(
    keywords=["cloud", "aws", "azure"],
    category=TenderCategory.CLOUD_INFRASTRUCTURE,
    limit=10
)

for tender in tenders:
    print(f"☁️ {tender.title} - {tender.budget:,}€")
```

---

### 4. Export to CSV

```python
import csv
from datetime import datetime
from boamp import TenderScraper

scraper = TenderScraper()
tenders = scraper.search(keywords=["informatique"], limit=50)

# Export
output_file = f"tenders_{datetime.now().strftime('%Y%m%d')}.csv"
with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Title", "Organization", "Budget", "URL"])
    
    for tender in tenders:
        writer.writerow([
            tender.title,
            tender.organisme,
            tender.budget,
            tender.url
        ])

print(f"✅ Exported to {output_file}")
```

---

### 5. Async Search (Advanced)

```python
import asyncio
from boamp import TenderScraper

async def main():
    scraper = TenderScraper()
    
    # Async search (faster for multiple queries)
    tenders = await scraper.search_async(
        keywords=["cybersécurité"],
        limit=10
    )
    
    print(f"Found {len(tenders)} tenders asynchronously")

# Run
asyncio.run(main())
```

---

## 📚 Available Categories

```python
from boamp import TenderCategory

# All available categories:
TenderCategory.IT_DEVELOPMENT       # Développement informatique
TenderCategory.CLOUD_INFRASTRUCTURE # Cloud et infrastructure
TenderCategory.CYBERSECURITY        # Cybersécurité
TenderCategory.BI_DATA              # BI et Data
TenderCategory.MOBILE               # Applications mobiles
TenderCategory.WEB                  # Développement web
TenderCategory.MAINTENANCE          # Maintenance et support
TenderCategory.CONSULTING           # Conseil IT
TenderCategory.OTHER                # Autre
```

---

## 🔍 Search Parameters

```python
scraper.search(
    keywords=["cloud"],          # List of keywords (OR logic)
    category=None,               # TenderCategory enum
    budget_min=None,             # Minimum budget in EUR
    budget_max=None,             # Maximum budget in EUR
    region=None,                 # Filter by region (future)
    limit=50                     # Max results (1-500)
)
```

---

## 💡 Tips & Best Practices

### 1. Use Specific Keywords

```python
# ❌ Too broad
tenders = scraper.search(keywords=["informatique"])

# ✅ Specific
tenders = scraper.search(keywords=["cloud", "aws", "migration"])
```

### 2. Combine Filters

```python
# Find high-value cloud tenders
tenders = scraper.search(
    keywords=["cloud", "infrastructure"],
    category=TenderCategory.CLOUD_INFRASTRUCTURE,
    budget_min=200000,
    limit=20
)
```

### 3. Handle Errors

```python
try:
    tenders = scraper.search(keywords=["cloud"], limit=10)
except Exception as e:
    print(f"Error: {e}")
```

### 4. Use Async for Speed

If you need to scrape many tenders, use async:

```python
# Sync: ~10 seconds for 100 tenders
# Async: ~5 seconds for 100 tenders
```

---

## 🐛 Troubleshooting

### Issue: No tenders found

**Cause:** Keywords too specific or no matching tenders today.

**Solution:**
- Try broader keywords
- Remove filters
- Check BOAMP website manually

### Issue: Timeout error

**Cause:** BOAMP server slow or unreachable.

**Solution:**
- Retry after 1 minute
- Check your internet connection
- Reduce `limit` parameter

### Issue: Import error

**Cause:** Package not installed correctly.

**Solution:**
```bash
pip uninstall boamp-scraper
pip install boamp-scraper
```

---

## 📖 Next Steps

1. **Read full documentation:** [README.md](../README.md)
2. **See examples:** `examples/` folder
3. **Contribute:** [CONTRIBUTING.md](../CONTRIBUTING.md)
4. **Report issues:** [GitHub Issues](https://github.com/Ouailleme/boamp-scraper/issues)

---

## 💬 Need Help?

- 📚 [Full Documentation](../README.md)
- 💡 [Examples](../examples/)
- 🐛 [Report a Bug](https://github.com/Ouailleme/boamp-scraper/issues/new?template=bug_report.md)
- 💡 [Request a Feature](https://github.com/Ouailleme/boamp-scraper/issues/new?template=feature_request.md)

---

**Happy scraping! 🚀**

