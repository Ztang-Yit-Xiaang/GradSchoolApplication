from __future__ import annotations

import json
import os
from typing import Any

PROFILE_SCHEMA = {
    "type": "object",
    "properties": {
        "target_degree": {"type": "string"},
        "target_fields": {"type": "array", "items": {"type": "string"}},
        "gpa": {"type": "number"},
        "english_test": {"type": "string"},
        "english_score": {"type": "integer"},
        "gre_status": {"type": "string"},
        "gre_quant": {"type": "integer"},
        "coursework": {"type": "array", "items": {"type": "string"}},
        "experience": {"type": "array", "items": {"type": "string"}},
        "research_interests": {"type": "array", "items": {"type": "string"}},
        "preferred_regions": {"type": "array", "items": {"type": "string"}},
        "funding_need": {"type": "string"},
        "orientation": {"type": "string"},
        "career_goal": {"type": "string"},
        "sop_notes": {"type": "string"},
    },
    "required": [
        "target_degree",
        "target_fields",
        "gpa",
        "english_test",
        "english_score",
        "gre_status",
        "gre_quant",
        "coursework",
        "experience",
        "research_interests",
        "preferred_regions",
        "funding_need",
        "orientation",
        "career_goal",
        "sop_notes",
    ],
    "additionalProperties": False,
}

PROGRAM_SCHEMA = {
    "type": "object",
    "properties": {
        "school": {"type": "string"},
        "program": {"type": "string"},
        "degree": {"type": "string"},
        "field": {"type": "string"},
        "location": {"type": "string"},
        "country": {"type": "string"},
        "deadline": {"type": "string"},
        "english_summary": {"type": "string"},
        "english_minimum": {"type": "integer"},
        "gre_status": {"type": "string"},
        "gre_summary": {"type": "string"},
        "coursework": {"type": "array", "items": {"type": "string"}},
        "program_preference": {"type": "string"},
        "sop": {"type": "string"},
        "experience": {"type": "array", "items": {"type": "string"}},
        "funding": {"type": "string"},
        "research_fit": {"type": "string"},
        "faculty_areas": {"type": "array", "items": {"type": "string"}},
        "evidence": {"type": "string"},
    },
    "required": [
        "school",
        "program",
        "degree",
        "field",
        "location",
        "country",
        "deadline",
        "english_summary",
        "english_minimum",
        "gre_status",
        "gre_summary",
        "coursework",
        "program_preference",
        "sop",
        "experience",
        "funding",
        "research_fit",
        "faculty_areas",
        "evidence",
    ],
    "additionalProperties": False,
}

QUERY_PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "queries": {"type": "array", "items": {"type": "string"}},
        "strategy": {"type": "string"},
    },
    "required": ["queries", "strategy"],
    "additionalProperties": False,
}

ADMIT_REASONING_SCHEMA = {
    "type": "object",
    "properties": {
        "band": {"type": "string"},
        "score": {"type": "integer"},
        "why": {"type": "string"},
        "strengths": {"type": "array", "items": {"type": "string"}},
        "risks": {"type": "array", "items": {"type": "string"}},
        "next_steps": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["band", "score", "why", "strengths", "risks", "next_steps"],
    "additionalProperties": False,
}

COMMUNITY_EVIDENCE_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "publication_expectation": {"type": "string"},
        "research_expectation": {"type": "string"},
        "risk_note": {"type": "string"},
    },
    "required": ["summary", "publication_expectation", "research_expectation", "risk_note"],
    "additionalProperties": False,
}

TRANSCRIPT_SCHEMA = {
    "type": "object",
    "properties": {
        "coursework": {"type": "array", "items": {"type": "string"}},
        "gpa": {"type": "number"},
        "notes": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["coursework", "gpa", "notes"],
    "additionalProperties": False,
}

FIT_PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "missing_requirements": {"type": "array", "items": {"type": "string"}},
        "recommended_coursework": {"type": "array", "items": {"type": "string"}},
        "research_actions": {"type": "array", "items": {"type": "string"}},
        "publication_project_positioning": {"type": "string"},
        "sop_angle": {"type": "string"},
        "faculty_contact": {"type": "string"},
    },
    "required": [
        "missing_requirements",
        "recommended_coursework",
        "research_actions",
        "publication_project_positioning",
        "sop_angle",
        "faculty_contact",
    ],
    "additionalProperties": False,
}

ADMIT_BANDS = {"Likely-ish", "Target", "Reach", "High Reach", "Needs More Evidence"}
DEFAULT_OPENAI_MODEL = "gpt-5.4-mini"


