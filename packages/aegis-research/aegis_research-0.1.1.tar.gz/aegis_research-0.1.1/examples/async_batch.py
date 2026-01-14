#!/usr/bin/env python3
"""
Example: Batch Research with Async

Research multiple topics efficiently using asyncio.
Great for processing lists of topics or parallel research.
"""

import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from aegis_research import AegisResearch

client = AegisResearch(api_key=os.environ.get("AEGIS_API_KEY", "res_demo"))


async def research_batch(topics: list[str], depth: str = "shallow") -> list[dict]:
    """
    Research multiple topics in parallel.

    Uses a thread pool since the SDK is synchronous.
    Rate limiting is handled server-side.
    """

    loop = asyncio.get_event_loop()

    def do_research(topic: str) -> dict:
        result = client.research(topic, depth=depth)
        return {
            "topic": topic,
            "summary": result.summary,
            "key_findings": result.key_findings[:3],
            "credits_used": result.credits_used,
        }

    # Run research in parallel with thread pool
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            loop.run_in_executor(executor, do_research, topic)
            for topic in topics
        ]
        results = await asyncio.gather(*futures)

    return results


async def main():
    # Example: Research multiple AI topics
    topics = [
        "LLM fine-tuning best practices",
        "Vector database comparison 2025",
        "RAG architecture patterns",
        "AI agent frameworks overview",
    ]

    print("\n" + "="*60)
    print("Batch Research")
    print("="*60 + "\n")

    print(f"Researching {len(topics)} topics in parallel...")

    results = await research_batch(topics, depth="shallow")

    total_credits = 0
    for result in results:
        print(f"\n## {result['topic']}")
        print(f"Summary: {result['summary'][:200]}...")
        print(f"Credits: {result['credits_used']}")
        total_credits += result['credits_used']

    print(f"\n{'='*60}")
    print(f"Total credits used: {total_credits}")


if __name__ == "__main__":
    asyncio.run(main())
