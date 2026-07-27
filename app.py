from __future__ import annotations

from typing import Any

import pandas as pd

try:
    import streamlit as st
except ModuleNotFoundError:
    class _MissingStreamlit:
        def set_page_config(self, **_: Any) -> None:
            return None

        def __getattr__(self, name: str) -> Any:
            raise RuntimeError(
                "Streamlit is required to run the GradPath UI. "
                "Install project dependencies, then run `python -m streamlit run app.py`."
            )

    st = _MissingStreamlit()

from gradpath.ai_extract import (
    extract_profile_with_ai,
    extract_program_with_ai,
    normalize_transcript_with_ai,
    openai_available,
    test_openai_connection,
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
    build_pi_outreach_urls,
    build_pi_peer_review_urls,
    evaluate_pi_mentorship_flags,
    normalize_matching_profile,
    pi_hiring_signal,
)
from gradpath.profile_import import (
    extract_text_from_upload,
    profile_from_text,
    profile_review_rows,
)
from gradpath.research_agent import (
    DeepResearchRequest,
    enrich_seeded_programs,
    run_deep_research,
)
from gradpath.school_research import (
    candidate_urls_from_text,
    extract_program_from_text,
    fetch_page_text,
    search_school_candidates,
)
from gradpath.transcript_import import (
    apply_transcript_to_profile,
    transcript_from_upload,
    transcript_review_rows,
)
from gradpath.persistence import get_pi_note, load_workspace, save_workspace, set_pi_note
from gradpath.ui.theme import CUSTOM_CSS, render_category_badge, render_kpi_card

st.set_page_config(
    page_title="GradPath Planner",
    page_icon="GP",
    layout="wide",
    initial_sidebar_state="expanded",
)


PALETTE_CSS = """
<style>
    :root {
        --gp-bg: #f7f5ef;
        --gp-panel: #ffffff;
        --gp-text: #1f2933;
        --gp-muted: #667085;
        --gp-accent: #2f6f73;
        --gp-accent-2: #d94b45;
        --gp-success: #407a52;
        --gp-warning: #b7791f;
        --gp-risk: #b45252;
        --gp-border: #d9d6cc;
        --gp-soft: #fbfaf7;
    }
    .stApp { background: var(--gp-bg); color: var(--gp-text); }
    .stMainBlockContainer {
        max-width: 1500px;
        padding-top: 5rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4,
    .stApp p, .stApp li, .stApp label,
    .stApp div[data-testid="stMarkdownContainer"] {
        color: var(--gp-text);
    }
    .stApp div[data-testid="stCaptionContainer"],
    .stApp small {
        color: var(--gp-muted);
    }
    section[data-testid="stSidebar"] {
        background: #262832;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p {
        color: #f5f5f0;
    }
    section[data-testid="stSidebar"] div[data-testid="stCaptionContainer"],
    section[data-testid="stSidebar"] small {
        color: #d7dae2;
        opacity: 1;
    }
    section[data-testid="stSidebar"] div.stButton > button,
    section[data-testid="stSidebar"] div.stButton > button *,
    section[data-testid="stSidebar"] button {
        background: #f8fafc;
        border-color: #f8fafc;
        color: #111827;
        fill: #111827;
        opacity: 1;
        font-weight: 800;
    }
    section[data-testid="stSidebar"] div.stButton > button:hover,
    section[data-testid="stSidebar"] button:hover {
        background: #e6f2f1;
        border-color: #8bb7b5;
        color: #111827;
    }
    section[data-testid="stSidebar"] div.stButton > button:disabled,
    section[data-testid="stSidebar"] button:disabled,
    section[data-testid="stSidebar"] button:disabled * {
        background: #e5e7eb;
        border-color: #e5e7eb;
        color: #111827;
        fill: #111827;
        opacity: 1;
    }
    div[data-testid="stMetric"] {
        background: var(--gp-panel);
        border: 1px solid var(--gp-border);
        border-radius: 8px;
        padding: 14px 16px;
        box-shadow: 0 1px 3px rgba(31, 41, 51, 0.06);
    }
    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] p,
    div[data-testid="stMetric"] div {
        color: var(--gp-text);
        opacity: 1;
    }
    .gp-card {
        background: var(--gp-panel);
        border: 1px solid var(--gp-border);
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 12px;
    }
    .gp-section {
        background: rgba(255, 255, 255, 0.86);
        border: 1px solid var(--gp-border);
        border-radius: 8px;
        padding: 18px 20px;
        margin: 14px 0;
        box-shadow: 0 1px 4px rgba(31, 41, 51, 0.05);
    }
    .gp-section-title {
        font-size: 1.02rem;
        line-height: 1.2;
        font-weight: 800;
        color: var(--gp-text);
        margin-bottom: 2px;
    }
    .gp-section-caption {
        color: var(--gp-muted);
        margin-bottom: 14px;
        font-size: 0.92rem;
    }
    .gp-workflow {
        background: #eef6f5;
        border: 1px solid #c9dfdd;
        border-radius: 8px;
        color: var(--gp-text);
        padding: 10px 14px;
        margin: 16px 0 20px;
        font-weight: 650;
    }
    .gp-workflow span {
        color: var(--gp-accent);
    }
    .gp-pill {
        display: inline-block;
        border: 1px solid var(--gp-border);
        border-radius: 999px;
        padding: 2px 10px;
        margin: 2px 4px 2px 0;
        font-size: 0.83rem;
        background: #fbfaf7;
    }
    .gp-strong { color: var(--gp-success); font-weight: 700; }
    .gp-good { color: var(--gp-accent); font-weight: 700; }
    .gp-review { color: var(--gp-warning); font-weight: 700; }
    .gp-risk { color: var(--gp-risk); font-weight: 700; }
    .gp-muted { color: var(--gp-muted); }
    .stMain div.stButton > button,
    .stMain div[data-testid="stFormSubmitButton"] button,
    .stMain div[data-testid="stDownloadButton"] button,
    .stMain div[data-testid="stFileUploader"] button {
        background: #ffffff;
        border: 1px solid var(--gp-border);
        color: var(--gp-text);
        box-shadow: 0 1px 2px rgba(31, 41, 51, 0.05);
        font-weight: 750;
        opacity: 1;
    }
    .stMain div.stButton > button *,
    .stMain div[data-testid="stFormSubmitButton"] button *,
    .stMain div[data-testid="stDownloadButton"] button *,
    .stMain div[data-testid="stFileUploader"] button * {
        color: inherit;
        fill: currentColor;
        opacity: 1;
    }
    .stMain div.stButton > button:hover,
    .stMain div[data-testid="stFormSubmitButton"] button:hover,
    .stMain div[data-testid="stDownloadButton"] button:hover,
    .stMain div[data-testid="stFileUploader"] button:hover {
        border-color: var(--gp-accent);
        background: #eef6f5;
        color: var(--gp-text);
    }
    .stMain div.stButton > button[kind="primary"],
    .stMain div[data-testid="stFormSubmitButton"] button[kind="primary"] {
        background: var(--gp-accent);
        border-color: var(--gp-accent);
        color: #ffffff;
    }
    .stMain div.stButton > button[kind="primary"]:hover,
    .stMain div[data-testid="stFormSubmitButton"] button[kind="primary"]:hover {
        background: #285f62;
        border-color: #285f62;
        color: #ffffff;
    }
    .stMain div.stButton > button:disabled,
    .stMain div[data-testid="stFormSubmitButton"] button:disabled,
    .stMain div[data-testid="stFileUploader"] button:disabled {
        background: #f3f1eb;
        border-color: var(--gp-border);
        color: #667085;
        opacity: 1;
    }
    .stMain div[data-testid="stFileUploader"] section {
        background: #ffffff;
        border: 1px dashed var(--gp-border);
        color: var(--gp-text);
    }
    .stMain div[data-testid="stFileUploader"] section *,
    .stMain div[data-testid="stFileUploader"] small {
        color: var(--gp-text);
        opacity: 1;
    }
    div[data-baseweb="tab-list"] {
        border-bottom: 1px solid var(--gp-border);
        gap: 10px;
    }
    button[data-baseweb="tab"] p {
        color: var(--gp-text);
        font-weight: 750;
    }
    button[data-baseweb="tab"][aria-selected="true"] p {
        color: var(--gp-accent-2);
    }
    .stMain div[data-baseweb="input"],
    .stMain div[data-baseweb="base-input"],
    .stMain div[data-baseweb="select"] > div,
    .stMain textarea {
        background-color: #ffffff;
        border-color: var(--gp-border);
    }
    .stMain div[data-baseweb="input"] input,
    .stMain div[data-baseweb="input"] input[type="number"],
    .stMain div[data-baseweb="input"] button,
    .stMain div[data-baseweb="input"] svg,
    .stMain div[data-baseweb="select"] div,
    .stMain div[data-baseweb="select"] span,
    .stMain div[data-baseweb="select"] input,
    .stMain div[data-baseweb="select"] svg,
    .stMain textarea {
        color: var(--gp-text);
        fill: var(--gp-text);
        caret-color: var(--gp-text);
        opacity: 1;
    }
    .stMain div[data-baseweb="input"] input::placeholder,
    .stMain textarea::placeholder {
        color: var(--gp-muted);
        opacity: 1;
    }
    .stMain div[data-baseweb="input"] button {
        background-color: #ffffff;
        border-left: 1px solid var(--gp-border);
    }
    .stMain div[data-baseweb="base-input"] {
        background-color: #ffffff;
    }
    .stMain div[data-testid="stNumberInputContainer"] button,
    .stMain div[data-testid="stNumberInputContainer"] button * {
        background-color: #ffffff;
        color: var(--gp-text);
        fill: var(--gp-text);
        opacity: 1;
    }
    .stMain div[data-baseweb="tag"] {
        background-color: var(--gp-accent-2);
    }
    .stMain div[data-baseweb="tag"] span {
        color: #ffffff;
    }
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
    section[data-testid="stSidebar"] div[data-baseweb="input"] {
        background-color: #11151c;
        border-color: #d9d6cc;
    }
    section[data-testid="stSidebar"] div[data-baseweb="select"] span,
    section[data-testid="stSidebar"] div[data-baseweb="select"] div,
    section[data-testid="stSidebar"] div[data-baseweb="select"] input,
    section[data-testid="stSidebar"] div[data-baseweb="select"] svg,
    section[data-testid="stSidebar"] div[data-baseweb="input"] input,
    section[data-testid="stSidebar"] div[data-baseweb="input"] button,
    section[data-testid="stSidebar"] div[data-baseweb="input"] svg {
        color: #f5f5f0;
        fill: #f5f5f0;
        caret-color: #f5f5f0;
        opacity: 1;
    }
    section[data-testid="stSidebar"] div[data-baseweb="select"] input::placeholder,
    section[data-testid="stSidebar"] div[data-baseweb="input"] input::placeholder {
        color: #f5f5f0;
        opacity: 1;
    }
    section[data-testid="stSidebar"] div[data-baseweb="tag"] {
        background-color: #e65a55;
    }
    section[data-testid="stSidebar"] div[data-baseweb="tag"],
    section[data-testid="stSidebar"] div[data-baseweb="tag"] span,
    section[data-testid="stSidebar"] div[data-baseweb="tag"] svg {
        color: #ffffff;
        fill: #ffffff;
        opacity: 1;
    }
    h1, h2, h3 { letter-spacing: 0; }
</style>
"""


