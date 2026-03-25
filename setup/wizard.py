#!/usr/bin/env python3
"""Interactive setup wizard for LinkedIn Autopilot.

Walks users through configuring their instance: business identity,
industry selection, content voice, case studies, schedule, API keys,
and dashboard settings. Generates all config files automatically.
"""

import os
import sys
import yaml
from pathlib import Path

from setup.validators import (
    validate_email,
    validate_url,
    validate_linkedin_url,
    validate_api_key,
)

# Resolve project root (parent of setup/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PRESETS_DIR = Path(__file__).resolve().parent / "industry_presets"
CONFIG_DIR = PROJECT_ROOT / "config"
ENV_FILE = PROJECT_ROOT / ".env"


# ── Helpers ──────────────────────────────────────────────────────────

def banner():
    print()
    print("=" * 60)
    print("   LinkedIn Autopilot  -  Setup Wizard")
    print("   AI-powered LinkedIn content machine")
    print("=" * 60)
    print()
    print("  This wizard will configure your instance in ~5 minutes.")
    print("  It generates config/business.yaml, content_calendar.yaml,")
    print("  influencers.yaml, trend_sources.yaml, and .env.")
    print()
    print("-" * 60)
    print()


def ask(prompt, default=None, validator=None, required=True):
    """Prompt user for input with optional default and validation."""
    while True:
        if default:
            raw = input(f"  {prompt} [{default}]: ").strip()
            if not raw:
                raw = default
        else:
            raw = input(f"  {prompt}: ").strip()

        if not raw and not required:
            return ""

        if not raw and required:
            print("    (required - please enter a value)")
            continue

        if validator and not validator(raw):
            print("    (invalid input - please try again)")
            continue

        return raw


def ask_choice(prompt, options, default=None):
    """Present numbered options and return the selection."""
    print(f"\n  {prompt}")
    for i, opt in enumerate(options, 1):
        marker = " *" if default and opt == default else ""
        print(f"    {i}. {opt}{marker}")

    while True:
        raw = input(f"\n  Enter number (1-{len(options)}): ").strip()
        if not raw and default:
            return default
        try:
            idx = int(raw)
            if 1 <= idx <= len(options):
                return options[idx - 1]
        except ValueError:
            pass
        print("    (invalid selection)")


def ask_yes_no(prompt, default=True):
    """Ask a yes/no question."""
    hint = "Y/n" if default else "y/N"
    raw = input(f"  {prompt} [{hint}]: ").strip().lower()
    if not raw:
        return default
    return raw in ("y", "yes")


def load_preset(name):
    """Load an industry preset YAML file."""
    filename = name.lower().replace(" ", "_").replace("/", "_") + ".yaml"
    filepath = PRESETS_DIR / filename
    if not filepath.exists():
        filepath = PRESETS_DIR / "default.yaml"
    with open(filepath, "r") as f:
        return yaml.safe_load(f)


def section(title):
    """Print a section header."""
    print()
    print(f"  {'─' * 50}")
    print(f"  {title}")
    print(f"  {'─' * 50}")
    print()


# ── Industry mapping ─────────────────────────────────────────────────

INDUSTRY_OPTIONS = [
    "SaaS / Tech Founder",
    "Agency Owner",
    "Coach / Consultant",
    "Realtor / Real Estate",
    "E-commerce / DTC",
    "Freelancer / Creator",
    "Custom / Other",
]

INDUSTRY_PRESET_MAP = {
    "SaaS / Tech Founder": "saas_founder",
    "Agency Owner": "agency_owner",
    "Coach / Consultant": "coach_consultant",
    "Realtor / Real Estate": "realtor",
    "E-commerce / DTC": "ecommerce",
    "Freelancer / Creator": "freelancer",
    "Custom / Other": "default",
}

TONE_OPTIONS = [
    "Professional",
    "Conversational",
    "Bold / Provocative",
    "Educational",
]

TIMEZONE_OPTIONS = [
    "US/Eastern",
    "US/Central",
    "US/Mountain",
    "US/Pacific",
    "Europe/London",
    "Europe/Berlin",
    "Asia/Tokyo",
    "Australia/Sydney",
    "UTC",
]


# ── Wizard Steps ─────────────────────────────────────────────────────

