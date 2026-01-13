# CLI Guide

Complete guide for using BOAMP Scraper from the command line.

---

## Installation

```bash
pip install boamp-scraper
```

Or from source:
```bash
git clone https://github.com/Ouailleme/boamp-scraper.git
cd boamp-scraper
pip install -e .
```

---

## Basic Usage

### Get Help

```bash
python -m boamp --help
```

### Check Version

```bash
python -m boamp version
```

Output:
```
boamp-scraper v0.1.0
```

---

## Search Command

### Basic Search

Search for tenders with keywords:

```bash
python -m boamp search "cloud"
```

Output (table format):
```
🔍 Searching for: cloud
📊 Limit: 50

⏳ Scraping BOAMP...

====================================================================================================
Title                                              Organisme                              Budget
====================================================================================================
Développement d'une plateforme Cloud Azure         Ministère de l'Intérieur              250,000€
Migration infrastructure vers AWS                  Ministère de l'Éducation Nationale    300,000€
====================================================================================================
Total: 2 tenders
```

---

### Multiple Keywords

```bash
python -m boamp search "cloud" "aws" "azure"
```

---

### Limit Results

```bash
python -m boamp search "cloud" --limit 10
```

---

### Filter by Budget

```bash
# Minimum budget
python -m boamp search "cloud" --budget-min 100000

# Maximum budget
python -m boamp search "cloud" --budget-max 500000

# Budget range
python -m boamp search "cloud" --budget-min 100000 --budget-max 500000
```

---

### Filter by Category

```bash
python -m boamp search "cloud" --category CLOUD_INFRASTRUCTURE
```

**Available categories:**
- `IT_DEVELOPMENT`
- `CLOUD_INFRASTRUCTURE`
- `CYBERSECURITY`
- `BI_DATA`
- `MOBILE`
- `WEB`
- `MAINTENANCE`
- `CONSULTING`
- `OTHER`

---

### Filter by Region

```bash
python -m boamp search "cloud" --region "Île-de-France"
```

---

### Complex Filters

Combine multiple filters:

```bash
python -m boamp search "cloud" "aws" \
  --category CLOUD_INFRASTRUCTURE \
  --budget-min 100000 \
  --budget-max 500000 \
  --region "Île-de-France" \
  --limit 20
```

---

## Output Formats

### Table Format (Default)

```bash
python -m boamp search "cloud" --format table
```

Human-readable table in terminal.

---

### JSON Format

```bash
python -m boamp search "cloud" --format json
```

Output:
```json
[
  {
    "title": "Développement d'une plateforme Cloud Azure",
    "organisme": "Ministère de l'Intérieur",
    "budget": 250000,
    "category": "Cloud et infrastructure",
    "region": null,
    "url": "https://www.boamp.fr/avis/detail/xxx",
    "date_publication": "2026-01-04T10:00:00"
  }
]
```

---

### CSV Format

```bash
python -m boamp search "cloud" --format csv
```

Output:
```csv
Title,Organisme,Budget,Category,Region,URL,Date Publication
Développement d'une plateforme Cloud Azure,Ministère de l'Intérieur,250000,Cloud et infrastructure,,https://www.boamp.fr/avis/detail/xxx,2026-01-04T10:00:00
```

---

## Save to File

### Save as CSV

```bash
python -m boamp search "cloud" --output tenders.csv
```

Output:
```
✅ Saved 50 tenders to tenders.csv
```

---

### Save as JSON

```bash
python -m boamp search "cloud" --output tenders.json
```

Output:
```
✅ Saved 50 tenders to tenders.json
```

---

## Real-World Examples

### Daily Report

```bash
python -m boamp search "cloud" "cybersécurité" \
  --budget-min 50000 \
  --limit 50 \
  --output daily_report_$(date +%Y-%m-%d).csv
```

---

### Find High-Value Projects

```bash
python -m boamp search "cloud" \
  --budget-min 200000 \
  --category CLOUD_INFRASTRUCTURE \
  --limit 100 \
  --output high_value_tenders.json
```

---

### Monitor Specific Region

```bash
python -m boamp search "cybersécurité" \
  --region "Île-de-France" \
  --limit 50 \
  --output ile_de_france_cyber.csv
```