FIELD_OPTIONS = [
    "Computer Science",
    "Data Science",
    "Operations Research",
    "Applied Math",
    "Statistics",
]
COURSE_OPTIONS = [
    "Programming",
    "Data Structures",
    "Algorithms",
    "Linear Algebra",
    "Probability/Statistics",
    "Optimization",
    "Databases",
    "Machine Learning",
    "Deep Learning",
    "Natural Language Processing",
    "Numerical Analysis",
    "Regression",
    "Software Design",
    "Operating Systems",
]
EXPERIENCE_OPTIONS = [
    "Research",
    "Internship",
    "Projects",
    "Publication",
    "Teaching/TA",
    "Leadership",
]


def init_state() -> None:
    workspace = load_workspace()
    if "workspace" not in st.session_state:
        st.session_state.workspace = workspace
    if "profile" not in st.session_state:
        saved_profile = workspace.get("profile")
        st.session_state.profile = saved_profile if saved_profile else default_profile()
    if "slider_weights" not in st.session_state:
        st.session_state.slider_weights = workspace.get(
            "custom_slider_weights",
            {
                "research_fit": 0.35,
                "evidence_fit": 0.20,
                "letter_fit": 0.15,
                "route_fit": 0.15,
                "practical_feasibility": 0.15,
            },
        )
    if "selected_program_ids" not in st.session_state:
        st.session_state.selected_program_ids = []
    if "imported_profile_draft" not in st.session_state:
        st.session_state.imported_profile_draft = None
    if "live_programs" not in st.session_state:
        st.session_state.live_programs = workspace.get("live_programs", [])
    if "research_log" not in st.session_state:
        st.session_state.research_log = workspace.get("research_logs", [])
    if "extraction_warnings" not in st.session_state:
        st.session_state.extraction_warnings = []
    if "openai_api_status" not in st.session_state:
        st.session_state.openai_api_status = None
    if "deep_research_results" not in st.session_state:
        st.session_state.deep_research_results = []
    if "deep_research_log" not in st.session_state:
        st.session_state.deep_research_log = []
    if "deep_research_status" not in st.session_state:
        st.session_state.deep_research_status = ""
    if "deep_search_strategy" not in st.session_state:
        st.session_state.deep_search_strategy = ""
    if "latest_research_set_id" not in st.session_state:
        st.session_state.latest_research_set_id = ""
    if "transcript_draft" not in st.session_state:
        st.session_state.transcript_draft = None
    if "transcript_notes" not in st.session_state:
        st.session_state.transcript_notes = []
    if "source_mode" not in st.session_state:
        st.session_state.source_mode = "Discovered programs"


def render_source_mode() -> str:
    return st.radio(
        "Program source mode",
        ["Discovered programs", "Discovered + manual", "Include sample seeded programs"],
        key="source_mode",
        horizontal=True,
        help="Samples stay hidden by default so recommendations come from AI/web discovery.",
    )


