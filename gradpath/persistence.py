from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from gradpath.schemas import SCHEMA_VERSION

WORKSPACE_FILE = Path(".gradpath/workspace.json")


def default_workspace_data() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "profile": {},
        "pi_notes": {},
        "hidden_programs": [],
        "hidden_pis": [],
        "custom_slider_weights": {
            "research_fit": 0.35,
            "evidence_fit": 0.20,
            "letter_fit": 0.15,
            "route_fit": 0.15,
            "practical_feasibility": 0.15,
        },
        "program_scores_weights": {
            "research_ecosystem": 0.25,
            "advisor_resilience": 0.20,
            "funding_col": 0.20,
            "admission_mode": 0.15,
            "outcomes": 0.10,
            "personal_constraints": 0.10,
        },
        "pi_scores_weights": {
            "research_fit": 0.35,
            "mentoring": 0.20,
            "recent_strength": 0.15,
            "recruiting_confidence": 0.15,
            "outcomes": 0.10,
            "collaboration": 0.05,
        },
        "live_programs": [],
        "research_logs": [],
        "portfolio_tracker": {},
        "outreach_tracker": {},
    }


def migrate_workspace(data: dict[str, Any]) -> dict[str, Any]:
    """Migrates workspace data to current schema version preserving all user entries."""
    if not isinstance(data, dict):
        return default_workspace_data()

    defaults = default_workspace_data()

    for key, val in defaults.items():
        if key not in data:
            data[key] = val

    data["schema_version"] = SCHEMA_VERSION
    return data


def load_workspace(filepath: Path | str | None = None) -> dict[str, Any]:
    """Loads workspace state from JSON file with migration and default fallback."""
    target_path = Path(filepath) if filepath else WORKSPACE_FILE
    if not target_path.exists():
        return default_workspace_data()

    try:
        with open(target_path, encoding="utf-8") as f:
            data = json.load(f)
            return migrate_workspace(data)
    except Exception as e:
        print(f"[GradPath Persistence Warning] Failed to load workspace from {target_path}: {e}")
        return default_workspace_data()


def save_workspace(data: dict[str, Any], filepath: Path | str | None = None) -> bool:
    """Saves workspace state atomically using a temporary file."""
    target_path = Path(filepath) if filepath else WORKSPACE_FILE
    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        data["schema_version"] = SCHEMA_VERSION
        temp_path = target_path.with_suffix(".tmp")

        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        os.replace(temp_path, target_path)
        return True
    except Exception as e:
        print(f"[GradPath Persistence Error] Failed to save workspace to {target_path}: {e}")
        return False


def get_pi_note(workspace: dict[str, Any], pi_name: str) -> str:
    """Returns persistent note for a specific Professor of Interest."""
    return workspace.get("pi_notes", {}).get(pi_name, "")


def set_pi_note(workspace: dict[str, Any], pi_name: str, note: str) -> None:
    """Sets persistent note for a specific Professor of Interest."""
    if "pi_notes" not in workspace:
        workspace["pi_notes"] = {}
    workspace["pi_notes"][pi_name] = note.strip()
