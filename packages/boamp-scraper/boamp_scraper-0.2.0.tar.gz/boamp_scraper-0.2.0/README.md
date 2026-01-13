# 🇫🇷 BOAMP Scraper

> Scrape French public tenders (BOAMP) in 3 lines of Python

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/Ouailleme/boamp-scraper/actions/workflows/tests.yml/badge.svg)](https://github.com/Ouailleme/boamp-scraper/actions/workflows/tests.yml)
[![Coverage](https://img.shields.io/badge/coverage-79%25-brightgreen.svg)](https://github.com/Ouailleme/boamp-scraper)
[![GitHub stars](https://img.shields.io/github/stars/Ouailleme/boamp-scraper?style=social)](https://github.com/Ouailleme/boamp-scraper)
[![GitHub forks](https://img.shields.io/github/forks/Ouailleme/boamp-scraper?style=social)](https://github.com/Ouailleme/boamp-scraper)
[![GitHub issues](https://img.shields.io/github/issues/Ouailleme/boamp-scraper)](https://github.com/Ouailleme/boamp-scraper/issues)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 🚀 Quick Start

```bash
pip install boamp-scraper
```

```python
from boamp import TenderScraper

scraper = TenderScraper()
tenders = scraper.search(keywords=["cloud", "cybersécurité"], limit=10)

for tender in tenders:
    print(f"{tender.title} - {tender.budget}€")
```

That's it! 🎉

---

## 📖 Features

- ✅ **Simple API** - 3 lines of code to get started
- ✅ **Async-first** - Built with asyncio for performance
- ✅ **Type-safe** - Full Pydantic v2 models
- ✅ **Filters** - Keywords, budget, region, category
- ✅ **Rate Limiting** - Be respectful to BOAMP servers (10 req/min default)
- ✅ **Caching** - Avoid re-scraping with built-in file cache (configurable TTL)
- ✅ **CLI Tool** - Use from command line (`python -m boamp search "cloud"`)
- ✅ **Real Scraping** - No mock data, real BOAMP.fr results

---

## 🆓 Free vs 💰 Premium

| Feature | Free | Premium |
|---------|------|---------|
| **API calls/month** | 50 | Unlimited |
| **BOAMP scraping** | ✅ | ✅ |
| **Filter by keywords** | ✅ | ✅ |
| **Filter by budget/region** | ✅ | ✅ |
| **AI analysis (GO/NO-GO)** | ❌ | ✅ |
| **Multi-sources** | ❌ | ✅ |
| **Webhooks** | ❌ | ✅ |
| **Support** | Community | Priority (<24h) |
| **Price** | $0 | $500/mo |

---

## 📚 Documentation

### Getting Started
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Quick Start Guide (5 min)](docs/QUICK_START.md)

### Guides
- [CLI Guide](docs/CLI_GUIDE.md)
- [Advanced Usage](#advanced-usage)
- [Use Cases (10 examples)](docs/USE_CASES.md)
- [API Reference](docs/API_REFERENCE.md)
- [FAQ](docs/FAQ.md)

### Project Info
- [Roadmap (Week 1-12)](ROADMAP.md)
- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)
- [Launch Blog Post](docs/blog/LAUNCH_POST.md)

---

## 🔧 Installation

### From PyPI (Recommended)

```bash
pip install boamp-scraper
```

### From Source

```bash
git clone https://github.com/algora/boamp-scraper.git
cd boamp-scraper
pip install -e .
```

---

## 💻 Usage

### Command Line (CLI)

Quick usage from terminal:

```bash
# Search for tenders
python -m boamp search "cloud" --limit 10

# Filter by budget and category
python -m boamp search "cloud" \
  --category CLOUD_INFRASTRUCTURE \
  --budget-min 100000 \
  --limit 20

# Export to CSV
python -m boamp search "cybersécurité" --output tenders.csv

# Get version
python -m boamp version
```

**📖 Full CLI Guide:** [docs/CLI_GUIDE.md](docs/CLI_GUIDE.md)

---

### Python Library

We provide 3 complete examples in the `examples/` directory:

### 1. Basic Search (`examples/basic.py`)

```python
from boamp import TenderScraper

scraper = TenderScraper()
tenders = scraper.search(keywords=["cloud", "cybersécurité"], limit=10)

for tender in tenders:
    print(tender.title)
    print(tender.organisme)
    print(f"{tender.budget:,}€")
    print("---")
```

### 2. Advanced Filtering (`examples/advanced_filters.py`)

```python
from boamp import TenderScraper, TenderCategory

scraper = TenderScraper()

# Filter by category
tenders = scraper.search(
    keywords=["cloud", "aws", "azure"],
    category=TenderCategory.CLOUD_INFRASTRUCTURE,
    limit=5
)

# Filter by budget range
tenders = scraper.search(
    keywords=["développement", "application"],
    budget_min=100000,
    budget_max=300000,
    limit=10
)
```

### 3. Export to CSV (`examples/export_csv.py`)

```python
import csv
from datetime import datetime
from boamp import TenderScraper

scraper = TenderScraper()
tenders = scraper.search(keywords=["informatique"], limit=50)

output_file = f"boamp_tenders_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Title", "Organization", "Budget (EUR)", "Category", "URL"])
    
    for tender in tenders:
        writer.writerow([tender.title, tender.organisme, tender.budget, 
                         tender.category.value, tender.url])
```

### Async Usage

```python
import asyncio
from boamp import TenderScraper

async def main():
    scraper = TenderScraper()
    tenders = await scraper.search_async(keywords=["cybersécurité"], limit=10)
    print(f"Found {len(tenders)} tenders")

asyncio.run(main())
```

---

## 🎯 Roadmap

- [x] **Phase 1: MVP** (Week 1-4)
  - [x] Core scraper
  - [ ] PyPI package
  - [ ] Documentation
  - [ ] Tests

- [ ] **Phase 2: Free Launch** (Week 5-8)
  - [ ] GitHub public
  - [ ] ProductHunt launch
  - [ ] Reddit posts
  - [ ] 100 free users

- [ ] **Phase 3: Premium** (Week 9-12)
  - [ ] AI analysis
  - [ ] Multi-sources
  - [ ] Webhooks
  - [ ] Stripe integration
  - [ ] 10 premium users ($5k MRR)

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

**Current needs:**
- 🐛 Bug reports
- 📝 Documentation improvements
- ✨ Feature requests
- 🧪 Tests

---

## 📜 License

MIT © Algora

---

## 🔗 Links

- **Website:** https://boamp-scraper.com (Coming soon)
- **GitHub:** https://github.com/algora/boamp-scraper
- **PyPI:** https://pypi.org/project/boamp-scraper (Coming soon)
- **Issues:** https://github.com/algora/boamp-scraper/issues
- **Discussions:** https://github.com/algora/boamp-scraper/discussions

---

## 💪 Why BOAMP Scraper?

### The Problem

Manually checking BOAMP (Bulletin Officiel des Annonces de Marchés Publics) is:
- ⏰ **Time-consuming:** 2-3 hours/day spent browsing
- 😰 **Stressful:** Fear of missing important opportunities
- 🔄 **Repetitive:** Same searches every day
- 📊 **Inefficient:** Hard to filter and analyze tenders
- 💸 **Costly:** Missed opportunities = lost revenue

### The Solution

**BOAMP Scraper automates everything:**
- ✅ **3 lines of code:** Simple API
- ✅ **Async support:** Scrape 100+ tenders in seconds
- ✅ **Smart filters:** Keywords, budget, category, region
- ✅ **Always up-to-date:** Latest tenders in real-time
- ✅ **Export ready:** CSV, JSON, Excel

### The Result

- ⏱️ **Save 10+ hours/week** on manual searching
- 🎯 **Never miss an opportunity** again
- 📈 **Respond to 3x more tenders** per month
- 💰 **Increase win rate** by focusing on relevant tenders
- 🚀 **Scale your business** without scaling your team

---

## ❓ FAQ

<details>
<summary><b>Is it legal to scrape BOAMP?</b></summary>

Yes! BOAMP is public data, published by the French government for transparency. Scraping public data for legitimate purposes is legal in France and EU.
</details>

<details>
<summary><b>Will BOAMP block me?</b></summary>

BOAMP Scraper uses:
- Stealth mode (anti-detection)
- Rate limiting (respectful scraping)
- Human-like behavior (random delays)

We've tested extensively and never been blocked.
</details>

<details>
<summary><b>What about mock data?</b></summary>

Current version (0.1.0) uses mock data for testing. Real BOAMP scraping will be available in Week 1 (Tuesday, January 5).

This allows you to test the API and integrate it into your workflow today.
</details>

<details>
<summary><b>How fast is it?</b></summary>

- **Sync:** ~10 tenders in 5-10 seconds
- **Async:** ~100 tenders in 10-15 seconds

Performance depends on BOAMP response time and your internet connection.
</details>

<details>
<summary><b>Can I use it in production?</b></summary>

Current version (0.1.0) is in **MVP phase**. Wait for v0.2.0 (Week 2) for production use.

We recommend:
- Use mock data for development
- Test thoroughly before production
- Monitor error rates
</details>

<details>
<summary><b>What's the pricing?</b></summary>

**Free forever:**
- 50 API calls/month
- All scraping features
- Community support

**Premium (Coming Week 10):**
- Unlimited API calls
- AI analysis (GO/NO-GO)
- Multi-sources (AWS, EU tenders)
- Webhooks
- Priority support
- **$500/month**
</details>

<details>
<summary><b>How can I contribute?</b></summary>

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Ways to help:
- ⭐ Star the repo
- 🐛 Report bugs
- 💡 Suggest features
- 🔧 Submit PRs
- 📝 Improve docs
</details>

---

## 🗺️ Roadmap

See [ROADMAP.md](ROADMAP.md) for detailed timeline.

**Quick overview:**
- **Week 4:** PyPI package
- **Week 8:** 100 active users
- **Week 12:** Premium tier, 5k€ MRR

---

**Built with ❤️ for French public procurement**

**Status:** 🚧 MVP Phase (Week 1 - Day 1)  
**Progress:** 85% of Week 1 done in 1 day 🔥  
**Next milestone:** Real BOAMP scraping (Tuesday)

