"""HTTP application factory with liveness/readiness separation."""

import logging
import time
import uuid
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from starlette.responses import Response

from risk_ml.api.schemas import (
    BatchRequest,
    BatchResponse,
    CreditApplication,
    ExplanationResponse,
    Prediction,
)
from risk_ml.config import Settings, get_settings
from risk_ml.logging import configure_logging
from risk_ml.services.scoring import ScoringService

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None, service: ScoringService | None = None) -> FastAPI:
    """Create an isolated app, allowing test injection without global model reloads."""

    config = settings or get_settings()
    configure_logging(config.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
        app.state.service = service
        app.state.load_error = None
        if app.state.service is None:
            try:
                app.state.service = ScoringService(config.model_path)
            except Exception as exc:  # readiness exposes category, logs contain no input
                app.state.load_error = type(exc).__name__
                logger.error("model_load_failed", extra={"error_type": type(exc).__name__})
        yield

    app = FastAPI(title="RiskML API", version="0.1.0", lifespan=lifespan)

    @app.middleware("http")
    async def correlation_middleware(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        correlation_id = request.headers.get("x-correlation-id", str(uuid.uuid4()))[:128]
        started = time.perf_counter()
        response = await call_next(request)
        response.headers["x-correlation-id"] = correlation_id
        logger.info(
            "request_completed",
            extra={"correlation_id": correlation_id},
        )
        response.headers["server-timing"] = f"app;dur={(time.perf_counter() - started) * 1000:.1f}"
        return response

    def ready_service(request: Request) -> ScoringService:
        active: ScoringService | None = request.app.state.service
        if active is None:
            raise HTTPException(status_code=503, detail="model is not ready")
        return active

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "alive"}

    @app.get("/ready")
    def ready(request: Request) -> dict[str, str]:
        active = ready_service(request)
        return {"status": "ready", "model_version": active.model_version}

    @app.post("/api/v1/predict", response_model=Prediction)
    def predict(application: CreditApplication, request: Request) -> dict[str, Any]:
        return ready_service(request).predict([application.model_dump()])[0]

    @app.post("/api/v1/predict/batch", response_model=BatchResponse)
    def predict_batch(payload: BatchRequest, request: Request) -> dict[str, Any]:
        if not payload.records or len(payload.records) > config.max_batch_size:
            raise HTTPException(
                status_code=422, detail=f"batch size must be between 1 and {config.max_batch_size}"
            )
        records = [record.model_dump() for record in payload.records]
        return {"predictions": ready_service(request).predict(records)}

    @app.post("/api/v1/explain", response_model=ExplanationResponse)
    def explain(application: CreditApplication, request: Request) -> dict[str, Any]:
        active = ready_service(request)
        try:
            explanation = active.explain(application.model_dump())
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return {
            "base_value": explanation.base_value,
            "contributions": [item.__dict__ for item in explanation.contributions],
            "note": explanation.note,
            "model_version": active.model_version,
        }

    return app
