# qgen/schemas.py
from __future__ import annotations
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
import re

# ---- ISO-8601 date or interval (basic check; full semantics verified in temporal.py) ----
# Accepts YYYY-MM-DD, YYYY-MM, YYYY, and intervals like start/end
ISO_DATE_RE = re.compile(r"^\d{4}(-\d{2}){0,2}$")
ISO_INTERVAL_RE = re.compile(
    r"^(?P<start>\d{4}(-\d{2}){0,2})\/(?P<end>\d{4}(-\d{2}){0,2})$"
)


def _is_iso8601_date_or_interval(s: str) -> bool:
    return bool(ISO_DATE_RE.match(s) or ISO_INTERVAL_RE.match(s))


# ---- Common dataset record ----
class TextRecord(BaseModel):
    text: str
    source: str
    title: str
    line_number: int


# ---- Shared news/analysis fields (mixin) ----
class NewsFields(BaseModel):
    event_when_iso: Optional[str] = Field(
        default=None,
        description="ISO-8601 date or start/end interval, e.g., '2025-11-12' or '2025-11-10/2025-11-13'",
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
                "event_when_iso must be ISO-8601 date or interval (YYYY[-MM[-DD]] or start/end)"
            )
        return v


# ---- Base citation ----
class Citation(BaseModel):
    source: str
    title: str
    line_number: int
    start_char: Optional[int] = None
    end_char: Optional[int] = None


# ---- Extractive QA (A) ----
class ExtractiveItem(NewsFields):
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
    items: List[ExtractiveItem]
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ---- Abstractive w/ Evidence (B) ----
class EvidenceCitation(Citation):
    evidence_sentences: List[str] = Field(
        description="Exact sentences from the context that support the answer"
    )


class AbstractiveItem(NewsFields):
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
    items: List[AbstractiveItem]
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# Helpers to emit JSON Schema for OpenAI Structured Outputs
def extractive_json_schema() -> dict:
    return ExtractiveBatch.model_json_schema()


def abstractive_json_schema() -> dict:
    return AbstractiveBatch.model_json_schema()
