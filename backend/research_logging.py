from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Optional


@dataclass
class _FileLogger:
    path: Path
    _lock: Lock

    def reset(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            self.path.write_text("", encoding="utf-8")

    def append(self, text: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            with self.path.open("a", encoding="utf-8") as f:
                f.write(text)


class ResearchContinuousPredictionLogger:
    """Logging adapter for a single prediction within research --continuous.

    Folder layout under base_root:
      iteration_{iter}/
        prediction_{pred}/
          statement.txt
          prediction_{pred}_log/
            prediction_{pred}.log
            iteration_{k}.log  (one per prover iteration)

    This class exposes the same public API methods used by Solver's logging hooks
    so it can be passed in place of backend.logging_hooks.logging_manager.
    """

    def __init__(
        self,
        base_root: Path,
        *,
        iteration_index: int,
        prediction_index: int,
        statement_text: str,
    ) -> None:
        self._enabled = True
        self._base_root = Path(base_root)
        self._iter_idx = iteration_index
        self._pred_idx = prediction_index

        # Build folders
        self._iter_dir = self._base_root / f"iteration_{self._iter_idx}"
        self._pred_dir = self._iter_dir / f"prediction_{self._pred_idx}"
        self._log_dir = self._pred_dir / f"prediction_{self._pred_idx}_log"
        self._main_log_path = self._log_dir / f"prediction_{self._pred_idx}.log"

        # Ensure directories
        self._iter_dir.mkdir(parents=True, exist_ok=True)
        self._pred_dir.mkdir(parents=True, exist_ok=True)
        self._log_dir.mkdir(parents=True, exist_ok=True)

        # Write statement file
        try:
            (self._pred_dir / "statement.txt").write_text(statement_text or "", encoding="utf-8")
        except Exception:
            pass

        # Initialize/reset main log
        self._main_logger = _FileLogger(self._main_log_path, Lock())
        try:
            header = (
                f"=== Prediction #{self._pred_idx} Log ===\n"
                f"Location: {self._log_dir}\n"
                f"Main file: {self._main_log_path.name}\n"
                f"(Per-iteration details are in iteration_k.log files)\n\n"
            )
            self._main_logger.reset()
            self._main_logger.append(header)
        except Exception:
            pass

        self._lock = Lock()

    # --- Compatibility surface with ProverSolverLogManager ---
    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def assign_index(self) -> Optional[int]:
        # Single prediction context; always index 1
        return 1

    def _iter_file(self, iteration: int) -> Path:
        return self._log_dir / f"iteration_{iteration}.log"

    def write_iteration_header(self, index: int, iteration: int, proof_len: int) -> None:
        if not self.is_enabled:
            return
        try:
            text = (
                f"=== Iteration {iteration} ===\n"
                f"- proof length: {proof_len} chars\n"
            )
            self._main_logger.append(text)
        except Exception:
            pass

    def write_iteration_start(self, index: int, iteration: int, proof_markdown: str) -> None:
        if not self.is_enabled:
            return
        path = self._iter_file(iteration)
        header = (
            f"========================================\n"
            f"Iteration {iteration} - Prover Output\n"
            f"========================================\n\n"
            f"[PROOF - Markdown]\n\n"
        )
        try:
            with self._lock:
                path.write_text(header + (proof_markdown or "(empty proof)\n"), encoding="utf-8")
                with path.open("a", encoding="utf-8") as f:
                    f.write("\n\n----------------------------------------\n")
        except Exception:
            pass

    def write_judge1(self, index: int, accepted: bool, feedback_len: Optional[int] = None) -> None:
        if not self.is_enabled:
            return
        try:
            if accepted:
                text = "- Judge #1: ACCEPT -> forwarding to Judge #2\n"
            else:
                text = f"- Judge #1: REJECT (feedback length: {feedback_len or 0})\n\n"
            self._main_logger.append(text)
        except Exception:
            pass

    def write_judge2(self, index: int, accepted: bool, feedback_len: Optional[int] = None) -> None:
        if not self.is_enabled:
            return
        try:
            if accepted:
                text = "- Judge #2: ACCEPT (final)\n\n"
            else:
                text = f"- Judge #2: REJECT (feedback length: {feedback_len or 0})\n\n"
            self._main_logger.append(text)
        except Exception:
            pass

    def append_judge1_detail(self, index: int, iteration: int, accepted: bool, feedback: Optional[str]) -> None:
        if not self.is_enabled:
            return
        path = self._iter_file(iteration)
        decision = "ACCEPT" if accepted else "REJECT"
        section = (
            f"\nJudge #1 Assessment\n"
            f"Decision: {decision}\n"
        )
        if not accepted:
            fb = (feedback or "").strip()
            if fb:
                section += f"\nFeedback (first flaw):\n\n{fb}\n"
        try:
            with self._lock:
                with path.open("a", encoding="utf-8") as f:
                    f.write(section)
                    f.write("\n----------------------------------------\n")
        except Exception:
            pass

    def append_judge2_detail(self, index: int, iteration: int, accepted: bool, feedback: Optional[str]) -> None:
        if not self.is_enabled:
            return
        path = self._iter_file(iteration)
        decision = "ACCEPT" if accepted else "REJECT"
        section = (
            f"\nJudge #2 Assessment\n"
            f"Decision: {decision}\n"
        )
        if not accepted:
            fb = (feedback or "").strip()
            if fb:
                section += f"\nFeedback (first flaw):\n\n{fb}\n"
        try:
            with self._lock:
                with path.open("a", encoding="utf-8") as f:
                    f.write(section)
                    f.write("\n========================================\n\n")
        except Exception:
            pass
    def write_final_outputs(self, final_statement: str, final_proof_markdown: str) -> None:
        """Write final statement and proof after refinement/tighten."""
        if not self.is_enabled:
            return
        try:
            (self._log_dir / 'final_statement.txt').write_text(final_statement or '', encoding='utf-8')
        except Exception:
            pass
        try:
            (self._log_dir / 'final_proof.md').write_text(final_proof_markdown or '', encoding='utf-8')
        except Exception:
            pass
