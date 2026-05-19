import os
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.db.database import engine
from app.db import init_db
from app.api.resume_routes import router as resume_router
from app.api.auth_routes import router as auth_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("resume-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db.init_db()
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(title="Resume Optimizer API", version="1.0.0", lifespan=lifespan)

    allowed_origins = os.getenv("CORS_ALLOW_ORIGINS", "").split(",")
    allowed_origins = [o.strip() for o in allowed_origins if o.strip()]
    if not allowed_origins:
        allowed_origins = ["http://localhost:5173", "http://localhost:3000"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration:.2f}s)")
        return response

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled error on {request.method} {request.url.path}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "服务器内部错误，请稍后重试"},
        )

    @app.get("/api/health")
    async def health_check():
        return {"status": "ok", "version": "1.0.0"}

    app.include_router(auth_router, prefix="/api")
    app.include_router(resume_router, prefix="/api")
    return app


app = create_app()
