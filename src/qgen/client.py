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
        self.client = genai.Client(api_key=api_key or os.getenv("GOOGLE_AI_STUDIO_API_KEY"))
        self.model = model
        # allow an optional system_instruction in defaults
        self.defaults = {"temperature": 0.2, "max_output_tokens": 2048, "system_instruction": "", **defaults}

    def generate_json(self, prompt: str, json_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate JSON strictly adhering to json_schema using Google GenAI.
        Returns a parsed dict when possible, otherwise returns {"_raw": "<text>"}.
        """
        base_sys = self.defaults.get("system_instruction", "") or ""
        schema_note = ''
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
        # gather text parts from the first candidate
        candidate = response.candidates[0]
        for part in candidate.content.parts:
            if getattr(part, "text", None):
                parts.append(part.text)

        text = "".join(parts).strip()
        # print("LLMClient received text:", text)

        return text

        # try:
        #     return json.loads(text)
        # except Exception:
        #     return {"_raw": text}

# from openai import OpenAI  # pip install openai>=1.40

# class LLMClientOAI:
#     """
#     Thin wrapper around OpenAI Responses API using Structured Outputs.
#     Docs: Structured outputs & Responses API.
#     """
#     def __init__(self, model: str, api_key: Optional[str] = None, **defaults: Any):
#         self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
#         self.model = model
#         self.defaults = {"temperature": 0.2, "max_output_tokens": 2048, **defaults}

#     def generate_json(self, prompt: str, json_schema: Dict[str, Any]) -> Dict[str, Any]:
#         """
#         Request JSON strictly adhering to json_schema.
#         """
#         resp = self.client.responses.create(
#             model=self.model,
#             input=[{"role": "user", "content": prompt}],
#             response_format={"type": "json_schema", "json_schema": json_schema, "strict": True},
#             **self.defaults,
#         )
#         # .output[0].content[0].text is common; SDK also offers .output_text
#         return resp.output[0].content[0].text  # JSON string
