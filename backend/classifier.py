from typing import Optional, List, Dict, Any


from .prompts import GEOMETRY_DETECT_SYSTEM_PROMPT, build_geometry_detect_user_prompt
from .output_schemas import GeometryDetection
from .llm_provider import generate_structured


class GeometryClassifier:
    """LLM-backed classifier to detect Euclidean plane geometry problems.

    Uses gpt-5-mini with medium reasoning effort by default.
    """

    def __init__(self, model: str = "gpt-5-mini", reasoning_effort: str = "medium", timeout: float = 180.0) -> None:
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.timeout = timeout

    def classify(
        self,
        problem: str,
        *,
        model: Optional[str] = None,
        reasoning_effort: Optional[str] = None,
    ) -> GeometryDetection:
        """Return structured classification for the given problem."""
        selected_model = model or self.model
        selected_effort = reasoning_effort or self.reasoning_effort

        transcript: List[Dict[str, Any]] = [
            {"role": "system", "content": GEOMETRY_DETECT_SYSTEM_PROMPT},
            {"role": "user", "content": build_geometry_detect_user_prompt(problem)},
        ]

        resp = generate_structured(
            messages=transcript,
            response_model=GeometryDetection,
            model=selected_model,
            reasoning_effort=selected_effort,
            timeout=self.timeout,
        )

        return resp.output_parsed

    def is_euclidean_geometry(
        self,
        problem: str,
        *,
        model: Optional[str] = None,
        reasoning_effort: Optional[str] = None,
    ) -> bool:
        return self.classify(problem, model=model, reasoning_effort=reasoning_effort).is_euclidean_geometry


