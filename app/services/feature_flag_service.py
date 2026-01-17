"""
Feature flag servic, main logic.
Handles caching with Redis and persistence with SSM.
"""

import json
import hashlib
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from loguru import logger

from core.redis_client import redis_client
from core.ssm_client import ssm_client
from core.config import settings
from models.feature_flag import (
    FeatureFlag,
    FeatureFlagCreate,
    FeatureFlagUpdate,
    FeatureFlagEvaluationResult,
    RolloutStrategy,
)


class FeatureFlagService:
    def __init__(self):
        self.cache_ttl = settings.feature_flag_cache_ttl

    def _get_cache_key(self, flag_key: str) -> str:
        return f"feature_flag:{flag_key}"

    def _get_from_cache(self, flag_key: str) -> Optional[FeatureFlag]:
        client = redis_client.get_client()
        if not client:
            return None

        try:
            cache_key = self._get_cache_key(flag_key)
            data = client.get(cache_key)
            if data:
                logger.debug(f"Cache hit for flag: {flag_key}")
                return FeatureFlag.model_validate_json(data)
        except Exception as e:
            logger.error(f"Cache read error: {e}")

        return None

    def _set_to_cache(self, flag: FeatureFlag) -> bool:
        client = redis_client.get_client()
        if not client:
            return False

        try:
            cache_key = self._get_cache_key(flag.key)
            client.setex(cache_key, self.cache_ttl, flag.model_dump_json())
            logger.debug(f"Cached flag: {flag.key}")
            return True
        except Exception as e:
            logger.error(f"Cache write error: {e}")
            return False

    def _invalidate_cache(self, flag_key: str) -> bool:
        client = redis_client.get_client()
        if not client:
            return False

        try:
            cache_key = self._get_cache_key(flag_key)
            client.delete(cache_key)
            logger.debug(f"Invalidated cache for flag: {flag_key}")
            return True
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
            return False

    def _get_from_ssm(self, flag_key: str) -> Optional[FeatureFlag]:
        if not ssm_client.is_enabled():
            return None

        try:
            data = ssm_client.get_parameter(flag_key)
            if data:
                logger.debug(f"SSM hit for flag: {flag_key}")
                flag_dict = json.loads(data)
                return FeatureFlag(**flag_dict)
        except Exception as e:
            logger.error(f"SSM read error: {e}")

        return None

    def _save_to_ssm(self, flag: FeatureFlag) -> bool:
        if not ssm_client.is_enabled():
            return False

        try:
            flag_dict = flag.model_dump(mode="json")
            data = json.dumps(flag_dict)
            description = flag.description or f"Feature flag: {flag.key}"
            return ssm_client.put_parameter(flag.key, data, description)
        except Exception as e:
            logger.error(f"SSM write error: {e}")
            return False

    def _delete_from_ssm(self, flag_key: str) -> bool:
        if not ssm_client.is_enabled():
            return False

        return ssm_client.delete_parameter(flag_key)

    def create_flag(self, flag_data: FeatureFlagCreate) -> FeatureFlag:
        existing = self.get_flag(flag_data.key)
        if existing:
            raise ValueError(f"Feature flag '{flag_data.key}' already exists")

        now = datetime.now(timezone.utc)
        flag = FeatureFlag(**flag_data.model_dump(), created_at=now, updated_at=now)

        self._save_to_ssm(flag)
        self._set_to_cache(flag)

        logger.info(f"Created feature flag: {flag.key}")
        return flag

    def get_flag(self, flag_key: str) -> Optional[FeatureFlag]:
        flag = self._get_from_cache(flag_key)
        if flag:
            return flag

        flag = self._get_from_ssm(flag_key)
        if flag:
            self._set_to_cache(flag)
            return flag

        return None

    def update_flag(self, flag_key: str, update_data: FeatureFlagUpdate) -> Optional[FeatureFlag]:
        flag = self.get_flag(flag_key)
        if not flag:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(flag, key, value)

        flag.updated_at = datetime.now(timezone.utc)

        self._save_to_ssm(flag)
        self._invalidate_cache(flag_key)

        logger.info(f"Updated feature flag: {flag_key}")
        return flag

    def delete_flag(self, flag_key: str) -> bool:
        flag = self.get_flag(flag_key)
        if not flag:
            return False

        self._delete_from_ssm(flag_key)
        self._invalidate_cache(flag_key)

        logger.info(f"Deleted feature flag: {flag_key}")
        return True

    def list_flags(self) -> List[FeatureFlag]:
        if not ssm_client.is_enabled():
            return []

        try:
            params = ssm_client.list_parameters()
            flags = []
            for key, value in params.items():
                try:
                    flag_dict = json.loads(value)
                    flags.append(FeatureFlag(**flag_dict))
                except Exception as e:
                    logger.error(f"Error parsing flag {key}: {e}")

            return flags
        except Exception as e:
            logger.error(f"Error listing flags: {e}")
            return []

    def evaluate_flag(
        self, flag_key: str, user_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None
    ) -> FeatureFlagEvaluationResult:
        flag = self.get_flag(flag_key)

        if not flag:
            return FeatureFlagEvaluationResult(
                key=flag_key, enabled=False, matched_rule="not_found", source="none"
            )

        if not flag.enabled:
            return FeatureFlagEvaluationResult(
                key=flag_key,
                enabled=False,
                matched_rule="disabled",
                source="cache" if self._get_from_cache(flag_key) else "ssm",
            )

        rules = flag.rules
        source = "cache" if self._get_from_cache(flag_key) else "ssm"

        if rules.strategy == RolloutStrategy.ALL:
            return FeatureFlagEvaluationResult(
                key=flag_key, enabled=True, matched_rule="all", source=source
            )

        if rules.strategy == RolloutStrategy.USER_LIST:
            if user_id and rules.user_ids and user_id in rules.user_ids:
                return FeatureFlagEvaluationResult(
                    key=flag_key, enabled=True, matched_rule="user_list", source=source
                )
            return FeatureFlagEvaluationResult(
                key=flag_key, enabled=False, matched_rule="user_not_in_list", source=source
            )

        if rules.strategy == RolloutStrategy.PERCENTAGE:
            if rules.percentage is not None and user_id:
                hash_value = int(hashlib.md5(f"{flag_key}:{user_id}".encode()).hexdigest(), 16)
                user_percentage = hash_value % 100

                if user_percentage < rules.percentage:
                    return FeatureFlagEvaluationResult(
                        key=flag_key,
                        enabled=True,
                        matched_rule=f"percentage_{rules.percentage}",
                        source=source,
                    )

            return FeatureFlagEvaluationResult(
                key=flag_key, enabled=False, matched_rule="percentage_not_matched", source=source
            )

        return FeatureFlagEvaluationResult(
            key=flag_key, enabled=False, matched_rule="no_rule_matched", source=source
        )


feature_flag_service = FeatureFlagService()
