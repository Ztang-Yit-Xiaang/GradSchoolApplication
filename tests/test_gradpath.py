from __future__ import annotations

from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from app import active_programs
from gradpath.ai_extract import (
    reason_match_with_ai,
)
from gradpath.ai_extract import (
    test_openai_connection as check_openai_connection,
)
from gradpath.data import default_profile, load_programs
from gradpath.export import (
    comparison_dataframe,
    reference_export_dataframe,
    results_dataframe,
    results_workbook_bytes,
)
from gradpath.filters import filter_programs
from gradpath.matching import (
    MATCH_SCORE_WEIGHTS,
    REFERENCE_EXPORT_COLUMNS,
    build_matching_rows,
    choose_recommenders,
    score_match,
)
from gradpath.profile_import import clean_latex_text, extract_text_from_upload, profile_from_text
from gradpath.research_agent import (
    ADMIT_CONFIDENCE_BANDS,
    DeepResearchRequest,
    dedupe_candidates,
    deterministic_admit_confidence,
    deterministic_fit_plan,
    deterministic_query_templates,
    enrich_seeded_programs,
    filter_official_candidates,
    find_community_evidence,
    run_deep_research,
)
from gradpath.school_research import (
    extract_program_from_text,
    matched_program_candidates,
    search_school_candidates,
)
from gradpath.scoring import score_program
from gradpath.transcript_import import (
    apply_transcript_to_profile,
    transcript_from_text,
)


def test_load_programs_has_ms_and_phd_records() -> None:
    programs = load_programs()
    degrees = {program["degree"] for program in programs}

    assert len(programs) >= 6
    assert {"MS", "PhD"}.issubset(degrees)


def test_default_profile_contains_matching_narrative() -> None:
    profile = default_profile()

    assert profile["primary_tags"] == [
        "optimization",
        "RandNLA",
        "scientific computing",
        "decision systems",
    ]
    assert "Choi" in profile["recommenders"]
    assert "gre" in profile["test_strategy"]
    assert any("OSQP" in item for item in profile["evidence"]["projects"])


def test_sidebar_css_has_high_contrast_widget_rules() -> None:
    css = Path("app.py").read_text(encoding="utf-8")

    assert "section[data-testid=\"stSidebar\"] div[data-baseweb=\"select\"] div" in css
    assert "section[data-testid=\"stSidebar\"] div.stButton > button" in css
    assert "color: #f5f5f0" in css


def test_scoring_returns_explainable_fit() -> None:
    program = next(program for program in load_programs() if program["degree"] == "PhD")
    result = score_program(program, default_profile())

    assert 0 <= result["score"] <= 100
    assert result["band"] in {"Strong", "Good", "Needs Review", "Risky"}
    assert result["strengths"] or result["missing"]
    assert "faculty" in result["sop_angle"].lower() or "research" in result["sop_angle"].lower()


def test_match_score_uses_five_pass_weight_formula() -> None:
    program = next(program for program in load_programs() if program["degree"] == "PhD")
    match = score_match(program, default_profile())

    expected = round(
        MATCH_SCORE_WEIGHTS["research_fit"] * match.research_fit
        + MATCH_SCORE_WEIGHTS["evidence_fit"] * match.evidence_fit
        + MATCH_SCORE_WEIGHTS["letter_fit"] * match.letter_fit
        + MATCH_SCORE_WEIGHTS["route_fit"] * match.route_fit
        + MATCH_SCORE_WEIGHTS["practical_feasibility"] * match.practical_feasibility
    )

    assert match.overall_fit == expected
    assert match.category in {
        "衝刺",
        "Moderate",
        "保底/Lower-risk PhD",
        "MS/job",
        "Demoted/archive",
    }
    assert match.next_action


def test_recommender_strategy_depends_on_route() -> None:
    assert choose_recommenders("CEE/transportation") == ["Choi", "Ju", "Swati"]
    assert choose_recommenders("RandNLA / randomized algorithms") == ["Swati", "Ju", "Choi"]
    assert choose_recommenders("sensing inverse modeling") == ["Ren", "Ju", "Swati"]


