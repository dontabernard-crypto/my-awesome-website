from __future__ import annotations

import random
from datetime import timedelta

from sqlmodel import select

from .db import session_scope
from .models import ActivityEvent, MetricDefinition, RoleConfig, User, utcnow


def simulate(role_slug: str, num_users: int, days: int, seed: int = 42) -> int:
    rng = random.Random(seed)
    created = 0

    with session_scope() as session:
        role = session.exec(select(RoleConfig).where(RoleConfig.slug == role_slug)).first()
        if not role:
            raise ValueError(f"role '{role_slug}' not seeded")

        metrics = session.exec(
            select(MetricDefinition).where(MetricDefinition.role_config_id == role.id)
        ).all()

        users: list[User] = []
        for i in range(num_users):
            u = User(
                role_config_id=role.id,
                email=f"{role_slug}-{i}@example.com",
                display_name=f"{role_slug.split('_')[0].title()} {i}",
                segment={"tenure": rng.choice(["new", "ramped", "veteran"])},
                tenure_days=rng.randint(30, 1200),
            )
            session.add(u)
            users.append(u)
        session.flush()

        now = utcnow()
        for u in users:
            skill = max(0.4, min(1.8, rng.gauss(1.0, 0.3)))
            for day in range(days):
                day_ts = now - timedelta(days=day)
                for m in metrics:
                    base = _base_for(m.key)
                    noise = rng.gauss(1.0, 0.15)
                    value = base * skill * noise

                    if "rate" in m.key or "ratio" in m.key or "pct" in m.key:
                        value = max(0.0, min(1.0, value))
                    elif "hours" in m.key or "days" in m.key:
                        value = max(0.1, value)
                    else:
                        value = max(0.0, value)

                    session.add(
                        ActivityEvent(
                            user_id=u.id,
                            metric_key=m.key,
                            value=value,
                            timestamp=day_ts,
                            source=m.source_api,
                        )
                    )
                    created += 1

    return created


def _base_for(metric_key: str) -> float:
    bases = {
        "calls_per_day": 55.0,
        "emails_per_day": 250.0,
        "linkedin_touches_per_day": 18.0,
        "connect_rate": 0.15,
        "meeting_rate": 0.06,
        "talk_listen_ratio": 1.4,
        "follow_up_hours": 4.0,
        "meetings_booked": 0.6,
        "prs_opened": 1.5,
        "prs_reviewed": 2.0,
        "cycle_time_hours": 36.0,
        "review_turnaround_hours": 8.0,
        "change_failure_rate": 0.12,
        "deep_work_blocks": 3.0,
        "deployment_frequency": 1.0,
        "specs_written": 0.3,
        "user_interviews": 0.4,
        "cycle_time_days": 14.0,
        "adoption_rate": 0.35,
        "stakeholder_nps": 30.0,
        "features_shipped": 0.4,
        "deliverables_completed": 1.2,
        "utilization_pct": 0.75,
        "revision_cycles": 2.0,
        "client_nps": 40.0,
        "deadline_buffer_days": 1.5,
        "engagements_delivered": 0.2,
        "models_built": 0.5,
        "close_cycle_days": 6.0,
        "accuracy_rate": 0.94,
        "reports_delivered": 0.8,
        "study_blocks": 3.0,
        "assignments_submitted": 0.5,
        "late_submissions": 0.15,
        "focus_minutes": 90.0,
        "assignments_completed": 0.4,
    }
    return bases.get(metric_key, 1.0)
