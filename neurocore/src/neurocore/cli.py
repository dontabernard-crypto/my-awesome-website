from __future__ import annotations

import argparse
import json

from dotenv import load_dotenv

load_dotenv()

from sqlmodel import func, select

from .benchmark import compute_benchmark
from .db import init_db, session_scope
from .gamification import apply_daily_xp, generate_quests, get_or_create_avatar
from .models import User
from .seed import seed_roles
from .simulation import simulate


def cmd_seed(_args) -> None:
    init_db()
    seed_roles()
    print("✓ Role packs seeded")


def cmd_simulate(args) -> None:
    init_db()
    n = simulate(args.role, args.users, args.days)
    print(f"✓ Generated {n} activity events for {args.users} users over {args.days} days")


def cmd_benchmark(args) -> None:
    init_db()
    record = compute_benchmark(args.role, window_days=args.window, top_quantile=args.quantile)
    if not record:
        print("✗ No benchmark computed — seed and simulate first")
        return
    print(json.dumps(record.profile, indent=2))


def cmd_avatar(args) -> None:
    init_db()
    avatar = get_or_create_avatar(args.user_id)
    print(json.dumps({
        "id": avatar.id,
        "user_id": avatar.user_id,
        "level": avatar.level,
        "health": round(avatar.health, 1),
        "wealth": round(avatar.wealth, 1),
        "wisdom": round(avatar.wisdom, 1),
        "momentum": round(avatar.momentum, 1),
        "total_xp": round(avatar.total_xp, 1),
    }, indent=2))


def cmd_quests(args) -> None:
    init_db()
    print(json.dumps(generate_quests(args.user_id), indent=2))


def cmd_apply(args) -> None:
    init_db()
    print(json.dumps(apply_daily_xp(args.user_id, day_offset_days=args.day_offset), indent=2))


def cmd_loop(args) -> None:
    init_db()
    seed_roles()
    print("✓ Seeded role packs")

    with session_scope() as session:
        existing = session.exec(select(func.count(User.id))).one()
    if existing == 0:
        simulate(args.role, args.users, args.days)
        print(f"✓ Simulated {args.users} users × {args.days} days")

    record = compute_benchmark(args.role, window_days=args.days)
    print(f"✓ Benchmark computed ({record.sample_size} users)")

    with session_scope() as session:
        user = session.exec(select(User)).first()
        uid = user.id

    apply_daily_xp(uid, day_offset_days=0)
    avatar = get_or_create_avatar(uid)
    print(f"\n── Avatar (user {uid}) ──")
    print(json.dumps({
        "level": avatar.level,
        "health": round(avatar.health, 1),
        "wealth": round(avatar.wealth, 1),
        "wisdom": round(avatar.wisdom, 1),
        "total_xp": round(avatar.total_xp, 1),
    }, indent=2))

    print("\n── Daily Quests ──")
    for q in generate_quests(uid):
        print(f"  • [{q['xp_layer']}] {q['label']}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="neurocore")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("seed").set_defaults(func=cmd_seed)

    p_sim = sub.add_parser("simulate")
    p_sim.add_argument("--role", default="mid_market_sdr")
    p_sim.add_argument("--users", type=int, default=20)
    p_sim.add_argument("--days", type=int, default=60)
    p_sim.set_defaults(func=cmd_simulate)

    p_bench = sub.add_parser("benchmark")
    p_bench.add_argument("--role", default="mid_market_sdr")
    p_bench.add_argument("--window", type=int, default=90)
    p_bench.add_argument("--quantile", type=float, default=0.75)
    p_bench.set_defaults(func=cmd_benchmark)

    p_av = sub.add_parser("avatar")
    p_av.add_argument("--user-id", type=int, required=True)
    p_av.set_defaults(func=cmd_avatar)

    p_q = sub.add_parser("quests")
    p_q.add_argument("--user-id", type=int, required=True)
    p_q.set_defaults(func=cmd_quests)

    p_apply = sub.add_parser("apply")
    p_apply.add_argument("--user-id", type=int, required=True)
    p_apply.add_argument("--day-offset", type=int, default=0)
    p_apply.set_defaults(func=cmd_apply)

    p_loop = sub.add_parser("loop")
    p_loop.add_argument("--role", default="mid_market_sdr")
    p_loop.add_argument("--users", type=int, default=20)
    p_loop.add_argument("--days", type=int, default=60)
    p_loop.set_defaults(func=cmd_loop)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
