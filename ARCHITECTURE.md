# ARCHITECTURE.md -- LinkedIn Autopilot V2

> System architecture for the multi-agent LinkedIn content and engagement pipeline.

---

## System Overview

LinkedIn Autopilot V2 is a fully autonomous LinkedIn pipeline built around two parallel engines -- a **Content Engine** that researches, writes, edits, and publishes posts, and an **Engagement Engine** that comments on influencer posts, replies to your audience, detects leads, and learns from performance data. A **Self-Learning Loop** closes the feedback gap between what gets published and what gets planned next.

```
                         +-------------------+
                         |     main.py       |
                         | (entry point)     |
                         +--------+----------+
                                  |
                    +-------------+-------------+
                    |                           |
           +--------v--------+        +---------v---------+
           |  scheduler.py   |        | scheduler_engage  |
           |  (content jobs) |        | ment.py           |
           +-----------------+        | (engage + learn)  |
                    |                 +-------------------+
                    |                          |
      +----+----+---+---+         +-----------+-----------+
      |    |    |       |         |           |           |
   Content Infl. Profile Auto    Outreach  v2 Engage  Campaign
   Team   Team  Team   Poster   Team      Team       Analyzer
```

---

## Core Components

### 1. Entry Point (`main.py`)

Two operating modes:

- **Production mode**: Starts the APScheduler blocking loop, registers all cron jobs from `scheduler.py` and `scheduler_engagement.py`, and launches the content review dashboard on port 8080.
- **Manual mode** (`--run <team>`): Runs a single team once for testing. Supports `content`, `influencer`, `leads`, `engagement`, `comments`, `profile`, and `all`.

Environment check on boot validates `ANTHROPIC_API_KEY` (required) and warns on missing optional keys (Firecrawl, Apify, PhantomBuster, Retriever).

### 2. BaseAgent (`agents/base.py`)

Every agent inherits from `BaseAgent`, which provides:

- **Prompt loading with template rendering** -- Reads `.md` files from `prompts/`, substitutes `{{owner_name}}`, `{{brand}}`, `{{business_name}}`, and other Jinja-style variables from `config/business.yaml`.
- **Claude API client** -- Initializes `anthropic.Anthropic()` with model from `CLAUDE_MODEL` env var (default: `claude-sonnet-4-20250514`).
- **Config resolution** -- Checks `config/` first, falls back to `config_examples/`. YAML loading, JSON I/O, and data directory helpers.

### 3. Agent Teams (`teams/`)

| Team File | Agents Orchestrated | Schedule |
|---|---|---|
| `content_team.py` | Trend Analyst, Post Writer, Quality Editor, Swipe Strategist | Daily 5:30 AM |
| `influencer_team.py` | Influencer Scraper, Influencer Analyzer, Lead Extractor | Daily 6:00 AM + 2:00 PM |
| `engagement_team.py` | Auto Commenter, Auto Responder, Smart Replier | Every 2 hours + 2x daily |
| `profile_team.py` | Profile Optimizer | 1st of month, 9:00 AM |
| `outreach_team.py` | Engagement Cycle, Peekaboo Sequences, Daily Connections, Email Triggers | Various (v1 outreach) |

---

## The Content Pipeline

The content pipeline runs daily and flows through four stages:

```
Stage 1: RESEARCH          Stage 2: CREATE           Stage 3: QUALITY         Stage 4: PUBLISH
+------------------+       +-----------------+       +-----------------+      +-----------------+
| Trend Analyst    | ----> | Post Writer     | ----> | Quality Editor  | ---> | Auto-Poster     |
| Article Research |       | Longform Writer |       | Fact Checker    |      | Dashboard       |
| Newsletter Rsrch |       | Swipe Strategist|       | Human Touch Chk |      | Email Digest    |
+------------------+       +-----------------+       +-----------------+      +-----------------+
```

### Stage 1: Research (5:30 AM)

- **Trend Analyst** (`prompts/trend_analyst.md`) -- Scans scraped web data from Serper/Firecrawl and surfaces 6-10 actionable content angles categorized by the content mix (40% pure value, 25% use cases, 20% industry insight, 15% business).
- **Article Researcher** (`prompts/article_researcher.md`) -- Deep-dives into specific topics for long-form content.
- **Newsletter Researcher** (`prompts/newsletter_researcher.md`) -- Curates material for LinkedIn newsletters.

### Stage 2: Creation

