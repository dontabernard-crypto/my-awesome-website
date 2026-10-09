# NeuroCore

Horizontal executive-function + performance platform.
One core engine, swappable RoleConfig packs per vertical
(SDR, Engineering, PM, Consulting, Finance, Student).

## Architecture rules

* `ActivityEvent` is the single fact table. Every integration writes here.
* Add a new vertical = add a RoleConfig + MetricDefinitions. Never fork the engine.
* Benchmarking is always relative to a RoleConfig's top-quartile performers.
* Privacy: respect `RoleConfig.privacy_floor` at query time. Never expose
  individual data when floor is AGGREGATE_ONLY.
* XP is benchmark-relative, never raw volume.

## Stack

* Python 3.11+, SQLModel, SQLite (dev) / Postgres (prod)
* Slack Bolt for delivery surface
* FastAPI for API layer (not yet built)
* No external services required for the demo loop

## Commands

* `pip install -e ".[dev]"`
* `neurocore loop --role mid_market_sdr --users 20 --days 60`
* `pytest`

## What NOT to do

* Do not gamify lines of code, commit count, or raw PR count.
* Do not gamify billable hours as a punitive target.
* Do not store call transcripts, email bodies, or Slack message content.
* Do not show individual metrics to managers when privacy_floor is AGGREGATE_ONLY.
* Do not refactor `ActivityEvent` into per-vertical tables.
