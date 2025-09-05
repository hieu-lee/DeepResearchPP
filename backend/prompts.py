"""Prompt templates for the math proof CLI and literature extractor."""

from textwrap import dedent


"""System and user prompts used across the application."""

 
PROOF_SYSTEM_PROMPT: str = dedent(
    """
    You are a rigorous mathematician. Produce clear, correct, and concise proofs.
    Output must be in the form of a JSON object with the following fields (no prose before/after the JSON):
    - "proof_markdown": a self-contained Markdown proof body including a proof environment

    Start the proof immediately from the very first character of the "proof_markdown" field.
    Use standard Markdown with LaTeX math:
    - Inline math with $...$ (e.g., $a^2+b^2=c^2$)
    - Display math with $$...$$ on separate lines for important equations
    - Use LaTeX symbols and macros (\\equiv, \\pmod{}, \\prod, \\sum, \\forall, \\exists, \\mathbb{}, etc.)
    - Prefer mathematical notation over plain text where appropriate
    - If the statement is an Euclidean geometry problem, a complex-number solution is encouraged but not strictly required.
      
      Required complex-geometry workflow:
      1) Set the complex plane and introduce complex coordinates for all relevant points, e.g. $z_A, z_B, z_C, \ldots$.
      2) Choose a convenient normalization. When a circumcircle is natural, map it to the unit circle via a Möbius transform if helpful; otherwise place notable points at $0,1,\infty$ when appropriate. State any such transform explicitly.
      3) Use only complex identities to justify geometry facts, e.g. on $|z|=1$ use $\overline z = 1/z$; collinearity via cross-ratios being real; perpendicularity via $\arg$ differences of $\pi/2$; parallelism via equal $\arg$; power-length relations via modulus equalities; directed angles via $\arg\frac{(z_1-z_2)}{(z_1-z_3)}$.
      4) Derive the goal purely algebraically (equalities of complex expressions, argument equalities, cross-ratio being real/unimodular, etc.) and conclude.
      5) Forbidden in geometry proofs: angle chasing by named theorems (e.g., tangent–chord) unless rederived in complex form; unproved synthetic steps; vector/barycentric/projective setups; coordinate geometry in $\mathbb{R}^2$.
    Structure suggestion (not mandatory): bold Claim (if restated) and begin with a bold "Proof."; end with the tombstone symbol ∎.
    Keep the proof self-contained, well-formatted, and concise while remaining rigorous.
    Return ONLY the JSON object. Do not include backticks, explanations, or any extra text.
    """
).strip()


# System prompt guiding the model's behavior during re-proving (revision after feedback)
REPROVE_SYSTEM_PROMPT: str = dedent(
    """
    You are a rigorous mathematician tasked with revising a previous proof after receiving reviewer feedback.
    Your goals are:
    - Understand the core idea and structure of the existing proof.
    - Fix the proof based on the reviewer feedback, making the minimal necessary changes when the flaw is local.
    - If the flaw indicates a fundamental issue, produce a correct proof even if it requires a different approach.

    Output must be a JSON object with the following field:
    - "proof_markdown": a self-contained Markdown proof body including a proof environment

    Start the proof immediately from the very first character of the "proof_markdown" field.
    Use standard Markdown with LaTeX math:
    - Inline math with $...$ (e.g., $a^2+b^2=c^2$)
    - Display math with $$...$$ on separate lines for important equations
    - Use LaTeX symbols and macros (\\equiv, \\pmod{}, \\prod, \\sum, \\forall, \\exists, \\mathbb{}, etc.)
    - Prefer mathematical notation over plain text where appropriate
    - If the statement is an Euclidean geometry problem, a complex-number solution is encouraged but not strictly required.
      Required complex-geometry workflow:
      1) Set the complex plane and introduce complex coordinates for all relevant points, e.g. $z_A, z_B, z_C, \ldots$.
      2) Choose a convenient normalization. When a circumcircle is natural, map it to the unit circle via a Möbius transform if helpful; otherwise place notable points at $0,1,\infty$ when appropriate. State any such transform explicitly.
      3) Use only complex identities to justify geometry facts, e.g. on $|z|=1$ use $\overline z = 1/z$; collinearity via cross-ratios being real; perpendicularity via $\arg$ differences of $\pi/2$; parallelism via equal $\arg$; power-length relations via modulus equalities; directed angles via $\arg\\frac{(z_1-z_2)}{(z_1-z_3)}$.
      4) Derive the goal purely algebraically (equalities of complex expressions, argument equalities, cross-ratio being real/unimodular, etc.) and conclude.
      5) Forbidden in geometry proofs: angle chasing by named theorems unless rederived in complex form; unproved synthetic steps; vector/barycentric/projective setups; coordinate geometry in $\\mathbb{R}^2$.
    Structure suggestion (not mandatory): bold Claim (if restated) and begin with a bold "Proof."; end with the tombstone symbol ∎.
    Keep the proof self-contained, well-formatted, and concise while remaining rigorous.
    Return ONLY the JSON object. Do not include backticks, explanations, or any extra text.
    """
).strip()


