from __future__ import annotations

import os
import tempfile
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from neurocore import db
from neurocore.api import app
from neurocore.benchmark import compute_benchmark
from neurocore.models import utcnow
from neurocore.simulation import simulate

ROLE = "software_engineer"


@pytest.fixture(scope="module")
def client():
    previous = os.environ.get("DATABASE_URL")
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp.name}"
    db.reset_engine()

    with TestClient(app) as c:  # runs lifespan: init_db + seed_roles
        simulate(ROLE, num_users=8, days=14, seed=3)
        compute_benchmark(ROLE, window_days=14)
        yield c

    db.reset_engine()
    if previous is None:
        os.environ.pop("DATABASE_URL", None)
    else:
        os.environ["DATABASE_URL"] = previous
    os.unlink(tmp.name)


@pytest.fixture(scope="module")
def user_id(client) -> int:
    r = client.post("/users", json={
        "email": "api@example.com",
        "role_slug": ROLE,
        "display_name": "API User",
        "segment": {"tenure": "new"},
    })
    assert r.status_code == 201
    return r.json()["id"]


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_roles_lists_seeded_packs(client):
    roles = {r["slug"]: r for r in client.get("/roles").json()}
    assert {"mid_market_sdr", "software_engineer", "university_student"} <= roles.keys()
    sdr = roles["mid_market_sdr"]
    assert sdr["privacy_floor"] == "aggregate_only"
    assert "meetings_booked" in {m["key"] for m in sdr["metrics"]}


def test_create_user(client, user_id):
    assert user_id > 0


def test_create_user_unknown_role(client):
    r = client.post("/users", json={"email": "x@example.com", "role_slug": "astronaut"})
    assert r.status_code == 404


def test_avatar_defaults(client, user_id):
    r = client.get(f"/users/{user_id}/avatar")
    assert r.status_code == 200
    body = r.json()
    assert body["user_id"] == user_id
    assert body["level"] == 1
    assert body["total_xp"] == 0.0


def test_avatar_unknown_user(client):
    assert client.get("/users/99999/avatar").status_code == 404


def test_quests(client, user_id):
    r = client.get(f"/users/{user_id}/quests")
    assert r.status_code == 200
    quests = r.json()
    assert quests and all("label" in q for q in quests)


def test_quests_unknown_user(client):
    assert client.get("/users/99999/quests").status_code == 404


def test_post_events(client, user_id):
    r = client.post(f"/users/{user_id}/events", json={"events": [
        {"metric_key": "deployment_frequency", "value": 2, "source": "GitHub"},
        {"metric_key": "deep_work_blocks", "value": 3,
         "timestamp": (utcnow() - timedelta(days=1)).isoformat()},
    ]})
    assert r.status_code == 201
    assert r.json() == {"user_id": user_id, "accepted": 2}


def test_post_events_rejects_metric_from_other_role(client, user_id):
    r = client.post(f"/users/{user_id}/events", json={"events": [
        {"metric_key": "deployment_frequency", "value": 1},
        {"metric_key": "calls_per_day", "value": 50},
    ]})
    assert r.status_code == 422
    assert "calls_per_day" in r.json()["detail"]


def test_post_events_rejects_empty_batch(client, user_id):
    assert client.post(f"/users/{user_id}/events", json={"events": []}).status_code == 422


def test_post_events_unknown_user(client):
    r = client.post("/users/99999/events", json={"events": [{"metric_key": "x"}]})
    assert r.status_code == 404


def test_benchmark(client):
    r = client.get(f"/benchmark/{ROLE}")
    assert r.status_code == 200
    body = r.json()
    assert body["segment"] == "all"
    assert body["profile"]["sample_size"] == 8
    assert "deployment_frequency" in body["profile"]["metrics"]


def test_benchmark_missing(client):
    assert client.get("/benchmark/astronaut").status_code == 404
    assert client.get(f"/benchmark/{ROLE}", params={"segment": "tenure:nobody"}).status_code == 404
