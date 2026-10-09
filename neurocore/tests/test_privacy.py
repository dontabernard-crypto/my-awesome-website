from __future__ import annotations

import os
import tempfile

import pytest
from fastapi.testclient import TestClient

from neurocore import db
from neurocore.api import app
from neurocore.db import assert_can_view_individual
from neurocore.models import Archetype, PrivacyFloor, RoleConfig


def _role(floor: PrivacyFloor) -> RoleConfig:
    return RoleConfig(
        slug=f"r_{floor.value}",
        name="R",
        archetype=Archetype.VOLUME_DRIVEN,
        outcome_metric_key="x",
        privacy_floor=floor,
    )


@pytest.mark.parametrize("floor", list(PrivacyFloor))
def test_self_can_always_view(floor):
    assert_can_view_individual(_role(floor), "self")


@pytest.mark.parametrize("floor", [PrivacyFloor.AGGREGATE_ONLY, PrivacyFloor.SELF_ONLY])
@pytest.mark.parametrize("viewer", ["manager", "peer", "other"])
def test_others_blocked_below_opt_in(floor, viewer):
    with pytest.raises(PermissionError, match=floor.value):
        assert_can_view_individual(_role(floor), viewer)


def test_others_allowed_when_opt_in_individual():
    assert_can_view_individual(_role(PrivacyFloor.OPT_IN_INDIVIDUAL), "manager")


@pytest.fixture(scope="module")
def client():
    previous = os.environ.get("DATABASE_URL")
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp.name}"
    db.reset_engine()

    with TestClient(app) as c:
        yield c

    db.reset_engine()
    if previous is None:
        os.environ.pop("DATABASE_URL", None)
    else:
        os.environ["DATABASE_URL"] = previous
    os.unlink(tmp.name)


@pytest.fixture(scope="module")
def users(client) -> dict[str, int]:
    ids = {}
    for slug in ("mid_market_sdr", "university_student", "software_engineer"):
        r = client.post("/users", json={"email": f"{slug}@example.com", "role_slug": slug})
        assert r.status_code == 201
        ids[slug] = r.json()["id"]
    return ids


INDIVIDUAL_ENDPOINTS = ["/users/{id}/avatar", "/users/{id}/quests"]


@pytest.mark.parametrize("path", INDIVIDUAL_ENDPOINTS)
@pytest.mark.parametrize("slug", ["mid_market_sdr", "university_student"])
def test_api_blocks_other_viewers(client, users, path, slug):
    uid = users[slug]
    other = users["software_engineer"]
    for headers in ({}, {"X-Viewer-Id": str(other)}):
        r = client.get(path.format(id=uid), headers=headers)
        assert r.status_code == 403
        assert "privacy_floor" in r.json()["detail"]


@pytest.mark.parametrize("path", INDIVIDUAL_ENDPOINTS)
@pytest.mark.parametrize("slug", ["mid_market_sdr", "university_student", "software_engineer"])
def test_api_allows_self(client, users, path, slug):
    uid = users[slug]
    r = client.get(path.format(id=uid), headers={"X-Viewer-Id": str(uid)})
    assert r.status_code == 200


@pytest.mark.parametrize("path", INDIVIDUAL_ENDPOINTS)
def test_api_allows_others_for_opt_in_role(client, users, path):
    uid = users["software_engineer"]
    r = client.get(path.format(id=uid), headers={"X-Viewer-Id": str(users["mid_market_sdr"])})
    assert r.status_code == 200


def test_unknown_user_is_404_not_403(client):
    assert client.get("/users/99999/avatar").status_code == 404