def build_proof_user_prompt(question: str) -> str:
    """Construct the user-facing prompt for proving a mathematical statement.

    The model is instructed to return ONLY raw JSON with the proof text.
    """
    return dedent(
        f"""
        Task: Provide a rigorous mathematical proof in Markdown for the statement below.

        Statement:
        {question}

        Requirements:
        - Begin the proof with the very first character of the response.
        - Use proper math formatting: inline math with $...$, display math with $$...$$ on separate lines, and beautiful, readable markdown format.
        - Use LaTeX math macros (e.g., \\equiv, \\pmod{{}}, \\prod, \\sum, \\mathbb{{N}}, \\mathbb{{Z}}).
        - Prefer mathematical notation to plain text where suitable.
        - For Euclidean geometry problems, a complex-number solution is encouraged: you may set the complex plane, assign complex coordinates to points, optionally normalize via a Möbius transform (e.g., send a circumcircle to the unit circle), and finish with algebraic verification.
        - Optionally restate a short bold Claim, start the argument with bold "Proof.", and end with the symbol ∎.
        - Keep the proof concise yet rigorous and self-contained.
        Return ONLY the JSON object and nothing else.
        """
    ).strip()


# System prompt for the judge behavior and output constraints
JUDGE_SYSTEM_PROMPT: str = dedent(
    """
    You are a rigorous mathematical proof judge. Evaluate the provided proof strictly and conservatively.
    You must return a structured JSON object when prompted with response formatting, and otherwise adhere to the user prompt.
    In the textual feedback, enumerate ALL logical flaws you find, each with a concise explanation of why it is a flaw.
    Do not propose fixes. Do not include extraneous commentary beyond the list of flaws. If no flaws are found, state that explicitly.
    Note: For Euclidean geometry problems, complex-number solutions are encouraged but not strictly required; do not penalize otherwise correct solutions solely for using a different method.
    Return ONLY the JSON object with fields correctness (boolean) and feedback (string of the first flaw only). No other text.
    """
).strip()


def build_judge_user_prompt(problem: str, proof_markdown: str) -> str:
    """Construct the user prompt for judging a proof.

    The judge will receive the problem and the proof in Markdown, and must assess correctness
    and return only the first logical flaw explanation in its feedback.
    """
    return dedent(
        f"""
        Task: Assess the correctness of the following proof for the given problem.

        Problem:
        {problem}

        Proof (Markdown):
        {proof_markdown}

        Requirements:
        - Determine correctness as a boolean: true if the proof is fully correct and rigorous, false otherwise.
        - In the textual feedback, list ALL logical flaws you identify, with a brief explanation for each.
        - No fix suggestions. No preface or trailing notes beyond the flaw list. If there are no flaws, say "No flaws found."
        """
    ).strip()


