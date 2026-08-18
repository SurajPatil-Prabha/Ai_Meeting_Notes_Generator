"""
Local meeting analytics: sentiment scoring, talk-time distribution,
action-item priority tagging, and summary stats. All rule/lexicon-based —
no API, no external model download.
"""

import re

from utils.text_utils import split_sentences

# --- Sentiment -------------------------------------------------------------
# Small curated lexicons. Not as accurate as a trained model, but fully
# local, instant, and dependency-free.
POSITIVE_WORDS = {
    "great", "good", "excellent", "agree", "agreed", "awesome", "happy",
    "glad", "love", "like", "success", "successful", "progress", "improve",
    "improved", "improvement", "positive", "win", "wins", "achieve",
    "achieved", "confident", "excited", "pleased", "thanks", "thank",
    "appreciate", "solid", "smooth", "resolved", "helpful", "on track",
    "ahead of schedule", "well done", "nice", "perfect", "works",
}
NEGATIVE_WORDS = {
    "bad", "issue", "issues", "problem", "problems", "concern", "concerns",
    "concerned", "delay", "delayed", "blocked", "blocker", "risk", "risks",
    "fail", "failed", "failure", "worried", "worry", "difficult", "hard",
    "confused", "confusing", "disagree", "unfortunately", "behind",
    "behind schedule", "broken", "bug", "bugs", "urgent", "critical",
    "frustrated", "frustrating", "stuck", "cancel", "cancelled", "delayed",
    "missed", "miss", "overdue", "escalate", "escalation",
}

_WORD_RE = re.compile(r"[a-zA-Z']+")


def sentiment_score(text: str) -> dict:
    """Returns {'label': 'Positive'|'Neutral'|'Negative', 'score': float}
    where score is in [-1, 1]."""
    words = [w.lower() for w in _WORD_RE.findall(text or "")]
    if not words:
        return {"label": "Neutral", "score": 0.0}

    pos = sum(1 for w in words if w in POSITIVE_WORDS)
    neg = sum(1 for w in words if w in NEGATIVE_WORDS)
    total_hits = pos + neg
    if total_hits == 0:
        return {"label": "Neutral", "score": 0.0}

    score = (pos - neg) / max(len(words), 1) * 10  # scaled for readability
    score = max(-1.0, min(1.0, score))

    if score > 0.08:
        label = "Positive"
    elif score < -0.08:
        label = "Negative"
    else:
        label = "Neutral"
    return {"label": label, "score": round(score, 3)}


def speaker_sentiment(speaker_notes: dict) -> dict:
    """speaker -> sentiment dict, computed from their concatenated lines."""
    result = {}
    for speaker, lines in (speaker_notes or {}).items():
        joined = " ".join(lines)
        result[speaker] = sentiment_score(joined)
    return result


# --- Talk-time distribution --------------------------------------------------

def talk_time_distribution(speaker_notes: dict) -> dict:
    """speaker -> {'words': int, 'pct': float} based on word count share.
    A rough proxy for airtime since we don't have real audio timestamps
    for pasted/uploaded text transcripts."""
    if not speaker_notes:
        return {}

    counts = {
        speaker: sum(len(_WORD_RE.findall(line)) for line in lines)
        for speaker, lines in speaker_notes.items()
    }
    total = sum(counts.values()) or 1
    return {
        speaker: {"words": c, "pct": round(c / total * 100, 1)}
        for speaker, c in counts.items()
    }


# --- Meeting-level stats -----------------------------------------------------

AVG_SPEAKING_WPM = 130   # rough average conversational speaking rate
AVG_READING_WPM = 200    # rough average silent reading rate


def meeting_stats(text: str) -> dict:
    words = _WORD_RE.findall(text or "")
    word_count = len(words)
    sentence_count = len(split_sentences(text or ""))
    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "est_duration_min": round(word_count / AVG_SPEAKING_WPM, 1) if word_count else 0.0,
        "est_reading_min": round(word_count / AVG_READING_WPM, 1) if word_count else 0.0,
    }


# --- Action item priority tagging --------------------------------------------

URGENT_WORDS = {"urgent", "asap", "immediately", "critical", "right away", "today", "now"}
HIGH_WORDS = {"tomorrow", "eod", "end of day", "by friday", "this week", "important", "priority"}
DATE_HINT_RE = re.compile(
    r"\bby\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow|next week|end of day|eod|\d{1,2}/\d{1,2})\b",
    re.IGNORECASE,
)


def tag_priority(action_item_text: str) -> str:
    """Returns 'Urgent' | 'High' | 'Normal' based on keyword/date cues."""
    lowered = (action_item_text or "").lower()
    if any(w in lowered for w in URGENT_WORDS):
        return "Urgent"
    if any(w in lowered for w in HIGH_WORDS) or DATE_HINT_RE.search(lowered):
        return "High"
    return "Normal"


def tag_action_items(action_items: list[str]) -> list[dict]:
    return [{"text": item, "priority": tag_priority(item)} for item in (action_items or [])]
