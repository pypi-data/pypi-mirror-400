"""Pydantic models for Firecrawl v2 API."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

__all__ = [
    "ActiveCrawl",
    "ActiveCrawlsResponse",
    "AgentJobResponse",
    "AgentRequest",
    "AgentStatusResponse",
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
    "JobError",
    "JobErrorsResponse",
    "Link",
    "LocationSettings",
    "MapRequest",
    "MapResponse",
    "QueueStatusResponse",
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
]

DEFAULT_FORMATS: list[str | dict[str, Any]] = ["markdown"]
DEFAULT_SOURCES: list[str | dict[str, str]] = ["web"]


# === Shared ===


class CancelResponse(BaseModel):
    """Response for cancel/delete operations across endpoints."""

    model_config = ConfigDict(extra="allow")

    success: bool | None = None
    status: str | None = None
    message: str | None = None


class LocationSettings(BaseModel):
    """Location/proxy settings."""

    country: str = "US"
    languages: list[str] = Field(default_factory=lambda: ["en-US"])


# === Map ===


class MapRequest(BaseModel):
    """POST /v2/map request."""

    url: HttpUrl
    search: str | None = None
    sitemap: Literal["skip", "include", "only"] = "include"
    includeSubdomains: bool = True
    ignoreQueryParameters: bool = True
    limit: int = Field(5000, le=100000)
    location: LocationSettings | None = None
    timeout: int | None = None


class Link(BaseModel):
    """Individual link in map response."""

    url: str
    title: str | None = None
    description: str | None = None


class MapResponse(BaseModel):
    """POST /v2/map response."""

    success: bool
    links: list[Link]


# === Scrape ===


class ScrapeRequest(BaseModel):
    """POST /v2/scrape request."""

    url: HttpUrl
    formats: list[str | dict[str, Any]] = Field(
        default_factory=lambda: DEFAULT_FORMATS.copy()
    )
    onlyMainContent: bool = True
    includeTags: list[str] | None = None
    excludeTags: list[str] | None = None
    maxAge: int = 172800000
    headers: dict[str, str] | None = None
    waitFor: int = 0
    mobile: bool = False
    skipTlsVerification: bool = True
    timeout: int | None = None
    parsers: list[str] | None = None
    actions: list[dict[str, Any]] | None = None
    location: LocationSettings | None = None
    removeBase64Images: bool = True
    blockAds: bool = True
    proxy: Literal["basic", "stealth", "auto"] = "auto"
    storeInCache: bool = True
    zeroDataRetention: bool = False


class ScrapeMetadata(BaseModel):
    """Metadata from scrape response."""

    model_config = ConfigDict(extra="allow")

    title: str | None = None
    description: str | None = None
    language: str | None = None
    sourceURL: str | None = None
    keywords: str | None = None
    ogLocaleAlternate: list[str] = Field(default_factory=list)
    statusCode: int | None = None
    error: str | None = None


class ScrapeData(BaseModel):
    """Data from scrape response."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    markdown: str | None = None
    summary: str | None = None
    html: str | None = None
    rawHtml: str | None = None
    links: list[str] | None = None
    images: list[str] | None = None
    screenshot: str | None = None
    json_data: dict[str, Any] | None = Field(None, alias="json")
    branding: dict[str, Any] | None = None
    actions: dict[str, Any] | None = None
    metadata: ScrapeMetadata | None = None
    warning: str | None = None
    changeTracking: ChangeTrackingData | None = None