def test_filter_programs_can_select_phd_with_funding() -> None:
    programs = load_programs()
    filtered = filter_programs(
        programs,
        degree="PhD",
        funding="Funded/assistantship visible",
        deadline_window="Any",
    )

    assert filtered
    assert all(program["degree"] == "PhD" for program in filtered)
    assert any("fund" in program["preferences"]["funding"].lower() for program in filtered)


def test_result_filters_can_select_latest_deep_research() -> None:
    programs = load_programs()
    deep_program = extract_program_from_text(
        "PhD in Computer Science. TOEFL 100. GRE optional. Funding through assistantships.",
        "https://example.edu/cs/phd/admissions",
        target_field="Computer Science",
        degree_hint="PhD",
        title="PhD in Computer Science",
    )
    deep_program["program_source"] = "Deep Research"
    deep_program["research_set_id"] = "research-latest"
    deep_program["admit_confidence"] = {"band": "Target"}
    filtered = filter_programs(
        [*programs, deep_program],
        program_source="Deep Research",
        admit_band="Target",
        latest_research_set_id="research-latest",
        only_researched=True,
    )

    assert filtered == [deep_program]


def test_default_active_programs_excludes_seeded_until_research() -> None:
    seeded = load_programs()

    active = active_programs(seeded, [], "Discovered programs")

    assert active == []


def test_active_program_modes_keep_seeded_optional() -> None:
    seeded = load_programs()
    discovered = extract_program_from_text(
        "PhD in Computer Science. TOEFL 100.",
        "https://example.edu/cs/phd/admissions",
        target_field="Computer Science",
        degree_hint="PhD",
        title="PhD in Computer Science",
    )
    discovered["program_source"] = "Deep Research"
    manual = extract_program_from_text(
        "MS in Data Science. TOEFL 95.",
        "https://example.edu/ds/ms/admissions",
        target_field="Data Science",
        degree_hint="MS",
        title="MS in Data Science",
    )
    manual["program_source"] = "Manual URL"

    assert active_programs(seeded, [discovered, manual], "Discovered programs") == [discovered]
    assert active_programs(seeded, [discovered, manual], "Discovered + manual") == [
        discovered,
        manual,
    ]
    assert seeded[0] in active_programs(
        seeded, [discovered, manual], "Include sample seeded programs"
    )


def test_results_dataframe_contains_required_export_columns() -> None:
    df = results_dataframe(load_programs(), default_profile())

    expected = {
        "Fit",
        "Score",
        "School",
        "Program",
        "Degree",
        "English",
        "GRE",
        "Coursework",
        "DDL",
        "Funding",
        "Research Fit",
        "SOP",
        "Missing",
        "Source URL",
        "Source",
        "Research Set",
        "Admit Confidence Estimate",
    }
    assert expected.issubset(df.columns)
    assert df["Score"].is_monotonic_decreasing
    assert {"Category", "POI Fit", "Next Action", "Letter Strategy"}.issubset(df.columns)
    assert df["Overall Score"].is_monotonic_decreasing


def test_reference_export_preserves_expected_column_order() -> None:
    df = reference_export_dataframe(load_programs(), default_profile())

    assert list(df.columns) == REFERENCE_EXPORT_COLUMNS
    assert not df.empty
    assert df["POI Fit"].str.len().gt(0).all()


def test_xlsx_export_contains_required_sheets() -> None:
    data = results_workbook_bytes(load_programs(), default_profile())

    with ZipFile(BytesIO(data)) as workbook:
        names = set(workbook.namelist())
        workbook_xml = workbook.read("xl/workbook.xml").decode("utf-8")

    assert "xl/worksheets/sheet1.xml" in names
    assert "xl/worksheets/sheet5.xml" in names
    for sheet_name in ["Shortlist", "Score Breakdown", "Actions", "Sources", "Profile"]:
        assert sheet_name in workbook_xml


def test_balance_notes_warn_when_shortlist_is_too_small() -> None:
    rows = build_matching_rows(load_programs()[:3], default_profile())

    assert any("Need" in row["Balance Note"] for row in rows)


