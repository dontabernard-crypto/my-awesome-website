from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

from sqlmodel import Session, SQLModel, create_engine

from . import models  # noqa: F401 — register tables
from .models import PrivacyFloor, RoleConfig


def _url() -> str:
    return os.environ.get("DATABASE_URL", "sqlite:///neurocore.db")


_engine = None


def get_engine():
    global _engine
    if _engine is None:
        connect_args = {}
        if _url().startswith("sqlite"):
            connect_args = {"check_same_thread": False}
        _engine = create_engine(_url(), echo=False, connect_args=connect_args)
    return _engine


def reset_engine() -> None:
    global _engine
    _engine = None


def init_db() -> None:
    SQLModel.metadata.create_all(get_engine())


@contextmanager
def session_scope() -> Iterator[Session]:
    with Session(get_engine(), expire_on_commit=False) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise


SELF = "self"
_INDIVIDUAL_BLOCKED = (PrivacyFloor.AGGREGATE_ONLY, PrivacyFloor.SELF_ONLY)


def assert_can_view_individual(role: RoleConfig, viewer_role: str) -> None:
    """Gate any read of one person's data by someone in `viewer_role`.

    People can always see their own data (viewer_role == "self"). Anyone else
    (a manager, a peer, an unidentified caller) is refused when the subject's
    RoleConfig.privacy_floor is AGGREGATE_ONLY or SELF_ONLY.
    """
    if viewer_role == SELF:
        return
    if role.privacy_floor in _INDIVIDUAL_BLOCKED:
        raise PermissionError(
            f"role '{role.slug}' has privacy_floor={role.privacy_floor.value}: "
            f"individual data is not visible to '{viewer_role}'"
        )
