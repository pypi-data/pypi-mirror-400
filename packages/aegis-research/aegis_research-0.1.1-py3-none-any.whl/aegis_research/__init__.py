"""
Aegis Research API - Python SDK

AI-powered web research as a service.

Usage:
    from aegis_research import AegisResearch

    client = AegisResearch(api_key="res_xxx")
    result = client.research("Best practices for API rate limiting")
    print(result.summary)
"""

from typing import Optional, List
import httpx

from .models import (
    ResearchResult,
    CreditsStatus,
    ResearchDepth,
    Source,
)
from .exceptions import (
    AegisError,
    AuthenticationError,
    RateLimitError,
    InsufficientCreditsError,
    ResearchError,
)

__version__ = "0.1.1"
__all__ = [
    "AegisResearch",
    "ResearchResult",
    "CreditsStatus",
    "ResearchDepth",
    "Source",
    "AegisError",
    "AuthenticationError",
    "RateLimitError",
    "InsufficientCreditsError",
    "ResearchError",
]

DEFAULT_BASE_URL = "https://aegisagent.ai/api/v1/research"


class AegisResearch:
    """
    Client for the Aegis Research API.

    Args:
        api_key: Your API key (starts with 'res_')
        base_url: API base URL (default: https://aegis.rbnk.uk/api/v1/research)
        timeout: Request timeout in seconds (default: 300 for deep research)

    Example:
        >>> client = AegisResearch(api_key="res_xxx")
        >>> result = client.research("What is quantum computing?")
        >>> print(result.summary)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 300.0,
    ):
        if not api_key:
            raise AuthenticationError("API key is required")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.Client(
            headers={"X-API-Key": api_key},
            timeout=timeout,
        )

    def research(
        self,
        topic: str,
        depth: str = "medium",
        urls: Optional[List[str]] = None,
        search_query: Optional[str] = None,
        use_cache: bool = True,
    ) -> ResearchResult:
        """
        Execute AI-powered research on a topic.

        Args:
            topic: The research topic or question (3-500 chars)
            depth: Research depth - "shallow" (1 credit), "medium" (3 credits), "deep" (10 credits)
            urls: Optional list of specific URLs to include
            search_query: Custom search query (auto-generated if not provided)
            use_cache: Use cached results if available (default: True)

        Returns:
            ResearchResult with summary, key_findings, detailed_analysis, and sources

        Raises:
            AuthenticationError: Invalid API key
            RateLimitError: Rate limit exceeded
            InsufficientCreditsError: Not enough credits
            ResearchError: Research execution failed

        Example:
            >>> result = client.research("Best Python frameworks 2025", depth="medium")
            >>> for finding in result.key_findings:
            ...     print(f"- {finding}")
        """
        if depth not in ("shallow", "medium", "deep"):
            raise ValueError("depth must be 'shallow', 'medium', or 'deep'")

        payload = {
            "topic": topic,
            "depth": depth,
            "urls": urls or [],
            "search_query": search_query,
            "output_format": "json",
            "include_sources": True,
            "use_cache": use_cache,
        }

        response = self._request("POST", "", json=payload)
        return ResearchResult.from_dict(response)

    def credits(self) -> CreditsStatus:
        """
        Check your credit balance and usage.

        Returns:
            CreditsStatus with remaining credits, usage stats, and tier info

        Example:
            >>> status = client.credits()
            >>> print(f"Credits remaining: {status.credits_remaining}")
        """
        response = self._request("GET", "/credits")
        return CreditsStatus.from_dict(response)

    def get_research(self, research_id: str) -> ResearchResult:
        """
        Retrieve a previous research result by ID.

        Args:
            research_id: The research ID (e.g., "res_abc123")

        Returns:
            ResearchResult from the stored research

        Example:
            >>> result = client.get_research("res_abc123")
        """
        response = self._request("GET", f"/{research_id}")
        return ResearchResult.from_dict(response)

    def history(self, limit: int = 20, offset: int = 0) -> List[dict]:
        """
        Get your research history.

        Args:
            limit: Number of results to return (default: 20)
            offset: Pagination offset

        Returns:
            List of research summaries
        """
        response = self._request("GET", f"/history?limit={limit}&offset={offset}")
        return response

    def pricing(self) -> dict:
        """
        Get current pricing information (no auth required).

        Returns:
            Pricing tiers and credit costs
        """
        # This endpoint doesn't require auth, but we'll use our client anyway
        response = self._request("GET", "/pricing")
        return response

    def _request(self, method: str, path: str, **kwargs) -> dict:
        """Make an HTTP request to the API."""
        url = f"{self.base_url}{path}"

        try:
            response = self._client.request(method, url, **kwargs)
        except httpx.TimeoutException:
            raise ResearchError("Request timed out. Try a shorter depth or simpler topic.")
        except httpx.RequestError as e:
            raise ResearchError(f"Network error: {e}")

        if response.status_code == 200:
            return response.json()

        # Handle errors
        try:
            error_data = response.json()
            error_msg = error_data.get("detail", {})
            if isinstance(error_msg, dict):
                error_text = error_msg.get("error", str(error_msg))
                error_code = error_msg.get("error_code", "UNKNOWN")
            else:
                error_text = str(error_msg)
                error_code = "UNKNOWN"
        except Exception:
            error_text = response.text
            error_code = "UNKNOWN"

        if response.status_code == 401:
            raise AuthenticationError(error_text or "Invalid API key")
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After", "60")
            raise RateLimitError(f"Rate limit exceeded. Retry after {retry_after} seconds")
        elif response.status_code == 402:
            raise InsufficientCreditsError(error_text or "Insufficient credits")
        elif response.status_code == 403:
            raise AuthenticationError(error_text or "Access forbidden")
        elif response.status_code == 404:
            raise ResearchError(error_text or "Resource not found")
        else:
            raise AegisError(f"API error ({response.status_code}): {error_text}")

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
