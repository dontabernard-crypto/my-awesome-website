from __future__ import annotations

import os
import tempfile
from datetime import timedelta

import pytest
from sqlmodel import select

from neurocore import db
from neurocore.benchmark import MIN_SEGMENT_SIZE, compute_benchmark, latest_benchmark
from neurocore.gamification import apply_daily_xp, benchmark_for_user, compute_xp
from neurocore.models import ActivityEvent, BenchmarkProfile, RoleConfig, User, utcnow
from neurocore.seed import seed_roles

ROLE = "software_engineer"
OUTCOME = "deployment_frequency"
WINDOW = 10


@pytest.fixture(scope="module", autouse=True)
def segmented_db():
    """Own database: new engineers deploy 1/day, veterans 3/day, one solo 'staff' user."""
    previous = os.environ.get("DATABASE_URL")
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp.name}"
    db.reset_engine()
    db.init_db()
    seed_roles()

    now = utcnow()
    with db.session_scope() as session:
        role = session.exec(select(RoleConfig).where(RoleConfig.slug == ROLE)).one()
        cohorts = [("new", 1.0, MIN_SEGMENT_SIZE), ("veteran", 3.0, MIN_SEGMENT_SIZE), ("staff", 5.0, 1)]
        for tenure, per_day, count in cohorts:
            for i in range(count):
                user = User(
                    role_config_id=role.id,
                    email=f"{tenure}-{i}@example.com",
                    segment={"tenure": tenure},
                )
                session.add(user)
                session.flush()
                for day in range(WINDOW):
                    session.add(
                        ActivityEvent(
                            user_id=user.id,
                            metric_key=OUTCOME,
                            value=per_day,
                            timestamp=now - timedelta(days=day),
                        )
                    )

    compute_benchmark(ROLE, window_days=WINDOW)
    yield

    db.reset_engine()
    if previous is None:
        os.environ.pop("DATABASE_URL", None)
    else:
        os.environ["DATABASE_URL"] = previous
    os.unlink(tmp.name)


def _top(record: BenchmarkProfile) -> float:
    return record.profile["metrics"][OUTCOME]["top_performer"]


def test_one_profile_per_segment_value():
    with db.session_scope() as session:
        segments = {p.segment: p.sample_size for p in session.exec(select(BenchmarkProfile))}
    assert segments == {
        "all": 2 * MIN_SEGMENT_SIZE + 1,
        "tenure:new": MIN_SEGMENT_SIZE,
        "tenure:veteran": MIN_SEGMENT_SIZE,
    }


def test_segments_below_minimum_size_are_skipped():
    assert latest_benchmark(ROLE, segment="tenure:staff") is None


def test_latest_benchmark_filters_by_segment():
    overall = latest_benchmark(ROLE)
    new = latest_benchmark(ROLE, segment="tenure:new")
    veteran = latest_benchmark(ROLE, segment="tenure:veteran")

    assert overall.segment == "all"
    assert new.profile["segment"] == "tenure:new"
    assert _top(new) == pytest.approx(1.0)
    assert _top(veteran) == pytest.approx(3.0)


def test_latest_benchmark_returns_newest_snapshot():
    first = latest_benchmark(ROLE, segment="tenure:new")
    compute_benchmark(ROLE, window_days=WINDOW)
    assert latest_benchmark(ROLE, segment="tenure:new").id > first.id


def test_user_is_matched_to_their_segment():
    assert benchmark_for_user(ROLE, {"tenure": "new"}).segment == "tenure:new"
    assert benchmark_for_user(ROLE, {"tenure": "veteran"}).segment == "tenure:veteran"


def test_falls_back_to_role_wide_profile():
    assert benchmark_for_user(ROLE, None).segment == "all"
    assert benchmark_for_user(ROLE, {"team": "platform"}).segment == "all"
    assert benchmark_for_user(ROLE, {"tenure": "staff"}).segment == "all"


def test_compute_xp_uses_segment_benchmark():
    day = {OUTCOME: 1.0}
    as_new = compute_xp(ROLE, day, {"tenure": "new"})
    as_veteran = compute_xp(ROLE, day, {"tenure": "veteran"})

    # 1 deploy matches the new-hire top quartile but is a third of the veterans'.
    assert as_new["total"] == pytest.approx(10.0 * 2.5 * 1.0)
    assert as_veteran["total"] == pytest.approx(10.0 * 2.5 / 3.0, abs=0.01)


def test_apply_daily_xp_uses_users_segment():
    with db.session_scope() as session:
        user = session.exec(select(User).where(User.email == "new-0@example.com")).one()
        uid, segment = user.id, user.segment

    result = apply_daily_xp(uid)
    assert result["daily_xp"] == compute_xp(ROLE, result["daily_activity"], segment)
    assert result["daily_xp"]["total"] == pytest.approx(25.0)
