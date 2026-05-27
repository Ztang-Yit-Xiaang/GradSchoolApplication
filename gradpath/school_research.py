from __future__ import annotations

import hashlib
import os
import re
from datetime import date
from typing import Any
from urllib.parse import parse_qs, quote_plus, urlparse

from gradpath.profile_import import COURSE_KEYWORDS, EXPERIENCE_KEYWORDS, FIELD_KEYWORDS

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; GradPathPlanner/0.1; "
        "+https://localhost/gradpath-planner)"
    )
}

KNOWN_SCHOOL_URLS = {
    "university of michigan": "https://rackham.umich.edu/admissions/",
    "georgia tech": "https://grad.gatech.edu/admissions",
    "columbia university": "https://www.gradengineering.columbia.edu/admissions",
    "stanford university": "https://gradadmissions.stanford.edu/",
    "uc berkeley": "https://grad.berkeley.edu/admissions/",
    "carnegie mellon university": "https://www.cmu.edu/graduate/admission/index.html",
    "cornell university": "https://gradschool.cornell.edu/admissions/",
}

CURATED_MATCHED_PROGRAMS = [
    {
        "title": "University of Michigan CSE Graduate Admissions",
        "url": "https://cse.engin.umich.edu/academics/graduate/admissions/",
        "degrees": {"MS", "PhD"},
        "fields": {"Computer Science", "Data Science"},
        "keywords": {"machine learning", "optimization", "systems", "data science"},
    },
    {
        "title": "Carnegie Mellon School of Computer Science Graduate Admissions",
        "url": "https://www.cs.cmu.edu/academics/graduate-admissions",
        "degrees": {"MS", "PhD"},
        "fields": {"Computer Science", "Data Science"},
        "keywords": {"machine learning", "systems", "ai", "optimization"},
    },
    {
        "title": "Georgia Tech College of Computing Graduate Admissions",
        "url": "https://grad.cc.gatech.edu/",
        "degrees": {"MS", "PhD"},
        "fields": {"Computer Science", "Data Science"},
        "keywords": {"machine learning", "systems", "optimization"},
    },
    {
        "title": "Cornell Computer Science Graduate Admissions",
        "url": "https://www.cs.cornell.edu/phd/admissions",
        "degrees": {"PhD"},
        "fields": {"Computer Science", "Data Science"},
        "keywords": {"machine learning", "optimization", "theory"},
    },
    {
        "title": "Stanford Statistics Graduate Admissions",
        "url": "https://statistics.stanford.edu/academics/graduate-program/admissions",
        "degrees": {"MS", "PhD"},
        "fields": {"Statistics", "Data Science", "Applied Math"},
        "keywords": {"statistics", "machine learning", "predictive modeling"},
    },
    {
        "title": "UC Berkeley Statistics Graduate Admissions",
        "url": "https://statistics.berkeley.edu/academics/graduate/admissions",
        "degrees": {"MS", "PhD"},
        "fields": {"Statistics", "Data Science", "Applied Math"},
        "keywords": {"statistics", "machine learning", "data science"},
    },
    {
        "title": "Columbia IEOR Graduate Admissions",
        "url": "https://www.ieor.columbia.edu/admissions",
        "degrees": {"MS", "PhD"},
        "fields": {"Operations Research", "Data Science", "Applied Math"},
        "keywords": {"operations research", "optimization", "analytics"},
    },
    {
        "title": "MIT Operations Research Center Graduate Admissions",
        "url": "https://orc.mit.edu/admissions",
        "degrees": {"MS", "PhD"},
        "fields": {"Operations Research", "Applied Math", "Data Science"},
        "keywords": {"operations research", "optimization", "decision making"},
    },
    {
        "title": "NYU Courant Mathematics Graduate Admissions",
        "url": "https://math.nyu.edu/dynamic/degree/graduate/",
        "degrees": {"MS", "PhD"},
        "fields": {"Applied Math", "Computer Science", "Data Science"},
        "keywords": {"applied math", "scientific computing", "numerical analysis"},
    },
    {
        "title": "University of Washington Statistics Graduate Admissions",
        "url": "https://stat.uw.edu/academics/graduate/admissions",
        "degrees": {"MS", "PhD"},
        "fields": {"Statistics", "Data Science"},
        "keywords": {"statistics", "machine learning", "data science"},
    },
]


def fetch_page_text(url: str, timeout: int = 15) -> tuple[str, str]:
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError as exc:
        raise RuntimeError("Install requests and beautifulsoup4 for online research.") from exc

    response = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    text = soup.get_text("\n", strip=True)
    return title, re.sub(r"\n{3,}", "\n\n", text)


