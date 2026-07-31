from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import date
from typing import Any
from urllib.parse import urlparse

from gradpath.ai_extract import (
    analyze_program_unified_with_ai,
    build_fit_plan_with_ai,
    enrich_program_unified_with_ai,
    extract_program_with_ai,
    plan_search_queries_with_ai,
    reason_admit_confidence_with_ai,
    reason_match_with_ai,
    search_program_candidates_with_ai_web,
    summarize_community_evidence_with_ai,
)
from gradpath.matching import score_match
from gradpath.school_research import (
    extract_program_from_text,
    fetch_page_text,
    matched_program_candidates,
    search_school_candidates,
    search_web_candidates,
)
from gradpath.scoring import score_program

ADMIT_CONFIDENCE_BANDS = {"Likely-ish", "Target", "Reach", "High Reach", "Needs More Evidence"}


@dataclass(frozen=True)
class DeepResearchRequest:
    degree: str
    fields: list[str]
    countries: list[str]
    ranking_range: str
    funding_importance: str
    research_interests: list[str]
    target_count: int
    seed_schools: list[str]
    use_ai: bool
    ai_mode: str = "AI Deep Search"
    research_set_id: str = ""
    include_community: bool = True
    search_breadth: str = "Balanced"
    use_hosted_web_search: bool = False


def deterministic_query_templates(
    profile: dict[str, Any],
    request: DeepResearchRequest,
) -> list[str]:
    fields = request.fields or profile.get("target_fields", [])[:2] or ["Computer Science"]
    interests = request.research_interests or profile.get("research_interests", [])[:3]
    interest_text = " ".join(interests[:3])
    country_text = " ".join(request.countries[:2]) if request.countries else "United States"
    funding_text = (
        "funding assistantship"
        if request.funding_importance != "Flexible"
        else "funding"
    )
    queries = []
    for field in fields[:3]:
        queries.append(
            f"{request.degree} {field} {interest_text} admissions TOEFL GRE "
            f"{funding_text} official site:.edu {country_text}"
        )
        queries.append(
            f"{request.degree} {field} graduate requirements deadline statement of purpose "
            f"official admissions {interest_text}"
        )
    for school in request.seed_schools[:4]:
        for field in fields[:2]:
            queries.append(f"{school} {request.degree} {field} admissions requirements funding")
    return _dedupe_strings(queries)[:8]


def plan_deep_research_queries(
    profile: dict[str, Any],
    request: DeepResearchRequest,
) -> tuple[list[str], str]:
    fallback = deterministic_query_templates(profile, request)
    if not request.use_ai:
        return fallback, "Deterministic query planning used."
    context = {
        "degree": request.degree,
        "fields": request.fields,
        "countries": request.countries,
        "ranking_range": request.ranking_range,
        "funding_importance": request.funding_importance,
        "research_interests": request.research_interests,
        "target_count": request.target_count,
        "seed_schools": request.seed_schools,
    }
    return plan_search_queries_with_ai(profile, context, fallback)


def dedupe_candidates(candidates: list[dict[str, str]]) -> list[dict[str, str]]:
    seen = set()
    deduped = []
    for candidate in candidates:
        url = _canonical_url(candidate.get("url", ""))
        if not url or url in seen:
            continue
        seen.add(url)
        item = dict(candidate)
        item["url"] = url
        deduped.append(item)
    return deduped


def official_page_score(candidate: dict[str, str]) -> int:
    url = candidate.get("url", "").lower()
    title = candidate.get("title", "").lower()
    haystack = f"{url} {title}"
    score = 0
    if ".edu" in url:
        score += 5
    if any(word in haystack for word in ["admission", "apply", "application"]):
        score += 4
    if any(word in haystack for word in ["graduate", "phd", "doctoral", "master", "ms"]):
        score += 3
    if any(word in haystack for word in ["requirement", "deadline", "funding", "program"]):
        score += 2
    if any(word in haystack for word in ["reddit", "forum", "ranking", "usnews"]):
        score -= 6
    return score


