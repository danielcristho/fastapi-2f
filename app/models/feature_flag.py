"""
Feature flag data models.
Use pydantic models for validation and serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class RolloutStrategy(str, Enum):
    ALL = "all"                # everyone gets it
    PERCENTAGE = "percentage"  # gradual rollout based on hash
    USER_LIST = "user_list"    # specific users only
    CUSTOM = "custom"          # for future expansion


class FeatureFlagRule(BaseModel):
    # rules for how to roll out a feature
    strategy: RolloutStrategy = RolloutStrategy.ALL
    percentage: Optional[int] = Field(None, ge=0, le=100)  # 0-100%
    user_ids: Optional[List[str]] = None                   # specific users
    custom_rules: Optional[Dict[str, Any]] = None          # for later


class FeatureFlag(BaseModel):
    # the main feature flag model
    key: str = Field(..., min_length=1, max_length=100)
    enabled: bool = True
    description: Optional[str] = None
    rules: FeatureFlagRule = Field(default_factory=lambda: FeatureFlagRule())
    metadata: Optional[Dict[str, Any]] = None  # extra stuff if needed
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class FeatureFlagCreate(BaseModel):
    # for creating new flags
    key: str = Field(..., min_length=1, max_length=100)
    enabled: bool = True
    description: Optional[str] = None
    rules: Optional[FeatureFlagRule] = None
    metadata: Optional[Dict[str, Any]] = None


class FeatureFlagUpdate(BaseModel):
    # for updating existing flags - everything optional
    enabled: Optional[bool] = None
    description: Optional[str] = None
    rules: Optional[FeatureFlagRule] = None
    metadata: Optional[Dict[str, Any]] = None


class FeatureFlagEvaluation(BaseModel):
    # request model for evaluating a flag
    key: str
    enabled: bool
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class FeatureFlagEvaluationResult(BaseModel):
    # response model for flag evaluation
    key: str
    enabled: bool
    matched_rule: Optional[str] = None  # which rule matched
    source: str                         # cache, ssm, or none
