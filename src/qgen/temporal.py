# qgen/temporal.py
"""
Temporal helpers for verifying/normalizing ISO-8601 in news QA.

- verify_event_when_iso: sanity-checks model outputs and (optionally)
  re-normalizes using rule-based taggers (SUTime or HeidelTime) when available.

This module is designed so you can plug in one of:
  * SUTime (Stanford CoreNLP) server or CLI
  * HeidelTime (UIMA/standalone)

Both are rule-based temporal taggers widely used for TIMEX3 normalization.
"""

from __future__ import annotations
from typing import Optional
import re
import os

ISO_DATE_RE = re.compile(r"^\d{4}(-\d{2}){0,2}$")
ISO_INTERVAL_RE = re.compile(r"^\d{4}(-\d{2}){0,2}\/\d{4}(-\d{2}){0,2}$")


def _looks_iso(s: str) -> bool:
    return bool(ISO_DATE_RE.match(s) or ISO_INTERVAL_RE.match(s))


def verify_event_when_iso(
    s: Optional[str], anchor_date: Optional[str]
) -> Optional[str]:
    """
    If s already looks ISO, keep it. Otherwise, attempt to normalize via SUTime/HeidelTime
    when configured; if unavailable or fails, return None to avoid false precision.
    """
    if s is None or s.strip() == "":
        return None
    s = s.strip()
    if _looks_iso(s):
        return s

    # Optional: attempt normalization via configured backend(s)
    backend = os.getenv("QGEN_TIME_BACKEND", "").lower()  # 'sutime' | 'heideltime' | ''
    if backend == "sutime":
        norm = _normalize_with_sutime(s, anchor_date)
        return norm if norm and _looks_iso(norm) else None
    if backend == "heideltime":
        norm = _normalize_with_heideltime(s, anchor_date)
        return norm if norm and _looks_iso(norm) else None

    return None


# --- Example stubs. Replace with your integration of choice. ---
def _normalize_with_sutime(text: str, anchor: Optional[str]) -> Optional[str]:
    """
    Example: call a local CoreNLP server or CLI and map SUTime TIMEX3 'value' to ISO date or interval.
    For a quick start, run CoreNLP server with SUTime annotator and query it here.
    """
    # Placeholder: implement your call here. Return ISO string or None.
    return None


def _normalize_with_heideltime(text: str, anchor: Optional[str]) -> Optional[str]:
    """
    Example: call HeidelTime standalone JAR and parse output (TIMEX3 value attribute).
    """
    # Placeholder: implement your call here. Return ISO string or None.
    return None
