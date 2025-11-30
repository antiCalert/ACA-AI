"""Pydantic models and helpers for the QA data structures used by QGen.

This module defines the small set of Pydantic models that represent input
records and the structured extractive/abstractive QA outputs. It also
exposes helpers that return JSON Schema for model-driven prompt construction.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

# ---- ISO-8601 date or interval (full semantics verified in temporal.py) ----
# Accepts YYYY-MM-DD, YYYY-MM, YYYY, and intervals like start/end
ISO_DATE_RE = re.compile(r"^\d{4}(-\d{2}){0,2}$")
ISO_INTERVAL_RE = re.compile(
    (
        r"^(?P<start>\d{4}(-\d{2}){0,2})\/"
        r"(?P<end>\d{4}(-\d{2}){0,2})$"
    )
)


def _is_iso8601_date_or_interval(s: str) -> bool:
    return bool(ISO_DATE_RE.match(s) or ISO_INTERVAL_RE.match(s))


# ---- Common dataset record ----
class TextRecord(BaseModel):
    """A single input text record from the corpus.

    Attributes correspond to the simple line-oriented dataset format used by
    the project: text, source filename, title and a 1-based line number.
    """

    text: str
    source: str
    title: str
    line_number: int


# ---- Shared news/analysis fields (mixin) ----
class NewsFields(BaseModel):
    """Mixin with common news analysis fields used by item models.

    This mixin is inherited by the extractive and abstractive QA item models
    to provide fields like event_when_iso, actors, evidence_citations, and
    meta information.
    """
    event_when_iso: Optional[str] = Field(
        default=None,
        description=(
            "ISO-8601 date or start/end interval, e.g., '2025-11-12' or "
            "'2025-11-10/2025-11-13'"
        ),
    )
    event_where: Optional[str] = Field(
        default=None, description="Canonical place name from the text"
    )
    actors: List[str] = Field(
        default_factory=list, description="Principal entities mentioned"
    )
    progression: Literal["precursor", "ongoing", "aftermath", "retrospective"] = (
        "ongoing"
    )
    analysis_tags: List[
        Literal[
            "policy",
            "market",
            "geopolitics",
            "risk",
            "forecast",
            "law",
            "security",
            "trade",
            "macro",
        ]
    ] = Field(default_factory=list)
    stance: Literal["neutral", "pro", "con", "mixed", "unclear"] = "neutral"

    # Allow one or many supporting spans
    evidence_citations: List["Citation"] = Field(default_factory=list)

    @field_validator("event_when_iso")
    @classmethod
    def _validate_when(cls, v):
        if v is None:
            return v
        if not _is_iso8601_date_or_interval(v):
            raise ValueError(
                (
                    "event_when_iso must be ISO-8601 date or interval "
                    "(YYYY[-MM[-DD]] or start/end)"
                )
            )
        return v


# ---- Base citation ----
class Citation(BaseModel):
    """Reference to a span inside a source record used as supporting evidence.

    Contains the source, title and optional character offsets.
    """
    source: str
    title: str
    line_number: int
    start_char: Optional[int] = None
    end_char: Optional[int] = None


# ---- Extractive QA (A) ----
class ExtractiveItem(NewsFields):
    """A single extractive QA item: question, answer span, and metadata.

    The answer is expected to be a verbatim span from the source text and
    optional character offsets may be provided.
    """
    question: str
    answer: str  # verbatim span from `text`
    answer_span_start: Optional[int] = None
    answer_span_end: Optional[int] = None
    difficulty: Literal["easy", "medium", "hard"]
    type: Literal[
        "event_basic",
        "timeline",
        "causal",
        "comparative",
        "numerical",
        "definition",
        "howto",
        "fact",
    ] = "event_basic"
    citation: Citation
    meta: dict = Field(default_factory=dict)

    @model_validator(mode="after")
    def _span_consistency(self):
        # If spans are provided, check order and that citation exists
        if self.answer_span_start is not None and self.answer_span_end is not None:
            if (
                self.answer_span_start < 0
                or self.answer_span_end < self.answer_span_start
            ):
                raise ValueError("answer_span_start/end invalid")
        return self


class ExtractiveBatch(BaseModel):
    """Container for a batch of extractive QA items produced for a record.

    The `created_at` field records the batch creation time (UTC ISO string).
    """
    items: List[ExtractiveItem]
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ---- Abstractive w/ Evidence (B) ----
class EvidenceCitation(Citation):
    """Citation extended with supporting sentences used by abstractive QA."""
    evidence_sentences: List[str] = Field(
        description="Exact sentences from the context that support the answer"
    )


class AbstractiveItem(NewsFields):
    """A single abstractive QA item with evidence citation and faithfulness.

    This item contains a synthesized answer and metadata about faithfulness
    and supporting evidence sentences.
    """
    question: str
    answer: str  # grounded synthesis
    difficulty: Literal["easy", "medium", "hard"]
    type: Literal[
        "event_basic",
        "timeline",
        "causal",
        "comparative",
        "numerical",
        "definition",
        "analysis",
    ] = "analysis"
    citation: EvidenceCitation
    faithfulness_claim: Literal["supported", "contradicted", "insufficient"]
    meta: dict = Field(default_factory=dict)


class AbstractiveBatch(BaseModel):
    """Container for a batch of abstractive QA items."""
    items: List[AbstractiveItem]
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# Helpers to emit JSON Schema for OpenAI Structured Outputs
def extractive_json_schema() -> dict:
    """Return the JSON Schema for the extractive batch model.

    This is used to pass a strict schema to the LLM when requesting
    structured JSON outputs.
    """
    return ExtractiveBatch.model_json_schema()


def abstractive_json_schema() -> dict:
    """Return the JSON Schema for the abstractive batch model."""
    return AbstractiveBatch.model_json_schema()
