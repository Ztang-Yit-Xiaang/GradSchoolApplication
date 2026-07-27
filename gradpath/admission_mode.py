"""Evidence-backed admission mode classifier and conflict detector."""

from __future__ import annotations

from typing import Any

from gradpath.schemas import AdmissionModeModel, now_utc_iso


def classify_admission_mode(
    page_text: str,
    degree: str = "PhD",
    source_url: str = "",
    page_title: str = "",
) -> AdmissionModeModel:
    """Deterministically extracts admission mode taxonomy and evidence from official text."""
    text_low = page_text.lower()
    retrieval_date = now_utc_iso()

    direct_pi_keywords = [
        "must secure a faculty sponsor",
        "advisor agreement required prior to admission",
        "pi-funded position",
        "direct lab admission",
        "accepted into a specific lab",
        "must have a willing advisor before apply",
        "sponsored directly by a professor",
    ]

    rotation_keywords = [
        "lab rotations",
        "rotate through labs",
        "first-year rotations",
        "umbrella program",
    ]

    committee_keywords = [
        "admissions committee reviews all applications",
        "departmental fellowship",
        "advisors are assigned after",
        "centralized admissions committee",
        "committee evaluates all candidates",
    ]

    hybrid_keywords = [
        "faculty interest is strongly considered",
        "encouraged to contact faculty",
        "faculty match during review",
        "list potential advisors",
    ]

    thesis_ms_keywords = [
        "thesis required",
        "master of science with thesis",
        "research-based master",
        "thesis option",
    ]

    coursework_ms_keywords = [
        "coursework-only",
        "non-thesis",
        "professional master",
        "tuition-based",
        "master of engineering",
    ]

    direct_matches = [kw for kw in direct_pi_keywords if kw in text_low]
    rotation_matches = [kw for kw in rotation_keywords if kw in text_low]
    committee_matches = [kw for kw in committee_keywords if kw in text_low]
    hybrid_matches = [kw for kw in hybrid_keywords if kw in text_low]
    thesis_matches = [kw for kw in thesis_ms_keywords if kw in text_low]
    coursework_matches = [kw for kw in coursework_ms_keywords if kw in text_low]

    mode = "unknown_needs_review"
    confidence = "Low"
    excerpt = ""
    contact_policy = "unknown"
    advisor_binding = "unknown"
    funding_owner = "unknown"

    if degree.upper() in ["MS", "MASTER", "MSC", "MENG"]:
        if thesis_matches and coursework_matches:
            mode = "unknown_needs_review"
            confidence = "Low"
            excerpt = f"Conflicting MS signals found: Thesis ({thesis_matches}) vs Coursework ({coursework_matches})"
        elif thesis_matches:
            mode = "research_thesis_ms"
            confidence = "High"
            excerpt = f"Research Thesis MS: matched '{thesis_matches[0]}'"
            funding_owner = "mixed"
        elif coursework_matches:
            mode = "coursework_professional_ms"
            confidence = "High"
            excerpt = f"Coursework MS: matched '{coursework_matches[0]}'"
            funding_owner = "self_funded"
        else:
            mode = "research_thesis_ms" if "thesis" in text_low else "coursework_professional_ms"
            confidence = "Medium"
            excerpt = "MS program mode inferred from general program description."

    else:  # PhD
        if direct_matches:
            mode = "direct_pi_sponsor"
            confidence = "High"
            excerpt = f"Direct PI Sponsorship: matched '{direct_matches[0]}'"
            contact_policy = "required"
            advisor_binding = "before_application"
            funding_owner = "pi"
        elif rotation_matches:
            mode = "rotation_or_umbrella"
            confidence = "High"
            excerpt = f"Rotation Program: matched '{rotation_matches[0]}'"
            contact_policy = "optional"
            advisor_binding = "after_rotations"
            funding_owner = "program"
        elif hybrid_matches and committee_matches:
            mode = "hybrid_committee_faculty"
            confidence = "High"
            excerpt = f"Hybrid Committee + Faculty: matched committee ({committee_matches[0]}) & hybrid ({hybrid_matches[0]})"
            contact_policy = "recommended"
            advisor_binding = "at_admission"
            funding_owner = "mixed"
        elif hybrid_matches:
            mode = "hybrid_committee_faculty"
            confidence = "Medium"
            excerpt = f"Hybrid Mode: matched '{hybrid_matches[0]}'"
            contact_policy = "recommended"
            advisor_binding = "at_admission"
            funding_owner = "mixed"
        elif committee_matches:
            mode = "committee_program"
            confidence = "High"
            excerpt = f"Committee Admissions: matched '{committee_matches[0]}'"
            contact_policy = "optional"
            advisor_binding = "after_admission"
            funding_owner = "program"
        elif "advisor" in text_low and not any(
            [direct_matches, rotation_matches, committee_matches, hybrid_matches]
        ):
            mode = "unknown_needs_review"
            confidence = "Low"
            excerpt = "Word 'advisor' present without explicit sponsorship or committee policy language. Contact graduate coordinator."
        else:
            mode = "unknown_needs_review"
            confidence = "Low"
            excerpt = "No clear admission mode signals extracted. Manual review required."

    return AdmissionModeModel(
        application_mode=mode,
        mode_evidence=excerpt,
        mode_source_url=source_url,
        mode_confidence=confidence,
        contact_policy=contact_policy,
        advisor_binding=advisor_binding,
        funding_owner=funding_owner,
        recruiting_last_checked=retrieval_date,
    )


def detect_evidence_conflicts(evidence_items: list[dict[str, Any]]) -> list[str]:
    """Identifies contradictory claims across extracted official evidence items."""
    conflicts = []
    if not evidence_items:
        return conflicts

    deadlines = set()
    funding_claims = set()

    for item in evidence_items:
        excerpt = str(item.get("evidence_excerpt", "")).lower()
        if "deadline" in excerpt:
            deadlines.add(excerpt)
        if any(w in excerpt for w in ["fund", "stipend", "tuition", "cost"]):
            funding_claims.add(excerpt)

    if len(deadlines) > 1:
        conflicts.append(f"Multiple conflicting deadline statements detected: {list(deadlines)}")
    if "fully funded" in str(funding_claims) and "self-funded" in str(funding_claims):
        conflicts.append(
            "Contradictory funding claims detected (fully funded vs self-funded across pages)."
        )

    return conflicts
