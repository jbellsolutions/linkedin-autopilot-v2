# TODOS.md -- LinkedIn Autopilot V2

> Prioritized task list. P0 = critical/blocking, P4 = nice-to-have.

---

## P0 -- Critical / Blocking

- [ ] **Missing influencer_team.py import** -- `teams/` has no `outreach_team.py` visible but `scheduler_engagement.py` imports from it. Verify the outreach team module exists and is functional, or stub it out with clear error handling.
- [ ] **Duplicate engagement scheduling** -- Both `scheduler.py` and `scheduler_engagement.py` register engagement-related jobs (`engagement_loop` and `strategic_commenting` in scheduler.py overlap with `engagement_cycle` and `auto_commenter` in scheduler_engagement.py). Reconcile which scheduler owns which jobs to prevent double-firing.
- [ ] **No test suite** -- Zero test files in the repo. Add at minimum: unit tests for `BaseAgent` config resolution, integration tests for the content pipeline (trend -> write -> edit -> queue), and mock-based tests for browser automation. Without tests, Rule 8 (Mandatory Testing) cannot be satisfied.
- [ ] **No `.env.example`** -- README references `.env.example` but the file does not exist. Create it with all required and optional environment variables documented.
- [ ] **Self-healing pipeline missing** -- Rule 28 requires every pipeline to have preflight health checks and self-healing auto-fix loops. Neither scheduler implements these. Add health check jobs that run 1 hour before each critical pipeline.

---

## P1 -- High Priority

- [ ] **Error classification not implemented** -- Rule 42 requires FATAL vs RETRYABLE error classification, cooldown retries with backoff, and circuit breakers. The scheduler jobs use `misfire_grace_time` but lack structured error handling within the job functions themselves.
- [ ] **No crash pattern logging** -- Rule 41 requires a crash patterns doc with Pattern, Trigger, Symptom, Root Cause, Prevention, First Seen. Create `data/crash_patterns.json` and wire auto-logging into all agent `run()` methods.
- [ ] **Dashboard implementation unclear** -- `main.py` imports `tools.dashboard.start_dashboard` but no `dashboard.py` was found in the tools listing. Verify this module exists or build it.
- [ ] **Content deduplication** -- README mentions embedding-based dedup via OpenAI but no dedup logic is visible in the content pipeline. Implement dedup check before queuing (Rule 24: No Double Posting).
- [ ] **Config validation on startup** -- No schema validation for YAML configs. A malformed `business.yaml` will cause cryptic runtime errors. Add a config validator that runs during `check_env()` and reports specific missing/invalid fields.
- [ ] **Logging to structured format** -- Current logging goes to `linkedin-autopilot.log` as plain text. Switch to structured JSON logging for production to enable log aggregation and alerting.

---

## P2 -- Medium Priority

- [ ] **Auto-poster retry logic** -- `tools/auto_poster.py` checks the queue every 15 minutes but there is no documented retry/backoff strategy for failed posts. Add exponential backoff with max 3 retries and a dead-letter queue.
- [ ] **Metrics collection pipeline** -- The Campaign Analyzer expects performance data but there is no visible metrics ingestion system. Build a metrics collector that scrapes LinkedIn post stats (or ingests from PhantomBuster/Airtop) and stores snapshots in `data/analytics/`.
- [ ] **Swipe library build script** -- `SWIPE_FILE_CONTEXT.md` references `python3 scripts/build_library.py` but the scripts directory only contains `deploy.sh` and `setup.sh`. Either the build script is missing or it lives in the swipe-library repo. Document the rebuild process.
- [ ] **Profile team coverage** -- `teams/profile_team.py` runs a monthly audit but there is only one prompt (`profile_optimizer.md`). Consider adding headline optimization, about section analysis, and featured section recommendations as separate passes.
- [ ] **Text sanitizer coverage** -- `tools/text_sanitizer.py` exists but its scope is unclear. Ensure it catches all markdown artifacts, AI-telltale phrases, and formatting violations that the Quality Editor checks for. DRY up the detection logic.
- [ ] **Timezone handling in outreach** -- The outreach team jobs use the same `_load_timezone()` helper but LinkedIn connections and messages may need to respect the recipient's timezone, not just the owner's.

---

## P3 -- Low Priority

- [ ] **Image generation pipeline** -- `tools/ai_image_generator.py` and `tools/post_with_image.py` exist but are not wired into the content pipeline. Add image generation as an optional step between Quality Editor approval and posting queue.
- [ ] **Newsletter agent** -- `prompts/newsletter_researcher.md` exists but there is no dedicated newsletter team or scheduled job. Wire up a weekly newsletter pipeline.
- [ ] **Multi-account support** -- Current architecture assumes one LinkedIn account. The config system could support multiple accounts with separate `business.yaml` files and scheduler instances.
- [ ] **Engagement analytics dashboard** -- The Campaign Analyzer produces reports as JSON files. Build a dashboard view (extend the existing port 8080 dashboard) to visualize trends, health scores, and strategy changes over time.
- [ ] **Airtable sync improvements** -- `tools/airtable_client.py` exists but its integration points are not documented. Map out which data flows to/from Airtable and ensure bidirectional sync is reliable.
- [ ] **Webhook support for real-time events** -- Currently all processing is cron-based. Add optional webhook endpoints for real-time LinkedIn notification handling (new comments, new followers) to reduce the 2-hour reply latency.
- [ ] **Prompt versioning** -- Prompts are plain `.md` files with no version tracking. When prompt changes cause quality regressions, there is no way to roll back. Add version headers to prompts and log which version produced each piece of content.

---

## P4 -- Nice-to-Have / Future

- [ ] **A/B testing framework** -- The Campaign Analyzer recommends experiments but there is no structured A/B testing system. Build one that can split content formats, hooks, or CTAs and measure statistical significance.
- [ ] **Slack/Discord notifications** -- Email digests are the only notification channel. Add Slack or Discord webhooks for real-time alerts (lead detected, content approved, campaign report ready).
- [ ] **Content calendar UI** -- The content calendar is YAML-based. A visual calendar UI showing scheduled, queued, published, and rejected content would improve the review workflow.
- [ ] **Influencer relationship scoring** -- Track comment frequency, response rate, and engagement reciprocity per influencer. Use the score to prioritize which influencers get comments first.
- [ ] **Voice fingerprinting** -- Run the owner's existing LinkedIn posts through a style analyzer to build a quantitative voice profile. Use it to score new content against the real voice, not just the configured voice.
- [ ] **Plugin system for new integrations** -- The tools directory is a flat collection. Refactor into a plugin system where new integrations (CRM, analytics, messaging platforms) can be added without modifying core code.
- [ ] **Observability stack** -- Add Prometheus metrics, Grafana dashboards, and structured alerting for production deployments. Track agent execution times, API costs, quality scores, and pipeline throughput.
