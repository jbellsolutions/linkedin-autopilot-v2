# LinkedIn Autopilot v2 — Setup Walkthrough

> **To install:** Open Claude Code in this folder and type `set this up for me` or `/walkthrough`

Claude Code will read this repo's actual files and walk you through every step interactively — the configuration wizard, industry preset selection, Airtop cookie setup, and getting all 40+ agents running.

---

## What This Repo Does

A fully autonomous LinkedIn content and engagement pipeline. 40+ agents across 5 teams: Trend Scouts, Content Creators, Quality Control, Engagement Engine, and Self-Learning Analytics. Posts content in your voice using a configurable copywriter DNA blend, comments strategically on influencer posts (2x daily, 4-layer quality-gated), replies to comments on your posts with lead detection, and runs weekly performance analysis with automatic strategy updates. Zero to autopilot in 5 minutes with Docker.

---

## Prerequisites

- **Python 3.10+** — `python3 --version` (for local install)
- **Docker + Docker Compose** — `docker --version` (recommended)
- **Anthropic API key** — runs all 40+ agents
- **Airtop account** — LinkedIn browser automation (requires cookies/session)
- **LinkedIn account** — the profile being grown
- **Industry preset** — choose from 8: Tech, Marketing, Sales, HR/Recruiting, Finance, Healthcare, Startup/Founder, Speaker/Thought Leader

---

## Environment Variables

The interactive wizard (`python setup.py`) generates your `config/` files automatically. You'll need to provide:

| Value | What It Is | Where to Get It |
|-------|-----------|-----------------|
| `ANTHROPIC_API_KEY` | Claude API key — runs all agents | console.anthropic.com → API Keys |
| `AIRTOP_API_KEY` | LinkedIn browser sessions | portal.airtop.ai |
| LinkedIn session cookies | Auth for LinkedIn automation | Export from your browser (Airtop handles this) |
| Your name + company | Populates voice profile | You know this |
| Industry preset | Configures content strategy | Choose from 8 options in the wizard |
| LinkedIn profile URL | The account being grown | Your LinkedIn URL |

---

## Quick Setup

### Option A: Docker (Recommended)

```bash
# 1. Run the interactive configuration wizard
python setup.py

# 2. Start all agents
docker compose up -d

# 3. View the dashboard
open http://localhost:8080
```

### Option B: Local Install

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the configuration wizard
python setup.py

# 3. Start the pipeline
python -m linkedin_autopilot.main
```

---

## Configuration Wizard (What It Asks)

`python setup.py` walks you through:

1. **Business profile** — name, company, industry, value proposition
2. **Industry preset** — selects content themes, influencers, tone
3. **Voice profile** — copywriter DNA blend (default: balanced mix)
4. **Engagement settings** — which influencers to track, comment frequency
5. **Posting schedule** — days/times, content mix (educational/story/engagement)
6. **Quality thresholds** — minimum scores for content and comments

Output: `config/business.yaml`, `config/content_calendar.yaml`, `config/influencers.yaml`, `config/trend_sources.yaml`

---

## The 4-Layer Quality Gate (No Low-Quality Output Ships)

Every piece of automated engagement passes:
1. **AI Quality Score** — 4 dimensions: relevance, voice alignment, substance, specificity (configurable minimum)
2. **Invisible Test** — "Would someone who knows nothing about your business think you're smart and worth following?"
3. **Forbidden Phrase Detection** — blocks any promotional language in comments
4. **Lead Detection** — flags buying signals without changing reply tone

---

## Key Commands

| Command | What It Does |
|---------|-------------|
| `python setup.py` | Interactive configuration wizard |
| `docker compose up -d` | Start all agents (detached) |
| `docker compose logs -f` | Watch agent logs |
| `docker compose down` | Stop all agents |
| `pip install -r requirements.txt` | Install dependencies (local install) |
| `python -m linkedin_autopilot.main` | Start pipeline locally |
| `open http://localhost:8080` | View dashboard |

---

## What Runs Automatically (After Setup)

| Frequency | What Happens |
|-----------|-------------|
| Daily | Trend Scouts research new content angles |
| Daily (2x) | Auto-Commenter posts on tracked influencer posts (quality-gated) |
| Every 2 hours | Auto-Responder checks and replies to comments on your posts |
| Per schedule | Content Creators write and publish posts in your voice |
| Weekly | Campaign Analyzer reviews performance and updates strategy |

---

*This file was deployed by [AGI-1](https://github.com/jbellsolutions/agi-1) — the self-healing, self-learning AI development framework.*
