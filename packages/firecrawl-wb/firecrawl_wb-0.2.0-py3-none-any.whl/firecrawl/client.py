"""Async Firecrawl v2 API client."""

from __future__ import annotations

from typing import Any, TypeVar

import httpx
from pydantic import BaseModel

from .exceptions import (
    AuthenticationError,
    FirecrawlError,
    PaymentRequiredError,
    RateLimitError,
)
from .models import (
    ActiveCrawlsResponse,
    AgentJobResponse,
    AgentRequest,
    AgentStatusResponse,
    BatchScrapeJobResponse,
    BatchScrapeRequest,
    BatchScrapeStatusResponse,
    CancelResponse,
    CrawlJobResponse,
    CrawlParamsPreviewRequest,
    CrawlParamsPreviewResponse,
    CrawlRequest,
    CrawlStatusResponse,
    CreditUsageHistoricalResponse,
    CreditUsageResponse,
    ExtractJobResponse,
    ExtractRequest,
    ExtractStatusResponse,
    JobErrorsResponse,
    MapRequest,
    MapResponse,
    QueueStatusResponse,
    ScrapeRequest,
    ScrapeResponse,
    SearchRequest,
    SearchResponse,
    TokenUsageHistoricalResponse,
    TokenUsageResponse,
)

__all__ = ["FirecrawlClient"]

T = TypeVar("T", bound=BaseModel)
API_BASE = "https://api.firecrawl.dev/v2"


