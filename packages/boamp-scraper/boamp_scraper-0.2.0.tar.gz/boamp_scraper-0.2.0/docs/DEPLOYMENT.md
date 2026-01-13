# 🚀 Deployment Guide

Complete guide to deploy BOAMP Scraper in production environments.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Docker Deployment](#docker-deployment)
4. [Railway Deployment](#railway-deployment)
5. [AWS Lambda Deployment](#aws-lambda-deployment)
6. [Cron Jobs](#cron-jobs)
7. [Monitoring](#monitoring)
8. [Security](#security)
9. [Performance Optimization](#performance-optimization)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **Python:** 3.10 or higher
- **RAM:** Minimum 512MB (1GB+ recommended for Playwright)
- **Disk:** 500MB for dependencies + Chromium browser
- **Network:** Stable internet connection

### Dependencies
```bash
pip install boamp-scraper
python -m playwright install chromium
```

---

## Environment Setup

### 1. Create Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install boamp-scraper
python -m playwright install chromium
```

### 2. Configuration

Create a `.env` file:

```env
# BOAMP Scraper Configuration
BOAMP_MAX_PAGES=5
BOAMP_PAGE_DELAY=3.0
BOAMP_CACHE_TTL=86400
BOAMP_RATE_LIMIT=10
BOAMP_LOG_LEVEL=INFO

# Optional: Monitoring
SENTRY_DSN=https://your-sentry-dsn
PLAUSIBLE_API_KEY=your-key
```

---

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

# Install system dependencies for Playwright
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN python -m playwright install --with-deps chromium

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 scraper && \
    chown -R scraper:scraper /app
USER scraper

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Run scraper
CMD ["python", "scraper_job.py"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  boamp-scraper:
    build: .
    container_name: boamp-scraper
    environment:
      - BOAMP_MAX_PAGES=5
      - BOAMP_RATE_LIMIT=10
    volumes:
      - ./data:/app/data
      - ./cache:/app/.cache
    restart: unless-stopped
    mem_limit: 1g
    cpus: 1.0
```

### Build and Run

```bash
# Build image
docker build -t boamp-scraper:latest .

# Run container
docker run -d \
  --name boamp-scraper \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  boamp-scraper:latest

# View logs
docker logs -f boamp-scraper

# Stop container
docker stop boamp-scraper
```

---

## Railway Deployment

[Railway](https://railway.app) provides easy serverless deployment.

### 1. Create `railway.json`

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python -m playwright install chromium && python scraper_job.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

### 2. Create `Procfile`

```
web: python scraper_job.py
```

### 3. Deploy

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Set environment variables
railway variables set BOAMP_MAX_PAGES=5

# Deploy
railway up
```

---

## AWS Lambda Deployment

Deploy as serverless function.

### 1. Create `lambda_handler.py`

```python
import asyncio
from boamp import TenderScraper


def lambda_handler(event, context):
    """
    AWS Lambda handler for BOAMP scraping
    
    Event format:
    {
        "keywords": ["cloud", "cybersécurité"],
        "limit": 20,
        "max_pages": 2
    }
    """
    keywords = event.get("keywords", ["informatique"])
    limit = event.get("limit", 10)
    
    scraper = TenderScraper()
    
    # Run async function in sync context
    loop = asyncio.get_event_loop()
    tenders = loop.run_until_complete(
        scraper.search_async(keywords=keywords, limit=limit)
    )
    
    return {
        "statusCode": 200,
        "body": {
            "count": len(tenders),
            "tenders": [t.model_dump() for t in tenders]
        }
    }
```

### 2. Create `serverless.yml`

```yaml
service: boamp-scraper

provider:
  name: aws
  runtime: python3.11
  region: eu-west-1
  memorySize: 1024
  timeout: 300
  
functions:
  scraper:
    handler: lambda_handler.lambda_handler
    events:
      - schedule:
          rate: cron(0 9 * * ? *)  # Daily at 9 AM
          enabled: true
    environment:
      BOAMP_MAX_PAGES: 5
      BOAMP_RATE_LIMIT: 10
```

### 3. Deploy

```bash
# Install Serverless Framework
npm install -g serverless

# Deploy
serverless deploy
```

---

## Cron Jobs

### Linux/Mac (crontab)

```bash
# Edit crontab
crontab -e

# Add job (daily at 9 AM)
0 9 * * * cd /path/to/boamp-scraper && /path/to/venv/bin/python scraper_job.py >> /var/log/boamp-scraper.log 2>&1

# Check logs
tail -f /var/log/boamp-scraper.log
```

### Python Script (`scraper_job.py`)

```python
#!/usr/bin/env python3
"""
Cron job script for BOAMP scraping
"""

import asyncio
import logging
from datetime import datetime
from boamp import TenderScraper
from boamp.cache import TenderCache

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('boamp-scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def main():
    """Main scraping job"""
    logger.info(f"Starting BOAMP scraping job at {datetime.now()}")
    
    scraper = TenderScraper()
    cache = TenderCache()
    
    try:
        # Define keywords to search
        keywords = ["cloud", "cybersécurité", "informatique"]
        
        # Scrape tenders
        tenders = await scraper.search_async(keywords=keywords, limit=50)
        
        logger.info(f"Found {len(tenders)} tenders")
        
        # Cache results
        cache.set_many(tenders)
        
        # Optional: Send to database, webhook, etc.
        # send_to_database(tenders)
        # send_webhook_notification(tenders)
        
        logger.info("Scraping job completed successfully")
    
    except Exception as e:
        logger.error(f"Scraping job failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Monitoring

### 1. Sentry (Error Tracking)

```python
import sentry_sdk

sentry_sdk.init(
    dsn="https://your-sentry-dsn",
    traces_sample_rate=1.0,
    environment="production"
)
```

### 2. Logging to File

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/boamp-scraper.log'),
        logging.StreamHandler()
    ]
)
```

### 3. Metrics with StatsD

```python
from statsd import StatsClient

statsd = StatsClient('localhost', 8125)

# Track metrics
statsd.incr('boamp.scrapes')
statsd.timing('boamp.duration', duration_ms)
statsd.gauge('boamp.tenders_found', len(tenders))
```

### 4. Health Checks

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }
```

---

## Security

### 1. Environment Variables

**Never commit secrets!**

```bash
# Use .env file (add to .gitignore)
BOAMP_API_KEY=your-secret-key
SENTRY_DSN=your-sentry-dsn
```

### 2. Rate Limiting

```python
from boamp.rate_limiter import RateLimiter

# Be respectful to BOAMP servers
limiter = RateLimiter(requests_per_minute=10)

async with limiter:
    tenders = await scraper.search_async(...)
```

### 3. User Agent Rotation

```python
# Already handled by TenderScraper with fake-useragent
scraper = TenderScraper()  # Automatic user agent rotation
```

### 4. Proxy Support

```python
from playwright.async_api import async_playwright

async with async_playwright() as p:
    browser = await p.chromium.launch(
        proxy={
            "server": "http://proxy-server:8080",
            "username": "user",
            "password": "pass"
        }
    )
```

---

## Performance Optimization

### 1. Caching

```python
from boamp.cache import TenderCache

cache = TenderCache(ttl=86400)  # 24 hours

# Check cache first
if cache.is_cached(tender_id):
    tender = cache.get(tender_id)
else:
    tender = await scrape_tender(tender_id)
    cache.set(tender_id, tender)
```

### 2. Async Concurrency

```python
import asyncio

# Scrape multiple keywords concurrently
keywords_list = [["cloud"], ["cybersécurité"], ["data"]]

tasks = [scraper.search_async(keywords=kw, limit=10) for kw in keywords_list]
results = await asyncio.gather(*tasks)
```

### 3. Resource Limits

```python
# Limit browser resources
scraper = TenderScraper()
scraper.browser_args = [
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--no-sandbox",
    "--max-old-space-size=512"  # Limit memory
]
```

---

## Troubleshooting

### Issue: Playwright TimeoutError

**Solution:**
```python
# Increase timeout
await page.goto(url, timeout=60000)  # 60 seconds

# Or wait for specific state
await page.wait_for_selector(".result", timeout=30000)
```

### Issue: BOAMP Blocking Requests

**Solution:**
```python
# Use rate limiting
from boamp.rate_limiter import RateLimiter

limiter = RateLimiter(requests_per_minute=5)  # Slower

# Add random delays
import random
await asyncio.sleep(random.uniform(2, 5))
```

### Issue: Memory Leaks

**Solution:**
```python
# Close browser after each batch
scraper = TenderScraper()
tenders = await scraper.search_async(...)
await scraper.close()  # Free memory
```

### Issue: Docker Chromium Not Found

**Solution:**
```dockerfile
# Install Chromium in Dockerfile
RUN apt-get update && apt-get install -y chromium

# Or use Playwright's bundled browser
RUN python -m playwright install --with-deps chromium
```

---

## Best Practices

### 1. **Be Respectful**
- Use rate limiting (10 req/min max)
- Scrape during off-peak hours
- Cache results to avoid re-scraping

### 2. **Error Handling**
- Implement retries with exponential backoff
- Log all errors to Sentry/file
- Send alerts on failures

### 3. **Monitoring**
- Track scraping success rate
- Monitor response times
- Alert on anomalies

### 4. **Data Management**
- Clean old cache entries regularly
- Backup scraped data
- Deduplicate results

### 5. **Security**
- Never commit secrets
- Use environment variables
- Rotate API keys regularly
- Keep dependencies updated

---

## Production Checklist

- [ ] Environment variables configured
- [ ] Rate limiting enabled (≤10 req/min)
- [ ] Caching configured (24h+ TTL)
- [ ] Error tracking (Sentry)
- [ ] Logging to file
- [ ] Health checks implemented
- [ ] Monitoring dashboards
- [ ] Backup strategy
- [ ] Secrets secured
- [ ] Docker/serverless configured
- [ ] Cron job scheduled
- [ ] Documentation updated
- [ ] Team trained

---

## Support

- **Issues:** https://github.com/Ouailleme/boamp-scraper/issues
- **Discussions:** https://github.com/Ouailleme/boamp-scraper/discussions
- **Email:** contact@algora.fr

---

**Built with ❤️ for production deployments**

