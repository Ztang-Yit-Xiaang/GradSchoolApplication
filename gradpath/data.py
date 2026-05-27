from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "programs.json"


def load_programs(path: Path = DATA_PATH) -> list[dict[str, Any]]:
    """Load seeded graduate program records."""
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("Program data must be a list of records.")
    return data


def default_profile() -> dict[str, Any]:
    """Return Yixin's CV-derived default graduate applicant profile."""
    return {
        "target_degree": "Both",
        "target_fields": [
            "Data Science",
            "Computer Science",
            "Applied Math",
            "Statistics",
            "Operations Research",
        ],
        "gpa": 4.0,
        "english_test": "TOEFL",
        "english_score": 102,
        "gre_status": "Planning",
        "gre_quant": 165,
        "coursework": [
            "Programming",
            "Algorithms",
            "Linear Algebra",
            "Probability/Statistics",
            "Optimization",
            "Machine Learning",
            "Deep Learning",
            "Natural Language Processing",
            "Numerical Analysis",
            "Software Design",
        ],
        "experience": [
            "Research",
            "Projects",
            "Publication",
            "Internship",
            "Teaching/TA",
            "Leadership",
        ],
        "research_interests": [
            "machine learning",
            "optimization",
            "scientific computing",
            "randomized numerical linear algebra",
            "sequential decision making",
            "learning-augmented decision systems",
            "predictive modeling",
        ],
        "preferred_regions": ["United States"],
        "funding_need": "Critical",
        "orientation": "Research + career",
        "career_goal": (
            "Research-oriented MS/PhD preparation in machine learning, optimization, "
            "scientific computing, and data-driven decision systems."
        ),
        "sop_notes": (
            "Emphasize research maturity, cross-disciplinary quantitative training, "
            "publications, optimization/ML projects, randomized numerical linear algebra, "
            "and faculty fit for research-intensive programs."
        ),
    }
