"""Pydantic output schemas for structured responses."""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, AliasChoices, ConfigDict, field_validator


class ProofResponse(BaseModel):
    """Structured output for a proof request."""

    model_config = ConfigDict(extra="ignore")

    proof_markdown: str = Field(
        ...,
        description="A self-contained Markdown proof body including a proof environment",
        validation_alias=AliasChoices("proof_markdown", "markdown", "proof"),
    )


class JudgeResponse(BaseModel):
    """Structured output for a judge assessment."""

    model_config = ConfigDict(extra="ignore")

    correctness: bool = Field(
        ...,
        description="True if the proof is fully correct and rigorous, else False",
        validation_alias=AliasChoices("correctness", "correct", "is_correct"),
    )
    feedback: str = Field(
        ...,
        description=(
            "A short explanation pointing out ONLY the first logical flaw and why it is a flaw; "
            "no fixes, no extra issues, no additional commentary."
        ),
        validation_alias=AliasChoices(
            "feedback",
            "flaw",
            "flaws",
            "errors",
            "issues",
            "reason",
            "message",
            "notes",
        ),
    )

    @field_validator("feedback", mode="before")
    @classmethod
    def _normalize_feedback(cls, v):  # type: ignore[no-untyped-def]
        if v is None:
            return ""
        if isinstance(v, str):
            return v
        if isinstance(v, list):
            return "\n".join([str(x) for x in v if x is not None])
        if isinstance(v, dict):
            for key in ("feedback", "flaw", "first_flaw", "detail", "message", "error", "reason", "notes"):
                if key in v:
                    val = v[key]
                    if isinstance(val, str):
                        return val
                    if isinstance(val, list):
                        return "\n".join([str(x) for x in val if x is not None])
                    return str(val)
            return str(v)
        return str(v)


class FinalJudgeResponse(BaseModel):
    """Structured output for the final-judge selection among multiple proofs."""

    model_config = ConfigDict(extra="ignore")

    chosen_index: int = Field(
        ..., description="0-based index of the selected proof deemed least incorrect",
        validation_alias=AliasChoices("chosen_index", "index", "choice"),
    )


class LiteratureContext(BaseModel):
    """Structured extraction of literature context from one or more papers/articles."""

    model_config = ConfigDict(extra="ignore")

    annotations: str = Field(
        ...,
        description=(
            "Markdown text defining common mathematical annotations and notation to be used "
            "throughout, using LaTeX math symbols where appropriate."
        ),
    )
    results: str = Field(
        ...,
        description=(
            "Markdown list of important results (theorems, lemmas, corollaries) distilled from the input, "
            "expressed using the chosen annotations. ONLY state results; do not include proofs. Use LaTeX math."
        ),
    )
    open_questions: List[str] = Field(
        ...,
        description=(
            "List of genuine open questions remaining after considering all provided works. "
            "Exclude questions that are resolved by any of the given references. Use Markdown with LaTeX math."
        ),
    )


# Note: Geometry detection schema removed since geometry detector is deprecated.

class LiteratureResultItem(BaseModel):
    """Single literature result item.

    Fields:
    - statement: result in Markdown with KaTeX-compatible math
    - url: source URL for the statement
    """

    model_config = ConfigDict(extra="ignore")

    statement: str = Field(
        ...,
        description=(
            "Result statement in Markdown (KaTeX-compatible). Use inline $...$ and display $$...$$ as needed."
        ),
        validation_alias=AliasChoices(
            "statement",
            "result",
            "latex",
            "result_latex",
            "result_statement_latex",
        ),
    )
    url: str = Field(
        ...,
        description="Source URL for the result statement (or seed://input for the seed).",
        validation_alias=AliasChoices("url", "source", "link"),
    )

class LiteratureReviewResult(BaseModel):
    """Structured output for literature review via web search.

    - annotations: shared notation/definitions used in all result statements (Markdown with LaTeX)
    - results: list of structured items with fields {statement, url}; the first entry must echo the input seed result
    """

    model_config = ConfigDict(extra="ignore")

    annotations: str = Field(
        ...,
        description=(
            "Markdown text defining common mathematical annotations and notation to be used throughout, "
            "using LaTeX math symbols where appropriate."
        ),
    )
    # Switch to a structured item type for clarity and future-proofing
    results: List["LiteratureResultItem"] = Field(
        ...,
        description=(
            "List of result items with Markdown KaTeX statements and URLs. The first item must contain the input seed result and a source tag."
        ),
    )

    @field_validator("results", mode="before")
    @classmethod
    def _normalize_results(cls, v):  # type: ignore[no-untyped-def]
        """Allow legacy shapes like [[stmt, url]] or dicts with result_latex/url keys."""
        if v is None:
            return []
        normalized: list[dict[str, str]] = []
        if isinstance(v, dict):
            v = [v]
        if isinstance(v, (list, tuple)):
            for item in v:
                # Legacy list/tuple pair
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    stmt, url = item[0], item[1]
                    normalized.append({"statement": str(stmt), "url": str(url)})
                    continue
                # Dict-like inputs
                if isinstance(item, dict):
                    stmt = (
                        item.get("statement")
                        or item.get("result")
                        or item.get("result_latex")
                        or item.get("result_statement_latex")
                        or item.get("latex")
                    )
                    src = item.get("url") or item.get("source") or item.get("link")
                    if stmt is not None and src is not None:
                        normalized.append({"statement": str(stmt), "url": str(src)})
                        continue
                # Fallback: stringify
                normalized.append({"statement": str(item), "url": ""})
            return normalized
        # Unknown type: return empty list
        return []


