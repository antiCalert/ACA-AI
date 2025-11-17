# qgen/generator.py (only the changed parts shown)
from __future__ import annotations
from typing import Iterable, List, Dict, Any, Literal, Optional
from pydantic import ValidationError
from .schemas import (
    TextRecord,
    ExtractiveBatch, extractive_json_schema,
    AbstractiveBatch, abstractive_json_schema,
)
from .client import LLMClient
from .utils import build_env, render_template, json_loads_strict
from .temporal import verify_event_when_iso   # NEW
import time

class QGen:
    def __init__(self, model: str, templates_dir: str = "qgen/templates", api_key: Optional[str] = None):
        self.env = build_env(templates_dir)
        self.client = LLMClient(model=model, api_key=api_key)
    
    def _retry(self, fn, retries=2, backoff=1.5):
        err = None
        for i in range(retries + 1):
            try:
                return fn()
            except Exception as e:
                err = e
                time.sleep(backoff ** (i + 1))
        raise err

    def _validate(self, payload: Dict[str, Any], mode: Literal["extractive", "abstractive"]):
        if mode == "extractive":
            return ExtractiveBatch.model_validate(payload)
        return AbstractiveBatch.model_validate(payload)

    def generate_extractive_batch(
        self,
        rec: TextRecord,
        K: int = 6,
        article_date: Optional[str] = None,
        dateline_location: Optional[str] = None,
    ) -> ExtractiveBatch:
        schema = extractive_json_schema()
        prompt = render_template(
            self.env, "extractive_qa.j2",
            rec=rec.model_dump(),
            K=K,
            schema_json=schema,
            article_date=article_date,
            dateline_location=dateline_location,
        )
        def task():
            json_str = self.client.generate_json(prompt, schema)
            data = json_loads_strict(json_str)
            batch = self._validate(data, "extractive")
            # enrich + temporal post-check
            for it in batch.items:
                it.meta.update({"source_headings": [], "chunk_id": f"{rec.source}:{rec.line_number}"})
                it.event_when_iso = verify_event_when_iso(it.event_when_iso, anchor_date=article_date)
            return batch
        return self._retry(task)

    def generate_abstractive_batch(
        self,
        rec: TextRecord,
        K: int = 6,
        article_date: Optional[str] = None,
        dateline_location: Optional[str] = None,
    ) -> AbstractiveBatch:
        schema = abstractive_json_schema()
        prompt = render_template(
            self.env, "abstractive_evidence_qa.j2",
            rec=rec.model_dump(),
            K=K,
            schema_json=schema,
            article_date=article_date,
            dateline_location=dateline_location,
        )
        def task():
            json_str = self.client.generate_json(prompt, schema)
            data = json_loads_strict(json_str)
            batch = self._validate(data, "abstractive")
            for it in batch.items:
                it.meta.update({"source_headings": [], "chunk_id": f"{rec.source}:{rec.line_number}"})
                it.event_when_iso = verify_event_when_iso(it.event_when_iso, anchor_date=article_date)
            return batch
        return self._retry(task)
