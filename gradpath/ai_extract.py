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
        "primary_tags": {"type": "array", "items": {"type": "string"}},
        "secondary_tags": {"type": "array", "items": {"type": "string"}},
        "evidence": {
            "type": "object",
            "properties": {
                "projects": {"type": "array", "items": {"type": "string"}},
                "papers": {"type": "array", "items": {"type": "string"}},
                "supervisors": {"type": "array", "items": {"type": "string"}},
                "publications": {"type": "array", "items": {"type": "string"}},
                "teaching": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["projects", "papers", "supervisors", "publications", "teaching"],
            "additionalProperties": False,
        },
        "test_strategy": {
            "type": "object",
            "properties": {
                "gre": {"type": "string"},
                "english": {"type": "string"},
                "ta": {"type": "string"},
            },
            "required": ["gre", "english", "ta"],
            "additionalProperties": False,
        },
        "recommenders": {
            "type": "object",
            "properties": {
                "Ju": {"type": "string"},
                "Swati": {"type": "string"},
                "Choi": {"type": "string"},
                "Ren": {"type": "string"},
            },
            "required": ["Ju", "Swati", "Choi", "Ren"],
            "additionalProperties": False,
        },
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
        "program_route": {"type": "string"},
        "poi_list": {"type": "array", "items": {"type": "string"}},
        "admission_system": {"type": "string"},
        "test_policy": {"type": "string"},
        "risk_factors": {"type": "array", "items": {"type": "string"}},
        "job_backup_value": {"type": "string"},
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
        "program_route",
        "poi_list",
        "admission_system",
        "test_policy",
        "risk_factors",
        "job_backup_value",
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

MATCH_REASONING_SCHEMA = {
    "type": "object",
    "properties": {
        "research_fit": {"type": "integer"},
        "evidence_fit": {"type": "integer"},
        "letter_fit": {"type": "integer"},
        "route_fit": {"type": "integer"},
        "practical_feasibility": {"type": "integer"},
        "overall_fit": {"type": "integer"},
        "category": {"type": "string"},
        "status": {"type": "string"},
        "poi_fit": {"type": "string"},
        "risk_note": {"type": "string"},
        "next_action": {"type": "string"},
        "research_signal": {"type": "string"},
        "letter_strategy": {"type": "string"},
    },
    "required": [
        "research_fit",
        "evidence_fit",
        "letter_fit",
        "route_fit",
        "practical_feasibility",
        "overall_fit",
        "category",
        "status",
        "poi_fit",
        "risk_note",
        "next_action",
        "research_signal",
        "letter_strategy",
    ],
    "additionalProperties": False,
}

WEB_CANDIDATES_SCHEMA = {
    "type": "object",
    "properties": {
        "candidates": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "url": {"type": "string"},
                    "source": {"type": "string"},
                    "reason": {"type": "string"},
                },
                "required": ["title", "url", "source", "reason"],
                "additionalProperties": False,
            },
        },
        "strategy": {"type": "string"},
    },
    "required": ["candidates", "strategy"],
    "additionalProperties": False,
}

UNIFIED_PROGRAM_ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "program": PROGRAM_SCHEMA,
        "admit_confidence": ADMIT_REASONING_SCHEMA,
        "fit_plan": FIT_PLAN_SCHEMA,
        "match_reasoning": MATCH_REASONING_SCHEMA,
    },
    "required": ["program", "admit_confidence", "fit_plan", "match_reasoning"],
    "additionalProperties": False,
}

UNIFIED_ENRICHMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "admit_confidence": ADMIT_REASONING_SCHEMA,
        "fit_plan": FIT_PLAN_SCHEMA,
        "match_reasoning": MATCH_REASONING_SCHEMA,
    },
    "required": ["admit_confidence", "fit_plan", "match_reasoning"],
    "additionalProperties": False,
}

ADMIT_BANDS = {"Likely-ish", "Target", "Reach", "High Reach", "Needs More Evidence"}
DEFAULT_OPENAI_MODEL = "gpt-5.5"

_OPENAI_CLIENT_CACHE: tuple[str | None, Any] = (None, None)


