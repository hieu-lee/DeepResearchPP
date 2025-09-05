from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
import logging

from .output_schemas import LiteratureReviewResult, PredictedResults, FinalReport, NoveltyCheck
from .prompts import (
    LIT_REVIEW_SYSTEM_PROMPT,
    build_lit_review_user_prompt,
    PREDICT_SYSTEM_PROMPT,
    build_predict_user_prompt,
    NOVELTY_SYSTEM_PROMPT,
    build_novelty_user_prompt,
    FINAL_REPORT_SYSTEM_PROMPT,
    build_final_report_user_prompt,
)
from .tool_llm import generate_structured_with_tools
from .code_tool import run_python, build_run_python_tool_definition
from .markdown_tool import validate_markdown, build_validate_markdown_tool_definition
from .llm_provider import GroqRetriesExhaustedError


def _python_tool_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    # Ensure required keys
    code = args.get("code", "")
    timeout = float(args.get("timeout_seconds", 10))
    mem = int(args.get("memory_limit_mb", 256))
    return run_python(code=code, timeout_seconds=timeout, memory_limit_mb=mem)


def _web_search_tool_for_model(model_name: str) -> dict:
    # Use legacy web_search tool for models that support tools.
    # If model has been mapped to o4-mini, tools are allowed; if it is an OSS text-only model, caller should avoid tools.
    return {"type": "web_search", "search_context_size": "medium"}


@dataclass
class ResearchConfig:
    lit_model: str = "gpt-5"
    lit_reasoning: str = "medium"
    predict_model: str = "gpt-5"
    predict_reasoning: str = "high"
    prove_model: str = "gpt-5"
    reporter_model: str = "gpt-5-mini"
    reporter_reasoning: str = "medium"
    novelty_model: str = "gpt-5"
    novelty_reasoning: str = "medium"
    # Optional directive to steer predictions toward a target research direction
    research_guideline: str | None = None


