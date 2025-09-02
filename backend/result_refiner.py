from typing import Optional, Tuple
import json

try:
    from openai import APITimeoutError, APIConnectionError
except Exception:  # pragma: no cover - fallback for older SDKs
    APITimeoutError = Exception  # type: ignore
    APIConnectionError = Exception  # type: ignore

from .prompts import (
    RESULT_REFINER_SYSTEM_PROMPT,
    build_result_refiner_user_prompt,
    TIGHTEN_SYSTEM_PROMPT,
    build_tighten_user_prompt,
)
from .output_schemas import ResultRefinementResponse, RefineTightenResult
from .llm_provider import generate_structured
import logging


class ResultRefiner:
    """Refine a statement and its proof using an LLM-driven policy.

    Policy:
    - Remove assumptions in the statement that are unused in the proof.
    - If the proof actually disproves the statement, correct the statement and rewrite the proof to assume the contrary.
    - Strip any textual markers denoting conjectural status from the statement (e.g., "(Conjecture ...)").

    Returns either (new_statement, new_proof_markdown) when changed, or None when no change is required.
    """

    def __init__(self, model: str = "gpt-5", reasoning_effort: str = "medium", timeout: float = 900.0, max_timeout_retries: int = 2) -> None:
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.timeout = timeout
        self.max_timeout_retries = max(0, int(max_timeout_retries))
        self.logger = logging.getLogger(self.__class__.__name__)
        self._messages = []

    def refine(self, statement: str, proof_markdown: str, *, model: Optional[str] = None, reasoning_effort: Optional[str] = None) -> Optional[Tuple[str, str]]:
        selected_model = model or self.model
        selected_effort = reasoning_effort or self.reasoning_effort

        # Reset conversation with system prompt
        self._messages = [{"role": "system", "content": RESULT_REFINER_SYSTEM_PROMPT}]
        user_prompt = build_result_refiner_user_prompt(statement, proof_markdown)
        self._messages.append({"role": "user", "content": user_prompt})

        self.logger.info("LLM request (refine): sending refinement prompt (%d bytes)", len(json.dumps(self._messages)))
        attempt = 0
        while True:
            try:
                self.logger.debug("LLM request (refine): parse attempt %d", attempt + 1)
                resp = generate_structured(
                    messages=self._messages,
                    response_model=ResultRefinementResponse,
                    model=selected_model,
                    reasoning_effort=selected_effort,
                    timeout=self.timeout,
                )
                break
            except (APITimeoutError, APIConnectionError) as e:
                self.logger.warning(
                    "LLM request (refine) timed out/connection error on attempt %d/%d: %s",
                    attempt + 1,
                    self.max_timeout_retries + 1,
                    e,
                )
                if attempt < self.max_timeout_retries:
                    attempt += 1
                    continue
                raise

        result: ResultRefinementResponse = resp.output_parsed
        # Track assistant message for continuity
        self._messages.append({"role": "assistant", "content": resp.output_text})
        self.logger.info("LLM response (refine): received refinement result")

        if not result.changed:
            return None
        return result.new_statement, result.new_proof_markdown

    def tighten(self, statement: str, proof_markdown: str, *, model: Optional[str] = None, reasoning_effort: Optional[str] = None) -> Optional[Tuple[str, str]]:
        selected_model = model or self.model
        selected_effort = reasoning_effort or self.reasoning_effort

        # Reset conversation with tightening system prompt
        self._messages = [{"role": "system", "content": TIGHTEN_SYSTEM_PROMPT}]
        user_prompt = build_tighten_user_prompt(statement, proof_markdown)
        self._messages.append({"role": "user", "content": user_prompt})

        self.logger.info("LLM request (tighten): sending tightening prompt (%d bytes)", len(json.dumps(self._messages)))
        attempt = 0
        while True:
            try:
                self.logger.debug("LLM request (tighten): parse attempt %d", attempt + 1)
                resp = generate_structured(
                    messages=self._messages,
                    response_model=RefineTightenResult,
                    model=selected_model,
                    reasoning_effort=selected_effort,
                    timeout=self.timeout,
                )
                break
            except (APITimeoutError, APIConnectionError) as e:
                self.logger.warning(
                    "LLM request (tighten) timed out/connection error on attempt %d/%d: %s",
                    attempt + 1,
                    self.max_timeout_retries + 1,
                    e,
                )
                if attempt < self.max_timeout_retries:
                    attempt += 1
                    continue
                raise

        result: RefineTightenResult = resp.output_parsed
        # Track assistant message for continuity
        self._messages.append({"role": "assistant", "content": resp.output_text})
        self.logger.info("LLM response (tighten): received result")

        if not result.can_tighten:
            return None
        updated_stmt = result.updated_statement.strip() if isinstance(result.updated_statement, str) else ""
        updated_proof = result.updated_proof.strip() if isinstance(result.updated_proof, str) else ""
        if not updated_stmt or not updated_proof:
            # Defensive: treat as not tightenable if outputs are empty
            return None
        return updated_stmt, updated_proof


