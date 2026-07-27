from __future__ import annotations

import json
from pathlib import Path
from typing import Any

WORKSPACE_FILE = Path(".gradpath/workspace.json")


def default_workspace_data() -> dict[str, Any]:
    return {
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
        "live_programs": [],
        "research_logs": [],
    }


def load_workspace(filepath: Path | str | None = None) -> dict[str, Any]:
    """Loads workspace state from JSON file or returns defaults."""
    target_path = Path(filepath) if filepath else WORKSPACE_FILE
    if not target_path.exists():
        return default_workspace_data()

    try:
        with open(target_path, encoding="utf-8") as f:
            data = json.load(f)
            defaults = default_workspace_data()
            for key, val in defaults.items():
                data.setdefault(key, val)
            return data
    except Exception:
        return default_workspace_data()


def save_workspace(data: dict[str, Any], filepath: Path | str | None = None) -> bool:
    """Saves workspace state dictionary to JSON file."""
    target_path = Path(filepath) if filepath else WORKSPACE_FILE
    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def get_pi_note(workspace: dict[str, Any], pi_name: str) -> str:
    """Returns persistent note for a specific Professor of Interest."""
    return workspace.get("pi_notes", {}).get(pi_name, "")


def set_pi_note(workspace: dict[str, Any], pi_name: str, note: str) -> None:
    """Sets persistent note for a specific Professor of Interest."""
    if "pi_notes" not in workspace:
        workspace["pi_notes"] = {}
    workspace["pi_notes"][pi_name] = note.strip()