def filter_official_candidates(
    candidates: list[dict[str, str]], limit: int
) -> list[dict[str, str]]:
    ranked = sorted(dedupe_candidates(candidates), key=official_page_score, reverse=True)
    return [candidate for candidate in ranked if official_page_score(candidate) >= 5][:limit]


def deterministic_admit_confidence(
    program: dict[str, Any],
    profile: dict[str, Any],
) -> dict[str, Any]:
    fit = score_program(program, profile)
    score = fit["score"]
    missing_text = " ".join(fit["missing"]).lower()
    source_confidence = program.get("source", {}).get("confidence", "")
    evidence_penalty = 8 if "Needs Review" in source_confidence else 0
    if "needs review" in missing_text:
        evidence_penalty += 5
    adjusted = max(0, score - evidence_penalty)
    if adjusted >= 84:
        band = "Likely-ish"
    elif adjusted >= 72:
        band = "Target"
    elif adjusted >= 58:
        band = "Reach"
    elif adjusted >= 42:
        band = "High Reach"
    else:
        band = "Needs More Evidence"
    return {
        "band": band,
        "score": adjusted,
        "why": (
            f"Deterministic fit score {score}, adjusted to {adjusted} for source certainty "
            "and missing evidence."
        ),
        "strengths": fit["strengths"][:4],
        "risks": fit["missing"][:4] or ["Competitiveness and faculty fit still need review."],
        "next_steps": fit["actions"][:4]
        or ["Verify official requirements and identify faculty/program fit."],
    }