class FirecrawlClient:
    """Async client for Firecrawl v2 API.

    Example:
        async with FirecrawlClient(api_key) as client:
            result = await client.map(MapRequest(url="https://example.com"))
    """

    __slots__ = ("_api_key", "_base_url", "_client")

    def __init__(self, api_key: str, *, base_url: str = API_BASE) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> FirecrawlClient:
        self._client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(90.0, read=300.0),
        )
        return self

    async def __aexit__(self, *_: object) -> None:
        if self._client:
            await self._client.aclose()

    # === Map ===

    async def map(self, request: MapRequest) -> MapResponse:
        """Map URLs from a website."""
        return await self._post("/map", request, MapResponse)

    # === Scrape ===

    async def scrape(self, request: ScrapeRequest) -> ScrapeResponse:
        """Scrape a single URL."""
        return await self._post("/scrape", request, ScrapeResponse)

    # === Search ===

    async def search(self, request: SearchRequest) -> SearchResponse:
        """Search web, images, or news."""
        return await self._post("/search", request, SearchResponse)

    # === Crawl ===

    async def crawl(self, request: CrawlRequest) -> CrawlJobResponse:
        """Start a crawl job."""
        return await self._post("/crawl", request, CrawlJobResponse)

    async def get_crawl_status(self, job_id: str) -> CrawlStatusResponse:
        """Get crawl job status."""
        return await self._get(f"/crawl/{job_id}", CrawlStatusResponse)

    async def get_crawl_errors(self, job_id: str) -> JobErrorsResponse:
        """Get crawl job errors."""
        return await self._get(f"/crawl/{job_id}/errors", JobErrorsResponse)

    async def get_active_crawls(self) -> ActiveCrawlsResponse:
        """Get all active crawls for the authenticated team."""
        return await self._get("/crawl/active", ActiveCrawlsResponse)

    async def crawl_params_preview(
        self, request: CrawlParamsPreviewRequest
    ) -> CrawlParamsPreviewResponse:
        """Preview crawl parameters generated from a natural language prompt."""
        return await self._post(
            "/crawl/params-preview", request, CrawlParamsPreviewResponse
        )

    async def cancel_crawl(self, job_id: str) -> CancelResponse:
        """Cancel a crawl job."""
        return await self._delete(f"/crawl/{job_id}", CancelResponse)

    # === Batch Scrape ===

    async def batch_scrape(self, request: BatchScrapeRequest) -> BatchScrapeJobResponse:
        """Start a batch scrape job."""
        return await self._post("/batch/scrape", request, BatchScrapeJobResponse)

    async def get_batch_scrape_status(self, job_id: str) -> BatchScrapeStatusResponse:
        """Get batch scrape job status."""
        return await self._get(f"/batch/scrape/{job_id}", BatchScrapeStatusResponse)

    async def get_batch_scrape_errors(self, job_id: str) -> JobErrorsResponse:
        """Get batch scrape job errors."""
        return await self._get(f"/batch/scrape/{job_id}/errors", JobErrorsResponse)

    async def cancel_batch_scrape(self, job_id: str) -> CancelResponse:
        """Cancel a batch scrape job."""
        return await self._delete(f"/batch/scrape/{job_id}", CancelResponse)

    # === Extract ===

    async def extract(self, request: ExtractRequest) -> ExtractJobResponse:
        """Start an extraction job."""
        return await self._post("/extract", request, ExtractJobResponse)

    async def get_extract_status(self, job_id: str) -> ExtractStatusResponse:
        """Get extraction job status."""
        return await self._get(f"/extract/{job_id}", ExtractStatusResponse)

    # === Account ===

    async def get_credit_usage(self) -> CreditUsageResponse:
        """Get remaining credits for the authenticated team."""
        return await self._get("/team/credit-usage", CreditUsageResponse)

    async def get_credit_usage_historical(
        self, *, by_api_key: bool = False
    ) -> CreditUsageHistoricalResponse:
        """Get historical credit usage for the authenticated team."""
        params = {"byApiKey": str(by_api_key).lower()} if by_api_key else None
        return await self._get(
            "/team/credit-usage/historical",
            CreditUsageHistoricalResponse,
            params=params,
        )

    async def get_token_usage(self) -> TokenUsageResponse:
        """Get remaining tokens for the authenticated team."""
        return await self._get("/team/token-usage", TokenUsageResponse)

    async def get_token_usage_historical(
        self, *, by_api_key: bool = False
    ) -> TokenUsageHistoricalResponse:
        """Get historical token usage for the authenticated team."""
        params = {"byApiKey": str(by_api_key).lower()} if by_api_key else None
        return await self._get(
            "/team/token-usage/historical",
            TokenUsageHistoricalResponse,
            params=params,
        )

    async def get_queue_status(self) -> QueueStatusResponse:
        """Get metrics about the authenticated team's scrape queue."""
        return await self._get("/team/queue-status", QueueStatusResponse)

    # === Agent ===

    async def agent(self, request: AgentRequest) -> AgentJobResponse:
        """Start an agent task for agentic data extraction."""
        return await self._post("/agent", request, AgentJobResponse)

    async def get_agent_status(self, job_id: str) -> AgentStatusResponse:
        """Get agent job status."""
        return await self._get(f"/agent/{job_id}", AgentStatusResponse)

    async def cancel_agent(self, job_id: str) -> CancelResponse:
        """Cancel an agent job."""
        return await self._delete(f"/agent/{job_id}", CancelResponse)

    # === Internal ===

    async def _get(self, endpoint: str, response_type: type[T], **kwargs: Any) -> T:
        return await self._request("GET", endpoint, response_type, **kwargs)

    async def _post(
        self, endpoint: str, request: BaseModel, response_type: type[T]
    ) -> T:
        payload = request.model_dump(exclude_none=True, by_alias=True, mode="json")
        return await self._request("POST", endpoint, response_type, json=payload)

    async def _delete(self, endpoint: str, response_type: type[T]) -> T:
        return await self._request("DELETE", endpoint, response_type)

    async def _request(
        self,
        method: str,
        endpoint: str,
        response_type: type[T],
        **kwargs: Any,
    ) -> T:
        if not self._client:
            raise FirecrawlError("Client not initialized. Use 'async with' context.")
        resp = await self._client.request(
            method, f"{self._base_url}{endpoint}", **kwargs
        )
        self._check_response(resp)
        return response_type.model_validate(resp.json())

    def _check_response(self, resp: httpx.Response) -> None:
        if resp.status_code == 401:
            raise AuthenticationError("Invalid API key")
        if resp.status_code == 402:
            raise PaymentRequiredError("Insufficient credits")
        if resp.status_code == 429:
            raise RateLimitError("Rate limit exceeded")
        if resp.status_code >= 400:
            try:
                msg = resp.json().get("error", resp.text)
            except Exception:
                msg = resp.text
            raise FirecrawlError(f"HTTP {resp.status_code}: {msg}")
