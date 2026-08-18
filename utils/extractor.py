"""
Rule/pattern-based extraction of action items, decisions, and
speaker-wise notes. Fully local, no ML model or API needed.
"""

import re

from utils.text_utils import split_sentences, parse_speaker_lines

ACTION_PATTERNS = [
    r"\bwill\s+(?:be\s+)?\w+",
    r"\bneed(?:s)?\s+to\b",
    r"\bhas\s+to\b",
    r"\bhave\s+to\b",
    r"\bshould\s+\w+",
    r"\bmust\s+\w+",
    r"\bgoing\s+to\b",
    r"\baction\s*item\b",
    r"\bassigned\s+to\b",
    r"\bfollow(?:s|ed)?\s*up\b",
    r"\bby\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow|next week|end of day|eod|\d{1,2}/\d{1,2})\b",
    r"\btake(?:s)?\s+care\s+of\b",
    r"\btodo\b",
    r"\bto-do\b",
]
_ACTION_RE = re.compile("|".join(ACTION_PATTERNS), re.IGNORECASE)

DECISION_PATTERNS = [
    r"\bwe\s+(?:have\s+)?decided\b",
    r"\bwe\s+agreed\b",
    r"\bagreed\s+that\b",
    r"\bfinal\s+(?:decision|call)\b",
    r"\bdecision\s+(?:was|is)\s+made\b",
    r"\bit\s+was\s+decided\b",
    r"\bconsensus\s+(?:was|is)\b",
    r"\bwe\s+will\s+go\s+with\b",
    r"\bconcluded\s+that\b",
    r"\bresolved\s+that\b",
    r"\bapproved\b",
    r"\bfinalized\b",
]
_DECISION_RE = re.compile("|".join(DECISION_PATTERNS), re.IGNORECASE)


def extract_action_items(text: str) -> list[str]:
    sentences = split_sentences(text)
    return [s for s in sentences if _ACTION_RE.search(s)]


def extract_decisions(text: str) -> list[str]:
    sentences = split_sentences(text)
    return [s for s in sentences if _DECISION_RE.search(s)]


def extract_speaker_breakdown(text: str) -> dict[str, list[str]]:
    """
    Group transcript lines by speaker. If no 'Name:' labels are found
    anywhere in the text, returns an empty dict (caller should treat
    this as 'no speaker info available').
    """
    parsed = parse_speaker_lines(text)
    has_any_speaker = any(speaker for speaker, _ in parsed)
    if not has_any_speaker:
        return {}

    breakdown: dict[str, list[str]] = {}
    current_speaker = "Unlabeled"
    for speaker, content in parsed:
        if speaker:
            current_speaker = speaker
        breakdown.setdefault(current_speaker, []).append(content)
    return breakdown