def _process_single_candidate(
    candidate: dict[str, str],
    profile: dict[str, Any],
    request: DeepResearchRequest,
    primary_field: str,
    research_set_id: str,
    search_strategy: str,
    breadth: dict[str, Any],
) -> tuple[dict[str, Any] | None, dict[str, str]]:
    url = candidate["url"]
    try:
        title, page_text = fetch_page_text(url)
        program = extract_program_from_text(
            page_text, url, primary_field, request.degree, title
        )
        program["source"]["confidence"] = "Deep Research/Needs Review"
        program["program_source"] = "Deep Research"
        program["research_set_id"] = research_set_id
        program["research_mode"] = request.ai_mode

        extract_note = "Rule extraction completed."
        reason_note = "Rule admit-confidence estimate."
        fit_note = "Rule fit-plan completed."
        match_note = "Rule match completed."

        if request.use_ai:
            unified_data, unified_note = analyze_program_unified_with_ai(
                page_text, profile, program, url
            )
            if unified_data:
                p_data = unified_data.get("program", {})
                if p_data:
                    program["school"] = p_data.get("school") or program["school"]
                    program["program"] = p_data.get("program") or program["program"]
                    program["degree"] = (
                        p_data.get("degree")
                        if p_data.get("degree") in {"MS", "PhD"}
                        else program["degree"]
                    )
                    program["field"] = p_data.get("field") or program["field"]
                    program["location"] = p_data.get("location") or program["location"]
                    program["country"] = p_data.get("country") or program["country"]
                    program["requirements"]["deadline"] = (
                        p_data.get("deadline") or program["requirements"]["deadline"]
                    )
                    program["requirements"]["english"]["summary"] = p_data.get(
                        "english_summary", ""
                    )
                    program["requirements"]["english"]["minimum_score"] = p_data.get(
                        "english_minimum", 0
                    )
                    program["requirements"]["gre"]["status"] = (
                        p_data.get("gre_status") or "Needs Review"
                    )
                    program["requirements"]["gre"]["summary"] = p_data.get(
                        "gre_summary", ""
                    )
                    program["requirements"]["coursework"] = (
                        p_data.get("coursework") or program["requirements"]["coursework"]
                    )
                    program["preferences"]["program"] = p_data.get("program_preference", "")
                    program["preferences"]["sop"] = p_data.get("sop", "")
                    program["preferences"]["experience"] = (
                        p_data.get("experience") or program["preferences"]["experience"]
                    )
                    program["preferences"]["funding"] = p_data.get("funding", "")
                    program["phd"]["research_fit"] = p_data.get("research_fit", "")
                    program["phd"]["faculty_areas"] = p_data.get("faculty_areas", [])
                    program["matching"] = {
                        "program_route": p_data.get("program_route", ""),
                        "poi_list": p_data.get("poi_list", []),
                        "admission_system": p_data.get("admission_system", ""),
                        "test_policy": p_data.get("test_policy", ""),
                        "risk_factors": p_data.get("risk_factors", []),
                        "job_backup_value": p_data.get("job_backup_value", ""),
                    }
                    program["source"]["confidence"] = "AI Deep Research/Needs Review"

                reasoning = (
                    unified_data.get("admit_confidence")
                    or deterministic_admit_confidence(program, profile)
                )
                fit_plan = (
                    unified_data.get("fit_plan")
                    or deterministic_fit_plan(profile, program, reasoning)
                )
                match_reasoning = unified_data.get("match_reasoning")
                if match_reasoning:
                    program["match_ai_reasoning"] = match_reasoning

                extract_note = "Unified AI single-pass extraction."
                reason_note = "Unified AI admit-confidence."
                fit_note = "Unified AI fit-plan."
                match_note = "Unified AI match reasoning."
            else:
                program, extract_note = extract_program_with_ai(page_text, program, url)
                program["source"]["confidence"] = "AI Deep Research/Needs Review"
                reasoning, reason_note = reason_admit_confidence_with_ai(
                    profile, program, deterministic_admit_confidence(program, profile)
                )
                fit_plan, fit_note = build_fit_plan_with_ai(
                    profile, program, deterministic_fit_plan(profile, program, reasoning)
                )
                rule_match = score_match(program, profile).as_dict()
                match_reasoning, match_note = reason_match_with_ai(
                    profile, program, rule_match
                )
                program["match_ai_reasoning"] = match_reasoning
        else:
            reasoning = deterministic_admit_confidence(program, profile)
            fit_plan = deterministic_fit_plan(profile, program, reasoning)

        program["admit_confidence"] = reasoning
        program["next_fit_plan"] = fit_plan

        program["unofficial_evidence"] = []
        program["community_summary"] = {
            "summary": "Community evidence not searched.",
            "publication_expectation": "No unofficial publication signal yet.",
            "research_expectation": "No unofficial research signal yet.",
            "risk_note": "Unofficial evidence is advisory only.",
        }
        community_note = "Community search skipped."
        if request.include_community:
            evidence = find_community_evidence(program, target_count=breadth["community"])
            program["unofficial_evidence"] = evidence
            if request.use_ai and evidence:
                summary, community_note = summarize_community_evidence_with_ai(
                    program, evidence
                )
                program["community_summary"] = summary
            elif evidence:
                program["community_summary"] = deterministic_community_summary(evidence)
                community_note = "Rule community summary completed."

        program["match_result"] = score_match(program, profile).as_dict()
        program["search_strategy"] = search_strategy

        log_entry = {
            "stage": "page fetch + extraction",
            "query": "",
            "candidate_url": url,
            "source_type": candidate.get("source", "Candidate"),
            "fetch_status": "ok",
            "extraction_status": (
                f"{extract_note} {reason_note} {community_note} {fit_note} {match_note}"
            ),
        }
        return program, log_entry
    except Exception as exc:
        log_entry = {
            "stage": "page fetch + extraction",
            "query": "",
            "candidate_url": url,
            "source_type": candidate.get("source", "Candidate"),
            "fetch_status": "failed",
            "extraction_status": str(exc),
        }
        return None, log_entry


