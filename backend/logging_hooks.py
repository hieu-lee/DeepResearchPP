from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Optional


@dataclass
class _PairLogger:
    path: Path
    _lock: Lock

    def reset(self) -> None:
        with self._lock:
            self.path.write_text("", encoding="utf-8")

    def write(self, text: str) -> None:
        with self._lock:
            with self.path.open("a", encoding="utf-8") as f:
                f.write(text)


class ProverSolverLogManager:
    def __init__(self) -> None:
        self._enabled = False
        self._base_dir: Optional[Path] = None
        self._base_stem: Optional[str] = None
        self._counter = 0
        self._lock = Lock()
        self._pair_loggers: dict[int, _PairLogger] = {}

    @property
    def is_enabled(self) -> bool:
        return self._enabled and self._base_dir is not None and self._base_stem is not None

    def configure_from_input_file(self, path: Path) -> None:
        base = Path(path)
        self._base_dir = base.parent
        self._base_stem = base.stem
        self._enabled = True
        self._counter = 0
        self._pair_loggers.clear()

    def _folder_for_index(self, index: int) -> Path:
        assert self._base_dir is not None and self._base_stem is not None
        return self._base_dir / f"{self._base_stem}_{index}_log"

    def _main_filepath_for_index(self, index: int) -> Path:
        folder = self._folder_for_index(index)
        folder.mkdir(parents=True, exist_ok=True)
        assert self._base_stem is not None
        return folder / f"{self._base_stem}_{index}.log"

    def _iter_filepath(self, index: int, iteration: int) -> Path:
        folder = self._folder_for_index(index)
        folder.mkdir(parents=True, exist_ok=True)
        return folder / f"Iteration{iteration}.log"

    def assign_index(self) -> Optional[int]:
        if not self.is_enabled:
            return None
        with self._lock:
            self._counter += 1
            idx = self._counter
        # Initialize file
        pl = self.get_pair_logger(idx)
        pl.reset()
        header = (
            f"=== Prover/Solver Pair #{idx} Log ===\n"
            f"Location: {self._folder_for_index(idx)}\n"
            f"Main file: {self._main_filepath_for_index(idx).name}\n"
            f"(Per-iteration details will be in IterationN.log files)\n\n"
        )
        pl.write(header)
        return idx

    def get_pair_logger(self, index: int) -> _PairLogger:
        with self._lock:
            if index not in self._pair_loggers:
                path = self._main_filepath_for_index(index)
                self._pair_loggers[index] = _PairLogger(path=path, _lock=Lock())
            return self._pair_loggers[index]

    def write_iteration_header(self, index: int, iteration: int, proof_len: int) -> None:
        if not self.is_enabled or index is None:
            return
        pl = self.get_pair_logger(index)
        text = (
            f"=== Iteration {iteration} ===\n"
            f"- proof length: {proof_len} chars\n"
        )
        pl.write(text)

    def write_judge1(self, index: int, accepted: bool, feedback_len: Optional[int] = None) -> None:
        if not self.is_enabled or index is None:
            return
        pl = self.get_pair_logger(index)
        if accepted:
            text = "- Judge #1: ACCEPT -> forwarding to Judge #2\n"
        else:
            text = f"- Judge #1: REJECT (feedback length: {feedback_len or 0})\n\n"
        pl.write(text)

    def write_judge2(self, index: int, accepted: bool, feedback_len: Optional[int] = None) -> None:
        if not self.is_enabled or index is None:
            return
        pl = self.get_pair_logger(index)
        if accepted:
            text = "- Judge #2: ACCEPT (final)\n\n"
        else:
            text = f"- Judge #2: REJECT (feedback length: {feedback_len or 0})\n\n"
        pl.write(text)

    # --- Detailed per-iteration logging ---
    def write_iteration_start(self, index: int, iteration: int, proof_markdown: str) -> None:
        """Create/reset Iteration{iteration}.log and write the proof section.

        The content is designed to be human-readable with clear separators.
        """
        if not self.is_enabled or index is None:
            return
        path = self._iter_filepath(index, iteration)
        header = (
            f"========================================\n"
            f"Iteration {iteration} - Prover Output\n"
            f"========================================\n\n"
            f"[PROOF - Markdown]\n\n"
        )
        with self._lock:
            path.write_text(header + (proof_markdown or "(empty proof)\n"), encoding="utf-8")
            with path.open("a", encoding="utf-8") as f:
                f.write("\n\n----------------------------------------\n")

    def append_judge1_detail(self, index: int, iteration: int, accepted: bool, feedback: Optional[str]) -> None:
        if not self.is_enabled or index is None:
            return
        path = self._iter_filepath(index, iteration)
        decision = "ACCEPT" if accepted else "REJECT"
        section = (
            f"\nJudge #1 Assessment\n"
            f"Decision: {decision}\n"
        )
        if not accepted:
            fb = (feedback or "").strip()
            if fb:
                section += f"\nFeedback (first flaw):\n\n{fb}\n"
        with self._lock:
            with path.open("a", encoding="utf-8") as f:
                f.write(section)
                f.write("\n----------------------------------------\n")

    def append_judge2_detail(self, index: int, iteration: int, accepted: bool, feedback: Optional[str]) -> None:
        if not self.is_enabled or index is None:
            return
        path = self._iter_filepath(index, iteration)
        decision = "ACCEPT" if accepted else "REJECT"
        section = (
            f"\nJudge #2 Assessment\n"
            f"Decision: {decision}\n"
        )
        if not accepted:
            fb = (feedback or "").strip()
            if fb:
                section += f"\nFeedback (first flaw):\n\n{fb}\n"
        with self._lock:
            with path.open("a", encoding="utf-8") as f:
                f.write(section)
                f.write("\n========================================\n\n")


logging_manager = ProverSolverLogManager()
