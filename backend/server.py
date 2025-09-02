from __future__ import annotations

import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .api import router as api_router
import logging
import time
from contextlib import asynccontextmanager


logger = logging.getLogger("backend")


def _configure_logging() -> None:
    # Configure a simple root logger if not already configured by the runner
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        )
    logger.setLevel(logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[override]
    logger.info("API startup complete")
    yield
    logger.info("API shutdown complete")


def create_app() -> FastAPI:
    _configure_logging()
    app = FastAPI(title="Research Report API", version="1.0.0", lifespan=lifespan)
    # Simple permissive CORS; adjust as needed by deployment
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    @app.middleware("http")
    async def log_requests(request: Request, call_next):  # type: ignore[override]
        start = time.perf_counter()
        logger.info("-> %s %s", request.method, request.url.path)
        try:
            response = await call_next(request)
        except Exception as e:  # pragma: no cover
            dur_ms = (time.perf_counter() - start) * 1000.0
            logger.exception("!! %s %s failed in %.1f ms: %s", request.method, request.url.path, dur_ms, e)
            raise
        dur_ms = (time.perf_counter() - start) * 1000.0
        logger.info("<- %s %s %s in %.1f ms", request.method, request.url.path, getattr(response, "status_code", "-"), dur_ms)
        return response

    app.include_router(api_router)
    return app


app = create_app()


if __name__ == "__main__":  # pragma: no cover
    # Run with: python -m backend.server or uvicorn backend.server:app --reload
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("backend.server:app", host=host, port=port, reload=True)