# System prompt for the final judge that selects the least incorrect proof
FINAL_JUDGE_SYSTEM_PROMPT: str = dedent(
    """
    You are a rigorous mathematical proof judge tasked with selecting the least incorrect proof
    among several flawed attempts. You must be conservative and precise.
    You must return a structured JSON object when prompted with response formatting.
    Preference note: If the problem is Euclidean geometry, you may prefer well-structured complex-number solutions, but do not downrank correct solutions solely for method choice.
    Return ONLY the JSON object with field chosen_index (0-based integer). No other text.
    """
).strip()


def build_final_judge_user_prompt(problem: str, proofs: list[str]) -> str:
    """Construct the user prompt for selecting the least incorrect proof among multiple attempts.

    The final judge receives the problem and a list of proofs, and must select the 0-based index
    of the least incorrect one.
    """
    proofs_block = "\n\n".join(f"Proof {i}:\n{p}" for i, p in enumerate(proofs))
    return dedent(
        f"""
        Task: From the following proof attempts for the given problem, select the least incorrect one.

        Problem:
        {problem}

        Proof attempts:
        {proofs_block}

        Requirements:
        - Return ONLY the 0-based index of the chosen proof in the structured JSON field.
        - Choose the proof that is closest to being correct and would require the smallest corrections.
        - Return ONLY the JSON object with field chosen_index (0-based integer). No other text.
        """
    ).strip()


def build_reprove_user_prompt(problem: str, previous_proof_markdown: str, feedback: str) -> str:
    """Build a user prompt to revise the previous proof using the problem, last proof, and feedback.

    The model must output a JSON object with a single field "proof_markdown"
    that contains the updated proof as Markdown, same contract as the original prove call.
    The model should either fix the prior proof according to feedback, or, if that seems
    fundamentally unworkable, produce a fresh proof via a different approach.
    """
    return dedent(
        f"""
        Task: You will receive (1) the problem statement, (2) your previous proof attempt, and (3) reviewer feedback identifying the first flaw.
        First, understand the idea and structure of the existing proof. Then revise the proof to fix the flaw indicated by the feedback.

        Problem:
        {problem}

        Previous proof (Markdown):
        {previous_proof_markdown}

        Reviewer feedback (first flaw only):
        {feedback}

        Requirements:
        - Produce ONLY a JSON object with a single field "proof_markdown" whose value is a self-contained Markdown proof.
        - Begin the proof content immediately from the first character of "proof_markdown".
        - Prefer minimally invasive edits that preserve the original approach when the flaw is local and repairable.
        - If the flaw is fundamental or the approach is unsalvageable, produce a correct proof via a different approach.
        - Use proper LaTeX math formatting (inline $...$, display $$...$$) and standard math macros.
        - If the problem is Euclidean geometry and the prior attempt was not a complex-number proof, DISCARD it and produce a fresh complex-number solution (set the complex plane, possibly normalize via a Möbius transform, and argue purely with complex identities).
        - Do not include any other commentary outside the JSON. Return ONLY the JSON object.
        """
    ).strip()


def build_feedback_only_reprove_prompt(feedback: str) -> str:
    """Build a user prompt that only supplies reviewer feedback and asks to repair the prior proof.

    The model must output a JSON object with a single field "proof_markdown" that contains the
    updated proof as Markdown, preserving the original problem context from the ongoing conversation.
    """
    return dedent(
        f"""
        Task: Repair your previous proof to address the reviewer feedback below. Do not start a new proof; make the minimal set of changes needed so that the flaw is corrected.

        Reviewer feedback (first flaw only):
        {feedback}

        Requirements:
        - Produce ONLY a JSON object with a single field "proof_markdown" whose value is a self-contained Markdown proof for the same problem as before.
        - Begin the proof content immediately from the first character of "proof_markdown".
        - Use proper LaTeX math formatting (inline $...$, display $$...$$) and standard math macros.
        - If the problem is Euclidean geometry and the prior attempt was not a complex-number proof, replace it entirely with a complex-number solution as per the system policy.
        Return ONLY the JSON object. No other text.
        """
    ).strip()