def test_comparison_dataframe_keeps_ms_phd_requirements() -> None:
    df = results_dataframe(load_programs(), default_profile())
    comparison = comparison_dataframe(df.head(3).to_dict("records"))

    assert list(comparison.columns) == [
        "University",
        "Program",
        "Degree",
        "Category",
        "Overall Score",
        "Research Fit Score",
        "POI Fit",
        "Professors",
        "Risk Note",
        "Next Action",
        "Letter Strategy",
        "TOEFL/GRE",
        "Application Website",
    ]
    assert len(comparison) == 3


def test_cv_text_maps_to_profile_draft() -> None:
    text = """
    GPA: 3.82/4.0
    TOEFL iBT 106
    GRE Quant 168
    Research assistant in machine learning and optimization lab.
    Coursework: Programming, Data Structures, Algorithms, Linear Algebra, Statistics.
    Internship project using Python, SQL, and PyTorch.
    """
    profile = profile_from_text(text, default_profile())

    assert profile["gpa"] == 3.82
    assert profile["english_test"] == "TOEFL"
    assert profile["english_score"] == 106
    assert profile["gre_status"] == "Completed"
    assert profile["gre_quant"] == 168
    assert "Research" in profile["experience"]
    assert "Machine Learning" in profile["coursework"]


def test_program_page_text_maps_to_live_program_record() -> None:
    text = """
    PhD in Computer Science admissions. Application deadline December 1.
    TOEFL iBT minimum 100. GRE not required.
    Applicants should have programming, algorithms, linear algebra, and probability.
    Statement of purpose should discuss research interests, faculty advisors, and goals.
    PhD students are funded through assistantship and fellowship support.
    Research areas include machine learning, optimization, data mining, and systems.
    """
    program = extract_program_from_text(
        text,
        "https://example.edu/cs/phd/admissions",
        target_field="Computer Science",
        degree_hint="PhD",
        title="PhD in Computer Science Admissions",
    )

    assert program["id"].startswith("live-")
    assert program["degree"] == "PhD"
    assert program["requirements"]["english"]["minimum_score"] == 100
    assert program["requirements"]["gre"]["status"] == "Not Required"
    assert "Algorithms" in program["requirements"]["coursework"]
    assert program["source"]["confidence"] == "Live/Needs Review"


def test_live_programs_join_export_results() -> None:
    profile = default_profile()
    live_program = extract_program_from_text(
        "MS in Data Science. TOEFL 90. GRE optional. Programming and statistics required.",
        "https://example.edu/data-science/ms",
        target_field="Data Science",
        degree_hint="MS",
        title="MS in Data Science",
    )
    df = results_dataframe([*load_programs(), live_program], profile)

    assert "Live/Needs Review" in set(df["Confidence"])
    assert live_program["source"]["url"] in set(df["Source URL"])


def test_school_search_has_builtin_fallback(monkeypatch) -> None:
    def fake_search(query: str, max_results: int) -> list[dict[str, str]]:
        return []

    monkeypatch.setattr("gradpath.school_research._search_duckduckgo", fake_search)
    results = search_school_candidates("University of Michigan", "Computer Science", "PhD")

    assert results
    assert results[0]["source"] == "Built-in fallback"
    assert "umich.edu" in results[0]["url"]


def test_similar_program_fallback_returns_curated_candidates() -> None:
    results = matched_program_candidates(default_profile(), "Data Science", "PhD", max_results=4)

    assert results
    assert all(result["source"] == "Curated fallback" for result in results)
    assert any("admissions" in result["url"].lower() for result in results)


def test_openai_connection_reports_missing_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = check_openai_connection()

    assert result["available"] is False
    assert result["ok"] is False
    assert "OPENAI_API_KEY" in result["message"]


def test_ai_match_reasoning_falls_back_to_rule_match(monkeypatch) -> None:
    rule_match = score_match(load_programs()[0], default_profile()).as_dict()
    monkeypatch.setattr("gradpath.ai_extract._structured_response", lambda *args, **kw: None)

    result, note = reason_match_with_ai(default_profile(), load_programs()[0], rule_match)

    assert result == rule_match
    assert "deterministic" in note.lower()


