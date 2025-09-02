from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel


@dataclass
class LLMResponse:
    output_parsed: BaseModel
    output_text: str


def _join_messages_as_text(messages: List[Dict[str, Any]]) -> str:
    parts: List[str] = []
    for msg in messages:
        content = msg.get("content", "")
        if not isinstance(content, str):
            try:
                content = str(content)
            except Exception:
                content = ""
        parts.append(content)
    return "\n\n".join([p for p in parts if p])


def generate_structured(
    *,
    messages: List[Dict[str, Any]],
    response_model: Type[BaseModel],
    model: str,
    reasoning_effort: Optional[str] = None,
    timeout: Optional[float] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
) -> LLMResponse:
    """Provider-agnostic structured generation.

    Selects provider via env var LLM_PROVIDER: 'openai' (default) or 'google'.
    - OpenAI: uses Responses API parse with Pydantic
    - Google: uses google-genai with response_schema=Pydantic model
    """
    provider = (os.getenv("LLM_PROVIDER", "openai") or "openai").lower()

    if provider == "google":
        # Lazy import to avoid requiring the dependency when unused
        from google import genai  # type: ignore

        client = genai.Client()
        contents = _join_messages_as_text(messages)
        cfg: Dict[str, Any] = {
            "response_mime_type": "application/json",
            "response_schema": response_model,
        }
        resp = client.models.generate_content(
            model=model,
            contents=contents,
            config=cfg,
        )
        text = getattr(resp, "text", "") or ""
        parsed = getattr(resp, "parsed", None)
        if parsed is None:
            # Best-effort: attempt to parse from text using the Pydantic model
            parsed = response_model.model_validate_json(text)
        return LLMResponse(output_parsed=parsed, output_text=text)

    # Default: OpenAI-compatible provider (OpenAI or Ollama via base URL)
    from openai import OpenAI  # type: ignore

    client = OpenAI(timeout=timeout)
    resp = client.responses.parse(
        model=model,
        input=messages,
        tools=tools or [],
        reasoning={"effort": reasoning_effort} if reasoning_effort else None,
        text_format=response_model,
    )
    return LLMResponse(output_parsed=resp.output_parsed, output_text=resp.output_text)