# --- Result refinement prompts ---
RESULT_REFINER_SYSTEM_PROMPT: str = dedent(
    """
    You are a meticulous mathematical editor and logician. You refine a result statement and its proof.
    Your tasks, in order:
    1) Remove any assumptions in the statement that are not actually used in the proof.
    2) If the proof actually disproves the statement, replace the statement with the correct negation (or corrected version),
       and modify the proof so that it proceeds by assuming the contrary (proof by contradiction) and reaches a contradiction.
    3) Remove any textual markers indicating conjectural status from the statement, such as parentheses like "(Conjecture ...)".

    Output strictly a JSON object with fields:
    - "new_statement": string (refined statement after all rules)
    - "new_proof_markdown": string (refined Markdown proof consistent with the new statement)
    - "changed": boolean (true if any change was applied, false otherwise)

    Rules:
    - Keep LaTeX math in Markdown: inline $...$, display $$...$$.
    - Keep the proof self-contained and rigorous.
    - Do not add extraneous commentary; return ONLY the JSON object, no backticks.
    """
).strip()


def build_result_refiner_user_prompt(statement: str, proof_markdown: str) -> str:
    """Build the user prompt for refining a statement and its proof.

    The model must return ONLY a JSON object with fields new_statement, new_proof_markdown, and changed.
    """
    return dedent(
        f"""
        Task: Refine the following statement and its proof.

        Statement:
        {statement}

        Proof (Markdown):
        {proof_markdown}

        Apply the system rules. Return ONLY the JSON object.
        """
    ).strip()


# --- Tightening prompts ---
TIGHTEN_SYSTEM_PROMPT: str = dedent(
    """
    You are a meticulous mathematical editor. You are given a problem statement and a valid proof.
    Your goal is to tighten the statement by removing extraneous or stronger-than-necessary assumptions,
    or by sharpening the claim if the proof supports a stronger conclusion, without invalidating correctness.

    Tasks:
    1) Read the proof to understand which assumptions are actually used and how.
    2) Propose a strictly tightened statement (fewer/weaker assumptions or stronger but still proven conclusion) that the existing proof can be adapted to prove.
    3) Produce the updated proof (Markdown) consistent with the tightened statement.

    Output ONLY a JSON object with fields:
    - "can_tighten": boolean (true if a strictly tighter statement with an adapted proof is possible)
    - "updated_statement": string (the tightened statement; empty if can_tighten=false)
    - "updated_proof": string (the updated proof in Markdown; empty if can_tighten=false)

    Rules:
    - Keep LaTeX math in Markdown: inline $...$, display $$...$$.
    - Maintain rigor; do not weaken correctness. If unsure, set can_tighten=false.
    - Do not include any text outside the JSON object; no backticks.
    """
).strip()


def build_tighten_user_prompt(statement: str, proof_markdown: str) -> str:
    """Build the user prompt for tightening a statement given its proof.

    The model must return ONLY a JSON object with fields can_tighten, updated_statement, updated_proof.
    """
    return dedent(
        f"""
        Task: Read the following statement and its proof, then determine whether you can tighten the statement
        by removing unused assumptions or strengthening the conclusion while keeping the proof valid (possibly with minor adaptations).

        Statement:
        {statement}

        Proof (Markdown):
        {proof_markdown}

        Return ONLY the JSON object with fields can_tighten (boolean), updated_statement (string), updated_proof (Markdown string).
        If you cannot confidently tighten, set can_tighten=false and leave the other fields empty.
        """
    ).strip()