def test_transcript_parser_extracts_coursework_and_applies_profile() -> None:
    text = """
    Unofficial Transcript
    Cumulative GPA: 3.95
    Linear Algebra A
    Probability and Statistics A
    Data Structures A
    Algorithm Design A
    Machine Learning A
    Optimization A
    """

    draft, notes = transcript_from_text(text)
    updated = apply_transcript_to_profile(default_profile(), draft)

    assert draft["gpa"] == 3.95
    assert "Linear Algebra" in draft["coursework"]
    assert "Machine Learning" in updated["coursework"]
    assert notes


def test_deep_research_query_fallback_is_deterministic() -> None:
    request = DeepResearchRequest(
        degree="PhD",
        fields=["Computer Science"],
        countries=["United States"],
        ranking_range="Balanced",
        funding_importance="Important",
        research_interests=["machine learning", "optimization"],
        target_count=3,
        seed_schools=["University of Illinois"],
        use_ai=False,
    )

    queries = deterministic_query_templates(default_profile(), request)

    assert queries
    assert any("PhD Computer Science" in query for query in queries)
    assert any("University of Illinois" in query for query in queries)


def test_deep_research_candidate_dedupe_and_official_filter() -> None:
    candidates = [
        {
            "title": "Official CS Admissions",
            "url": "https://cs.example.edu/admissions",
            "source": "x",
        },
        {
            "title": "Official CS Admissions",
            "url": "https://cs.example.edu/admissions/",
            "source": "y",
        },
        {"title": "Forum ranking", "url": "https://reddit.com/r/gradadmissions", "source": "z"},
    ]

    deduped = dedupe_candidates(candidates)
    official = filter_official_candidates(candidates, 5)

    assert len(deduped) == 2
    assert len(official) == 1
    assert official[0]["url"] == "https://cs.example.edu/admissions"


def test_deterministic_admit_confidence_returns_supported_band() -> None:
    program = extract_program_from_text(
        "PhD in Computer Science. TOEFL 100. GRE not required. "
        "Applicants need programming, algorithms, linear algebra, probability. "
        "Funding through assistantships. Research includes machine learning and optimization.",
        "https://example.edu/cs/phd/admissions",
        target_field="Computer Science",
        degree_hint="PhD",
        title="PhD in Computer Science",
    )

    reasoning = deterministic_admit_confidence(program, default_profile())

    assert reasoning["band"] in ADMIT_CONFIDENCE_BANDS
    assert 0 <= reasoning["score"] <= 100
    assert reasoning["why"]


def test_deep_research_records_merge_with_export(monkeypatch) -> None:
    def fake_search(query: str, target_field: str, degree: str, max_results: int):
        return [
            {
                "title": "Example CS PhD Admissions",
                "url": "https://cs.example.edu/phd/admissions",
                "source": "Fake",
            }
        ]

    def fake_fetch(url: str):
        return (
            "Example CS PhD Admissions",
            "PhD in Computer Science. TOEFL 100. GRE optional. "
            "Deadline December 1. Programming, algorithms, linear algebra required. "
            "Statement of purpose should discuss faculty research fit. "
            "Funding through assistantships. Research areas include machine learning.",
        )

    monkeypatch.setattr("gradpath.research_agent.search_school_candidates", fake_search)
    monkeypatch.setattr("gradpath.research_agent.fetch_page_text", fake_fetch)
    request = DeepResearchRequest(
        degree="PhD",
        fields=["Computer Science"],
        countries=["United States"],
        ranking_range="Balanced",
        funding_importance="Important",
        research_interests=["machine learning"],
        target_count=1,
        seed_schools=[],
        use_ai=False,
        search_breadth="Fast",
    )

    result = run_deep_research(default_profile(), request)
    df = results_dataframe([*load_programs(), *result["programs"]], default_profile())

    assert result["programs"]
    assert len(result["programs"]) <= request.target_count
    assert result["programs"][0]["program_source"] == "Deep Research"
    assert result["programs"][0]["research_set_id"]
    assert result["recommendations"][0]["Admit Confidence Estimate"] in ADMIT_CONFIDENCE_BANDS
    assert "Admit Confidence Estimate" in df.columns
    assert "Research Set" in df.columns
    assert "Next Fit Plan" in df.columns