- **Post Writer** (`prompts/post_writer.md`) -- Drafts one LinkedIn post per day using the Mueller Storytelling Framework. Applies format rotation (story-driven, big idea, behind the curtain, framework/system, blog-style). Output is structured JSON with content mix category, format style, copywriter DNA applied, and specificity stack.
- **Longform Writer** (`prompts/longform_writer.md`) -- Writes articles (1000-1500 words) and newsletters (800-1200 words).
- **Swipe Strategist** (`prompts/swipe_strategist.md`) -- Selects and applies patterns from the swipe library. Matches copywriter DNA to the topic and format.

### Stage 3: Quality Control

- **Quality Editor** (`prompts/quality_editor.md`) -- Reviews ALL content with a 10-point checklist: Mueller storytelling check, voice/tone alignment, specificity stack verification, CTA audit, formatting check, AI detection avoidance. Scores 0-100 with penalties for markdown artifacts (-5), AI-telltale phrases (-3), missing contractions (-2). Returns APPROVED or REJECTED with specific edits.
- **Fact Checker** (`prompts/fact_checker.md`, `scoring_fact_checker.md`) -- Verifies claims, numbers, and tool references.
- **Human Touch Checker** (`prompts/human_touch_checker.md`) -- Scans for AI-generated patterns and rewrites to sound human.

### Stage 4: Publishing

- **Auto-Poster** (`tools/auto_poster.py`) -- Checks the posting queue every 15 minutes (7 AM-10 PM). Posts via PhantomBuster API or browser automation.
- **Dashboard** (`tools/dashboard.py`) -- Web UI on port 8080 for reviewing, approving, and editing queued content.
- **Email Notifier** (`tools/email_notifier.py`) -- Sends daily digest via Resend at 7:00 AM.

---

## The Engagement Engine

### Auto Commenter (`agents/engagement/auto_commenter.py`)

Runs 2x daily (10 AM + 4 PM). Generates strategic comments on tracked influencer posts using six formulas:

1. **Yes-And** -- Build on their specific point with added experience.
2. **Data Drop** -- Share a relevant metric from direct work.
3. **Contrarian Add** -- Respectful pushback with counter-example.
4. **Smart Question** -- Ask something only a practitioner would think of.
5. **Brief Story** -- One-sentence anecdote, one-sentence lesson.
6. **Tool Insight** -- Share a specific workflow or technique.

Quality gates (all must pass):
- 4-dimension scoring (relevance, voice, substance, specificity) -- minimum average 7.0/10
- Invisible test -- would someone with zero context still find this person smart?
- Forbidden phrase detection -- configurable blocklist, no self-promotion
- Rate limiting -- max 3 comments per influencer per week

### Auto Responder (`agents/engagement/auto_responder.py`)

Runs every 2 hours (7:30 AM - 9:30 PM). For each new comment on your posts:

1. **Classify** -- supportive, question, experience, disagreement, thoughtful, generic, spam
2. **Generate** -- Tailored reply matched to comment type
3. **Quality-gate** -- Minimum score 7/10
4. **Lead detect** -- Dual detection: AI analysis + keyword matching
5. **Skip** -- Generic one-word comments and spam filtered out

Lead signals are configurable in `business.yaml` under `engagement.auto_responding.lead_signals`.

### Engagement Cycle (v1 Legacy)

- **Outreach Team** (`teams/outreach_team.py`) -- Engagement cycle (every 2hrs), Peekaboo 7-day sequences (daily 8 AM), daily connection requests (11 AM), email triggers (9 AM), recurring engagement (Tue/Fri).
- **Messaging Bot** (`tools/messaging_bot.py`) -- Processes new connections, runs trigger-based sequences every 30 min.

---

## The Self-Learning Loop

### Campaign Analyzer (`agents/learning/campaign_analyzer.py`)

Runs weekly, Sunday at 8:00 PM. Closes the feedback loop between publishing and planning:

```
Create content --> Measure performance --> Analyze patterns --> Adjust strategy --> Repeat
```

**Analysis framework:**
1. Collect and normalize metrics (saves weighted 40%, comments 30%, engagement rate 20%, consistency 10%)
2. Identify top 20% performers -- extract replicable elements
3. Identify bottom 20% -- diagnose failures (topic, hook, format, timing)
4. Cross-reference dimensions -- which theme+format combos win?
5. Generate strategy adjustments -- content mix changes, max 10% swing per week

**Outputs:**
- Health score (0-100) with A+ through D grades
- Top/bottom performer analysis with concrete takeaways
- Pattern recognition across content types, themes, hooks, timing
- Strategy adjustments (max 5 changes per week to avoid overload)
- Experiments with hypotheses and success metrics

