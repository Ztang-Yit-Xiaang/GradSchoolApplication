from __future__ import annotations

import re
from typing import Any

from gradpath.profile_import import COURSE_KEYWORDS, extract_text_from_upload

COURSE_CODE_HINTS = {
    "Programming": ["intro computing", "programming", "python", "java", "software"],
    "Data Structures": ["data structure"],
    "Algorithms": ["algorithm"],
    "Linear Algebra": ["linear algebra", "matrix"],
    "Probability/Statistics": ["probability", "statistics", "regression", "inference"],
    "Optimization": ["optimization", "operations research", "linear programming"],
    "Databases": ["database", "sql"],
    "Machine Learning": ["machine learning", "artificial intelligence"],
    "Deep Learning": ["deep learning", "neural"],
    "Natural Language Processing": ["natural language", "nlp"],
    "Numerical Analysis": ["numerical analysis", "scientific computing"],
    "Regression": ["regression"],
    "Software Design": ["software design", "object oriented"],
    "Operating Systems": ["operating system"],
}


def transcript_from_upload(file_name: str, content: bytes) -> tuple[dict[str, Any], list[str]]:
    text = extract_text_from_upload(file_name, content)
    return transcript_from_text(text)


def transcript_from_text(text: str) -> tuple[dict[str, Any], list[str]]:
    normalized = _normalize(text)
    coursework = _coursework_from_text(normalized)
    gpa = _extract_transcript_gpa(text)
    draft = {
        "gpa": gpa,
        "coursework": coursework,
        "raw_course_mentions": _course_mentions(text),
        "coverage": _coverage_notes(coursework),
    }
    notes = [
        f"Detected {len(coursework)} coursework categories from transcript text.",
        "Transcript extraction is approximate; review course names before applying.",
    ]
    if gpa is not None:
        notes.insert(0, f"Detected transcript GPA around {gpa}.")
    return draft, notes


def transcript_review_rows(draft: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {"Field": "GPA", "Extracted value": str(draft.get("gpa") or "Needs Review")},
        {"Field": "Coursework", "Extracted value": ", ".join(draft.get("coursework", []))},
        {"Field": "Coverage notes", "Extracted value": "; ".join(draft.get("coverage", []))},
        {
            "Field": "Course mentions",
            "Extracted value": "; ".join(draft.get("raw_course_mentions", [])[:12]),
        },
    ]


def apply_transcript_to_profile(
    profile: dict[str, Any], draft: dict[str, Any]
) -> dict[str, Any]:
    updated = dict(profile)
    courses = list(dict.fromkeys([*profile.get("coursework", []), *draft.get("coursework", [])]))
    updated["coursework"] = courses
    if draft.get("gpa") is not None:
        updated["gpa"] = draft["gpa"]
    return updated


def _coursework_from_text(text: str) -> list[str]:
    matches = []
    combined = {**COURSE_KEYWORDS, **COURSE_CODE_HINTS}
    for label, keywords in combined.items():
        if label in matches:
            continue
        if any(keyword.lower() in text for keyword in keywords):
            matches.append(label)
    return matches


def _extract_transcript_gpa(text: str) -> float | None:
    patterns = [
        r"(?:cumulative|overall|total)?\s*gpa\s*[:\-]?\s*([0-4](?:\.\d{1,3})?)",
        r"grade point average\s*[:\-]?\s*([0-4](?:\.\d{1,3})?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return min(round(float(match.group(1)), 2), 4.0)
    return None


def _course_mentions(text: str) -> list[str]:
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    candidates = []
    for line in lines:
        lowered = line.lower()
        if any(keyword in lowered for values in COURSE_CODE_HINTS.values() for keyword in values):
            candidates.append(line[:140])
    return candidates[:20]


def _coverage_notes(coursework: list[str]) -> list[str]:
    expected = [
        "Programming",
        "Data Structures",
        "Algorithms",
        "Linear Algebra",
        "Probability/Statistics",
        "Optimization",
        "Machine Learning",
    ]
    missing = [course for course in expected if course not in coursework]
    if not missing:
        return ["Core quantitative CS/DS prerequisites appear covered."]
    return [f"Review evidence for: {', '.join(missing)}."]


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()
