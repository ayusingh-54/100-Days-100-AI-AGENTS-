"""Small utility helpers for the Vibe Matcher prototype."""
from __future__ import annotations

import re
from typing import Optional


def normalize_text(text: str) -> str:
    """Normalize a short text: trim, lowercase, collapse whitespace, remove control chars.

    Args:
        text: input string

    Returns:
        Cleaned string
    """
    if text is None:
        return ""
    # Basic normalizations
    s = text.strip().lower()
    # replace newlines/tabs with space
    s = re.sub(r"[\r\n\t]+", " ", s)
    # collapse multiple spaces
    s = re.sub(r"\s+", " ", s)
    # remove uncommon control characters
    s = re.sub(r"[^\x20-\x7E\n]", "", s)
    return s


def ensure_two_words(text: Optional[str]) -> bool:
    """Return True when text looks like at least two words (simple guard for query input)."""
    if not text:
        return False
    parts = [p for p in re.split(r"\s+", text.strip()) if p]
    return len(parts) >= 2
