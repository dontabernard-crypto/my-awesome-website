from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlmodel import select

from .benchmark import latest_benchmark
from .db import session_scope
from .models import (
    ActivityEvent,
    Avatar,
    Direction,
    RoleConfig,
    User,
    utcnow,
)

BASE_XP = 10.0
XP_CAP = 2.0
XP_FLOOR = 0.0


def _ratio(actual: float, target: float, direction: Direction) -> float:
    if target <= 0:
        return 1.0
    if direction == Direction.HIGHER_IS_BETTER:
        raw = actual / target
    else:
        raw = target / max(actual, 1e-6)
    return max(XP_FLOOR, min(XP_CAP, raw))


def compute_xp(role_slug: str, user_daily: dict[str, float]) -> dict[str, float]:
    profile_record = latest_benchmark(role_slug)
    if not profile_record:
        return {"wealth": 0.0, "wisdom": 0.0, "health": 0.0, "total": 0.0}

    metrics = profile_record.profile["metrics"]
    wealth = wisdom = health = 0.0

    for key, actual in user_daily.items():
        m = metrics.get(key)
        if not m:
            continue
        r = _ratio(actual, m["top_performer"], Direction(m["direction"]))
        xp = BASE_XP * m["weight"] * r

        layer = m["layer"]
        if layer in ("volume", "efficiency"):
            wealth += xp
        elif layer == "quality":
            wisdom += xp
        elif layer == "behavioral":
            health += xp

    return {
        "wealth": round(wealth, 2),
        "wisdom": round(wisdom, 2),
        "health": round(health, 2),
        "total": round(wealth + wisdom + health, 2),
    }


def get_or_create_avatar(user_id: int) -> Avatar:
    with session_scope() as session:
        avatar = session.exec(select(Avatar).where(Avatar.user_id == user_id)).first()
        if avatar:
            return avatar
        avatar = Avatar(user_id=user_id, name="Companion")
        session.add(avatar)
        session.flush()
        session.refresh(avatar)
        return avatar


def _day_bounds(day_offset_days: int) -> tuple[datetime, datetime]:
    now = utcnow()
    target = now - timedelta(days=day_offset_days)
    start = datetime(target.year, target.month, target.day, tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    return start, end


def apply_daily_xp(user_id: int, day_offset_days: int = 0) -> dict:
    with session_scope() as session:
        user = session.get(User, user_id)
        if not user:
            return {"error": "user not found"}
        role = session.get(RoleConfig, user.role_config_id)
        if not role:
            return {"error": "role not found"}

        start, end = _day_bounds(day_offset_days)
        events = session.exec(
            select(ActivityEvent).where(
                ActivityEvent.user_id == user_id,
                ActivityEvent.timestamp >= start,
                ActivityEvent.timestamp < end,
            )
        ).all()

        daily: dict[str, float] = {}
        for e in events:
            daily[e.metric_key] = daily.get(e.metric_key, 0.0) + e.value

        xp = compute_xp(role.slug, daily)

        avatar = session.exec(select(Avatar).where(Avatar.user_id == user_id)).first()
        if not avatar:
            avatar = Avatar(user_id=user_id)
            session.add(avatar)
            session.flush()

        avatar.wealth += xp["wealth"]
        avatar.wisdom += xp["wisdom"]
        avatar.health = min(100.0, avatar.health + xp["health"] * 0.1)
        avatar.total_xp += xp["total"]
        avatar.level = 1 + int(avatar.total_xp // 500)
        avatar.momentum = min(100.0, avatar.momentum + 2.0)
        avatar.updated_at = utcnow()

        session.flush()
        session.refresh(avatar)

        return {
            "avatar_id": avatar.id,
            "level": avatar.level,
            "health": round(avatar.health, 1),
            "wealth": round(avatar.wealth, 1),
            "wisdom": round(avatar.wisdom, 1),
            "total_xp": round(avatar.total_xp, 1),
            "daily_xp": xp,
            "daily_activity": daily,
        }


def generate_quests(user_id: int) -> list[dict]:
    with session_scope() as session:
        user = session.get(User, user_id)
        if not user:
            return []
        role = session.get(RoleConfig, user.role_config_id)
        if not role:
            return []
        profile_record = latest_benchmark(role.slug)
        if not profile_record:
            return []

        metrics = profile_record.profile["metrics"]
        quests: list[dict] = []

        for key, m in metrics.items():
            if m["layer"] == "volume":
                quests.append({
                    "metric": key,
                    "label": f"Hit {m['top_performer']:.0f} {m['label'].lower()}",
                    "target": m["top_performer"],
                    "xp_layer": "wealth",
                })
            elif m["layer"] == "quality":
                direction = "under" if m["direction"] == "lower_is_better" else "above"
                quests.append({
                    "metric": key,
                    "label": f"Stay {direction} {m['top_performer']:.2f} on {m['label'].lower()}",
                    "target": m["top_performer"],
                    "xp_layer": "wisdom",
                })

        quests.append({
            "metric": "deep_work_blocks",
            "label": "Take a 10-min break every 90 min of focused work",
            "target": 4,
            "xp_layer": "health",
        })

        return quests
