# GEMINI.md -- LinkedIn Autopilot V2 (Google Gemini / AI Studio Context)

> Context file for Google Gemini, AI Studio, and other LLM-based tools working on this codebase.

---

## Project Summary

LinkedIn Autopilot V2 is a fully autonomous LinkedIn content and engagement pipeline. It uses 40+ AI agents organized into 5 teams to research trends, generate posts, engage with influencer content, respond to audiences, and learn from performance data.

**Stack**: Python 3.11+, Docker, Anthropic Claude API, APScheduler, browser automation (Airtop/Browser Use).

---

## Repository Structure

```
linkedin-autopilot-v2/
  main.py                  # Entry point (scheduler or manual team runs)
  scheduler.py             # Content pipeline cron jobs
  scheduler_engagement.py  # Engagement pipeline cron jobs
  agents/
    base.py                # BaseAgent -- all agents inherit this
    engagement/            # Auto Commenter, Auto Responder
    influencer/            # Scraper, Analyzer
    learning/              # Campaign Analyzer
  teams/
    content_team.py        # Orchestrates content agents
    engagement_team.py     # Orchestrates engagement agents
    profile_team.py        # Profile optimization
  prompts/                 # 18 markdown prompt files for agents
  tools/                   # Browser automation, Airtable, image gen, email
  config_examples/         # Template configs (committed)
  config/                  # Runtime configs (gitignored)
  skills/                  # 8 Claude Code skills
  swipe_library/           # Content inspiration database
  infrastructure/          # Deployment configs
```

---

## Key Files to Read First

1. `CLAUDE.md` -- Operational rules (52 rules + session protocols)
2. `AGENTS.md` -- Full agent registry with teams, prompts, and data flow
3. `ARCHITECTURE.md` -- Detailed system architecture and pipeline flow
4. `main.py` -- Entry point, environment validation
5. `agents/base.py` -- BaseAgent class all agents inherit from
6. `requirements.txt` -- Python dependencies

---

## Important Conventions

- **Config**: Runtime config lives in `config/` (gitignored). Templates in `config_examples/`.
- **Prompts**: All agent prompts are markdown files in `prompts/`. They use Jinja-style `{{variable}}` substitution from `config/business.yaml`.
- **Model**: Default Claude model is `claude-sonnet-4-20250514`, set via `CLAUDE_MODEL` env var.
- **Testing**: Use `python main.py --run <team>` for manual testing. Teams: `content`, `influencer`, `engagement`, `comments`, `profile`, `all`.
- **No hardcoded timezones**: Timezones come from config dynamically.
- **No duplicate posts**: Embedding-based deduplication is enforced.

---

## Security Constraints

- LinkedIn cookies are sensitive credentials -- never log or commit them.
- API keys live in `.env` (gitignored). See `.env.example` for the full list.
- No unauthorized cron job testing. Use `--dry-run` first.
- Browser automation sessions must be properly closed to avoid leaked sessions.

---

## What NOT to Do

- Do not bypass the quality pipeline (Quality Editor + Fact Checker).
- Do not increase engagement frequency without explicit approval (LinkedIn rate limits).
- Do not hardcode business persona details -- they belong in `config/business.yaml`.
- Do not commit anything in `config/`, `data/`, or `.env`.
