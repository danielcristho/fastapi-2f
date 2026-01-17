"""
General API endpoints.
Utility routes.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from core.config import settings
from core.redis_client import redis_client
from loguru import logger


router = APIRouter()


class PingResponse(BaseModel):
    message: str
    version: str


class InfoResponse(BaseModel):
    app_name: str
    version: str
    environment: str
    redis_enabled: bool
    redis_connected: bool


@router.get("/ping", response_model=PingResponse)
async def ping():
    logger.debug("Ping endpoint called")
    return PingResponse(message="pong", version=settings.app_version)


@router.get("/info", response_model=InfoResponse)
async def info():
    logger.debug("Info endpoint called")

    redis_connected = False
    if settings.redis_enabled:
        redis_connected = redis_client.is_connected()

    return InfoResponse(
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        redis_enabled=settings.redis_enabled,
        redis_connected=redis_connected,
    )


@router.get("/cache/test")
async def test_cache():
    logger.debug("Cache test endpoint called")

    if not settings.redis_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Redis is not enabled"
        )

    client = redis_client.get_client()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Redis is not connected"
        )

    try:
        test_key = "test:connection"
        test_value = "ok"
        client.set(test_key, test_value, ex=60)
        retrieved_value = client.get(test_key)

        if retrieved_value == test_value:
            logger.info("Redis cache test successful")
            return {
                "status": "success",
                "message": "Redis is working correctly",
                "test_key": test_key,
                "test_value": test_value,
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Redis test failed: value mismatch",
            )
    except Exception as e:
        logger.error(f"Redis cache test failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Redis operation failed: {str(e)}",
        )
