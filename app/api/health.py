"""
Health check endpoints for Kubernetes.
"""

from fastapi import APIRouter, status
from fastapi.responses import PlainTextResponse
from pyfiglet import figlet_format
from core.config import settings
from core.redis_client import redis_client
from loguru import logger


router = APIRouter(tags=["health"])


def generate_ascii_status(text: str) -> str:
    # ascii art for status messages - makes logs more fun
    return figlet_format(text, font="slant")


@router.get(
    "/health/live",
    response_class=PlainTextResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness check",
)
async def liveness():
    # basic liveness check
    logger.debug("Liveness check called")
    ascii_art = generate_ascii_status("ALIVE")
    return f"{ascii_art}App: {settings.app_name}\nVersion: {settings.app_version}"


@router.get("/health/ready", response_class=PlainTextResponse, summary="Readiness check")
async def readiness():
    # readiness check to verify dependencies are working
    logger.debug("Readiness check called")

    redis_status = "disabled"
    is_ready = True

    # check redis if it's enabled
    if settings.redis_enabled:
        if redis_client.is_connected():
            redis_status = "connected"
        else:
            redis_status = "disconnected"
            is_ready = False
            logger.warning("Readiness check failed: Redis not connected")

    status_text = "READY" if is_ready else "NOT READY"
    ascii_art = generate_ascii_status(status_text)
    response_text = (
        f"{ascii_art}"
        f"App: {settings.app_name}\n"
        f"Version: {settings.app_version}\n"
        f"Environment: {settings.environment}\n"
        f"Redis: {redis_status}"
    )

    # return 503 if not ready
    response_status = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE

    return PlainTextResponse(content=response_text, status_code=response_status)


@router.get(
    "/health/startup",
    response_class=PlainTextResponse,
    status_code=status.HTTP_200_OK,
    summary="Startup check",
)
async def startup():
    # startup probe - just confirms we've started up
    logger.debug("Startup check called")
    ascii_art = generate_ascii_status("STARTED")
    return f"{ascii_art}App: {settings.app_name}\nVersion: {settings.app_version}"
