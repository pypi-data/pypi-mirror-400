# Introducing BOAMP Scraper: Scrape French Public Tenders in 3 Lines of Python

**Published:** January 4, 2026  
**Author:** Algora  
**Tags:** Python, Open Source, Web Scraping, Public Procurement, France

---

## TL;DR

BOAMP Scraper is a Python library that makes scraping French public tenders (BOAMP) as simple as:

```python
from boamp import TenderScraper

scraper = TenderScraper()
tenders = scraper.search(keywords=["cloud"], limit=10)
```

**Features:** Async support, smart filters, type-safe, production-ready.  
**License:** MIT  
**Status:** Open source, 100% free

👉 **Get started:** `pip install boamp-scraper` (coming Week 4)  
👉 **GitHub:** https://github.com/Ouailleme/boamp-scraper

---

## The Problem

If you've ever tried to monitor French public tenders (BOAMP - Bulletin Officiel des Annonces de Marchés Publics), you know the pain:

- ⏰ **2-3 hours/day** spent manually browsing
- 😰 **Fear of missing** important opportunities
- 🔄 **Repetitive work** checking the same searches
- 📊 **No easy way** to filter, analyze, or export data
- 💸 **Lost revenue** from missed tenders

For IT consulting firms, freelancers, and business developers, this manual process is:
- **Time-consuming**
- **Error-prone**
- **Not scalable**

We built BOAMP Scraper to solve this problem.

---

## The Solution

### 1. Simple API

No complex setup, no configuration files. Just 3 lines:

```python
from boamp import TenderScraper

scraper = TenderScraper()
tenders = scraper.search(keywords=["cybersécurité"], limit=10)

for tender in tenders:
    print(f"{tender.title} - {tender.budget:,}€")
```

### 2. Smart Filters

Find exactly what you need:

```python
tenders = scraper.search(
    keywords=["cloud", "aws"],
    category=TenderCategory.CLOUD_INFRASTRUCTURE,
    budget_min=100000,
    budget_max=500000,
    limit=50
)
```

### 3. Type-Safe (Pydantic v2)

All models are validated with Pydantic:

```python
class Tender(BaseModel):
    title: str
    organisme: str
    budget: int
    category: TenderCategory
    url: str
    # ... and more
```

No more `KeyError` or `None` surprises!

### 4. Async Support

Need speed? Use async:

```python
tenders = await scraper.search_async(keywords=["cloud"], limit=100)
```

Scrape 100+ tenders in seconds, not minutes.

### 5. Export Ready

CSV, JSON, Excel - your choice:

```python
import csv

with open("tenders.csv", "w") as f:
    writer = csv.writer(f)
    for tender in tenders:
        writer.writerow([tender.title, tender.budget, tender.url])
```

---

## Real-World Use Cases

### 1. **Daily Monitoring** (ESN, Consulting Firms)

```python
# daily_report.py
tenders = scraper.search(
    keywords=["cloud", "cybersécurité"],
    budget_min=50000,
    limit=50
)

send_email_report(tenders)  # Your SMTP logic
```

**Schedule with cron:**
```bash
0 9 * * * python daily_report.py
```

**Result:** Save 2h/day, never miss an opportunity.

---

### 2. **Freelance Lead Generation**

```python
# Find high-value projects for freelancers
tenders = scraper.search(
    keywords=["architecte cloud", "migration aws"],
    budget_min=100000,
    budget_max=300000,
    limit=100
)

# Score and export top opportunities
scored_leads = score_by_relevance(tenders)
export_to_csv(scored_leads[:10], "top_leads.csv")
```

**Result:** Focus on best opportunities, increase revenue by 50k€/year.

---

### 3. **Competitive Intelligence**

```python
# Track who's buying what in your niche
tenders = scraper.search(
    keywords=["cybersécurité", "pentest"],
    limit=200
)

# Analyze market
stats = {
    "total_budget": sum(t.budget for t in tenders),
    "top_buyers": Counter(t.organisme for t in tenders).most_common(5)
}
```

**Result:** Know the market, target high-activity buyers.

---

## Why We Built This

As IT consultants ourselves, we spent too much time manually checking BOAMP. We built BOAMP Scraper to:

1. **Save time** (10+ hours/week)
2. **Never miss opportunities** (automated monitoring)
3. **Make data actionable** (easy filtering and export)
4. **Share with the community** (open source, MIT license)

---

## Technical Stack

- **Python 3.10+**
- **Playwright** (headless browser, stealth mode)
- **Pydantic v2** (data validation)
- **Async/await** (performance)
- **pytest** (19 tests, 79% coverage)
- **CI/CD** (GitHub Actions)

---

## What's Next?

### Week 4 (January 25)
- 📦 **PyPI publish** - `pip install boamp-scraper`
- 📚 Complete documentation
- 🎥 Video tutorials

### Week 8 (February 22)
- 🚀 ProductHunt launch
- 🌟 Goal: 100 active users, 200+ GitHub stars

### Week 12 (March 22)
- 🤖 **Premium tier:** AI analysis (GO/NO-GO decision)
- 🔗 Multi-sources (AWS, EU tenders)
- 📡 Webhooks (real-time notifications)
- 💰 Pricing: $500/month unlimited

---

## How You Can Help

### ⭐ Star the repo
Show your support: https://github.com/Ouailleme/boamp-scraper

### 🐛 Report bugs
Found an issue? Open a GitHub issue.

### 💡 Suggest features
What would make BOAMP Scraper more useful for you?

### 🔧 Contribute
We welcome pull requests! See [CONTRIBUTING.md](../CONTRIBUTING.md)

---

## Get Started

### 1. Clone the repo
```bash
git clone https://github.com/Ouailleme/boamp-scraper.git
cd boamp-scraper
pip install -e .
```

### 2. Try the examples
```bash
python examples/basic.py
```

### 3. Read the docs
- [Quick Start Guide](../QUICK_START.md)
- [Use Cases](../USE_CASES.md)
- [API Reference](../../README.md)

---

## Conclusion

BOAMP Scraper makes French public tender monitoring **simple**, **fast**, and **scalable**.

Whether you're a freelancer, a consulting firm, or a business developer, BOAMP Scraper saves you time and helps you win more contracts.

**Try it today:** https://github.com/Ouailleme/boamp-scraper

---

## About the Author

**Algora** is building tools for the French public procurement ecosystem. Our mission: make tender monitoring accessible to everyone.

**Connect:**
- GitHub: [@Ouailleme](https://github.com/Ouailleme)
- Email: contact@algora.fr

---

**Status:** MVP Phase (Week 1)  
**License:** MIT  
**Last Updated:** January 4, 2026

**Built with ❤️ for French public procurement**

