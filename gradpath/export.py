from __future__ import annotations

from typing import Any

import pandas as pd

from gradpath.scoring import score_program


def build_results(programs: list[dict[str, Any]], profile: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for program in programs:
        fit = score_program(program, profile)
        admit = program.get("admit_confidence", {})
        community = program.get("community_summary", {})
        fit_plan = program.get("next_fit_plan", {})
        source_type = program.get("program_source") or (
            "Seeded" if program["source"].get("confidence") == "Sample" else "Manual URL"
        )
        rows.append(
            {
                "Fit": fit["band"],
                "Score": fit["score"],
                "Program ID": program["id"],
                "Admit Confidence Estimate": admit.get("band", ""),
                "Admit Confidence Score": admit.get("score", ""),
                "Admit Confidence Why": admit.get("why", ""),
                "Source": source_type,
                "Research Set": program.get("research_set_id", ""),
                "Community Evidence": community.get("summary", ""),
                "Publication Expectation": community.get("publication_expectation", ""),
                "Research Expectation": community.get("research_expectation", ""),
                "Search Strategy": program.get("search_strategy", ""),
                "Next Fit Plan": _fit_plan_text(fit_plan),
                "School": program["school"],
                "Program": program["program"],
                "Degree": program["degree"],
                "Field": program["field"],
                "Location": f"{program['location']}, {program['country']}",
                "DDL": program["requirements"]["deadline"],
                "English": program["requirements"]["english"]["summary"],
                "GRE": program["requirements"]["gre"]["summary"],
                "Coursework": ", ".join(program["requirements"]["coursework"]),
                "Funding": program["preferences"]["funding"],
                "Research Fit": program.get("phd", {}).get("research_fit", "N/A"),
                "SOP": program["preferences"]["sop"],
                "Missing": "; ".join(fit["missing"]) or "None flagged",
                "Strengths": "; ".join(fit["strengths"]),
                "Actions": "; ".join(fit["actions"]),
                "SOP Angle": fit["sop_angle"],
                "Confidence": program["source"]["confidence"],
                "Source URL": program["source"]["url"],
            }
        )
    return sorted(rows, key=lambda row: row["Score"], reverse=True)


def results_dataframe(programs: list[dict[str, Any]], profile: dict[str, Any]) -> pd.DataFrame:
    return pd.DataFrame(build_results(programs, profile))


def comparison_dataframe(rows: list[dict[str, Any]]) -> pd.DataFrame:
    fields = [
        "School",
        "Program",
        "Degree",
        "DDL",
        "English",
        "GRE",
        "Coursework",
        "Funding",
        "Research Fit",
        "SOP",
        "Missing",
        "Source URL",
    ]
    return pd.DataFrame([{field: row.get(field, "") for field in fields} for row in rows])


def _fit_plan_text(plan: dict[str, Any]) -> str:
    if not plan:
        return ""
    parts = []
    for key, value in plan.items():
        if isinstance(value, list):
            value = "; ".join(value)
        if value:
            parts.append(f"{key.replace('_', ' ').title()}: {value}")
    return " | ".join(parts)
