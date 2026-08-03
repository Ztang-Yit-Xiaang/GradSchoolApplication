from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from gradpath.scoring import deadline_days

MATCH_SCORE_WEIGHTS = {
    "research_fit": 0.35,
    "evidence_fit": 0.20,
    "letter_fit": 0.15,
    "route_fit": 0.15,
    "practical_feasibility": 0.15,
}

REFERENCE_EXPORT_COLUMNS = [
    "University",
    "Program",
    "Track",
    "Category",
    "Degree",
    "Application Website",
    "Deadline",
    "TOEFL/GRE",
    "POI Fit",
    "Professors",
    "System Type",
    "System Evidence",
    "System Confidence",
    "Job Value",
    "Risk Note",
    "Source",
    "Next Action",
    "Research Signal",
    "Letter Strategy",
    "GRE Strategy",
    "English / TOEFL Strategy",
    "TA / Funding Note",
    "Status",
    "Overall Score",
    "Research Fit Score",
    "Evidence Fit Score",
    "Letter Fit Score",
    "Route Fit Score",
    "Feasibility Score",
    "Balance Note",
    "Last Reviewed",
]

TAG_SYNONYMS = {
    "optimization": [
        "optimization",
        "optimisation",
        "operations research",
        "convex",
        "stochastic",
        "linear programming",
        "osqp",
    ],
    "randnla": [
        "randnla",
        "randomized numerical linear algebra",
        "randomized linear algebra",
        "sketching",
        "numerical linear algebra",
    ],
    "scientific computing": [
        "scientific computing",
        "numerical analysis",
        "computational mathematics",
        "tensor",
        "high performance computing",
    ],
    "decision systems": [
        "decision system",
        "decision systems",
        "decision-making",
        "sequential decision",
        "online decision",
        "operations",
        "transportation",
        "urban",
    ],
    "transportation": ["transportation", "mobility", "traffic", "travel", "itinerary"],
    "urban systems": ["urban", "city", "smart cities", "infrastructure"],
    "ml systems": ["machine learning systems", "ml systems", "systems", "scalable ml"],
    "sensing/inverse modeling": ["sensing", "inverse", "inverse modeling", "signal"],
}

SELECTIVE_SCHOOLS = {
    "stanford",
    "mit",
    "massachusetts institute",
    "berkeley",
    "carnegie mellon",
    "cmu",
    "princeton",
    "harvard",
    "cornell",
    "caltech",
    "columbia",
    "ucla",
}

TOP_LOTTERY_SCHOOLS = {
    "stanford",
    "mit",
    "massachusetts institute",
    "harvard",
    "princeton",
    "berkeley",
    "carnegie mellon",
    "cmu",
    "caltech",
}


def _is_top_lottery_school(program: dict[str, Any]) -> bool:
    text = f"{program.get('school', '')} {program.get('program', '')}".lower()
    return any(name in text for name in TOP_LOTTERY_SCHOOLS)



@dataclass(frozen=True)
class MatchResult:
    research_fit: int
    evidence_fit: int
    letter_fit: int
    route_fit: int
    practical_feasibility: int
    overall_fit: int
    category: str
    status: str
    poi_fit: str
    risk_note: str
    next_action: str
    research_signal: str
    letter_strategy: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "research_fit": self.research_fit,
            "evidence_fit": self.evidence_fit,
            "letter_fit": self.letter_fit,
            "route_fit": self.route_fit,
            "practical_feasibility": self.practical_feasibility,
            "overall_fit": self.overall_fit,
            "category": self.category,
            "status": self.status,
            "poi_fit": self.poi_fit,
            "risk_note": self.risk_note,
            "next_action": self.next_action,
            "research_signal": self.research_signal,
            "letter_strategy": self.letter_strategy,
        }