Reports saved to `data/reports/`, strategy updates to `data/reports/strategy_update_*.json`.

---

## The Swipe Library System

The swipe library is a 28MB+ curated copywriting pattern database from 18 legendary direct-response copywriters.

### Structure

```
swipe_library/
  codex/                      # Author-specific pattern codexes
    alex_hormozi/             # Value stacking, grand slam offers
    bill_mueller/             # Storytelling, narrative selling (1382 entries)
    brian_kurtz/              # Direct response, relationship building
    jay_abraham/              # Strategy, leverage, growth
    jon_buchan/               # Cold email, personality-driven outreach (2528 entries)
    lead_gen_jay/             # Lead generation, B2B outbound
    liam_ottley/              # AI agencies, automation
    todd_brown/               # Funnels, mechanisms, E5 method (1228 entries)
    tom_bilyeu/               # Mindset, motivation
  council/                    # Copywriter Council (18 agents, 59 sub-agents)
  swipe_compact.json          # Compressed lookup table
  swipe_database.json         # Full database (7832 canonical entries)
  style_analysis.json         # Per-author style traits
  swipe_file_agent_context.json  # Agent-readable context map
```

### How Agents Use It

The agents do NOT copy these writers. The system works in three layers:

1. **Style Analysis** -- Each author has extracted style traits (tone, sentence length, hook patterns, CTA style, persuasion techniques).
2. **Pattern Matching** -- The Swipe Strategist matches the current topic and format to the most appropriate author DNA.
3. **Voice Synthesis** -- The Post Writer applies the matched patterns while maintaining the owner's authentic voice. The `copywriter_dna_applied` field in output tracks which author influenced each post.

The Mueller Storytelling Framework is the primary writing system, with other author patterns layered in for hooks, frameworks, and persuasion structure.

---

## Scheduler Architecture

Two scheduler files register jobs with APScheduler:

### `scheduler.py` (Content + Core Jobs)

| Job | Schedule | Grace Time |
|---|---|---|
| Content Production | Daily 5:30 AM | 1 hour |
| Influencer Scrape | Daily 6:00 AM | 1 hour |
| Lead Extraction | Daily 2:00 PM | 1 hour |
| Engagement Loop | Every 2hrs, 7AM-9PM | 30 min |
| Strategic Commenting | 10:00 AM + 4:00 PM | 1 hour |
| Auto-Poster | Every 15 min, 7AM-10PM | 15 min |
| Monthly Profile Audit | 1st of month, 9:00 AM | 24 hours |

### `scheduler_engagement.py` (Engagement + Learning Jobs)

| Job | Schedule | Grace Time |
|---|---|---|
| Engagement Cycle (v1) | Every 2hrs, 7:15AM-9:15PM | 15 min |
| Peekaboo Sequences | Daily 8:00 AM | 1 hour |
| Email Triggers | Daily 9:00 AM | 1 hour |
| Daily Connections | Daily 11:00 AM | 1 hour |
| Recurring Engagement | Tue+Fri 1:00 PM | 1 hour |
| Messaging Bot | Every 30 min, 7AM-10PM | 10 min |
| Auto Commenter (v2) | 10:00 AM + 4:00 PM | 30 min |
| Auto Responder (v2) | Every 2hrs, 7:30AM-9:30PM | 15 min |
| Campaign Analyzer (v2) | Sunday 8:00 PM | 2 hours |

All jobs read timezone dynamically from `config/content_calendar.yaml` (Rule 50 compliance). Misfire grace times ensure jobs run even if the system was briefly down.

---

## Browser Automation

Two backends for LinkedIn interaction:

### Airtop (Cloud -- Production)
Cloud-hosted sessions with anti-detection, residential proxy rotation, and LinkedIn session persistence. Set `BROWSER_BACKEND=airtop` and `AIRTOP_API_KEY`.

### Browser Use (Local -- Development)
AI-powered local browser agent using natural language instructions. Set `BROWSER_BACKEND=browser_use` and `OPENAI_API_KEY`.

Both backends are wrapped by `tools/browser_automation.py` which provides:
- Humanized timing (random delays between keystrokes)
- Rate limiting (5 comments/hour, 10 replies/hour, 20 DMs/day)
- Dry run mode (default: enabled)
- Full action logging to `data/comments/` and `data/replies/`

---

## Configuration System

### Config Resolution Order

All agents use `BaseAgent._find_config()` which checks:
1. `config/<filename>.yaml` (user-generated, gitignored)
2. `config_examples/<filename>.example.yaml` (documented defaults, committed)

### Config Files

