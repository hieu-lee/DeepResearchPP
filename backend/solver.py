from typing import Tuple, Optional, Any
import logging

from .judge import Judge
from .prover import Prover
from .output_schemas import LiteratureReviewResult
from .logging_hooks import logging_manager


class Solver:
    """Coordinates a single Prover with two sequential Judges and a feedback loop."""

    def __init__(self, model: str = "gpt-5") -> None:
        self.model = model
        # If user selected gpt-oss-120b, use 120b for Prover with no tools; otherwise default behavior
        if model == "gpt-oss-120b":
            self.prover = Prover(model="openai/gpt-oss-120b", use_tools=False)
        else:
            self.prover = Prover(model=model)
        self.logger = logging.getLogger(self.__class__.__name__)
        # Assign a logging pair index if logging is enabled by CLI
        self._pair_index: Optional[int] = logging_manager.assign_index()

    def solve(
        self,
        problem: str,
        max_tries_per_prover: int = 10,
        literature: Optional[LiteratureReviewResult] = None,
    ) -> Tuple[bool, str]:
        """Run a single Prover with two sequential Judges and iterative feedback.

        Control flow:
        - Generate or revise a proof using the Prover.
        - Submit to Judge #1. If incorrect, feed Judge #1 feedback to Prover and continue.
        - If Judge #1 says correct, submit to Judge #2.
          - If Judge #2 says incorrect, return incorrect and feed its feedback to Prover in the next iteration.
          - If Judge #2 also says correct, return correct with the proof.

        Returns (correctness, proof_markdown_or_feedback).
        """

        feedback: str = ""
        last_proof: str = ""
        # Judges: if user selected gpt-oss-120b, prefer o4-mini for judges (tool-capable)
        judge_model = "o4-mini" if self.model in {"gpt-oss-120b", "openai/gpt-oss-120b"} else self.model
        judge1 = Judge(model=judge_model)
        judge2 = Judge(model=judge_model)

        judge_context: dict[str, Any] = {}
        if literature is not None:
            judge_context = {
                "literature_annotations": literature.annotations,
                "literature_results": [(x.statement, x.url) for x in literature.results],
            }

        for iter_idx in range(1, max_tries_per_prover + 1):
            self.logger.info("Prover: attempting proof%s", " (with feedback)" if feedback else "")

            # Produce or revise proof
            if not feedback:
                if judge_context:
                    proof_resp = self.prover.prove(
                        problem,
                        literature_annotations=judge_context["literature_annotations"],
                        literature_results=judge_context["literature_results"],
                    )
                else:
                    proof_resp = self.prover.prove(problem)
            else:
                if judge_context:
                    proof_resp = self.prover.reprove(
                        problem,
                        last_proof,
                        feedback,
                        literature_annotations=judge_context["literature_annotations"],
                        literature_results=judge_context["literature_results"],
                    )
                else:
                    proof_resp = self.prover.reprove(problem, last_proof, feedback)

            proof_markdown = proof_resp.proof_markdown
            last_proof = proof_markdown
            try:
                logging_manager.write_iteration_header(self._pair_index, iter_idx, len(proof_markdown or ""))
                logging_manager.write_iteration_start(self._pair_index, iter_idx, proof_markdown or "")
            except Exception:
                pass

            # Judge #1 assessment
            self.logger.info("Submitting to Judge #1")
            if judge_context:
                j1 = judge1.assess(
                    problem,
                    proof_markdown,
                    literature_annotations=judge_context["literature_annotations"],
                    literature_results=judge_context["literature_results"],
                )
            else:
                j1 = judge1.assess(problem, proof_markdown)

            if not j1.correctness:
                feedback = j1.feedback
                self.logger.info("Judge #1 found a flaw; looping with feedback")
                try:
                    logging_manager.write_judge1(self._pair_index, accepted=False, feedback_len=len(feedback or ""))
                    logging_manager.append_judge1_detail(self._pair_index, iter_idx, accepted=False, feedback=feedback)
                except Exception:
                    pass
                continue

            # Judge #2 assessment only if Judge #1 accepted
            self.logger.info("Judge #1 accepted; submitting to Judge #2")
            try:
                logging_manager.write_judge1(self._pair_index, accepted=True)
                logging_manager.append_judge1_detail(self._pair_index, iter_idx, accepted=True, feedback=j1.feedback)
            except Exception:
                pass
            if judge_context:
                j2 = judge2.assess(
                    problem,
                    proof_markdown,
                    literature_annotations=judge_context["literature_annotations"],
                    literature_results=judge_context["literature_results"],
                )
            else:
                j2 = judge2.assess(problem, proof_markdown)

            if j2.correctness:
                self.logger.info("Judge #2 also accepted; returning correct proof")
                try:
                    logging_manager.write_judge2(self._pair_index, accepted=True)
                    logging_manager.append_judge2_detail(self._pair_index, iter_idx, accepted=True, feedback=j2.feedback)
                except Exception:
                    pass
                return True, proof_markdown

            # Judge #2 rejected; return incorrect now and use its feedback for the next iteration
            feedback = j2.feedback
            self.logger.info("Judge #2 found a flaw; returning incorrect for this round and improving")
            try:
                logging_manager.write_judge2(self._pair_index, accepted=False, feedback_len=len(feedback or ""))
                logging_manager.append_judge2_detail(self._pair_index, iter_idx, accepted=False, feedback=feedback)
            except Exception:
                pass

        # Exhausted tries; return the last available feedback
        self.logger.info("Exhausted max tries; returning last feedback")
        return False, feedback or "No correct proof found within allotted attempts."