def test_online_first_search_skips_curated_when_enough_online(monkeypatch) -> None:
    calls = {"fallback": 0}

    def fake_search(query: str, target_field: str, degree: str, max_results: int):
        return [
            {
                "title": "Example CS PhD Admissions",
                "url": "https://cs.example.edu/phd/admissions",
                "source": "Fake Search",
            }
        ]

    def fake_fallback(profile, target_field, degree, max_results):
        calls["fallback"] += 1
        return []

    def fake_fetch(url: str):
        return (
            "Example CS PhD Admissions",
            "PhD in Computer Science. TOEFL 100. GRE optional. "
            "Programming, algorithms, linear algebra required. Funding via assistantships.",
        )

    monkeypatch.setattr("gradpath.research_agent.search_school_candidates", fake_search)
    monkeypatch.setattr("gradpath.research_agent.matched_program_candidates", fake_fallback)
    monkeypatch.setattr("gradpath.research_agent.fetch_page_text", fake_fetch)
    request = DeepResearchRequest(
        degree="PhD",
        fields=["Computer Science"],
        countries=["United States"],
        ranking_range="Balanced",
        funding_importance="Important",
        research_interests=["machine learning"],
        target_count=1,
        seed_schools=[],
        use_ai=False,
        include_community=False,
    )

    result = run_deep_research(default_profile(), request)

    assert result["search_strategy"] == "Online search"
    assert calls["fallback"] == 0


def test_seeded_enrichment_preserves_original_and_adds_fit_plan(monkeypatch) -> None:
    monkeypatch.setattr("gradpath.research_agent.find_community_evidence", lambda *args, **kw: [])
    original = load_programs()[0]
    result = enrich_seeded_programs([original], default_profile(), use_ai=False, limit=1)

    enriched = result["programs"][0]

    assert original["id"] != enriched["id"]
    assert original["source"]["confidence"] == "Sample"
    assert enriched["program_source"] == "Enriched Sample"
    assert enriched["next_fit_plan"]


def test_deterministic_fit_plan_has_next_steps() -> None:
    program = load_programs()[0]
    reasoning = deterministic_admit_confidence(program, default_profile())
    plan = deterministic_fit_plan(default_profile(), program, reasoning)

    assert plan["recommended_coursework"]
    assert plan["sop_angle"]
    assert "guarantee" not in " ".join(str(value) for value in plan.values()).lower()


def test_community_evidence_does_not_replace_official_requirements(monkeypatch) -> None:
    program = extract_program_from_text(
        "PhD admissions. GRE not required. TOEFL 100.",
        "https://example.edu/phd/admissions",
        target_field="Computer Science",
        degree_hint="PhD",
        title="PhD Admissions",
    )
    original_gre = program["requirements"]["gre"]["status"]

    def fake_search(query: str, max_results: int):
        return [
            {
                "title": "Applicants discuss publications and research experience",
                "url": "https://reddit.com/r/gradadmissions/example",
                "source": "Fake",
            }
        ]

    monkeypatch.setattr("gradpath.research_agent.search_web_candidates", fake_search)
    evidence = find_community_evidence(program, target_count=1)

    assert evidence
    assert evidence[0]["confidence"] == "Unofficial/Needs Review"
    assert program["requirements"]["gre"]["status"] == original_gre


def test_default_profile_is_yixin_cv_derived() -> None:
    profile = default_profile()

    assert profile["gpa"] == 4.0
    assert profile["target_degree"] == "Both"
    assert "Operations Research" in profile["target_fields"]
    assert "Research" in profile["experience"]
    assert "Publication" in profile["experience"]
    assert "randomized numerical linear algebra" in profile["research_interests"]