| File | Purpose | Key Sections |
|---|---|---|
| `business.yaml` | Business identity, voice, positioning, case studies | `engagement.auto_commenting`, `engagement.auto_responding`, `lead_signals` |
| `content_calendar.yaml` | Schedule, formats, posting slots, timezone | `schedule.timezone`, `content_mix`, `format_rotation` |
| `influencers.yaml` | Who to monitor, commenting strategy | `commenting_strategy`, `influencer_list` |
| `trend_sources.yaml` | Web queries, scrape targets | `serper_queries`, `firecrawl_targets` |

### Setup Wizard (`setup.py` + `setup/`)

Interactive wizard with 8 industry presets (SaaS, Agency, Coach, Realtor, E-commerce, Freelancer, Speaker, Custom). Generates all config files from templates in `setup/industry_presets/`.

---

## Docker Deployment

```yaml
# docker-compose.yml
services:
  autopilot:
    build: .                    # Python 3.12-slim base
    ports: ["8080:8080"]        # Dashboard
    env_file: [.env]            # API keys
    volumes:
      - ./config:/app/config    # Config persistence
      - ./data:/app/data        # Data persistence
    restart: unless-stopped
```

The Dockerfile installs system dependencies for Pillow (image generation), creates runtime data directories, and runs `python main.py` as the entrypoint.

---

## Data Flow

```
External Sources                Internal Processing              Outputs
+------------------+           +--------------------+           +------------------+
| Serper (web)     |           | data/trend-intel/  |           | LinkedIn Posts   |
| Firecrawl (scrape|  ------>  | data/briefs/       |  ------>  | LinkedIn Comments|
| LinkedIn (posts) |           | data/drafts/       |           | LinkedIn Replies |
| Influencer feeds |           | data/posting-queue/ |           | Email Digests    |
+------------------+           | data/published/    |           | Lead Alerts      |
                               | data/analytics/    |           | Weekly Reports   |
                               | data/comments/     |           +------------------+
                               | data/replies/      |
                               | data/leads/        |
                               | data/reports/      |
                               +--------------------+
```

---

## Prompt System

18 prompt files in `prompts/`, each a Markdown template with `{{variable}}` placeholders:

| Prompt | Agent Role | Key Responsibility |
|---|---|---|
| `post_writer.md` | Content creation | Mueller framework, format rotation, voice alignment |
| `quality_editor.md` | Quality control | 10-point checklist, scoring, APPROVED/REJECTED |
| `trend_analyst.md` | Research | 6-10 angles per day, specificity stack, content mix |
| `auto_commenter.md` | Engagement | 6 comment formulas, 4-dimension scoring, invisible test |
| `auto_responder.md` | Engagement | Comment classification, lead detection, tailored replies |
| `campaign_analyzer.md` | Learning | Health score, pattern recognition, strategy updates |
| `swipe_strategist.md` | Content | Copywriter DNA matching, pattern selection |
| `longform_writer.md` | Content | Articles (1000-1500w), newsletters (800-1200w) |
| `article_researcher.md` | Research | Deep-dive topic research |
| `newsletter_researcher.md` | Research | Newsletter material curation |
| `fact_checker.md` | Quality | Claim verification |
| `human_touch_checker.md` | Quality | AI detection avoidance |
| `profile_optimizer.md` | Profile | Monthly LinkedIn profile audit |
| `authority_checker.md` | Quality | Authority positioning verification |
| `reply_composer.md` | Engagement | Reply drafting |
| `smart_replier.md` | Engagement | Intelligent reply generation |
| `strategic_commenter.md` | Engagement | Comment strategy |
| `scoring_fact_checker.md` | Quality | Scored fact verification |

---

## Integration Points

| Integration | Tool File | Purpose | Required? |
|---|---|---|---|
| Anthropic Claude | `agents/base.py` | All AI generation | Yes |
| PhantomBuster | `tools/auto_poster.py` | Auto-posting to LinkedIn | No |
| Serper | (trend research) | Web search for trends | No |
| Firecrawl | (scraping) | Website content extraction | No |
| Resend | `tools/email_notifier.py` | Email digest delivery | No |
| Airtop | `tools/browser_automation.py` | Cloud browser sessions | No |
| Browser Use | `tools/browser_automation.py` | Local AI browser agent | No |
| Apify | (data extraction) | LinkedIn data scraping | No |
| OpenAI | (embeddings) | Deduplication via embeddings | No |
| Airtable | `tools/airtable_client.py` | Data storage integration | No |
| Pillow | `tools/ai_image_generator.py` | Post image generation | No |
