from __future__ import annotations

import json
import os
import time
import random
from typing import Any, Dict, List, Optional, Callable, Tuple
import logging

from pydantic import BaseModel

from .llm_provider import LLMResponse


def _collect_text_from_response(resp: Any) -> str:
    """Best-effort extraction of assistant text from a Responses API response."""
    text = getattr(resp, "output_text", None)
    if isinstance(text, str) and text.strip():
        return text
    # Fallback: concatenate textual parts from output
    parts: List[str] = []
    for item in getattr(resp, "output", []) or []:
        # item may be a message with .content list
        if getattr(item, "type", None) == "message":
            content_list = getattr(item, "content", []) or []
            for c in content_list:
                if getattr(c, "type", None) == "output_text":
                    val = getattr(c, "text", "") or ""
                    if val:
                        parts.append(val)
        elif getattr(item, "type", None) == "output_text":
            val = getattr(item, "text", "") or ""
            if val:
                parts.append(val)
    return "\n".join([p for p in parts if p])


def _find_tool_uses(resp: Any) -> List[Any]:
    tool_uses: List[Any] = []
    for item in getattr(resp, "output", []) or []:
        if getattr(item, "type", None) == "tool_use":
            tool_uses.append(item)
        # Some SDK variants pack tool uses inside message.content
        if getattr(item, "type", None) == "message":
            for c in getattr(item, "content", []) or []:
                if getattr(c, "type", None) == "tool_use":
                    tool_uses.append(c)
    return tool_uses


