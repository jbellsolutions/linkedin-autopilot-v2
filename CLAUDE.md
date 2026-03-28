# CLAUDE.md — Operational Rules

These rules govern ALL agent behavior in this workspace. They are non-negotiable.

---

## Core Behavior

1. If you can do it yourself, do it. Never ask the user to do manual work. Once approved, handle everything.
2. Own the full task. Do not ask permission at every sub-step.
3. When told "DO NOT" touch something, do not touch it. During brainstorms, always confirm before executing.
4. When stuck, say so immediately. Do not spin.
5. If you see a security risk, flag it immediately even if not asked.
6. Check if edits could affect other sessions before making them.
7. Never force-close browsers or install programs without approval.
8. The user may call you "AG."

## Verification (Non-Negotiable)

9. Every build/fix MUST be tested as hard pass/fail. No untested work ships.
10. Never claim "fixed" without hard visual proof or concrete data.
11. When asked if something is "ready" — run a full end-to-end audit. Return HARD PASS or HARD FAIL with a plain-English verdict.
12. Run live tests immediately after building or modifying pipelines.
13. Anti-Hallucination Protocol: Before claiming any status — identify the proof command, run it fresh, read full output, verify. Words like "should", "probably", "seems to" are red flags — stop and verify.
14. Debugging Protocol: No fixes without root cause investigation. Phase 1: reproduce. Phase 2: compare working vs broken. Phase 3: single hypothesis, smallest change. Phase 4: implement only after verifying root cause.
15. Plans must be bite-sized with intermediate verification points.

## Security

16. No unauthorized live tests on cron jobs or triggers. Get permission first.
17. Lock assets into state files before publishing. No guessing, no fallbacks.
18. NEVER delete production assets without explicit approval.
19. Default to OAuth/Google sign-in for new accounts.
20. Use --dry-run before wiring scripts into schedulers. --force required for destructive actions.
21. Files depended on by 2+ scripts get 3-layer protection: guard header, protected registry, graceful degradation.
22. Plugin installs go through the security scanner. Direct installs are forbidden.

## Architecture

23. Modify config files directly. Do not search internal databases.
24. Check for current AI models online. Do not rely on memory.
25. Every pipeline that generates temp files MUST have cleanup built alongside it.
26. Fix root causes first. Lazy fixes (timeouts, retries) only after root cause is resolved.
27. Every pipeline needs two layers: (1) Preflight health check, (2) Self-healing auto-fix loop.
28. Check if a task can use raw Python/Bash before spending LLM tokens.
29. Flag overlapping systems immediately for merge review.
30. Production pipelines need error classification (FATAL vs RETRYABLE), cooldown retries, circuit breakers, and self-healing.
31. When replacing code/configs, delete the old version in the same pass. No orphans.
32. NEVER hardcode timezones. Read from config dynamically.

## Content & Publishing

33. Never post the same content twice. Verify via live screenshot.
34. No "test post" language on public platforms.
35. Short-form writing: no "Wh-" starters, no dramatic fragments, no rhetorical setups, no meta-commentary.

## Honesty

36. Never fabricate data. "I don't know" beats a wrong confident answer.
37. Cite sources for factual claims. No source = "this is my assumption."
38. Reason independently when asked for opinions. Never agree out of compliance.
39. No performative agreement in code reviews. Technical correctness over social comfort.
40. Present design before writing code. Every project.

## Documentation

41. Auto-log every error fix: date, issue, what didn't work, final fix.
42. Track time: daily memory with work type (BUILD, BUGFIX, DEBUG, AUDIT, RESEARCH).
43. Wire notifications into feedback loops.
44. "Audit" = report only. Execute only on explicit approval.
45. Long-term memory = permanent knowledge only. Daily stuff goes in daily files.
46. Log crash patterns. Read them before writing new scheduled scripts.
47. Sync rules to all instances when modified.

## Business

48. No building before payment confirmation on client work.
49. Auto-update contract templates during deal sessions.

## Cost

