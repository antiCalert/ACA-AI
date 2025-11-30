# qgen/client.py
from __future__ import annotations
import os
from typing import Any, Dict, Optional
from google import genai
from google.genai import types
import json


class LLMClient:
    """
    Thin wrapper around Google GenAI models to produce JSON outputs matching a schema.
    """

    def __init__(self, model: str, api_key: Optional[str] = None, **defaults: Any):
        self.client = genai.Client(
            api_key=api_key or os.getenv("GOOGLE_AI_STUDIO_API_KEY")
        )
        self.model = model
        # allow an optional system_instruction in defaults
        self.defaults = {
            "temperature": 0.2,
            "max_output_tokens": 2048,
            "system_instruction": "",
            **defaults,
        }

    def generate_json(self, prompt: str, json_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate JSON strictly adhering to json_schema using Google GenAI.
        Returns a parsed dict when possible, otherwise returns {"_raw": "<text>"}.
        """
        base_sys = self.defaults.get("system_instruction", "") or ""
        schema_note = ""
        system_instruction = base_sys + schema_note

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            thinking_config=types.ThinkingConfig(thinking_budget=-1),
            response_modalities=["Text"],
            response_mime_type="application/json",
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=[prompt],
            config=config,
        )

        parts: list[str] = []

        # gather text parts from the first candidate if available
        try:
            candidate = response.candidates[0]
        except Exception:
            return {"_raw": ""}

        for part in getattr(candidate.content, "parts", []) or []:
            txt = getattr(part, "text", None)
            if txt:
                parts.append(txt)

        text = "".join(parts).strip()

        # Try to parse JSON; if parsing fails, return raw text under _raw
        if not text:
            return ""

        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return text
        except Exception:
            return ""
