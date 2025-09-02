from __future__ import annotations

import argparse
import json
import logging
from typing import Any, Dict, List

from pydantic import BaseModel

from .tool_llm import generate_structured_with_tools


class WebSearchPing(BaseModel):
    ok: bool
    query_used: str | None = None


def test_web_search_tool(model: str) -> int:
    """Smoke-test that the selected model can call the correct web_search tool.

    Returns process exit code (0=pass, 1=fail).
    """
    logger = logging.getLogger("smoke")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
    # Tool selection heuristic mirrors research.py
    tools: List[Dict[str, Any]] = [{"type": "web_search", "search_context_size": "medium"}]

    messages = [
        {
            "role": "system",
            "content": (
                "You are a test runner. You MUST call the web search tool exactly once with a short query, then return ONLY a JSON object "
                "with fields ok=true and query_used set to the query string you issued. No extra text."
            ),
        },
        {
            "role": "user",
            "content": "Perform a web search for 'test ping' and then return {\"ok\": true, \"query_used\": <your_query>} strictly as JSON.",
        },
    ]

    try:
        resp = generate_structured_with_tools(
            messages=messages,
            response_model=WebSearchPing,
            model=model,
            tools=tools,
            tool_registry={},
            reasoning_effort="low",
            timeout=120.0,
        )
        out: WebSearchPing = resp.output_parsed  # type: ignore[assignment]
        tool_type_label = tools[0].get("type")
        logger.info("Tool type=%s model=%s -> ok=%s query=%s", tool_type_label, model, out.ok, out.query_used)
        print(json.dumps({"pass": bool(out.ok), "tool_type": tool_type_label, "query_used": out.query_used}, ensure_ascii=False))
        return 0 if out.ok else 1
    except Exception as e:
        logger.exception("Smoke test failed: %s", e)
        print(json.dumps({"pass": False, "error": f"{type(e).__name__}: {e}"}, ensure_ascii=False))
        return 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Backend smoke tests")
    ap.add_argument("test", choices=["websearch"], help="Test to run")
    ap.add_argument("--model", default="o4-mini")
    args = ap.parse_args()

    if args.test == "websearch":
        return test_web_search_tool(args.model)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())


