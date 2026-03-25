"""
Engagement Scheduler — adds engagement machine jobs to the existing APScheduler.

Import this from scheduler.py or main.py to add the engagement jobs.

Usage:
    from scheduler_engagement import add_engagement_jobs
    add_engagement_jobs(scheduler)
"""

import logging
import yaml
from pathlib import Path
from apscheduler.triggers.cron import CronTrigger

from teams.outreach_team import (
    run_engagement_cycle,
    run_peekaboo_sequences,
    run_daily_connections,
    run_email_triggers,
    run_recurring_engagement,
)
from tools.messaging_bot import run_messaging_cycle

# v2 agents
from agents.engagement.auto_commenter import AutoCommenter
from agents.engagement.auto_responder import AutoResponder
from agents.learning.campaign_analyzer import CampaignAnalyzer

logger = logging.getLogger(__name__)


def _load_timezone() -> str:
    """Read timezone from content_calendar.yaml, fallback to America/New_York."""
    for config_dir in ("config", "config_examples"):
        path = Path(__file__).parent / config_dir / "content_calendar.yaml"
        if path.exists():
            try:
                with open(path) as f:
                    cal = yaml.safe_load(f) or {}
                tz = cal.get("timezone") or cal.get("schedule", {}).get("timezone")
                if tz:
                    return tz
            except Exception:
                pass
    return "America/New_York"


# ------------------------------------------------------------------
# v2 job runners
# ------------------------------------------------------------------

def run_auto_commenter():
    """Run the auto-commenting agent. Called by scheduler."""
    logger.info("[scheduler] running auto_commenter")
    agent = AutoCommenter()
    return agent.run()


def run_auto_responder():
    """Run the auto-responder agent. Called by scheduler."""
    logger.info("[scheduler] running auto_responder")
    agent = AutoResponder()
    return agent.run()


def run_campaign_analyzer():
    """Run the weekly campaign analyzer. Called by scheduler."""
    logger.info("[scheduler] running campaign_analyzer")
    agent = CampaignAnalyzer()
    return agent.run()


# ------------------------------------------------------------------
# Main scheduler registration
# ------------------------------------------------------------------

