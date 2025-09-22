from __future__ import annotations

import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence
from urllib.parse import urlparse

from .output_schemas import (
    BibliographyEntries,
    BibliographyEntry,
    GeneratedTex,
    PaperDependencyItem,
    PaperDependenciesResponse,
    PaperLabelAssignment,
)
from .prompts import (
    PAPER_BIBLIOGRAPHY_SYSTEM_PROMPT,
    PAPER_DEPENDENCY_SYSTEM_PROMPT,
    PAPER_LABEL_SYSTEM_PROMPT,
    PAPER_MAIN_SYSTEM_PROMPT,
    PAPER_RELATED_BIB_SYSTEM_PROMPT,
    PAPER_RESULT_SYSTEM_PROMPT,
    build_paper_bibliography_prompt,
    build_paper_dependency_prompt,
    build_paper_label_prompt,
    build_related_work_bibliography_prompt,
    build_paper_main_prompt,
    build_paper_result_tex_prompt,
)
from .tool_llm import generate_structured_with_tools


@dataclass
class ResultEntry:
    statement: str
    proof_markdown: str


@dataclass
class PreparedResult:
    statement: str
    proof_markdown: str
    latex_label: str
    file_stem: str
    dependencies: List[PaperDependencyItem]
    external_urls: List[str]
    newcommands: List[str]


@dataclass
class LatexPaperConverterConfig:
    label_model: str = "gpt-5-mini"
    label_reasoning: str = "medium"
    dependency_model: str = "gpt-5"
    dependency_reasoning: str = "medium"
    bib_model: str = "gpt-5-mini"
    bib_reasoning: str = "medium"
    result_model: str = "gpt-5"
    result_reasoning: str = "medium"
    main_model: str = "gpt-5"
    main_reasoning: str = "medium"
    timeout: float = 300.0
    main_timeout: float = 900.0


def _web_search_tool() -> dict:
    # Medium context balances recall and latency for literature lookups.
    return {"type": "web_search", "search_context_size": "medium"}


def _ensure_results(data: Sequence[dict]) -> List[ResultEntry]:
    results: List[ResultEntry] = []
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"Result at index {idx} is not an object")
        statement = str(item.get("statement", "")).strip()
        proof = str(item.get("proof_markdown", "")).strip()
        if not statement or not proof:
            raise ValueError(f"Result at index {idx} is missing statement or proof_markdown")
        results.append(ResultEntry(statement=statement, proof_markdown=proof))
    if not results:
        raise ValueError("No result entries found in input JSON")
    return results


def _sanitize_label(raw: str, fallback: str) -> str:
    candidate = (raw or "").strip()
    candidate = candidate.replace(" ", "-").replace("_", "-")
    # Allow :, letters, digits, and hyphen
    candidate = re.sub(r"[^A-Za-z0-9:-]+", "-", candidate)
    candidate = candidate.strip("-:")
    if not candidate:
        candidate = fallback
    return candidate


def _filename_from_label(label: str) -> str:
    # Windows does not permit ':' in filenames; replace with underscores for file stems.
    stem = label.replace(":", "_")
    stem = stem.replace(" ", "_")
    stem = re.sub(r"[^A-Za-z0-9_\-]+", "_", stem)
    stem = stem.strip("_") or "result"
    return stem