class PredictedResults(BaseModel):
    """Structured output for predicted new results based on a literature review.

    - annotations: shared notation/definitions (may refine the literature annotations)
    - predicted_results: list of Markdown (KaTeX-compatible) conjectured results that the agent believes to be novel
    """

    annotations: str = Field(
        ...,
        description=(
            "Markdown text defining shared notation and symbols (KaTeX-compatible). May reference or refine prior annotations."
        ),
    )
    predicted_results: List[str] = Field(
        ...,
        description=(
            "List of Markdown (KaTeX-compatible) statements for predicted new results (conjectures) vetted for likely novelty via web search."
        ),
    )


class FinalReport(BaseModel):
    """Structured output for the compiled final Markdown report."""

    model_config = ConfigDict(extra="ignore")

    report_markdown: str = Field(
        ...,
        description="Beautifully formatted Markdown (KaTeX-compatible) report combining literature context and new results with proofs.",
        validation_alias=AliasChoices("report_markdown", "markdown", "report"),
    )


class NoveltyCheck(BaseModel):
    """Structured output for novelty verification of a predicted result."""

    model_config = ConfigDict(extra="ignore")

    is_novel: bool = Field(
        ...,
        description=(
            "True if the predicted result appears to be novel (no existing equal/stronger result found); False otherwise."
        ),
        validation_alias=AliasChoices("is_novel", "novel", "is_new", "novelty"),
    )
    matched_statement: str | None = Field(
        None,
        description=(
            "If not novel, the closest matched known result statement (Markdown/LaTeX) that justifies non-novelty."
        ),
        validation_alias=AliasChoices(
            "matched_statement",
            "existing_statement",
            "prior_statement",
            "match_statement",
        ),
    )
    matched_url: str | None = Field(
        None,
        description="If not novel, a reliable source URL for the matched known result.",
        validation_alias=AliasChoices(
            "matched_url",
            "existing_url",
            "prior_url",
            "source",
            "url",
            "link",
        ),
    )


class ResultRefinementResponse(BaseModel):
    """Structured output for refining a statement and its proof.

    - new_statement: the refined statement string after applying all rules
    - new_proof_markdown: the refined proof in Markdown
    - changed: whether any change was applied; if false, caller may treat result as None
    """

    model_config = ConfigDict(extra="ignore")

    new_statement: str = Field(
        ...,
        description=(
            "Refined statement string with unused assumptions removed, any (Conjecture ...) annotations stripped, "
            "and corrected if disproved."
        ),
        validation_alias=AliasChoices("new_statement", "statement", "refined_statement"),
    )
    new_proof_markdown: str = Field(
        ...,
        description=(
            "Refined proof in Markdown; if the original proof disproved the statement, this proof should assume the contrary."
        ),
        validation_alias=AliasChoices("new_proof_markdown", "proof_markdown", "markdown", "proof"),
    )
    changed: bool = Field(
        ...,
        description="True if any refinement was applied; False if no changes were necessary.",
        validation_alias=AliasChoices("changed", "is_changed", "modified"),
    )


class RefineTightenResult(BaseModel):
    """Structured output for tightening a disproving proof's statement and proof.

    - can_tighten: whether the problem statement can be tightened (remove or weaken assumptions) while keeping the proof valid
    - updated_statement: the tightened statement (if can_tighten=true), else echo the original or leave empty
    - updated_proof: the updated proof in Markdown consistent with the tightened statement (if can_tighten=true)
    """

    model_config = ConfigDict(extra="ignore")

    can_tighten: bool = Field(
        ...,
        description=(
            "True if the proof can be adapted to a strictly tighter problem by removing extraneous assumptions or sharpening the claim without invalidating correctness."
        ),
        validation_alias=AliasChoices("can_tighten", "tightenable", "tighten"),
    )
    updated_statement: str = Field(
        "",
        description=(
            "If can_tighten is true, the tightened problem statement in Markdown/LaTeX; otherwise may be empty or copy of original."
        ),
        validation_alias=AliasChoices("updated_statement", "new_statement", "statement"),
    )
    updated_proof: str = Field(
        "",
        description=(
            "If can_tighten is true, an updated proof in Markdown fully consistent with updated_statement; otherwise may be empty or copy of original."
        ),
        validation_alias=AliasChoices("updated_proof", "new_proof_markdown", "proof_markdown", "proof"),
    )


