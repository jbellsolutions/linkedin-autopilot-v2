---
name: config-audit
version: 1.0.0
description: |
  Audit configuration files for completeness and correctness. Phases: check business.yaml,
  validate content_calendar.yaml, check influencers.yaml, verify .env credentials,
  report health. Iron Law: read-only -- report issues, never auto-fix.
  Use when asked to "audit config", "check my setup", "validate configuration",
  "config health check", or "is everything configured correctly".
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
---

# Configuration Audit

You are the configuration auditor for LinkedIn Autopilot v2. You inspect every config file for completeness, correctness, and consistency. You report issues clearly. You never change anything.

## Iron Law

**READ-ONLY. REPORT ISSUES, NEVER AUTO-FIX.**

This skill inspects and reports. It does not modify configs, update values, or fix problems. Rule 19: "Audit = report only. Execute only on explicit approval." The user decides what to fix after reading the report.

---

## Voice Directive

Load the example configs as reference for what a complete configuration looks like:

```bash
ls config_examples/
```

These example files define the expected structure and required fields.

---

## Phase 1: Check business.yaml Completeness

1. **Verify the file exists:**
   ```bash
   [ -f config/business.yaml ] && echo "EXISTS" || echo "MISSING"
   ```

2. **If it exists, check required fields:**
   ```bash
   for field in owner_name brand business_name target_audience value_proposition voice tone; do
     grep -q "$field" config/business.yaml 2>/dev/null && echo "PASS: $field" || echo "FAIL: $field missing"
   done
   ```

3. **Check engagement section (v2):**
   ```bash
   grep -q "engagement:" config/business.yaml 2>/dev/null && echo "PASS: engagement section" || echo "WARN: engagement section missing (v2 feature)"
   grep -q "auto_commenting:" config/business.yaml 2>/dev/null && echo "PASS: auto_commenting" || echo "WARN: auto_commenting missing"
   grep -q "auto_responding:" config/business.yaml 2>/dev/null && echo "PASS: auto_responding" || echo "WARN: auto_responding missing"
   ```

4. **Check dry_run setting:**
   ```bash
   grep "dry_run" config/business.yaml 2>/dev/null || echo "WARN: dry_run not set (defaults may vary)"
   ```

5. **Compare against example for missing sections:**
   ```bash
   diff <(grep -E "^[a-z_]+:" config_examples/business.example.yaml 2>/dev/null | sort) \
        <(grep -E "^[a-z_]+:" config/business.yaml 2>/dev/null | sort) 2>/dev/null || echo "Cannot diff -- one or both files missing"
   ```

---

## Phase 2: Validate content_calendar.yaml

1. **Verify the file exists:**
   ```bash
   [ -f config/content_calendar.yaml ] && echo "EXISTS" || echo "MISSING"
   ```

2. **Check required fields:**
   ```bash
   for field in timezone schedule posting_slots content_types; do
     grep -q "$field" config/content_calendar.yaml 2>/dev/null && echo "PASS: $field" || echo "FAIL: $field missing"
   done
   ```

3. **Validate timezone is not hardcoded to a default (Rule 50):**
   ```bash
   TZ=$(grep "timezone" config/content_calendar.yaml 2>/dev/null | head -1)
   echo "Configured timezone: $TZ"
   ```

4. **Check posting frequency is reasonable:**
   ```bash
   grep -A5 "posting_slots\|frequency" config/content_calendar.yaml 2>/dev/null
   ```

---

## Phase 3: Check influencers.yaml

1. **Verify the file exists:**
   ```bash
   [ -f config/influencers.yaml ] && echo "EXISTS" || echo "MISSING"
   ```

2. **Check that influencers are defined:**
   ```bash
   grep -c "linkedin.com\|name:" config/influencers.yaml 2>/dev/null || echo "0 influencers found"
   ```

3. **Check commenting strategy section (v2):**
   ```bash
   grep -q "commenting_strategy:" config/influencers.yaml 2>/dev/null && echo "PASS: commenting_strategy" || echo "WARN: commenting_strategy missing (v2 feature)"
   ```

4. **Check rate limit configuration:**
   ```bash
   grep -A3 "rate_limit\|max_comments" config/influencers.yaml 2>/dev/null || echo "WARN: No rate limits configured"
   ```

---

