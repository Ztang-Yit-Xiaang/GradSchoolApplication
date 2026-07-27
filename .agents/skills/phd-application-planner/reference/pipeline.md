# Detailed Function & I/O Pipeline Reference

Complete function parameters, return types, and file locations for the 6-phase **GradPath Planner** Web App Pipeline.

---

## Phase 1: Intake & Profile Parsing
- **`extract_text_from_upload(filename: str, content_bytes: bytes) -> str`**
  - *Location*: `gradpath/profile_import.py`
  - *Input*: File basename and raw content bytes.
  - *Output*: Cleaned text string (LaTeX macros stripped if `.tex`, PDF text extracted via `pypdf`).
- **`profile_from_text(text: str, base_profile: dict) -> dict[str, Any]`**
  - *Location*: `gradpath/profile_import.py`
  - *Input*: Cleaned text string and base profile dict.
  - *Output*: Profile dict (`gpa`, `target_fields`, `coursework`, `experience`, `research_interests`).

---

## Phase 2: Agent Deep Search & Web Scraping
- **`search_school_candidates(school: str, field: str, degree: str, max_results: int) -> list[dict[str, str]]`**
  - *Location*: `gradpath/school_research.py`
  - *Input*: School name, field, degree, max results integer.
  - *Output*: List of candidate URL dicts `[{"title": str, "url": str, "source": str}]`.
- **`fetch_page_text(url: str) -> tuple[str, str]`**
  - *Location*: `gradpath/school_research.py`
  - *Input*: Admissions page URL string.
  - *Output*: Tuple `(page_title, main_body_text)`.
- **`extract_program_from_text(text: str, url: str, target_field: str, degree_hint: str, title: str) -> dict[str, Any]`**
  - *Location*: `gradpath/school_research.py`
  - *Input*: Body text, URL, target field, degree, title.
  - *Output*: Standardized program dict schema.

---

## Phase 3: Grant & Hiring Intelligence (NSF, NIH, DARPA)
- **`build_pi_outreach_urls(prof_name: str, university: str = "") -> dict[str, str]`**
  - *Location*: `gradpath/matching.py`
  - *Input*: Professor name and university string.
  - *Output*: Dict of 6 URLs (`nsf_awards`, `nih_reporter`, `google_scholar`, `linkedin`, `x_twitter`, `personal_homepage`).
- **`pi_hiring_signal(prof_name: str, note_text: str = "") -> dict[str, Any]`**
  - *Location*: `gradpath/matching.py`
  - *Input*: Professor name and user notes string.
  - *Output*: Dict `{"hiring_badge": str, "level": str, "reason": str}`.

---

## Phase 4: Dynamic Match & COL Scoring
- **`calculate_real_stipend(stipend_amount: float | int, location: str = "") -> dict[str, Any]`**
  - *Location*: `gradpath/matching.py`
  - *Input*: Nominal stipend number and location string.
  - *Output*: Dict `{"nominal": int, "col_index": float, "real_stipend": int, "tier": str}`.
- **`score_match(program: dict, profile: dict, custom_weights: dict | None = None) -> MatchResult`**
  - *Location*: `gradpath/matching.py`
  - *Input*: Program dict, profile dict, custom slider weights dict.
  - *Output*: `MatchResult` dataclass instance with `overall_fit`, `category`, `status`, `poi_fit`, `risk_note`, `next_action`.

---

## Phase 5: UI & Design System
- **`render_kpi_card(label: str, value: Any, subtext: str = "", badge_class: str = "") -> str`**
  - *Location*: `gradpath/ui/theme.py`
  - *Input*: Label, value, subtext, badge class string.
  - *Output*: Glassmorphic HTML card string.
- **`render_pi_browser_tab(programs: list[dict[str, Any]]) -> None`**
  - *Location*: `app.py`
  - *Input*: List of program dicts.
  - *Output*: Renders Streamlit PI browser tab.

---

## Phase 6: Workspace Persistence & Testing
- **`load_workspace(filepath: Path | str | None = None) -> dict[str, Any]`**
  - *Location*: `gradpath/persistence.py`
  - *Input*: Optional JSON filepath (defaults to `.gradpath/workspace.json`).
  - *Output*: Workspace dict (`profile`, `pi_notes`, `custom_slider_weights`, `live_programs`, `research_logs`).
- **`save_workspace(data: dict[str, Any], filepath: Path | str | None = None) -> bool`**
  - *Location*: `gradpath/persistence.py`
  - *Input*: Workspace data dict and filepath.
  - *Output*: Boolean success flag.
