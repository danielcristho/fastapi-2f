"""
Redis client wrapper
Handles connection, disconnection, and basic health checks
Gracefully fails if redis isn't available
"""

import redis
from typing import Optional
from loguru import logger
from core.config import settings


class RedisClient:
    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._connected: bool = False

    def connect(self) -> bool:
        # don't even try if redis is disabled
        if not settings.redis_enabled:
            logger.info("Redis is disabled")
            return False

        try:
            self._client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            # test the connection
            self._client.ping()
            self._connected = True
            logger.info(f"Connected to Redis at {settings.redis_host}:{settings.redis_port}")
            return True
        except redis.ConnectionError as e:
            # this is expected if redis isn't running
            logger.warning(f"Failed to connect to Redis: {e}")
            self._connected = False
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to Redis: {e}")
            self._connected = False
            return False

    def disconnect(self):
        if self._client:
            try:
                self._client.close()
                logger.info("Disconnected from Redis")
            except Exception as e:
                logger.error(f"Error disconnecting from Redis: {e}")
            finally:
                self._connected = False
                self._client = None

    def is_connected(self) -> bool:
        if not self._connected or not self._client:
            return False

        try:
            self._client.ping()
            return True
        except Exception:
            # connection died, mark as disconnected
            self._connected = False
            return False

    def get_client(self) -> Optional[redis.Redis]:
        # only return client if we're actually connected
        return self._client if self._connected else None


# global redis client instance
redis_client = RedisClient()
