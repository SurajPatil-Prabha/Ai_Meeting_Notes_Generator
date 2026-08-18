"""
Local meeting history: saves generated notes as JSON files on disk so
past sessions can be revisited. No database, no API — just a folder.
"""

import json
import os
import re
from datetime import datetime

HISTORY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "meeting_history")


def _ensure_dir():
    os.makedirs(HISTORY_DIR, exist_ok=True)


def _safe_filename(title: str, ts: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", title.strip()) or "meeting"
    return f"{ts}__{slug}.json"[:200]


def save_meeting(record: dict) -> str:
    """Save a meeting record (title, transcript, results, timestamp) to disk.
    Returns the filename it was saved as."""
    _ensure_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    record = dict(record)
    record.setdefault("saved_at", datetime.now().isoformat(timespec="seconds"))
    filename = _safe_filename(record.get("title", "meeting"), ts)
    path = os.path.join(HISTORY_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    return filename


def list_meetings() -> list[dict]:
    """Return metadata (filename, title, saved_at) for all saved meetings,
    most recent first."""
    _ensure_dir()
    entries = []
    for fn in os.listdir(HISTORY_DIR):
        if not fn.endswith(".json"):
            continue
        path = os.path.join(HISTORY_DIR, fn)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            entries.append({
                "filename": fn,
                "title": data.get("title", fn),
                "saved_at": data.get("saved_at", ""),
            })
        except (json.JSONDecodeError, OSError):
            continue
    entries.sort(key=lambda e: e["saved_at"], reverse=True)
    return entries


def load_meeting(filename: str) -> dict:
    _ensure_dir()
    path = os.path.join(HISTORY_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def delete_meeting(filename: str) -> None:
    _ensure_dir()
    path = os.path.join(HISTORY_DIR, filename)
    if os.path.exists(path):
        os.remove(path)
