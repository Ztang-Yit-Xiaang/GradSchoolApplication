# Implementation Notes

## Progress Log

- Created a Streamlit MVP UI for `GradPath Planner`.
- Added a small `gradpath` helper package for profile defaults, seeded data loading, filters, fit scoring, and export shaping.
- Added seeded sample data for CS, Data Science, Statistics, Operations Research, and Applied Math MS/PhD programs.
- Added tests for data loading, filtering, scoring, result export columns, and compare-table shape.
- Added CV/TXT profile import with rule-based extraction and optional OpenAI structured extraction.
- Added online school research helpers for official URLs, school-name candidate search, similar-program queries, and live extracted program records.
- Added local session state for imported profile drafts, live programs, research logs, and extraction warnings.
- Replaced the generic default profile with Yixin's academic CV-derived profile.
- Added `.tex` LaTeX CV upload support and a Streamlit Guide tab.
- Added `README.md` with launch instructions, API-key setup, and the intended workflow.
- Improved UI readability with higher-contrast text, visible metric labels, clearer tabs, a workflow hint, and grouped Profile sections.
- Fixed dark-on-dark Streamlit widget styling by separating main-content input colors from sidebar control colors.

## Comparable Tool Research

Research summary used for the MVP design:

- GradFit: AI fit scoring, professor tracking, deadline management, funding intelligence, spreadsheet-style comparison, free-to-start positioning.
- Studyportals: global Master's/PhD search, scholarships, reviews, comparison tools, and AI advisor based on academic background, goals, English level, and budget.
- ApplyBoard: guided international student search by destination, study level, field, tuition, scholarships, and application workflow.
- IDP Live: free course matching, document upload, application status tracking, and counselor-backed study-abroad guidance.
- Yocket Premium: counseling plus platform support for shortlisting, SOP editing, scholarships, loans, visa support, and admits-focused positioning.
- Magoosh GRE/admissions resources: GRE prep, application tracker, guided essay writing, SOP examples, and workshops for Master's/PhD applicants.
- AdmitYogi: AI counselor pattern, accepted-profile data, reach/target/safety framing, essay scoring, and school matching.
- Counselly Graduate: program matching, SOP/research proposal coaching, GRE strategy, deadlines, funding/assistantship guidance, and PhD faculty fit.

Common gaps:

- Requirements are often shown as broad advice instead of structured evidence fields.
- MS and PhD matching are frequently blended even though PhD applicants need faculty, research, and funding fit.
- Fit scores are rarely transparent about missing coursework, GRE/English readiness, and experience gaps.
- Many tools are counseling-led or paid; this MVP focuses on transparent local self-research.

## Design Decisions

- Chose Streamlit because the repo had no existing app stack and the MVP needs forms, dense tables, compare views, and CSV export quickly.
- Designed for international senior undergrads in CS, DS, OR, Applied Math, Statistics, and adjacent quantitative fields.
- Used a dense dashboard instead of a guided wizard so users can compare many schools quickly.
- Kept the first version offline-first with seeded sample data. Live scraping is intentionally deferred because official university pages vary and need source-aware extraction.
- Added separate MS and PhD scoring behavior. PhD scoring emphasizes research/faculty fit, funding language, and prior research experience more than general program popularity.
- Kept all requirements visible in table/export fields: English, GRE, coursework, DDL, funding, research fit, SOP, missing items, and source URLs.
- CV import supports PDF/TXT and always shows extracted fields for review before applying them to the active profile.
- CV import now supports PDF/TXT/TEX. LaTeX files are cleaned before rule or AI extraction.
- Yixin's CV-derived profile is the default because this repo is currently a personal local planning tool.
- Online research starts from user intent: pasted official URLs or schools already in mind. Similar-program discovery uses the current profile and target degree/field.
- Search uses `SERPAPI_API_KEY` when configured, otherwise a direct DuckDuckGo HTML attempt plus built-in fallbacks for common schools.
- OpenAI extraction is optional and uses `OPENAI_API_KEY` from the local environment. If no key is present, rules still run and the UI disables AI checkboxes.
- LinkedIn scraping is intentionally out of scope. Users should upload a CV, resume, or saved/exported LinkedIn PDF instead of asking the app to log into LinkedIn.
- The UI now favors explicit sections and high-contrast labels over a flatter form layout, because Streamlit's default widget styling made some labels too faint on the light background.

