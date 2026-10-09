from __future__ import annotations

from sqlmodel import select

from .db import session_scope
from .models import (
    Archetype,
    Direction,
    MetricDefinition,
    MetricLayer,
    PrivacyFloor,
    RoleConfig,
)


ROLE_PACKS: list[dict] = [
    {
        "slug": "mid_market_sdr",
        "name": "Mid-Market SDR",
        "archetype": Archetype.VOLUME_DRIVEN,
        "outcome_metric_key": "meetings_booked",
        "description": "Outbound sales development rep.",
        "segmentation_keys": ["tenure", "territory"],
        "privacy_floor": PrivacyFloor.AGGREGATE_ONLY,
        "metrics": [
            ("calls_per_day", "Calls per day", MetricLayer.VOLUME, Direction.HIGHER_IS_BETTER, 1.0, "Salesforce"),
            ("emails_per_day", "Emails per day", MetricLayer.VOLUME, Direction.HIGHER_IS_BETTER, 0.8, "Outreach"),
            ("linkedin_touches_per_day", "LinkedIn touches/day", MetricLayer.VOLUME, Direction.HIGHER_IS_BETTER, 0.5, "LinkedIn"),
            ("connect_rate", "Connect rate", MetricLayer.EFFICIENCY, Direction.HIGHER_IS_BETTER, 2.0, "Salesforce"),
            ("meeting_rate", "Meeting-booked rate", MetricLayer.EFFICIENCY, Direction.HIGHER_IS_BETTER, 2.5, "Salesforce"),
            ("talk_listen_ratio", "Talk-to-listen ratio", MetricLayer.QUALITY, Direction.LOWER_IS_BETTER, 1.5, "Gong"),
            ("follow_up_hours", "Follow-up lag (hrs)", MetricLayer.QUALITY, Direction.LOWER_IS_BETTER, 1.0, "Salesforce"),
            ("meetings_booked", "Meetings booked", MetricLayer.VOLUME, Direction.HIGHER_IS_BETTER, 3.0, "Salesforce"),
        ],
    },
    {
        "slug": "software_engineer",
        "name": "Software Engineer",
        "archetype": Archetype.FLOW_DRIVEN,
        "outcome_metric_key": "deployment_frequency",
        "description": "DORA-aligned engineering role.",
        "segmentation_keys": ["tenure", "team"],
        "privacy_floor": PrivacyFloor.OPT_IN_INDIVIDUAL,
        "metrics": [
            ("prs_opened", "PRs opened", MetricLayer.VOLUME, Direction.HIGHER_IS_BETTER, 1.0, "GitHub"),
            ("prs_reviewed", "PRs reviewed", MetricLayer.VOLUME, Direction.HIGHER_IS_BETTER, 1.0, "GitHub"),
            ("cycle_time_hours", "Cycle time (hrs)", MetricLayer.EFFICIENCY, Direction.LOWER_IS_BETTER, 2.0, "Linear"),
            ("review_turnaround_hours", "Review turnaround (hrs)", MetricLayer.EFFICIENCY, Direction.LOWER_IS_BETTER, 1.5, "GitHub"),
            ("change_failure_rate", "Change failure rate", MetricLayer.QUALITY, Direction.LOWER_IS_BETTER, 2.0, "GitHub"),
            ("deep_work_blocks", "Deep work blocks", MetricLayer.BEHAVIORAL, Direction.HIGHER_IS_BETTER, 1.5, "Calendar"),
            ("deployment_frequency", "Deployment frequency", MetricLayer.VOLUME, Direction.HIGHER_IS_BETTER, 2.5, "GitHub"),
        ],
    },
    {
        "slug": "product_manager",
        "name": "Product Manager",
        "archetype": Archetype.FLOW_DRIVEN,
        "outcome_metric_key": "features_shipped",
        "description": "Product management role.",
        "segmentation_keys": ["tenure", "product_line"],
        "privacy_floor": PrivacyFloor.AGGREGATE_ONLY,
        "metrics": [
            ("specs_written", "Specs written", MetricLayer.VOLUME, Direction.HIGHER_IS_BETTER, 1.0, "Notion"),
            ("user_interviews", "User interviews", MetricLayer.VOLUME, Direction.HIGHER_IS_BETTER, 1.5, "Calendar"),
            ("cycle_time_days", "Cycle time (days)", MetricLayer.EFFICIENCY, Direction.LOWER_IS_BETTER, 2.0, "Jira"),
            ("adoption_rate", "Feature adoption rate", MetricLayer.EFFICIENCY, Direction.HIGHER_IS_BETTER, 2.5, "Analytics"),
            ("stakeholder_nps", "Stakeholder NPS", MetricLayer.QUALITY, Direction.HIGHER_IS_BETTER, 2.0, "Survey"),
            ("features_shipped", "Features shipped", MetricLayer.VOLUME, Direction.HIGHER_IS_BETTER, 3.0, "Jira"),
        ],
    },
    {
        "slug": "management_consultant",
        "name": "Management Consultant",
        "archetype": Archetype.DELIVERABLE_DRIVEN,
        "outcome_metric_key": "engagements_delivered",
        "description": "Consulting role. Utilization framed as self-awareness.",
        "segmentation_keys": ["tenure", "practice"],
        "privacy_floor": PrivacyFloor.SELF_ONLY,
        "metrics": [
            ("deliverables_completed", "Deliverables completed", MetricLayer.VOLUME, Direction.HIGHER_IS_BETTER, 1.5, "SharePoint"),
            ("utilization_pct", "Utilization %", MetricLayer.EFFICIENCY, Direction.HIGHER_IS_BETTER, 1.0, "Harvest"),
            ("revision_cycles", "Revision cycles", MetricLayer.QUALITY, Direction.LOWER_IS_BETTER, 2.0, "Docs"),
            ("client_nps", "Client NPS", MetricLayer.QUALITY, Direction.HIGHER_IS_BETTER, 2.5, "Survey"),
            ("deadline_buffer_days", "Deadline buffer (days)", MetricLayer.BEHAVIORAL, Direction.HIGHER_IS_BETTER, 1.5, "Calendar"),
            ("engagements_delivered", "Engagements delivered", MetricLayer.VOLUME, Direction.HIGHER_IS_BETTER, 3.0, "CRM"),
        ],
    },
    {
        "slug": "financial_analyst",
        "name": "Financial Analyst",
        "archetype": Archetype.DELIVERABLE_DRIVEN,
        "outcome_metric_key": "reports_delivered",
        "description": "Finance/analyst role. Accuracy weighted above volume.",
        "segmentation_keys": ["tenure", "desk"],
        "privacy_floor": PrivacyFloor.SELF_ONLY,
        "metrics": [
            ("models_built", "Models built", MetricLayer.VOLUME, Direction.HIGHER_IS_BETTER, 1.0, "Excel"),
            ("close_cycle_days", "Close cycle (days)", MetricLayer.EFFICIENCY, Direction.LOWER_IS_BETTER, 2.0, "NetSuite"),
            ("accuracy_rate", "Accuracy rate", MetricLayer.QUALITY, Direction.HIGHER_IS_BETTER, 3.0, "Audit"),
            ("revision_cycles", "Revision cycles", MetricLayer.QUALITY, Direction.LOWER_IS_BETTER, 1.5, "Docs"),
            ("deep_work_blocks", "Deep work blocks", MetricLayer.BEHAVIORAL, Direction.HIGHER_IS_BETTER, 1.5, "Calendar"),
            ("reports_delivered", "Reports delivered", MetricLayer.VOLUME, Direction.HIGHER_IS_BETTER, 2.5, "BI"),
        ],
    },
    {
        "slug": "university_student",
        "name": "University Student",
        "archetype": Archetype.DELIVERABLE_DRIVEN,
        "outcome_metric_key": "assignments_completed",
        "description": "Higher-ed student. Original B2C use case.",
        "segmentation_keys": ["year", "major"],
        "privacy_floor": PrivacyFloor.SELF_ONLY,
        "metrics": [
            ("study_blocks", "Study blocks", MetricLayer.VOLUME, Direction.HIGHER_IS_BETTER, 1.0, "Calendar"),
            ("assignments_submitted", "Assignments submitted", MetricLayer.VOLUME, Direction.HIGHER_IS_BETTER, 2.0, "Canvas"),
            ("late_submissions", "Late submissions", MetricLayer.QUALITY, Direction.LOWER_IS_BETTER, 2.5, "Canvas"),
            ("focus_minutes", "Focus minutes", MetricLayer.BEHAVIORAL, Direction.HIGHER_IS_BETTER, 1.5, "Focus"),
            ("assignments_completed", "Assignments completed", MetricLayer.VOLUME, Direction.HIGHER_IS_BETTER, 3.0, "Canvas"),
        ],
    },
]


def seed_roles() -> None:
    with session_scope() as session:
        for pack in ROLE_PACKS:
            existing = session.exec(
                select(RoleConfig).where(RoleConfig.slug == pack["slug"])
            ).first()
            if existing:
                continue

            role = RoleConfig(
                slug=pack["slug"],
                name=pack["name"],
                archetype=pack["archetype"],
                outcome_metric_key=pack["outcome_metric_key"],
                description=pack["description"],
                segmentation_keys=pack["segmentation_keys"],
                privacy_floor=pack["privacy_floor"],
            )
            session.add(role)
            session.flush()

            for key, label, layer, direction, weight, source in pack["metrics"]:
                session.add(
                    MetricDefinition(
                        role_config_id=role.id,
                        key=key,
                        label=label,
                        layer=layer,
                        direction=direction,
                        weight=weight,
                        source_api=source,
                        is_primary_outcome=(key == pack["outcome_metric_key"]),
                    )
                )
