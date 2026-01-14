#!/usr/bin/env python3
"""
Example: Startup Due Diligence Research

Use Aegis Research for investment due diligence or partnership evaluation.
Great for VCs, angel investors, and business development teams.
"""

import os
from dataclasses import dataclass
from aegis_research import AegisResearch

client = AegisResearch(api_key=os.environ.get("AEGIS_API_KEY", "res_demo"))


@dataclass
class DueDiligenceReport:
    company: str
    market_position: dict
    technology: dict
    team: dict
    risks: dict
    opportunities: dict
    total_credits_used: int


def run_due_diligence(company: str, industry: str) -> DueDiligenceReport:
    """
    Run comprehensive due diligence research on a company.

    Researches:
    - Market position and competition
    - Technology and product
    - Team and leadership
    - Risks and red flags
    - Growth opportunities
    """

    total_credits = 0

    # Market position
    print(f"Researching market position...")
    market = client.research(
        f"{company} market position competitive landscape {industry}",
        depth="medium"
    )
    total_credits += market.credits_used

    # Technology
    print(f"Researching technology...")
    tech = client.research(
        f"{company} technology stack product architecture",
        depth="medium"
    )
    total_credits += tech.credits_used

    # Team
    print(f"Researching team...")
    team = client.research(
        f"{company} founders leadership team background",
        depth="shallow"
    )
    total_credits += team.credits_used

    # Risks
    print(f"Researching risks...")
    risks = client.research(
        f"{company} risks challenges controversies concerns",
        depth="medium"
    )
    total_credits += risks.credits_used

    # Opportunities
    print(f"Researching opportunities...")
    opps = client.research(
        f"{company} growth opportunities expansion plans future",
        depth="shallow"
    )
    total_credits += opps.credits_used

    return DueDiligenceReport(
        company=company,
        market_position={
            "summary": market.summary,
            "findings": market.key_findings,
        },
        technology={
            "summary": tech.summary,
            "findings": tech.key_findings,
        },
        team={
            "summary": team.summary,
            "findings": team.key_findings,
        },
        risks={
            "summary": risks.summary,
            "findings": risks.key_findings,
        },
        opportunities={
            "summary": opps.summary,
            "findings": opps.key_findings,
        },
        total_credits_used=total_credits,
    )


def main():
    company = "Anthropic"
    industry = "AI"

    print("\n" + "="*60)
    print(f"Due Diligence Report: {company}")
    print("="*60 + "\n")

    report = run_due_diligence(company, industry)

    sections = [
        ("Market Position", report.market_position),
        ("Technology", report.technology),
        ("Team & Leadership", report.team),
        ("Risks & Concerns", report.risks),
        ("Growth Opportunities", report.opportunities),
    ]

    for title, data in sections:
        print(f"\n## {title}")
        print(f"{data['summary']}")
        print(f"\nKey Findings:")
        for finding in data['findings'][:3]:
            print(f"  - {finding}")

    print(f"\n{'='*60}")
    print(f"Total credits used: {report.total_credits_used}")

    status = client.credits()
    print(f"Credits remaining: {status.credits_remaining}")


if __name__ == "__main__":
    main()