def add_engagement_jobs(scheduler):
    """
    Add all engagement engine jobs to an existing APScheduler instance.
    Call this from your main scheduler setup.
    """
    tz = _load_timezone()

    # ═══════════════════════════════════════════════════════════════
    # v1 JOBS (Outreach + Messaging)
    # ═══════════════════════════════════════════════════════════════

    # ─── Engagement Cycle (replaces old engagement_loop for Unipile) ───
    # Every 2 hours, 7 AM - 9 PM ET
    # Scans posts -> replies to comments -> enriches profiles -> starts sequences
    scheduler.add_job(
        run_engagement_cycle,
        CronTrigger(hour="7,9,11,13,15,17,19,21", minute=15, timezone=tz),
        id="engagement_cycle",
        name="Engagement Cycle (monitor + reply + enrich + sequence)",
        misfire_grace_time=900,
        replace_existing=True,
    )

    # ─── Peekaboo Sequences — Daily 8 AM ──────────────────────────────
    # Processes all active 7-day LinkedIn sequences
    scheduler.add_job(
        run_peekaboo_sequences,
        CronTrigger(hour=8, minute=0, timezone=tz),
        id="peekaboo_sequences",
        name="7-Day Peekaboo Sequences",
        misfire_grace_time=3600,
        replace_existing=True,
    )

    # ─── Daily Connections — 11 AM ────────────────────────────────────
    # Sends top 5 connection requests per day
    scheduler.add_job(
        run_daily_connections,
        CronTrigger(hour=11, minute=0, timezone=tz),
        id="daily_connections",
        name="Daily Connection Requests (Top 5)",
        misfire_grace_time=3600,
        replace_existing=True,
    )

    # ─── Email Triggers — Daily 9 AM ─────────────────────────────────
    # Fires outreach emails for 7-day-old non-responders
    scheduler.add_job(
        run_email_triggers,
        CronTrigger(hour=9, minute=0, timezone=tz),
        id="email_triggers",
        name="Email Outreach Triggers",
        misfire_grace_time=3600,
        replace_existing=True,
    )

    # ─── Recurring Engagement — Tue + Fri 1 PM ───────────────────────
    # Checks engager DB for recent posts, likes + comments
    scheduler.add_job(
        run_recurring_engagement,
        CronTrigger(day_of_week="tue,fri", hour=13, minute=0, timezone=tz),
        id="recurring_engagement",
        name="Recurring Engagement (Tue/Fri)",
        misfire_grace_time=3600,
        replace_existing=True,
    )

    # ─── Messaging Bot — Every 30 min, 7 AM - 10 PM ────────────────
    # Checks for new connections with triggers, processes sequences
    scheduler.add_job(
        run_messaging_cycle,
        CronTrigger(hour="7-22", minute="*/30", timezone=tz),
        id="messaging_bot",
        name="Messaging Bot (triggers + sequences)",
        misfire_grace_time=600,
        replace_existing=True,
    )

    # ═══════════════════════════════════════════════════════════════
    # v2 JOBS (Auto-Commenting + Auto-Responding + Campaign Learning)
    # ═══════════════════════════════════════════════════════════════

    # ─── Auto Commenter — 2x Daily: 10 AM + 4 PM ─────────────────
    # Generates and posts strategic comments on influencer posts.
    # Morning batch catches overnight posts; afternoon batch catches
    # midday posts while they still have momentum.
    scheduler.add_job(
        run_auto_commenter,
        CronTrigger(hour="10,16", minute=0, timezone=tz),
        id="auto_commenter",
        name="Auto Commenter (influencer comments, 2x daily)",
        misfire_grace_time=1800,
        replace_existing=True,
    )

    # ─── Auto Responder — Every 2 hrs, 7 AM - 9 PM ───────────────
    # Monitors comments on your posts and generates quality replies.
    # Also flags high-intent leads for follow-up.
    scheduler.add_job(
        run_auto_responder,
        CronTrigger(hour="7,9,11,13,15,17,19,21", minute=30, timezone=tz),
        id="auto_responder",
        name="Auto Responder (reply to comments, every 2hrs)",
        misfire_grace_time=900,
        replace_existing=True,
    )

    # ─── Campaign Analyzer — Weekly, Sunday 8 PM ─────────────────
    # Analyzes the past week of content performance, generates a
    # report with health score, and produces strategy adjustments
    # for the coming week.
    scheduler.add_job(
        run_campaign_analyzer,
        CronTrigger(day_of_week="sun", hour=20, minute=0, timezone=tz),
        id="campaign_analyzer",
        name="Campaign Analyzer (weekly strategy update)",
        misfire_grace_time=7200,
        replace_existing=True,
    )

    # ═══════════════════════════════════════════════════════════════
    # Logging summary
    # ═══════════════════════════════════════════════════════════════

    logger.info("Engagement engine jobs added to scheduler:")
    logger.info("  v1 (Outreach):")
    logger.info("    Engagement Cycle: every 2hrs, 7:15AM-9:15PM")
    logger.info("    Peekaboo Sequences: daily 8:00AM")
    logger.info("    Email Triggers: daily 9:00AM")
    logger.info("    Daily Connections: daily 11:00AM")
    logger.info("    Recurring Engagement: Tue+Fri 1:00PM")
    logger.info("    Messaging Bot: every 30min, 7AM-10PM")
    logger.info("  v2 (Engagement + Learning):")
    logger.info("    Auto Commenter: 10:00AM + 4:00PM daily")
    logger.info("    Auto Responder: every 2hrs, 7:30AM-9:30PM")
    logger.info("    Campaign Analyzer: Sunday 8:00PM (weekly)")
