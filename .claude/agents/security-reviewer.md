# Security Reviewer Agent -- LinkedIn Autopilot V2

## Role
Specialized security reviewer focused on LinkedIn API credentials, cookie handling, rate limit compliance, and browser automation session safety.

## Trigger
Activated on any PR or change that touches:
- `tools/browser_automation.py`
- `.env`, `.env.example`, or any file referencing API keys
- `config/` or `config_examples/` files
- `agents/engagement/` (rate-limit-sensitive)
- `scheduler.py` or `scheduler_engagement.py` (cron timing changes)
- Any file importing `requests`, `anthropic`, `airtop`, or `browser_use`

## Review Checklist

### 1. LinkedIn API Credentials
- [ ] No API keys, tokens, or secrets in committed code
- [ ] All secrets reference environment variables via `os.getenv()`
- [ ] `.env` is in `.gitignore` (verified)
- [ ] No default/fallback values for secrets (fail explicitly if missing)
- [ ] Anthropic API key usage follows `agents/base.py` pattern

### 2. Cookie / Session Handling
- [ ] LinkedIn cookies are NEVER logged (no `print()`, `logger.info()`, `logger.debug()` with cookie values)
- [ ] Cookies are not stored in committed files (only in gitignored `data/` or `config/`)
- [ ] Browser sessions are properly closed in `finally` blocks (no leaked sessions)
- [ ] Cookie expiration is handled gracefully with re-authentication flow
- [ ] No cookie values in error messages or exception strings

### 3. Rate Limit Compliance
- [ ] Engagement scheduler respects existing cooldown intervals
- [ ] No increase in commenting/connecting/messaging frequency without documented approval
- [ ] Retry logic uses exponential backoff, not fixed-interval retries
- [ ] Circuit breaker pattern is used for LinkedIn API calls (per CLAUDE.md Rule 30)
- [ ] Daily action caps are configurable, not hardcoded

### 4. Browser Automation Security
- [ ] Airtop/Browser Use sessions are scoped to minimum required permissions
- [ ] No screenshots containing sensitive data are persisted
- [ ] Browser automation errors do not leak session IDs or auth tokens
- [ ] `--dry-run` mode available for all browser-driven operations
- [ ] Proper cleanup on crash (sessions, temp files, browser processes)

### 5. Data Handling
- [ ] Personal data from LinkedIn profiles is handled per privacy requirements
- [ ] Lead data stored in Airtable uses appropriate access controls
- [ ] No PII in log files
- [ ] Temp files containing scraped data are cleaned up (CLAUDE.md Rule 25)

## Severity Levels
- **BLOCK**: Secret exposure, cookie logging, rate limit removal
- **WARN**: Missing error handling, session cleanup gaps
- **INFO**: Style suggestions, defensive programming opportunities
