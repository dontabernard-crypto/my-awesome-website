from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import JSON, Column, UniqueConstraint
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Archetype(str, Enum):
    VOLUME_DRIVEN = "volume_driven"
    FLOW_DRIVEN = "flow_driven"
    DELIVERABLE_DRIVEN = "deliverable_driven"


class MetricLayer(str, Enum):
    VOLUME = "volume"
    EFFICIENCY = "efficiency"
    QUALITY = "quality"
    BEHAVIORAL = "behavioral"


class Direction(str, Enum):
    HIGHER_IS_BETTER = "higher_is_better"
    LOWER_IS_BETTER = "lower_is_better"


class PrivacyFloor(str, Enum):
    AGGREGATE_ONLY = "aggregate_only"
    OPT_IN_INDIVIDUAL = "opt_in_individual"
    SELF_ONLY = "self_only"


class Organization(SQLModel, table=True):
    __tablename__ = "organizations"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    created_at: datetime = Field(default_factory=utcnow)


class RoleConfig(SQLModel, table=True):
    __tablename__ = "role_configs"
    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(index=True, unique=True)
    name: str
    archetype: Archetype
    outcome_metric_key: str
    description: str = ""
    segmentation_keys: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    privacy_floor: PrivacyFloor = PrivacyFloor.AGGREGATE_ONLY
    created_at: datetime = Field(default_factory=utcnow)


class MetricDefinition(SQLModel, table=True):
    __tablename__ = "metric_definitions"
    __table_args__ = (UniqueConstraint("role_config_id", "key", name="uq_role_metric"),)
    id: Optional[int] = Field(default=None, primary_key=True)
    role_config_id: int = Field(foreign_key="role_configs.id", index=True)
    key: str
    label: str
    layer: MetricLayer
    direction: Direction = Direction.HIGHER_IS_BETTER
    unit: str = "count"
    weight: float = 1.0
    source_api: str = ""
    is_primary_outcome: bool = False


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    org_id: Optional[int] = Field(default=None, foreign_key="organizations.id", index=True)
    role_config_id: int = Field(foreign_key="role_configs.id", index=True)
    email: str
    display_name: str = ""
    slack_user_id: Optional[str] = None
    segment: dict = Field(default_factory=dict, sa_column=Column(JSON))
    tenure_days: int = 0
    created_at: datetime = Field(default_factory=utcnow)


class ActivityEvent(SQLModel, table=True):
    __tablename__ = "activity_events"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    metric_key: str = Field(index=True)
    value: float = 1.0
    timestamp: datetime = Field(default_factory=utcnow, index=True)
    source: str = ""


class BenchmarkProfile(SQLModel, table=True):
    __tablename__ = "benchmark_profiles"
    id: Optional[int] = Field(default=None, primary_key=True)
    role_config_id: int = Field(foreign_key="role_configs.id", index=True)
    segment: str = "all"
    window_days: int = 90
    sample_size: int = 0
    top_quantile: float = 0.75
    profile: dict = Field(default_factory=dict, sa_column=Column(JSON))
    computed_at: datetime = Field(default_factory=utcnow)


class Avatar(SQLModel, table=True):
    __tablename__ = "avatars"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True, index=True)
    name: str = "Companion"
    health: float = 100.0
    wealth: float = 0.0
    wisdom: float = 0.0
    resilience: float = 0.0
    momentum: float = 0.0
    level: int = 1
    total_xp: float = 0.0
    updated_at: datetime = Field(default_factory=utcnow)