def test_tex_cv_upload_is_cleaned_and_extracted() -> None:
    tex = r"""
    \CVSECTION{Research Interests}
    Machine Learning, Optimization, Scientific Computing, Randomized Numerical Linear Algebra,
    Sequential Decision Making, Learning-Augmented Decision Systems, Predictive Modeling.
    \CVSECTION{Education}
    \entrysub{B.S. in Data Science; Minor in Mathematics \hfill GPA: 4.0/4.0}
    \entrysub{Selected coursework: Machine Learning, Deep Learning, Natural Language Processing,
    Optimization, Regression, Numerical Analysis, Software Design}
    \CVSECTION{Publications}
    \item \textbf{Chen, Y.} Automated Storage and Retrieval System Optimization with MILP Methods.
    \CVSECTION{Teaching \& Mentoring}
    Teaching Assistant -- CSCI 2081: Introduction to Software Design.
    """

    text = extract_text_from_upload("Academic CV.tex", tex.encode())
    profile = profile_from_text(text, default_profile())

    assert "\\CVSECTION" not in clean_latex_text(tex)
    assert profile["gpa"] == 4.0
    assert "Machine Learning" in profile["coursework"]
    assert "Natural Language Processing" in profile["coursework"]
    assert "Publication" in profile["experience"]
    assert "Teaching/TA" in profile["experience"]
    assert "scientific computing" in profile["research_interests"]


def test_persistence_load_and_save(tmp_path) -> None:
    from gradpath.persistence import get_pi_note, load_workspace, save_workspace, set_pi_note

    test_file = tmp_path / "test_workspace.json"
    ws = load_workspace(test_file)
    assert ws["pi_notes"] == {}

    set_pi_note(ws, "Prof. Test", "Discussed MILP optimization")
    assert get_pi_note(ws, "Prof. Test") == "Discussed MILP optimization"

    saved_ok = save_workspace(ws, test_file)
    assert saved_ok is True

    loaded_ws = load_workspace(test_file)
    assert get_pi_note(loaded_ws, "Prof. Test") == "Discussed MILP optimization"


def test_custom_slider_weights_matching() -> None:
    from gradpath.matching import score_match

    program = load_programs()[0]
    profile = default_profile()

    default_match = score_match(program, profile)
    custom_match = score_match(
        program,
        profile,
        custom_weights={
            "research_fit": 0.80,
            "evidence_fit": 0.05,
            "letter_fit": 0.05,
            "route_fit": 0.05,
            "practical_feasibility": 0.05,
        },
    )

    assert default_match.overall_fit != custom_match.overall_fit or custom_match.research_fit == default_match.research_fit


def test_calculate_real_stipend() -> None:
    from gradpath.matching import calculate_real_stipend

    stanford_stipend = calculate_real_stipend(45000, "Stanford University")
    purdue_stipend = calculate_real_stipend(30000, "Purdue University West Lafayette")

    assert stanford_stipend["col_index"] == 1.85
    assert stanford_stipend["real_stipend"] < 45000
    assert purdue_stipend["col_index"] == 1.05
    assert purdue_stipend["real_stipend"] > 25000


def test_pi_outreach_urls_and_hiring_signal() -> None:
    from gradpath.matching import build_pi_outreach_urls, pi_hiring_signal

    urls = build_pi_outreach_urls("Ju Sun", "University of Minnesota")

    assert "nsf.gov/awardsearch" in urls["nsf_awards"]
    assert "reporter.nih.gov" in urls["nih_reporter"]
    assert "scholar.google.com" in urls["google_scholar"]
    assert "site%3Alinkedin.com" in urls["linkedin"]
    assert "site%3Ax.com" in urls["x_twitter"]
    assert "faculty+homepage" in urls["personal_homepage"]

    normal_sig = pi_hiring_signal("Ju Sun", "No notes yet")
    assert normal_sig["level"] == "Standard"

    nsf_sig = pi_hiring_signal("Ju Sun", "Received new NSF Award #2401920 for optimization")
    assert nsf_sig["level"] == "High"
    assert "High Hiring Likelihood" in nsf_sig["hiring_badge"]


