"""
Feature flag API endpoints.
CRUD operations and flag evaluation.
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from loguru import logger

from models.feature_flag import (
    FeatureFlag,
    FeatureFlagCreate,
    FeatureFlagUpdate,
    FeatureFlagEvaluation,
    FeatureFlagEvaluationResult,
)
from services.feature_flag_service import feature_flag_service


router = APIRouter(prefix="/flags", tags=["feature-flags"])


@router.post("", response_model=FeatureFlag, status_code=status.HTTP_201_CREATED)
async def create_feature_flag(flag_data: FeatureFlagCreate):
    try:
        flag = feature_flag_service.create_flag(flag_data)
        return flag
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating flag: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create feature flag",
        )


@router.get("", response_model=List[FeatureFlag])
async def list_feature_flags():
    try:
        flags = feature_flag_service.list_flags()
        return flags
    except Exception as e:
        logger.error(f"Error listing flags: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list feature flags"
        )


@router.get("/{flag_key}", response_model=FeatureFlag)
async def get_feature_flag(flag_key: str):
    flag = feature_flag_service.get_flag(flag_key)
    if not flag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Feature flag '{flag_key}' not found"
        )
    return flag


@router.put("/{flag_key}", response_model=FeatureFlag)
async def update_feature_flag(flag_key: str, update_data: FeatureFlagUpdate):
    try:
        flag = feature_flag_service.update_flag(flag_key, update_data)
        if not flag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Feature flag '{flag_key}' not found"
            )
        return flag
    except Exception as e:
        logger.error(f"Error updating flag: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update feature flag",
        )


@router.delete("/{flag_key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feature_flag(flag_key: str):
    try:
        success = feature_flag_service.delete_flag(flag_key)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Feature flag '{flag_key}' not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting flag: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete feature flag",
        )


@router.post("/evaluate", response_model=FeatureFlagEvaluationResult)
async def evaluate_feature_flag(evaluation: FeatureFlagEvaluation):
    try:
        result = feature_flag_service.evaluate_flag(
            flag_key=evaluation.key, user_id=evaluation.user_id, context=evaluation.context
        )
        return result
    except Exception as e:
        logger.error(f"Error evaluating flag: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to evaluate feature flag",
        )


@router.get("/{flag_key}/evaluate", response_model=FeatureFlagEvaluationResult)
async def evaluate_feature_flag_get(flag_key: str, user_id: Optional[str] = Query(None)):
    try:
        result = feature_flag_service.evaluate_flag(flag_key=flag_key, user_id=user_id)
        return result
    except Exception as e:
        logger.error(f"Error evaluating flag: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to evaluate feature flag",
        )
