# AGENTS.md -- LinkedIn Autopilot V2 Agent Registry

> Canonical map of every AI agent, its role, team membership, and prompt file.
> Updated: 2026-03-28

---

## Architecture Overview

LinkedIn Autopilot V2 runs **40+ agents** organized into **5 teams**, orchestrated by two schedulers:
- `scheduler.py` -- Content pipeline (daily content generation)
- `scheduler_engagement.py` -- Engagement pipeline (commenting, responding, learning)

All agents inherit from `agents/base.py:BaseAgent`, which provides prompt loading, Claude API access, and config resolution.

---

## Team 1: Content Team (`teams/content_team.py`)

**Schedule**: Daily 5:30 AM
**Purpose**: Research trends, generate posts, enforce quality, prepare for publishing.

| Agent | Prompt File | Role | Input | Output |
|-------|------------|------|-------|--------|
| Trend Analyst | `prompts/trend_analyst.md` | Scans web data for 6-10 content angles by content mix (40% value, 25% use cases, 20% industry, 15% business) | Serper/Firecrawl data | Content angles JSON |
| Article Researcher | `prompts/article_researcher.md` | Deep-dives into topics for long-form content | Topic from Trend Analyst | Research brief |
| Newsletter Researcher | `prompts/newsletter_researcher.md` | Curates newsletter-worthy findings | Web data | Newsletter draft |
| Post Writer | `prompts/post_writer.md` | Writes LinkedIn posts from research | Research brief + content angles | Draft post |
| Longform Writer | `prompts/longform_writer.md` | Writes LinkedIn articles/carousels | Research brief | Long-form draft |
| Swipe Strategist | `prompts/swipe_strategist.md` | Adapts swipe-file patterns to current topics | Swipe library + topic | Adapted post |
| Quality Editor | `prompts/quality_editor.md` | Edits for clarity, engagement, brand voice | Draft post | Edited post |
| Fact Checker | `prompts/fact_checker.md` | Validates claims and sources | Edited post | Pass/fail + corrections |
| Scoring Fact Checker | `prompts/scoring_fact_checker.md` | Numeric quality scoring with detailed rubric | Edited post | Score 0-100 + breakdown |
| Human Touch Checker | `prompts/human_touch_checker.md` | Detects AI-sounding patterns, ensures authenticity | Post | Pass/fail + suggestions |
| Authority Checker | `prompts/authority_checker.md` | Verifies author has credibility to make claims | Post + profile | Pass/fail |

---

## Team 2: Engagement Team (`teams/engagement_team.py`)

**Schedule**: Every 2 hours + 2x daily
**Purpose**: Comment on relevant posts, reply to audience, detect leads.

| Agent | Prompt File | Role | Input | Output |
|-------|------------|------|-------|--------|
| Auto Commenter | `prompts/auto_commenter.md` | Posts strategic comments on influencer content | Influencer posts | Comments |
| Strategic Commenter | `prompts/strategic_commenter.md` | Crafts high-value comments for visibility | Target posts | Strategic comments |
| Auto Responder | `prompts/auto_responder.md` | Replies to comments on your posts | Incoming comments | Replies |
| Smart Replier | `prompts/smart_replier.md` | Context-aware reply generation | Comment thread | Smart reply |
| Reply Composer | `prompts/reply_composer.md` | Composes detailed replies for complex threads | Thread context | Composed reply |

**Implementation**: `agents/engagement/auto_commenter.py`, `agents/engagement/auto_responder.py`

---

## Team 3: Influencer Team

**Schedule**: Daily 6:00 AM + 2:00 PM
**Purpose**: Discover influencers, analyze their content, extract leads.

| Agent | Prompt File | Role | Input | Output |
|-------|------------|------|-------|--------|
| Influencer Scraper | N/A (tool-based) | Scrapes LinkedIn for influencer profiles and posts | Target list | Raw profile/post data |
| Influencer Analyzer | N/A (tool-based) | Analyzes influencer engagement patterns | Scraped data | Engagement analysis |
| Lead Extractor | N/A (derived) | Identifies potential leads from influencer audiences | Engagement data | Lead list |

**Implementation**: `agents/influencer/scraper.py`, `agents/influencer/analyzer.py`

---

## Team 4: Profile Team (`teams/profile_team.py`)

**Schedule**: 1st of month, 9:00 AM
**Purpose**: Optimize LinkedIn profile for discoverability and authority.

| Agent | Prompt File | Role | Input | Output |
|-------|------------|------|-------|--------|
| Profile Optimizer | `prompts/profile_optimizer.md` | Audits and suggests profile improvements | Current profile data | Optimization report |

---

## Team 5: Learning Team

**Schedule**: Post-campaign (triggered after content cycles)
**Purpose**: Analyze performance, feed insights back into content strategy.

| Agent | Prompt File | Role | Input | Output |
|-------|------------|------|-------|--------|
| Campaign Analyzer | `prompts/campaign_analyzer.md` | Analyzes engagement metrics and content performance | Campaign data | Performance report + recommendations |

**Implementation**: `agents/learning/campaign_analyzer.py`

---

## Shared Tools (`tools/`)

| Tool | File | Used By |
|------|------|---------|
| Browser Automation | `tools/browser_automation.py` | Engagement Team, Influencer Team |
| Airtable Client | `tools/airtable_client.py` | All teams (data persistence) |
| AI Image Generator | `tools/ai_image_generator.py` | Content Team |
| Post with Image | `tools/post_with_image.py` | Content Team (publishing) |
| Text Sanitizer | `tools/text_sanitizer.py` | Content Team, Engagement Team |
| Email Notifier | `tools/email_notifier.py` | All teams (alerts/digests) |
| Messaging Bot | `tools/messaging_bot.py` | Engagement Team |

---

## Skills (`skills/`)

| Skill | Purpose |
|-------|---------|
| `campaign-report` | Generate campaign performance reports |
| `config-audit` | Audit configuration for issues |
| `content-calendar` | Plan content calendar |
| `create-post` | Manual post creation flow |
| `deploy` | Deploy to production |
| `engagement` | Run engagement cycle manually |
| `profile-optimize` | Run profile optimization |
| `swipe-update` | Update swipe file library |

---

## Agent Communication Flow

```
Content Team                    Engagement Team
    |                               |
    v                               v
[Research] --> [Write] --> [Quality Gate] --> [Publish]
                                    |
                                    v
                           [Auto-Comment on influencer posts]
                           [Auto-Respond to audience]
                                    |
                                    v
                            Learning Team
                                    |
                                    v
                           [Campaign Analyzer]
                                    |
                                    v
                           [Feed back to Content Team]
```

---

## Key Constraints

1. **Rate Limits**: LinkedIn throttles automated actions. Engagement scheduler has built-in cooldowns.
2. **Brand Voice**: All agents reference `config/business.yaml` for persona consistency.
3. **Quality Pipeline**: No content bypasses Quality Editor + Fact Checker.
4. **Cookie Security**: Browser automation sessions use LinkedIn cookies -- never log or commit them.
5. **Deduplication**: Embedding-based dedup prevents duplicate posts. See `CLAUDE.md` Rule 33.
