"""Firecrawl Python API wrapper.

A lightweight, async-first Python wrapper for the Firecrawl v2 API.

Example:
    >>> import asyncio
    >>> from firecrawl import FirecrawlClient, MapRequest, load_api_key
    >>> async def main():
    ...     async with FirecrawlClient(load_api_key()) as client:
    ...         result = await client.map(MapRequest(url="https://example.com"))
    ...         print(f"Found {len(result.links)} links")
    >>> asyncio.run(main())
"""

from importlib.metadata import PackageNotFoundError, version

from .client import FirecrawlClient
from .exceptions import (
    AuthenticationError,
    FirecrawlError,
    PaymentRequiredError,
    RateLimitError,
)
from .models import (
    ActiveCrawl,
    ActiveCrawlsResponse,
    AgentJobResponse,
    AgentRequest,
    AgentStatusResponse,
    BatchScrapeJobResponse,
    BatchScrapeRequest,
    BatchScrapeStatusResponse,
    CancelResponse,
    ChangeTrackingData,
    CrawlJobResponse,
    CrawlParamsPreviewData,
    CrawlParamsPreviewRequest,
    CrawlParamsPreviewResponse,
    CrawlRequest,
    CrawlStatusResponse,
    CreditUsageData,
    CreditUsageHistoricalResponse,
    CreditUsagePeriod,
    CreditUsageResponse,
    ExtractJobResponse,
    ExtractRequest,
    ExtractStatusResponse,
    JobError,
    JobErrorsResponse,
    Link,
    LocationSettings,
    MapRequest,
    MapResponse,
    QueueStatusResponse,
    ScrapeData,
    ScrapeMetadata,
    ScrapeRequest,
    ScrapeResponse,
    SearchData,
    SearchImageResult,
    SearchNewsResult,
    SearchRequest,
    SearchResponse,
    SearchWebResult,
    TokenUsageData,
    TokenUsageHistoricalResponse,
    TokenUsagePeriod,
    TokenUsageResponse,
)
from .utils import load_api_key

try:
    __version__ = version("firecrawl-wb")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"
__all__ = [
    "ActiveCrawl",
    "ActiveCrawlsResponse",
    "AgentJobResponse",
    "AgentRequest",
    "AgentStatusResponse",
    "AuthenticationError",
    "BatchScrapeJobResponse",
    "BatchScrapeRequest",
    "BatchScrapeStatusResponse",
    "CancelResponse",
    "ChangeTrackingData",
    "CrawlJobResponse",
    "CrawlParamsPreviewData",
    "CrawlParamsPreviewRequest",
    "CrawlParamsPreviewResponse",
    "CrawlRequest",
    "CrawlStatusResponse",
    "CreditUsageData",
    "CreditUsageHistoricalResponse",
    "CreditUsagePeriod",
    "CreditUsageResponse",
    "ExtractJobResponse",
    "ExtractRequest",
    "ExtractStatusResponse",
    "FirecrawlClient",
    "FirecrawlError",
    "JobError",
    "JobErrorsResponse",
    "Link",
    "LocationSettings",
    "MapRequest",
    "MapResponse",
    "PaymentRequiredError",
    "QueueStatusResponse",
    "RateLimitError",
    "ScrapeData",
    "ScrapeMetadata",
    "ScrapeRequest",
    "ScrapeResponse",
    "SearchData",
    "SearchImageResult",
    "SearchNewsResult",
    "SearchRequest",
    "SearchResponse",
    "SearchWebResult",
    "TokenUsageData",
    "TokenUsageHistoricalResponse",
    "TokenUsagePeriod",
    "TokenUsageResponse",
    "load_api_key",
]