class PaperLabelAssignment(BaseModel):
    """Structured label assignment for a single result."""

    model_config = ConfigDict(extra="ignore")

    label: str = Field(
        ...,
        description="Candidate LaTeX label identifier (letters, digits, optional single colon).",
        validation_alias=AliasChoices("label", "latex_label"),
    )


class PaperDependencyItem(BaseModel):
    """Dependency descriptor for LaTeX paper generation."""

    model_config = ConfigDict(extra="ignore")

    kind: Literal["internal", "external"] = Field(
        ...,
        description="'internal' for references to other results in the batch; 'external' for literature sources requiring bibliography.",
        validation_alias=AliasChoices("kind", "type"),
    )
    target_label: str | None = Field(
        None,
        description="Label of the referenced internal result when kind='internal'.",
        validation_alias=AliasChoices("target_label", "label", "latex_label"),
    )
    url: str | None = Field(
        None,
        description="URL for the referenced external source when kind='external'.",
        validation_alias=AliasChoices("url", "source", "link"),
    )
    note: str | None = Field(
        None,
        description="Optional short note describing how the dependency is used.",
        validation_alias=AliasChoices("note", "description", "reason"),
    )

    @field_validator("target_label", mode="after")
    @classmethod
    def _validate_internal(cls, v, info):  # type: ignore[no-untyped-def]
        kind = info.data.get("kind")
        if kind == "internal":
            if v is None:
                return None
            cleaned = str(v).strip()
            return cleaned or None
        return v

    @field_validator("url", mode="after")
    @classmethod
    def _validate_external(cls, v, info):  # type: ignore[no-untyped-def]
        kind = info.data.get("kind")
        if kind == "external":
            if v is None:
                return None
            cleaned = str(v).strip()
            return cleaned or None
        return v


class PaperDependenciesResponse(BaseModel):
    """Structured output capturing dependency lists for a result."""

    model_config = ConfigDict(extra="ignore")

    dependencies: List[PaperDependencyItem] = Field(
        default_factory=list,
        description="Dependencies referencing internal labels or external URLs required by the proof.",
        validation_alias=AliasChoices("dependencies", "refs", "references"),
    )


class BibliographyEntry(BaseModel):
    """Structured bibliography entry for bib.tex generation."""

    model_config = ConfigDict(extra="ignore")

    key: str = Field(
        ...,
        description="Citation key used for \cite commands and \bibitem identifiers (alphanumeric, no spaces).",
        validation_alias=AliasChoices("key", "citation_key", "id"),
    )
    citation_text: str = Field(
        ...,
        description="Full text of the bibliographic entry to appear after \\bibitem, including authors, title, venue, and optional year.",
        validation_alias=AliasChoices("citation_text", "text", "entry"),
    )
    url: str = Field(
        ...,
        description="Canonical URL for the source; included to ensure reproducibility and tie back to dependencies.",
        validation_alias=AliasChoices("url", "link", "source"),
    )


class BibliographyEntries(BaseModel):
    """Container for a list of bibliography entries."""

    model_config = ConfigDict(extra="ignore")

    entries: List[BibliographyEntry] = Field(
        default_factory=list,
        description="List of bibliography entries for bib.tex generation.",
        validation_alias=AliasChoices("entries", "items", "bibliography"),
    )


class GeneratedTex(BaseModel):
    """Generic structured wrapper for generated LaTeX content."""

    model_config = ConfigDict(extra="ignore")

    content: str = Field(
        ...,
        description="Complete LaTeX source for a file.",
        validation_alias=AliasChoices("content", "latex", "tex"),
    )
    newcommands: List[str] = Field(
        default_factory=list,
        description="List of LaTeX newcommand definitions used within the content.",
        validation_alias=AliasChoices("newcommands", "macros", "commands"),
    )

class LatexRefinerFileUpdate(BaseModel):
    """Instruction describing a single LaTeX source update."""

    model_config = ConfigDict(extra="ignore")

    file_path: str = Field(
        ...,
        description="Path to the file to update, relative to the LaTeX project root.",
        validation_alias=AliasChoices("file_path", "path", "filename"),
    )
    content: str = Field(
        ...,
        description="Full replacement content for the target file in UTF-8.",
        validation_alias=AliasChoices("content", "text", "body"),
    )


class LatexRefinerResponse(BaseModel):
    """Structured response for LaTeX compilation repairs."""

    model_config = ConfigDict(extra="ignore")

    updates: List[LatexRefinerFileUpdate] = Field(
        default_factory=list,
        description="Ordered list of file updates to apply.",
        validation_alias=AliasChoices("updates", "files", "patches"),
    )
    notes: Optional[str] = Field(
        None,
        description="Optional short explanation of the fixes that were applied.",
        validation_alias=AliasChoices("notes", "explanation", "summary"),
    )