def openai_available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def _get_openai_client() -> Any:
    global _OPENAI_CLIENT_CACHE
    api_key = os.getenv("OPENAI_API_KEY")
    cached_key, client = _OPENAI_CLIENT_CACHE
    if client is None or cached_key != api_key:
        from openai import OpenAI

        client = OpenAI(timeout=30.0)
        _OPENAI_CLIENT_CACHE = (api_key, client)
    return client


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
        client = _get_openai_client()
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
        "Extract graduate applicant profile from CV text. Use rule profile as base. "
        "Return schema fields only. Keep unknown values conservative.\n\n"
        f"Rule profile:\n{json.dumps(rule_profile, separators=(',', ':'))}\n\n"
        f"CV text:\n{text[:12000]}"
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
        "Return conservative values; do not invent facts. Use draft as base.\n\n"
        f"URL: {source_url}\nDraft:\n{json.dumps(rule_program, separators=(',', ':'))}\n\n"
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
    program["matching"] = {
        "program_route": data["program_route"],
        "poi_list": data["poi_list"],
        "admission_system": data["admission_system"],
        "test_policy": data["test_policy"],
        "risk_factors": data["risk_factors"],
        "job_backup_value": data["job_backup_value"],
    }
    program["source"]["confidence"] = "AI/Needs Review"
    return program, "AI extraction applied; verify fields against official page."


def plan_search_queries_with_ai(
    profile: dict[str, Any],
    context: dict[str, Any],
    fallback_queries: list[str],
) -> tuple[list[str], str]:
    prompt = (
        "Plan official web search queries for graduate admissions research. "
        "Target university admissions, requirements, TOEFL/GRE, funding, and faculty pages. "
        "Write search queries only; do not invent schools.\n\n"
        f"Profile:\n{json.dumps(profile, separators=(',', ':'))}\n\n"
        f"Context:\n{json.dumps(context, separators=(',', ':'))}\n\n"
        f"Fallback queries:\n{json.dumps(fallback_queries, separators=(',', ':'))}"
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
        "Estimate graduate admissions confidence using profile, program record, and rule reasoning. "
        "Keep claims conservative. Use exact band: Likely-ish, Target, Reach, High Reach, Needs More Evidence.\n\n"
        f"Profile:\n{json.dumps(profile, separators=(',', ':'))}\n\n"
        f"Program:\n{json.dumps(program, separators=(',', ':'))}\n\n"
        f"Rule reasoning:\n{json.dumps(rule_reasoning, separators=(',', ':'))}"
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
        "Forum posts are advisory only. Note publications, research experience, and faculty contact signals.\n\n"
        f"Program:\n{json.dumps(program, separators=(',', ':'))}\n\n"
        f"Evidence:\n{json.dumps(evidence, separators=(',', ':'))}"
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
        "Normalize transcript text into graduate prerequisite categories. "
        "Use allowed coursework labels only; keep uncertainty in notes.\n\n"
        f"Allowed labels:\n{json.dumps(allowed_courses, separators=(',', ':'))}\n\n"
        f"Rule draft:\n{json.dumps(rule_draft, separators=(',', ':'))}\n\n"
        f"Transcript text:\n{text[:12000]}"
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
        "Create conservative next-step fit improvement plan for applicant and program. "
        "Include missing requirements, coursework, research/advisor actions, SOP angle, and faculty contact.\n\n"
        f"Profile:\n{json.dumps(profile, separators=(',', ':'))}\n\n"
        f"Program:\n{json.dumps(program, separators=(',', ':'))}\n\n"
        f"Rule plan:\n{json.dumps(rule_plan, separators=(',', ':'))}"
    )
    data = _structured_response(prompt, FIT_PLAN_SCHEMA, "gradpath_fit_plan")
    if not data:
        return rule_plan, "AI fit-plan unavailable; used rule plan."
    return data, "AI fit-plan applied; use as planning guidance."


