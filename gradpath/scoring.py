from __future__ import annotations

from datetime import date, datetime
from typing import Any

COURSE_ALIASES = {
    "Probability": "Probability/Statistics",
    "Statistics": "Probability/Statistics",
    "Programming": "Programming",
    "Data Structures": "Data Structures",
    "Algorithms": "Algorithms",
    "Linear Algebra": "Linear Algebra",
    "Optimization": "Optimization",
    "Databases": "Databases",
    "Machine Learning": "Machine Learning",
}


def normalize_profile(profile: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(profile)
    normalized["target_fields"] = list(profile.get("target_fields", []))
    normalized["coursework"] = list(profile.get("coursework", []))
    normalized["experience"] = list(profile.get("experience", []))
    normalized["research_interests"] = [
        item.lower().strip() for item in profile.get("research_interests", []) if item
    ]
    return normalized


def deadline_days(deadline: str, today: date | None = None) -> int | None:
    if not deadline:
        return None
    today = today or date.today()
    try:
        parsed = datetime.strptime(deadline, "%Y-%m-%d").date()
    except ValueError:
        return None
    return (parsed - today).days


def fit_band(score: int) -> str:
    if score >= 82:
        return "Strong"
    if score >= 68:
        return "Good"
    if score >= 50:
        return "Needs Review"
    return "Risky"


def score_program(program: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    profile = normalize_profile(profile)
    degree = program["degree"]
    if degree == "PhD":
        score, strengths, missing, actions = _score_phd(program, profile)
    else:
        score, strengths, missing, actions = _score_ms(program, profile)

    return {
        "score": max(0, min(100, round(score))),
        "band": fit_band(round(score)),
        "strengths": strengths,
        "missing": missing,
        "actions": actions,
        "sop_angle": _sop_angle(program, profile),
    }


def _english_points(
    program: dict[str, Any], profile: dict[str, Any], weight: int
) -> tuple[int, str]:
    requirement = program["requirements"]["english"]
    score = profile.get("english_score") or 0
    minimum = requirement.get("minimum_score") or 0
    if not requirement.get("required"):
        return weight, "English waiver or not required"
    if score >= minimum:
        return weight, f"{profile.get('english_test')} {score} meets minimum {minimum}"
    if score >= minimum - 5:
        return round(weight * 0.55), f"English score is close to minimum {minimum}"
    return 0, f"English score below minimum {minimum}"


def _gre_points(program: dict[str, Any], profile: dict[str, Any], weight: int) -> tuple[int, str]:
    gre = program["requirements"]["gre"]
    status = profile.get("gre_status", "")
    quant = profile.get("gre_quant") or 0
    if gre["status"] in {"Not Required", "Optional"}:
        return weight, f"GRE {gre['status'].lower()}"
    if gre["status"] == "Recommended" and quant >= 160:
        return round(weight * 0.9), "GRE Quant is competitive for recommended GRE"
    if status == "Completed" and quant >= 160:
        return weight, "GRE requirement appears ready"
    if status in {"Planning", "Scheduled"}:
        return round(weight * 0.45), "GRE still needs completion"
    return 0, "GRE requirement may be unresolved"


def _coursework_points(
    program: dict[str, Any], profile: dict[str, Any], weight: int
) -> tuple[int, list[str], list[str]]:
    required = program["requirements"]["coursework"]
    taken = set(profile.get("coursework", []))
    normalized_required = [COURSE_ALIASES.get(course, course) for course in required]
    covered = [course for course in normalized_required if course in taken]
    missing = [course for course in normalized_required if course not in taken]
    ratio = len(covered) / max(len(normalized_required), 1)
    return round(weight * ratio), covered, missing


def _preference_points(
    program: dict[str, Any], profile: dict[str, Any], weight: int
) -> tuple[int, str]:
    preferred_regions = profile.get("preferred_regions", [])
    funding_need = profile.get("funding_need", "")
    region_match = not preferred_regions or program["country"] in preferred_regions
    funding_text = program["preferences"]["funding"].lower()
    funding_match = funding_need != "Critical" or any(
        word in funding_text for word in ["funded", "assistantship", "fellowship"]
    )
    points = 0
    if region_match:
        points += weight * 0.45
    if funding_match:
        points += weight * 0.35
    if profile.get("orientation", "").lower() in program["preferences"]["program"].lower():
        points += weight * 0.2
    return round(points), "Region/funding preferences partially or fully align"


def _experience_points(
    program: dict[str, Any], profile: dict[str, Any], weight: int
) -> tuple[int, list[str], list[str]]:
    preferred = program["preferences"]["experience"]
    applicant = set(profile.get("experience", []))
    matched = [item for item in preferred if item in applicant]
    missing = [item for item in preferred if item not in applicant]
    ratio = len(matched) / max(len(preferred), 1)
    return round(weight * ratio), matched, missing


def _research_points(
    program: dict[str, Any], profile: dict[str, Any], weight: int
) -> tuple[int, list[str]]:
    interests = profile.get("research_interests", [])
    faculty = " ".join(program.get("phd", {}).get("faculty_areas", [])).lower()
    matched = [interest for interest in interests if interest in faculty]
    ratio = min(len(matched) / 2, 1)
    return round(weight * ratio), matched


def _deadline_points(program: dict[str, Any], weight: int) -> tuple[int, str]:
    days = deadline_days(program["requirements"]["deadline"])
    if days is None:
        return round(weight * 0.35), "Deadline needs manual review"
    if days < 0:
        return 0, "Deadline has passed"
    if days <= 30:
        return round(weight * 0.45), "Deadline is soon"
    return weight, "Deadline window is workable"


def _score_ms(
    program: dict[str, Any], profile: dict[str, Any]
) -> tuple[int, list[str], list[str], list[str]]:
    strengths: list[str] = []
    missing: list[str] = []
    actions: list[str] = []
    score = 0

    english, english_note = _english_points(program, profile, 20)
    score += english
    (strengths if english == 20 else missing).append(english_note)

    gre, gre_note = _gre_points(program, profile, 12)
    score += gre
    (strengths if gre >= 10 else actions).append(gre_note)

    coursework, covered, missing_courses = _coursework_points(program, profile, 24)
    score += coursework
    if covered:
        strengths.append(f"Coursework match: {', '.join(covered)}")
    if missing_courses:
        missing.append(f"Missing coursework: {', '.join(missing_courses)}")
        actions.append("Plan transcript notes or bridge coursework for missing prerequisites.")

    deadline, deadline_note = _deadline_points(program, 14)
    score += deadline
    (strengths if deadline >= 10 else actions).append(deadline_note)

    preference, preference_note = _preference_points(program, profile, 14)
    score += preference
    strengths.append(preference_note)

    experience, matched_exp, missing_exp = _experience_points(program, profile, 16)
    score += experience
    if matched_exp:
        strengths.append(f"Experience match: {', '.join(matched_exp)}")
    if missing_exp:
        missing.append(f"Experience gap: {', '.join(missing_exp)}")

    return score, strengths, missing, actions


def _score_phd(
    program: dict[str, Any], profile: dict[str, Any]
) -> tuple[int, list[str], list[str], list[str]]:
    strengths: list[str] = []
    missing: list[str] = []
    actions: list[str] = []
    score = 0

    research, matches = _research_points(program, profile, 30)
    score += research
    if matches:
        strengths.append(f"Research fit: {', '.join(matches)}")
    else:
        missing.append("No clear faculty/research keyword match")
        actions.append("Identify 2-3 faculty and tune research interests before applying.")

    experience, matched_exp, missing_exp = _experience_points(program, profile, 18)
    score += experience
    if matched_exp:
        strengths.append(f"PhD experience match: {', '.join(matched_exp)}")
    if missing_exp:
        missing.append(f"PhD experience gap: {', '.join(missing_exp)}")

    coursework, covered, missing_courses = _coursework_points(program, profile, 14)
    score += coursework
    if covered:
        strengths.append(f"Coursework match: {', '.join(covered)}")
    if missing_courses:
        missing.append(f"Missing coursework: {', '.join(missing_courses)}")

    english, english_note = _english_points(program, profile, 10)
    score += english
    (strengths if english == 10 else missing).append(english_note)

    gre, gre_note = _gre_points(program, profile, 8)
    score += gre
    (strengths if gre >= 7 else actions).append(gre_note)

    funding_text = program["preferences"]["funding"].lower()
    if any(word in funding_text for word in ["funded", "assistantship", "fellowship"]):
        score += 10
        strengths.append("Funding language is visible")
    else:
        score += 4
        missing.append("Funding details need review")

    deadline, deadline_note = _deadline_points(program, 10)
    score += deadline
    (strengths if deadline >= 8 else actions).append(deadline_note)

    return score, strengths, missing, actions


def _sop_angle(program: dict[str, Any], profile: dict[str, Any]) -> str:
    interests = ", ".join(profile.get("research_interests", [])[:3]) or "quantitative preparation"
    if program["degree"] == "PhD":
        return (
            f"Frame {interests} around faculty fit, prior projects, "
            "and a focused research question."
        )
    return (
        f"Connect {interests}, technical coursework, and career goals "
        "to the program's applied strengths."
    )


PROGRAM_SCORE_WEIGHTS = {
    "research_ecosystem": 0.25,
    "advisor_resilience": 0.20,
    "funding_col": 0.20,
    "admission_mode": 0.15,
    "outcomes": 0.10,
    "personal_constraints": 0.10,
}

PI_SCORE_WEIGHTS = {
    "research_fit": 0.35,
    "mentoring": 0.20,
    "recent_strength": 0.15,
    "recruiting_confidence": 0.15,
    "outcomes": 0.10,
    "collaboration": 0.05,
}


def compute_program_score(program: dict[str, Any], profile: dict[str, Any]) -> float:
    """Computes program score using transparent 6-component weights."""
    eco = _research_points(program, profile, 100)[0]
    resilience = min(100.0, len(program.get("phd", {}).get("poi_list", [])) * 33.3)
    stipend = program.get("stipend_amount", 30000)
    col = program.get("col_index", 1.0)
    real_stipend = stipend / max(col, 0.5)
    funding_score = min(100.0, (real_stipend / 35000.0) * 100.0)

    mode = program.get("admission_mode", {}).get("application_mode", "unknown")
    mode_score = (
        90.0
        if mode in ["committee_program", "rotation_or_umbrella", "hybrid_committee_faculty"]
        else 70.0
    )

    outcomes = 80.0
    constraints = 85.0

    score = (
        eco * PROGRAM_SCORE_WEIGHTS["research_ecosystem"]
        + resilience * PROGRAM_SCORE_WEIGHTS["advisor_resilience"]
        + funding_score * PROGRAM_SCORE_WEIGHTS["funding_col"]
        + mode_score * PROGRAM_SCORE_WEIGHTS["admission_mode"]
        + outcomes * PROGRAM_SCORE_WEIGHTS["outcomes"]
        + constraints * PROGRAM_SCORE_WEIGHTS["personal_constraints"]
    )
    return round(score, 1)


def compute_pi_score(pi_data: dict[str, Any], profile: dict[str, Any]) -> float:
    """Computes PI score using transparent 6-component weights."""
    r_fit = float(pi_data.get("research_fit_score", 75.0))
    fb = pi_data.get("feedback", {})
    mentoring_5 = float(fb.get("score", 2.5)) if isinstance(fb, dict) else 2.5
    mentoring = (mentoring_5 / 5.0) * 100.0

    recent = 80.0 if pi_data.get("recent_grants") else 60.0
    recruiting = (
        90.0 if pi_data.get("recruiting_status") in ["recruiting", "High"] else 60.0
    )
    outcomes = 75.0
    collab = 75.0

    score = (
        r_fit * PI_SCORE_WEIGHTS["research_fit"]
        + mentoring * PI_SCORE_WEIGHTS["mentoring"]
        + recent * PI_SCORE_WEIGHTS["recent_strength"]
        + recruiting * PI_SCORE_WEIGHTS["recruiting_confidence"]
        + outcomes * PI_SCORE_WEIGHTS["outcomes"]
        + collab * PI_SCORE_WEIGHTS["collaboration"]
    )
    return round(score, 1)


def compute_joint_score(program_score: float, pi_score: float) -> float:
    """Combines program score and PI score into joint evaluation score."""
    return round(0.55 * program_score + 0.45 * pi_score, 1)


def check_portfolio_balance(programs: list[dict[str, Any]]) -> list[str]:
    """Generates portfolio distribution warnings and recommendations."""
    warnings = []
    counts: dict[str, int] = {}
    for p in programs:
        cat = p.get("portfolio_category", "Needs more evidence")
        counts[cat] = counts.get(cat, 0) + 1

    lottery = counts.get("Lottery", 0)
    core = counts.get("Core/Target", 0)
    lower_var = counts.get("Lower-variance high-fit", 0)

    if lottery > 2:
        warnings.append(
            f"⚠️ High Risk: You have {lottery} Lottery applications (recommended max: 2). High lottery ratio decreases funded PhD placement odds."
        )
    if core < 3:
        warnings.append(
            f"💡 Portfolio Warning: Core/Target programs ({core}) is below recommended target (5). Add more Core/Target programs."
        )
    if lower_var < 2:
        warnings.append(
            f"💡 Portfolio Warning: Lower-variance high-fit programs ({lower_var}) is low (recommended: 3)."
        )

    return warnings