def step_business_identity():
    """Step 1: Collect business identity info."""
    section("1/8  BUSINESS IDENTITY")

    data = {}
    data["owner_name"] = ask("Your full name")
    data["business_name"] = ask("Business / brand name")
    data["brand"] = ask("Short brand handle (e.g. TenXVA, GrowthCo)")
    data["email"] = ask("Contact email", validator=validate_email)
    data["website"] = ask("Website URL", validator=validate_url, required=False)
    data["linkedin_url"] = ask(
        "LinkedIn profile URL",
        validator=validate_linkedin_url,
    )
    data["future_brand"] = ask(
        "Future brand name (if rebranding, or leave blank)",
        required=False,
    )
    return data


def step_industry():
    """Step 2: Select industry."""
    section("2/8  INDUSTRY")
    choice = ask_choice("Select your industry:", INDUSTRY_OPTIONS)
    preset_key = INDUSTRY_PRESET_MAP[choice]
    preset = load_preset(preset_key)
    print(f"\n    Loaded preset: {preset.get('industry', preset_key)}")
    return choice, preset_key, preset


def step_content_voice(preset):
    """Step 3: Configure content voice."""
    section("3/8  CONTENT VOICE")

    default_tone = preset.get("tone_defaults", {}).get("primary", "Conversational")
    tone = ask_choice("Primary tone:", TONE_OPTIONS, default=default_tone)

    description = ask(
        "Describe your voice in one sentence\n"
        "  (e.g. 'Direct, data-driven, no fluff')",
        default="Authoritative but approachable. Data-driven with real examples.",
    )

    perspective = ask(
        "Writing perspective",
        default="first_person",
    )

    return {
        "personality": description,
        "tone": tone.lower().replace(" / ", "_").replace(" ", "_"),
        "perspective": perspective,
    }


def step_case_studies():
    """Step 4: Add case studies (optional)."""
    section("4/8  CASE STUDIES (optional)")

    if not ask_yes_no("Add case studies to use in content?", default=True):
        return []

    studies = []
    for i in range(1, 4):
        print(f"\n  Case Study #{i}:")
        title = ask(f"  Title (or blank to stop)", required=False)
        if not title:
            break
        result = ask("  Key result (e.g. '3x revenue in 90 days')")
        context = ask("  One-line context", required=False)
        studies.append({
            "title": title,
            "result": result,
            "context": context or "",
        })

    return studies


def step_schedule():
    """Step 5: Configure posting schedule."""
    section("5/8  POSTING SCHEDULE")

    tz = ask_choice("Timezone:", TIMEZONE_OPTIONS, default="US/Eastern")
    posts_per_day = ask("Posts per day", default="2")
    posting_time = ask("Primary posting time (HH:MM, 24h)", default="07:30")

    article_days = ask(
        "Article days (comma-separated, e.g. tuesday,thursday)",
        default="tuesday,thursday",
    )
    newsletter_day = ask("Newsletter day", default="friday")

    return {
        "timezone": tz,
        "posts_per_day": int(posts_per_day),
        "posting_time": posting_time,
        "article_days": [d.strip().lower() for d in article_days.split(",")],
        "newsletter_day": newsletter_day.strip().lower(),
    }


def step_api_keys():
    """Step 6: Collect API keys."""
    section("6/8  API KEYS")

    print("  Anthropic API key is REQUIRED. All others are optional.")
    print("  (Keys are stored in .env -- never committed to git)\n")

    keys = {}
    keys["ANTHROPIC_API_KEY"] = ask(
        "Anthropic API Key (required)",
        validator=validate_api_key,
    )
    keys["OPENAI_API_KEY"] = ask(
        "OpenAI API Key (optional, for embeddings)",
        required=False,
    )
    keys["RESEND_API_KEY"] = ask(
        "Resend API Key (optional, for email digests)",
        required=False,
    )
    keys["PHANTOMBUSTER_API_KEY"] = ask(
        "PhantomBuster API Key (optional, for auto-posting)",
        required=False,
    )
    keys["SERPER_API_KEY"] = ask(
        "Serper API Key (optional, for web trend search)",
        required=False,
    )
    keys["LINKEDIN_PHANTOM_ID"] = ask(
        "PhantomBuster LinkedIn Poster Phantom ID (optional)",
        required=False,
    )

    return keys


def step_dashboard():
    """Step 7: Dashboard settings."""
    section("7/8  DASHBOARD")

    password = ask("Dashboard password", default="autopilot2026")
    port = ask("Dashboard port", default="8080")

    return {
        "password": password,
        "port": int(port),
    }