def run_deep_research(
    profile: dict[str, Any],
    request: DeepResearchRequest,
) -> dict[str, Any]:
    queries, query_note = plan_deep_research_queries(profile, request)
    fields = request.fields or profile.get("target_fields", [])[:1] or ["Computer Science"]
    primary_field = fields[0]
    logs: list[dict[str, str]] = [
        {
            "stage": "query planning",
            "query": query,
            "candidate_url": "",
            "source_type": "AI" if request.use_ai else "Rules",
            "fetch_status": "planned",
            "extraction_status": query_note,
        }
        for query in queries
    ]

    target_count = max(1, min(request.target_count, 30))
    breadth = _breadth_config(request.search_breadth)
    candidates = []
    online_candidates = []
    if request.use_ai and request.use_hosted_web_search:
        context = {
            "degree": request.degree,
            "fields": fields,
            "countries": request.countries,
            "ranking_range": request.ranking_range,
            "funding_importance": request.funding_importance,
            "research_interests": request.research_interests,
            "target_count": target_count,
            "seed_schools": request.seed_schools,
        }
        hosted_candidates, hosted_note = search_program_candidates_with_ai_web(
            profile, context, queries
        )
        candidates.extend(hosted_candidates)
        logs.append(
            {
                "stage": "hosted web search",
                "query": "OpenAI web_search_preview",
                "candidate_url": "",
                "source_type": "OpenAI",
                "fetch_status": "ok" if hosted_candidates else "fallback",
                "extraction_status": hosted_note,
            }
        )

    def _fetch_query_candidates(query: str) -> tuple[str, list[dict[str, str]], str | None]:
        try:
            found = search_school_candidates(
                query, primary_field, request.degree, breadth["results_per_query"]
            )
            return query, found, None
        except Exception as exc:
            return query, [], str(exc)

    with ThreadPoolExecutor(max_workers=min(6, len(queries) or 1)) as executor:
        futures = [executor.submit(_fetch_query_candidates, query) for query in queries]
        for future in futures:
            query, found, err = future.result()
            if err is None:
                online_candidates.extend(found)
                logs.append(
                    {
                        "stage": "web search",
                        "query": query,
                        "candidate_url": "",
                        "source_type": "Search",
                        "fetch_status": "ok",
                        "extraction_status": f"{len(found)} candidates",
                    }
                )
            else:
                logs.append(
                    {
                        "stage": "web search",
                        "query": query,
                        "candidate_url": "",
                        "source_type": "Search",
                        "fetch_status": "failed",
                        "extraction_status": err,
                    }
                )

    candidates.extend(online_candidates)
    fallback_used = False
    if len(dedupe_candidates(candidates)) < target_count:
        fallback_used = True
        for field in fields[:3]:
            candidates.extend(
                matched_program_candidates(profile, field, request.degree, target_count)
            )
        for school in request.seed_schools:
            candidates.extend(
                search_school_candidates(
                    school, primary_field, request.degree, breadth["results_per_query"]
                )
            )
    if online_candidates and fallback_used:
        search_strategy = "Online + fallback"
    elif online_candidates:
        search_strategy = "Online search"
    else:
        search_strategy = "Fallback only"
    research_set_id = request.research_set_id or f"research-{date.today().isoformat()}"
    official_candidates = filter_official_candidates(
        candidates, max(target_count * breadth["candidate_multiplier"], 8)
    )
    programs = []
    recommendations = []

    with ThreadPoolExecutor(max_workers=min(8, len(official_candidates) or 1)) as executor:
        futures = [
            executor.submit(
                _process_single_candidate,
                candidate,
                profile,
                request,
                primary_field,
                research_set_id,
                search_strategy,
                breadth,
            )
            for candidate in official_candidates
        ]
        for future in futures:
            program, log_entry = future.result()
            logs.append(log_entry)
            if program and len(programs) < target_count:
                programs.append(program)
                recommendations.append(_recommendation_row(program, program["admit_confidence"]))

    return {
        "queries": queries,
        "candidates": official_candidates,
        "programs": programs,
        "recommendations": sorted(
            recommendations, key=lambda item: item["Fit Score"], reverse=True
        ),
        "log": logs,
        "research_set_id": research_set_id,
        "search_strategy": search_strategy,
        "status": f"Deep research completed: {len(programs)} programs extracted.",
    }