def openai_available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def test_openai_connection() -> dict[str, Any]:
    model = os.getenv("GRADPATH_OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
    if not openai_available():
        return {
            "available": False,
            "ok": False,
            "model": model,
            "message": "OPENAI_API_KEY is not set in this app process.",
        }
    try:
        from openai import OpenAI
    except ImportError:
        return {
            "available": True,
            "ok": False,
            "model": model,
            "message": "The openai package is not installed in this environment.",
        }

    try:
        client = OpenAI()
        response = client.responses.create(
            model=model,
            input="Reply with exactly: GradPath API check OK",
            max_output_tokens=16,
        )
        text = getattr(response, "output_text", "").strip()
    except Exception as exc:
        return {
            "available": True,
            "ok": False,
            "model": model,
            "message": f"OpenAI API call failed: {exc}",
        }

    if "GradPath API check OK" in text:
        message = "OpenAI API call succeeded."
    else:
        message = f"OpenAI API call returned an unexpected response: {text or 'empty output'}"
    return {
        "available": True,
        "ok": "GradPath API check OK" in text,
        "model": model,
        "message": message,
    }


def extract_profile_with_ai(text: str, rule_profile: dict[str, Any]) -> tuple[dict[str, Any], str]:
    prompt = (
        "Extract a graduate applicant profile from this CV/resume text. "
        "Use the provided rule-based profile as a starting point. "
        "Return only fields in the schema. Keep unknown values conservative.\n\n"
        f"Rule profile:\n{json.dumps(rule_profile)}\n\nCV text:\n{text[:12000]}"
    )
    data = _structured_response(prompt, PROFILE_SCHEMA, "gradpath_profile")
    if not data:
        return rule_profile, "AI extraction unavailable; used rule-based profile only."
    merged = dict(rule_profile)
    merged.update({key: value for key, value in data.items() if value not in (None, "", [])})
    return merged, "AI extraction applied; review before using for applications."


def extract_program_with_ai(
    text: str, rule_program: dict[str, Any], source_url: str
) -> tuple[dict[str, Any], str]:
    prompt = (
        "Extract graduate program admissions requirements from official page text. "
        "Return conservative values, preserve uncertainty in summaries, and do not invent facts. "
        "Use this rule-based draft as a starting point.\n\n"
        f"Source URL: {source_url}\nDraft:\n{json.dumps(rule_program)}\n\n"
        f"Page text:\n{text[:16000]}"
    )
    data = _structured_response(prompt, PROGRAM_SCHEMA, "gradpath_program")
    if not data:
        return rule_program, "AI extraction unavailable; used rule-based program extraction only."

    program = dict(rule_program)
    program["school"] = data["school"] or program["school"]
    program["program"] = data["program"] or program["program"]
    program["degree"] = data["degree"] if data["degree"] in {"MS", "PhD"} else program["degree"]
    program["field"] = data["field"] or program["field"]
    program["location"] = data["location"] or program["location"]
    program["country"] = data["country"] or program["country"]
    program["requirements"]["deadline"] = data["deadline"] or program["requirements"]["deadline"]
    program["requirements"]["english"]["summary"] = data["english_summary"]
    program["requirements"]["english"]["minimum_score"] = data["english_minimum"]
    program["requirements"]["gre"]["status"] = data["gre_status"] or "Needs Review"
    program["requirements"]["gre"]["summary"] = data["gre_summary"]
    program["requirements"]["coursework"] = (
        data["coursework"] or program["requirements"]["coursework"]
    )
    program["preferences"]["program"] = data["program_preference"]
    program["preferences"]["sop"] = data["sop"]
    program["preferences"]["experience"] = (
        data["experience"] or program["preferences"]["experience"]
    )
    program["preferences"]["funding"] = data["funding"]
    program["phd"]["research_fit"] = data["research_fit"]
    program["phd"]["faculty_areas"] = data["faculty_areas"]
    program["source"]["confidence"] = "AI/Needs Review"
    return program, "AI extraction applied; verify fields against official page."


def plan_search_queries_with_ai(
    profile: dict[str, Any],
    context: dict[str, Any],
    fallback_queries: list[str],
) -> tuple[list[str], str]:
    prompt = (
        "Plan official-web search queries for graduate admissions research. "
        "Use the applicant profile and search context to produce targeted queries. "
        "Prefer official university pages, program admissions pages, requirements pages, "
        "TOEFL/GRE pages, funding pages, and PhD faculty/research pages. "
        "Do not invent schools; write search queries only.\n\n"
        f"Profile:\n{json.dumps(profile)}\n\nContext:\n{json.dumps(context)}\n\n"
        f"Fallback query examples:\n{json.dumps(fallback_queries)}"
    )
    data = _structured_response(prompt, QUERY_PLAN_SCHEMA, "gradpath_query_plan")
    if not data:
        return fallback_queries, "AI query planning unavailable; used deterministic queries."
    queries = [
        str(query).strip()
        for query in data.get("queries", [])
        if str(query).strip()
    ]
    if not queries:
        return (
            fallback_queries,
            "AI query planning returned no queries; used deterministic queries.",
        )
    return queries[:8], f"AI query planning applied: {data.get('strategy', 'targeted search')}"


def reason_admit_confidence_with_ai(
    profile: dict[str, Any],
    program: dict[str, Any],
    rule_reasoning: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    prompt = (
        "Estimate graduate admissions planning confidence using only the provided applicant "
        "profile, extracted official-source program record, and deterministic fit reasoning. "
        "This is not a guarantee of admission. Keep claims conservative. "
        "Use one band exactly: Likely-ish, Target, Reach, High Reach, Needs More Evidence.\n\n"
        f"Applicant profile:\n{json.dumps(profile)}\n\n"
        f"Program record:\n{json.dumps(program)}\n\n"
        f"Rule reasoning:\n{json.dumps(rule_reasoning)}"
    )
    data = _structured_response(prompt, ADMIT_REASONING_SCHEMA, "gradpath_admit_reasoning")
    if not data:
        return rule_reasoning, "AI admit-confidence reasoning unavailable; used rule reasoning."
    band = data.get("band") if data.get("band") in ADMIT_BANDS else rule_reasoning["band"]
    score = data.get("score")
    if not isinstance(score, int):
        score = rule_reasoning["score"]
    reasoning = {
        "band": band,
        "score": max(0, min(100, score)),
        "why": data.get("why") or rule_reasoning["why"],
        "strengths": data.get("strengths") or rule_reasoning["strengths"],
        "risks": data.get("risks") or rule_reasoning["risks"],
        "next_steps": data.get("next_steps") or rule_reasoning["next_steps"],
    }
    return reasoning, "AI admit-confidence reasoning applied; treat as planning guidance."


def summarize_community_evidence_with_ai(
    program: dict[str, Any], evidence: list[dict[str, str]]
) -> tuple[dict[str, str], str]:
    prompt = (
        "Summarize unofficial public community evidence for graduate admissions planning. "
        "Never treat forum posts as official requirements. Focus on whether applicants report "
        "publications, research experience, faculty contact, or hidden preferences.\n\n"
        f"Program:\n{json.dumps(program)}\n\nEvidence:\n{json.dumps(evidence)}"
    )
    data = _structured_response(prompt, COMMUNITY_EVIDENCE_SCHEMA, "gradpath_community")
    if not data:
        return (
            {
                "summary": "Community evidence needs manual review.",
                "publication_expectation": "No reliable unofficial publication signal yet.",
                "research_expectation": "No reliable unofficial research signal yet.",
                "risk_note": "Unofficial sources are advisory only.",
            },
            "AI community synthesis unavailable; kept raw community evidence.",
        )
    return data, "AI community evidence synthesis applied; verify manually."


def normalize_transcript_with_ai(
    text: str, rule_draft: dict[str, Any], allowed_courses: list[str]
) -> tuple[dict[str, Any], str]:
    prompt = (
        "Normalize transcript text into graduate-school prerequisite categories. "
        "Use only allowed coursework labels and keep uncertainty in notes.\n\n"
        f"Allowed coursework labels:\n{json.dumps(allowed_courses)}\n\n"
        f"Rule draft:\n{json.dumps(rule_draft)}\n\nTranscript text:\n{text[:12000]}"
    )
    data = _structured_response(prompt, TRANSCRIPT_SCHEMA, "gradpath_transcript")
    if not data:
        return rule_draft, "AI transcript normalization unavailable; used rule extraction."
    draft = dict(rule_draft)
    courses = [course for course in data["coursework"] if course in allowed_courses]
    if courses:
        draft["coursework"] = courses
    if isinstance(data.get("gpa"), int | float) and 0 <= data["gpa"] <= 4:
        draft["gpa"] = round(float(data["gpa"]), 2)
    draft["coverage"] = data.get("notes") or draft.get("coverage", [])
    return draft, "AI transcript normalization applied; review before applying."


def build_fit_plan_with_ai(
    profile: dict[str, Any],
    program: dict[str, Any],
    rule_plan: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    prompt = (
        "Create a conservative next-step fit improvement plan for this applicant and graduate "
        "program. This is planning guidance, not an admissions guarantee. Include missing "
        "requirements, coursework, research/advisor actions, publication/project positioning, "
        "SOP angle, and faculty-contact advice for PhD-oriented programs.\n\n"
        f"Applicant profile:\n{json.dumps(profile)}\n\nProgram:\n{json.dumps(program)}\n\n"
        f"Rule plan:\n{json.dumps(rule_plan)}"
    )
    data = _structured_response(prompt, FIT_PLAN_SCHEMA, "gradpath_fit_plan")
    if not data:
        return rule_plan, "AI fit-plan unavailable; used rule plan."
    return data, "AI fit-plan applied; use as planning guidance."


def _structured_response(prompt: str, schema: dict[str, Any], name: str) -> dict[str, Any] | None:
    if not openai_available():
        return None
    try:
        from openai import OpenAI
    except ImportError:
        return None

    try:
        client = OpenAI()
        response = client.responses.create(
            model=os.getenv("GRADPATH_OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
            input=prompt,
            text={
                "format": {
                    "type": "json_schema",
                    "name": name,
                    "schema": schema,
                    "strict": True,
                }
            },
        )
        return json.loads(response.output_text)
    except Exception:
        return None