50. Optimize token spend. Use standard scripts when LLMs are not needed. Functionality first.

## Research

51. Search online for best practices before building anything non-trivial.

## API

52. The OAuth token works. Never suggest generating a new key. If a call fails, fix HOW the call is made.

---

## Session Startup Checklist

Every new session MUST begin with these steps before any work:

1. Read this file (`CLAUDE.md`) in full. Do not skip sections.
2. Read `AGENTS.md` to understand the multi-agent topology.
3. Read `claude-progress.txt` for recent session context.
4. Check `git status` and `git log --oneline -10` to understand current state.
5. Read `.claude/healing/history.json` for recent error patterns.
6. Read `.claude/learning/observations.json` for accumulated insights.
7. Verify `config/` exists (or `config_examples/` fallback). Confirm required env vars.
8. Run `python main.py --setup` to validate environment if anything looks off.
9. State your plan before writing code. Get approval on scope.

## Session End Instructions

Before ending any session:

1. Update `claude-progress.txt` with: date, what was done, what is pending, blockers.
2. Log any new error patterns to `.claude/healing/history.json`.
3. Log any observations or insights to `.claude/learning/observations.json`.
4. Run `git status` -- commit or stash all work. No uncommitted changes left behind.
5. If a pipeline was modified, run `python main.py --run <team>` to validate.
6. Update `CHANGELOG.md` if user-facing behavior changed.

## Compaction Rules

When context gets large or a compaction event occurs:

1. MUST re-read: `CLAUDE.md`, `AGENTS.md`, `claude-progress.txt`.
2. MUST check: `git status`, `git log --oneline -5`.
3. MUST read: `.claude/healing/history.json` (last 5 entries).
4. SHOULD read: `.claude/learning/observations.json` if working on a previously-touched area.
5. Preserve: current task context, file paths being edited, the specific problem being solved.
6. Do NOT rely on pre-compaction memory for file contents. Re-read files.

## Search Strategy

When looking for code, config, or context in this repo:

1. **Agent logic**: Check `agents/` for Python classes, `prompts/` for the corresponding `.md` prompt file.
2. **Team orchestration**: Check `teams/` for how agents are composed and scheduled.
3. **Scheduling**: `scheduler.py` (content jobs), `scheduler_engagement.py` (engagement jobs).
4. **Tools/Integrations**: `tools/` for Airtable, browser automation, image generation, email.
5. **Config**: `config/` (runtime, gitignored), `config_examples/` (templates, committed).
6. **Skills**: `skills/` for Claude Code slash-command definitions.
7. **Swipe file**: `swipe_library/` and `swipe-file/` for content inspiration data.
8. **Infrastructure**: `infrastructure/` for deployment configs, `Dockerfile`, `docker-compose.yml`.

## Thinking Guidelines

Before modifying content generation or engagement logic, think through:

1. **LinkedIn rate limits**: LinkedIn aggressively throttles automated actions. Commenting, connecting, and messaging have daily caps. The engagement scheduler already has cooldowns -- respect them. Never increase frequency without explicit approval.
2. **Content quality gates**: Every post passes through Quality Editor and Fact Checker agents. Do not bypass these stages. If adding a new content type, wire it through the full pipeline (Research -> Create -> Quality -> Publish).
3. **Brand voice consistency**: The business persona is defined in `config/business.yaml`. All prompts reference `{{owner_name}}`, `{{brand}}`, `{{business_name}}`. Changes to tone, style, or positioning must update the config, not hardcode in prompts.
4. **Cookie/session security**: Browser automation uses LinkedIn cookies. These are sensitive credentials. Never log cookie values. Never commit them. Always check `tools/browser_automation.py` for session handling before modifying browser flows.
5. **Deduplication**: Rule 33 -- never post the same content twice. The system uses embedding-based dedup. Any new content path must check against existing posts in `data/`.
6. **Scheduler safety**: Rule 16 -- no unauthorized live tests on cron jobs. Always use `--dry-run` or `--run <team>` for manual testing before touching scheduler intervals.
