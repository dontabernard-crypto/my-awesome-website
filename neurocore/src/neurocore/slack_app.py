"""Slack Bolt entry point. Optional: pip install -e ".[slack]"

Run:
    export SLACK_BOT_TOKEN=... SLACK_SIGNING_SECRET=...
    neurocore-slack
"""
from __future__ import annotations

import os

from dotenv import load_dotenv
from sqlmodel import select

load_dotenv()

from .db import init_db, session_scope
from .gamification import apply_daily_xp, generate_quests, get_or_create_avatar
from .models import User
from .seed import seed_roles


def _resolve(slack_user_id: str) -> int:
    with session_scope() as session:
        u = session.exec(select(User).where(User.slack_user_id == slack_user_id)).first()
        if u:
            return u.id
        first = session.exec(select(User)).first()
        return first.id if first else 1


def build_app():
    try:
        from slack_bolt import App
    except ImportError:
        raise SystemExit("Install slack support: pip install -e '.[slack]'")

    app = App(
        token=os.environ["SLACK_BOT_TOKEN"],
        signing_secret=os.environ["SLACK_SIGNING_SECRET"],
    )

    @app.command("/neurocore-quests")
    def quests(ack, body, respond):
        ack()
        user_id = _resolve(body["user_id"])
        qs = generate_quests(user_id)
        lines = "\n".join(f"• [{q['xp_layer']}] {q['label']}" for q in qs)
        respond(f"*Today's quests:*\n{lines}")

    @app.command("/neurocore-avatar")
    def avatar(ack, body, respond):
        ack()
        user_id = _resolve(body["user_id"])
        apply_daily_xp(user_id, day_offset_days=0)
        a = get_or_create_avatar(user_id)
        respond(
            f"*{a.name}* — Lvl {a.level}\n"
            f"❤️ Health {a.health:.0f}  💰 Wealth {a.wealth:.0f}  "
            f"🧠 Wisdom {a.wisdom:.0f}  ⚡ Momentum {a.momentum:.0f}"
        )

    return app


def main() -> None:
    init_db()
    seed_roles()
    app = build_app()
    app.start(port=int(os.environ.get("PORT", 3000)))


if __name__ == "__main__":
    main()