def active_programs(
    seeded_programs: list[dict[str, Any]],
    live_programs: list[dict[str, Any]],
    source_mode: str,
) -> list[dict[str, Any]]:
    discovered = [
        program
        for program in live_programs
        if program.get("program_source") in {"Deep Research", "AI Enriched Sample"}
    ]
    manual = [
        program
        for program in live_programs
        if program.get("program_source") == "Manual URL"
    ]
    if source_mode == "Include sample seeded programs":
        return [*discovered, *manual, *seeded_programs]
    if source_mode == "Discovered + manual":
        return [*discovered, *manual]
    return discovered


def render_header(results: pd.DataFrame, source_mode: str) -> None:
    st.markdown(
        f"""
        <div class="gp-main-header">
            <h1 class="gp-main-title">GradPath Planner</h1>
            <div class="gp-main-subtitle">GPT-Assisted Graduate Matching Workspace • Showing: {source_mode}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    active_phd = (
        int((results["Degree"].eq("PhD") & results["Status"].eq("Active")).sum())
        if not results.empty and {"Degree", "Status"}.issubset(results.columns)
        else 0
    )
    ms_backups = (
        int(results["Track"].eq("MS/job").sum())
        if not results.empty and "Track" in results.columns
        else 0
    )
    sprint_count = (
        int(results["Category"].eq("衝刺").sum())
        if not results.empty and "Category" in results.columns
        else 0
    )
    action_count = (
        int(results["Next Action"].astype(str).ne("").sum())
        if not results.empty and "Next Action" in results.columns
        else 0
    )

    kpi_html = f"""
    <div class="gp-kpi-container">
        {render_kpi_card("Programs Tracked", len(results), "Target pool size")}
        {render_kpi_card("Active PhD Routes", active_phd, "Target: 20-25")}
        {render_kpi_card("MS / Job Backups", ms_backups, "Target: 6-10")}
        {render_kpi_card("Next Actions Required", action_count, f"{sprint_count} Reach/Sprint programs")}
    </div>
    """
    st.markdown(kpi_html, unsafe_allow_html=True)


def _comma_list(value: list[str] | str) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value)


def _split_commas(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _evidence_to_text(evidence: Any) -> str:
    if isinstance(evidence, dict):
        lines = []
        for key, value in evidence.items():
            if isinstance(value, list):
                lines.append(f"{key}: " + "; ".join(str(item) for item in value))
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)
    if isinstance(evidence, list):
        return "\n".join(str(item) for item in evidence)
    return str(evidence)


def _text_to_evidence(text: str) -> dict[str, list[str]]:
    evidence: dict[str, list[str]] = {}
    for line in [item.strip() for item in text.splitlines() if item.strip()]:
        if ":" in line:
            key, value = line.split(":", maxsplit=1)
            evidence[key.strip()] = [item.strip() for item in value.split(";") if item.strip()]
        else:
            evidence.setdefault("notes", []).append(line)
    return evidence


def _mapping_to_text(mapping: Any) -> str:
    if isinstance(mapping, dict):
        return "\n".join(f"{key}: {value}" for key, value in mapping.items())
    return str(mapping)


def _text_to_mapping(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in [item.strip() for item in text.splitlines() if item.strip()]:
        if ":" in line:
            key, value = line.split(":", maxsplit=1)
            values[key.strip()] = value.strip()
    return values


def profile_form() -> dict[str, Any]:
    profile = normalize_matching_profile(dict(st.session_state.profile))
    with st.form("profile_form"):
        with st.container(border=True):
            section_header(
                "Goal, Fields & Narrative",
                "The matcher uses this research story before it thinks about prestige.",
            )
            left, right = st.columns([1, 2])
            with left:
                profile["target_degree"] = st.radio(
                    "Target degree", ["Both", "MS", "PhD"], horizontal=True, index=0
                )
                profile["gpa"] = st.number_input(
                    "GPA", min_value=0.0, max_value=4.0, value=profile["gpa"]
                )
            with right:
                profile["target_fields"] = st.multiselect(
                    "Target fields", FIELD_OPTIONS, default=profile["target_fields"]
                )
                profile["primary_tags"] = _split_commas(
                    st.text_input(
                        "Primary tags",
                        value=_comma_list(profile.get("primary_tags", [])),
                        help="Highest-weight research identity used for POI and route matching.",
                    )
                )
                profile["secondary_tags"] = _split_commas(
                    st.text_input(
                        "Secondary tags",
                        value=_comma_list(profile.get("secondary_tags", [])),
                        help="Useful applied contexts that can strengthen a route.",
                    )
                )

        with st.container(border=True):
            section_header(
                "Scores",
                "Keep placeholders until official TOEFL/IELTS/GRE scores are ready.",
            )
            score_left, score_mid, score_right = st.columns(3)
            with score_left:
                profile["english_test"] = st.selectbox(
                    "English test", ["TOEFL", "IELTS", "Duolingo"], index=0
                )
            with score_mid:
                profile["english_score"] = st.number_input(
                    "English score", min_value=0, max_value=180, value=profile["english_score"]
                )
            with score_right:
                profile["gre_status"] = st.selectbox(
                    "GRE status", ["Planning", "Scheduled", "Completed", "Not taking"], index=0
                )
                profile["gre_quant"] = st.number_input(
                    "GRE Quant", min_value=130, max_value=170, value=profile["gre_quant"]
                )

        with st.container(border=True):
            section_header(
                "Preferences",
                "Use these to surface funding-sensitive and region-compatible programs.",
            )
            pref_left, pref_mid, pref_right = st.columns(3)
            with pref_left:
                profile["preferred_regions"] = st.multiselect(
                    "Preferred regions",
                    ["United States", "Canada", "United Kingdom", "Europe"],
                    default=profile["preferred_regions"],
                )
            with pref_mid:
                profile["funding_need"] = st.selectbox(
                    "Funding need", ["Flexible", "Important", "Critical"], index=1
                )
            with pref_right:
                profile["orientation"] = st.selectbox(
                    "Orientation", ["Career", "Research", "Research + career"], index=2
                )

        with st.container(border=True):
            section_header("Coursework", "Select transcript evidence relevant to prerequisites.")
            profile["coursework"] = st.multiselect(
                "Coursework completed", COURSE_OPTIONS, default=profile["coursework"]
            )

        with st.container(border=True):
            section_header("Experience", "Select evidence the app should use for MS/PhD fit.")
            profile["experience"] = st.multiselect(
                "Experience", EXPERIENCE_OPTIONS, default=profile["experience"]
            )

        with st.container(border=True):
            section_header(
                "Evidence & Research Signal",
                "Keep claims application-safe: in-prep, submitted, or accepted only when true.",
            )
            profile["evidence"] = _text_to_evidence(
                st.text_area(
                    "Evidence",
                    value=_evidence_to_text(profile.get("evidence", {})),
                    height=130,
                    help="Format each line as label: item; item; item.",
                )
            )
            interests = st.text_input(
                "Research interests",
                value=", ".join(profile["research_interests"]),
                help="Comma-separated topics used for PhD research/faculty matching.",
            )
            profile["research_interests"] = [
                item.strip() for item in interests.split(",") if item.strip()
            ]
            profile["career_goal"] = st.text_input("Career goal", value=profile["career_goal"])
            profile["sop_notes"] = st.text_area("SOP notes", value=profile["sop_notes"], height=90)

        with st.container(border=True):
            section_header(
                "Tests & Recommenders",
                "These drive feasibility and letter-fit calibration for each department route.",
            )
            tleft, tright = st.columns(2)
            with tleft:
                profile["test_strategy"] = _text_to_mapping(
                    st.text_area(
                        "Test strategy",
                        value=_mapping_to_text(profile.get("test_strategy", {})),
                        height=130,
                    )
                )
            with tright:
                profile["recommenders"] = _text_to_mapping(
                    st.text_area(
                        "Recommender contexts",
                        value=_mapping_to_text(profile.get("recommenders", {})),
                        height=130,
                    )
                )

        submitted = st.form_submit_button("Update profile", type="primary")
        if submitted:
            st.session_state.profile = profile
            st.success("Profile updated.")
    return st.session_state.profile


def section_header(title: str, caption: str) -> None:
    st.markdown(
        f"""
        <div class="gp-section">
            <div class="gp-section-title">{title}</div>
            <div class="gp-section-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_readiness(profile: dict[str, Any]) -> None:
    profile = normalize_matching_profile(profile)
    course_ratio = len(profile["coursework"]) / len(COURSE_OPTIONS)
    research_depth = "High" if "Research" in profile["experience"] else "Developing"
    evidence_count = sum(
        len(value) if isinstance(value, list) else 1
        for value in profile.get("evidence", {}).values()
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Primary tags", len(profile.get("primary_tags", [])))
    c2.metric("Evidence items", evidence_count)
    c3.metric("Coursework", f"{course_ratio:.0%}")
    c4.metric("Research depth", research_depth)


def render_filters(programs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    countries = ["All", *sorted({program["country"] for program in programs})]
    confidences = ["All", *sorted({program["source"]["confidence"] for program in programs})]
    admit_bands = [
        "All",
        "Likely-ish",
        "Target",
        "Reach",
        "High Reach",
        "Needs More Evidence",
    ]
    with st.sidebar:
        st.header("Result Filters")
        st.caption("Filters only change program results, not your applicant profile.")
        if st.button("Clear filters"):
            for key, value in {
                "filter_degree": "All",
                "filter_fields": [],
                "filter_country": "All",
                "filter_funding": "Any",
                "filter_deadline": "Any",
                "filter_source": "All",
                "filter_confidence": "All",
                "filter_admit": "All",
                "filter_latest": False,
            }.items():
                st.session_state[key] = value
            st.rerun()
        degree = st.selectbox("Degree", ["All", "MS", "PhD"], key="filter_degree")
        fields = st.multiselect("Field", FIELD_OPTIONS, default=[], key="filter_fields")
        country = st.selectbox("Region", countries, key="filter_country")
        funding = st.selectbox(
            "Funding", ["Any", "Funded/assistantship visible"], key="filter_funding"
        )
        deadline_window = st.selectbox(
            "DDL window",
            ["Any", "Next 60 days", "Next 120 days", "Future only"],
            key="filter_deadline",
        )
        program_source = st.selectbox(
            "Program source",
            ["All", "Seeded", "Deep Research", "Manual URL", "AI Enriched Sample"],
            key="filter_source",
        )
        confidence = st.selectbox("Confidence", confidences, key="filter_confidence")
        admit_band = st.selectbox("Admit band", admit_bands, key="filter_admit")
        only_researched = st.checkbox(
            "Only researched this session",
            value=False,
            key="filter_latest",
        )
    filtered = filter_programs(
        programs,
        degree,
        fields,
        country,
        funding,
        deadline_window,
        program_source,
        confidence,
        admit_band,
        st.session_state.latest_research_set_id,
        only_researched,
    )
    with st.sidebar:
        st.caption(f"{len(filtered)} of {len(programs)} programs visible")
    return filtered


def band_class(band: str) -> str:
    return {
        "Strong": "gp-strong",
        "Good": "gp-good",
        "Needs Review": "gp-review",
        "Risky": "gp-risk",
    }.get(band, "gp-muted")


def render_program_detail(program: dict[str, Any], row: dict[str, Any]) -> None:
    st.subheader(f"{program['school']} - {program['program']}")
    category = row.get("Category", row.get("Fit", "Needs Review"))
    score = row.get("Overall Score", row.get("Score", 0))
    st.markdown(
        f"<span class='{band_class(row.get('Fit', 'Needs Review'))}'>{category}</span> "
        f"<span class='gp-muted'>Overall score {score}/100</span>",
        unsafe_allow_html=True,
    )
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Research", row.get("Research Fit Score", 0))
    m2.metric("Evidence", row.get("Evidence Fit Score", 0))
    m3.metric("Letters", row.get("Letter Fit Score", 0))
    m4.metric("Route", row.get("Route Fit Score", 0))
    m5.metric("Feasibility", row.get("Feasibility Score", 0))
    detail_cols = st.columns(3)
    detail_cols[0].markdown(
        card("POI Fit", row.get("POI Fit", row.get("Research Fit", ""))),
        unsafe_allow_html=True,
    )
    detail_cols[1].markdown(
        card("Risk Note", row.get("Risk Note", row.get("Missing", ""))),
        unsafe_allow_html=True,
    )
    detail_cols[2].markdown(
        card("Next Action", row.get("Next Action", row.get("Actions", ""))),
        unsafe_allow_html=True,
    )
    st.markdown(
        card(
            "Letter + Research Signal",
            "<br>".join(
                [
                    row.get("Letter Strategy", ""),
                    row.get("Research Signal", ""),
                    row.get("Balance Note", ""),
                ]
            ),
        ),
        unsafe_allow_html=True,
    )
    if program.get("admit_confidence"):
        admit = program["admit_confidence"]
        st.markdown(
            card(
                "Admit Confidence Estimate",
                f"{admit['band']} ({admit['score']}/100): {admit['why']}",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("**Official Requirements**")
    req_cols = st.columns(4)
    reqs = program["requirements"]
    req_cols[0].markdown(card("English", reqs["english"]["summary"]), unsafe_allow_html=True)
    req_cols[1].markdown(card("GRE", reqs["gre"]["summary"]), unsafe_allow_html=True)
    req_cols[2].markdown(card("Coursework", ", ".join(reqs["coursework"])), unsafe_allow_html=True)
    req_cols[3].markdown(card("DDL", reqs["deadline"]), unsafe_allow_html=True)

    pref_cols = st.columns(4)
    pref = program["preferences"]
    pref_cols[0].markdown(card("SOP", pref["sop"]), unsafe_allow_html=True)
    pref_cols[1].markdown(card("Preference", pref["program"]), unsafe_allow_html=True)
    pref_cols[2].markdown(card("Experience", ", ".join(pref["experience"])), unsafe_allow_html=True)
    pref_cols[3].markdown(
        card("Funding / Research Fit", f"{pref['funding']}<br>{program['phd']['research_fit']}"),
        unsafe_allow_html=True,
    )

    st.markdown(card("Suggested SOP Angle", row.get("SOP Angle", "")), unsafe_allow_html=True)
    st.markdown("**Unofficial / Community Signals**")
    community = program.get("community_summary", {})
    st.warning("Unofficial evidence is not official admissions policy; verify manually.")
    st.markdown(
        card(
            "Community Summary",
            community.get("summary", "No unofficial community evidence collected."),
        ),
        unsafe_allow_html=True,
    )
    cpub, cres = st.columns(2)
    cpub.markdown(
        card(
            "Publication / Research Expectation",
            community.get("publication_expectation", "No unofficial publication signal yet."),
        ),
        unsafe_allow_html=True,
    )
    cres.markdown(
        card(
            "Application Preference Inference",
            community.get("research_expectation", "No unofficial research signal yet."),
        ),
        unsafe_allow_html=True,
    )
    evidence = program.get("unofficial_evidence", [])
    if evidence:
        st.dataframe(pd.DataFrame(evidence), width="stretch", hide_index=True)
    else:
        st.caption("No public forum/community signals collected for this program yet.")
    st.markdown("**Next Fit Plan**")
    plan = program.get("next_fit_plan", {})
    if plan:
        fit_cols = st.columns(2)
        fit_cols[0].markdown(
            card(
                "Requirements / Coursework",
                "<br>".join(
                    [
                        "Missing: " + "; ".join(plan.get("missing_requirements", [])),
                        "Coursework: " + "; ".join(plan.get("recommended_coursework", [])),
                    ]
                ),
            ),
            unsafe_allow_html=True,
        )
        fit_cols[1].markdown(
            card(
                "Research / Positioning",
                "<br>".join(
                    [
                        "Actions: " + "; ".join(plan.get("research_actions", [])),
                        "Projects: " + plan.get("publication_project_positioning", ""),
                    ]
                ),
            ),
            unsafe_allow_html=True,
        )
        st.markdown(card("SOP Angle", plan.get("sop_angle", "")), unsafe_allow_html=True)
        st.markdown(
            card("Faculty Contact", plan.get("faculty_contact", "")),
            unsafe_allow_html=True,
        )
    else:
        st.caption("No next fit plan generated yet. Run AI Deep Search or seeded enrichment.")
    source = program["source"]
    st.markdown(
        f"Source: [{source['url']}]({source['url']}) | Retrieved: `{source['retrieved_at']}` "
        f"| Confidence: `{source['confidence']}`"
    )


def card(title: str, body: str) -> str:
    return f"<div class='gp-card'><strong>{title}</strong><br><span>{body}</span></div>"


def program_by_id(programs: list[dict[str, Any]], program_id: str) -> dict[str, Any] | None:
    return next((program for program in programs if program["id"] == program_id), None)


def _append_unique_warning(message: str) -> None:
    if message not in st.session_state.extraction_warnings:
        st.session_state.extraction_warnings.append(message)


def _extend_research_log(candidates: list[dict[str, str]]) -> list[dict[str, str]]:
    existing_urls = {item["url"] for item in st.session_state.research_log}
    added = []
    for candidate in candidates:
        if candidate["url"] in existing_urls:
            continue
        st.session_state.research_log.append(candidate)
        existing_urls.add(candidate["url"])
        added.append(candidate)
    return added


def render_import_profile_tab() -> None:
    st.subheader("Import Profile")
    st.write("Upload a PDF, TXT, or TEX CV, review extracted fields, then apply them.")
    uploaded = st.file_uploader("CV or resume", type=["pdf", "txt", "tex"])
    use_ai = st.checkbox(
        "Use AI extraction when OPENAI_API_KEY is available",
        value=openai_available(),
        disabled=not openai_available(),
    )
    if not openai_available():
        st.info("No OPENAI_API_KEY found. The importer will use rule-based extraction.")

    if uploaded and st.button("Extract profile", type="primary"):
        try:
            raw_text = extract_text_from_upload(uploaded.name, uploaded.getvalue())
            draft = profile_from_text(raw_text, st.session_state.profile)
            note = "Rule-based extraction completed."
            if use_ai:
                draft, note = extract_profile_with_ai(raw_text, draft)
            st.session_state.imported_profile_draft = draft
            st.session_state.extraction_warnings.append(note)
        except Exception as exc:
            st.error(f"Could not extract this CV: {exc}")

    draft = st.session_state.imported_profile_draft
    if draft:
        st.markdown("**Review extracted profile**")
        st.dataframe(pd.DataFrame(profile_review_rows(draft)), width="stretch", hide_index=True)
        if st.button("Apply imported profile"):
            st.session_state.profile = draft
            st.success("Imported profile applied. Match Board scores will use the updated profile.")

    if st.session_state.extraction_warnings:
        st.markdown("**Extraction notes**")
        for warning in st.session_state.extraction_warnings[-5:]:
            st.caption(warning)

    st.divider()
    st.subheader("Import Transcript")
    st.write("Upload an unofficial transcript PDF/TXT to extract coursework evidence.")
    transcript = st.file_uploader(
        "Unofficial transcript",
        type=["pdf", "txt"],
        key="transcript_upload",
    )
    use_transcript_ai = st.checkbox(
        "Use AI to normalize transcript coursework when available",
        value=openai_available(),
        disabled=not openai_available(),
        key="transcript_ai",
    )
    if transcript and st.button("Extract transcript coursework", type="primary"):
        try:
            draft, notes = transcript_from_upload(transcript.name, transcript.getvalue())
            if use_transcript_ai:
                raw_text = extract_text_from_upload(transcript.name, transcript.getvalue())
                draft, ai_note = normalize_transcript_with_ai(raw_text, draft, COURSE_OPTIONS)
                notes.append(ai_note)
            st.session_state.transcript_draft = draft
            st.session_state.transcript_notes = notes
        except Exception as exc:
            st.error(f"Could not extract transcript: {exc}")

    if st.session_state.transcript_draft:
        st.markdown("**Review transcript-derived coursework**")
        st.dataframe(
            pd.DataFrame(transcript_review_rows(st.session_state.transcript_draft)),
            width="stretch",
            hide_index=True,
        )
        if st.button("Apply transcript coursework"):
            st.session_state.profile = apply_transcript_to_profile(
                st.session_state.profile, st.session_state.transcript_draft
            )
            st.success("Transcript coursework applied to applicant profile.")
    if st.session_state.transcript_notes:
        st.markdown("**Transcript notes**")
        for note in st.session_state.transcript_notes[-5:]:
            st.caption(note)


def render_research_schools_tab() -> None:
    st.subheader("Agent Search")
    st.write(
        "GPT searches, extracts, and scores official program evidence with deterministic "
        "matching guardrails."
    )
    api_left, api_right = st.columns([2, 1])
    with api_left:
        if openai_available():
            st.info(
                "OPENAI_API_KEY detected. Use the test button to confirm this app can call it. "
                "Set GRADPATH_OPENAI_MODEL to override the recommended GPT model."
            )
        else:
            st.info(
                "No OPENAI_API_KEY found in this app process. "
                "Rule-based extraction still works."
            )
        status = st.session_state.openai_api_status
        if status:
            status_text = f"{status['message']} Model: `{status['model']}`"
            if status["ok"]:
                st.success(status_text)
            else:
                st.warning(status_text)
    with api_right:
        if st.button("Test OpenAI API"):
            st.session_state.openai_api_status = test_openai_connection()
            st.rerun()

    c1, c2, c3 = st.columns(3)
    with c1:
        target_field = st.selectbox("Target field", FIELD_OPTIONS, index=0)
    with c2:
        degree = st.selectbox("Degree for search", ["MS", "PhD"], index=0)
    with c3:
        max_results = st.number_input("Search results per query", 1, 8, 3)

    with st.container(border=True):
        section_header(
            "Find Best-Fit Programs",
            "Discover programs from online evidence first, then estimate admit confidence.",
        )
        d1, d2, d3 = st.columns(3)
        with d1:
            deep_degree = st.selectbox("Deep degree", ["MS", "PhD"], index=1)
            deep_fields = st.multiselect(
                "Deep fields",
                FIELD_OPTIONS,
                default=st.session_state.profile.get("target_fields", FIELD_OPTIONS[:1])[:2],
            )
        with d2:
            deep_countries = st.multiselect(
                "Preferred countries",
                ["United States", "Canada", "United Kingdom", "Singapore", "Hong Kong"],
                default=st.session_state.profile.get("preferred_regions", ["United States"]),
            )
            ranking_range = st.selectbox(
                "Preferred ranking range",
                ["Balanced", "Top 20", "Top 50", "Broad safety search"],
            )
        with d3:
            recommended_count = st.slider("Recommended schools count", 1, 30, 8)
            search_breadth = st.selectbox("Search breadth", ["Fast", "Balanced", "Deep"], index=1)
            hosted_web_search = st.checkbox(
                "Use hosted OpenAI web search",
                value=False,
                disabled=not openai_available(),
                help=(
                    "Adds Responses API web_search_preview candidates, then falls back "
                    "to local search."
                ),
            )
            deep_funding = st.selectbox(
                "Funding importance",
                ["Flexible", "Important", "Critical"],
                index=["Flexible", "Important", "Critical"].index(
                    st.session_state.profile.get("funding_need", "Important")
                ),
            )
        deep_interests = st.text_input(
            "Research interests for deep search",
            value=", ".join(st.session_state.profile.get("research_interests", [])[:5]),
        )
        deep_seed_schools = st.text_area(
            "Seed schools for deep search",
            height=70,
            placeholder="University of Illinois Urbana-Champaign\nUniversity of Michigan",
        )
        no_ai_panel, ai_panel = st.columns(2)
        with ai_panel:
            st.markdown("**GPT Match Search**")
            st.caption("Primary path: discover programs, extract evidence, and build match rows.")
            if openai_available():
                st.success("OPENAI_API_KEY detected")
            else:
                st.warning("Set OPENAI_API_KEY to enable AI query planning and synthesis.")
            if st.button(
                "Run AI Deep Search",
                type="primary",
                disabled=not openai_available(),
            ):
                _run_deep_search_from_ui(
                    deep_degree,
                    deep_fields or [target_field],
                    deep_countries,
                    ranking_range,
                    deep_funding,
                    deep_interests,
                    deep_seed_schools,
                    int(recommended_count),
                    use_ai=True,
                    ai_mode="AI Deep Search",
                    search_breadth=search_breadth,
                    use_hosted_web_search=hosted_web_search,
                )
        with no_ai_panel:
            st.markdown("**No-AI Search**")
            st.caption("Uses deterministic online queries and rule scoring.")
            if st.button("Run No-AI Search"):
                _run_deep_search_from_ui(
                    deep_degree,
                    deep_fields or [target_field],
                    deep_countries,
                    ranking_range,
                    deep_funding,
                    deep_interests,
                    deep_seed_schools,
                    int(recommended_count),
                    use_ai=False,
                    ai_mode="No-AI Search",
                    search_breadth=search_breadth,
                    use_hosted_web_search=False,
                )
        with st.expander("Optional: Enrich Sample Programs"):
            st.caption(
                "Use this only to benchmark sample seeded records; "
                "not default recommendations."
            )
            if st.button("Enrich Sample Programs With AI", disabled=not openai_available()):
                _enrich_seeded_from_ui(int(recommended_count))

        if st.session_state.deep_research_status:
            st.info(st.session_state.deep_research_status)
            if st.session_state.deep_search_strategy:
                st.caption(f"Search strategy: {st.session_state.deep_search_strategy}")
            st.caption("Open Match Board and choose 'Only latest research run' to inspect it.")
        if st.session_state.deep_research_results:
            st.markdown("**Match Preview**")
            st.dataframe(
                pd.DataFrame(st.session_state.deep_research_results),
                width="stretch",
                hide_index=True,
            )
        if st.session_state.deep_research_log:
            st.markdown("**Deep research log**")
            st.dataframe(
                pd.DataFrame(st.session_state.deep_research_log),
                width="stretch",
                hide_index=True,
            )

    with st.expander("Manual Research Tools"):
        url_text = st.text_area(
            "Official program/admission URLs",
            height=100,
            placeholder="https://department.university.edu/graduate/admissions",
        )
        use_ai = st.checkbox(
            "Use AI to normalize school pages when available",
            value=openai_available(),
            disabled=not openai_available(),
            key="research_ai",
        )
        if st.button("Extract pasted URLs", type="primary"):
            urls = candidate_urls_from_text(url_text)
            if not urls:
                st.warning("Paste at least one official URL.")
            for url in urls:
                _add_program_from_url(url, target_field, degree, use_ai)

        school_text = st.text_area(
            "Schools already in mind",
            height=90,
            placeholder="University of Michigan\nGeorgia Tech\nColumbia University",
        )
        if st.button("Find official-looking URLs"):
            for school in [line.strip() for line in school_text.splitlines() if line.strip()]:
                try:
                    candidates = search_school_candidates(
                        school, target_field, degree, int(max_results)
                    )
                    _extend_research_log(candidates)
                    if not candidates:
                        _append_unique_warning(f"No candidate URLs found for {school}.")
                except Exception as exc:
                    _append_unique_warning(f"Search failed for {school}: {exc}")

    if st.session_state.research_log:
        st.markdown("**Candidate URLs**")
        st.dataframe(pd.DataFrame(st.session_state.research_log), width="stretch", hide_index=True)

    if st.session_state.live_programs:
        st.markdown("**Live extracted programs**")
        live_results = results_dataframe(st.session_state.live_programs, st.session_state.profile)
        st.dataframe(live_results, width="stretch", hide_index=True)

    if st.session_state.extraction_warnings:
        st.markdown("**Research notes**")
        for warning in st.session_state.extraction_warnings[-8:]:
            st.caption(warning)


def render_pi_browser_tab(programs: list[dict[str, Any]]) -> None:
    st.subheader("Professors of Interest (PI) Tracker & Grant Intelligence")
    st.caption("Track faculty members, newly approved NSF/NIH/DARPA grants, hiring signals, and 1-click outreach channels.")

    pi_records = []
    for prog in programs:
        pois = prog.get("phd", {}).get("poi_list", []) or prog.get("matching", {}).get("poi_list", [])
        if isinstance(pois, list):
            for poi in pois:
                if poi and poi not in {"TBD / faculty fit to be refined", "Faculty match under review"}:
                    pi_records.append({
                        "Professor": poi,
                        "University": prog.get("school", ""),
                        "Program": prog.get("program", ""),
                        "Field": prog.get("field", ""),
                        "Research Areas": ", ".join(prog.get("phd", {}).get("faculty_areas", [])),
                    })

    if not pi_records:
        st.info("No Professors of Interest extracted yet. Run Agent Search to populate PIs.")
        return

    df_pi = pd.DataFrame(pi_records).drop_duplicates(subset=["Professor", "University"])
    search_q = st.text_input("Filter PIs by name, university, or research keyword", "", key="pi_search_q")
    if search_q:
        q_low = search_q.lower()
        df_pi = df_pi[df_pi.apply(lambda r: any(q_low in str(v).lower() for v in r), axis=1)]

    st.write(f"Showing **{len(df_pi)}** faculty members across target programs:")
    for _, row in df_pi.iterrows():
        prof_name = row["Professor"]
        uni = row["University"]
        prog_name = row["Program"]
        areas = row["Research Areas"]
        current_note = get_pi_note(st.session_state.workspace, prof_name)
        signal = pi_hiring_signal(prof_name, current_note)
        mentorship = evaluate_pi_mentorship_flags(prof_name, current_note)
        urls = build_pi_outreach_urls(prof_name, uni)
        review_urls = build_pi_peer_review_urls(prof_name, uni)

        with st.expander(f"📌 {prof_name} ({uni}) — {signal['hiring_badge']} | {mentorship['badge']}"):
            st.markdown(f"**University**: {uni} | **Program**: {prog_name}")
            if areas:
                st.markdown(f"**Research Focus**: {areas}")
            st.caption(f"Hiring Signal: {signal['reason']} | Mentorship Status: {mentorship['safety']}")

            st.markdown("**Outreach & Grant Links:**")
            l1, l2, l3, l4, l5, l6 = st.columns(6)
            l1.markdown(f"[🔬 NSF Awards]({urls['nsf_awards']})")
            l2.markdown(f"[🏥 NIH RePORTER]({urls['nih_reporter']})")
            l3.markdown(f"[🎓 Google Scholar]({urls['google_scholar']})")
            l4.markdown(f"[💼 LinkedIn]({urls['linkedin']})")
            l5.markdown(f"[🐦 X / Twitter]({urls['x_twitter']})")
            l6.markdown(f"[🌐 Lab Homepage]({urls['personal_homepage']})")

            st.markdown("**Peer Review & Advisor Safety Screening (Avoid Toxic PIs):**")
            r1, r2, r3, r4 = st.columns(4)
            r1.markdown(f"[💬 RateMyProfessors]({review_urls['ratemyprofessors']})")
            r2.markdown(f"[🗣️ Reddit Peer Feedback]({review_urls['reddit_peer_review']})")
            r3.markdown(f"[⚖️ RateYourPI Search]({review_urls['rateyourpi']})")
            r4.markdown(f"[🎓 Lab Alumni Placements]({review_urls['lab_alumni_placements']})")

            note_input = st.text_area(
                f"Grant Notes, Peer Review & Outreach Status for {prof_name}",
                value=current_note,
                key=f"note_{prof_name}_{uni}",
                placeholder="e.g. Approved NSF Award #240192; Peer reviews positive (supportive 5-yr graduation); Emailed 10/12.",
            )
            if note_input != current_note:
                set_pi_note(st.session_state.workspace, prof_name, note_input)
                save_workspace(st.session_state.workspace)
                st.toast(f"Saved notes for {prof_name}!")


def render_guide_tab() -> None:
    st.subheader("Guide")
    st.markdown(
        """
        **Launch**

        ```bash
        cd "/Users/chenyixin/Documents/Grad School Analysis"
        export OPENAI_API_KEY="your_key_here"
        export GRADPATH_OPENAI_MODEL="gpt-5.5"
        python3 -m streamlit run app.py
        ```

        **Workflow**

        1. Open **Profile Narrative** and review the default research story, evidence,
           test strategy, and recommender contexts.
        2. Open **Import Profile** if you update your CV. Upload `.tex`, `.pdf`, or `.txt`,
           extract, review, then apply the draft.
        3. Open **Agent Search** to discover official program pages and build match rows.
        4. Use the sidebar filters to switch between MS, PhD, fields, regions, funding, and DDL.
        5. Open **Match Board** for ranked results and **Program Detail** for route/risk evidence.
        6. Open **Compare** to inspect 2-4 programs side by side.
        7. Open **Export** to download the reference-shaped CSV or formatted XLSX workbook.

        **Notes**

        - Live extracted school information is marked `Live/Needs Review` or `AI/Needs Review`.
        - The recommended OpenAI model is `gpt-5.5`; override it with
          `GRADPATH_OPENAI_MODEL` only when needed.
        - Research signals should stay conservative: in-prep, submitted, or accepted only
          when that status is accurate at application time.
        - Always verify deadlines, English requirements, GRE policy, funding, and SOP prompts
          on official program pages before applying.
        - Do not put API keys in code. Use environment variables in your terminal.
        """
    )


def _run_deep_search_from_ui(
    degree: str,
    fields: list[str],
    countries: list[str],
    ranking_range: str,
    funding_importance: str,
    interests: str,
    seed_schools: str,
    recommended_count: int,
    use_ai: bool,
    ai_mode: str,
    search_breadth: str,
    use_hosted_web_search: bool,
) -> None:
    next_index = len(st.session_state.live_programs) + 1
    research_set_id = f"{ai_mode.lower().replace(' ', '-')}-{next_index}"
    request = DeepResearchRequest(
        degree=degree,
        fields=fields,
        countries=countries,
        ranking_range=ranking_range,
        funding_importance=funding_importance,
        research_interests=[item.strip() for item in interests.split(",") if item.strip()],
        target_count=recommended_count,
        seed_schools=[line.strip() for line in seed_schools.splitlines() if line.strip()],
        use_ai=use_ai,
        ai_mode=ai_mode,
        research_set_id=research_set_id,
        include_community=True,
        search_breadth=search_breadth,
        use_hosted_web_search=use_hosted_web_search,
    )
    with st.spinner(f"Running {ai_mode} from official and public evidence..."):
        result = run_deep_research(st.session_state.profile, request)
    st.session_state.deep_research_results = result["recommendations"]
    st.session_state.deep_research_log = result["log"]
    st.session_state.deep_research_status = result["status"]
    st.session_state.deep_search_strategy = result["search_strategy"]
    st.session_state.latest_research_set_id = result["research_set_id"]
    for program in result["programs"]:
        _upsert_live_program(program)
    _extend_research_log(result["candidates"])
    st.success(result["status"])


def _enrich_seeded_from_ui(recommended_count: int) -> None:
    with st.spinner("Enriching sample programs with AI and public evidence..."):
        result = enrich_seeded_programs(
            load_programs(),
            st.session_state.profile,
            use_ai=True,
            limit=recommended_count,
        )
    st.session_state.deep_research_results = result["recommendations"]
    st.session_state.deep_research_log = result["log"]
    st.session_state.deep_research_status = result["status"]
    st.session_state.deep_search_strategy = result["search_strategy"]
    st.session_state.latest_research_set_id = result["research_set_id"]
    for program in result["programs"]:
        _upsert_live_program(program)
    st.success(result["status"])


def _add_program_from_url(url: str, target_field: str, degree: str, use_ai: bool) -> None:
    try:
        title, page_text = fetch_page_text(url)
        program = extract_program_from_text(page_text, url, target_field, degree, title)
        note = "Rule-based program extraction completed."
        if use_ai:
            program, note = extract_program_with_ai(page_text, program, url)
        program["program_source"] = "Manual URL"
        _upsert_live_program(program)
        st.session_state.extraction_warnings.append(f"{note} Source: {url}")
    except Exception as exc:
        st.session_state.extraction_warnings.append(f"Could not extract {url}: {exc}")


def _upsert_live_program(program: dict[str, Any]) -> None:
    existing = [item for item in st.session_state.live_programs if item["id"] != program["id"]]
    st.session_state.live_programs = [*existing, program]


def main() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    init_state()
    source_mode = render_source_mode()
    seeded_programs = load_programs()
    programs = active_programs(seeded_programs, st.session_state.live_programs, source_mode)
    all_programs = [*seeded_programs, *st.session_state.live_programs]
    filtered_programs = render_filters(programs)
    results = results_dataframe(
        filtered_programs,
        st.session_state.profile,
        custom_weights=st.session_state.slider_weights,
    )
    render_header(results, source_mode)

    (
        profile_tab,
        import_tab,
        research_tab,
        pi_tab,
        guide_tab,
        explorer_tab,
        detail_tab,
        compare_tab,
        export_tab,
    ) = st.tabs(
        [
            "Profile Narrative",
            "Import Profile",
            "Agent Search",
            "PI Tracker",
            "Guide",
            "Match Board",
            "Program Detail",
            "Compare",
            "Export",
        ]
    )

    with profile_tab:
        st.subheader("Profile Narrative")
        profile = profile_form()
        st.session_state.workspace["profile"] = profile
        save_workspace(st.session_state.workspace)
        render_readiness(profile)

    with import_tab:
        render_import_profile_tab()

    with research_tab:
        render_research_schools_tab()

    with pi_tab:
        render_pi_browser_tab(filtered_programs)

    with guide_tab:
        render_guide_tab()

    with explorer_tab:
        st.subheader("Match Board")
        with st.expander("⚙️ Dynamic Priority Ranker (Custom Weight Sliders)", expanded=False):
            st.caption("Adjust sliders to dynamically re-rank all programs based on your personal preferences.")
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                w_rf = st.slider("Research Fit", 0.0, 1.0, float(st.session_state.slider_weights.get("research_fit", 0.35)), 0.05, key="w_rf")
            with c2:
                w_ef = st.slider("Evidence Fit", 0.0, 1.0, float(st.session_state.slider_weights.get("evidence_fit", 0.20)), 0.05, key="w_ef")
            with c3:
                w_lf = st.slider("Letter Strategy", 0.0, 1.0, float(st.session_state.slider_weights.get("letter_fit", 0.15)), 0.05, key="w_lf")
            with c4:
                w_rt = st.slider("Route Fit", 0.0, 1.0, float(st.session_state.slider_weights.get("route_fit", 0.15)), 0.05, key="w_rt")
            with c5:
                w_pf = st.slider("Feasibility", 0.0, 1.0, float(st.session_state.slider_weights.get("practical_feasibility", 0.15)), 0.05, key="w_pf")

            new_weights = {
                "research_fit": w_rf,
                "evidence_fit": w_ef,
                "letter_fit": w_lf,
                "route_fit": w_rt,
                "practical_feasibility": w_pf,
            }
            if new_weights != st.session_state.slider_weights:
                st.session_state.slider_weights = new_weights
                st.session_state.workspace["custom_slider_weights"] = new_weights
                save_workspace(st.session_state.workspace)
                st.rerun()

        default_view_index = 1 if st.session_state.latest_research_set_id else 0
        explorer_view = st.selectbox(
            "Board view",
            ["All programs", "Only latest research run", "Only manually added/live"],
            index=default_view_index,
        )
        explorer_results = results
        if explorer_view == "Only latest research run":
            explorer_results = results.loc[
                results["Research Set"].eq(st.session_state.latest_research_set_id)
            ]
        elif explorer_view == "Only manually added/live":
            explorer_results = results.loc[results["Source"].ne("Seeded")]
        if explorer_results.empty:
            if not st.session_state.latest_research_set_id and source_mode == "Discovered programs":
                st.info("Run AI Deep Search to discover programs for this applicant.")
            else:
                st.warning("No programs match the current filters.")
        else:
            board_columns = [
                "Category",
                "Overall Score",
                "University",
                "Program",
                "Degree",
                "Track",
                "Status",
                "POI Fit",
                "Professors",
                "Risk Note",
                "Next Action",
                "Research Signal",
                "Letter Strategy",
                "Balance Note",
                "Source",
            ]
            visible_board_columns = [
                column for column in board_columns if column in explorer_results
            ]
            st.dataframe(
                explorer_results[visible_board_columns],
                width="stretch",
                hide_index=True,
            )
            options = explorer_results["University"] + " - " + explorer_results["Program"]
            selected_label = st.selectbox("Open detail", options)
            selected_row = explorer_results.loc[options == selected_label].iloc[0].to_dict()
            selected_program = program_by_id(all_programs, selected_row["Program ID"])
            if selected_program:
                render_program_detail(selected_program, selected_row)

    with detail_tab:
        st.subheader("Program Detail")
        labels = {
            f"{program['school']} - {program['program']}": program["id"]
            for program in filtered_programs
        }
        if labels:
            label = st.selectbox("Program", list(labels.keys()), key="detail_select")
            program = program_by_id(all_programs, labels[label])
            if program:
                row = results.loc[results["Program ID"].eq(program["id"])].iloc[0].to_dict()
                render_program_detail(program, row)
        else:
            st.info("Adjust filters to inspect a program.")

    with compare_tab:
        st.subheader("Compare")
        labels = {
            f"{row['University']} - {row['Program']}": row for row in results.to_dict("records")
        }
        selected = st.multiselect("Select 2-4 programs", list(labels.keys()), max_selections=4)
        if selected:
            compare_df = comparison_dataframe([labels[label] for label in selected])
            st.dataframe(compare_df, width="stretch", hide_index=True)
        else:
            st.info("Choose programs from the list to compare requirements and fit.")

    with export_tab:
        st.subheader("Export")
        st.write(
            "Download the filtered match board in the reference CSV shape "
            "or as a formatted workbook."
        )
        export_df = reference_export_dataframe(filtered_programs, st.session_state.profile)
        workbook_data = (
            results_workbook_bytes(filtered_programs, st.session_state.profile)
            if filtered_programs
            else b""
        )
        st.download_button(
            "Download CSV",
            data=export_df.to_csv(index=False).encode("utf-8"),
            file_name="gradpath_matching_shortlist.csv",
            mime="text/csv",
            disabled=export_df.empty,
        )
        st.download_button(
            "Download XLSX",
            data=workbook_data,
            file_name="gradpath_matching_workbook.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            disabled=not workbook_data,
        )
        st.dataframe(
            export_df if not export_df.empty else results,
            width="stretch",
            hide_index=True,
        )


if __name__ == "__main__":
    main()
