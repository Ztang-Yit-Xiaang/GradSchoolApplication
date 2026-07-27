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
        "english_score": 98,
        "gre_status": "Completed",
        "gre_quant": 168,
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
            "optimization",
            "RandNLA",
            "randomized numerical linear algebra",
            "scientific computing",
            "decision systems",
            "transportation",
            "urban systems",
            "ML systems",
            "sensing/inverse modeling",
        ],
        "primary_tags": [
            "optimization",
            "RandNLA",
            "scientific computing",
            "decision systems",
        ],
        "secondary_tags": [
            "transportation",
            "urban systems",
            "ML systems",
            "sensing/inverse modeling",
        ],
        "evidence": {
            "projects": [
                "OSQP/Torch optimization work with Ju Sun",
                "RandNLA UROP with Swati Padmanabhan",
                "Travel-itinerary predictive optimization with Prof. Choi",
                "Sensing/inverse modeling with Prof. Hongliang Ren",
            ],
            "papers": [
                "Travel-itinerary paper may target TRB/CHI with Choi; label only as "
                "in-prep, submitted, or accepted when true.",
                "OSQP/Torch and RandNLA papers may help only if their application-time "
                "status is accurate.",
            ],
            "teaching": [
                "UMN undergraduate TA experience in CSCI 2081",
            ],
        },
        "test_strategy": {
            "gre": (
                "Probably no retake. Current GRE: 150V + 168Q + 3.5 AWA. "
                "Submit only where optional and helpful, especially quant-heavy OR/IE, "
                "applied math, and MS programs."
            ),
            "english": (
                "Fall 2023 TOEFL 98 likely expires for official reporting by Fall 2027. "
                "Check whether a U.S. bachelor's degree waives admission English proficiency."
            ),
            "ta": (
                "Prior TOEFL Speaking 23/30 plus UMN undergraduate TA experience supports "
                "teaching readiness, but graduate TA/oral rules must be checked by school."
            ),
        },
        "recommenders": {
            "Ju": "Optimization, OSQP/Torch, scalable computation, and local PhD fit.",
            "Swati": "RandNLA, randomized algorithms, and scientific computing.",
            "Choi": "Transportation, urban systems, decision systems, and itinerary paper.",
            "Ren": "Sensing, inverse modeling, and signal-processing angle.",
        },
        "preferred_regions": ["United States"],
        "funding_need": "Critical",
        "orientation": "Research + career",
        "career_goal": (
            "PhD-first search around optimization and scalable computation for decision systems, "
            "with MS/job backups only where employability value is clear."
        ),
        "sop_notes": (
            "Prestige is not the first filter. Prioritize departments that can clearly understand "
            "and sponsor optimization + scalable computation for decision systems."
        ),
    }