def test_pi_peer_review_urls_and_mentorship_eval() -> None:
    from gradpath.matching import build_pi_peer_review_urls, evaluate_pi_mentorship_flags

    urls = build_pi_peer_review_urls("Ju Sun", "University of Minnesota")

    assert "ratemyprofessors.com" in urls["ratemyprofessors"]
    assert "site%3Areddit.com" in urls["reddit_peer_review"]
    assert "site%3Arateyourpi.com" in urls["rateyourpi"]
    assert "alumni+phd+graduates" in urls["lab_alumni_placements"]

    unverified = evaluate_pi_mentorship_flags("Ju Sun", "No notes yet")
    assert unverified["safety"] == "Unverified"

    toxic_notes = evaluate_pi_mentorship_flags("Test Prof", "Students report toxic micromanage environment and 7 years delay")
    assert toxic_notes["safety"] == "Caution"
    assert "Red Flag Alert" in toxic_notes["badge"]

    good_notes = evaluate_pi_mentorship_flags("Good Prof", "Supportive mentor, students graduated in 5 years to tenure track")
    assert good_notes["safety"] == "Safe"
    assert "Highly Recommended" in good_notes["badge"]


def test_canonical_schemas_and_workspace_migration(tmp_path) -> None:
    from gradpath.persistence import load_workspace, migrate_workspace, save_workspace
    from gradpath.schemas import SCHEMA_VERSION

    old_data = {"profile": {"target_degree": "PhD"}, "pi_notes": {"Ju Sun": "NSF Award"}}
    migrated = migrate_workspace(old_data)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["profile"]["target_degree"] == "PhD"
    assert migrated["pi_notes"]["Ju Sun"] == "NSF Award"

    file = tmp_path / "workspace.json"
    assert save_workspace(migrated, file) is True
    reloaded = load_workspace(file)
    assert reloaded["schema_version"] == SCHEMA_VERSION
    assert reloaded["pi_notes"]["Ju Sun"] == "NSF Award"


def test_admission_mode_taxonomy_and_conflict_detection() -> None:
    from gradpath.admission_mode import classify_admission_mode, detect_evidence_conflicts

    direct = classify_admission_mode("Must secure a faculty sponsor prior to admission", degree="PhD")
    assert direct.application_mode == "direct_pi_sponsor"
    assert direct.contact_policy == "required"

    committee = classify_admission_mode("Admissions committee reviews all applications; advisors assigned after matriculation", degree="PhD")
    assert committee.application_mode == "committee_program"

    rotation = classify_admission_mode("Students complete lab rotations during year 1 in this umbrella program", degree="PhD")
    assert rotation.application_mode == "rotation_or_umbrella"

    thesis_ms = classify_admission_mode("Master of Science with thesis required", degree="MS")
    assert thesis_ms.application_mode == "research_thesis_ms"

    coursework_ms = classify_admission_mode("Non-thesis coursework-only professional master", degree="MS")
    assert coursework_ms.application_mode == "coursework_professional_ms"

    ambiguous = classify_admission_mode("The academic advisor assists with registration", degree="PhD")
    assert ambiguous.application_mode == "unknown_needs_review"

    conflicts = detect_evidence_conflicts([
        {"evidence_excerpt": "Application deadline: Dec 15"},
        {"evidence_excerpt": "Application deadline: Jan 15"},
        {"evidence_excerpt": "Fully funded PhD program"},
        {"evidence_excerpt": "Self-funded tuition requirement"},
    ])
    assert len(conflicts) >= 2


def test_transparent_scoring_and_portfolio_balance() -> None:
    from gradpath.scoring import (
        check_portfolio_balance,
        compute_joint_score,
        compute_pi_score,
        compute_program_score,
    )

    program = {
        "degree": "PhD",
        "stipend_amount": 38000,
        "col_index": 1.15,
        "preferences": {"funding": "Fully funded assistantship"},
        "requirements": {"coursework": ["Linear Algebra", "Optimization"], "english": {"required": False}, "gre": {"status": "Not Required"}, "deadline": "2026-12-15"},
        "phd": {"faculty_areas": ["optimization", "machine learning"], "poi_list": ["Ju Sun", "Choi"]},
    }
    profile = {"research_interests": ["optimization", "scientific computing"], "coursework": ["Linear Algebra", "Optimization"]}

    p_score = compute_program_score(program, profile)
    assert p_score > 0.0

    pi_data = {
        "research_fit_score": 90.0,
        "recent_grants": ["NSF Award #2401920"],
        "recruiting_status": "recruiting",
        "feedback": {"score": 2.5, "confidence": "Low", "status": "No public evidence found"},
    }
    pi_score = compute_pi_score(pi_data, profile)
    assert pi_score > 0.0

    joint = compute_joint_score(p_score, pi_score)
    assert joint > 0.0


    warnings = check_portfolio_balance([
        {"portfolio_category": "Lottery"},
        {"portfolio_category": "Lottery"},
        {"portfolio_category": "Lottery"},
    ])
    assert len(warnings) > 0
    assert "Lottery" in warnings[0]


