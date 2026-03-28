# CHANGELOG.md -- LinkedIn Autopilot

All notable changes to this project are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [2.0.0] -- 2026-03-26

### Added -- Engagement Engine
- **Auto Commenter agent** -- Generates strategic comments on tracked influencer posts 2x daily (10 AM + 4 PM). Six comment formulas: yes-and, data drop, contrarian add, smart question, brief story, tool insight.
- **Auto Responder agent** -- Monitors comments on your posts every 2 hours. Classifies comment types (supportive, question, experience, disagreement, thoughtful, generic, spam) and generates tailored replies.
- **Lead detection system** -- Dual detection (AI analysis + keyword matching) flags buying signals in comments without changing reply tone. Configurable lead signals in `business.yaml`.
- **4-layer quality gates** -- AI quality scoring (4 dimensions, min 7.0/10), invisible test, forbidden phrase detection, and lead filter. All automated engagement must pass all four layers.

### Added -- Self-Learning Loop
- **Campaign Analyzer agent** -- Runs weekly (Sunday 8 PM). Calculates health score (0-100), identifies top/bottom performers, runs pattern recognition across content types, themes, hooks, and timing.
- **Automatic strategy updates** -- Learning agent recommends changes to content mix, themes, formats, hooks, and CTAs based on actual engagement data. Max 10% swing per week, max 5 changes per cycle.
- **Performance reports** -- Saved to `data/reports/` with strategy updates in `data/reports/strategy_update_*.json`.

### Added -- Browser Automation
- **Airtop integration** -- Cloud-hosted browser sessions with anti-detection, residential proxy rotation, and LinkedIn session persistence for production use.
- **Browser Use integration** -- Local AI-powered browser agent using natural language instructions for development and debugging.
- **Humanized timing** -- Random delays between keystrokes and actions to mimic human behavior.
- **Rate limiting** -- 5 comments/hour, 10 replies/hour, 20 DMs/day (configurable).
- **Dry run mode** -- Enabled by default. Generates and logs all engagement without posting to LinkedIn.

### Added -- New Prompts
- `auto_commenter.md` -- Strategic influencer comment generation with quality scoring.
- `auto_responder.md` -- Comment reply generation with classification and lead detection.
- `campaign_analyzer.md` -- Weekly performance analysis with health scoring.
- `reply_composer.md` -- Reply drafting system.
- `smart_replier.md` -- Intelligent reply generation.
- `strategic_commenter.md` -- Comment strategy.
- `scoring_fact_checker.md` -- Scored fact verification.

### Added -- Engagement Scheduler
- `scheduler_engagement.py` -- Registers all engagement engine jobs (v1 outreach + v2 engagement + learning).
- Outreach team with engagement cycle, peekaboo sequences, daily connections, email triggers, recurring engagement.
- Messaging bot for trigger-based connection sequences.

### Added -- Swipe Library Expansion
- **Copywriter Council** -- 18 agents with 59 sub-agents for deep pattern analysis.
- Expanded from 9 to 18 tracked authors (7832 canonical entries).
- New authors: Eugene Schwartz, Jay Abraham, Jon Buchan, Lead Gen Jay, Liam Ottley, Todd Brown, Tom Bilyeu, Perry Marshall, Joe Sugarman, Ken McCarthy, Fred Catona, Greg Renker, Dan Kennedy, Gary Bencivenga, Gordon Grossman.

### Added -- Infrastructure
- **Speaker/Thought Leader** industry preset (8th preset).
- Data directories for engagement tracking: `data/comments/`, `data/replies/`, `data/leads/`, `data/reports/`, `data/analytics/`.

### Changed
- Content quality gates upgraded from basic to 4-layer system.
- Engagement quality gates now require explicit scoring on all four dimensions.
- Scheduler now reads timezone dynamically from config (Rule 50 compliance).

---

## [1.0.0] -- Initial Release

### Added -- Content Engine
- **Trend Analyst** -- Scans web sources, influencer feeds, and news. Surfaces 6-10 actionable content angles per day categorized by content mix.
- **Post Writer** -- Writes one LinkedIn post per day using Mueller Storytelling Framework. Format rotation across story-driven, big idea, behind the curtain, framework/system, and blog-style.
- **Quality Editor** -- Reviews all content with Mueller checklist, voice/tone check, specificity stack verification, CTA audit, formatting check, and AI detection avoidance. Scores 0-100.
- **Fact Checker** -- Verifies claims, numbers, and tool references.
- **Human Touch Checker** -- Scans for AI-generated patterns.

### Added -- Influencer Intelligence
- **Influencer Scraper** -- Daily scraping of tracked influencer LinkedIn feeds.
- **Influencer Analyzer** -- Analyzes influencer content for trends and patterns.
- **Lead Extractor** -- Identifies potential leads from influencer post engagement.

### Added -- Publishing Pipeline
- **Auto-Poster** -- Posts approved content via PhantomBuster or browser automation.
- **Content Dashboard** -- Web UI on port 8080 for reviewing and approving content.
- **Email Digests** -- Daily digest via Resend with content for review.

### Added -- Swipe Library (v1)
- 9 copywriter codexes: Hormozi, Halbert, Ogilvy, Albuquerque, George Ten, Justin Welsh, Dickie Bush, Nicolas Cole, Dan Koe.
- Style analysis profiles per author.
- Swipe Strategist agent for DNA matching.

### Added -- Configuration
- Setup wizard (`setup.py`) with 7 industry presets.
- YAML-based config system with documented examples.
- `.env`-based secrets management.

### Added -- Deployment
- Docker support with `docker-compose.yml` and `Dockerfile`.
- Systemd service support for server deployment.
- APScheduler-based cron system with configurable timezone.

### Added -- Governance
- 52 operational rules in `rules/RULES.md`.
- Anti-slop writing protocol baked into all prompts.
- Anti-hallucination protocol for agent behavior.