def _enrich_single_seeded_program(
    seed: dict[str, Any],
    profile: dict[str, Any],
    use_ai: bool,
    research_set_id: str,
) -> tuple[dict[str, Any], dict[str, str]]:
    enriched = _copy_program(seed)
    enriched["id"] = f"enriched-{seed['id']}"
    enriched["program_source"] = "AI Enriched Sample" if use_ai else "Enriched Sample"
    enriched["research_set_id"] = research_set_id
    enriched["research_mode"] = "AI Seeded Enrichment" if use_ai else "Rule Seeded Enrichment"
    enriched["source"] = dict(seed["source"])
    enriched["source"]["confidence"] = (
        "AI Enriched Seeded/Needs Review" if use_ai else "Enriched Seeded/Needs Review"
    )
    evidence = find_community_evidence(enriched, target_count=4)
    enriched["unofficial_evidence"] = evidence
    if use_ai and evidence:
        community, community_note = summarize_community_evidence_with_ai(enriched, evidence)
    else:
        community = (
            deterministic_community_summary(evidence)
            if evidence
            else {
                "summary": "No community evidence collected.",
                "publication_expectation": "No unofficial publication signal yet.",
                "research_expectation": "No unofficial research signal yet.",
                "risk_note": "Unofficial evidence is advisory only.",
            }
        )
        community_note = "Rule community summary completed."
    enriched["community_summary"] = community

    reasoning = deterministic_admit_confidence(enriched, profile)
    fit_plan = deterministic_fit_plan(profile, enriched, reasoning)
    rule_match = score_match(enriched, profile).as_dict()

    reason_note = "Rule admit-confidence estimate."
    fit_note = "Rule fit-plan completed."
    match_note = "Rule match completed."

    if use_ai:
        unified_data, unified_note = enrich_program_unified_with_ai(profile, enriched)
        if unified_data:
            if "admit_confidence" in unified_data:
                reasoning = unified_data["admit_confidence"]
                reason_note = "Unified AI admit-confidence."
            if "fit_plan" in unified_data:
                fit_plan = unified_data["fit_plan"]
                fit_note = "Unified AI fit-plan."
            if "match_reasoning" in unified_data:
                enriched["match_ai_reasoning"] = unified_data["match_reasoning"]
                match_note = "Unified AI match reasoning."
        else:
            reasoning, reason_note = reason_admit_confidence_with_ai(profile, enriched, reasoning)
            fit_plan, fit_note = build_fit_plan_with_ai(profile, enriched, fit_plan)
            match_reasoning, match_note = reason_match_with_ai(profile, enriched, rule_match)
            enriched["match_ai_reasoning"] = match_reasoning

    enriched["admit_confidence"] = reasoning
    enriched["next_fit_plan"] = fit_plan
    enriched["match_result"] = score_match(enriched, profile).as_dict()
    enriched["search_strategy"] = "Seeded enrichment"

    log_entry = {
        "stage": "seeded enrichment",
        "query": seed["school"],
        "candidate_url": seed["source"]["url"],
        "source_type": enriched["program_source"],
        "fetch_status": "ok",
        "extraction_status": f"{community_note} {reason_note} {fit_note} {match_note}",
    }
    return enriched, log_entry