def extract_program_from_text(
    text: str,
    source_url: str,
    target_field: str = "Computer Science",
    degree_hint: str = "MS",
    title: str = "",
) -> dict[str, Any]:
    normalized = _normalize(text)
    school = _infer_school(source_url, title)
    degree = _infer_degree(normalized, degree_hint)
    field = _infer_field(normalized, target_field)
    deadline = _extract_deadline(text)
    english_minimum, english_summary = _extract_english_requirement(text)
    gre_status, gre_summary = _extract_gre_requirement(normalized)
    coursework = _extract_keyword_labels(normalized, COURSE_KEYWORDS) or ["Needs Review"]
    experience = _extract_keyword_labels(normalized, EXPERIENCE_KEYWORDS) or ["Projects"]
    funding = _extract_sentence(
        text,
        ["funding", "funded", "assistantship", "fellowship", "tuition"],
        "Funding details need manual review.",
    )
    sop = _extract_sentence(
        text,
        ["statement of purpose", "personal statement", "essay", "goals"],
        "Essay/SOP prompt needs manual review.",
    )
    research_fit = _extract_sentence(
        text,
        ["research", "faculty", "advisor", "laboratory", "lab"],
        "Research/advisor fit needs manual review.",
    )
    faculty_areas = _extract_research_areas(normalized)

    return {
        "id": _program_id(source_url, school, degree),
        "school": school,
        "program": _infer_program_name(title, field, degree),
        "degree": degree,
        "field": field,
        "location": "Needs Review",
        "country": "United States" if ".edu" in source_url else "Needs Review",
        "requirements": {
            "deadline": deadline,
            "english": {
                "required": "toefl" in normalized or "ielts" in normalized,
                "test": "TOEFL/IELTS",
                "minimum_score": english_minimum,
                "summary": english_summary,
            },
            "gre": {
                "status": gre_status,
                "summary": gre_summary,
            },
            "coursework": coursework,
        },
        "preferences": {
            "program": _extract_sentence(
                text,
                ["preparation", "background", "preferred", "recommended"],
                "Program preferences need manual review.",
            ),
            "sop": sop,
            "experience": experience,
            "funding": funding,
        },
        "phd": {
            "research_fit": research_fit if degree == "PhD" else "N/A",
            "faculty_areas": faculty_areas if degree == "PhD" else [],
        },
        "source": {
            "url": source_url,
            "retrieved_at": date.today().isoformat(),
            "confidence": "Live/Needs Review",
        },
    }


def search_school_candidates(
    query: str,
    target_field: str,
    degree: str,
    max_results: int = 5,
) -> list[dict[str, str]]:
    search_query = f"{query} {degree} {target_field} graduate admissions requirements"
    fallback = _known_school_candidates(query, max_results)
    if fallback:
        return fallback
    if os.getenv("SERPAPI_API_KEY"):
        results = _search_serpapi(search_query, max_results)
    else:
        results = _search_duckduckgo(search_query, max_results)
    return results


def search_web_candidates(query: str, max_results: int = 5) -> list[dict[str, str]]:
    if os.getenv("SERPAPI_API_KEY"):
        return _search_serpapi(query, max_results)
    return _search_duckduckgo(query, max_results, official_only=False)


def similar_program_queries(
    profile: dict[str, Any], degree: str, max_queries: int = 3
) -> list[str]:
    fields = profile.get("target_fields", [])[:2] or ["Computer Science"]
    interests = profile.get("research_interests", [])[:3]
    queries = []
    for field in fields:
        interest_part = " ".join(interests[:2])
        queries.append(f"best {degree} {field} programs {interest_part} admissions")
    return queries[:max_queries]


def matched_program_candidates(
    profile: dict[str, Any],
    target_field: str,
    degree: str,
    max_results: int = 5,
) -> list[dict[str, str]]:
    fields = set(profile.get("target_fields", []))
    fields.add(target_field)
    interests = {interest.lower() for interest in profile.get("research_interests", [])}
    candidates = []

    for program in CURATED_MATCHED_PROGRAMS:
        if degree not in program["degrees"]:
            continue
        field_overlap = fields.intersection(program["fields"])
        keyword_overlap = interests.intersection(program["keywords"])
        if not field_overlap and not keyword_overlap:
            continue
        score = (len(field_overlap) * 3) + len(keyword_overlap)
        if target_field in program["fields"]:
            score += 2
        candidates.append(
            {
                "title": program["title"],
                "url": program["url"],
                "source": "Curated fallback",
                "_score": str(score),
            }
        )

    ranked = sorted(candidates, key=lambda item: int(item["_score"]), reverse=True)
    return [
        {key: value for key, value in candidate.items() if key != "_score"}
        for candidate in ranked[:max_results]
    ]


def candidate_urls_from_text(text: str) -> list[str]:
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip().startswith(("http://", "https://"))
    ]


