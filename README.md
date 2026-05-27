# GradPath Planner

GradPath Planner is a local Streamlit app for graduate school hunting and preparation. It compares MS and PhD programs by English requirements, GRE policy, coursework fit, deadlines, SOP preferences, funding, research/advisor fit, and applicant background.

The app opens with Yixin's academic CV-derived profile as the default profile. You can edit it manually or import an updated CV.

## Launch

```bash
cd "/Users/chenyixin/Documents/Grad School Analysis"
export OPENAI_API_KEY="your_key_here"
# Optional; defaults to gpt-5.4-mini if unset.
export GRADPATH_OPENAI_MODEL="gpt-5.4-mini"
python3 -m streamlit run app.py
```

The app usually opens at:

```text
http://localhost:8501
```

`OPENAI_API_KEY` is optional. Without it, the app still uses rule-based CV parsing and school-page extraction.
The default OpenAI model is `gpt-5.4-mini`; set `GRADPATH_OPENAI_MODEL` only if
you want to override it.
After launch, open **Research Schools** and click **Test OpenAI API** to confirm the
running Streamlit process can actually use the key.

Optional search API:

```bash
export SERPAPI_API_KEY="your_key_here"
```

## How To Use

1. **Profile**: Review the default Yixin profile and edit GPA, test scores, coursework, experience, research interests, and preferences.
2. **Import Profile**: Upload a `.tex`, `.pdf`, or `.txt` CV, extract a draft, review it, and apply it.
   You can also upload an unofficial `.pdf` or `.txt` transcript to extract coursework evidence.
3. **Research Schools**: Run **AI Deep Search** to discover programs online for the active
   applicant profile. Manual URL/school-name tools are available in the collapsed manual section.
   Sample seeded programs are hidden by default and are only shown when you explicitly include them.
4. **Explorer**: Review ranked programs and open details.
5. **Detail**: Inspect English, GRE, coursework, DDL, SOP, funding, research fit, missing items, and sources.
6. **Compare**: Select 2-4 programs for side-by-side comparison.
7. **Export**: Download the ranked results as CSV.

## Important Notes

- Do not run the app with `python app.py`; use `python3 -m streamlit run app.py`.
- Do not put API keys into source files.
- Live extracted school information is marked `Live/Needs Review` or `AI/Needs Review`.
- Deep school search asks GPT to reason only over gathered profile data, search results, and
  fetched official page text. Admit confidence bands are planning estimates, not guarantees.
- The default source mode is `Discovered programs`, so Explorer/Compare/Export start from
  AI/web-discovered recommendations rather than seeded examples.
- Unofficial/community evidence from public forums is advisory only and never overrides official
  program requirements.
- Program Detail can include a Next Fit Plan with coursework, research, publication/project,
  SOP, and faculty-contact suggestions.
- Always verify requirements on official university pages before applying.
- LinkedIn scraping is not supported; use a CV, resume, or exported/saved LinkedIn PDF instead.
