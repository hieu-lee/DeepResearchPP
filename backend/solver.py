from typing import Tuple, Optional
import logging

from .judge import Judge
from .prover import Prover
from .output_schemas import LiteratureReviewResult


class Solver:
    """Coordinates a single Prover with two sequential Judges and a feedback loop."""

    def __init__(self, model: str = "gpt-5") -> None:
        self.model = model
        self.prover: Prover = Prover(model=model)
        self.logger = logging.getLogger(self.__class__.__name__)

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
        judge1 = Judge(model=self.model)
        judge2 = Judge(model=self.model)

        for _ in range(max_tries_per_prover):
            self.logger.info("Prover: attempting proof%s", " (with feedback)" if feedback else "")

            # Produce or revise proof
            if not feedback:
                if literature is not None:
                    proof_resp = self.prover.prove(
                        problem,
                        literature_annotations=literature.annotations,
                        literature_results=[(x.statement, x.url) for x in literature.results],
                    )
                else:
                    proof_resp = self.prover.prove(problem)
            else:
                if literature is not None:
                    proof_resp = self.prover.reprove(
                        problem,
                        last_proof,
                        feedback,
                        literature_annotations=literature.annotations,
                        literature_results=[(x.statement, x.url) for x in literature.results],
                    )
                else:
                    proof_resp = self.prover.reprove(problem, last_proof, feedback)

            proof_markdown = proof_resp.proof_markdown
            last_proof = proof_markdown

            # Judge #1 assessment
            self.logger.info("Submitting to Judge #1")
            if literature is not None:
                j1 = judge1.assess(
                    problem,
                    proof_markdown,
                    literature_annotations=literature.annotations,
                    literature_results=[(x.statement, x.url) for x in literature.results],
                )
            else:
                j1 = judge1.assess(problem, proof_markdown)

            if not j1.correctness:
                feedback = j1.feedback
                self.logger.info("Judge #1 found a flaw; looping with feedback")
                continue

            # Judge #2 assessment only if Judge #1 accepted
            self.logger.info("Judge #1 accepted; submitting to Judge #2")
            if literature is not None:
                j2 = judge2.assess(
                    problem,
                    proof_markdown,
                    literature_annotations=literature.annotations,
                    literature_results=[(x.statement, x.url) for x in literature.results],
                )
            else:
                j2 = judge2.assess(problem, proof_markdown)

            if j2.correctness:
                self.logger.info("Judge #2 also accepted; returning correct proof")
                return True, proof_markdown

            # Judge #2 rejected; return incorrect now and use its feedback for the next iteration
            feedback = j2.feedback
            self.logger.info("Judge #2 found a flaw; returning incorrect for this round and improving")

        # Exhausted tries; return the last available feedback
        self.logger.info("Exhausted max tries; returning last feedback")
        return False, feedback or "No correct proof found within allotted attempts."