def enrich_seeded_programs(
    seeded_programs: list[dict[str, Any]],
    profile: dict[str, Any],
    use_ai: bool,
    limit: int = 8,
) -> dict[str, Any]:
    programs = []
    logs = []
    research_set_id = f"seeded-enrichment-{date.today().isoformat()}"
    targets = seeded_programs[:limit]

    with ThreadPoolExecutor(max_workers=min(8, len(targets) or 1)) as executor:
        futures = [
            executor.submit(
                _enrich_single_seeded_program,
                seed,
                profile,
                use_ai,
                research_set_id,
            )
            for seed in targets
        ]
        for future in futures:
            enriched, log_entry = future.result()
            programs.append(enriched)
            logs.append(log_entry)

    return {
        "programs": programs,
        "recommendations": [
            _recommendation_row(program, program["admit_confidence"]) for program in programs
        ],
        "log": logs,
        "research_set_id": research_set_id,
        "search_strategy": "Seeded enrichment",
        "status": f"Seeded enrichment completed: {len(programs)} programs enriched.",
    }


def find_community_evidence(
    program: dict[str, Any], target_count: int = 5
) -> list[dict[str, str]]:
    school = program.get("school", "")
    field = program.get("field", "")
    degree = program.get("degree", "")
    base = f"{school} {degree} {field} admissions publication research experience"
    platform_queries = [
        ("Reddit", f"{base} reddit"),
        ("Zhihu", f"{base} 知乎"),
        ("Baidu Tieba", f"{base} 百度贴吧"),
        ("Xiaohongshu", f"{base} 小红书"),
        ("X/Twitter", f"{base} twitter"),
        ("Facebook", f"{base} facebook"),
    ]

    def _fetch_platform(item: tuple[str, str]) -> tuple[str, list[dict[str, str]]]:
        platform, query = item
        try:
            return platform, search_web_candidates(query, 2)
        except Exception:
            return platform, []

    evidence = []
    with ThreadPoolExecutor(max_workers=min(6, len(platform_queries))) as executor:
        futures = [executor.submit(_fetch_platform, item) for item in platform_queries]
        for future in futures:
            platform, results = future.result()
            for result in results:
                if len(evidence) >= target_count:
                    break
                evidence.append(
                    {
                        "platform": platform,
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "snippet": result.get("title", ""),
                        "retrieved_at": date.today().isoformat(),
                        "signal_type": _community_signal_type(result.get("title", "")),
                        "risk_note": "Not official; verify manually.",
                        "confidence": "Unofficial/Needs Review",
                    }
                )
            if len(evidence) >= target_count:
                break
    return evidence[:target_count]


def deterministic_community_summary(evidence: list[dict[str, str]]) -> dict[str, str]:
    text = " ".join(item.get("title", "") for item in evidence).lower()
    publication_signal = "publication" in text or "paper" in text
    research_signal = "research" in text or "lab" in text or "advisor" in text
    return {
        "summary": f"{len(evidence)} unofficial public result(s) collected for manual review.",
        "publication_expectation": (
            "Some unofficial results mention publications/papers."
            if publication_signal
            else "No clear unofficial publication signal in collected titles."
        ),
        "research_expectation": (
            "Some unofficial results mention research/lab/advisor fit."
            if research_signal
            else "No clear unofficial research signal in collected titles."
        ),
        "risk_note": "Unofficial sources are not admissions policy; verify manually.",
    }


def deterministic_fit_plan(
    profile: dict[str, Any],
    program: dict[str, Any],
    reasoning: dict[str, Any],
) -> dict[str, Any]:
    profile_courses = set(profile.get("coursework", []))
    required_courses = program.get("requirements", {}).get("coursework", [])
    missing_courses = [course for course in required_courses if course not in profile_courses]
    degree = program.get("degree", "")
    research_actions = [
        "Identify 2-3 faculty whose recent work matches your research interests.",
        "Map one prior project/publication to each target faculty area.",
    ]
    if degree != "PhD":
        research_actions = [
            "Prepare one concise project story showing quantitative and programming depth.",
            "Connect coursework and projects to the program specialization.",
        ]
    return {
        "missing_requirements": reasoning.get("risks", [])[:4],
        "recommended_coursework": missing_courses[:5]
        or ["Keep transcript evidence ready for listed prerequisites."],
        "research_actions": research_actions,
        "publication_project_positioning": (
            "Emphasize publications if available; otherwise frame strong research projects, "
            "technical reports, or reproducible code as evidence of research maturity."
        ),
        "sop_angle": (
            f"Connect {', '.join(profile.get('research_interests', [])[:3]) or 'your interests'} "
            f"to {program.get('school')} faculty/program fit."
        ),
        "faculty_contact": (
            "For PhD applications, draft a short faculty-fit email after verifying active labs."
            if degree == "PhD"
            else "Faculty contact is optional; prioritize program fit and project evidence."
        ),
    }


