from typing import Optional, List, Dict, Any
import json

try:
    from openai import APITimeoutError, APIConnectionError
except Exception:  # pragma: no cover - fallback for older SDKs
    APITimeoutError = Exception  # type: ignore
    APIConnectionError = Exception  # type: ignore

from .prompts import (
    PROOF_SYSTEM_PROMPT,
    REPROVE_SYSTEM_PROMPT,
    build_proof_user_prompt,
    build_reprove_user_prompt,
    build_proof_user_prompt_with_context,
)
from .output_schemas import ProofResponse
from .llm_provider import generate_structured
from .tool_llm import generate_structured_with_tools
from .code_tool import build_run_python_tool_definition, run_python
import logging


class Prover:
    """LLM-backed prover that returns a structured proof for a given statement.

    Maintains conversation state to enable iterative reproving with feedback.
    """

    def __init__(self, model: str = "gpt-5-mini", reasoning_effort: str = "high", timeout: float = 2400.0, max_timeout_retries: int = 2) -> None:
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.timeout = timeout
        self.max_timeout_retries = max(0, int(max_timeout_retries))
        self._messages: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(self.__class__.__name__)

    def _reset_conversation(self) -> None:
        self._messages = [{"role": "system", "content": PROOF_SYSTEM_PROMPT}]
        self.logger.debug("Conversation reset with system prompt")

    def prove(
        self,
        question: str,
        *,
        model: Optional[str] = None,
        reasoning_effort: Optional[str] = None,
        literature_annotations: Optional[str] = None,
        literature_results: Optional[list[tuple[str, str]]] = None,
    ) -> ProofResponse:
        """Request a rigorous Markdown proof from the LLM.

        Returns a ProofResponse with field proof_markdown.
        """
        selected_model = model or self.model
        selected_effort = reasoning_effort or self.reasoning_effort

        self._reset_conversation()
        if literature_annotations is not None and literature_results is not None:
            prompt = build_proof_user_prompt_with_context(question, literature_annotations, literature_results)
        else:
            prompt = build_proof_user_prompt(question)
        self._messages.append({"role": "user", "content": prompt})
        self.logger.info("LLM request (prove): sending initial prompt (%d bytes)", len(json.dumps(self._messages)))
        attempt = 0
        while True:
            try:
                self.logger.debug("LLM request (prove): parse attempt %d", attempt + 1)
                # Use tool-aware path to enable local Python scratchpad
                resp = generate_structured_with_tools(
                    messages=self._messages,
                    response_model=ProofResponse,
                    model=selected_model,
                    tools=[build_run_python_tool_definition()],
                    tool_registry={"run_python": lambda args: run_python(**args)},
                    reasoning_effort=selected_effort,
                    timeout=self.timeout,
                )
                break
            except (APITimeoutError, APIConnectionError) as e:
                self.logger.warning(
                    "LLM request (prove) timed out/connection error on attempt %d/%d: %s",
                    attempt + 1,
                    self.max_timeout_retries + 1,
                    e,
                )
                if attempt < self.max_timeout_retries:
                    attempt += 1
                    continue
                raise
        proof = resp.output_parsed
        self._messages.append({"role": "assistant", "content": resp.output_text})
        self.logger.info("LLM response (prove): received proof")
        return proof

    def reprove(
        self,
        problem: str,
        previous_proof_markdown: str,
        feedback: str,
        *,
        model: Optional[str] = None,
        reasoning_effort: Optional[str] = None,
        literature_annotations: Optional[str] = None,
        literature_results: Optional[list[tuple[str, str]]] = None,
    ) -> ProofResponse:
        """Revise a previous proof using the problem, the prior proof, and reviewer feedback.

        Behavior: reset conversation state and use a re-proving system prompt that emphasizes
        understanding the existing proof and fixing it according to feedback.
        """
        selected_model = model or self.model
        selected_effort = reasoning_effort or self.reasoning_effort

        # Reset conversation with the re-prove system prompt
        self._messages = [{"role": "system", "content": REPROVE_SYSTEM_PROMPT}]
        # Supply problem, previous proof, feedback, and optional literature context
        base_prompt = build_reprove_user_prompt(problem, previous_proof_markdown, feedback)
        if literature_annotations is not None and literature_results is not None:
            # Append context so the model may use lemmas and consistent notation
            lemmas_md = "\n".join([f"- ${{{stmt}}}$ (source: {url})" for stmt, url in literature_results])
            context = (
                f"\n\nContext you may use without proof:\n"
                f"- Unified annotations:\n{literature_annotations}\n"
                f"- Allowed lemmas/results (cite as needed):\n{lemmas_md}\n"
            )
            content = base_prompt + context
        else:
            content = base_prompt
        self._messages.append({"role": "user", "content": content})
        self.logger.info("LLM request (reprove): sending reprove prompt (%d bytes)", len(json.dumps(self._messages)))
        attempt = 0
        while True:
            try:
                self.logger.debug("LLM request (reprove): parse attempt %d", attempt + 1)
                resp = generate_structured_with_tools(
                    messages=self._messages,
                    response_model=ProofResponse,
                    model=selected_model,
                    tools=[build_run_python_tool_definition()],
                    tool_registry={"run_python": lambda args: run_python(**args)},
                    reasoning_effort=selected_effort,
                    timeout=self.timeout,
                )
                break
            except (APITimeoutError, APIConnectionError) as e:
                self.logger.warning(
                    "LLM request (reprove) timed out/connection error on attempt %d/%d: %s",
                    attempt + 1,
                    self.max_timeout_retries + 1,
                    e,
                )
                if attempt < self.max_timeout_retries:
                    attempt += 1
                    continue
                raise
        proof = resp.output_parsed
        # Track last assistant message for continuity
        self._messages.append({"role": "assistant", "content": resp.output_text})
        self.logger.info("LLM response (reprove): received revised proof")
        return proof
