"""Question-generation orchestration built on top of the LLM client.

The QGen class composes templates, the LLM client, and validation to
produce structured extractive and abstractive QA batches.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Literal, Optional

from .client import LLMClient
from .schemas import (
    AbstractiveBatch,
    ExtractiveBatch,
    TextRecord,
    abstractive_json_schema,
    extractive_json_schema,
)
from .temporal import verify_event_when_iso  # NEW
from .utils import build_env, json_loads_strict, render_template


class QGen:
    """High-level generator that produces QA batches from text records.

    Public methods:
        - generate_extractive_batch: produce extractive QA items
        - generate_abstractive_batch: produce abstractive QA items with evidence
    """

    def __init__(
        self,
        model: str,
        templates_dir: str = "qgen/templates",
        api_key: Optional[str] = None,
    ):
        """Create a QGen instance.

        Args:
            model: LLM model name for the underlying client.
            templates_dir: Directory with Jinja2 templates used to build prompts.
            api_key: Optional API key forwarded to the LLM client.
        """
        self.env = build_env(templates_dir)
        self.client = LLMClient(model=model, api_key=api_key)

    def _retry(self, fn, retries=2, backoff=1.5):
        """Retry helper: call ``fn`` up to ``retries`` times with exponential backoff.

        Args:
            fn: Callable with no arguments to execute.
            retries: Number of retry attempts after the first failure.
            backoff: Backoff base; sleep time grows as backoff ** attempt.
        """
        err = None
        for i in range(retries + 1):
            try:
                return fn()
            except Exception as e:  # pylint: disable=broad-exception-caught
                # Record last exception and sleep before next attempt
                err = e
                time.sleep(backoff ** (i + 1))
        raise err

    def _validate(
        self, payload: Dict[str, Any], mode: Literal["extractive", "abstractive"]
    ):
        """Validate a parsed payload against the selected Pydantic schema.

        Args:
            payload: The decoded JSON payload (mapping).
            mode: Either 'extractive' or 'abstractive' to select schema.

        Returns:
            Validated Pydantic model instance for the batch.
        """
        if mode == "extractive":
            return ExtractiveBatch.model_validate(payload)
        return AbstractiveBatch.model_validate(payload)

    def generate_extractive_batch(
        self,
        rec: TextRecord,
        k: int = 6,
        article_date: Optional[str] = None,
        dateline_location: Optional[str] = None,
    ) -> ExtractiveBatch:
        """Generate an extractive QA batch for a single input record.

        Args:
            rec: Input `TextRecord` being processed.
            k: Maximum number of items to request from the LLM.
            article_date: Optional article date used as temporal anchor.
            dateline_location: Optional dateline/location string.

        Returns:
            An `ExtractiveBatch` validated by pydantic.
        """

        schema = extractive_json_schema()
        prompt = render_template(
            self.env,
            "extractive_qa.j2",
            rec=rec.model_dump(),
            K=k,
            schema_json=schema,
            article_date=article_date,
            dateline_location=dateline_location,
        )

        def task():
            """Task executed with retries: call the LLM and validate output.

            This nested function is intentionally small and is retried via
            :meth:`_retry` to handle transient LLM errors.
            """
            json_str = self.client.generate_json(prompt, schema)
            data = json_loads_strict(json_str)
            batch = self._validate(data, "extractive")
            # enrich + temporal post-check
            for it in batch.items:
                it.meta.update(
                    {
                        "source_headings": [],
                        "chunk_id": f"{rec.source}:{rec.line_number}",
                    }
                )
                it.event_when_iso = verify_event_when_iso(
                    it.event_when_iso, anchor_date=article_date
                )
            return batch

        return self._retry(task)

    def generate_abstractive_batch(
        self,
        rec: TextRecord,
        k: int = 6,
        article_date: Optional[str] = None,
        dateline_location: Optional[str] = None,
    ) -> AbstractiveBatch:
        """Generate an abstractive QA batch (with evidence) for a record.

        Args:
            rec: Input `TextRecord` being processed.
            k: Maximum number of items to request from the LLM.
            article_date: Optional article date used as temporal anchor.
            dateline_location: Optional dateline/location string.

        Returns:
            An `AbstractiveBatch` validated by pydantic.
        """

        schema = abstractive_json_schema()
        prompt = render_template(
            self.env,
            "abstractive_evidence_qa.j2",
            rec=rec.model_dump(),
            K=k,
            schema_json=schema,
            article_date=article_date,
            dateline_location=dateline_location,
        )

        def task():
            """Nested task to call the LLM and validate abstractive output.

            Kept as a nested function so it can be retried by :meth:`_retry`.
            """
            json_str = self.client.generate_json(prompt, schema)
            data = json_loads_strict(json_str)
            batch = self._validate(data, "abstractive")
            for it in batch.items:
                it.meta.update(
                    {
                        "source_headings": [],
                        "chunk_id": f"{rec.source}:{rec.line_number}",
                    }
                )
                it.event_when_iso = verify_event_when_iso(
                    it.event_when_iso, anchor_date=article_date
                )
            return batch

        return self._retry(task)
