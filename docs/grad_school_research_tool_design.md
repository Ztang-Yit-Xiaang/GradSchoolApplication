# Grad School Research Tool Design

## Goal

Build a tool that helps an applicant search graduate programs by major, collect official admissions requirements, and compare each program against the applicant's background.

Example query:

```text
Major: Computer Science
Degree: MS or PhD
Country: United States
Applicant background: statistics/math undergraduate, Python, ML projects, TOEFL 102, GPA 3.7
```

The tool should return a structured shortlist of schools with:

- English language requirements
- Coursework or prerequisite requirements
- Application deadlines
- Essay, statement of purpose, and personal statement preferences
- PhD advisor, lab, funding, and research fit signals
- Program fit based on the applicant's background
- Source links and extraction confidence

## Core User Flow

1. User enters target major, degree level, location, term, and personal profile.
2. Tool discovers relevant graduate programs.
3. Tool visits official university/program pages and extracts requirements.
4. Tool stores structured results in a searchable database.
5. Tool compares requirements with the user's profile.
6. Tool produces a ranked table, alerts for missing qualifications, and essay guidance.

## Recommended First Version

Start with a semi-automated research assistant rather than a fully autonomous crawler.

The first version should accept a list of program URLs manually or from search results, then extract and compare information. This is more reliable because university pages vary a lot and some requirements are hidden in PDFs, FAQ pages, or graduate school portals.

## Data Model

### Applicant Profile

```json
{
  "name": "Applicant",
  "target_major": "Computer Science",
  "degree_level": "MS or PhD",
  "term": "Fall 2027",
  "citizenship_or_region": "International",
  "gpa": "3.7/4.0",
  "english_scores": {
    "toefl": 102,
    "ielts": null,
    "duolingo": null
  },
  "coursework": [
    "Data Structures",
    "Algorithms",
    "Linear Algebra",
    "Probability",
    "Machine Learning"
  ],
  "skills": ["Python", "SQL", "PyTorch"],
  "research_interests": ["machine learning", "data mining"],
  "publication_or_research_experience": [
    "Independent ML project",
    "Research assistant experience, if any",
    "Thesis, poster, preprint, or publication, if any"
  ],
  "potential_phd_topics": [
    "applied machine learning",
    "data mining",
    "optimization"
  ],
  "projects": [
    "Weather-aware travel itinerary optimization",
    "Machine learning classification project"
  ],
  "notes": "Interested in applied CS, ML, and data science programs."
}
```

### Program Record

```json
{
  "school": "University Name",
  "program_name": "MS in Computer Science",
  "department": "Computer Science",
  "degree_level": "MS or PhD",
  "location": "City, State, Country",
  "official_url": "https://...",
  "application_url": "https://...",
  "deadline": {
    "fall_priority": "YYYY-MM-DD",
    "fall_final": "YYYY-MM-DD",
    "spring": null,
    "notes": "International applicants should apply by priority deadline."
  },
  "english_requirements": {
    "required": true,
    "toefl_min": 90,
    "ielts_min": 7.0,
    "duolingo_min": 120,
    "waiver_policy": "Waived for applicants with degree from English-instruction institution.",
    "notes": ""
  },
  "coursework_requirements": {
    "required_courses": ["Data Structures", "Algorithms", "Discrete Math"],
    "recommended_courses": ["Operating Systems", "Computer Architecture"],
    "bridge_allowed": true,
    "notes": ""
  },
  "essay_requirements": {
    "sop_required": true,
    "personal_statement_required": false,
    "word_limit": "500-1000 words",
    "program_preferences": [
      "Discuss research interests",
      "Name potential faculty",
      "Explain preparation for graduate CS coursework"
    ],
    "prompt_text": ""
  },
  "phd_requirements": {
    "advisor_contact_expected": false,
    "faculty_match_required": true,
    "funding_guarantee": "Usually funded for admitted PhD students",
    "assistantship_info": "TA/RA funding available",
    "research_statement_required": true,
    "writing_sample_required": false,
    "potential_faculty": [
      {
        "name": "Faculty Name",
        "research_area": "Machine learning",
        "profile_url": "https://...",
        "fit_reason": "Works on applied ML/data mining topics related to applicant interests"
      }
    ],
    "notes": ""
  },
  "fit_analysis": {
    "eligibility_status": "Likely eligible",
    "missing_items": ["Operating Systems recommended but not required"],
    "strengths": ["Strong TOEFL score", "ML project background"],
    "risks": ["Limited systems coursework"],
    "essay_angles": [
      "Connect applied ML projects to faculty/lab interests",
      "Explain quantitative preparation through statistics/math coursework"
    ],
    "fit_score": 82
  },
  "sources": [
    {
      "url": "https://...",
      "page_title": "Admissions Requirements",
      "retrieved_at": "YYYY-MM-DD",
      "fields_supported": ["deadline", "english_requirements"],
      "confidence": "high"
    }
  ]
}
```

## System Architecture

### 1. Program Discovery

Inputs:

- Major, such as Computer Science, Data Science, Statistics, Business Analytics
- Degree level, such as MS, PhD, MEng
- Region or ranking preference
- Optional school list

Discovery methods:

- Search official university domains
- Import user-provided URLs
- Import CSV/XLSX school lists
- Later: integrate ranking or public dataset sources

Output:

- Candidate program URLs
- Admissions page URLs
- Graduate school general requirement URLs

### 2. Page Collection

For each program, collect:

- Program overview page
- Admissions requirements page
- Application deadline page
- International applicant page
- English proficiency page
- FAQ page
- Curriculum or prerequisite page
- Faculty, lab, and research group pages for PhD programs
- Funding, assistantship, fellowship, and stipend pages for PhD programs
- PDF requirement sheets, if available

Important rule: every extracted requirement should keep source URL and retrieval date.

