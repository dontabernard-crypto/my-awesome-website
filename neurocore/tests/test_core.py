from __future__ import annotations

import os
import tempfile

import pytest
from sqlmodel import select

_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp.name}"

from neurocore.benchmark import compute_benchmark
from neurocore.db import init_db, session_scope
from neurocore.gamification import apply_daily_xp, generate_quests
from neurocore.models import User
from neurocore.seed import seed_roles
from neurocore.simulation import simulate


@pytest.fixture(scope="module", autouse=True)
def setup():
    init_db()
    seed_roles()
    simulate("mid_market_sdr", num_users=15, days=30, seed=1)


def test_benchmark_produces_profile():
    record = compute_benchmark("mid_market_sdr", window_days=30)
    assert record is not None
    assert record.sample_size == 15
    assert "meetings_booked" in record.profile["metrics"]
    assert record.profile["metrics"]["meetings_booked"]["top_performer"] > 0


def test_avatar_gains_xp():
    with session_scope() as session:
        user = session.exec(select(User)).first()
        uid = user.id
    result = apply_daily_xp(uid, day_offset_days=0)
    assert "total_xp" in result
    assert result["avatar_id"] is not None


def test_quests_generated():
    with session_scope() as session:
        user = session.exec(select(User)).first()
        uid = user.id
    quests = generate_quests(uid)
    assert len(quests) > 0
    assert all("label" in q for q in quests)