def _recommendation_row(program: dict[str, Any], reasoning: dict[str, Any]) -> dict[str, Any]:
    match = program.get("match_result") or score_match(program, {}).as_dict()
    return {
        "School": program["school"],
        "Program": program["program"],
        "Degree": program["degree"],
        "Field": program["field"],
        "Category": match.get("category", ""),
        "Overall Score": match.get("overall_fit", reasoning["score"]),
        "POI Fit": match.get("poi_fit", ""),
        "Risk Note": match.get("risk_note", ""),
        "Next Action": match.get("next_action", ""),
        "Research Signal": match.get("research_signal", ""),
        "Letter Strategy": match.get("letter_strategy", ""),
        "Admit Confidence Estimate": reasoning["band"],
        "Fit Score": reasoning["score"],
        "Why This Band": reasoning["why"],
        "Deadline": program["requirements"]["deadline"],
        "Funding": program["preferences"]["funding"],
        "Research Fit": program.get("phd", {}).get("research_fit", "N/A"),
        "Missing/Risks": "; ".join(reasoning["risks"]),
        "Next Steps": "; ".join(reasoning["next_steps"]),
        "Source URL": program["source"]["url"],
        "Research Set": program.get("research_set_id", ""),
        "Source": program.get("program_source", "Deep Research"),
        "Community Summary": program.get("community_summary", {}).get("summary", ""),
        "Search Strategy": program.get("search_strategy", ""),
        "Next Fit Plan": _fit_plan_text(program.get("next_fit_plan", {})),
    }


def _fit_plan_text(plan: dict[str, Any]) -> str:
    if not plan:
        return ""
    parts = []
    for key in [
        "missing_requirements",
        "recommended_coursework",
        "research_actions",
        "publication_project_positioning",
        "sop_angle",
        "faculty_contact",
    ]:
        value = plan.get(key)
        if isinstance(value, list):
            value = "; ".join(value)
        if value:
            parts.append(f"{key.replace('_', ' ').title()}: {value}")
    return " | ".join(parts)


def _breadth_config(search_breadth: str) -> dict[str, int]:
    return {
        "Fast": {"results_per_query": 3, "candidate_multiplier": 2, "community": 2},
        "Balanced": {"results_per_query": 5, "candidate_multiplier": 3, "community": 4},
        "Deep": {"results_per_query": 8, "candidate_multiplier": 4, "community": 6},
    }.get(search_breadth, {"results_per_query": 5, "candidate_multiplier": 3, "community": 4})


def _copy_program(program: dict[str, Any]) -> dict[str, Any]:
    import copy

    return copy.deepcopy(program)


def _community_signal_type(title: str) -> str:
    lowered = title.lower()
    if any(word in lowered for word in ["publication", "paper", "research"]):
        return "Research/publication expectation"
    if any(word in lowered for word in ["admit", "accepted", "offer", "录取"]):
        return "Admission outcome report"
    return "General community discussion"


def _canonical_url(url: str) -> str:
    parsed = urlparse(url.strip())
    if not parsed.scheme or not parsed.netloc:
        return ""
    path = parsed.path.rstrip("/") or "/"
    return parsed._replace(path=path, params="", query="", fragment="").geturl()


def _dedupe_strings(values: list[str]) -> list[str]:
    seen = set()
    deduped = []
    for value in values:
        normalized = " ".join(value.split())
        lowered = normalized.lower()
        if normalized and lowered not in seen:
            seen.add(lowered)
            deduped.append(normalized)
    return deduped