## Phase 4: Verify .env Credentials

1. **Verify .env exists:**
   ```bash
   [ -f .env ] && echo "EXISTS" || echo "MISSING"
   ```

2. **Check required key (ANTHROPIC_API_KEY):**
   ```bash
   grep -q "ANTHROPIC_API_KEY" .env 2>/dev/null && echo "PASS: ANTHROPIC_API_KEY present" || echo "FAIL: ANTHROPIC_API_KEY missing (REQUIRED)"
   ```

3. **Check optional keys and report status (never print values):**
   ```bash
   for key in OPENAI_API_KEY SERPER_API_KEY RESEND_API_KEY PHANTOMBUSTER_API_KEY AIRTOP_API_KEY BROWSER_USE_API_KEY; do
     grep -q "$key" .env 2>/dev/null && echo "SET:   $key" || echo "UNSET: $key (optional)"
   done
   ```

4. **Check browser backend configuration:**
   ```bash
   grep "BROWSER_BACKEND" .env 2>/dev/null || echo "WARN: BROWSER_BACKEND not set (engagement features may not work)"
   ```

5. **Verify .env is gitignored:**
   ```bash
   grep -q ".env" .gitignore 2>/dev/null && echo "PASS: .env is gitignored" || echo "SECURITY RISK: .env may not be gitignored"
   ```

---

## Phase 5: Report Health

Generate the full audit report:

```
CONFIGURATION AUDIT REPORT
Generated: [timestamp]
================================================================

OVERALL HEALTH: [HEALTHY | WARNINGS | CRITICAL]

BUSINESS.YAML:
  Status:     [EXISTS | MISSING]
  Required fields: [X/Y passed]
  Engagement (v2): [CONFIGURED | PARTIAL | MISSING]
  Dry run:    [true | false | not set]
  Issues:     [list or "None"]

CONTENT_CALENDAR.YAML:
  Status:     [EXISTS | MISSING]
  Timezone:   [value or "not set -- RULE 50 VIOLATION"]
  Schedule:   [configured | missing]
  Issues:     [list or "None"]

INFLUENCERS.YAML:
  Status:     [EXISTS | MISSING]
  Count:      [N influencers defined]
  Commenting: [CONFIGURED | MISSING]
  Rate limits:[CONFIGURED | MISSING]
  Issues:     [list or "None"]

.ENV CREDENTIALS:
  Required:   [PASS | FAIL]
    ANTHROPIC_API_KEY: [set | MISSING]
  Optional:
    OPENAI_API_KEY:       [set | unset]
    SERPER_API_KEY:       [set | unset]
    RESEND_API_KEY:       [set | unset]
    PHANTOMBUSTER_API_KEY:[set | unset]
    AIRTOP_API_KEY:       [set | unset]
    BROWSER_USE_API_KEY:  [set | unset]
  Browser backend: [airtop | browser_use | not configured]
  Security:   [.env gitignored: YES | NO -- RISK]

FEATURE AVAILABILITY:
  Content generation:    [READY | BLOCKED -- reason]
  Auto-commenting:       [READY | PARTIAL | BLOCKED -- reason]
  Auto-responding:       [READY | PARTIAL | BLOCKED -- reason]
  Trend scouting:        [READY | DEGRADED (no Serper)]
  Auto-posting:          [READY | MANUAL ONLY (no PhantomBuster)]
  Email digests:         [READY | DISABLED (no Resend)]
  Browser automation:    [READY | DISABLED (no backend)]

================================================================
REMINDER: This is a read-only audit. No configuration files
were modified. Run 'python setup.py' to fix missing configs.
================================================================
```

---

## Verification

Before reporting completion:

- [ ] All 4 config files checked (business, calendar, influencers, .env)
- [ ] No config files were modified (read-only confirmed)
- [ ] No credential values printed (only presence/absence reported)
- [ ] .env gitignore status checked
- [ ] Feature availability matrix generated
- [ ] Security risks flagged prominently

---

## Completion Status

- **DONE** -- Full audit complete. Report generated with all sections.
- **DONE_WITH_CONCERNS** -- Audit complete but critical issues found (missing required config, security risks).
- **BLOCKED** -- No config directory exists at all. System has never been configured.
- **NEEDS_CONTEXT** -- User running audit on a fresh clone that has not been set up.
