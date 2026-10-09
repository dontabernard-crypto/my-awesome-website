from __future__ import annotations

from collections import defaultdict
from datetime import timedelta

from sqlmodel import select

from .db import session_scope
from .models import (
    ActivityEvent,
    BenchmarkProfile,
    MetricDefinition,
    RoleConfig,
    User,
    utcnow,
)


def _daily_average(events: list[ActivityEvent], days: int, metric_key: str) -> float:
    total = sum(e.value for e in events if e.metric_key == metric_key)
    return total / max(days, 1)


def _user_outcome(events: list[ActivityEvent], outcome_key: str) -> float:
    return sum(e.value for e in events if e.metric_key == outcome_key)


MIN_SEGMENT_SIZE = 5


def _build_profile(
    role: RoleConfig,
    metrics: list[MetricDefinition],
    users: list[User],
    by_user: dict[int, list[ActivityEvent]],
    segment: str,
    window_days: int,
    top_quantile: float,
) -> BenchmarkProfile:
    ranked = sorted(
        users,
        key=lambda u: _user_outcome(by_user.get(u.id, []), role.outcome_metric_key),
        reverse=True,
    )
    top_n = max(1, int(len(ranked) * (1 - top_quantile)))
    top_users = ranked[:top_n]

    profile: dict = {
        "role_slug": role.slug,
        "archetype": role.archetype.value,
        "outcome_metric": role.outcome_metric_key,
        "segment": segment,
        "window_days": window_days,
        "top_quantile": top_quantile,
        "sample_size": len(users),
        "top_performers_sampled": len(top_users),
        "metrics": {},
    }

    def mean(xs: list[float]) -> float:
        return sum(xs) / len(xs) if xs else 0.0

    for m in metrics:
        top_vals = [_daily_average(by_user.get(u.id, []), window_days, m.key) for u in top_users]
        team_vals = [_daily_average(by_user.get(u.id, []), window_days, m.key) for u in users]

        profile["metrics"][m.key] = {
            "label": m.label,
            "layer": m.layer.value,
            "direction": m.direction.value,
            "weight": m.weight,
            "unit": m.unit,
            "top_performer": round(mean(top_vals), 4),
            "team_baseline": round(mean(team_vals), 4),
            "is_primary_outcome": m.is_primary_outcome,
        }

    return BenchmarkProfile(
        role_config_id=role.id,
        segment=segment,
        window_days=window_days,
        sample_size=len(users),
        top_quantile=top_quantile,
        profile=profile,
    )


def segment_label(key: str, value: object) -> str:
    return f"{key}:{value}"


def compute_benchmark(
    role_slug: str, window_days: int = 90, top_quantile: float = 0.75
) -> BenchmarkProfile | None:
    """Compute the role-wide ("all") profile plus one per segment value.

    Segments come from RoleConfig.segmentation_keys matched against User.segment,
    e.g. "tenure:new". Segments with fewer than MIN_SEGMENT_SIZE users are skipped
    so a profile never describes one or two individuals. Returns the "all" profile.
    """
    with session_scope() as session:
        role = session.exec(select(RoleConfig).where(RoleConfig.slug == role_slug)).first()
        if not role:
            return None

        metrics = session.exec(
            select(MetricDefinition).where(MetricDefinition.role_config_id == role.id)
        ).all()
        users = session.exec(
            select(User).where(User.role_config_id == role.id)
        ).all()
        if not users:
            return None

        cutoff = utcnow() - timedelta(days=window_days)
        events = session.exec(select(ActivityEvent).where(ActivityEvent.timestamp >= cutoff)).all()

        by_user: dict[int, list[ActivityEvent]] = defaultdict(list)
        for e in events:
            by_user[e.user_id].append(e)

        groups: dict[str, list[User]] = {"all": list(users)}
        for key in role.segmentation_keys or []:
            for u in users:
                value = (u.segment or {}).get(key)
                if value is not None:
                    groups.setdefault(segment_label(key, value), []).append(u)

        overall = None
        for segment, members in groups.items():
            if segment != "all" and len(members) < MIN_SEGMENT_SIZE:
                continue
            record = _build_profile(
                role, metrics, members, by_user, segment, window_days, top_quantile
            )
            session.add(record)
            if segment == "all":
                overall = record

        session.flush()
        session.refresh(overall)
        return overall


def latest_benchmark(role_slug: str, segment: str | None = None) -> BenchmarkProfile | None:
    """Newest profile for a role; segment=None means the role-wide "all" profile."""
    with session_scope() as session:
        role = session.exec(select(RoleConfig).where(RoleConfig.slug == role_slug)).first()
        if not role:
            return None
        return session.exec(
            select(BenchmarkProfile)
            .where(
                BenchmarkProfile.role_config_id == role.id,
                BenchmarkProfile.segment == (segment or "all"),
            )
            .order_by(BenchmarkProfile.computed_at.desc(), BenchmarkProfile.id.desc())
        ).first()