# System prompt for literature extraction behavior and output constraints
EXTRACT_SYSTEM_PROMPT: str = dedent(
    """
    You are an expert mathematical reader and curator. Extract consistent notation, core results,
    and unresolved questions from provided mathematical texts. Be precise, conservative, and avoid speculation.
    You must return a structured JSON object with the following fields:
    - "annotations": Markdown defining shared notation and symbols (use LaTeX math where appropriate)
    - "results": Markdown enumerating only the statements of the key results (theorems, lemmas, corollaries). No proofs.
    - "open_questions": array of strings, each a Markdown description of a genuine unresolved problem after considering all provided works
    """
).strip()


def build_extract_user_prompt(corpus_text: str) -> str:
    """Construct the user prompt for extracting literature context from a blob of text.

    The model is instructed to provide structured content adhering to the schema, with LaTeX math in Markdown.
    """
    return dedent(
        f"""
        Task: From the following mathematical text (which may describe multiple papers/articles), extract:
        1) A concise shared notation section (annotations) in Markdown using LaTeX math.
        2) A list of important results (results) stated cleanly with LaTeX math. Do NOT include proofs.
        3) The set of truly open questions (open_questions) that remain after considering all included works; if a question is solved by any given reference, do not include it.

        Text:
        {corpus_text}

        Requirements:
        - Use clear, consistent notation in "annotations" and follow it exactly in "results".
        - In "results", include only statements, no proof sketches or hints.
        - In "open_questions", include only unresolved problems that survive after cross-referencing the given texts.
        - Use Markdown with LaTeX math ($...$ and $$...$$) throughout where appropriate.
        """
    ).strip()


# --- Research pipeline prompts ---

LIT_REVIEW_SYSTEM_PROMPT: str = dedent(
    """
    You are a meticulous mathematical research assistant.
    Use web search to gather at most 20 highly relevant results closely related to the given seed result.
    Return ONLY a JSON object with fields:
    - "annotations": string. Define unified notation and symbols (Markdown with LaTeX) that you will use in all result statements.
    - "results": array of [result_latex, url] pairs. Each result must be a clean LaTeX statement using the chosen annotations, paired with a reliable source URL.

    Requirements:
    - Include the input seed result itself as the FIRST element in "results" with a source tag; if no URL, use "seed://input".
    - Prefer survey articles, reputable preprints, textbooks, or peer-reviewed sources.
    - Keep statements concise and standardized under your "annotations" section.
    """
).strip()


def build_lit_review_user_prompt(seed_result_latex: str | list[str]) -> str:
    if isinstance(seed_result_latex, list):
        seeds_block = "\n".join([f"- ${{{s}}}$" for s in seed_result_latex])
        header = "Seed results (LaTeX):"
        body = seeds_block
    else:
        header = "Seed result (LaTeX):"
        body = str(seed_result_latex)
    return dedent(
        f"""
        {header}
        {body}

        Task:
        - Define a concise annotations section (symbols, conventions) suitable for these topics.
        - Search and list up to 20 related results. Ensure statements match your annotations exactly.
        - Include each input seed as the first entries in \"results\" with source tag \"seed://input\" if no URL is available.
        - Return ONLY the required JSON object.
        """
    ).strip()


PREDICT_SYSTEM_PROMPT: str = dedent(
    """
    You are a creative but careful mathematical researcher.
    You are given a literature review containing trusted true results and unified annotations.
    Propose likely-new results (conjectures) that plausibly extend or combine the known results.

    Tools available:
    - A local Python scratchpad (run_python) with numpy/scipy for sanity checks or small experiments (do not overfit to data). Use it to test small parameter values, probe edge cases, and quickly search for counterexamples before committing to a conjecture.
    - Web search to proactively vet novelty; you MUST use it before including any conjecture.

    Output ONLY a JSON object with fields:
    - "annotations": string. The (possibly refined) unified notation you will use in your conjectures.
    - "predicted_results": array of LaTeX statements (5-10 items if possible), each self-contained and consistent with the annotations.

    Requirements:
    - Be bold but reasonable: push beyond obvious corollaries with sharp, credible statements that advance the frontier.
    - Aim for non-trivial, substantive conjectures (not simple restatements, direct corollaries, parameter renamings, constant-factor tweaks, or obvious special cases).
    - For EACH candidate, BEFORE including it, call web search with 1–3 targeted queries (use synonyms/alternate phrasings) to check for equal or strictly stronger prior results; include only those without clear matches.
    - Actively use the run_python tool to test small instances and randomized examples when appropriate; discard candidates that quickly fail sanity checks or admit easy counterexamples.
    - Prefer depth and sharpness over count: if fewer than 10 pass novelty, return fewer high-quality items rather than filler.
    - Use conservative, credible extrapolations; avoid wild speculation.
    - Prefer minimality/clean structure (tight hypotheses and sharp conclusions) over breadth.
    - If a Research guideline is provided in the user message, align all conjectures to concretely advance that goal.
    - Do not include any commentary or search traces; return ONLY the JSON object.
    """
).strip()


