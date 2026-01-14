#!/usr/bin/env python3
"""
Example: Technology Decision Research

Use Aegis Research to make informed technology decisions.
Compare frameworks, databases, or architectural approaches.
"""

import os
from aegis_research import AegisResearch

client = AegisResearch(api_key=os.environ.get("AEGIS_API_KEY", "res_demo"))


def compare_technologies(tech_a: str, tech_b: str, use_case: str) -> dict:
    """
    Compare two technologies for a specific use case.

    Returns a structured comparison with pros, cons, and recommendation.
    """

    # Research both technologies and compare
    topic = f"{tech_a} vs {tech_b} for {use_case} - comparison pros cons 2025"

    print(f"Researching: {topic}")
    result = client.research(topic, depth="deep")

    return {
        "technologies": [tech_a, tech_b],
        "use_case": use_case,
        "summary": result.summary,
        "key_findings": result.key_findings,
        "detailed_analysis": result.detailed_analysis,
        "sources_count": len(result.sources),
        "credits_used": result.credits_used,
    }


def main():
    # Example: Database decision
    comparison = compare_technologies(
        tech_a="PostgreSQL",
        tech_b="MongoDB",
        use_case="building a SaaS application with complex queries"
    )

    print("\n" + "="*60)
    print(f"Technology Comparison")
    print(f"{comparison['technologies'][0]} vs {comparison['technologies'][1]}")
    print("="*60 + "\n")

    print(f"Use Case: {comparison['use_case']}")
    print(f"\nSummary:\n{comparison['summary']}")

    print(f"\nKey Findings:")
    for finding in comparison['key_findings']:
        print(f"  - {finding}")

    print(f"\nBased on {comparison['sources_count']} sources")
    print(f"Credits used: {comparison['credits_used']}")


if __name__ == "__main__":
    main()