## MVP Limits

- Program records are seeded examples and must be replaced or verified against official pages before real application decisions.
- Profile edits are stored only in the current Streamlit session.
- No account system, reminders, or automatic source refresh yet.
- Live web extraction is best-effort. University pages vary widely, and all imported program records are marked `Live/Needs Review` or `AI/Needs Review`.
- AI extraction depends on a local `OPENAI_API_KEY`; no API key is stored in the repo.
- Fit scoring is deterministic and explainable, but still a planning aid rather than an admissions prediction.

## CV Import And Online Research

CV import:

- PDF files use `pypdf`; TXT files are decoded directly.
- TEX files are cleaned by removing common LaTeX commands, moderncv section commands, wrappers, braces, and escaped characters.
- Rules extract GPA, TOEFL/IELTS/Duolingo, GRE Quant, coursework, experience, target fields, and research interests.
- Optional AI extraction normalizes messy CV text into the existing profile schema, then the user reviews the draft before applying it.

Online school research:

- Pasted official URLs are fetched with `requests`, cleaned with BeautifulSoup, and mapped into the existing program schema.
- School-name search tries configured search API first, then direct search, and finally common built-in fallbacks.
- Similar-program search builds queries from the active profile fields, degree target, and research interests.
- Extracted live records are combined with seeded programs for ranking, compare, detail, and CSV export.

Environment variables:

- `OPENAI_API_KEY`: enables AI extraction for CV and school pages.
- `GRADPATH_OPENAI_MODEL`: optional model override; defaults to `gpt-5.4-mini`.
- `SERPAPI_API_KEY`: optional search API key.

## Button Contrast, Similar Search, And API Check

- Main-page buttons, form submit buttons, download buttons, and file-upload controls now use
  scoped high-contrast CSS so action labels stay readable while the sidebar keeps its dark style.
- Similar-program search now starts with curated offline recommendations for CS, Data Science,
  Statistics, Applied Math, and OR programs, then merges any live search results that are available.
  Candidate URLs are deduplicated and source-labeled.
- The Research Schools tab includes a `Test OpenAI API` action. It checks whether
  `OPENAI_API_KEY` is visible to the running Streamlit process and performs a tiny Responses API
  call without displaying or storing the key.

## Deep GPT-Assisted School Research

- Added a deep research workflow that separates GPT reasoning from web access: the app plans
  queries, runs search/fetching itself, extracts official page evidence, and only then asks GPT to
  normalize or reason over provided text.
- Added deterministic query templates, official-page filtering, candidate dedupe, page extraction,
  and admit-confidence estimates with bands: `Likely-ish`, `Target`, `Reach`, `High Reach`, and
  `Needs More Evidence`.
- Deep research records reuse the live program schema, so extracted programs flow into Explorer,
  Detail, Compare, and Export. Export now includes admit-confidence columns when present.
- The UI labels these outputs as estimates and keeps source confidence as `Needs Review` because
  admissions outcomes and live requirements must be checked on official pages.

## Connected Planner Update

- Sidebar filters were reframed as `Result Filters` and now include program source, confidence,
  admit band, and latest-research controls so they no longer feel like applicant-profile inputs.
- Research Schools now separates `AI Deep Search` from `No-AI Search`. The no-AI path uses rules
  and curated candidates; the AI path uses OpenAI for query planning, extraction cleanup,
  confidence reasoning, and community-signal synthesis when the key is available.
