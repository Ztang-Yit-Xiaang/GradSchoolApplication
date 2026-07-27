---
name: phd-application-planner
description: >-
  A Claude Code / Codex / Antigravity skill that turns a short conversation into a researched,
  interactive decision dashboard for planning PhD applications: find programs, surface fitting
  advisors (PIs), track NSF/NIH/DARPA grant hiring signals, compare cost-of-living stipends,
  and decide where to apply.
---

# PhD Application Planner Skill

A skill for planning PhD applications: find programs, surface fitting advisors (PIs), track NSF/NIH/DARPA grants, compare stipends, and build an interactive decision dashboard.

## What You Get
A single-page interactive workspace with:
- **KPI Metrics & Top Picks Grid**: Glassmorphic summary cards and high-level fit categories.
- **Program & Match Board**: Filter by region, fit, stipend, deadline; interactive dynamic slider ranker.
- **PI Tracker & Grant Intelligence**: Surface Professors of Interest (PIs), flag recent NSF/NIH/DARPA grants with `🔥 High Hiring Likelihood`, 1-click search buttons (NSF, NIH, Scholar, LinkedIn, X/Twitter, Homepage), and persistent notes per advisor.
- **Cost-of-Living Adjusted Real Stipend Calculator**: Displays nominal vs real stipend adjusted for regional cost indices.
- **Data Persistence**: Workspace state saved to `.gradpath/workspace.json` surviving browser reloads and restarts.

## Requirements
- Antigravity / Claude Code / Codex with local Skills enabled
- Python 3.10+ with `streamlit`, `pandas`, `openpyxl`, `requests`, `beautifulsoup4`, `pypdf`

```bash
cd "/Users/chenyixin/Documents/Grad School Analysis"
python3 -m streamlit run app.py
```

## Directory Structure
```
phd-application-planner/
├── SKILL.md                 # shared execution guide
├── agents/
│   └── openai.yaml          # display metadata
├── reference/
│   ├── intake.md            # intake question bank
│   ├── schema.md            # data schemas (_config.json & _wf_result.json)
│   ├── honesty.md           # verification & no-fabrication rules
│   └── pipeline.md          # 6-phase web app adjustment pipeline
```

## The 5 Steps It Runs

### 1. Interactive Intake
Asks what you care about across 5 intake rounds (see `reference/intake.md`): research field/subfields, target regions, minimum stipend floor, PI preferences, and application constraints.

### 2. Config & Taxonomy
Writes a `_config.json` configuration file with region settings, stipend floor, and field taxonomy.

### 3. Research & Grant Intelligence
Performs program & PI research (see `reference/honesty.md`):
- Fetches `.edu` admissions pages.
- Extracts PI lists and generates 1-click links for NSF Award Search (`nsf.gov/awardsearch`), NIH RePORTER (`reporter.nih.gov`), Google Scholar, LinkedIn, X/Twitter, and Lab Homepages.
- Flags faculty with recent grant signals (`🔥 High Hiring Likelihood`).

### 4. Build & Score Data
Calculates dynamic priority scores based on user weight sliders and computes Cost-of-Living real stipends.

### 5. Launch Dashboard
Launches the Streamlit app:
```bash
python3 -m streamlit run app.py
```

## Reference Documentation
- **Intake Question Bank**: [reference/intake.md](reference/intake.md)
- **Data Schemas**: [reference/schema.md](reference/schema.md)
- **Accuracy & Honesty Rules**: [reference/honesty.md](reference/honesty.md)
