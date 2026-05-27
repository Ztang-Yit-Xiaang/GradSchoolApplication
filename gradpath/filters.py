from __future__ import annotations

from typing import Any

from gradpath.scoring import deadline_days


def filter_programs(
    programs: list[dict[str, Any]],
    degree: str = "All",
    fields: list[str] | None = None,
    country: str = "All",
    funding: str = "Any",
    deadline_window: str = "Any",
    program_source: str = "All",
    confidence: str = "All",
    admit_band: str = "All",
    latest_research_set_id: str = "",
    only_researched: bool = False,
) -> list[dict[str, Any]]:
    fields = fields or []
    filtered = []
    for program in programs:
        if degree != "All" and program["degree"] != degree:
            continue
        if fields and program["field"] not in fields:
            continue
        if country != "All" and program["country"] != country:
            continue
        if funding == "Funded/assistantship visible":
            funding_text = program["preferences"]["funding"].lower()
            if not any(word in funding_text for word in ["funded", "assistantship", "fellowship"]):
                continue
        if not _deadline_matches(program, deadline_window):
            continue
        if not _source_matches(program, program_source):
            continue
        if confidence != "All" and program["source"].get("confidence") != confidence:
            continue
        admit = program.get("admit_confidence", {}).get("band", "")
        if admit_band != "All" and admit != admit_band:
            continue
        if only_researched and program.get("research_set_id") != latest_research_set_id:
            continue
        filtered.append(program)
    return filtered


def _deadline_matches(program: dict[str, Any], deadline_window: str) -> bool:
    days = deadline_days(program["requirements"]["deadline"])
    if deadline_window == "Any" or days is None:
        return True
    if deadline_window == "Next 60 days":
        return 0 <= days <= 60
    if deadline_window == "Next 120 days":
        return 0 <= days <= 120
    if deadline_window == "Future only":
        return days >= 0
    return True


def _source_matches(program: dict[str, Any], program_source: str) -> bool:
    if program_source == "All":
        return True
    source_type = program.get("program_source") or (
        "Seeded" if program["source"].get("confidence") == "Sample" else "Manual URL"
    )
    if program_source == "AI Enriched Sample" and source_type in {
        "AI Enriched Sample",
        "AI Enriched Seeded",
        "Enriched Seeded",
    }:
        return True
    return source_type == program_source