class ChangeTrackingData(BaseModel):
    """Change tracking information from scrape responses."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    previousScrapeAt: str | None = None
    changeStatus: str | None = None
    visibility: str | None = None
    diff: str | None = None
    json_data: dict[str, Any] | None = Field(None, alias="json")


class ScrapeResponse(BaseModel):
    """POST /v2/scrape response."""

    success: bool
    data: ScrapeData


# === Search ===


class SearchRequest(BaseModel):
    """POST /v2/search request."""

    query: str
    limit: int = Field(5, ge=1, le=100)
    sources: list[str | dict[str, str]] = Field(
        default_factory=lambda: DEFAULT_SOURCES.copy()
    )
    categories: list[str | dict[str, str]] | None = None
    tbs: str | None = None
    location: str | None = None
    country: str = "US"
    timeout: int = 60000
    ignoreInvalidURLs: bool = False
    scrapeOptions: dict[str, Any] | None = None


class SearchWebResult(BaseModel):
    """Web search result."""

    model_config = ConfigDict(extra="allow")

    title: str
    description: str | None = None
    url: str
    position: int | None = None
    markdown: str | None = None
    html: str | None = None
    rawHtml: str | None = None
    links: list[str] | None = None
    screenshot: str | None = None
    metadata: ScrapeMetadata | None = None
    category: str | None = None


class SearchImageResult(BaseModel):
    """Image search result."""

    model_config = ConfigDict(extra="allow")

    title: str
    imageUrl: str
    imageWidth: int | None = None
    imageHeight: int | None = None
    url: str
    position: int


class SearchNewsResult(BaseModel):
    """News search result."""

    model_config = ConfigDict(extra="allow")

    title: str
    snippet: str | None = None
    url: str
    date: str | None = None
    imageUrl: str | None = None
    position: int
    markdown: str | None = None
    html: str | None = None
    rawHtml: str | None = None
    links: list[str] | None = None
    screenshot: str | None = None
    metadata: ScrapeMetadata | None = None


class SearchData(BaseModel):
    """Search response data."""

    web: list[SearchWebResult] | None = None
    images: list[SearchImageResult] | None = None
    news: list[SearchNewsResult] | None = None


class SearchResponse(BaseModel):
    """POST /v2/search response."""

    success: bool
    data: SearchData
    warning: str | None = None
    id: str | None = None
    creditsUsed: int | None = None


# === Crawl ===


class CrawlRequest(BaseModel):
    """POST /v2/crawl request."""

    url: HttpUrl
    prompt: str | None = None
    excludePaths: list[str] | None = None
    includePaths: list[str] | None = None
    maxDepth: int | None = None
    maxDiscoveryDepth: int | None = None
    sitemap: Literal["skip", "include"] = "include"
    ignoreQueryParameters: bool = False
    deduplicateSimilarURLs: bool | None = None
    limit: int = Field(10000, le=100000)
    crawlEntireDomain: bool = False
    allowExternalLinks: bool = False
    allowSubdomains: bool = False
    delay: float | None = None
    maxConcurrency: int | None = None
    webhook: dict[str, Any] | None = None
    scrapeOptions: dict[str, Any] | None = None
    zeroDataRetention: bool = False


class CrawlJobResponse(BaseModel):
    """POST /v2/crawl response."""

    success: bool
    id: str
    url: str


class CrawlStatusResponse(BaseModel):
    """GET /v2/crawl/{id} response."""

    status: str
    total: int | None = None
    completed: int | None = None
    creditsUsed: int | None = None
    expiresAt: str | None = None
    next: str | None = None
    data: list[dict[str, Any]] | None = None


class CrawlParamsPreviewRequest(BaseModel):
    """POST /v2/crawl/params-preview request."""

    url: HttpUrl
    prompt: str = Field(..., max_length=10000)


class CrawlParamsPreviewData(BaseModel):
    """Generated crawl parameters from params-preview."""

    model_config = ConfigDict(extra="allow")

    url: str
    includePaths: list[str] | None = None
    excludePaths: list[str] | None = None
    maxDepth: int | None = None
    maxDiscoveryDepth: int | None = None
    crawlEntireDomain: bool | None = None
    allowExternalLinks: bool | None = None
    allowSubdomains: bool | None = None
    sitemap: str | None = None
    ignoreQueryParameters: bool | None = None
    deduplicateSimilarURLs: bool | None = None
    delay: float | None = None
    limit: int | None = None


class CrawlParamsPreviewResponse(BaseModel):
    """POST /v2/crawl/params-preview response."""

    success: bool
    data: CrawlParamsPreviewData


class JobError(BaseModel):
    """Error detail for crawl/batch scrape errors endpoints."""

    id: str
    timestamp: str
    url: str
    error: str


class JobErrorsResponse(BaseModel):
    """GET /v2/crawl/{id}/errors and /v2/batch/scrape/{id}/errors response."""

    errors: list[JobError]
    robotsBlocked: list[str] = Field(default_factory=list)


class ActiveCrawl(BaseModel):
    """Active crawl info from GET /v2/crawl/active."""

    model_config = ConfigDict(extra="allow")

    id: str
    teamId: str | None = None
    url: str
    options: dict[str, Any] | None = None


class ActiveCrawlsResponse(BaseModel):
    """GET /v2/crawl/active response."""

    success: bool
    crawls: list[ActiveCrawl]


# === Batch Scrape ===


class BatchScrapeRequest(BaseModel):
    """POST /v2/batch/scrape request."""

    urls: list[HttpUrl]
    formats: list[str | dict[str, Any]] = Field(
        default_factory=lambda: DEFAULT_FORMATS.copy()
    )
    onlyMainContent: bool = True
    includeTags: list[str] | None = None
    excludeTags: list[str] | None = None
    maxAge: int = 172800000
    headers: dict[str, str] | None = None
    webhook: dict[str, Any] | None = None
    maxConcurrency: int | None = None
    ignoreInvalidURLs: bool = True
    waitFor: int = 0
    mobile: bool = False
    skipTlsVerification: bool = True
    timeout: int | None = None
    parsers: list[str] | None = None
    actions: list[dict[str, Any]] | None = None
    location: LocationSettings | None = None
    removeBase64Images: bool = True
    blockAds: bool = True
    proxy: Literal["basic", "stealth", "auto"] = "auto"
    storeInCache: bool = True
    zeroDataRetention: bool = False


class BatchScrapeJobResponse(BaseModel):
    """POST /v2/batch/scrape response."""

    success: bool
    id: str
    url: str
    invalidURLs: list[str] | None = None


class BatchScrapeStatusResponse(BaseModel):
    """GET /v2/batch/scrape/{id} response."""

    status: str
    total: int | None = None
    completed: int | None = None
    creditsUsed: int | None = None
    expiresAt: str | None = None
    next: str | None = None
    data: list[dict[str, Any]] | None = None


# === Extract ===


class ExtractRequest(BaseModel):
    """POST /v2/extract request."""

    model_config = ConfigDict(populate_by_name=True)

    urls: list[str]
    prompt: str | None = None
    schema_: dict[str, Any] | None = Field(None, alias="schema")
    enableWebSearch: bool = False
    ignoreSitemap: bool = False
    includeSubdomains: bool = True
    showSources: bool = False
    scrapeOptions: dict[str, Any] | None = None
    ignoreInvalidURLs: bool = True


class ExtractJobResponse(BaseModel):
    """POST /v2/extract response."""

    success: bool
    id: str
    invalidURLs: list[str] | None = None


class ExtractStatusResponse(BaseModel):
    """GET /v2/extract/{id} response."""

    model_config = ConfigDict(extra="allow")

    success: bool
    data: dict[str, Any] | None = None
    status: Literal["completed", "processing", "failed", "cancelled"]
    expiresAt: str | None = None
    tokensUsed: int | None = None
    creditsUsed: int | None = None
    sources: list[dict[str, Any]] | None = None
    error: str | None = None
    warning: str | None = None


# === Agent ===


class AgentRequest(BaseModel):
    """POST /v2/agent request."""

    model_config = ConfigDict(populate_by_name=True)

    prompt: str = Field(..., max_length=10000)
    urls: list[str] | None = None
    schema_: dict[str, Any] | None = Field(None, alias="schema")
    maxCredits: int | None = None
    strictConstrainToURLs: bool = False


class AgentJobResponse(BaseModel):
    """POST /v2/agent response."""

    success: bool
    id: str


class AgentStatusResponse(BaseModel):
    """GET /v2/agent/{id} response."""

    success: bool
    status: Literal["processing", "completed", "failed"]
    data: dict[str, Any] | None = None
    error: str | None = None
    expiresAt: str | None = None
    creditsUsed: int | None = None


# === Account ===


class CreditUsageData(BaseModel):
    """Credit usage data."""

    model_config = ConfigDict(extra="allow")

    remainingCredits: int
    planCredits: int
    billingPeriodStart: str
    billingPeriodEnd: str


class CreditUsageResponse(BaseModel):
    """GET /v2/team/credit-usage response."""

    success: bool
    data: CreditUsageData


class CreditUsagePeriod(BaseModel):
    """Historical credit usage period."""

    model_config = ConfigDict(extra="allow")

    startDate: str
    endDate: str
    apiKey: str | None = None
    totalCredits: int


class CreditUsageHistoricalResponse(BaseModel):
    """GET /v2/team/credit-usage/historical response."""

    success: bool
    periods: list[CreditUsagePeriod]


class TokenUsageData(BaseModel):
    """Token usage data."""

    model_config = ConfigDict(extra="allow")

    remainingTokens: int
    planTokens: int
    billingPeriodStart: str
    billingPeriodEnd: str


class TokenUsageResponse(BaseModel):
    """GET /v2/team/token-usage response."""

    success: bool
    data: TokenUsageData


class TokenUsagePeriod(BaseModel):
    """Historical token usage period."""

    model_config = ConfigDict(extra="allow")

    startDate: str
    endDate: str
    apiKey: str | None = None
    totalTokens: int


class TokenUsageHistoricalResponse(BaseModel):
    """GET /v2/team/token-usage/historical response."""

    success: bool
    periods: list[TokenUsagePeriod]


class QueueStatusResponse(BaseModel):
    """GET /v2/team/queue-status response."""

    model_config = ConfigDict(extra="allow")

    success: bool
    jobsInQueue: int
    activeJobsInQueue: int
    waitingJobsInQueue: int
    maxConcurrency: int
    mostRecentSuccess: str | None = None
