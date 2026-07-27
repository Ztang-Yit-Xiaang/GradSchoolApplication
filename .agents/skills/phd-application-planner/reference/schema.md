# PhD Application Planner Data Schema

## 1. Config Schema (`_config.json`)
```json
{
  "degree_target": "PhD",
  "primary_fields": ["Computer Science", "Operations Research"],
  "subfields": ["Optimization", "RandNLA", "Scientific Computing"],
  "regions": ["US Midwest", "US West Coast", "US East Coast"],
  "stipend_floor": 30000,
  "currency": "USD",
  "priority_weights": {
    "research_fit": 0.35,
    "evidence_fit": 0.20,
    "letter_fit": 0.15,
    "route_fit": 0.15,
    "practical_feasibility": 0.15
  }
}
```

## 2. Research Result Schema (`_wf_result.json` & `workspace.json`)
```json
{
  "programs": [
    {
      "id": "program-id-slug",
      "school": "University Name",
      "program": "Program Name",
      "degree": "PhD",
      "field": "Computer Science",
      "country": "United States",
      "location": "City, State",
      "requirements": {
        "deadline": "2026-12-15",
        "english": {"required": true, "minimum_score": 100},
        "gre": {"status": "Not Required"},
        "coursework": ["Linear Algebra", "Algorithms"]
      },
      "stipend": {
        "nominal": 38000,
        "col_index": 1.15,
        "real_stipend": 33043,
        "tier": "Comfortable"
      },
      "phd": {
        "faculty_areas": ["Optimization", "Machine Learning"],
        "poi_list": ["Prof. Name 1", "Prof. Name 2"]
      },
      "grant_intelligence": {
        "nsf_awards_search_url": "https://www.nsf.gov/awardsearch/...",
        "nih_reporter_url": "https://reporter.nih.gov/search...",
        "hiring_badge": "🔥 High Hiring Likelihood (Recent Grant)"
      }
    }
  ],
  "pi_notes": {
    "Prof. Name 1": "Approved NSF Award #2401920; Emailed on 10/12; open to Fall 2027 PhDs."
  }
}
```