def _is_http_url(url: str) -> bool:
    parsed = urlparse(url.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _unique_preserve(items: Iterable[str]) -> List[str]:
    seen: set[str] = set()
    ordered: List[str] = []
    for item in items:
        candidate = item.strip()
        if not candidate:
            continue
        if candidate in seen:
            continue
        seen.add(candidate)
        ordered.append(candidate)
    return ordered


class LatexPaperConverter:
    def __init__(self, config: Optional[LatexPaperConverterConfig] = None) -> None:
        self.config = config or LatexPaperConverterConfig()
        self.logger = logging.getLogger(self.__class__.__name__)

    def convert(self, json_path: str | Path) -> Path:
        """Convert a JSON file of results into a LaTeX paper folder."""

        src_path = Path(json_path).expanduser().resolve()
        if not src_path.exists():
            raise FileNotFoundError(f"Input JSON file not found: {src_path}")
        data = json.loads(src_path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("Input JSON must be an array of objects")

        results = _ensure_results(data)

        output_dir = src_path.with_suffix("")
        output_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("[Paper] Loaded %d results from %s", len(results), src_path)

        raw_labels = self._assign_labels(results)
        final_labels = self._finalize_labels(raw_labels)

        dependencies = self._collect_dependencies(results, final_labels)
        prepared = self._assemble_results(results, final_labels, dependencies)

        bib_entries = self._build_bibliography(prepared)
        bib_preview = self._write_bibliography_file(bib_entries, output_dir)

        label_to_statement = {pr.latex_label: pr.statement for pr in prepared}
        tex_files = self._write_result_files(
            prepared,
            label_to_statement,
            bib_entries,
            bib_preview,
            output_dir,
        )

        self._write_main_file(prepared, bib_entries, tex_files, output_dir)

        self.logger.info("[Paper] Conversion complete: %s", output_dir)

        # Final step: generate a debugging prompt and copy it to the clipboard
        prompt_text = (
            f"there's a latex paper in {output_dir}\n\n"
            "Debug it for me until there's no more error in the compiler.\n"
            "You should:\n"
            "- comment all \"\\input{{...}}\" lines first, compile, ignore all \\ref to unknown label messages, fix the other errors\n"
            "- then one line at a time, uncomment \"\\input{{...}}\", compile, and fix the errors (still ignore all \\ref to unknown label messages)\n"
            "- after fixing all errors, check for unidentified references (\\ref to unknown label) then fix them\n"
            "- tidy all overfull and underfull \\hbox\n"
        )
        try:
            self._copy_to_clipboard(prompt_text)
            self.logger.info("[Paper] Copied debugging prompt to clipboard.")
        except Exception as _e:
            self.logger.warning("[Paper] Failed to copy prompt to clipboard: %s", _e)
        # Also persist the prompt alongside the project for convenience
        try:
            (output_dir / "DEBUG_PROMPT.txt").write_text(prompt_text, encoding="utf-8")
        except Exception:
            pass
        return output_dir

    # ------------------------------------------------------------------
    # Labeling and dependency extraction

    def _assign_labels(self, results: Sequence[ResultEntry]) -> List[str]:
        if not results:
            return []

        labels: List[str] = [""] * len(results)

        def _task(idx: int, entry: ResultEntry) -> str:
            messages = [
                {"role": "system", "content": PAPER_LABEL_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": build_paper_label_prompt(idx, entry.statement),
                },
            ]
            resp = generate_structured_with_tools(
                messages=messages,
                response_model=PaperLabelAssignment,
                model=self.config.label_model,
                tools=[],
                tool_registry={},
                reasoning_effort=self.config.label_reasoning,
                timeout=self.config.main_timeout,
            )
            return resp.output_parsed.label

        max_workers = min(8, len(results)) or 1
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(_task, idx, entry): idx for idx, entry in enumerate(results)}
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    label = future.result()
                except Exception as exc:  # pragma: no cover - propagate after logging
                    self.logger.error("[Paper] Label assignment failed for index %d: %s", idx, exc)
                    raise
                labels[idx] = label
                self.logger.info("[Paper] Assigned label '%s' to result %d", label, idx)
        return labels

    def _finalize_labels(self, raw_labels: Sequence[str]) -> List[str]:
        finalized: List[str] = []
        seen: Dict[str, int] = {}
        for idx, raw in enumerate(raw_labels):
            fallback = f"result-{idx+1}"
            base = _sanitize_label(raw, fallback)
            if not base:
                base = fallback
            candidate = base
            counter = 1
            while candidate.lower() in seen:
                counter += 1
                candidate = f"{base}-{counter}"
            seen[candidate.lower()] = idx
            finalized.append(candidate)
        return finalized

    def _collect_dependencies(
        self,
        results: Sequence[ResultEntry],
        labels: Sequence[str],
    ) -> List[List[PaperDependencyItem]]:
        if len(results) != len(labels):
            raise ValueError("Label count does not match results count")

        labeled_statements = list(zip(labels, (r.statement for r in results)))

        def _task(idx: int, entry: ResultEntry) -> List[PaperDependencyItem]:
            messages = [
                {"role": "system", "content": PAPER_DEPENDENCY_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": build_paper_dependency_prompt(
                        labels[idx],
                        entry.statement,
                        entry.proof_markdown,
                        labeled_statements,
                    ),
                },
            ]
            resp = generate_structured_with_tools(
                messages=messages,
                response_model=PaperDependenciesResponse,
                model=self.config.dependency_model,
                tools=[_web_search_tool()],
                tool_registry={},
                reasoning_effort=self.config.dependency_reasoning,
                timeout=self.config.main_timeout,
            )
            return list(resp.output_parsed.dependencies)

        dependencies: List[List[PaperDependencyItem]] = [[] for _ in results]
        if not results:
            return dependencies

        max_workers = min(8, len(results)) or 1
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(_task, idx, entry): idx for idx, entry in enumerate(results)}
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    deps = future.result()
                except Exception as exc:  # pragma: no cover
                    self.logger.error("[Paper] Dependency extraction failed for %d: %s", idx, exc)
                    raise
                dependencies[idx] = deps
                self.logger.info(
                    "[Paper] Collected %d dependencies for label '%s'",
                    len(deps),
                    labels[idx],
                )
        return dependencies

    def _assemble_results(
        self,
        results: Sequence[ResultEntry],
        labels: Sequence[str],
        dependencies: Sequence[List[PaperDependencyItem]],
    ) -> List[PreparedResult]:
        if not (len(results) == len(labels) == len(dependencies)):
            raise ValueError("Mismatch assembling results: counts differ")

        prepared: List[PreparedResult] = []
        for entry, label, deps in zip(results, labels, dependencies):
            cleaned_deps: List[PaperDependencyItem] = []
            for dep in deps:
                if dep.kind == "internal":
                    label = (dep.target_label or "").strip()
                    if not label:
                        continue
                    cleaned_deps.append(dep.model_copy(update={"target_label": label}))
                elif dep.kind == "external":
                    url = (dep.url or "").strip()
                    if not url or not _is_http_url(url):
                        continue
                    cleaned_deps.append(dep.model_copy(update={"url": url}))
                else:
                    cleaned_deps.append(dep)
            file_stem = _filename_from_label(label)
            external_urls = _unique_preserve(
                dep.url
                for dep in cleaned_deps
                if dep.kind == "external" and dep.url and _is_http_url(dep.url)
            )
            prepared.append(
                PreparedResult(
                    statement=entry.statement,
                    proof_markdown=entry.proof_markdown,
                    latex_label=label,
                    file_stem=file_stem,
                    dependencies=list(cleaned_deps),
                    external_urls=external_urls,
                    newcommands=[],
                )
            )
        return prepared

    # ------------------------------------------------------------------
    # Bibliography

    @staticmethod
    def _escape_bib_text(text: str) -> str:
        specials = {'&', '%', '$', '#', '_'}
        result: list[str] = []
        i = 0
        length = len(text)
        while i < length:
            ch = text[i]
            if ch == '\\':
                result.append('\\')
                i += 1
                if i < length:
                    result.append(text[i])
                    i += 1
                continue
            if ch in specials:
                result.append('\\')
            result.append(ch)
            i += 1
        return ''.join(result)


    def _build_bibliography(self, prepared: Sequence[PreparedResult]) -> BibliographyEntries:
        raw_items: List[str] = []
        for item in prepared:
            for dep in item.dependencies:
                if dep.kind == "internal" and dep.target_label:
                    raw_items.append(dep.target_label.strip())
                elif dep.kind == "external" and dep.url:
                    raw_items.append(dep.url.strip())

        union_items = _unique_preserve(raw_items)
        url_candidates = [item for item in union_items if _is_http_url(item)]
        if not url_candidates:
            if union_items:
                self.logger.info("[Paper] Dependency union contains no URLs; skipping bibliography generation")
            else:
                self.logger.info("[Paper] No dependencies reported; skipping bibliography generation")
            return BibliographyEntries(entries=[])

        self.logger.info("[Paper] Building bibliography for %d URLs", len(url_candidates))
        messages = [
            {"role": "system", "content": PAPER_BIBLIOGRAPHY_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": build_paper_bibliography_prompt(union_items),
            },
        ]
        resp = generate_structured_with_tools(
            messages=messages,
            response_model=BibliographyEntries,
            model=self.config.bib_model,
            tools=[_web_search_tool()],
            tool_registry={},
            reasoning_effort=self.config.bib_reasoning,
            timeout=self.config.main_timeout,
        )
        parsed: BibliographyEntries = resp.output_parsed
        if not parsed.entries:
            self.logger.warning("[Paper] Bibliography generation returned empty entries; creating placeholder")
        return parsed

    def _write_bibliography_file(self, bib_entries: BibliographyEntries, output_dir: Path) -> str:
        lines: List[str] = []
        lines.append("% Auto-generated bibliography")
        lines.append("\begin{thebibliography}{99}")
        if bib_entries.entries:
            for entry in bib_entries.entries:
                citation = entry.citation_text.strip()
                if "\\url{" not in citation:
                    citation = (f"{citation} \\url{{{entry.url.strip()}}}").strip()
                citation = self._escape_bib_text(citation)
                key = self._escape_bib_text(entry.key.strip())
                lines.append(f"\bibitem{{{key}}} {citation}")
        else:
            lines.append("\bibitem{Placeholder} No external references were required for this manuscript.")
        lines.append("\end{thebibliography}")
        content = "\n".join(lines) + "\n"
        (output_dir / "bib.tex").write_text(content, encoding="utf-8")
        self.logger.info("[Paper] Wrote bibliography to %s", output_dir / "bib.tex")
        return content


    def _extend_bibliography_with_related_work(
        self,
        prepared: Sequence[PreparedResult],
        bib_entries: BibliographyEntries,
    ) -> int:
        if not prepared:
            return 0

        labeled_statements = [(p.latex_label, p.statement) for p in prepared]
        existing_keys = [entry.key for entry in bib_entries.entries]

        messages = [
            {"role": "system", "content": PAPER_RELATED_BIB_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": build_related_work_bibliography_prompt(
                    labeled_statements,
                    existing_keys,
                ),
            },
        ]

        try:
            resp = generate_structured_with_tools(
                messages=messages,
                response_model=BibliographyEntries,
                model=self.config.main_model,
                tools=[_web_search_tool()],
                tool_registry={},
                reasoning_effort=self.config.main_reasoning,
                timeout=self.config.main_timeout,
            )
        except Exception as exc:  # pragma: no cover
            self.logger.warning("[Paper] Related work augmentation skipped: %s", exc)
            return 0

        new_entries = []
        existing_keys_lower = {entry.key.lower() for entry in bib_entries.entries}
        existing_urls = {entry.url for entry in bib_entries.entries}

        for entry in resp.output_parsed.entries:
            key_lower = entry.key.lower().strip()
            if not key_lower or key_lower in existing_keys_lower:
                continue
            if entry.url in existing_urls:
                continue
            new_entries.append(entry)
            existing_keys_lower.add(key_lower)
            existing_urls.add(entry.url)

        if new_entries:
            bib_entries.entries.extend(new_entries)
            self.logger.info("[Paper] Added %d related-work references", len(new_entries))
        else:
            self.logger.info("[Paper] No additional related-work references were added")
        return len(new_entries)

    # ------------------------------------------------------------------
    # Per-result files

    def _write_result_files(
        self,
        prepared: Sequence[PreparedResult],
        label_to_statement: Dict[str, str],
        bib_entries: BibliographyEntries,
        bib_preview: str,
        output_dir: Path,
    ) -> List[str]:
        if not prepared:
            return []

        url_to_entry: Dict[str, BibliographyEntry] = {e.url: e for e in bib_entries.entries}
        filenames: List[str] = [""] * len(prepared)
        newcommands_per_result: List[List[str]] = [[] for _ in prepared]

        def _task(idx: int, prep: PreparedResult) -> tuple[int, str, List[str]]:
            internal_pairs: List[tuple[str, str]] = []
            seen_internal: set[str] = set()
            for dep in prep.dependencies:
                if dep.kind == "internal" and dep.target_label and dep.target_label not in seen_internal:
                    stmt = label_to_statement.get(dep.target_label)
                    if stmt:
                        internal_pairs.append((dep.target_label, stmt))
                        seen_internal.add(dep.target_label)

            external_pairs: List[tuple[str, str, str]] = []
            seen_urls: set[str] = set()
            for url in prep.external_urls:
                if url in seen_urls or url not in url_to_entry:
                    continue
                entry = url_to_entry[url]
                external_pairs.append((entry.key, url, entry.citation_text))
                seen_urls.add(url)

            dependency_summary = []
            for dep in prep.dependencies:
                if dep.kind == "internal" and dep.target_label:
                    dependency_summary.append(f"internal:{dep.target_label}")
                elif dep.kind == "external" and dep.url:
                    dependency_summary.append(f"external:{dep.url}")
            dependency_summary = _unique_preserve(dependency_summary)

            messages = [
                {"role": "system", "content": PAPER_RESULT_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": build_paper_result_tex_prompt(
                        prep.latex_label,
                        prep.statement,
                        prep.proof_markdown,
                        internal_pairs,
                        external_pairs,
                        bib_preview,
                        dependency_summary,
                    ),
                },
            ]
            resp = generate_structured_with_tools(
                messages=messages,
                response_model=GeneratedTex,
                model=self.config.result_model,
                tools=[_web_search_tool()],
                tool_registry={},
                reasoning_effort=self.config.result_reasoning,
                timeout=self.config.main_timeout,
            )
            parsed = resp.output_parsed
            tex: str = parsed.content
            filename = f"{prep.file_stem}.tex"
            (output_dir / filename).write_text(tex, encoding="utf-8")
            new_cmds = [cmd.strip() for cmd in parsed.newcommands or [] if cmd and cmd.strip()]
            return idx, filename, new_cmds

        max_workers = min(8, len(prepared)) or 1
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(_task, idx, prep): idx for idx, prep in enumerate(prepared)
            }
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    position, filename, new_cmds = future.result()
                except Exception as exc:  # pragma: no cover
                    self.logger.error("[Paper] Writing result file failed for %s: %s", prepared[idx].latex_label, exc)
                    raise
                filenames[position] = filename
                newcommands_per_result[position] = new_cmds
                prepared[position].newcommands = new_cmds
                self.logger.info("[Paper] Wrote result %s to %s", prepared[position].latex_label, filename)

        return filenames

    # ------------------------------------------------------------------
    # Main file

    def _write_main_file(
        self,
        prepared: Sequence[PreparedResult],
        bib_entries: BibliographyEntries,
        tex_files: Sequence[str],
        output_dir: Path,
    ) -> None:
        added = self._extend_bibliography_with_related_work(prepared, bib_entries)
        bib_preview = self._write_bibliography_file(bib_entries, output_dir) if added else (output_dir / "bib.tex").read_text(encoding="utf-8")
        labeled_statements = [(prep.latex_label, prep.statement) for prep in prepared]
        bibliography_keys = [entry.key for entry in bib_entries.entries]
        all_newcommands = []
        seen_commands = set()
        for prep in prepared:
            for cmd in prep.newcommands:
                normalized = cmd.strip()
                if not normalized or normalized.lower() in seen_commands:
                    continue
                seen_commands.add(normalized.lower())
                all_newcommands.append(normalized)
        messages = [
            {"role": "system", "content": PAPER_MAIN_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": build_paper_main_prompt(
                    labeled_statements,
                    bibliography_keys,
                    list(tex_files),
                ),
            },
            {
                "role": "user",
                "content": "Aggregated \newcommand definitions (define each once in the preamble; skip duplicates if the same command name appears):\n" + ("\n".join(all_newcommands) if all_newcommands else "(none)"),
            },
            {
                "role": "user",
                "content": "Preamble requirements for theorem environments (support nested lemmas and their proofs inside theorem proofs):\n\theoremstyle{plain}\n\newtheorem{theorem}{Theorem}[section]\n\newtheorem{lemma}[theorem]{Lemma}\n\newtheorem{proposition}[theorem]{Proposition}\n\newtheorem{corollary}[theorem]{Corollary}\n\theoremstyle{definition}\n\newtheorem{definition}[theorem]{Definition}\n\theoremstyle{remark}\n\newtheorem{remark}[theorem]{Remark}\nUse the optional argument to \begin{proof}[...] when proving lemmas inside theorem proofs.\n",
            },
        ]
        resp = generate_structured_with_tools(
            messages=messages,
            response_model=GeneratedTex,
            model=self.config.main_model,
            tools=[_web_search_tool()],
            tool_registry={},
            reasoning_effort=self.config.main_reasoning,
            timeout=self.config.main_timeout,
        )
        main_tex = resp.output_parsed.content
        (output_dir / "main.tex").write_text(main_tex, encoding="utf-8")
        self.logger.info("[Paper] Wrote main.tex to %s", output_dir / "main.tex")

    # ------------------------------------------------------------------
    # Utilities

    def _copy_to_clipboard(self, text: str) -> None:
        """Copy the given text to the system clipboard using best-effort fallbacks.

        Tries pyperclip if installed, else uses platform tools:
        - Windows: clip
        - macOS: pbcopy
        - Linux: xclip or xsel (clipboard selection)
        Raises on failure.
        """
        try:
            import pyperclip  # type: ignore
            pyperclip.copy(text)
            return
        except Exception:
            pass

        if os.name == "nt":  # Windows
            # Use built-in clip command
            completed = subprocess.run(
                "clip",
                input=text,
                text=True,
                shell=True,
                check=False,
            )
            if completed.returncode != 0:
                raise RuntimeError("Failed to use Windows clip to set clipboard")
            return

        # macOS
        if sys.platform == "darwin":
            completed = subprocess.run(["pbcopy"], input=text, text=True, check=False)
            if completed.returncode != 0:
                raise RuntimeError("Failed to use pbcopy to set clipboard")
            return

        # Linux/X11 fallbacks
        for cmd in (["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"]):
            try:
                completed = subprocess.run(cmd, input=text, text=True, check=False)
                if completed.returncode == 0:
                    return
            except Exception:
                continue
        raise RuntimeError("No clipboard mechanism available (pyperclip/pbcopy/xclip/xsel)")

    # (No compile/refiner steps; conversion ends after writing main.tex.)