class ResearchPipeline:
    def __init__(self, config: ResearchConfig | None = None) -> None:
        self.config = config or ResearchConfig()
        self.logger = logging.getLogger(self.__class__.__name__)

    def literature_review(self, seed_result_latex: str | list[str]) -> LiteratureReviewResult:
        self.logger.info("[Research] Literature review: start (seed length %d)", len(seed_result_latex))
        messages = [
            {"role": "system", "content": LIT_REVIEW_SYSTEM_PROMPT},
            {"role": "user", "content": build_lit_review_user_prompt(seed_result_latex)},
        ]

        # The model is responsible for placing the seed result as the first tuple
        try:
            resp = generate_structured_with_tools(
                messages=messages,
                response_model=LiteratureReviewResult,
                model=self.config.lit_model,
                tools=[_web_search_tool_for_model(self.config.lit_model)],
                tool_registry={},  # no local tools for this step
                reasoning_effort=self.config.lit_reasoning,
                timeout=2400.0,
            )
        except GroqRetriesExhaustedError:
            # Skip straight to report generation later; return minimal literature context
            self.logger.warning("[Research] Groq retries exhausted in literature review; continuing with minimal context")
            minimal = LiteratureReviewResult(annotations="", results=[])
            return minimal
        lit = resp.output_parsed  # type: ignore[assignment]
        try:
            count = len(getattr(lit, "results", []) or [])
        except Exception:
            count = 0
        self.logger.info("[Research] Literature review: done (%d results)", count)
        return lit  # type: ignore[return-value]

    def predict(self, lit: LiteratureReviewResult) -> PredictedResults:
        # Register local python tool alongside web search
        # Allow both web search (built-in) and local python experiments
        tools = [_web_search_tool_for_model(self.config.predict_model), build_run_python_tool_definition()]
        registry = {"run_python": _python_tool_impl}

        self.logger.info("[Research] Prediction: start (literature results=%d)", len(lit.results))
        messages = [
            {"role": "system", "content": PREDICT_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": build_predict_user_prompt(
                    lit.annotations,
                    [[x.statement, x.url] for x in lit.results],
                    self.config.research_guideline,
                ),
            },
        ]
        # Retry logic for parse/validation errors (e.g., empty JSON leading to EOF)
        max_retries = 2
        attempt = 0
        last_err: Exception | None = None
        while attempt <= max_retries:
            try:
                resp = generate_structured_with_tools(
                    messages=messages,
                    response_model=PredictedResults,
                    model=self.config.predict_model,
                    tools=tools,
                    tool_registry=registry,
                    reasoning_effort=self.config.predict_reasoning,
                    timeout=3600.0,
                )
                preds = resp.output_parsed  # type: ignore[assignment]
                try:
                    count = len(getattr(preds, "predicted_results", []) or [])
                except Exception:
                    count = 0
                self.logger.info("[Research] Prediction: done (%d predicted results)", count)
                return preds  # type: ignore[return-value]
            except GroqRetriesExhaustedError:
                # Treat as no predictions; proceed to report
                self.logger.warning("[Research] Groq retries exhausted in prediction; no new results.")
                empty = PredictedResults(annotations=lit.annotations, predicted_results=[])
                return empty
            except Exception as e:
                err_str = str(e)
                last_err = e
                # Detect empty/EOF JSON validation cases specifically
                is_empty_json = (
                    "EOF while parsing a value" in err_str
                    or "json_invalid" in err_str
                    or "input_value=''" in err_str
                )
                if is_empty_json and attempt < max_retries:
                    self.logger.warning(
                        "[Research] Prediction parse failed (attempt %d/%d): %s",
                        attempt + 1,
                        max_retries + 1,
                        e,
                    )
                    attempt += 1
                    continue
                if is_empty_json:
                    # Treat as: model cannot propose any new result — finish gracefully
                    self.logger.info(
                        "[Research] Prediction produced empty output after %d attempts; no new results.",
                        attempt + 1,
                    )
                    empty = PredictedResults(annotations=lit.annotations, predicted_results=[])
                    return empty
                # Non-empty/other errors bubble up
                raise

    def novelty_filter(self, lit: LiteratureReviewResult, preds: PredictedResults) -> list[str]:
        """Run the novelty checker per predicted result with web_search tool in parallel; keep only novel results."""
        from concurrent.futures import ThreadPoolExecutor, as_completed

        tools = [_web_search_tool_for_model(self.config.novelty_model)]
        registry: dict[str, Any] = {}

        def _check(stmt: str) -> tuple[str, bool, str | None, str | None]:
            messages = [
                {"role": "system", "content": NOVELTY_SYSTEM_PROMPT},
                {"role": "user", "content": build_novelty_user_prompt(lit.annotations, stmt)},
            ]
            try:
                resp = generate_structured_with_tools(
                    messages=messages,
                    response_model=NoveltyCheck,
                    model=self.config.novelty_model,
                    tools=tools,
                    tool_registry=registry,
                    reasoning_effort=self.config.novelty_reasoning,
                    timeout=900.0,
                )
            except GroqRetriesExhaustedError:
                # If novelty check fails globally by retries, mark as not novel to skip proving
                return stmt, False, None, None
            parsed = resp.output_parsed  # type: ignore[assignment]
            is_novel = bool(getattr(parsed, "is_novel", False))
            matched_stmt = getattr(parsed, "matched_statement", None)
            matched_url = getattr(parsed, "matched_url", None)
            return stmt, is_novel, matched_stmt, matched_url

        kept: list[str] = []
        appended_non_novel = 0
        with ThreadPoolExecutor(max_workers=8) as ex:
            futures = {ex.submit(_check, s): s for s in preds.predicted_results}
            for fut in as_completed(futures):
                try:
                    stmt, is_novel, matched_stmt, matched_url = fut.result()
                except Exception:
                    # If a single novelty check fails, treat it as not novel
                    continue
                if is_novel:
                    kept.append(stmt)
                else:
                    # If not novel and we have a matched known result with source, append it like Literature Review
                    if matched_stmt and matched_url is not None:
                        try:
                            lit.results.append(type(lit.results[0])(statement=str(matched_stmt), url=str(matched_url)))
                            appended_non_novel += 1
                        except Exception:
                            # Be resilient if schema shape changes; skip append on error
                            pass
        self.logger.info(
            "[Research] Novelty check: kept %d/%d results (appended known=%d)",
            len(kept),
            len(preds.predicted_results),
            appended_non_novel,
        )
        return kept

    def compile_final_report(
        self,
        lit: LiteratureReviewResult,
        compiled_results: list[tuple[str, str]],
    ) -> FinalReport:
        """Use an LLM to compile a beautiful KaTeX Markdown report from literature context and new results.

        compiled_results: list of (new_result_latex, proof_markdown)
        """
        self.logger.info(
            "[Research] Final report: start (lit results=%d, new results=%d)",
            len(lit.results),
            len(compiled_results),
        )
        messages = [
            {"role": "system", "content": FINAL_REPORT_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": build_final_report_user_prompt(
                    lit.annotations,
                    [[x.statement, x.url] for x in lit.results],
                    compiled_results,
                ),
            },
        ]

        # Allow the model to optionally call a validator tool, and also validate locally after each attempt.
        tools = [build_validate_markdown_tool_definition()]
        registry = {"validate_markdown": lambda args: validate_markdown(str(args.get("markdown", "")))}

        max_rounds = 5
        round_idx = 0
        last_report: FinalReport | None = None
        while round_idx < max_rounds:
            try:
                resp = generate_structured_with_tools(
                    messages=messages,
                    response_model=FinalReport,
                    model=self.config.reporter_model,
                    tools=tools,
                    tool_registry=registry,
                    reasoning_effort=self.config.reporter_reasoning,
                    timeout=1800.0,
                )
            except GroqRetriesExhaustedError:
                # If the final report cannot be generated via Groq after retries, synthesize a minimal report
                self.logger.warning("[Research] Groq retries exhausted in final report; returning minimal report")
                minimal = FinalReport(report_markdown="# Research Report\n\n_No content due to upstream model failures._")
                return minimal
            report = resp.output_parsed  # type: ignore[assignment]
            last_report = report
            report_md = getattr(report, "report_markdown", "") or ""
            result = validate_markdown(report_md)
            if bool(result.get("ok")):
                self.logger.info("[Research] Final report: valid markdown (length %d)", len(report_md))
                return report  # type: ignore[return-value]

            errors = list(result.get("errors", []) or [])
            try:
                err_count = len(errors)
            except Exception:
                err_count = 0
            self.logger.info(
                "[Research] Final report validation failed (round %d/%d, errors=%d)",
                round_idx + 1,
                max_rounds,
                err_count,
            )

            # Feed the exact validator errors back to the model to repair.
            error_list = "\n".join([f"- {e}" for e in errors])
            messages.append(
                {
                    "role": "user",
                    "content": (
                        "Your previous report failed Markdown/KaTeX validation.\n"
                        "Fix ALL issues below and regenerate a clean report.\n"
                        "Do not add backticks or unsupported environments/macros.\n"
                        "Validation errors:\n" + error_list
                    ),
                }
            )
            round_idx += 1

        # If still invalid after max rounds, return the last attempt (best effort)
        self.logger.info(
            "[Research] Final report: returning best-effort after %d rounds (still invalid)",
            max_rounds,
        )
        return last_report or resp.output_parsed  # type: ignore[return-value]

    def predict_and_filter(self, lit: LiteratureReviewResult) -> list[str]:
        preds = self.predict(lit)
        return self.novelty_filter(lit, preds)


