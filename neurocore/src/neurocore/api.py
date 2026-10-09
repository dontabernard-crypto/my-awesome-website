"""FastAPI layer. Optional: pip install -e ".[api]"

Run:
    uvicorn neurocore.api:app --reload
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import select

from .benchmark import latest_benchmark
from .db import init_db, session_scope
from .gamification import generate_quests, get_or_create_avatar
from .models import ActivityEvent, MetricDefinition, RoleConfig, User, utcnow
from .seed import seed_roles


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    seed_roles()
    yield


app = FastAPI(title="NeuroCore", version="0.1.0", lifespan=lifespan)


class UserCreate(BaseModel):
    email: str
    role_slug: str
    display_name: str = ""
    slack_user_id: str | None = None
    segment: dict = Field(default_factory=dict)
    tenure_days: int = 0


class EventIn(BaseModel):
    # Metadata only: a metric key and a number, never message or call content.
    metric_key: str
    value: float = 1.0
    timestamp: datetime | None = None
    source: str = ""


class EventsIn(BaseModel):
    events: list[EventIn] = Field(min_length=1)


def _user_dict(user: User, role_slug: str) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "role_slug": role_slug,
        "slack_user_id": user.slack_user_id,
        "segment": user.segment,
        "tenure_days": user.tenure_days,
    }


def _require_user(user_id: int) -> User:
    with session_scope() as session:
        user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"user {user_id} not found")
    return user


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/roles")
def list_roles() -> list[dict]:
    with session_scope() as session:
        roles = session.exec(select(RoleConfig).order_by(RoleConfig.id)).all()
        metrics = session.exec(select(MetricDefinition).order_by(MetricDefinition.id)).all()

    by_role: dict[int, list[dict]] = {}
    for m in metrics:
        by_role.setdefault(m.role_config_id, []).append({
            "key": m.key,
            "label": m.label,
            "layer": m.layer.value,
            "direction": m.direction.value,
            "weight": m.weight,
            "is_primary_outcome": m.is_primary_outcome,
        })

    return [
        {
            "slug": r.slug,
            "name": r.name,
            "archetype": r.archetype.value,
            "outcome_metric_key": r.outcome_metric_key,
            "segmentation_keys": r.segmentation_keys,
            "privacy_floor": r.privacy_floor.value,
            "metrics": by_role.get(r.id, []),
        }
        for r in roles
    ]


@app.post("/users", status_code=201)
def create_user(body: UserCreate) -> dict:
    with session_scope() as session:
        role = session.exec(select(RoleConfig).where(RoleConfig.slug == body.role_slug)).first()
        if not role:
            raise HTTPException(status_code=404, detail=f"role '{body.role_slug}' not found")
        user = User(
            role_config_id=role.id,
            email=body.email,
            display_name=body.display_name,
            slack_user_id=body.slack_user_id,
            segment=body.segment,
            tenure_days=body.tenure_days,
        )
        session.add(user)
        session.flush()
        session.refresh(user)
        return _user_dict(user, role.slug)


@app.get("/users/{user_id}/avatar")
def user_avatar(user_id: int) -> dict:
    _require_user(user_id)
    avatar = get_or_create_avatar(user_id)
    return {
        "id": avatar.id,
        "user_id": avatar.user_id,
        "name": avatar.name,
        "level": avatar.level,
        "health": round(avatar.health, 1),
        "wealth": round(avatar.wealth, 1),
        "wisdom": round(avatar.wisdom, 1),
        "resilience": round(avatar.resilience, 1),
        "momentum": round(avatar.momentum, 1),
        "total_xp": round(avatar.total_xp, 1),
    }


@app.get("/users/{user_id}/quests")
def user_quests(user_id: int) -> list[dict]:
    _require_user(user_id)
    return generate_quests(user_id)


@app.post("/users/{user_id}/events", status_code=201)
def ingest_events(user_id: int, body: EventsIn) -> dict:
    user = _require_user(user_id)
    with session_scope() as session:
        known = set(
            session.exec(
                select(MetricDefinition.key).where(
                    MetricDefinition.role_config_id == user.role_config_id
                )
            ).all()
        )
        unknown = sorted({e.metric_key for e in body.events} - known)
        if unknown:
            raise HTTPException(
                status_code=422,
                detail=f"metric keys not defined for this user's role: {', '.join(unknown)}",
            )
        for e in body.events:
            session.add(
                ActivityEvent(
                    user_id=user_id,
                    metric_key=e.metric_key,
                    value=e.value,
                    timestamp=e.timestamp or utcnow(),
                    source=e.source,
                )
            )
    return {"user_id": user_id, "accepted": len(body.events)}


@app.get("/benchmark/{role_slug}")
def role_benchmark(role_slug: str, segment: str | None = None) -> dict:
    record = latest_benchmark(role_slug, segment=segment)
    if not record:
        raise HTTPException(
            status_code=404,
            detail=f"no benchmark for role '{role_slug}'"
            + (f" segment '{segment}'" if segment else ""),
        )
    return {
        "role_slug": role_slug,
        "segment": record.segment,
        "computed_at": record.computed_at.isoformat(),
        "profile": record.profile,
    }