- Deep-research programs now carry a local research-set ID, program source, and optional
  unofficial/community evidence. Explorer can show only the latest research run, and export
  includes research-set/source/admit/community columns.
- Import Profile now includes unofficial transcript upload. Transcript parsing stays local and
  produces a reviewable coursework/GPA draft before updating the applicant profile.
- Program Detail separates official requirements from unofficial/community signals and labels
  the latter as advisory, not admissions policy.

## Online-First AI Research And Seeded Enrichment

- Sidebar widget CSS now explicitly covers buttons, selected values, placeholders, tags, disabled
  controls, captions, and nested BaseWeb elements so text remains readable on the dark sidebar.
- AI Deep Search is now online-first: live search candidates are collected before curated/seeded
  fallback, and the run records whether it used `Online search`, `Online + fallback`, or
  `Fallback only`.
- Added search breadth controls (`Fast`, `Balanced`, `Deep`) to tune how many pages and community
  sources the research agent considers before returning the requested recommendation count.
- Added seeded-program enrichment. Seeded sample records stay unchanged; enriched copies are
  tagged separately and receive admit estimates, community evidence, and next-fit plans.
- Added Next Fit Plan output for detail/export with coursework, research, publication/project,
  SOP, and faculty-contact suggestions.

## Research-First Default

- The app now defaults to `Discovered programs`, so seeded sample records are not included in
  metrics, Explorer, Compare, or Export unless the user explicitly chooses
  `Include sample seeded programs`.
- Research Schools is framed around `Find Best-Fit Programs`; AI Deep Search is the primary
  action, while manual URL/school-name tools and sample enrichment are collapsed optional tools.
- Explorer defaults to the latest research run after deep research completes, and otherwise shows
  an empty-state prompt to run AI Deep Search.

## Manual Smoke Test Notes

- To run: `streamlit run app.py`.
- Confirm dashboard loads with seeded programs.
- Edit profile to target both MS/PhD in CS, Data Science, and Statistics.
- Confirm ranked results update after profile changes.
- Filter to PhD and verify research/funding/advisor fields appear.
- Select 2-4 programs in Compare.
- Export CSV and verify requirement, preference, experience, deadline, fit, and source columns are present.

Completed smoke test:

- Launched app at `http://localhost:8501`.
- Confirmed header metrics and profile form render.
- Confirmed `Import Profile` tab renders with PDF/TXT upload, AI availability state, and rule-based fallback message.
- Confirmed Guide tab is available with launch, API-key, workflow, and verification instructions.
- Added automated coverage for Yixin default profile and representative LaTeX CV extraction.
- Confirmed `Research Schools` tab renders with target field, degree, URL extraction, school-name search, and similar-program controls.
- Opened Explorer and confirmed ranked table/detail section render with English, GRE, coursework, DDL, SOP, funding, missing items, and source link.
- Filtered Degree to `PhD`; results reduced to 3 PhD programs and displayed research/funding fit fields.
- Opened Compare and selected University of Michigan PhD CSE and Stanford PhD Statistics.
- Opened Export and confirmed the `Download CSV` control is visible.
- CV TXT parsing, live program extraction, search fallback, and live export behavior are covered by automated tests.

Validation results:

- `python -m pytest` could not run because this Mac environment does not expose a `python` executable.
- Equivalent test command `python3 -m pytest` passed: 9 tests passed.
- `python -m ruff check .` could not run for the same PATH reason.
- Equivalent lint command `python3 -m ruff check .` passed.

## Remaining Follow-Ups

- Add user-editable custom program records.
- Add persistence for profiles and selected schools.
- Add source snapshots for fetched official pages.
- Add richer PDF extraction for program handbooks and admissions requirement sheets.
- Add deadline reminders and recurring requirement refresh.
- Add deeper advisor/faculty matching with official faculty pages.
- Add a small local cache so the same official URLs do not need to be fetched repeatedly.