def reason_match_with_ai(
    profile: dict[str, Any],
    program: dict[str, Any],
    rule_match: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    prompt = (
        "Create conservative graduate matching row for applicant and program. Anchor on rule match. "
        "Evaluate department research fit before prestige. Exact categories: 衝刺, Moderate, "
        "保底/Lower-risk PhD, MS/job, Demoted/archive. Exact status: Active, MS backup, Demoted/archive.\n\n"
        f"Profile:\n{json.dumps(profile, separators=(',', ':'), ensure_ascii=False)}\n\n"
        f"Program:\n{json.dumps(program, separators=(',', ':'), ensure_ascii=False)}\n\n"
        f"Rule match:\n{json.dumps(rule_match, separators=(',', ':'), ensure_ascii=False)}"
    )
    data = _structured_response(prompt, MATCH_REASONING_SCHEMA, "gradpath_match_reasoning")
    if not data:
        return rule_match, "AI match reasoning unavailable; used deterministic match."
    return data, "AI match reasoning applied; verify POI and policy details."


def search_program_candidates_with_ai_web(
    profile: dict[str, Any],
    context: dict[str, Any],
    fallback_queries: list[str],
) -> tuple[list[dict[str, str]], str]:
    prompt = (
        "Search web for official graduate program pages matching applicant profile. "
        "Target department admissions, requirements, faculty, funding, and deadline pages. "
        "Return candidate pages only; do not invent URLs.\n\n"
        f"Profile:\n{json.dumps(profile, separators=(',', ':'), ensure_ascii=False)}\n\n"
        f"Context:\n{json.dumps(context, separators=(',', ':'), ensure_ascii=False)}\n\n"
        f"Fallback queries:\n{json.dumps(fallback_queries, separators=(',', ':'), ensure_ascii=False)}"
    )
    data = _structured_response(
        prompt,
        WEB_CANDIDATES_SCHEMA,
        "gradpath_web_candidates",
        tools=[{"type": "web_search_preview"}],
    )
    if not data:
        return [], "Hosted OpenAI web search unavailable; used local search fallback."
    candidates = []
    for item in data.get("candidates", []):
        url = str(item.get("url", "")).strip()
        title = str(item.get("title", "")).strip()
        if not url or not title:
            continue
        candidates.append(
            {
                "title": title,
                "url": url,
                "source": item.get("source") or "OpenAI hosted web search",
                "reason": item.get("reason", ""),
            }
        )
    strategy = data.get("strategy", "targeted search")
    return candidates, f"Hosted OpenAI web search applied: {strategy}"


def analyze_program_unified_with_ai(
    text: str,
    profile: dict[str, Any],
    rule_program: dict[str, Any],
    source_url: str,
) -> tuple[dict[str, Any], str]:
    """Perform single-pass extraction, admit confidence, fit plan, and match reasoning in 1 unified API call."""
    prompt = (
        "Perform single-pass graduate admissions analysis for applicant and official admissions page.\n"
        "1. Extract requirement fields (program).\n"
        "2. Reason admit confidence band & score (admit_confidence).\n"
        "3. Formulate next fit steps (fit_plan).\n"
        "4. Calculate route & research match scores (match_reasoning).\n\n"
        "Keep claims conservative and grounded in official text.\n\n"
        f"URL: {source_url}\n"
        f"Profile:\n{json.dumps(profile, separators=(',', ':'), ensure_ascii=False)}\n\n"
        f"Draft:\n{json.dumps(rule_program, separators=(',', ':'), ensure_ascii=False)}\n\n"
        f"Page text:\n{text[:10000]}"
    )
    data = _structured_response(prompt, UNIFIED_PROGRAM_ANALYSIS_SCHEMA, "gradpath_unified_analysis")
    if not data:
        return {}, "Unified AI analysis unavailable; using fallback pipeline."
    return data, "Unified AI single-pass extraction and reasoning applied."


def enrich_program_unified_with_ai(
    profile: dict[str, Any],
    program: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    """Perform single-pass admit confidence, fit plan, and match reasoning in 1 unified API call."""
    prompt = (
        "Perform graduate admissions reasoning for this applicant and program.\n"
        "1. Reason admit confidence band & score (admit_confidence).\n"
        "2. Formulate next fit improvement steps (fit_plan).\n"
        "3. Calculate route & research match scores (match_reasoning).\n\n"
        "Keep claims conservative and grounded.\n\n"
        f"Applicant profile:\n{json.dumps(profile, separators=(',', ':'), ensure_ascii=False)}\n\n"
        f"Program record:\n{json.dumps(program, separators=(',', ':'), ensure_ascii=False)}"
    )
    data = _structured_response(prompt, UNIFIED_ENRICHMENT_SCHEMA, "gradpath_unified_enrichment")
    if not data:
        return {}, "Unified AI enrichment unavailable; using fallback reasoning."
    return data, "Unified AI single-pass enrichment applied."


def _structured_response(
    prompt: str,
    schema: dict[str, Any],
    name: str,
    tools: list[dict[str, Any]] | None = None,
) -> dict[str, Any] | None:
    if not openai_available():
        return None
    try:
        client = _get_openai_client()
    except Exception:
        return None

    try:
        kwargs: dict[str, Any] = {
            "model": os.getenv("GRADPATH_OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
            "input": prompt,
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": name,
                    "schema": schema,
                    "strict": True,
                }
            },
            "reasoning": {"effort": "low"},
        }
        if tools:
            kwargs["tools"] = tools
        response = client.responses.create(**kwargs)
        return json.loads(response.output_text)
    except Exception:
        return None

