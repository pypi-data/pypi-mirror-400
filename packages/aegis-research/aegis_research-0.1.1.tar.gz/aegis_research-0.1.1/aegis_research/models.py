"""
Data models for the Aegis Research SDK.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum


class ResearchDepth(str, Enum):
    """Research depth levels."""
    SHALLOW = "shallow"  # 1 credit, 3 sources, ~2 min
    MEDIUM = "medium"    # 3 credits, 5-7 sources, ~5 min
    DEEP = "deep"        # 10 credits, 10+ sources, ~15 min


@dataclass
class Source:
    """A cited source in the research."""
    url: str
    title: str
    snippet: str
    relevance_score: float
    fetched_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Source":
        fetched_at = None
        if data.get("fetched_at"):
            try:
                fetched_at = datetime.fromisoformat(data["fetched_at"].replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pass
        return cls(
            url=data.get("url", ""),
            title=data.get("title", ""),
            snippet=data.get("snippet", ""),
            relevance_score=data.get("relevance_score", 0.0),
            fetched_at=fetched_at,
        )


@dataclass
class ResearchResult:
    """Result from a research request."""
    id: str
    topic: str
    status: str
    summary: str
    key_findings: List[str]
    detailed_analysis: str
    sources: List[Source]
    source_count: int
    depth: str
    cached: bool
    duration_ms: int
    created_at: Optional[datetime]
    credits_used: int

    @classmethod
    def from_dict(cls, data: dict) -> "ResearchResult":
        created_at = None
        if data.get("created_at"):
            try:
                created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pass

        sources = [Source.from_dict(s) for s in data.get("sources", [])]

        return cls(
            id=data.get("id", ""),
            topic=data.get("topic", ""),
            status=data.get("status", ""),
            summary=data.get("summary", ""),
            key_findings=data.get("key_findings", []),
            detailed_analysis=data.get("detailed_analysis", ""),
            sources=sources,
            source_count=data.get("source_count", len(sources)),
            depth=data.get("depth", "medium"),
            cached=data.get("cached", False),
            duration_ms=data.get("duration_ms", 0),
            created_at=created_at,
            credits_used=data.get("credits_used", 0),
        )

    def __str__(self) -> str:
        return f"ResearchResult(id={self.id}, topic='{self.topic[:50]}...', status={self.status})"

    def to_markdown(self) -> str:
        """Convert result to markdown format."""
        lines = [
            f"# {self.topic}",
            "",
            "## Summary",
            self.summary,
            "",
            "## Key Findings",
        ]
        for finding in self.key_findings:
            lines.append(f"- {finding}")
        lines.extend([
            "",
            "## Detailed Analysis",
            self.detailed_analysis,
            "",
            "## Sources",
        ])
        for i, source in enumerate(self.sources, 1):
            lines.append(f"{i}. [{source.title}]({source.url})")
        return "\n".join(lines)


@dataclass
class CreditsStatus:
    """Credit balance and usage status."""
    credits_remaining: int
    credits_used_today: int
    credits_used_month: int
    tier: str
    rate_limit_remaining: int
    rate_limit_reset_at: Optional[datetime]

    @classmethod
    def from_dict(cls, data: dict) -> "CreditsStatus":
        reset_at = None
        if data.get("rate_limit_reset_at"):
            try:
                reset_at = datetime.fromisoformat(data["rate_limit_reset_at"].replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pass

        return cls(
            credits_remaining=data.get("credits_remaining", 0),
            credits_used_today=data.get("credits_used_today", 0),
            credits_used_month=data.get("credits_used_month", 0),
            tier=data.get("tier", "free"),
            rate_limit_remaining=data.get("rate_limit_remaining", 0),
            rate_limit_reset_at=reset_at,
        )

    def __str__(self) -> str:
        return f"CreditsStatus(remaining={self.credits_remaining}, tier={self.tier})"