def _search_serpapi(query: str, max_results: int) -> list[dict[str, str]]:
    import requests

    response = requests.get(
        "https://serpapi.com/search.json",
        params={"q": query, "api_key": os.getenv("SERPAPI_API_KEY"), "num": max_results},
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()
    results = []
    for item in data.get("organic_results", [])[:max_results]:
        link = item.get("link")
        if link:
            results.append({"title": item.get("title", link), "url": link, "source": "SerpAPI"})
    return results


def _search_duckduckgo(
    query: str, max_results: int, official_only: bool = True
) -> list[dict[str, str]]:
    import requests
    from bs4 import BeautifulSoup

    response = requests.get(
        f"https://duckduckgo.com/html/?q={quote_plus(query)}",
        headers=DEFAULT_HEADERS,
        timeout=15,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    for link in soup.select("a.result__a"):
        href = link.get("href", "")
        title = link.get_text(" ", strip=True)
        parsed = urlparse(href)
        if parsed.query:
            href = parse_qs(parsed.query).get("uddg", [href])[0]
        if not official_only or _looks_official(href):
            results.append({"title": title, "url": href, "source": "DuckDuckGo"})
        if len(results) >= max_results:
            break
    return results


def _known_school_candidates(query: str, max_results: int) -> list[dict[str, str]]:
    lowered = query.lower()
    results = [
        {"title": school.title(), "url": url, "source": "Built-in fallback"}
        for school, url in KNOWN_SCHOOL_URLS.items()
        if school in lowered or lowered in school
    ]
    return results[:max_results]


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).lower()


def _infer_school(url: str, title: str) -> str:
    if title:
        return re.split(r"[-|:]", title)[-1].strip()[:80] or "Needs Review"
    host = urlparse(url).netloc.replace("www.", "")
    return host.split(".")[0].replace("-", " ").title()


def _infer_degree(text: str, hint: str) -> str:
    if "phd" in text or "ph.d" in text or "doctoral" in text:
        return "PhD"
    if "master" in text or "m.s." in text or "ms " in text:
        return "MS"
    return hint if hint in {"MS", "PhD"} else "MS"


def _infer_field(text: str, fallback: str) -> str:
    matches = _extract_keyword_labels(text, FIELD_KEYWORDS)
    return matches[0] if matches else fallback


def _infer_program_name(title: str, field: str, degree: str) -> str:
    if title and len(title) <= 110:
        return title
    return f"{degree} in {field}"


def _extract_deadline(text: str) -> str:
    iso = re.search(r"20\d{2}[-/](0?[1-9]|1[0-2])[-/](0?[1-9]|[12]\d|3[01])", text)
    if iso:
        return iso.group(0).replace("/", "-")
    month = re.search(
        r"(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|"
        r"aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
        r"\s+([0-3]?\d)",
        text,
        flags=re.IGNORECASE,
    )
    if month:
        return f"{month.group(1).title()} {month.group(2)}"
    return "Needs Review"


def _extract_english_requirement(text: str) -> tuple[int, str]:
    toefl = re.search(r"toefl(?:\s*ibt)?[^\d]{0,30}(\d{2,3})", text, flags=re.IGNORECASE)
    ielts = re.search(r"ielts[^\d]{0,30}(\d(?:\.\d)?)", text, flags=re.IGNORECASE)
    if toefl:
        score = int(toefl.group(1))
        return score, f"TOEFL appears to require or recommend {score}; verify source."
    if ielts:
        return 0, f"IELTS appears to require or recommend {ielts.group(1)}; verify source."
    return 0, "English requirement needs manual review."


def _extract_gre_requirement(text: str) -> tuple[str, str]:
    if "gre not required" in text or "gre is not required" in text:
        return "Not Required", "GRE not required appears on page; verify context."
    if "gre optional" in text:
        return "Optional", "GRE optional appears on page; verify context."
    if "gre required" in text:
        return "Required", "GRE required appears on page; verify context."
    if "gre" in text:
        return "Needs Review", "GRE mentioned; requirement status needs manual review."
    return "Needs Review", "GRE requirement not found."


def _extract_keyword_labels(text: str, keyword_map: dict[str, list[str]]) -> list[str]:
    return [
        label
        for label, keywords in keyword_map.items()
        if any(keyword.lower() in text for keyword in keywords)
    ]


def _extract_sentence(text: str, keywords: list[str], fallback: str) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text))
    for sentence in sentences:
        lowered = sentence.lower()
        if any(keyword in lowered for keyword in keywords):
            return sentence[:280]
    return fallback


def _extract_research_areas(text: str) -> list[str]:
    areas = [
        "machine learning",
        "data mining",
        "optimization",
        "statistics",
        "systems",
        "theory",
        "artificial intelligence",
        "data science",
    ]
    return [area for area in areas if area in text][:6]


def _program_id(url: str, school: str, degree: str) -> str:
    digest = hashlib.sha1(f"{url}{school}{degree}".encode()).hexdigest()[:10]
    return f"live-{digest}"


def _looks_official(url: str) -> bool:
    lowered = url.lower()
    return any(marker in lowered for marker in [".edu", "admission", "graduate", "program"])
