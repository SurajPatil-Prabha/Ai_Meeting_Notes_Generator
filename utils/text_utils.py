"""
Basic text utilities: cleaning + sentence splitting.
Deliberately avoids NLTK's punkt downloader (which needs internet at
runtime) so the app works fully offline, every time.
"""

import re


def clean_text(text: str) -> str:
    """Normalize whitespace and strip weird control characters."""
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# Matches sentence-ending punctuation followed by a space + capital letter,
# while avoiding common abbreviations (Mr., Dr., e.g., etc.) and decimals.
_ABBREVIATIONS = {
    "mr", "mrs", "ms", "dr", "prof", "sr", "jr", "vs", "etc",
    "e.g", "i.e", "inc", "ltd", "co", "st", "no",
}

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])")
_LEADING_SPEAKER_LABEL_RE = re.compile(r"^\s*(?:\[[\d:]+\]\s*)?[A-Za-z][A-Za-z .'-]{0,40}:\s*")


def strip_speaker_label(line: str) -> str:
    """Remove a leading 'Name:' or '[10:32] Name:' label from a line, if present."""
    return _LEADING_SPEAKER_LABEL_RE.sub("", line, count=1)


def split_sentences(text: str) -> list[str]:
    """Split raw text into sentences without external NLP downloads."""
    text = clean_text(text)
    if not text:
        return []

    # Remove speaker labels like "John: " or "[10:32] Sarah:" before splitting;
    # they're handled separately for speaker breakdown, and left in here would
    # pollute the summary/keywords with names.
    lines = text.split("\n")
    flat_text = " ".join(strip_speaker_label(line.strip()) for line in lines if line.strip())

    raw_sentences = _SENTENCE_SPLIT_RE.split(flat_text)

    sentences = []
    buffer = ""
    for chunk in raw_sentences:
        chunk = chunk.strip()
        if not chunk:
            continue
        buffer = (buffer + " " + chunk).strip() if buffer else chunk
        last_word = re.findall(r"[A-Za-z\.]+$", buffer)
        last_token = last_word[0].lower().rstrip(".") if last_word else ""
        if last_token in _ABBREVIATIONS:
            continue  # keep accumulating, don't treat as sentence end
        sentences.append(buffer)
        buffer = ""
    if buffer:
        sentences.append(buffer)

    # Filter out junk (too short to be a real sentence)
    return [s.strip() for s in sentences if len(s.strip()) > 3]


def parse_speaker_lines(text: str) -> list[tuple[str | None, str]]:
    """
    Parse transcript lines of the form 'Speaker Name: text...'
    Returns list of (speaker_or_None, text) tuples, preserving order.
    Lines without a recognizable 'Name:' prefix get speaker=None.
    """
    text = clean_text(text)
    lines = [l for l in text.split("\n") if l.strip()]

    speaker_pattern = re.compile(r"^\s*(?:\[[\d:]+\]\s*)?([A-Za-z][A-Za-z .'-]{0,40}):\s*(.+)$")

    result = []
    for line in lines:
        m = speaker_pattern.match(line)
        if m:
            speaker, content = m.group(1).strip(), m.group(2).strip()
            result.append((speaker, content))
        else:
            result.append((None, line.strip()))
    return result
