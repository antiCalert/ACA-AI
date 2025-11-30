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

import os
import re
from typing import Optional

ISO_DATE_RE = re.compile(r"^\d{4}(-\d{2}){0,2}$")
ISO_INTERVAL_RE = re.compile(
    (
        r"^\d{4}(-\d{2}){0,2}\/"
        r"\d{4}(-\d{2}){0,2}$"
    )
)


def _looks_iso(s: str) -> bool:
    return bool(ISO_DATE_RE.match(s) or ISO_INTERVAL_RE.match(s))


def verify_event_when_iso(
    s: Optional[str], anchor_date: Optional[str]
) -> Optional[str]:
    """Verify or normalize an ISO-8601 date/interval string.

    If ``s`` already looks like an ISO date or interval, return it unchanged.
    Otherwise, attempt to normalize using a configured backend (SUTime or
    HeidelTime). If no backend is configured or normalization fails, return
    ``None`` to avoid returning a falsely precise value.
    """
    if s is None or s.strip() == "":
        return None
    s = s.strip()
    if _looks_iso(s):
        return s

    # Optional: attempt normalization via configured backend(s)
    backend = os.getenv("QGEN_TIME_BACKEND", "").lower()  # 'sutime' | 'heideltime' | ''
    if backend == "sutime":
        # _normalize_with_sutime is a pluggable backend and may be a stub in
        # some environments; suppress assignment-from-none which arises when
        # the function body is a placeholder returning None.
        # pylint: disable=assignment-from-none
        norm = _normalize_with_sutime(s, anchor_date)
        # pylint: enable=assignment-from-none
        return norm if norm and _looks_iso(norm) else None
    if backend == "heideltime":
        # pylint: disable=assignment-from-none
        norm = _normalize_with_heideltime(s, anchor_date)
        # pylint: enable=assignment-from-none
        return norm if norm and _looks_iso(norm) else None

    return None


# --- Example stubs. Replace with your integration of choice. ---
def _normalize_with_sutime(_text: str, _anchor: Optional[str]) -> Optional[str]:
    """Example stub for SUTime integration.

    In a real integration you would call a local CoreNLP server or CLI and
    map the SUTime TIMEX3 ``value`` attribute to an ISO date or interval.
    For a quick start, run the CoreNLP server with the SUTime annotator and
    query it from this helper.
    """
    # Placeholder: implement your call here. Return ISO string or None.
    return None


def _normalize_with_heideltime(_text: str, _anchor: Optional[str]) -> Optional[str]:
    """Example stub for HeidelTime integration.

    Call a standalone HeidelTime JAR and parse the TIMEX3 ``value`` attribute
    into an ISO string, returning it or ``None`` on failure.
    """
    # Placeholder: implement your call here. Return ISO string or None.
    return None