def generate_structured_with_tools(
    *,
    messages: List[Dict[str, Any]],
    response_model: type[BaseModel],
    model: str,
    tools: Optional[List[Dict[str, Any]]] = None,
    tool_registry: Optional[Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]]] = None,
    reasoning_effort: Optional[str] = None,
    timeout: Optional[float] = None,
) -> LLMResponse:
    """Tool-aware structured generation using OpenAI Responses API.

    - Supports built-in tools like {"type": "web_search"}
    - Supports function tools by executing local callables from tool_registry and
      submitting their outputs via submit_tool_outputs
    - Returns LLMResponse with output_parsed (Pydantic) and output_text (raw JSON string)
    """
    logger = logging.getLogger("ToolLLM")
    provider = (os.getenv("LLM_PROVIDER", "openai") or "openai").lower()

    if provider == "google":
        # Fall back to provider-agnostic structured call without tool loop
        # Tools are not supported in this simplified Google path
        from llm_provider import generate_structured as _gen

        return _gen(
            messages=messages,
            response_model=response_model,
            model=model,
            reasoning_effort=reasoning_effort,
            timeout=timeout,
        )

    # For Groq, there is no tool-use loop supported; fall back to provider-agnostic call
    if provider == "groq":
        from llm_provider import generate_structured as _gen
        return _gen(
            messages=messages,
            response_model=response_model,
            model=model,
            reasoning_effort=reasoning_effort,
            timeout=timeout,
        )

    from openai import OpenAI  # type: ignore
    try:  # Best-effort import of typed exceptions across SDK versions
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

    # Retry configuration (env-tunable)
    try:
        max_retries = max(0, int(os.getenv("OPENAI_RETRY_ATTEMPTS", "4")))
    except Exception:
        max_retries = 4
    try:
        base_backoff = max(0.1, float(os.getenv("OPENAI_RETRY_BACKOFF_SECONDS", "2")))
    except Exception:
        base_backoff = 2.0

    def _sleep_backoff(attempt: int) -> None:
        # Exponential backoff with jitter
        delay = base_backoff * (2 ** attempt)
        jitter = random.uniform(0, base_backoff)
        time.sleep(min(60.0, delay + jitter))

    def _should_retry_error(e: Exception) -> bool:
        if isinstance(e, (APITimeoutError, APIConnectionError, RateLimitError, InternalServerError)):
            return True
        # Treat generic 5xx status codes as retryable if surfaced as APIStatusError
        if isinstance(e, APIStatusError):
            try:
                status = int(getattr(e, "status_code", 0) or 0)
            except Exception:
                status = 0
            return 500 <= status < 600
        return False

    def _parse_with_retry(*, input_messages: List[Dict[str, Any]]) -> Any:
        attempt = 0
        while True:
            try:
                return client.responses.parse(
                    model=model,
                    input=input_messages,
                    tools=tools or [],
                    reasoning={"effort": reasoning_effort} if reasoning_effort else None,
                    text_format=response_model,
                )
            except Exception as e:  # pragma: no cover
                if attempt < max_retries and _should_retry_error(e):
                    logger.warning(
                        "[ToolLLM] parse failed (attempt %d/%d): %s",
                        attempt + 1,
                        max_retries + 1,
                        e,
                    )
                    _sleep_backoff(attempt)
                    attempt += 1
                    continue
                raise

    def _submit_tool_outputs_with_retry(*, response_id: str, tool_outputs: List[Dict[str, str]]) -> Any:
        attempt = 0
        while True:
            try:
                return client.responses.submit_tool_outputs(
                    response_id=response_id,
                    tool_outputs=tool_outputs,
                )
            except Exception as e:  # pragma: no cover
                if attempt < max_retries and _should_retry_error(e):
                    logger.warning(
                        "[ToolLLM] submit_tool_outputs failed (attempt %d/%d): %s",
                        attempt + 1,
                        max_retries + 1,
                        e,
                    )
                    _sleep_backoff(attempt)
                    attempt += 1
                    continue
                raise

    # First request via parse to get Pydantic-typed output enforced by the model
    logger.info(
        "[ToolLLM] parse: model=%s tools=%s reasoning=%s",
        model,
        [t.get("type") or t.get("name") for t in (tools or [])],
        reasoning_effort,
    )
    resp = _parse_with_retry(input_messages=messages)

    # Tool-use loop
    while True:
        all_tool_uses = _find_tool_uses(resp)
        logger.info("[ToolLLM] tool_uses received: total=%d", len(all_tool_uses))
        # Only handle local function tools that we registered
        tool_uses = [tu for tu in all_tool_uses if tool_registry and getattr(tu, "name", None) in tool_registry]
        if all_tool_uses and not tool_uses:
            logger.info("[ToolLLM] only non-local tools requested; no local executions needed")
        if not tool_uses:
            break
        outputs: List[Dict[str, str]] = []
        for tu in tool_uses:
            name = getattr(tu, "name", None) or getattr(tu, "tool_name", None)
            call_id = getattr(tu, "id", None) or getattr(tu, "tool_call_id", None)
            # Inputs may be available as a dict or JSON string
            tool_input = getattr(tu, "input", None)
            if isinstance(tool_input, str):
                try:
                    tool_input = json.loads(tool_input)
                except Exception:
                    tool_input = {"raw": tool_input}
            tool_input = tool_input or {}

            if name and tool_registry and name in tool_registry:
                logger.info("[ToolLLM] executing local tool: %s", name)
                try:
                    result_obj = tool_registry[name](tool_input)  # type: ignore[arg-type]
                    logger.info("[ToolLLM] local tool '%s' completed", name)
                    output_text = json.dumps(result_obj, ensure_ascii=False)
                except Exception as e:  # pragma: no cover
                    logger.exception("[ToolLLM] local tool '%s' failed: %s", name, e)
                    output_text = json.dumps({"error": f"tool '{name}' failed: {type(e).__name__}: {e}"})

            if call_id:
                outputs.append({"tool_call_id": call_id, "output": output_text})

        if outputs:
            logger.info("[ToolLLM] submit_tool_outputs: count=%d", len(outputs))
            resp = _submit_tool_outputs_with_retry(response_id=resp.id, tool_outputs=outputs)
            # After tool outputs, request final structured parse to enforce schema
            # Supply the original conversation again to guide the model output
            resp = _parse_with_retry(input_messages=messages)
        else:
            break

    text = _collect_text_from_response(resp)
    logger.info("[ToolLLM] final text length=%d", len(text))
    parsed = getattr(resp, "output_parsed", None)
    if parsed is None:
        # As a last resort, attempt direct validation (should rarely happen)
        try:
            parsed = response_model.model_validate_json(text)
        except Exception as e:  # pragma: no cover
            # Corrective re-prompt: instruct the model to return ONLY valid JSON per schema
            max_format_retries_env = os.getenv("FORMAT_RETRY_ATTEMPTS", "2")
            try:
                max_format_retries = max(0, int(max_format_retries_env))
            except Exception:
                max_format_retries = 2

            # Build a strict instruction using the Pydantic model schema and field names
            try:
                schema_json = json.dumps(response_model.model_json_schema(), ensure_ascii=False)
            except Exception:
                schema_json = "{}"
            try:
                required_keys = ", ".join(list(getattr(response_model, "model_fields", {}).keys()))
            except Exception:
                required_keys = ""

            repair_instruction = (
                "Your previous response was invalid or empty. You must return ONLY a valid JSON object that conforms exactly to the required schema. "
                "Do not include any prose, code fences, markdown, or prefix/suffix text. Output a single JSON object.\n"
                f"Required keys: {required_keys}\n"
                f"JSON Schema:\n{schema_json}"
            )

            last_retry_text = text
            for _attempt in range(max_format_retries):
                repair_messages = list(messages) + [{"role": "user", "content": repair_instruction}]
                try:
                    resp_retry = client.responses.parse(
                        model=model,
                        input=repair_messages,
                        tools=[],  # avoid triggering new tool calls during repair
                        reasoning={"effort": reasoning_effort} if reasoning_effort else None,
                        text_format=response_model,
                    )
                except Exception:
                    # If the retry request itself fails, continue to next attempt
                    continue

                parsed_retry = getattr(resp_retry, "output_parsed", None)
                if parsed_retry is not None:
                    # Derive a reasonable output_text for logging/traceability
                    try:
                        retry_text = _collect_text_from_response(resp_retry) or json.dumps(parsed_retry.model_dump(), ensure_ascii=False)
                    except Exception:
                        retry_text = _collect_text_from_response(resp_retry)
                    return LLMResponse(output_parsed=parsed_retry, output_text=retry_text)

                # Fallback: try to parse whatever text we got
                last_retry_text = _collect_text_from_response(resp_retry)
                if last_retry_text:
                    try:
                        parsed_retry = response_model.model_validate_json(last_retry_text)
                        return LLMResponse(output_parsed=parsed_retry, output_text=last_retry_text)
                    except Exception:
                        pass  # continue retries

            # Exhausted retries; raise with the most recent raw text for debugging
            raise ValueError(
                "Failed to obtain structured output after repair retries: "
                f"{type(e).__name__}: {e}\nRaw text (last):\n{last_retry_text}"
            )

    return LLMResponse(output_parsed=parsed, output_text=text)


