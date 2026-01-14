# Aegis Research SDK

Python SDK for the [Aegis Research API](https://aegisagent.ai/research) - AI-powered web research as a service.

## Installation

```bash
pip install aegis-research
```

## Quick Start

```python
from aegis_research import AegisResearch

# Initialize client
client = AegisResearch(api_key="res_your_api_key")

# Execute research
result = client.research("Best practices for API rate limiting in 2025")

print(result.summary)
for finding in result.key_findings:
    print(f"- {finding}")
```

## Features

- **AI-Powered Research**: Get synthesized research results, not just search links
- **Multiple Depth Levels**: Choose shallow (1 credit), medium (3 credits), or deep (10 credits) research
- **Caching**: Results cached for 24 hours to save credits
- **Source Citations**: Every claim backed by sources

## Usage

### Research

```python
# Basic research
result = client.research("What is quantum computing?")

# Deep research with more sources
result = client.research(
    "Impact of AI on healthcare in 2025",
    depth="deep",  # 10 credits, 10+ sources
    use_cache=False  # Force fresh research
)

# Include specific URLs
result = client.research(
    "Compare FastAPI vs Flask",
    urls=["https://fastapi.tiangolo.com", "https://flask.palletsprojects.com"]
)
```

### Check Credits

```python
status = client.credits()
print(f"Credits remaining: {status.credits_remaining}")
print(f"Tier: {status.tier}")
```

### Research History

```python
history = client.history(limit=10)
for item in history:
    print(f"{item['id']}: {item['topic']}")
```

### Get Previous Result

```python
result = client.get_research("res_abc123")
```

## Response Format

```python
ResearchResult:
    id: str                     # "res_abc123"
    topic: str                  # Original query
    status: str                 # "completed", "cached", "failed"
    summary: str                # Executive summary (2-3 sentences)
    key_findings: List[str]     # Main findings as bullet points
    detailed_analysis: str      # Full analysis
    sources: List[Source]       # Cited sources
    source_count: int           # Number of sources
    depth: str                  # "shallow", "medium", "deep"
    cached: bool                # Whether result was cached
    credits_used: int           # Credits consumed
    duration_ms: int            # Time taken
```

## Depth Levels

| Depth | Credits | Sources | Time | Use Case |
|-------|---------|---------|------|----------|
| shallow | 1 | 3 | ~2 min | Quick facts, verification |
| medium | 3 | 5-7 | ~5 min | General research, decisions |
| deep | 10 | 10+ | ~15 min | Comprehensive investigation |

## Real-World Examples

The `examples/` directory contains ready-to-use scripts for common use cases:

| Example | Description | Credits |
|---------|-------------|---------|
| `competitor_analysis.py` | Analyze competitors across multiple dimensions | ~12 |
| `content_research.py` | Research for blog posts with structured briefs | ~10 |
| `due_diligence.py` | Startup/company due diligence research | ~11 |
| `tech_decision.py` | Compare technologies for informed decisions | ~10 |
| `async_batch.py` | Research multiple topics in parallel | varies |

```bash
# Set your API key
export AEGIS_API_KEY=res_your_key

# Run an example
python examples/competitor_analysis.py
```

## Error Handling

```python
from aegis_research import (
    AegisError,
    AuthenticationError,
    RateLimitError,
    InsufficientCreditsError,
)

try:
    result = client.research("topic")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limited: {e}")
except InsufficientCreditsError:
    print("Not enough credits")
except AegisError as e:
    print(f"API error: {e}")
```

## Pricing

| Tier | Price | Credits/Month | Rate Limit |
|------|-------|---------------|------------|
| Free | $0 | 500 | 10/min |
| Starter | $9/mo | 2,000 | 20/min |
| Pro | $49/mo | 10,000 | 60/min |

Get your API key at [aegisagent.ai/research](https://aegisagent.ai/research)

## License

MIT
