# firecrawl-wb

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A lightweight, async-first Python wrapper for the [Firecrawl v2 API](https://docs.firecrawl.dev).

## Features

- **Async-first** — Built on `httpx` for native async/await support
- **Type-safe** — Full Pydantic v2 validation with strict typing
- **Minimal** — ~500 LOC, only 2 dependencies (`httpx`, `pydantic`)
- **Complete** — All v2 endpoints: map, scrape, search, crawl, batch scrape, extract, agent
- **Modern** — Python 3.11+, PEP 517/518 compliant packaging

## Installation

```bash
# From GitHub
pip install git+https://github.com/wb200/firecrawl-wb.git

# Or clone and install locally
git clone https://github.com/wb200/firecrawl-wb.git
cd firecrawl-wb
pip install -e .
```

Or with uv:

```bash
uv add git+https://github.com/wb200/firecrawl-wb.git
```

## Quick Start

### 1. Get an API Key

Sign up at [firecrawl.dev](https://www.firecrawl.dev/) and get your API key.

### 2. Configure API Key

```bash
# Option A: Environment variable (recommended)
export FIRECRAWL_API_KEY="fc-your-api-key"

# Option B: File-based
echo "fc-your-api-key" > ~/.secrets/firecrawl.key
```

### 3. Basic Usage

```python
import asyncio
from firecrawl import FirecrawlClient, MapRequest, load_api_key

async def main():
    async with FirecrawlClient(load_api_key()) as client:
        result = await client.map(MapRequest(
            url="https://example.com",
            limit=100
        ))
        print(f"Found {len(result.links)} links")
        for link in result.links[:5]:
            print(f"  - {link.title}: {link.url}")

asyncio.run(main())
```

## API Reference

### Map — Discover URLs

Get all URLs from a website quickly.

```python
from firecrawl import MapRequest

result = await client.map(MapRequest(
    url="https://example.com",
    search="blog",        # Filter URLs containing "blog"
    sitemap="include",    # "include", "skip", or "only"
    limit=1000,
    includeSubdomains=True,
))

for link in result.links:
    print(f"{link.title}: {link.url}")
```

### Scrape — Extract Content

Scrape a single URL with multiple output formats.

```python
from firecrawl import ScrapeRequest

# Basic markdown
result = await client.scrape(ScrapeRequest(
    url="https://example.com",
    formats=["markdown"],
    maxAge=0,  # Force fresh scrape (skip cache)
))
print(result.data.markdown)

# JSON extraction with schema
result = await client.scrape(ScrapeRequest(
    url="https://example.com",
    formats=[{
        "type": "json",
        "schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "price": {"type": "number"},
            }
        },
        "prompt": "Extract product information"
    }]
))
print(result.data.json_data)  # API's "json" field is aliased to avoid shadowing

# Multiple formats
result = await client.scrape(ScrapeRequest(
    url="https://example.com",
    formats=["markdown", "html", "links"],
    onlyMainContent=True,
    blockAds=True,
))
```

**Advanced options:**

```python
result = await client.scrape(ScrapeRequest(
    url="https://example.com/protected",
    formats=["markdown"],
    waitFor=2000,          # Wait 2s for JS to load
    mobile=True,           # Emulate mobile device
    proxy="stealth",       # Use stealth proxies
    headers={"Cookie": "session=abc123"},
    actions=[              # Perform actions before scraping
        {"type": "wait", "milliseconds": 1000},
        {"type": "click", "selector": "button.load-more"},
        {"type": "screenshot", "fullPage": True},
    ],
))
```

### Search — Web Search with Scraping

Search the web and optionally scrape results.

```python
from firecrawl import SearchRequest

# Web search
result = await client.search(SearchRequest(
    query="python web scraping",
    limit=10,
    sources=[{"type": "web"}],
))
for item in result.data.web:
    print(f"{item.title}: {item.url}")

# Search with scraping
result = await client.search(SearchRequest(
    query="machine learning tutorials",
    limit=5,
    scrapeOptions={
        "formats": ["markdown"],
        "onlyMainContent": True,
    }
))

# News search
result = await client.search(SearchRequest(
    query="AI developments",
    sources=[{"type": "news"}],
    tbs="qdr:w",  # Past week
))

# Image search
result = await client.search(SearchRequest(
    query="sunset mountains",
    sources=[{"type": "images"}],
))
```

### Crawl — Full Site Crawling

Crawl multiple pages (async job pattern).

```python
from firecrawl import CrawlRequest
import asyncio

# Start crawl
job = await client.crawl(CrawlRequest(
    url="https://example.com/docs",
    limit=100,
    maxDiscoveryDepth=2,
    prompt="Only crawl documentation pages",  # Natural language filter
    scrapeOptions={
        "formats": ["markdown"],
        "onlyMainContent": True,
    }
))
print(f"Crawl started: {job.id}")

# Poll for completion
while True:
    status = await client.get_crawl_status(job.id)
    print(f"Status: {status.status} ({status.completed}/{status.total})")
    
    if status.status == "completed":
        for page in status.data:
            url = page["metadata"]["sourceURL"]
            print(f"  - {url}")
        break
    elif status.status == "failed":
        break
    
    await asyncio.sleep(5)
```

**Advanced crawl options:**

```python
job = await client.crawl(CrawlRequest(
    url="https://example.com",
    limit=500,
    crawlEntireDomain=True,
    allowSubdomains=True,
    includePaths=["^/docs/.*", "^/blog/.*"],
    excludePaths=["^/admin/.*"],
    webhook={
        "url": "https://your-server.com/webhook",
        "events": ["completed", "page"],
    }
))
```

### Batch Scrape — Multiple URLs

Scrape multiple URLs in parallel.

```python
from firecrawl import BatchScrapeRequest

job = await client.batch_scrape(BatchScrapeRequest(
    urls=[
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.com/page3",
    ],
    formats=["markdown"],
    ignoreInvalidURLs=True,
))

# Poll for completion
while True:
    status = await client.get_batch_scrape_status(job.id)
    if status.status == "completed":
        for page in status.data:
            print(page["metadata"]["sourceURL"])
        break
    await asyncio.sleep(5)
```

### Extract — Structured Data Extraction

Extract structured data using LLMs.

```python
from firecrawl import ExtractRequest

job = await client.extract(ExtractRequest(
    urls=["https://example.com/*"],  # Glob patterns supported
    prompt="Extract all product information",
    schema={
        "type": "object",
        "properties": {
            "products": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "price": {"type": "number"},
                    }
                }
            }
        }
    },
    enableWebSearch=True,
    showSources=True,
))

# Poll for completion
while True:
    status = await client.get_extract_status(job.id)
    if status.status == "completed":
        print(status.data)
        break
    await asyncio.sleep(5)
```

### Agent — Agentic Data Extraction

Let an AI agent autonomously navigate and extract data.

```python
from firecrawl import AgentRequest

job = await client.agent(AgentRequest(
    prompt="Find the pricing information and feature list",
    urls=["https://example.com"],  # Optional: constrain to specific URLs
    maxCredits=100,                # Optional: limit credit usage
    strictConstrainToURLs=True,    # Only visit provided URLs
))

# Poll for completion
while True:
    status = await client.get_agent_status(job.id)
    if status.status == "completed":
        print(status.data)
        break
    elif status.status == "failed":
        print(f"Error: {status.error}")
        break
    await asyncio.sleep(5)
```

### Cancel Jobs

All async job endpoints support cancellation:

```python
# Cancel running jobs
await client.cancel_crawl(job.id)
await client.cancel_batch_scrape(job.id)
await client.cancel_agent(job.id)
```

## Error Handling

```python
from firecrawl import (
    FirecrawlError,
    RateLimitError,
    PaymentRequiredError,
    AuthenticationError,
)

try:
    result = await client.map(request)
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limit exceeded - wait and retry")
except PaymentRequiredError:
    print("Insufficient credits")
except FirecrawlError as e:
    print(f"API error: {e}")
```

## Best Practices

### Use Caching

```python
# Use default 2-day cache (fastest)
result = await client.scrape(ScrapeRequest(url="..."))

# Force fresh data
result = await client.scrape(ScrapeRequest(url="...", maxAge=0))

# Custom cache window (10 minutes)
result = await client.scrape(ScrapeRequest(url="...", maxAge=600000))
```

### Parallel Requests

```python
import asyncio

urls = ["https://example.com/1", "https://example.com/2", "https://example.com/3"]

# Parallel scraping
results = await asyncio.gather(*[
    client.scrape(ScrapeRequest(url=url))
    for url in urls
])
```

### Polling Helper

```python
async def poll_job(client, job_id, get_status, max_wait=300, interval=5):
    """Generic polling helper."""
    elapsed = 0
    while elapsed < max_wait:
        status = await get_status(job_id)
        if status.status == "completed":
            return status.data
        if status.status == "failed":
            raise FirecrawlError("Job failed")
        await asyncio.sleep(interval)
        elapsed += interval
    raise TimeoutError(f"Job didn't complete in {max_wait}s")

# Usage
data = await poll_job(client, job.id, client.get_crawl_status)
```

## Configuration

### API Key Loading Priority

1. `FIRECRAWL_API_KEY` environment variable
2. Explicit file path passed to `load_api_key(path)`
3. `~/.secrets/firecrawl.key`
4. `~/.secrets` (first line starting with `fc-`)

### Custom Base URL

```python
client = FirecrawlClient(
    api_key="fc-...",
    base_url="https://custom.firecrawl.dev/v2"
)
```

## Credits & Costs

Different operations consume different credits:

| Operation | Cost |
|-----------|------|
| Basic scrape | 1 credit |
| PDF page | 1 credit/page |
| Stealth proxy | +4 credits |
| JSON extraction | +4 credits |
| Search | 2 credits/10 results |

Track usage via `status.creditsUsed` on responses.

## Development

```bash
# Clone and install
git clone https://github.com/wb200/firecrawl-wb
cd firecrawl-wb
uv sync --dev

# Run tests
uv run pytest

# Lint and format
uv run ruff check --fix src/
uv run ruff format src/

# Type check
uv run mypy src/
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [Firecrawl Documentation](https://docs.firecrawl.dev)
- [Firecrawl API Reference](https://docs.firecrawl.dev/api-reference/v2-introduction)
- [GitHub Repository](https://github.com/wb200/firecrawl-wb)