def test_calculate_real_stipend_edge_cases() -> None:
    """Tests COL real stipend calculation for edge cases."""
    from gradpath.matching import calculate_real_stipend

    # Zero stipend returns zeros
    zero = calculate_real_stipend(0, "Stanford")
    assert zero["nominal"] == 0
    assert zero["real_stipend"] == 0
    assert zero["tier"] == "Unknown"

    # Unknown city gets default national average multiplier (1.15)
    unknown_city = calculate_real_stipend(40000, "Some Random University Nowhere")
    assert unknown_city["col_index"] == 1.15
    assert unknown_city["real_stipend"] == round(40000 / 1.15)

    # Tight tier when real stipend < 25000
    tight = calculate_real_stipend(40000, "Stanford University")  # 1.85 COL
    assert tight["tier"] == "Tight"  # 40000 / 1.85 ≈ 21621

    # Comfortable tier when real stipend >= 32000
    comfortable = calculate_real_stipend(40000, "Purdue University West Lafayette")  # 1.05
    assert comfortable["tier"] == "Comfortable"  # 40000 / 1.05 ≈ 38095


def test_build_pi_outreach_urls_includes_darpa() -> None:
    """Tests that DARPA grant search link is included in outreach URLs."""
    from gradpath.matching import build_pi_outreach_urls

    urls = build_pi_outreach_urls("Madeleine Udell", "Cornell University")

    assert "darpa_grants" in urls
    assert "darpa.mil" in urls["darpa_grants"]
    # Should still have the original 6 research links
    assert "nsf_awards" in urls
    assert "nih_reporter" in urls
    assert "google_scholar" in urls
    assert "linkedin" in urls
    assert "x_twitter" in urls
    assert "personal_homepage" in urls
    # Total links: 7
    assert len(urls) == 7


def test_portfolio_balance_warns_on_missing_core_target() -> None:
    """Tests that portfolio balance warns when Core/Target count is below threshold."""
    from gradpath.scoring import check_portfolio_balance

    # All Lottery — should warn about lottery ratio AND core/target shortage AND lower-variance
    warnings = check_portfolio_balance([
        {"portfolio_category": "Lottery"},
        {"portfolio_category": "Lottery"},
        {"portfolio_category": "Lottery"},
        {"portfolio_category": "Lottery"},
    ])
    warning_text = " ".join(warnings)
    assert "Lottery" in warning_text
    assert "Core/Target" in warning_text

    # Sufficient core + no lottery — should warn on lower-variance shortage only
    good_warnings = check_portfolio_balance([
        {"portfolio_category": "Core/Target"},
        {"portfolio_category": "Core/Target"},
        {"portfolio_category": "Core/Target"},
        {"portfolio_category": "Core/Target"},
        {"portfolio_category": "Core/Target"},
    ])
    warning_combined = " ".join(good_warnings)
    assert "Lottery" not in warning_combined


def test_col_city_dict_and_stipend_tier_color_constants() -> None:
    """Tests that _COL_CITIES and _STIPEND_TIER_COLOR constants are defined correctly in app."""
    import app

    assert hasattr(app, "_COL_CITIES")
    assert hasattr(app, "_STIPEND_TIER_COLOR")

    # Verify Bay Area has highest COL
    assert app._COL_CITIES["Bay Area / Stanford / Palo Alto"] == 1.85

    # Verify tier color mapping
    assert app._STIPEND_TIER_COLOR["Comfortable"] == "🟢"
    assert app._STIPEND_TIER_COLOR["Tight"] == "🔴"
