"""
Handles startup/shutdown lifecycle and routes.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from loguru import logger

from core.config import settings
from core.logging import setup_logging
from core.redis_client import redis_client
from core.ssm_client import ssm_client
from api import health
from api.v1 import router as v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # setup logging first, obviously
    setup_logging()
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")

    # connect to redis if we're using it
    if settings.redis_enabled:
        redis_client.connect()

    # same for ssm
    if settings.ssm_enabled:
        ssm_client.connect()

    yield

    # cleanup when shutting down
    logger.info("Shutting down application")
    if settings.redis_enabled:
        redis_client.disconnect()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Feature Flag Service with Redis caching and AWS SSM Parameter Store",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# wire up the routes
app.include_router(health.router)
app.include_router(v1_router)


@app.get("/", include_in_schema=False)
async def root():
    # just redirect to docs
    return RedirectResponse(url="/docs")
