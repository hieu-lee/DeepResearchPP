from __future__ import annotations

from typing import List, Union, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import logging
from pydantic import BaseModel

from .cli import run_automate_math_research, _parse_seed_content


class ReportRequest(BaseModel):
    seeds: Union[str, List[str]]
    research_guideline: Optional[str] = None
    model: str = "gpt-5"


class ReportResponse(BaseModel):
    report_markdown: str


logger = logging.getLogger("backend.api")

router = APIRouter()


@router.post("/report", response_model=ReportResponse)
def generate_report(req: ReportRequest) -> ReportResponse:
    try:
        logger.info("/report: received request (model=%s) with seeds length=%s, guideline=%s", req.model, (len(req.seeds) if isinstance(req.seeds, list) else len(req.seeds or "")), bool(req.research_guideline))
        # Normalize seeds to match CLI behavior (accept raw string or bracketed multi-seed text)
        normalized_seeds: Union[str, List[str]]
        if isinstance(req.seeds, str):
            normalized_seeds = _parse_seed_content(req.seeds)
        else:
            normalized_seeds = req.seeds

        logger.info("/report: normalized seeds -> %s item(s)", (1 if isinstance(normalized_seeds, str) else len(normalized_seeds)))
        _results, report_markdown = run_automate_math_research(
            seed_result=normalized_seeds,
            model=req.model,
            research_guideline=req.research_guideline,
        )
        logger.info("/report: completed report generation (length=%d)", len(report_markdown or ""))
        return ReportResponse(report_markdown=report_markdown)
    except Exception as e:  # pragma: no cover
        logger.exception("/report: failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {type(e).__name__}: {e}")


@router.post("/report/stream")
def generate_report_stream(req: ReportRequest) -> StreamingResponse:
    import json, time

    def _iter():
        try:
            logger.info("/report/stream: start")
            seeds = _parse_seed_content(req.seeds) if isinstance(req.seeds, str) else req.seeds
            yield json.dumps({"phase": "start", "model": req.model}) + "\n"
            from .research import ResearchPipeline, ResearchConfig
            from .cli import _append_correct_result_json  # reuse util if desired
            cfg = ResearchConfig(
                lit_model=req.model,
                predict_model=req.model,
                prove_model=req.model,
                reporter_model=(req.model or "gpt-5-mini"),
                novelty_model=req.model,
                research_guideline=req.research_guideline,
            )
            pipe = ResearchPipeline(cfg)
            yield json.dumps({"phase": "literature_review", "status": "begin"}) + "\n"
            lit = pipe.literature_review(seeds)
            yield json.dumps({"phase": "literature_review", "status": "done", "count": len(lit.results)}) + "\n"

            yield json.dumps({"phase": "prediction", "status": "begin"}) + "\n"
            preds = pipe.predict(lit)
            pred_list = list(getattr(preds, "predicted_results", []) or [])
            pred_count = len(pred_list)
            yield json.dumps({"phase": "prediction", "status": "done", "count": pred_count, "predictions": pred_list}) + "\n"

            yield json.dumps({"phase": "novelty", "status": "begin"}) + "\n"
            kept = pipe.novelty_filter(lit, preds)
            yield json.dumps({"phase": "novelty", "status": "done", "kept": len(kept), "total": pred_count, "statements": kept}) + "\n"

            # Prove and refine/tighten inline with progress updates
            from concurrent.futures import ThreadPoolExecutor, as_completed
            yield json.dumps({"phase": "proving", "status": "begin", "candidates": len(kept)}) + "\n"
            results: list[tuple[str, str]] = []
            def _prove_one(s: str):
                from .solver import Solver
                sol = Solver(model=req.model)
                return s, sol.solve(s, 8, lit)
            with ThreadPoolExecutor(max_workers=12) as ex:
                futs = {ex.submit(_prove_one, s): s for s in kept}
                for fut in as_completed(futs):
                    stmt, (ok, payload) = fut.result()
                    if not ok:
                        yield json.dumps({"phase": "proving", "status": "failed", "statement": stmt}) + "\n"
                        continue
                    yield json.dumps({"phase": "proving", "status": "proved", "statement": stmt}) + "\n"
                    # Refine/tighten/judge sequentially here but per-item (already parallel per future)
                    from .result_refiner import ResultRefiner
                    from .judge import Judge
                    ref = ResultRefiner(model=req.model, reasoning_effort="medium")
                    try:
                        r = ref.refine(stmt, payload)
                    except Exception:
                        r = None
                    if r is not None:
                        base_stmt, base_proof = r
                    else:
                        base_stmt, base_proof = stmt, payload
                    try:
                        t = ref.tighten(base_stmt, base_proof)
                        if t is not None:
                            t_stmt, t_proof = t
                            j = Judge(model=req.model)
                            jres = j.assess(t_stmt, t_proof)
                            if jres.correctness:
                                results.append((t_stmt, t_proof))
                                yield json.dumps({"phase": "proving", "status": "accepted", "tightened": True, "statement": t_stmt}) + "\n"
                                # Second independent judge confirmation
                                try:
                                    j2 = Judge(model=req.model)
                                    j2res = j2.assess(t_stmt, t_proof)
                                    if j2res.correctness:
                                        yield json.dumps({"phase": "proving", "status": "accepted_both", "statement": t_stmt}) + "\n"
                                except Exception:
                                    pass
                                continue
                    except Exception:
                        pass
                    results.append((base_stmt, base_proof))
                    yield json.dumps({"phase": "proving", "status": "accepted", "tightened": False, "statement": base_stmt}) + "\n"
                    # Second independent judge confirmation
                    try:
                        j2 = Judge(model=req.model)
                        j2res = j2.assess(base_stmt, base_proof)
                        if j2res.correctness:
                            yield json.dumps({"phase": "proving", "status": "accepted_both", "statement": base_stmt}) + "\n"
                    except Exception:
                        pass

            yield json.dumps({"phase": "report", "status": "begin", "count": len(results)}) + "\n"
            report = pipe.compile_final_report(lit, results)
            yield json.dumps({"phase": "report", "status": "done"}) + "\n"
            yield json.dumps({"phase": "complete", "report_markdown": report.report_markdown}) + "\n"
        except Exception as e:
            yield json.dumps({"phase": "error", "error": f"{type(e).__name__}: {e}"}) + "\n"

    return StreamingResponse(_iter(), media_type="application/x-ndjson")


