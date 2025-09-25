from typing import Optional
import logging

try:
    # Newer OpenAI Python SDK exception names
    from openai import (
        APITimeoutError,
        APIConnectionError,
        RateLimitError,
        InternalServerError,
        APIStatusError,
    )
except Exception:  # pragma: no cover - fallback for older SDKs
    APITimeoutError = Exception  # type: ignore
    APIConnectionError = Exception  # type: ignore
    RateLimitError = Exception  # type: ignore
    InternalServerError = Exception  # type: ignore
    APIStatusError = Exception  # type: ignore

from .output_schemas import JudgeResponse, FinalJudgeResponse
from .prompts import (
    JUDGE_SYSTEM_PROMPT,
    build_judge_user_prompt,
    FINAL_JUDGE_SYSTEM_PROMPT,
    build_final_judge_user_prompt,
    build_judge_user_prompt_with_context,
)
from .llm_provider import generate_structured
from .tool_llm import generate_structured_with_tools
from .code_tool import build_run_python_tool_definition, run_python


class Judge:
    """LLM-backed judge that evaluates a proof for a given problem.

    It returns (correctness: bool, feedback: str). The feedback must only point out
    the first logical flaw and explain why it is a flaw, with no suggestions or extra flaws.
    """

    def __init__(self, model: str = "gpt-5-mini", reasoning_effort: str = "high", timeout: float = 1800.0, max_timeout_retries: int = 2) -> None:
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.timeout = timeout
        self.max_timeout_retries = max(0, int(max_timeout_retries))
        self.logger = logging.getLogger(self.__class__.__name__)

    def assess(
        self,
        problem: str,
        proof_markdown: str,
        *,
        model: Optional[str] = None,
        reasoning_effort: Optional[str] = None,
        literature_annotations: Optional[str] = None,
        literature_results: Optional[list[tuple[str, str]]] = None,
    ) -> JudgeResponse:
        selected_model = model or self.model
        selected_effort = reasoning_effort or self.reasoning_effort

        if literature_annotations is not None and literature_results is not None:
            user_prompt = build_judge_user_prompt_with_context(
                problem, proof_markdown, literature_annotations, literature_results
            )
        else:
            user_prompt = build_judge_user_prompt(problem, proof_markdown)

        transcript = [
            {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
            {
                "role": "user",
                "content": "Return ONLY a JSON object with fields: correctness (boolean) and feedback (string of the first flaw only). If you generate a list of flaws, put only the first one into the feedback string.",
            },
        ]

        attempt = 0
        while True:
            try:
                self.logger.debug("Judge assess: sending request (attempt %d)", attempt + 1)
                # Allow code tool for small verification if needed
                resp = generate_structured_with_tools(
                    messages=transcript,
                    response_model=JudgeResponse,
                    model=selected_model,
                    tools=[build_run_python_tool_definition()],
                    tool_registry={"run_python": lambda args: run_python(**args)},
                    reasoning_effort=selected_effort,
                    timeout=self.timeout,
                )
                self.logger.debug("Judge assess: received response")
                return resp.output_parsed
            except (APITimeoutError, APIConnectionError, RateLimitError, InternalServerError, APIStatusError) as e:
                self.logger.warning(
                    "Judge assess timed out/connection error on attempt %d/%d: %s",
                    attempt + 1,
                    self.max_timeout_retries + 1,
                    e,
                )
                if attempt < self.max_timeout_retries:
                    attempt += 1
                    continue
                raise


class FinalJudge:
    """LLM-backed final judge that selects the least incorrect proof among several attempts.

    It returns the 0-based index of the chosen proof.
    """

    def __init__(self, model: str = "gpt-5", reasoning_effort: str = "medium", timeout: float = 1800.0, max_timeout_retries: int = 1) -> None:
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.timeout = timeout
        self.max_timeout_retries = max(0, int(max_timeout_retries))
        self.logger = logging.getLogger(self.__class__.__name__)

    def select(
        self,
        problem: str,
        proofs_markdown: list[str],
        *,
        model: Optional[str] = None,
        reasoning_effort: Optional[str] = None,
    ) -> int:
        selected_model = model or self.model
        selected_effort = reasoning_effort or self.reasoning_effort

        transcript = [
            {"role": "system", "content": FINAL_JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": build_final_judge_user_prompt(problem, proofs_markdown)},
        ]

        attempt = 0
        while True:
            try:
                self.logger.debug(
                    "FinalJudge select: sending request with %d proofs (attempt %d)",
                    len(proofs_markdown),
                    attempt + 1,
                )
                resp = generate_structured(
                    messages=transcript,
                    response_model=FinalJudgeResponse,
                    model=selected_model,
                    reasoning_effort=selected_effort,
                    timeout=self.timeout,
                )
                self.logger.debug("FinalJudge select: received response")
                return int(resp.output_parsed.chosen_index)
            except (APITimeoutError, APIConnectionError, RateLimitError, InternalServerError, APIStatusError) as e:
                self.logger.warning(
                    "FinalJudge select timed out/connection error on attempt %d/%d: %s",
                    attempt + 1,
                    self.max_timeout_retries + 1,
                    e,
                )
                if attempt < self.max_timeout_retries:
                    attempt += 1
                    continue
                raise