def step_positioning(identity, preset):
    """Step 8: Positioning (uses preset + customization)."""
    section("8/8  POSITIONING")

    template = preset.get("positioning_template", "")
    if template:
        print(f"  Preset positioning template:")
        print(f"    \"{template}\"")
        print()

    core_message = ask(
        "Your core positioning message\n"
        "  (one sentence: who you help + what outcome)",
        default=template if template else None,
    )

    unique_angle = ask(
        "What makes you different? (one sentence)",
        default="",
        required=False,
    )

    return {
        "core_message": core_message,
        "unique_angle": unique_angle,
    }


# ── File Generators ──────────────────────────────────────────────────

def generate_business_yaml(identity, positioning, voice, case_studies, preset):
    """Generate config/business.yaml."""
    config = {
        "business_name": identity["business_name"],
        "brand": identity["brand"],
        "owner_name": identity["owner_name"],
        "contact": {
            "email": identity["email"],
            "website": identity.get("website", ""),
            "linkedin": identity["linkedin_url"],
        },
        "future_brand": identity.get("future_brand", ""),
        "positioning": positioning,
        "primary_offer": {
            "product": f"{identity['brand']} Services",
            "price": "Custom",
            "description": f"Core offering from {identity['business_name']}",
        },
        "case_studies": case_studies if case_studies else preset.get("sample_case_studies", []),
        "voice": voice,
        "copywriter_dna_emphasis": [
            "Alex Hormozi - value stacking, grand slam offers",
            "Justin Welsh - solopreneur LinkedIn growth",
            "Dickie Bush - atomic essay framework",
            "Nicolas Cole - digital writing, category design",
            "Sahil Bloom - curiosity-driven frameworks",
            "Dan Koe - one-person business philosophy",
            "George Ten - fascinations and hooks",
            "Evaldo Albuquerque - big idea, belief shifting",
            "Gary Halbert - direct response, urgency",
        ],
        "content_philosophy": {
            "value_posts": 40,
            "authority_posts": 25,
            "engagement_posts": 20,
            "promotional_posts": 15,
        },
        "cta_philosophy": {
            "style": "soft",
            "rules": [
                "No hashtags ever",
                "No hard sells in feed posts",
                "Soft CTAs only: 'DM me X' or 'Comment Y for Z'",
                "Let value do the selling",
            ],
        },
        "linkedin_2026_rules": {
            "saves_over_likes": True,
            "carousel_priority": True,
            "newsletter_integration": True,
            "profile_alignment": "360_brew",
        },
        "content_themes": preset.get("content_themes", []),
        "target_audience": preset.get("target_audience", "Business professionals"),
    }
    return config


def generate_content_calendar(schedule):
    """Generate config/content_calendar.yaml."""
    config = {
        "timezone": schedule["timezone"],
        "content_phase": "growth",
        "daily_quotas": {
            "linkedin_posts": schedule["posts_per_day"],
            "articles": 0,
            "newsletters": 0,
        },
        "posting_slots": [
            {
                "time": schedule["posting_time"],
                "type": "primary",
                "days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
            },
        ],
        "article_days": schedule["article_days"],
        "newsletter_days": [schedule["newsletter_day"]],
        "retry_config": {
            "max_retries": 3,
            "retry_delay_minutes": 30,
            "backoff_multiplier": 2,
        },
        "format_styles": {
            "short_post": {"min_words": 50, "max_words": 200},
            "long_post": {"min_words": 200, "max_words": 500},
            "article": {"min_words": 800, "max_words": 2000},
            "carousel": {"slides": "5-10", "words_per_slide": "20-40"},
            "newsletter": {"min_words": 500, "max_words": 1500},
        },
    }
    return config


def generate_influencers(preset):
    """Generate config/influencers.yaml from preset."""
    influencers = preset.get("sample_influencers", [])
    config = {
        "influencers": influencers,
        "monitor_frequency": "daily",
        "extract_hooks": True,
        "extract_frameworks": True,
    }
    return config


def generate_trend_sources(preset):
    """Generate config/trend_sources.yaml from preset."""
    queries = preset.get("trend_search_queries", [])
    config = {
        "web_search_queries": queries,
        "scrape_urls": [],
        "linkedin_topics": preset.get("content_themes", []),
        "refresh_interval_hours": 12,
        "max_trends_per_cycle": 10,
    }
    return config


