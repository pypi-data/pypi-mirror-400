#!/usr/bin/env python3
"""
Example: Automated Competitor Analysis

Use Aegis Research to analyze competitors and generate actionable insights.
Great for product managers, founders, and market researchers.
"""

import os
from aegis_research import AegisResearch

# Initialize client
client = AegisResearch(api_key=os.environ.get("AEGIS_API_KEY", "res_demo"))


def analyze_competitor(company: str, aspects: list[str]) -> dict:
    """
    Analyze a competitor across multiple aspects.

    Args:
        company: Company name (e.g., "Stripe", "Notion")
        aspects: List of aspects to research (e.g., ["pricing", "features"])

    Returns:
        Dict with research results for each aspect
    """
    results = {}

    for aspect in aspects:
        topic = f"{company} {aspect} analysis 2025"
        print(f"Researching: {topic}...")

        result = client.research(topic, depth="medium")
        results[aspect] = {
            "summary": result.summary,
            "key_findings": result.key_findings,
            "sources": len(result.sources),
        }

    return results


def main():
    # Example: Analyze Notion as a competitor
    competitor = "Notion"
    aspects = [
        "pricing strategy",
        "enterprise features",
        "API capabilities",
        "customer complaints",
    ]

    print(f"\n{'='*60}")
    print(f"Competitor Analysis: {competitor}")
    print(f"{'='*60}\n")

    analysis = analyze_competitor(competitor, aspects)

    for aspect, data in analysis.items():
        print(f"\n## {aspect.title()}")
        print(f"Summary: {data['summary']}")
        print(f"\nKey Findings:")
        for finding in data['key_findings'][:3]:
            print(f"  - {finding}")
        print(f"\n({data['sources']} sources analyzed)")

    # Check remaining credits
    status = client.credits()
    print(f"\n{'='*60}")
    print(f"Credits remaining: {status.credits_remaining}")


if __name__ == "__main__":
    main()
