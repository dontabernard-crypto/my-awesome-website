# NeuroCore architecture: one ActivityEvent's journey

Simulation → benchmark → avatar XP → quests. Paths are relative to
`src/neurocore/`; line numbers are as of this commit.

## 0. Setup: roles define what gets measured

`seed_roles()` (`seed.py:124`) writes one `RoleConfig` per entry in
`ROLE_PACKS` (`seed.py:16`), plus a `MetricDefinition` per metric tuple. Each
definition carries the metric's `layer` (volume / efficiency / quality /
behavioral), `direction`, `weight`, and whether it is the role's
`outcome_metric_key`. Nothing downstream hard-codes a vertical: every later
stage reads these rows (or a snapshot of them).

## 1. Ingestion: `simulate()` writes the fact table

`simulate()` (`simulation.py:12`) stands in for real integrations. It creates
`num_users` `User` rows for the role, gives each a fixed `skill` multiplier
(`simulation.py:40`), then for every day × metric writes one `ActivityEvent`
(`models.py:87`): `user_id`, `metric_key`, `value`, `timestamp`, `source`.
`value = _base_for(key) * skill * noise` (`_base_for`, `simulation.py:69`),
clamped by key name (`simulation.py:49-53`). Only metadata is stored: a number
per metric per day, no content.

## 2. Benchmark: top quartile of the role, by outcome

`compute_benchmark(role_slug, window_days, top_quantile)` (`benchmark.py:28`):

1. Loads the role's `MetricDefinition`s and `User`s, and every `ActivityEvent`
   newer than `cutoff` (`benchmark.py:45`), grouped by user.
2. Ranks users by `_user_outcome()` (`benchmark.py:24`), the sum of their
   outcome metric, and keeps the top `1 - top_quantile` share (`top_n`,
   `benchmark.py:57`; at least one user).
3. For each metric, `_daily_average()` (`benchmark.py:19`) gives each user
   `sum(values) / window_days`; the means over the top group and over the
   whole role become `top_performer` and `team_baseline`
   (`benchmark.py:78`), alongside the metric's layer, direction and weight.
4. Persists the snapshot as a `BenchmarkProfile` (`models.py:97`) whose
   `profile` JSON is self-contained.

`latest_benchmark(role_slug)` (`benchmark.py:103`) returns the newest snapshot.
Later stages read only this JSON, never `MetricDefinition` directly.

## 3. Avatar XP: one day of events against the snapshot

`apply_daily_xp(user_id, day_offset_days)` (`gamification.py:84`):

1. `_day_bounds()` (`gamification.py:76`) gives the UTC day; that user's
   `ActivityEvent`s in it are summed per `metric_key` into `daily`.
2. `compute_xp(role.slug, daily)` (`gamification.py:33`) fetches
   `latest_benchmark()` and, per metric, takes
   `_ratio(actual, top_performer, direction)` (`gamification.py:23`):
   `actual/target` or `target/actual` for lower-is-better, clamped to
   `[0, XP_CAP=2.0]`. XP is `BASE_XP (10) × weight × ratio`, so it is
   relative to the top quartile, never raw volume. Layers map to stats
   (`gamification.py:49-54`): volume + efficiency → wealth, quality → wisdom,
   behavioral → health.
3. Adds the result to the user's `Avatar` (`models.py:109`), creating it if
   missing: wealth and wisdom accumulate; health gains 10% of health XP,
   capped at 100 (`gamification.py:116`); `level = 1 + total_xp // 500`
   (`gamification.py:118`); momentum +2 per call.

`get_or_create_avatar()` (`gamification.py:64`) reads the avatar without
changing it.

## 4. Quests: the snapshot turned into targets

`generate_quests(user_id)` (`gamification.py:137`) reads the same
`latest_benchmark()` snapshot for the user's role. Each **volume** metric
becomes "Hit {top_performer} {label}" (wealth, `gamification.py:154`); each
**quality** metric becomes "Stay under/above {top_performer} on {label}"
(wisdom, `gamification.py:162`). Efficiency and behavioral metrics produce no
quests; one fixed break-taking health quest is always appended
(`gamification.py:169`). Quests do not read the user's own events, so every
user in a role gets the same list.

## Delivery surfaces

* CLI (`cli.py`): `cmd_loop` (`cli.py:66`) runs the whole chain:
  `seed_roles` → `simulate` (only if the DB has no users) →
  `compute_benchmark` → `apply_daily_xp` + `get_or_create_avatar` →
  `generate_quests`, for the first user.
* Slack (`slack_app.py`): `/neurocore-quests` and `/neurocore-avatar` map a
  Slack user via `_resolve()` (`slack_app.py:22`) and call the same functions.

## Where the architecture rules live today

* **Single fact table:** every stage reads `ActivityEvent`; there are no
  per-vertical tables.
* **Benchmark-relative XP:** enforced by `_ratio` and `XP_CAP`.
* **`privacy_floor`:** stored on `RoleConfig` but not yet checked by any
  read path.