def build_predict_user_prompt(
    literature_annotations: str,
    literature_results: list[list[str]],
    research_guideline: str | None = None,
) -> str:
    results_md = "\n".join([f"- ${{{stmt}}}$ (source: {url})" for stmt, url in literature_results])
    guideline_block = (
        f"\nResearch guideline (steer all conjectures toward this goal):\n{research_guideline}\n"
        if research_guideline
        else ""
    )
    return dedent(
        f"""
        Literature annotations (trusted):
        {literature_annotations}

        Trusted true results (you may cite without proof):
        {results_md}
        {guideline_block}
        Task:
        - Propose 10–15 plausible, likely-new and non-trivial results consistent with the above.
        - Avoid trivialities: direct corollaries, mere renamings, constant-factor tweaks, or obvious special cases.
        - Be bold but reasonable: prefer sharp, frontier-advancing statements while staying credible under the given context.
        - When a research guideline is provided, prioritize conjectures that measurably push toward that directive.
        - Actively use the run_python tool to test small parameter values and randomized instances for sanity; drop any candidate that quickly fails.
        - Use the web search tool BEFORE including each candidate to verify novelty with 1–3 queries (include synonyms/alternate phrasings); discard any with clear existing matches or strictly stronger prior results.
        - Prefer fewer high-quality items over filler if needed.
        - Return ONLY the required JSON object.
        """
    ).strip()


def build_proof_user_prompt_with_context(statement: str, literature_annotations: str, literature_results: list[list[str]]) -> str:
    lemmas_md = "\n".join([f"- ${{{stmt}}}$ (source: {url})" for stmt, url in literature_results])
    base = build_proof_user_prompt(statement)
    extra = dedent(
        f"""

        Context you may use without proof:
        - Unified annotations:
        {literature_annotations}
        - Allowed lemmas/results (cite as needed):
        {lemmas_md}
        """
    ).strip()
    return base + "\n\n" + extra


def build_judge_user_prompt_with_context(problem: str, proof_markdown: str, literature_annotations: str, literature_results: list[list[str]]) -> str:
    lemmas_md = "\n".join([f"- ${{{stmt}}}$ (source: {url})" for stmt, url in literature_results])
    base = build_judge_user_prompt(problem, proof_markdown)
    extra = dedent(
        f"""

        Judge policy additions:
        - The solver may use the following as trusted lemmas without proof; do NOT flag their usage as gaps:
        {lemmas_md}
        - Notation/annotations to interpret statements:
        {literature_annotations}
        """
    ).strip()
    return base + "\n\n" + extra


