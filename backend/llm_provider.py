from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type
import random

from pydantic import BaseModel


@dataclass
class LLMResponse:
    output_parsed: BaseModel
    output_text: str


class GroqRetriesExhaustedError(RuntimeError):
    """Raised when Groq chat.completions.create fails after all retry attempts."""


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

    Selects provider via LLM_PROVIDER env (openai|google|groq) with auto-detection:
    - If model is 'openai/gpt-oss-120b' and GROQ_API_KEY is set, route to Groq
    - Google: uses google-genai with response_schema=Pydantic model
    - OpenAI-compatible: uses Responses API parse with Pydantic
    """
    provider = (os.getenv("LLM_PROVIDER", "openai") or "openai").lower()
    if (model == "openai/gpt-oss-120b") and os.getenv("GROQ_API_KEY"):
        provider = "groq"

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

    if provider == "groq":
        # Use Groq Chat Completions with JSON schema response_format
        from groq import Groq  # type: ignore
        import json as _json

        # Configure a long timeout for Groq requests (default 30 minutes)
        groq_timeout: float = (
            float(timeout) if timeout is not None else float(os.getenv("GROQ_TIMEOUT_SECONDS", "1800"))
        )
        # Allow configuring the maximum completion tokens (default to 90k)
        groq_max_completion_tokens: int = int(os.getenv("GROQ_MAX_COMPLETION_TOKENS", "65536"))
        try:
            client = Groq(timeout=groq_timeout)
            _timeout_in_kwargs = False
        except TypeError:
            # Older SDKs may not support timeout on the client; pass per-request instead
            client = Groq()
            _timeout_in_kwargs = True
        groq_kwargs: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "structured_output",
                    "schema": response_model.model_json_schema(),
                },
            },
            "reasoning_format": "hidden",
            "temperature": 0.8,
            "top_p": 1,
            "max_completion_tokens": groq_max_completion_tokens,
        }
        if _timeout_in_kwargs:
            groq_kwargs["timeout"] = groq_timeout
        if reasoning_effort:
            groq_kwargs["reasoning_effort"] = reasoning_effort
        max_attempts: int = int(os.getenv("GROQ_MAX_RETRIES", "10"))
        attempt: int = 0
        last_exception: Optional[Exception] = None
        messages_patched: bool = False
        while attempt < max_attempts:
            try:
                resp = client.chat.completions.create(**groq_kwargs)
                text = (getattr(resp.choices[0].message, "content", None) or "")
                # Try strict JSON then fallback to pydantic JSON parsing; if both fail, retry
                try:
                    raw = _json.loads(text or "{}")
                    parsed = response_model.model_validate(raw)
                    return LLMResponse(output_parsed=parsed, output_text=_json.dumps(raw, ensure_ascii=False))
                except Exception:
                    try:
                        parsed = response_model.model_validate_json(text)
                        return LLMResponse(output_parsed=parsed, output_text=text)
                    except Exception as parse_exc:
                        last_exception = parse_exc
                        # Treat parsing errors as retryable
                        if not messages_patched:
                            try:
                                schema_json = _json.dumps(response_model.model_json_schema(), ensure_ascii=False)
                            except Exception:
                                schema_json = "{}"
                            repair_messages = list(messages) + [
                                {
                                    "role": "user",
                                    "content": (
                                        "Return ONLY a valid JSON object that conforms exactly to the following JSON Schema. "
                                        "Do not include any prose, code fences, or extra text. Output a single JSON object.\n"
                                        f"JSON Schema:\n{schema_json}"
                                    ),
                                }
                            ]
                            groq_kwargs["messages"] = repair_messages
                            groq_kwargs["max_completion_tokens"] = groq_max_completion_tokens
                            messages_patched = True
                        attempt += 1
                        time.sleep(1.0)
                        continue
            except Exception as e:
                last_exception = e
                err_str = str(e)
                if (("json_validate_failed" in err_str) or ("max completion tokens" in err_str)) and not messages_patched:
                    try:
                        schema_json = _json.dumps(response_model.model_json_schema(), ensure_ascii=False)
                    except Exception:
                        schema_json = "{}"
                    repair_messages = list(messages) + [
                        {
                            "role": "user",
                            "content": (
                                "Return ONLY a valid JSON object that conforms exactly to the following JSON Schema. "
                                "Do not include any prose, code fences, or extra text. Output a single JSON object.\n"
                                f"JSON Schema:\n{schema_json}"
                            ),
                        }
                    ]
                    groq_kwargs["messages"] = repair_messages
                    groq_kwargs["max_completion_tokens"] = groq_max_completion_tokens
                    messages_patched = True
                attempt += 1
                time.sleep(1.0)
        raise GroqRetriesExhaustedError(
            f"Groq request failed after {max_attempts} attempts. Last error: {last_exception}"
        )

    # Default: OpenAI-compatible provider (OpenAI or Ollama via base URL)
    from openai import OpenAI  # type: ignore
    try:  # Best-effort import across SDK versions
        from openai import (
            APITimeoutError,
            APIConnectionError,
            RateLimitError,
            InternalServerError,
            APIStatusError,
        )  # type: ignore
    except Exception:  # pragma: no cover
        APITimeoutError = Exception  # type: ignore
        APIConnectionError = Exception  # type: ignore
        RateLimitError = Exception  # type: ignore
        InternalServerError = Exception  # type: ignore
        APIStatusError = Exception  # type: ignore

    client = OpenAI(timeout=timeout)
    # Simple retry loop for transient/network/server errors
    try:
        max_retries = max(0, int(os.getenv("OPENAI_RETRY_ATTEMPTS", "4")))
    except Exception:
        max_retries = 4
    try:
        base_backoff = max(0.1, float(os.getenv("OPENAI_RETRY_BACKOFF_SECONDS", "2")))
    except Exception:
        base_backoff = 2.0

    def _should_retry_error(e: Exception) -> bool:
        if isinstance(e, (APITimeoutError, APIConnectionError, RateLimitError, InternalServerError)):
            return True
        if isinstance(e, APIStatusError):
            try:
                status = int(getattr(e, "status_code", 0) or 0)
            except Exception:
                status = 0
            return 500 <= status < 600
        return False

    attempt = 0
    while True:
        try:
            resp = client.responses.parse(
                model=model,
                input=messages,
                tools=tools or [],
                reasoning={"effort": reasoning_effort} if reasoning_effort else None,
                text_format=response_model,
            )
            break
        except Exception as e:
            if attempt < max_retries and _should_retry_error(e):
                delay = base_backoff * (2 ** attempt) + random.uniform(0, base_backoff)
                time.sleep(min(60.0, delay))
                attempt += 1
                continue
            raise
    return LLMResponse(output_parsed=resp.output_parsed, output_text=resp.output_text)


