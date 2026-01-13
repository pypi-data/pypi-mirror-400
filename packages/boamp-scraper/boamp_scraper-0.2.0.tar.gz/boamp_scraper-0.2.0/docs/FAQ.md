# Frequently Asked Questions (FAQ)

Common questions and answers about BOAMP Scraper.

---

## General

### What is BOAMP Scraper?

BOAMP Scraper is a Python library for scraping French public tenders from [BOAMP.fr](https://www.boamp.fr) (Bulletin Officiel des Annonces de Marchés Publics).

It provides a simple, type-safe API to search, filter, and export tender data.

---

### Is it free?

Yes! BOAMP Scraper is 100% free and open source (MIT License).

**Premium features** (coming Week 12):
- AI tender analysis (GO/NO-GO decisions)
- Multi-source scraping (AWS, EU tenders)
- Webhooks & real-time notifications
- Priority support

Pricing: $500/month unlimited.

---

### Is it legal to scrape BOAMP?

**Yes.** BOAMP is a public database of French public procurement. All data is publicly accessible.

**However:**
- Respect rate limits (don't DDoS BOAMP)
- Don't resell raw BOAMP data
- Use responsibly

BOAMP Scraper includes built-in rate limiting and stealth mode to be respectful.

---

## Installation

### How do I install it?

**Option 1: PyPI (coming Week 4)**
```bash
pip install boamp-scraper
```

**Option 2: From source (now)**
```bash
git clone https://github.com/Ouailleme/boamp-scraper.git
cd boamp-scraper
pip install -e .
playwright install chromium
```

---

### What are the requirements?

- **Python 3.10+**
- **Playwright** (headless browser)
- **Internet connection** (to access BOAMP.fr)

---

### Why Playwright and not BeautifulSoup?

BOAMP uses JavaScript rendering. Simple HTTP requests won't work.

Playwright simulates a real browser, handles JS, and includes stealth mode to avoid detection.

---

## Usage

### How do I search for tenders?

```python
from boamp import TenderScraper

scraper = TenderScraper()
tenders = scraper.search(keywords=["cloud"], limit=10)

for tender in tenders:
    print(tender.title)
```

See [Quick Start Guide](QUICK_START.md) for more examples.

---

### What filters are available?

- **keywords** (List[str]): Search terms
- **category** (TenderCategory): IT category (Cloud, Cyber, BI, etc.)
- **budget_min / budget_max** (int): Budget range in EUR
- **region** (str): Geographic region
- **limit** (int): Max results (1-500)

Example:
```python
tenders = scraper.search(
    keywords=["cloud", "aws"],
    category=TenderCategory.CLOUD_INFRASTRUCTURE,
    budget_min=100000,
    budget_max=500000,
    limit=50
)
```

---

### How fast is it?

**With mock data:** ~5 seconds per query

**Real-world estimates:**
- 10 tenders: 5-10 seconds
- 50 tenders: 20-30 seconds
- 100 tenders: 40-60 seconds

**Tips:**
- Use async mode for large queries
- Batch multiple searches with `asyncio.gather()`
- Use filters to reduce result size

See [benchmarks](../benchmarks/speed_test.py) for details.

---

### Can I export to CSV/Excel?

**Yes!** See [examples/export_csv.py](../examples/export_csv.py).

```python
import csv

with open("tenders.csv", "w") as f:
    writer = csv.writer(f)
    for tender in tenders:
        writer.writerow([tender.title, tender.budget, tender.url])
```

For Excel, use `pandas`:
```python
import pandas as pd

df = pd.DataFrame([t.model_dump() for t in tenders])
df.to_excel("tenders.xlsx", index=False)
```

---

## Troubleshooting

### I get "TimeoutError"

**Cause:** BOAMP didn't respond in 30s.

**Solutions:**
1. Check your internet connection
2. Check if BOAMP.fr is up (visit in browser)
3. Reduce `limit` (fewer results = faster)
4. Try again later (BOAMP might be slow)

---

### I get "ConnectionError"

**Cause:** Network issues or BOAMP is down.

**Solutions:**
1. Check internet connection
2. Check if BOAMP.fr is up
3. Check firewall/VPN settings
4. Try again later

---

### I get "No tenders found" but I know they exist

**Current reason:** Mock data is enabled (`Config.USE_MOCK_DATA = True`).

Real scraping (Week 2-3) will fix this.

**Future troubleshooting:**
1. Try broader keywords
2. Remove filters (category, budget, region)
3. Increase `limit`
4. Check BOAMP.fr manually to verify tenders exist

---

### The scraper is slow

**Tips:**
1. Use async mode: `await scraper.search_async()`
2. Reduce `limit` (fewer results)
3. Use specific filters (category, budget) to reduce search space
4. Batch multiple searches with `asyncio.gather()`

**Note:** BOAMP response time is out of our control. If BOAMP is slow, scraping will be slow.

---

### I want to run headful mode (see browser)

```python
scraper = TenderScraper(headless=False)
```

Useful for debugging.

---

## Advanced

### Can I scrape 1000+ tenders?

**Yes**, but:
1. Split into batches (e.g., 10 queries of 100 each)
2. Use async with `asyncio.gather()`
3. Add delays between batches (be respectful)
4. Consider using filters to reduce total

**Example:**
```python
async def scrape_large():
    scraper = TenderScraper()
    
    # Batch 1-10 in parallel
    batches = await asyncio.gather(*[
        scraper.search_async(keywords=["cloud"], limit=100, offset=i*100)
        for i in range(10)
    ])
    
    all_tenders = [t for batch in batches for t in batch]
    return all_tenders
```

---

### Can I schedule daily scraping?

**Yes!**

**Option 1: Cron (Linux/Mac)**
```bash
# Every day at 9 AM
0 9 * * * python /path/to/your_script.py
```

**Option 2: Task Scheduler (Windows)**
- Open Task Scheduler
- Create Basic Task
- Trigger: Daily at 9 AM
- Action: Run `python your_script.py`

**Option 3: Python APScheduler**
```python
from apscheduler.schedulers.blocking import BlockingScheduler

def scrape_daily():
    scraper = TenderScraper()
    tenders = scraper.search(keywords=["cloud"], limit=50)
    # Send email, save to DB, etc.

scheduler = BlockingScheduler()
scheduler.add_job(scrape_daily, 'cron', hour=9)
scheduler.start()
```

---

### Can I integrate with my CRM/Database?

**Yes!** Tenders are Pydantic models, easy to serialize:

**SQLite:**
```python
import sqlite3

conn = sqlite3.connect("tenders.db")
cursor = conn.cursor()

for tender in tenders:
    cursor.execute(
        "INSERT INTO tenders VALUES (?, ?, ?, ?)",
        (tender.title, tender.organisme, tender.budget, tender.url)
    )

conn.commit()
```

**PostgreSQL/MySQL:**
```python
import psycopg2

conn = psycopg2.connect("...")
cursor = conn.cursor()

for tender in tenders:
    cursor.execute(
        "INSERT INTO tenders (...) VALUES (%s, %s, %s, %s)",
        (tender.title, tender.organisme, tender.budget, tender.url)
    )

conn.commit()
```

**MongoDB:**
```python
from pymongo import MongoClient

client = MongoClient("...")
db = client.tenders
collection = db.tenders

for tender in tenders:
    collection.insert_one(tender.model_dump())
```

---

### Can I send email notifications?

**Yes!**

```python
import smtplib
from email.mime.text import MIMEText

def send_tenders_email(tenders):
    body = "\n".join([f"{t.title} - {t.budget}€" for t in tenders])
    
    msg = MIMEText(body)
    msg["Subject"] = f"New tenders: {len(tenders)}"
    msg["From"] = "bot@example.com"
    msg["To"] = "you@example.com"
    
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("bot@example.com", "password")
        server.send_message(msg)
```

---

## Contributing

### How can I contribute?

See [CONTRIBUTING.md](../CONTRIBUTING.md).

**Ways to contribute:**
1. ⭐ Star the repo
2. 🐛 Report bugs
3. 💡 Suggest features
4. 🔧 Submit pull requests
5. 📚 Improve documentation

---

### I found a bug, what do I do?

1. Check if it's already reported: [GitHub Issues](https://github.com/Ouailleme/boamp-scraper/issues)
2. If not, open a new issue with:
   - Python version
   - OS (Windows/Mac/Linux)
   - Error message
   - Steps to reproduce

---

### Can I request a feature?

**Yes!** Open a GitHub issue with:
- Feature description
- Use case (why you need it)
- Example API (how you'd like to use it)

We prioritize features based on community votes (👍 reactions).

---

## Support

### Where can I get help?

1. **Read the docs:**
   - [README](../README.md)
   - [Quick Start](QUICK_START.md)
   - [API Reference](API_REFERENCE.md)
   - [Use Cases](USE_CASES.md)

2. **GitHub Issues:** https://github.com/Ouailleme/boamp-scraper/issues

3. **Email:** contact@algora.fr

---

### Is there a community?

Not yet! We're building it.

**Join us:**
- ⭐ Star the repo
- 👥 Follow [@Ouailleme](https://github.com/Ouailleme)
- 📧 Subscribe to updates

---

## License

### What license is it?

**MIT License** - You can use it for anything (commercial, personal, etc.).

See [LICENSE](../LICENSE) for details.

---

### Can I use it commercially?

**Yes!** The MIT License allows commercial use.

---

### Can I modify it?

**Yes!** Fork it, modify it, do whatever you want.

If you make something cool, please contribute back! 🙏

---

**Last Updated:** January 4, 2026  
**Version:** 0.1.0

**Have more questions? Open an issue:** https://github.com/Ouailleme/boamp-scraper/issues

