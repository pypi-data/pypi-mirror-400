"""
Utilities for data stored in ~/.society
"""

import hashlib
import os
import uuid
from datetime import datetime
from pathlib import Path

from society.datatypes import CharacterOutput


def get_base_data_dir() -> Path:
    """Get the base data directory (~/.society), ignoring SOCIETY_DATA_DIR."""
    return Path.home() / ".society"


def get_data_dir() -> Path:
    """Get the data directory (~/.society or SOCIETY_DATA_DIR)."""
    if env_dir := os.environ.get("SOCIETY_DATA_DIR"):
        return Path(env_dir)
    return get_base_data_dir()


def get_scoped_data_dir(api_key: str) -> Path:
    """Get data directory scoped by API key hash."""
    base = get_base_data_dir()  # Always use base, not potentially-scoped dir
    user_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
    return base / "users" / user_hash


def list_runs() -> list[Path]:
    runs_dir = get_data_dir() / "runs"
    if not runs_dir.exists():
        return []
    return sorted(runs_dir.iterdir(), reverse=True)


def list_characters(limit: int | None = None) -> list[Path]:
    characters_dir = get_data_dir() / "characters"
    if not characters_dir.exists():
        return []

    # Sort by modification time, most recent first
    paths = sorted(
        characters_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True
    )
    if limit is not None:
        paths = paths[:limit]

    return paths


def write_character(output: CharacterOutput, overwrite: bool = False) -> Path | None:
    output_dir = get_data_dir() / "characters"
    output_dir.mkdir(parents=True, exist_ok=True)

    name_slug = output.name.lower().replace(" ", "-")
    output_path = output_dir / f"{name_slug}.json"

    if output_path.exists() and not overwrite:
        if (
            input(f"{output.name} already exists at {output_path}\nOverwrite? (y/n) ")
            != "y"
        ):
            return None

    output_path.write_text(output.model_dump_json(indent=2))
    return output_path


def create_run_dir(name: str | None = None) -> Path:
    """
    Create a new timestamped run directory

    Ex: ~/.society/runs/2025-12-04_14-32-01_abc123_{name}/
    """
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    short_id = uuid.uuid4().hex[:6]

    dirname = f"{ts}_{short_id}{f'_{name}' if name else ''}"
    run_dir = get_data_dir() / "runs" / dirname

    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir
