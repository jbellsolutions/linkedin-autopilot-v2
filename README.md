# LinkedIn Autopilot v2 -- Content + Engagement + Learning

**AI-powered LinkedIn content and engagement machine. 40+ agents. 5 teams + engagement engine + self-learning loop. Built-in swipe file from 9 legendary copywriters. Zero to autopilot in 5 minutes.**

LinkedIn Autopilot v2 is a fully autonomous LinkedIn pipeline that researches trends, writes posts in your voice, comments strategically on influencer posts, replies to your audience, detects leads, and learns from its own performance to get better every week. It does not post generic AI slop. It studies the DNA of the best copywriters who ever lived, engages like a real human, and continuously optimizes based on data.

---

## What is New in v2

### Engagement Engine
v2 adds an autonomous engagement system that runs alongside content creation:

- **Auto Commenter** -- Generates strategic comments on tracked influencer posts. Quality-gated with a 4-dimension scoring system and an "invisible test" that catches any hint of self-promotion.
- **Auto Responder** -- Monitors comments on your posts and replies with substance. Classifies comment types (supportive, question, experience, disagreement, thoughtful) and tailors each reply. Flags high-intent leads automatically.

### Self-Learning Loop
v2 closes the feedback loop between publishing and planning:

- **Campaign Analyzer** -- Runs weekly analysis of content performance. Calculates a health score, identifies top performers and underperformers, and generates concrete strategy adjustments with expected impact.
- **Automatic Strategy Updates** -- The learning agent recommends changes to content mix, themes, formats, hooks, and CTAs based on actual engagement data.

### Quality Gates
Every piece of automated engagement passes through multiple quality gates:

1. **AI Quality Scoring** -- 4-dimension scoring (relevance, voice alignment, substance, specificity) with configurable minimum thresholds.
2. **Invisible Test** -- Would someone who knows nothing about your business still think you are smart and worth following?
3. **Forbidden Phrase Detection** -- Configurable blocklist prevents promotional language from ever appearing in comments.
4. **Lead Detection** -- AI + keyword-based dual detection flags buying signals without changing reply tone.

---

## v1 vs v2 Comparison

| Feature | v1 (Content) | v2 (Content + Engagement) |
|---|---|---|
| AI content generation | Yes | Yes |
| Trend scouting | Yes | Yes |
| Influencer monitoring | Yes | Yes |
| Auto-posting | Yes | Yes |
| Email digests | Yes | Yes |
| Strategic commenting on influencer posts | No | Yes (2x daily, quality-gated) |
| Auto-replying to comments on your posts | No | Yes (every 2hrs, lead detection) |
| Lead flagging from comments | No | Yes (AI + keyword dual detection) |
| Weekly performance analysis | No | Yes (health score + strategy updates) |
| Content strategy self-optimization | No | Yes (data-driven recommendations) |
| Industry presets | 7 | 8 (added Speaker/Thought Leader) |
| Engagement quality gates | Basic | 4-layer (scoring + invisible test + blocklist + lead filter) |

---

## Quick Start

### Option A: Docker (Recommended)

```bash
git clone https://github.com/yourorg/linkedin-autopilot.git
cd linkedin-autopilot
python setup.py          # Interactive wizard generates all config
docker-compose up -d     # Start the pipeline
```

### Option B: Local Install

```bash
git clone https://github.com/yourorg/linkedin-autopilot.git
cd linkedin-autopilot
pip install -r requirements.txt
python setup.py          # Interactive wizard
python -m linkedin_autopilot.main   # Start the pipeline
```

Your dashboard will be live at `http://localhost:8080`.

---

## How It Works

LinkedIn Autopilot v2 runs two parallel engines:

```
CONTENT ENGINE                    ENGAGEMENT ENGINE

TREND SCOUTS        CREATORS      AUTO COMMENTER     AUTO RESPONDER
  Monitor web    ->  Write     ->  Comment on          Reply to your
  Track influencers  Match voice   influencer posts    audience comments
  Surface topics     Apply hooks   Quality-gated       Detect leads

         QUALITY CONTROL          CAMPAIGN ANALYZER
           Score & refine           Weekly performance
           Check alignment          Strategy updates
           Enforce rules            Feedback loop

         PUBLISHING TEAM
           Queue approved
           Auto-post
           Retry failures
```

**The daily cycle:**

1. **5:30 AM** - Trend scouts scan web sources, influencer feeds, and news
2. **6:00 AM** - Content creators draft posts using trends + your voice config
3. **6:30 AM** - Quality control scores, refines, and queues content
4. **7:00 AM** - Dashboard email digest sent for your review
5. **7:30 AM** - Approved content auto-posts to LinkedIn
6. **10:00 AM** - Auto Commenter posts strategic comments on influencer posts (batch 1)
7. **Every 2hrs** - Auto Responder checks for new comments and replies
8. **4:00 PM** - Auto Commenter posts strategic comments (batch 2)
9. **Sunday 8 PM** - Campaign Analyzer runs weekly performance review

---

## The Swipe File Library

LinkedIn Autopilot ships with a 28MB curated library of copywriting patterns, hooks, frameworks, and structures from 9 legendary direct-response copywriters:

| Copywriter | What the Agents Learn |
|---|---|
| Alex Hormozi | Value stacking, grand slam offers, lead magnets |
| Gary Halbert | Direct response, urgency, storytelling |
| David Ogilvy | Headlines, brand voice, long-form persuasion |
| Evaldo Albuquerque | Big idea development, belief shifting |
| George Ten | Fascinations, hooks, curiosity gaps |
| Justin Welsh | LinkedIn-native growth, solopreneur systems |
| Dickie Bush | Atomic essays, frameworks, consistency |
| Nicolas Cole | Category design, digital writing |
| Dan Koe | One-person business philosophy |

The agents do not copy these writers. They study the underlying patterns and apply them to your voice and your topics.

---

## Engagement Engine Details

### Auto Commenter

The Auto Commenter generates strategic comments on tracked influencer posts twice daily (10 AM and 4 PM). Every comment passes through:

1. **Generation** -- Claude generates a comment using one of 6 formulas (yes_and, data_drop, contrarian, question, story, tool_insight)
2. **Quality scoring** -- 4 dimensions scored 0-10 (relevance, voice alignment, substance, specificity). Must average above threshold (default: 7)
3. **Invisible test** -- Scans for promotional language and forbidden phrases
4. **Rate limiting** -- Max 3 comments per influencer per week

Configured in `business.yaml` under `engagement.auto_commenting` and `influencers.yaml` under `commenting_strategy`.

### Auto Responder

The Auto Responder monitors comments on your posts every 2 hours and:

1. **Classifies** each comment (supportive, question, experience, disagreement, thoughtful, generic, spam)
2. **Generates** a tailored reply matched to the comment type
3. **Quality-gates** the reply (minimum score: 7/10)
4. **Flags leads** using dual detection (AI analysis + keyword matching)
5. **Skips** generic one-word comments and spam

Lead signals are configurable in `business.yaml` under `engagement.auto_responding.lead_signals`.

### Campaign Analyzer

Runs every Sunday evening and produces:

- **Health score** (0-100) weighted by saves (40%), comments (30%), engagement rate (20%), consistency (10%)
- **Top/bottom performer analysis** with replicable elements and fixes
- **Pattern recognition** across content types, themes, hooks, and timing
- **Strategy adjustments** with concrete content mix changes
- **Experiments to run** with hypotheses and success metrics

Reports are saved to `data/reports/` and strategy updates to `data/reports/strategy_update_*.json`.

---

## Browser Automation

The engagement engine uses browser automation to interact with LinkedIn directly -- scraping influencer posts, posting comments, reading replies, and collecting engagement metrics. Two backends are available:

### Airtop (Cloud -- Recommended for Production)

Airtop provides cloud-hosted browser sessions with anti-detection, residential proxy rotation, and LinkedIn session persistence. Best for reliable, scaled operation.

1. Sign up at [airtop.ai](https://www.airtop.ai/)
2. Set `AIRTOP_API_KEY` in your `.env`
3. Set `BROWSER_BACKEND=airtop` in `.env`
4. Log into LinkedIn once through the Airtop dashboard to establish the session

### Browser Use (Local -- Good for Development)

Browser Use is an AI-powered local browser agent that navigates LinkedIn autonomously using natural language instructions. Best for debugging and complex flows.

1. Install: `pip install browser-use langchain-openai`
2. Set `OPENAI_API_KEY` (or `BROWSER_USE_API_KEY`) in your `.env`
3. Set `BROWSER_BACKEND=browser_use` in `.env`
4. Ensure a Chromium browser is available locally

### Safety and Configuration

- **Dry run mode** is enabled by default (`dry_run: true` in `config/business.yaml` or `config_examples/business.example.yaml`). The agents will generate comments and replies but will not post them to LinkedIn until you set `dry_run: false`.
- **Rate limiting** is built in: 5 comments/hour, 10 replies/hour, 20 DMs/day (configurable under `browser.rate_limit`).
- **Humanized timing**: Random delays between keystrokes and actions to mimic human behavior.
- All browser actions are logged. Check `data/comments/` and `data/replies/` for full records.

---

## Features at a Glance

| Feature | Required API Key | Without It |
|---|---|---|
| AI content generation | Anthropic (required) | N/A |
| Auto-commenting | Anthropic (required) | N/A |
| Auto-responding | Anthropic (required) | N/A |
| Campaign analysis | Anthropic (required) | N/A |
| Web trend scouting | Serper (optional) | Uses LinkedIn-only trends |
| Influencer monitoring | None | Always active |
| Auto-posting to LinkedIn | PhantomBuster (optional) | Manual posting via dashboard |
| Email digests | Resend (optional) | Dashboard-only review |
| Embedding-based dedup | OpenAI (optional) | Basic text similarity |
| Content dashboard | None | Always active |
| Browser automation (Airtop) | Airtop (optional) | Manual posting; no live scraping |
| Browser automation (Browser Use) | OpenAI (optional) | Manual posting; no live scraping |

---

## Configuration

The setup wizard (`python setup.py`) generates all config files automatically. You can also create them manually using the examples in `config_examples/`.

| File | Purpose |
|---|---|
| `config/business.yaml` | Business identity, voice, positioning, case studies, **engagement settings** |
| `config/content_calendar.yaml` | Schedule, formats, posting slots |
| `config/influencers.yaml` | Who to monitor, **commenting strategy** |
| `config/trend_sources.yaml` | Web queries and scrape targets |
| `.env` | API keys and secrets (never committed) |

See `config_examples/` for fully documented example files with comments explaining every field.

---

## Industry Presets

The setup wizard includes 8 industry presets that pre-configure content themes, influencer lists, trend queries, tone defaults, and engagement settings:

| Preset | Best For |
|---|---|
| **SaaS / Tech Founder** | Software companies, developer tools, B2B tech |
| **Agency Owner** | Marketing agencies, creative shops, consultancies |
| **Coach / Consultant** | Executive coaches, business consultants, trainers |
| **Realtor** | Real estate agents, investors, property managers |
| **E-commerce / DTC** | Online stores, direct-to-consumer brands, Shopify |
| **Freelancer / Creator** | Solo practitioners, content creators, writers |
| **Speaker / Thought Leader** | Keynote speakers, authors, public intellectuals |
| **Custom / Other** | General business (fully customizable) |

Each preset includes curated influencer lists, search queries, sample case studies, tone recommendations, and engagement defaults specific to that industry.

---

## Architecture

```
linkedin-autopilot-v2/
├── setup.py                    # Setup wizard entry point
├── setup/
│   ├── wizard.py               # Interactive configuration wizard
│   ├── validators.py           # Input validation helpers
│   └── industry_presets/       # 8 industry YAML presets
├── config/                     # Generated config (gitignored)
│   ├── business.yaml           # + engagement section (v2)
│   ├── content_calendar.yaml
│   ├── influencers.yaml        # + commenting_strategy (v2)
│   └── trend_sources.yaml
├── config_examples/            # Documented example configs
├── agents/
│   ├── base.py                 # BaseAgent foundation class
│   ├── influencer/             # Influencer monitoring agents
│   ├── engagement/             # v2: Auto-commenting + auto-responding
│   │   ├── auto_commenter.py   # Strategic influencer commenting
│   │   └── auto_responder.py   # Comment reply + lead detection
│   └── learning/               # v2: Self-learning agents
│       └── campaign_analyzer.py # Weekly performance analysis
├── teams/                      # Agent team orchestrators
├── tools/                      # Integrations (Airtable, email, browser, etc.)
│   ├── browser_automation.py   # v2: Airtop + Browser Use LinkedIn automation
├── prompts/                    # Agent system prompts (template-rendered)
│   ├── auto_commenter.md       # v2: Commenting agent prompt
│   ├── auto_responder.md       # v2: Reply agent prompt
│   └── campaign_analyzer.md    # v2: Analysis agent prompt
├── swipe_library/              # 28MB copywriter pattern library
├── data/
│   ├── comments/               # v2: Generated comment logs
│   ├── replies/                # v2: Reply cycle logs
│   ├── leads/                  # v2: Flagged lead records
│   ├── reports/                # v2: Weekly analysis reports
│   └── analytics/              # v2: Performance metric snapshots
├── scheduler.py                # Content pipeline scheduler
├── scheduler_engagement.py     # Engagement + learning scheduler (v2 updated)
├── main.py                     # Pipeline orchestrator
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env                        # API keys (gitignored)
```

---

## API Keys Guide

| Key | Provider | What It Enables | Required? |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | [Anthropic](https://console.anthropic.com/) | All AI generation + engagement | Yes |
| `OPENAI_API_KEY` | [OpenAI](https://platform.openai.com/) | Embedding-based deduplication | No |
| `SERPER_API_KEY` | [Serper](https://serper.dev/) | Web search for trend scouting | No |
| `RESEND_API_KEY` | [Resend](https://resend.com/) | Email digest delivery | No |
| `PHANTOMBUSTER_API_KEY` | [PhantomBuster](https://phantombuster.com/) | Auto-posting to LinkedIn | No |
| `LINKEDIN_PHANTOM_ID` | PhantomBuster | Specific phantom for posting | No |
| `AIRTOP_API_KEY` | [Airtop](https://www.airtop.ai/) | Cloud browser automation (recommended) | No |
| `BROWSER_USE_API_KEY` | Browser Use | Local AI browser agent | No |

LinkedIn Autopilot works with just the Anthropic key. Every other integration is optional and gracefully degrades.

---

## Deployment

**Local development:**
```bash
python -m linkedin_autopilot.main
```

**Docker (production):**
```bash
docker-compose up -d
```

**Server deployment:**
```bash
# Uses systemd service
sudo systemctl start linkedin-autopilot
sudo systemctl enable linkedin-autopilot
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

**Built for people who would rather build their business than spend 2 hours a day writing LinkedIn posts and commenting on everyone else's.**