def normalize_matching_profile(profile: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(profile)
    normalized.setdefault(
        "primary_tags",
        ["optimization", "RandNLA", "scientific computing", "decision systems"],
    )
    normalized.setdefault(
        "secondary_tags",
        ["transportation", "urban systems", "ML systems", "sensing/inverse modeling"],
    )
    normalized.setdefault(
        "evidence",
        {
            "projects": [
                "OSQP/Torch optimization work with Ju Sun",
                "RandNLA UROP with Swati Padmanabhan",
                "Travel-itinerary predictive optimization with Prof. Choi",
                "Sensing/inverse modeling with Prof. Hongliang Ren",
            ],
            "papers": [
                "Travel-itinerary paper may be in preparation/submitted/accepted later",
                "OSQP/Torch and RandNLA papers must be labeled only by true status",
            ],
            "teaching": ["UMN undergraduate TA experience in CSCI 2081"],
        },
    )
    normalized.setdefault(
        "test_strategy",
        {
            "gre": (
                "Probably no retake. Submit GRE only where optional and helpful for "
                "quant-heavy OR/IE/applied math/MS programs."
            ),
            "english": (
                "Fall 2023 TOEFL may expire for Fall 2027; verify U.S. bachelor's "
                "degree waivers and school-specific TA/oral rules."
            ),
            "ta": (
                "Prior TOEFL Speaking and UMN TA experience support teaching readiness, "
                "but oral-proficiency rules must be checked school by school."
            ),
        },
    )
    normalized.setdefault(
        "recommenders",
        {
            "Ju": "Optimization, OSQP/Torch, scalable computation, local PhD fit",
            "Swati": "RandNLA, randomized algorithms, scientific computing",
            "Choi": "Transportation, urban systems, decision systems, itinerary paper",
            "Ren": "Sensing, inverse modeling, signal-processing angle",
        },
    )
    return normalized


def normalize_program_matching(program: dict[str, Any]) -> dict[str, Any]:
    matching = dict(program.get("matching", {}))
    matching.setdefault("program_route", _infer_program_route(program))
    matching.setdefault("poi_list", _infer_poi_list(program))
    matching.setdefault("admission_system", _infer_admission_system(program))
    matching.setdefault("test_policy", _infer_test_policy(program))
    matching.setdefault("risk_factors", _infer_risk_factors(program))
    matching.setdefault("job_backup_value", _infer_job_backup_value(program))
    return matching


def calculate_real_stipend(stipend_amount: float | int, location: str = "") -> dict[str, Any]:
    """Calculates cost-of-living adjusted real stipend based on regional multipliers."""
    if not stipend_amount or stipend_amount <= 0:
        return {"nominal": 0, "col_index": 1.0, "real_stipend": 0, "tier": "Unknown"}

    loc_lower = location.lower()
    # Cost-of-Living index multiplier relative to baseline US national average (100)
    if any(city in loc_lower for city in ["stanford", "berkeley", "san francisco", "bay area", "palo alto"]):
        col_index = 1.85
    elif any(city in loc_lower for city in ["boston", "cambridge", "mit", "harvard", "new york", "columbia"]):
        col_index = 1.70
    elif any(city in loc_lower for city in ["los angeles", "ucla", "seattle", "washington", "london"]):
        col_index = 1.50
    elif any(city in loc_lower for city in ["chicago", "eth", "zurich", "singapore", "toronto"]):
        col_index = 1.35
    elif any(city in loc_lower for city in ["champaign", "urbana", "west lafayette", "purdue", "madison"]):
        col_index = 1.05
    else:
        col_index = 1.15

    real_stipend = round(stipend_amount / col_index)
    if real_stipend >= 32000:
        tier = "Comfortable"
    elif real_stipend >= 25000:
        tier = "Workable"
    else:
        tier = "Tight"

    return {
        "nominal": stipend_amount,
        "col_index": col_index,
        "real_stipend": real_stipend,
        "tier": tier,
    }


def score_match(
    program: dict[str, Any],
    profile: dict[str, Any],
    custom_weights: dict[str, float] | None = None,
) -> MatchResult:
    profile = normalize_matching_profile(profile)
    matching = normalize_program_matching(program)
    route = matching["program_route"]
    haystack = _program_text(program, matching)
    primary_hits = _matched_tags(profile.get("primary_tags", []), haystack)
    secondary_hits = _matched_tags(profile.get("secondary_tags", []), haystack)
    concrete_pois = _concrete_pois(matching.get("poi_list", []))
    degree = program.get("degree", "")

    research_fit = _score_research_fit(
        profile, program, primary_hits, secondary_hits, concrete_pois
    )
    evidence_fit = _score_evidence_fit(profile, primary_hits, secondary_hits)
    letter_names = choose_recommenders(route, haystack)
    letter_fit = _score_letter_fit(profile, letter_names)
    route_fit = _score_route_fit(route, degree, primary_hits, secondary_hits, haystack)
    feasibility = _score_practical_feasibility(program, profile, matching)

    weights = dict(MATCH_SCORE_WEIGHTS)
    if custom_weights:
        total_w = sum(custom_weights.values()) or 1.0
        weights = {k: custom_weights.get(k, MATCH_SCORE_WEIGHTS[k]) / total_w for k in MATCH_SCORE_WEIGHTS}

    overall = round(
        (weights["research_fit"] * research_fit)
        + (weights["evidence_fit"] * evidence_fit)
        + (weights["letter_fit"] * letter_fit)
        + (weights["route_fit"] * route_fit)
        + (weights["practical_feasibility"] * feasibility)
    )

    category, status = _category_and_status(
        program, matching, overall, research_fit, feasibility, concrete_pois, haystack
    )

    letter_strategy = "; ".join(letter_names)
    result = MatchResult(
        research_fit=research_fit,
        evidence_fit=evidence_fit,
        letter_fit=letter_fit,
        route_fit=route_fit,
        practical_feasibility=feasibility,
        overall_fit=overall,
        category=category,
        status=status,
        poi_fit=_poi_fit_sentence(program, route, primary_hits, secondary_hits, concrete_pois),
        risk_note=_risk_note(program, matching, category, feasibility, concrete_pois),
        next_action=_next_action(program, matching, category, concrete_pois),
        research_signal=_research_signal(profile),
        letter_strategy=letter_strategy,
    )
    return apply_ai_match_reasoning(result, program.get("match_ai_reasoning", {}))


def apply_ai_match_reasoning(result: MatchResult, ai_reasoning: dict[str, Any]) -> MatchResult:
    if not ai_reasoning:
        return result
    scores = {
        "research_fit": _bounded_int(ai_reasoning.get("research_fit"), result.research_fit),
        "evidence_fit": _bounded_int(ai_reasoning.get("evidence_fit"), result.evidence_fit),
        "letter_fit": _bounded_int(ai_reasoning.get("letter_fit"), result.letter_fit),
        "route_fit": _bounded_int(ai_reasoning.get("route_fit"), result.route_fit),
        "practical_feasibility": _bounded_int(
            ai_reasoning.get("practical_feasibility"), result.practical_feasibility
        ),
    }
    overall = _bounded_int(ai_reasoning.get("overall_fit"), 0)
    if not overall:
        overall = round(
            (MATCH_SCORE_WEIGHTS["research_fit"] * scores["research_fit"])
            + (MATCH_SCORE_WEIGHTS["evidence_fit"] * scores["evidence_fit"])
            + (MATCH_SCORE_WEIGHTS["letter_fit"] * scores["letter_fit"])
            + (MATCH_SCORE_WEIGHTS["route_fit"] * scores["route_fit"])
            + (MATCH_SCORE_WEIGHTS["practical_feasibility"] * scores["practical_feasibility"])
        )
    category = str(ai_reasoning.get("category") or result.category)
    if category not in {"衝刺", "Moderate", "保底/Lower-risk PhD", "MS/job", "Demoted/archive"}:
        category = result.category
    status = str(ai_reasoning.get("status") or result.status)
    if status not in {"Active", "MS backup", "Demoted/archive"}:
        status = result.status
    return MatchResult(
        research_fit=scores["research_fit"],
        evidence_fit=scores["evidence_fit"],
        letter_fit=scores["letter_fit"],
        route_fit=scores["route_fit"],
        practical_feasibility=scores["practical_feasibility"],
        overall_fit=overall,
        category=category,
        status=status,
        poi_fit=_clean_sentence(ai_reasoning.get("poi_fit"), result.poi_fit),
        risk_note=_clean_sentence(ai_reasoning.get("risk_note"), result.risk_note),
        next_action=_clean_sentence(ai_reasoning.get("next_action"), result.next_action),
        research_signal=_safe_research_signal(
            str(ai_reasoning.get("research_signal") or result.research_signal),
            result.research_signal,
        ),
        letter_strategy=_clean_sentence(
            ai_reasoning.get("letter_strategy"), result.letter_strategy
        ),
    )


def build_matching_rows(
    programs: list[dict[str, Any]],
    profile: dict[str, Any],
    custom_weights: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    rows = [
        _row_from_match(program, score_match(program, profile, custom_weights=custom_weights), profile)
        for program in programs
    ]
    rows = sorted(
        rows,
        key=lambda row: (-row["Overall Score"], row["University"], row["Program"]),
    )
    return balance_shortlist(rows)


def balance_shortlist(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    balanced = [dict(row) for row in rows]
    active_phd = [
        row for row in balanced if row["Degree"] == "PhD" and row["Status"] == "Active"
    ]
    ms_backups = [row for row in balanced if row["Track"] == "MS/job"]
    sprint = [row for row in active_phd if row["Category"] == "衝刺"]

    if len(active_phd) < 20:
        _append_balance_note(
            balanced,
            f"Need {20 - len(active_phd)} more active PhD route(s) to reach the 20-25 target.",
        )
    elif len(active_phd) > 25:
        overflow = sorted(active_phd, key=lambda row: row["Overall Score"])[: len(active_phd) - 25]
        overflow_ids = {row["Program ID"] for row in overflow}
        for row in balanced:
            if row["Program ID"] in overflow_ids:
                row["Status"] = "Demoted/archive"
                row["Track"] = "Archive"
                row["Category"] = "Demoted/archive"
                row["Balance Note"] = "Demoted to keep active PhD routes near 20-25."

    if len(ms_backups) < 6:
        _append_balance_note(
            balanced,
            f"Need {6 - len(ms_backups)} more MS/job backup(s) to reach the 6-10 target.",
        )
    elif len(ms_backups) > 10:
        low_priority = sorted(ms_backups, key=lambda item: item["Overall Score"])
        for row in low_priority[: len(ms_backups) - 10]:
            row["Balance Note"] = "Low-priority MS backup; keep only if ROI is attractive."

    active_phd = [
        row for row in balanced if row["Degree"] == "PhD" and row["Status"] == "Active"
    ]
    sprint = [row for row in active_phd if row["Category"] == "衝刺"]
    if active_phd and len(sprint) / len(active_phd) > 0.45:
        for row in sprint:
            row["Balance Note"] = _join_note(
                row["Balance Note"], "衝刺 share is high; add more moderate/lower-risk POI routes."
            )

    for row in balanced:
        if _looks_generic_or_ranking_only(row):
            row["Status"] = "Demoted/archive"
            row["Track"] = "Archive"
            row["Category"] = "Demoted/archive"
            row["Balance Note"] = _join_note(
                row["Balance Note"], "Demoted because POI or route fit is too generic."
            )
    return balanced


def choose_recommenders(program_route: str, program_text: str = "") -> list[str]:
    route = f"{program_route} {program_text}".lower()
    if any(word in route for word in ["transportation", "urban", "cee", "mobility"]):
        return ["Choi", "Ju", "Swati"]
    if any(word in route for word in ["randnla", "randomized", "sketching"]):
        return ["Swati", "Ju", "Choi"]
    if any(word in route for word in ["sensing", "inverse", "signal"]):
        return ["Ren", "Ju", "Swati"]
    if any(word in route for word in ["operations", "industrial", "or/ie", "optimization"]):
        return ["Ju", "Choi", "Swati"]
    return ["Ju", "Swati", "Choi"]


def _row_from_match(
    program: dict[str, Any], match: MatchResult, profile: dict[str, Any]
) -> dict[str, Any]:
    matching = normalize_program_matching(program)
    reqs = program.get("requirements", {})
    english = reqs.get("english", {}).get("summary", "Needs review")
    gre = reqs.get("gre", {}).get("summary", "Needs review")
    source_type = program.get("program_source") or (
        "Seeded" if program.get("source", {}).get("confidence") == "Sample" else "Manual URL"
    )
    track = "MS/job" if program.get("degree") != "PhD" else "PhD"
    if match.status == "Demoted/archive":
        track = "Archive"
    row = {
        "University": program.get("school", ""),
        "Program": program.get("program", ""),
        "Track": track,
        "Category": match.category,
        "Degree": program.get("degree", ""),
        "Application Website": program.get("source", {}).get("url", ""),
        "Deadline": reqs.get("deadline", ""),
        "TOEFL/GRE": f"{english} | {gre}",
        "POI Fit": match.poi_fit,
        "Professors": "; ".join(_concrete_pois(matching.get("poi_list", [])))
        or "; ".join(program.get("phd", {}).get("faculty_areas", [])[:3]),
        "System Type": matching.get("admission_system", ""),
        "System Evidence": program.get("admit_confidence", {}).get(
            "why", program.get("phd", {}).get("research_fit", "")
        ),
        "System Confidence": program.get("source", {}).get("confidence", ""),
        "Job Value": matching.get("job_backup_value", ""),
        "Risk Note": match.risk_note,
        "Source": source_type,
        "Next Action": match.next_action,
        "Research Signal": match.research_signal,
        "Letter Strategy": match.letter_strategy,
        "GRE Strategy": _strategy_text(profile, "gre"),
        "English / TOEFL Strategy": _strategy_text(profile, "english"),
        "TA / Funding Note": _strategy_text(profile, "ta"),
        "Status": match.status,
        "Overall Score": match.overall_fit,
        "Research Fit Score": match.research_fit,
        "Evidence Fit Score": match.evidence_fit,
        "Letter Fit Score": match.letter_fit,
        "Route Fit Score": match.route_fit,
        "Feasibility Score": match.practical_feasibility,
        "Balance Note": "",
        "Last Reviewed": date.today().isoformat(),
        "Program ID": program.get("id", ""),
        "Field": program.get("field", ""),
        "Location": f"{program.get('location', '')}, {program.get('country', '')}",
        "Research Set": program.get("research_set_id", ""),
        "Search Strategy": program.get("search_strategy", ""),
        "Confidence": program.get("source", {}).get("confidence", ""),
        "Source URL": program.get("source", {}).get("url", ""),
    }
    row.update(_legacy_columns(row, program))
    return row


def _legacy_columns(row: dict[str, Any], program: dict[str, Any]) -> dict[str, Any]:
    score = row["Overall Score"]
    if score >= 82:
        fit = "Strong"
    elif score >= 68:
        fit = "Good"
    elif score >= 50:
        fit = "Needs Review"
    else:
        fit = "Risky"
    return {
        "Fit": fit,
        "Score": score,
        "School": row["University"],
        "DDL": row["Deadline"],
        "English": program.get("requirements", {}).get("english", {}).get("summary", ""),
        "GRE": program.get("requirements", {}).get("gre", {}).get("summary", ""),
        "Coursework": ", ".join(program.get("requirements", {}).get("coursework", [])),
        "Funding": program.get("preferences", {}).get("funding", ""),
        "Research Fit": row["POI Fit"],
        "SOP": program.get("preferences", {}).get("sop", ""),
        "Missing": row["Risk Note"] or "None flagged",
        "Strengths": row["POI Fit"],
        "Actions": row["Next Action"],
        "SOP Angle": row["POI Fit"],
        "Admit Confidence Estimate": row["Category"],
        "Admit Confidence Score": row["Overall Score"],
        "Admit Confidence Why": row["Risk Note"],
        "Community Evidence": program.get("community_summary", {}).get("summary", ""),
        "Publication Expectation": program.get("community_summary", {}).get(
            "publication_expectation", ""
        ),
        "Research Expectation": program.get("community_summary", {}).get(
            "research_expectation", ""
        ),
        "Next Fit Plan": program.get("next_fit_plan", {}).get("sop_angle", ""),
    }


def _score_research_fit(
    profile: dict[str, Any],
    program: dict[str, Any],
    primary_hits: list[str],
    secondary_hits: list[str],
    concrete_pois: list[str],
) -> int:
    primary_total = max(len(profile.get("primary_tags", [])), 1)
    primary_score = 72 * (len(primary_hits) / primary_total)
    secondary_score = min(len(secondary_hits), 2) * 7
    poi_score = 14 if concrete_pois else 4
    score = round(primary_score + secondary_score + poi_score)
    if program.get("degree") == "PhD" and not concrete_pois:
        score = min(score, 68)
    return _clip(score)


def _score_evidence_fit(
    profile: dict[str, Any], primary_hits: list[str], secondary_hits: list[str]
) -> int:
    evidence_text = _profile_evidence_text(profile)
    score = 38
    for tag in [*primary_hits, *secondary_hits[:2]]:
        if _tag_matches_text(tag, evidence_text):
            score += 13
    if "publication" in " ".join(profile.get("experience", [])).lower():
        score += 8
    paper_status_words = ["submitted", "accepted", "in preparation", "in-prep"]
    if any(word in evidence_text for word in paper_status_words):
        score += 8
    return _clip(score)


def _score_letter_fit(profile: dict[str, Any], letter_names: list[str]) -> int:
    recommenders = profile.get("recommenders", {})
    found = [name for name in letter_names if name in recommenders]
    score = 45 + (len(found) * 15)
    if len(found) == 3:
        score += 10
    return _clip(score)


def _score_route_fit(
    route: str,
    degree: str,
    primary_hits: list[str],
    secondary_hits: list[str],
    haystack: str,
) -> int:
    route_lower = route.lower()
    if degree != "PhD":
        job_words = ["career", "job", "industry", "capstone"]
        return 76 if any(word in haystack for word in job_words) else 68
    if any(word in route_lower for word in ["or/ie", "operations", "applied math", "statistics"]):
        return 88 if primary_hits else 72
    if any(word in route_lower for word in ["transportation", "cee", "urban"]):
        return 86 if secondary_hits or "decision systems" in primary_hits else 70
    if "computer science" in route_lower or route_lower == "cs":
        return 78 if primary_hits else 52
    return 66 if primary_hits else 48


def _score_practical_feasibility(
    program: dict[str, Any], profile: dict[str, Any], matching: dict[str, Any]
) -> int:
    score = 72
    if _is_top_lottery_school(program):
        score -= 15  # Penalty for top hyper-selective schools (Stanford, MIT, Harvard, Berkeley, CMU, etc.)
    reqs = program.get("requirements", {})
    gre = reqs.get("gre", {})
    gre_text = f"{gre.get('status', '')} {gre.get('summary', '')}".lower()
    if "not required" in gre_text or "not reviewed" in gre_text:
        score += 8
    elif "optional" in gre_text:
        score += 5
    elif profile.get("gre_status") != "Completed":
        score -= 14
    english = reqs.get("english", {})
    english_score = profile.get("english_score") or 0
    minimum = english.get("minimum_score") or 0
    english_text = english.get("summary", "").lower()
    if english.get("required") and minimum and english_score < minimum:
        score -= 14
    elif "waiver" in english_text or "exempt" in english_text:
        score += 4
    if profile.get("funding_need") == "Critical":
        funding = program.get("preferences", {}).get("funding", "").lower()
        if any(word in funding for word in ["funded", "assistantship", "fellowship"]):
            score += 6
        elif program.get("degree") == "PhD":
            score -= 10
    days = deadline_days(reqs.get("deadline", ""))
    if days is not None and days < 0:
        score -= 20
    confidence = program.get("source", {}).get("confidence", "").lower()
    if "needs review" in confidence:
        score -= 5
    risk_text = " ".join(matching.get("risk_factors", [])).lower()
    if any(word in risk_text for word in ["capacity", "selective", "publication"]):
        score -= 6
    return _clip(score)


def _category_and_status(
    program: dict[str, Any],
    matching: dict[str, Any],
    overall: int,
    research_fit: int,
    feasibility: int,
    concrete_pois: list[str],
    haystack: str,
) -> tuple[str, str]:
    if program.get("degree") != "PhD":
        return "MS/job", "MS backup"
    if _is_local_lower_risk(program, haystack) and overall >= 68:
        return "保底/Lower-risk PhD", "Active"
    if research_fit < 42 or (not concrete_pois and overall < 55):
        return "Demoted/archive", "Demoted/archive"
    if _is_top_lottery_school(program) or _is_selective(program) or feasibility < 62 or (not concrete_pois and research_fit >= 55):
        return "衝刺", "Active"
    if overall >= 58:
        return "Moderate", "Active"
    return "Demoted/archive", "Demoted/archive"


def _poi_fit_sentence(
    program: dict[str, Any],
    route: str,
    primary_hits: list[str],
    secondary_hits: list[str],
    concrete_pois: list[str],
) -> str:
    tags = primary_hits or secondary_hits or ["quantitative preparation"]
    poi = ", ".join(concrete_pois[:2]) if concrete_pois else "named faculty to verify"
    return (
        f"{program.get('school', 'This program')} is real through the {route} route: "
        f"{poi} can read the applicant as {' + '.join(tags[:3])}."
    )


def _risk_note(
    program: dict[str, Any],
    matching: dict[str, Any],
    category: str,
    feasibility: int,
    concrete_pois: list[str],
) -> str:
    risks = list(matching.get("risk_factors", []))
    if _is_top_lottery_school(program):
        risks.append("Top hyper-selective lottery school (Stanford/MIT/Harvard/etc.); selectivity penalty applied")
    if not concrete_pois and program.get("degree") == "PhD":
        risks.append("POI names/capacity are not verified")
    if feasibility < 65:
        risks.append("test, funding, or deadline feasibility needs review")
    if category == "衝刺":
        risks.append("selectivity or advisor availability can kill the application")
    if not risks:
        risks.append("still competitive; verify advisor availability and official test policy")
    return "; ".join(_dedupe(risks)[:3])


def _next_action(
    program: dict[str, Any],
    matching: dict[str, Any],
    category: str,
    concrete_pois: list[str],
) -> str:
    if category == "Demoted/archive":
        return "Archive unless a concrete POI and department route are identified."
    if program.get("degree") != "PhD":
        return "Verify MS ROI, deadline, English waiver, and job-placement value."
    if concrete_pois:
        return f"Email or read recent papers from {concrete_pois[0]} and verify recruiting fit."
    route = matching.get("program_route", "department")
    return f"Verify the {route} route and identify 2-3 active POIs before applying."


def _research_signal(profile: dict[str, Any]) -> str:
    evidence = _profile_evidence_text(profile)
    if "accepted" in evidence:
        return "Accepted paper/project only where the acceptance is verifiable."
    if "submitted" in evidence:
        return "Submitted papers may be listed as submitted; do not overclaim acceptance."
    return "In-prep/submitted/accepted status must be labeled accurately at application time."


def _safe_research_signal(candidate: str, fallback: str) -> str:
    lowered = candidate.lower()
    if "accepted" in lowered and "accepted" not in fallback.lower():
        return fallback
    if any(word in lowered for word in ["in-prep", "in preparation", "submitted", "accepted"]):
        return candidate
    return fallback


def _infer_program_route(program: dict[str, Any]) -> str:
    text = f"{program.get('program', '')} {program.get('field', '')}".lower()
    if any(word in text for word in ["ieor", "iems", "industrial", "operations research", "isye"]):
        return "OR/IE"
    if any(word in text for word in ["cee", "civil", "transportation"]):
        return "CEE/transportation"
    if "applied math" in text or "mathematics" in text or "math" in text:
        return "Applied Math"
    if "stat" in text:
        return "Statistics"
    if "data science" in text:
        return "Data Science"
    if "computer science" in text or "cs" in text or "cse" in text:
        return "CS"
    return program.get("field", "Needs Review")


def _infer_poi_list(program: dict[str, Any]) -> list[str]:
    matching = program.get("matching", {})
    if matching.get("poi_list"):
        return list(matching["poi_list"])
    faculty = program.get("phd", {}).get("faculty_areas", [])
    return [item for item in faculty if _looks_like_name(item)]


def _infer_admission_system(program: dict[str, Any]) -> str:
    text = _program_text(program, {}).lower()
    if any(word in text for word in ["committee", "graduate admissions committee"]):
        return "committee"
    if any(word in text for word in ["advisor", "supervisor", "faculty sponsor"]):
        return "advisor-driven/mixed"
    return "mixed/verify"


def _infer_test_policy(program: dict[str, Any]) -> str:
    reqs = program.get("requirements", {})
    english = reqs.get("english", {}).get("summary", "English policy needs review")
    gre = reqs.get("gre", {}).get("summary", "GRE policy needs review")
    return f"{gre}; {english}"


def _infer_risk_factors(program: dict[str, Any]) -> list[str]:
    risks = []
    if _is_selective(program):
        risks.append("high selectivity")
    if program.get("degree") == "PhD" and not _infer_poi_list(program):
        risks.append("POI capacity unknown")
    if "needs review" in _program_text(program, {}).lower():
        risks.append("source or route ambiguity")
    return risks or ["competitive admissions"]


def _infer_job_backup_value(program: dict[str, Any]) -> str:
    if program.get("degree") == "PhD":
        return "Not a job-backup row; evaluate only for PhD mentorship."
    text = f"{program.get('school', '')} {program.get('location', '')}".lower()
    if any(word in text for word in ["georgia tech", "illinois", "uiuc", "usc", "washington"]):
        return "High MS/job backup value if cost and placement are acceptable."
    return "MS/job backup value needs ROI and placement verification."


def _program_text(program: dict[str, Any], matching: dict[str, Any]) -> str:
    parts: list[str] = [
        program.get("school", ""),
        program.get("program", ""),
        program.get("field", ""),
        program.get("location", ""),
        matching.get("program_route", ""),
        matching.get("admission_system", ""),
        matching.get("test_policy", ""),
        matching.get("job_backup_value", ""),
        program.get("preferences", {}).get("program", ""),
        program.get("preferences", {}).get("sop", ""),
        program.get("preferences", {}).get("funding", ""),
        program.get("phd", {}).get("research_fit", ""),
    ]
    parts.extend(program.get("requirements", {}).get("coursework", []))
    parts.extend(program.get("phd", {}).get("faculty_areas", []))
    parts.extend(matching.get("poi_list", []))
    parts.extend(matching.get("risk_factors", []))
    return " ".join(str(part) for part in parts if part).lower()


def _profile_evidence_text(profile: dict[str, Any]) -> str:
    evidence = profile.get("evidence", {})
    parts: list[str] = []
    if isinstance(evidence, dict):
        for value in evidence.values():
            if isinstance(value, list):
                parts.extend(str(item) for item in value)
            else:
                parts.append(str(value))
    elif isinstance(evidence, list):
        parts.extend(str(item) for item in evidence)
    else:
        parts.append(str(evidence))
    parts.extend(profile.get("experience", []))
    parts.extend(profile.get("research_interests", []))
    return " ".join(parts).lower()


def _matched_tags(tags: list[str], text: str) -> list[str]:
    matched = []
    for tag in tags:
        normalized = tag.lower()
        if _tag_matches_text(normalized, text):
            matched.append(tag)
    return matched


def _tag_matches_text(tag: str, text: str) -> bool:
    variants = TAG_SYNONYMS.get(tag.lower(), [tag.lower()])
    return any(variant in text for variant in variants)


def _concrete_pois(values: list[str]) -> list[str]:
    return [value for value in values if _looks_like_name(value)]


def _looks_like_name(value: str) -> bool:
    if not value or "needs review" in value.lower():
        return False
    words = value.replace(";", " ").split()
    return 2 <= len(words) <= 5 and any(word[:1].isupper() for word in words)


def _is_selective(program: dict[str, Any]) -> bool:
    text = f"{program.get('school', '')} {program.get('program', '')}".lower()
    return any(name in text for name in SELECTIVE_SCHOOLS)


def _is_local_lower_risk(program: dict[str, Any], haystack: str) -> bool:
    school = program.get("school", "").lower()
    return "minnesota" in school and any(name in haystack for name in ["ju", "swati", "choi"])


def _strategy_text(profile: dict[str, Any], key: str) -> str:
    strategy = normalize_matching_profile(profile).get("test_strategy", {})
    if isinstance(strategy, dict):
        return strategy.get(key, "")
    return str(strategy)


def _append_balance_note(rows: list[dict[str, Any]], note: str) -> None:
    for row in rows:
        row["Balance Note"] = _join_note(row.get("Balance Note", ""), note)


def _join_note(existing: str, note: str) -> str:
    if not existing:
        return note
    if note in existing:
        return existing
    return f"{existing} {note}"


def _looks_generic_or_ranking_only(row: dict[str, Any]) -> bool:
    text = f"{row.get('POI Fit', '')} {row.get('Risk Note', '')}".lower()
    return row["Overall Score"] < 50 and any(
        phrase in text for phrase in ["named faculty to verify", "too generic", "route ambiguity"]
    )


def _clean_sentence(value: Any, fallback: str) -> str:
    text = str(value or "").strip()
    if not text:
        return fallback
    return " ".join(text.split())


def _bounded_int(value: Any, fallback: int) -> int:
    try:
        return _clip(round(float(value)))
    except (TypeError, ValueError):
        return fallback


def _clip(value: int) -> int:
    return max(0, min(100, value))


def _dedupe(values: list[str]) -> list[str]:
    seen = set()
    deduped = []
    for value in values:
        normalized = " ".join(str(value).split())
        lowered = normalized.lower()
        if normalized and lowered not in seen:
            seen.add(lowered)
            deduped.append(normalized)
    return deduped


def build_pi_outreach_urls(prof_name: str, university: str = "") -> dict[str, str]:
    """Generates 1-click research & outreach URLs for a given professor."""
    p_q = prof_name.replace(" ", "+")
    u_q = university.replace(" ", "+")
    combined = f"{p_q}+{u_q}" if u_q else p_q

    return {
        "nsf_awards": f"https://www.nsf.gov/awardsearch/simpleSearchResult?queryText={combined}",
        "nih_reporter": f"https://reporter.nih.gov/search?q={combined}",
        "darpa_grants": f"https://www.google.com/search?q=site%3Adarpa.mil+OR+site%3Asamhsa.gov+{combined}+grant+contract",
        "google_scholar": f"https://scholar.google.com/scholar?q={combined}",
        "linkedin": f"https://www.google.com/search?q=site%3Alinkedin.com%2Fin%2F+{combined}",
        "x_twitter": f"https://www.google.com/search?q=site%3Ax.com+OR+site%3Atwitter.com+{combined}",
        "personal_homepage": f"https://www.google.com/search?q={combined}+faculty+homepage+lab",
    }


def pi_hiring_signal(prof_name: str, note_text: str = "") -> dict[str, Any]:
    """Evaluates hiring likelihood signal based on NSF/NIH/DARPA grant keywords."""
    note_low = note_text.lower()
    has_recent_grant = any(
        kw in note_low
        for kw in ["nsf", "nih", "darpa", "doe", "grant", "award", "new funding", "funded 2025", "funded 2026", "funded 2024"]
    )
    if has_recent_grant or "hiring" in note_low or "open position" in note_low:
        return {
            "hiring_badge": "🔥 High Hiring Likelihood (Recent Grant)",
            "level": "High",
            "reason": "Active/Recent NSF, NIH, DARPA, or Federal Grant signal noted.",
        }
    return {
        "hiring_badge": "⚡ Normal Hiring Pool",
        "level": "Standard",
        "reason": "Verify recent grants on NSF Award Search / NIH RePORTER / Personal Homepage.",
    }


def build_pi_peer_review_urls(prof_name: str, university: str = "") -> dict[str, str]:
    """Generates 1-click peer review & advisor reputation search URLs."""
    p_q = prof_name.replace(" ", "+")
    u_q = university.replace(" ", "+")
    combined = f"{p_q}+{u_q}" if u_q else p_q

    return {
        "ratemyprofessors": f"https://www.ratemyprofessors.com/search/professors?q={p_q}",
        "reddit_peer_review": f"https://www.google.com/search?q=site%3Areddit.com%2Fr%2FGradAdmissions+OR+site%3Areddit.com%2Fr%2FAcademia+{combined}+advisor",
        "rateyourpi": f"https://www.google.com/search?q=site%3Arateyourpi.com+OR+site%3Api-review.com+{combined}",
        "lab_alumni_placements": f"https://www.google.com/search?q={combined}+lab+alumni+phd+graduates+placements",
    }


def evaluate_pi_mentorship_flags(prof_name: str, note_text: str = "") -> dict[str, Any]:
    """Evaluates mentorship safety, green flags, and red flags from notes/peer feedback."""
    note_low = note_text.lower()

    red_keywords = ["toxic", "micromanage", "abusive", "dropout", "7 years", "delay", "overtime", "non-compete", "red flag", "avoid"]
    green_keywords = ["supportive", "great mentor", "4 years", "5 years", "graduated", "alumni", "tenure track", "student first author", "green flag", "recommend"]

    red_matches = [kw for kw in red_keywords if kw in note_low]
    green_matches = [kw for kw in green_keywords if kw in note_low]

    if red_matches:
        status_badge = "🚩 Red Flag Alert (Peer Review Warning)"
        safety = "Caution"
    elif green_matches:
        status_badge = "🟩 Highly Recommended Mentor"
        safety = "Safe"
    else:
        status_badge = "⚪ Mentorship Unchecked (Run Peer Review)"
        safety = "Unverified"

    return {
        "badge": status_badge,
        "safety": safety,
        "red_flags": red_matches,
        "green_flags": green_matches,
    }
