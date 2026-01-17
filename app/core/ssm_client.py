"""
AWS SSM Parameter Store client.
Handles parameter storage and retrieval.
"""

import boto3
from typing import Optional, Dict, Any
from loguru import logger
from core.config import settings


class SSMClient:
    def __init__(self):
        self._client: Optional[Any] = None
        self._enabled: bool = settings.ssm_enabled

    def connect(self) -> bool:
        if not self._enabled:
            logger.info("SSM is disabled")
            return False

        try:
            self._client = boto3.client("ssm", region_name=settings.aws_region)
            self._client.describe_parameters(MaxResults=1)
            logger.info(f"Connected to SSM in region {settings.aws_region}")
            return True
        except Exception as e:
            logger.warning(f"Failed to connect to SSM: {e}")
            self._client = None
            return False

    def get_parameter(self, name: str, decrypt: bool = False) -> Optional[str]:
        if not self._client:
            return None

        try:
            full_name = f"{settings.ssm_prefix}/{name}"
            response = self._client.get_parameter(Name=full_name, WithDecryption=decrypt)
            return response["Parameter"]["Value"]
        except self._client.exceptions.ParameterNotFound:
            logger.debug(f"Parameter not found: {name}")
            return None
        except Exception as e:
            logger.error(f"Error getting parameter {name}: {e}")
            return None

    def put_parameter(
        self, name: str, value: str, description: str = "", overwrite: bool = True
    ) -> bool:
        if not self._client:
            return False

        try:
            full_name = f"{settings.ssm_prefix}/{name}"
            self._client.put_parameter(
                Name=full_name,
                Value=value,
                Type="String",
                Description=description,
                Overwrite=overwrite,
            )
            logger.info(f"Parameter saved: {name}")
            return True
        except Exception as e:
            logger.error(f"Error saving parameter {name}: {e}")
            return False

    def delete_parameter(self, name: str) -> bool:
        if not self._client:
            return False

        try:
            full_name = f"{settings.ssm_prefix}/{name}"
            self._client.delete_parameter(Name=full_name)
            logger.info(f"Parameter deleted: {name}")
            return True
        except self._client.exceptions.ParameterNotFound:
            logger.debug(f"Parameter not found for deletion: {name}")
            return False
        except Exception as e:
            logger.error(f"Error deleting parameter {name}: {e}")
            return False

    def list_parameters(self, prefix: str = "") -> Dict[str, str]:
        if not self._client:
            return {}

        try:
            search_prefix = f"{settings.ssm_prefix}/{prefix}" if prefix else settings.ssm_prefix
            paginator = self._client.get_paginator("get_parameters_by_path")

            parameters = {}
            for page in paginator.paginate(Path=search_prefix, Recursive=True):
                for param in page.get("Parameters", []):
                    key = param["Name"].replace(f"{settings.ssm_prefix}/", "")
                    parameters[key] = param["Value"]

            return parameters
        except Exception as e:
            logger.error(f"Error listing parameters: {e}")
            return {}

    def is_enabled(self) -> bool:
        return self._enabled and self._client is not None


ssm_client = SSMClient()
