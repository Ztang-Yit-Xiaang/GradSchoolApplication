# GradPath Planner

GradPath Planner is a local Streamlit app for graduate school hunting and preparation. It now works as a GPT-assisted graduate matching workspace: it matches the applicant's research narrative to programs first, then calibrates admission risk, actions, test-policy uncertainty, and recommender strategy.

The app opens with Yixin's academic CV-derived profile as the default profile. You can edit it manually or import an updated CV.

## Launch

```bash
cd "/Users/chenyixin/Documents/Grad School Analysis"
export OPENAI_API_KEY="your_key_here"
# Optional; defaults to the recommended GPT matching model if unset.
export GRADPATH_OPENAI_MODEL="gpt-5.5"
python3 -m streamlit run app.py
```

The app usually opens at:

```text
http://localhost:8501
```

`OPENAI_API_KEY` is optional. Without it, the app still uses rule-based CV parsing and school-page extraction.
The recommended OpenAI model is `gpt-5.5`; set `GRADPATH_OPENAI_MODEL` only if
you want to override it with another available model.
After launch, open **Agent Search** and click **Test OpenAI API** to confirm the
running Streamlit process can actually use the key.

Optional search API:

```bash
export SERPAPI_API_KEY="your_key_here"
```

## How To Use

1. **Profile Narrative**: Review the default Yixin profile, research tags, evidence, test strategy, and recommender contexts.
2. **Import Profile**: Upload a `.tex`, `.pdf`, or `.txt` CV, extract a draft, review it, and apply it.
   You can also upload an unofficial `.pdf` or `.txt` transcript to extract coursework evidence.
3. **Agent Search**: Run **GPT Match Search** to discover programs online for the active
   applicant profile. Hosted OpenAI web search is optional; local URL/school-name tools remain available.
   Sample seeded programs are hidden by default and are only shown when you explicitly include them.
4. **Match Board**: Review ranked programs by category, POI fit, risk note, next action, research signal, and letter strategy.
5. **Program Detail**: Inspect matching scores, official requirements, community signals, fit plan, and source links.
6. **Compare**: Select 2-4 programs for side-by-side comparison.
7. **Export**: Download the reference-shaped CSV or formatted XLSX workbook.

## Important Notes

- Do not run the app with `python app.py`; use `python3 -m streamlit run app.py`.
- Do not put API keys into source files.
- Live extracted school information is marked `Live/Needs Review` or `AI/Needs Review`.
- Deep school search asks GPT to reason only over gathered profile data, search results, and
  fetched official page text. Admit confidence bands are planning estimates, not guarantees.
- The default source mode is `Discovered programs`, so Match Board/Compare/Export start from
  AI/web-discovered recommendations rather than seeded examples.
- Unofficial/community evidence from public forums is advisory only and never overrides official
  program requirements.
- Program Detail can include a Next Fit Plan with coursework, research, publication/project,
  SOP, faculty-contact suggestions, POI fit, risk note, and next action.
- Research signals are conservative: in-prep, submitted, or accepted only when that status is accurate.
- Always verify requirements on official university pages before applying.
- LinkedIn scraping is not supported; use a CV, resume, or exported/saved LinkedIn PDF instead.