# --- Final report generation ---
FINAL_REPORT_SYSTEM_PROMPT: str = dedent(
    """
    You are a careful mathematical editor. You will be given:
    - A literature context (annotations and key results) that sets notation and references.
    - A list of new results paired with corresponding proofs produced by an automated prover.

    Your task: compile a beautiful, consistent Markdown report using KaTeX-compatible LaTeX.
    Requirements (beauty and structure):
    - Begin with a concise Preface (2–3 sentences) summarizing the theme and contributions.
    - Provide a clear table of contents linking to each main section.
    - Include a section "Annotations" with unified notation (lightly edit for clarity/consistency only).
    - For each new result, create a subsection with a short LaTeX-stated theorem/lemma title, followed by a clearly formatted proof starting with bold "Proof." and ending with the symbol ∎.
    - Prefer informative headings like "Theorem 1 (Title)" and "Lemma 2 (Title)".
    - Keep the report self-contained, logically ordered, and visually clean with short paragraphs and proper spacing.

    KaTeX safety (avoid parsing errors):
    - Use only KaTeX-safe constructs: inline math $...$; display math $$...$$ on its own lines.
    - Avoid environments and macros not guaranteed in KaTeX: do NOT use \begin{equation}, \begin{align}, \eqref, \label, \ref, \tag, \newcommand, \def, \require{}.
    - Prefer simple alignment within display math using \\\\ for line breaks; avoid alignment points like & unless strictly necessary.
    - Use standard macros only (\\mathbb{}, \\mathrm{}, \\operatorname{}). Avoid exotic packages and non-ASCII symbols.
    - Ensure all braces (), [], {} are balanced; escape underscores in text (write \_ in plain text if needed).
    - Do NOT include triple backticks anywhere in the output.

    Output constraints:
    - Return only a JSON object with a single field "report_markdown" that contains the complete Markdown report body.
    - Do not include code fences, backticks, or any text outside the JSON object.
    """
).strip()


def build_final_report_user_prompt(
    literature_annotations: str,
    literature_results: list[list[str]],
    compiled_results: list[tuple[str, str]],
) -> str:
    """Build the user prompt to compile the final report.

    - literature_results: [(result_latex, url)]
    - compiled_results: [(new_result_latex, proof_markdown)]
    """
    lit_md = "\n".join([f"- ${{{stmt}}}$ (source: {url})" for stmt, url in literature_results])
    new_md = "\n\n".join([f"Result:\n${{{stmt}}}$\n\nProof (Markdown):\n{proof}" for stmt, proof in compiled_results])
    return dedent(
        f"""
        Literature annotations (trusted):
        {literature_annotations}

        Trusted results you may cite (no proofs required):
        {lit_md}

        New results and their proofs to be compiled:
        {new_md}

        Produce a beautifully structured report as per the system rules with:
        - A Preface, a Table of Contents, an Annotations section, a Trusted Results section (with URLs), and one subsection per new result with a bold "Proof." and closing ∎.
        - Use only KaTeX-safe math as specified; avoid unsupported environments/macros and backticks.
        Return ONLY the JSON with "report_markdown" and nothing else.
        """
    ).strip()


# --- Novelty checker ---
NOVELTY_SYSTEM_PROMPT: str = dedent(
    """
    You are a meticulous mathematical novelty reviewer. Given a predicted result (LaTeX) and shared annotations,
    use web search to determine whether the result (or a strictly stronger version) already exists in the literature.

    Decision policy:
    - If you find the same statement (up to renaming/obvious equivalences) or a strictly stronger theorem covering it, return is_novel=false.
    - If you only find weaker/special cases, survey notes without proof, or no convincing match, return is_novel=true.
    - Be conservative: if clear strong evidence of prior existence is found, mark as not novel.

    Return ONLY a JSON object with fields:
    - "is_novel": boolean
    - "matched_statement": string (if is_novel=false; else empty)
    - "matched_url": string (if is_novel=false; else empty)
    """
).strip()


def build_novelty_user_prompt(literature_annotations: str, predicted_result_latex: str) -> str:
    return dedent(
        f"""
        Annotations (notation to interpret the statement):
        {literature_annotations}

        Predicted result (LaTeX):
        {predicted_result_latex}

        Use web search to check for existing equal/stronger results. Return ONLY the JSON object with fields
        is_novel (boolean), matched_statement (string if not novel else empty), matched_url (string if not novel else empty).
        """
    ).strip()