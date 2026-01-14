"""State management for research tasks."""

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class State:
    """Research task state."""
    task_id: str
    model: str
    api_type: str  # "poe" or "google"
    prompt: str
    task_dir: str
    status: str = "pending"  # pending, in_progress, completed, failed
    interaction_id: Optional[str] = None
    attempts: int = 0
    partial_output: str = ""
    error: Optional[str] = None


def get_cache_dir() -> Path:
    """Get the cache directory for research results."""
    cache_dir = Path.home() / ".cache" / "poe-research"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def save_state(state: State) -> None:
    """Save state to disk."""
    state_path = Path(state.task_dir) / "state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)

    data = asdict(state)
    state_path.write_text(json.dumps(data, indent=2))


def load_state(state_path: Path) -> State:
    """Load state from disk."""
    data = json.loads(state_path.read_text())
    # Add api_type for legacy states that don't have it
    if "api_type" not in data:
        # Infer api_type from model name
        model = data.get("model", "")
        if "gemini" in model.lower():
            data["api_type"] = "google"
        else:
            data["api_type"] = "poe"
    return State(**data)