def generate_env(api_keys, dashboard):
    """Generate .env file."""
    lines = [
        "# LinkedIn Autopilot - Environment Variables",
        "# Generated by setup wizard",
        "",
        "# === API Keys ===",
    ]
    for key, value in api_keys.items():
        if value:
            lines.append(f"{key}={value}")
        else:
            lines.append(f"# {key}=")

    lines.extend([
        "",
        "# === Dashboard ===",
        f"DASHBOARD_PASSWORD={dashboard['password']}",
        f"DASHBOARD_PORT={dashboard['port']}",
        "",
        "# === Notification Email (optional) ===",
        "# NOTIFICATION_EMAIL=you@example.com",
    ])
    return "\n".join(lines) + "\n"


# ── Main Wizard ──────────────────────────────────────────────────────

def run_wizard():
    """Run the full interactive setup wizard."""
    banner()

    # Step 1: Business identity
    identity = step_business_identity()

    # Step 2: Industry selection
    industry_name, preset_key, preset = step_industry()

    # Step 3: Content voice
    voice = step_content_voice(preset)

    # Step 4: Case studies
    case_studies = step_case_studies()

    # Step 5: Posting schedule
    schedule = step_schedule()

    # Step 6: API keys
    api_keys = step_api_keys()

    # Step 7: Dashboard
    dashboard = step_dashboard()

    # Step 8: Positioning
    positioning = step_positioning(identity, preset)

    # ── Generate files ───────────────────────────────────────────────
    section("GENERATING CONFIGURATION FILES")

    # Ensure config/ exists
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # business.yaml
    biz_config = generate_business_yaml(
        identity, positioning, voice, case_studies, preset
    )
    biz_path = CONFIG_DIR / "business.yaml"
    with open(biz_path, "w") as f:
        yaml.dump(biz_config, f, default_flow_style=False, sort_keys=False)
    print(f"    Created {biz_path}")

    # content_calendar.yaml
    cal_config = generate_content_calendar(schedule)
    cal_path = CONFIG_DIR / "content_calendar.yaml"
    with open(cal_path, "w") as f:
        yaml.dump(cal_config, f, default_flow_style=False, sort_keys=False)
    print(f"    Created {cal_path}")

    # influencers.yaml
    inf_config = generate_influencers(preset)
    inf_path = CONFIG_DIR / "influencers.yaml"
    with open(inf_path, "w") as f:
        yaml.dump(inf_config, f, default_flow_style=False, sort_keys=False)
    print(f"    Created {inf_path}")

    # trend_sources.yaml
    trend_config = generate_trend_sources(preset)
    trend_path = CONFIG_DIR / "trend_sources.yaml"
    with open(trend_path, "w") as f:
        yaml.dump(trend_config, f, default_flow_style=False, sort_keys=False)
    print(f"    Created {trend_path}")

    # .env
    env_content = generate_env(api_keys, dashboard)
    with open(ENV_FILE, "w") as f:
        f.write(env_content)
    print(f"    Created {ENV_FILE}")

    # ── Summary ──────────────────────────────────────────────────────
    print()
    print("=" * 60)
    print("   SETUP COMPLETE")
    print("=" * 60)
    print()
    print(f"  Business:   {identity['business_name']}")
    print(f"  Brand:      {identity['brand']}")
    print(f"  Industry:   {industry_name}")
    print(f"  Tone:       {voice['tone']}")
    print(f"  Schedule:   {schedule['posts_per_day']} posts/day at {schedule['posting_time']} {schedule['timezone']}")
    print(f"  Dashboard:  port {dashboard['port']}")
    print()
    print("  Generated files:")
    print(f"    config/business.yaml")
    print(f"    config/content_calendar.yaml")
    print(f"    config/influencers.yaml")
    print(f"    config/trend_sources.yaml")
    print(f"    .env")
    print()
    print("-" * 60)
    print("  NEXT STEPS:")
    print("-" * 60)
    print()
    print("  1. Review your config files in config/")
    print("  2. Add any additional case studies to config/business.yaml")
    print("  3. Customize influencers in config/influencers.yaml")
    print("  4. Start the pipeline:")
    print()
    print("     python -m linkedin_autopilot.main")
    print()
    print("  5. Open the dashboard:")
    print(f"     http://localhost:{dashboard['port']}")
    print()
    print("  For Docker deployment:")
    print("     docker-compose up -d")
    print()
    print("=" * 60)
    print()
