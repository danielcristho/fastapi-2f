"""
Configuration settings using Pydantic.
Environment-based with sensible defaults.
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Literal


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", case_sensitive=False)
    
    # basic app stuff
    app_name: str = "fastapi-eks"
    app_version: str = "1.0.0"
    environment: Literal["development", "staging", "production"] = "development"

    # server config
    host: str = "0.0.0.0"
    port: int = 8000

    # redis settings - disabled by default
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None
    redis_enabled: bool = False

    # aws stuff - also disabled by default
    aws_region: str = "us-east-1"
    ssm_enabled: bool = False
    ssm_prefix: str = "/feature-flags"

    # how long to cache flags in redis == 5 minutes
    feature_flag_cache_ttl: int = 300

    # logging level
    log_level: str = "INFO"


# global settings instance
settings = Settings()