---

### Export All IT Tenders

```bash
python -m boamp search "informatique" \
  --limit 200 \
  --output all_it_tenders.csv
```

---

## Automation

### Cron Job (Linux/Mac)

Add to crontab (`crontab -e`):

```bash
# Every day at 9 AM
0 9 * * * cd /path/to/project && python -m boamp search "cloud" --limit 50 --output daily_$(date +\%Y\%m\%d).csv
```

---

### Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 9 AM
4. Action: Run program
   - Program: `python`
   - Arguments: `-m boamp search "cloud" --limit 50 --output daily.csv`
   - Start in: `C:\path\to\project`

---

### Bash Script

Create `scrape_daily.sh`:

```bash
#!/bin/bash

DATE=$(date +%Y-%m-%d)
OUTPUT="reports/tenders_$DATE.csv"

python -m boamp search "cloud" "cybersécurité" \
  --budget-min 50000 \
  --limit 100 \
  --output "$OUTPUT"

echo "✅ Report saved: $OUTPUT"

# Optional: Send email
# mail -s "BOAMP Daily Report $DATE" you@example.com < "$OUTPUT"
```

Make executable:
```bash
chmod +x scrape_daily.sh
```

Run:
```bash
./scrape_daily.sh
```

---

### PowerShell Script (Windows)

Create `scrape_daily.ps1`:

```powershell
$date = Get-Date -Format "yyyy-MM-dd"
$output = "reports\tenders_$date.csv"

python -m boamp search "cloud" "cybersécurité" `
  --budget-min 50000 `
  --limit 100 `
  --output $output

Write-Host "✅ Report saved: $output"
```

Run:
```powershell
.\scrape_daily.ps1
```

---

## Tips & Best Practices

### 1. Start Small

Test with small limits first:
```bash
python -m boamp search "cloud" --limit 5
```

---

### 2. Use Specific Keywords

More specific = better results:
```bash
# Generic (lots of noise)
python -m boamp search "informatique"

# Specific (relevant)
python -m boamp search "architecte cloud aws"
```

---

### 3. Combine Filters

Use multiple filters to reduce noise:
```bash
python -m boamp search "cloud" \
  --category CLOUD_INFRASTRUCTURE \
  --budget-min 100000
```

---

### 4. Save to Files

Don't rely on terminal output for large queries:
```bash
python -m boamp search "cloud" --limit 100 --output results.csv
```

---

### 5. Schedule Regular Scraping

Automate with cron/Task Scheduler for daily monitoring.

---

## Troubleshooting

### Command Not Found

**Problem:**
```
bash: boamp: command not found
```

**Solution:**
Use `python -m boamp` instead of just `boamp`:
```bash
python -m boamp search "cloud"
```

---

### TimeoutError

**Problem:**
```
❌ Error: Timeout waiting for selector
```

**Solutions:**
1. Check internet connection
2. Check if BOAMP.fr is up
3. Reduce `--limit`
4. Try again later

---

### No Results

**Problem:**
```
Total: 0 tenders
```

**Solutions:**
1. Try broader keywords
2. Remove filters (--category, --budget-min, etc.)
3. Increase --limit
4. Check BOAMP.fr manually

---

## Advanced Usage

### Pipe to Other Commands

```bash
# Count results
python -m boamp search "cloud" --format json | jq '. | length'

# Filter with jq
python -m boamp search "cloud" --format json | jq '.[] | select(.budget > 200000)'

# Convert to Excel (with csvkit)
python -m boamp search "cloud" --format csv | csvlook
```

---

### Combine with Python Scripts

```bash
# Scrape and process
python -m boamp search "cloud" --output raw.csv
python process_tenders.py raw.csv > scored.csv
```

---

### Multiple Searches

```bash
# Search multiple keywords separately
for keyword in cloud cybersécurité mobile; do
  python -m boamp search "$keyword" --output "${keyword}_tenders.csv"
done
```

---

## Support

- **GitHub Issues:** https://github.com/Ouailleme/boamp-scraper/issues
- **Documentation:** https://github.com/Ouailleme/boamp-scraper
- **Email:** contact@algora.fr

---

**Last Updated:** January 4, 2026  
**Version:** 0.1.0