### 3. Information Extraction

Use a two-pass extraction process:

First pass: deterministic parsing

- HTML title
- headings
- tables
- dates
- links
- PDF text

Second pass: LLM structured extraction

- Normalize TOEFL/IELTS/Duolingo minimums
- Identify deadline categories
- Separate required coursework from recommended background
- Extract essay prompt and program-specific preferences
- For PhD programs, extract advisor expectations, faculty fit, research statement requirements, and funding language
- Flag uncertainty when pages conflict

Recommended extraction output:

```json
{
  "field": "toefl_min",
  "value": 90,
  "evidence": "Minimum TOEFL iBT score is 90.",
  "source_url": "https://...",
  "confidence": "high"
}
```

### 4. Matching And Scoring

Compare applicant profile against each program.

Suggested scoring:

- English requirement match: 20 points
- Coursework match: 25 points
- Research/program interest match: 20 points
- Deadline readiness: 15 points
- Essay/background alignment: 10 points
- Risk/uncertainty penalty: 10 points

The score should not replace human judgment. It should explain why a school is a reach, target, likely fit, or needs manual review.

For PhD programs, use a separate scoring model:

- Research fit with faculty/labs: 30 points
- Prior research/project preparation: 20 points
- Coursework and technical preparation: 15 points
- English requirement match: 10 points
- Funding/advisor clarity: 10 points
- Statement of purpose alignment: 10 points
- Risk/uncertainty penalty: 5 points

PhD ranking should care less about general school popularity and much more about advisor match, research direction, funding, and whether the program expects applicants to contact faculty before applying.

### 5. User Interface

Best first UI:

- Search form at top
- Applicant profile panel
- Results table
- Detail drawer for each program
- Source/evidence viewer
- Export button

Table columns:

- School
- Program
- Degree
- Deadline
- TOEFL/IELTS
- Prerequisites
- PhD advisor/faculty fit
- Funding notes
- Essay notes
- Fit score
- Missing items
- Confidence
- Source

Detail view:

- Official links
- Full extracted requirements
- Evidence snippets
- Applicant fit summary
- PhD research/advisor fit summary, when relevant
- Suggested essay strategy
- Manual notes

### 6. Storage

For a simple local tool:

- `profiles/applicant_profile.json`
- `data/programs.sqlite`
- `exports/program_shortlist.xlsx`
- `exports/program_shortlist.csv`
- `reports/program_fit_report.md`

For a web app:

- PostgreSQL database
- Object storage for PDFs and page snapshots
- Background jobs for refresh

## Suggested Tech Stack

### Local Python Version

- Python
- Streamlit for UI
- SQLite for storage
- Playwright or requests/BeautifulSoup for page collection
- PyMuPDF for PDF extraction
- pandas/openpyxl for export
- OpenAI API or another LLM for structured extraction and matching

This is the fastest version to build for personal use.

### Web App Version

- Next.js frontend
- FastAPI backend
- PostgreSQL
- Celery/RQ background workers
- Playwright for difficult pages
- LLM extraction service

This is better if multiple users will use the tool.

## Quality Controls

Because admissions requirements are high-stakes and change often:

- Prefer official school/program pages over aggregator sites.
- Store source URL and retrieval date for every field.
- Mark conflicting information as `needs_review`.
- Show evidence snippets beside extracted values.
- Refresh deadlines and requirements before final submission.
- Avoid claiming eligibility unless all required fields are supported by official sources.

## MVP Build Plan

### Phase 1: Manual URL Research Assistant

Features:

- User creates applicant profile.
- User enters 5-20 program URLs.
- Tool extracts requirements into a table.
- Tool compares TOEFL/IELTS and coursework.
- For PhD programs, tool also extracts faculty/lab/funding information when available.
- Tool exports CSV/XLSX.

### Phase 2: Search And Discovery

Features:

- Search by major, degree, country, and state.
- Auto-discover admissions, deadline, and English proficiency pages.
- Deduplicate programs.

### Phase 3: Essay Fit Assistant

Features:

- Extract program-specific SOP prompt.
- Compare prompt with applicant profile.
- Suggest essay angles.
- Identify faculty/lab/topic matching opportunities.

### Phase 3B: PhD Research Fit Assistant

Features:

- Extract faculty names, research areas, and lab URLs.
- Match applicant research interests and projects to potential advisors.
- Identify whether the program recommends contacting faculty before applying.
- Summarize funding guarantees, assistantships, fellowships, and stipend notes.
- Generate a short advisor-fit memo for each promising PhD program.

### Phase 4: Monitoring

Features:

- Re-check selected programs weekly.
- Notify if deadlines or requirements change.
- Keep historical snapshots.

## Example Output Table

| School | Program | Degree | Deadline | English Requirement | Coursework Requirement | PhD Research/Funding Notes | Essay Preference | Fit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| University A | Computer Science | MS | Dec 15 | TOEFL 90 / IELTS 7.0 | Data Structures, Algorithms | N/A | Discuss research interests and faculty fit | Strong |
| University B | Computer Science | PhD | Dec 1 | TOEFL 100 | CS background recommended | Faculty match important; funded TA/RA usually available | Research goals, faculty fit, prior preparation | Needs review |
| University C | Data Science | MS/PhD | Feb 1 | TOEFL 80 | Linear Algebra, Statistics, Programming | PhD applicants should identify research area | Career goals and quantitative background | Strong |

## First Implementation Target

Build a local Streamlit app with these pages:

1. Profile
2. Add Programs
3. Extract Requirements
4. Compare & Rank
5. Export

Minimum useful output:

- A ranked table of programs
- One detail page per program
- Source links and confidence notes
- MS and PhD comparison modes
- PhD advisor/funding/research fit fields
- Exportable spreadsheet
