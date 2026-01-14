#!/usr/bin/env python3
"""
Example: Content Research for Blog Posts

Use Aegis Research to gather information for writing authoritative content.
Great for content marketers, technical writers, and bloggers.
"""

import os
import json
from aegis_research import AegisResearch

client = AegisResearch(api_key=os.environ.get("AEGIS_API_KEY", "res_demo"))


def research_blog_topic(topic: str, target_audience: str = "developers") -> dict:
    """
    Research a topic to prepare for writing a blog post.

    Returns structured data including:
    - Executive summary
    - Key points to cover
    - Statistics and data points
    - Expert quotes/sources to cite
    """

    # Main research query
    main_query = f"{topic} - comprehensive guide for {target_audience}"

    print(f"Researching: {main_query}")
    result = client.research(main_query, depth="deep")

    # Structure the output for content creation
    content_brief = {
        "topic": topic,
        "target_audience": target_audience,
        "executive_summary": result.summary,
        "key_points": result.key_findings,
        "detailed_analysis": result.detailed_analysis,
        "sources_to_cite": [
            {"title": s.title, "url": s.url, "snippet": s.snippet}
            for s in result.sources[:5]
        ],
        "word_count_suggestion": len(result.detailed_analysis.split()) * 2,
        "credits_used": result.credits_used,
    }

    return content_brief


def main():
    # Example: Research for a technical blog post
    topic = "GraphQL vs REST API design patterns"

    print("\n" + "="*60)
    print("Content Research Brief")
    print("="*60 + "\n")

    brief = research_blog_topic(topic, target_audience="backend developers")

    print(f"Topic: {brief['topic']}")
    print(f"Audience: {brief['target_audience']}")
    print(f"\nExecutive Summary:\n{brief['executive_summary']}")

    print(f"\nKey Points to Cover:")
    for i, point in enumerate(brief['key_points'], 1):
        print(f"  {i}. {point}")

    print(f"\nSources to Cite:")
    for source in brief['sources_to_cite']:
        print(f"  - {source['title']}")
        print(f"    {source['url']}")

    print(f"\nSuggested word count: ~{brief['word_count_suggestion']} words")
    print(f"Credits used: {brief['credits_used']}")

    # Save to file for later use
    with open("content_brief.json", "w") as f:
        json.dump(brief, f, indent=2)
    print("\nBrief saved to content_brief.json")


if __name__ == "__main__":
    main()
