from __future__ import annotations

import re
from typing import Any

from gradpath.data import default_profile

COURSE_KEYWORDS = {
    "Programming": ["python", "java", "c++", "programming", "software"],
    "Data Structures": ["data structures", "linked list", "tree", "graph"],
    "Algorithms": ["algorithm", "algorithms"],
    "Linear Algebra": ["linear algebra", "matrix", "matrices"],
    "Probability/Statistics": ["probability", "statistics", "statistical", "inference"],
    "Optimization": ["optimization", "operations research", "linear programming"],
    "Databases": ["database", "sql", "data warehouse"],
    "Machine Learning": ["machine learning", "deep learning", "pytorch", "tensorflow"],
    "Deep Learning": ["deep learning", "neural network", "neural networks"],
    "Natural Language Processing": ["natural language processing", "nlp"],
    "Numerical Analysis": ["numerical analysis", "numerical linear algebra"],
    "Regression": ["regression", "least-squares", "least squares"],
    "Software Design": ["software design", "object-oriented", "docker"],
    "Operating Systems": ["operating system", "systems programming"],
}

FIELD_KEYWORDS = {
    "Computer Science": ["computer science", "software", "algorithm", "systems"],
    "Data Science": ["data science", "machine learning", "analytics", "data mining"],
    "Operations Research": ["operations research", "optimization", "decision science"],
    "Applied Math": ["applied math", "mathematical modeling", "stochastic"],
    "Statistics": ["statistics", "statistical", "probability"],
}

EXPERIENCE_KEYWORDS = {
    "Research": ["research assistant", "research", "lab", "thesis"],
    "Internship": ["intern", "internship"],
    "Projects": ["project", "github", "portfolio"],
    "Publication": ["publication", "paper", "poster", "conference"],
    "Teaching/TA": ["teaching assistant", "ta ", "tutor"],
    "Leadership": ["president", "leader", "leadership", "captain"],
}

INTEREST_KEYWORDS = [
    "machine learning",
    "data mining",
    "optimization",
    "statistics",
    "operations research",
    "natural language processing",
    "computer vision",
    "databases",
    "systems",
    "applied mathematics",
    "deep learning",
    "scientific computing",
    "randomized numerical linear algebra",
    "sequential decision making",
    "learning-augmented decision systems",
    "predictive modeling",
]


def extract_text_from_upload(file_name: str, content: bytes) -> str:
    suffix = file_name.lower().rsplit(".", maxsplit=1)[-1]
    if suffix == "txt":
        return content.decode("utf-8", errors="ignore")
    if suffix == "tex":
        return clean_latex_text(content.decode("utf-8", errors="ignore"))
    if suffix == "pdf":
        return _extract_pdf_text(content)
    raise ValueError("Only PDF, TXT, and TEX files are supported.")


def clean_latex_text(text: str) -> str:
    text = re.sub(r"%.*", "", text)
    text = re.sub(r"\\href\{([^{}]*)\}\{([^{}]*)\}", r"\2 \1", text)
    text = re.sub(r"\\entryrow\{([^{}]*)\}\{([^{}]*)\}", r"\1 \2", text)
    text = re.sub(r"\\entrysub\{([^{}]*)\}", r"\1", text)
    text = re.sub(r"\\CVSECTION\{([^{}]*)\}", r"\n\1\n", text)
    text = re.sub(r"\\(?:textbf|textit|textsc|emph)\{([^{}]*)\}", r"\1", text)
    text = re.sub(r"\\(?:name|address|phone|email|social)(?:\[[^\]]*\])?\{([^{}]*)\}", r"\1", text)
    text = re.sub(r"\\(?:begin|end)\{[^{}]*\}", " ", text)
    text = re.sub(r"\\[a-zA-Z]+(?:\[[^\]]*\])?", " ", text)
    text = text.replace("\\&", "&").replace("--", "-")
    text = re.sub(r"[{}$]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def profile_from_text(text: str, base_profile: dict[str, Any] | None = None) -> dict[str, Any]:
    profile = dict(base_profile or default_profile())
    normalized = _normalize_text(text)
    profile["gpa"] = _extract_gpa(text, profile["gpa"])
    english_test, english_score = _extract_english(text)
    if english_test and english_score:
        profile["english_test"] = english_test
        profile["english_score"] = english_score
    gre_quant = _extract_gre_quant(text)
    if gre_quant:
        profile["gre_status"] = "Completed"
        profile["gre_quant"] = gre_quant

    profile["coursework"] = _keyword_matches(normalized, COURSE_KEYWORDS) or profile["coursework"]
    profile["experience"] = (
        _keyword_matches(normalized, EXPERIENCE_KEYWORDS) or profile["experience"]
    )
    fields = _keyword_matches(normalized, FIELD_KEYWORDS)
    if fields:
        profile["target_fields"] = fields
    interests = [keyword for keyword in INTEREST_KEYWORDS if keyword in normalized]
    if interests:
        profile["research_interests"] = interests[:6]
    profile["career_goal"] = _infer_career_goal(normalized, profile["career_goal"])
    profile["sop_notes"] = _build_sop_notes(profile)
    return profile


def profile_review_rows(profile: dict[str, Any]) -> list[dict[str, str]]:
    rows = []
    for key, value in profile.items():
        if isinstance(value, list):
            display = ", ".join(str(item) for item in value)
        else:
            display = str(value)
        rows.append({"Field": key, "Extracted value": display})
    return rows


def _extract_pdf_text(content: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("Install pypdf to import PDF resumes.") from exc

    import io

    reader = PdfReader(io.BytesIO(content))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def _extract_gpa(text: str, fallback: float) -> float:
    patterns = [
        r"gpa\s*[:\-]?\s*([0-4](?:\.\d{1,2})?)\s*/\s*4(?:\.0)?",
        r"gpa\s*[:\-]?\s*([0-4](?:\.\d{1,2})?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return min(float(match.group(1)), 4.0)
    return fallback


def _extract_english(text: str) -> tuple[str | None, int | None]:
    patterns = [
        ("TOEFL", r"toefl(?:\s*ibt)?\s*[:\-]?\s*(\d{2,3})"),
        ("IELTS", r"ielts\s*[:\-]?\s*(\d(?:\.\d)?)"),
        ("Duolingo", r"duolingo\s*[:\-]?\s*(\d{2,3})"),
    ]
    for label, pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            score = float(match.group(1))
            return label, int(score)
    return None, None


def _extract_gre_quant(text: str) -> int | None:
    patterns = [
        r"gre\s*(?:quant|q|quantitative)\s*[:\-]?\s*(1[3-7]\d)",
        r"quantitative\s*[:\-]?\s*(1[3-7]\d)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def _keyword_matches(text: str, keyword_map: dict[str, list[str]]) -> list[str]:
    return [
        label
        for label, keywords in keyword_map.items()
        if any(keyword.lower() in text for keyword in keywords)
    ]


def _infer_career_goal(text: str, fallback: str) -> str:
    if "phd" in text or "research" in text:
        return "Research-oriented quantitative graduate study with applied project experience"
    if "data scientist" in text or "machine learning engineer" in text:
        return "Data science or machine learning career after graduate study"
    return fallback


def _build_sop_notes(profile: dict[str, Any]) -> str:
    interests = ", ".join(profile.get("research_interests", [])[:3])
    experience = ", ".join(profile.get("experience", [])[:3])
    if interests:
        return (
            f"Use CV evidence around {experience or 'projects'} "
            f"to support interest in {interests}."
        )
    return profile.get("sop_notes", "")
