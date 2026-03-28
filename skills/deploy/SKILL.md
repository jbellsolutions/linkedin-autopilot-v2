---
name: deploy
version: 1.0.0
description: |
  Deploy the LinkedIn bot. Phases: validate config, run tests if they exist, build
  Docker image, deploy to server, verify scheduler is running, check first cycle.
  Iron Law: never deploy without validating config first.
  Use when asked to "deploy", "start the bot", "launch", "docker up",
  "go live", or "put it in production".
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
---

# Deploy LinkedIn Bot

You are the deployment operator for LinkedIn Autopilot v2. You take the system from configured to running through a validated sequence. No blind deploys. Every step is verified before proceeding to the next.

## Iron Law

**NEVER DEPLOY WITHOUT VALIDATING CONFIG FIRST.**

A deployment without config validation is a production incident waiting to happen. Phase 1 must pass before any Docker command runs. Rule 38: "Run a live test immediately to ensure it works end-to-end."

---

## Voice Directive

Read the deployment architecture before starting:

```bash
cat docker-compose.yml
cat Dockerfile
cat main.py | head -50
```

---

## Phase 1: Validate Config

**This phase must PASS before any deployment action.**

1. **Check required config files exist:**
   ```bash
   echo "=== Config Check ==="
   [ -f config/business.yaml ] && echo "PASS: business.yaml" || echo "FAIL: business.yaml missing"
   [ -f config/content_calendar.yaml ] && echo "PASS: content_calendar.yaml" || echo "FAIL: content_calendar.yaml missing"
   [ -f config/influencers.yaml ] && echo "PASS: influencers.yaml" || echo "FAIL: influencers.yaml missing"
   [ -f .env ] && echo "PASS: .env" || echo "FAIL: .env missing"
   ```

2. **Validate required API key:**
   ```bash
   grep -q "ANTHROPIC_API_KEY" .env 2>/dev/null && echo "PASS: ANTHROPIC_API_KEY set" || echo "FAIL: ANTHROPIC_API_KEY missing"
   ```

3. **Check business.yaml is not empty/default:**
   ```bash
   grep -c "owner_name\|brand\|business_name" config/business.yaml 2>/dev/null
   ```

4. **Check dry_run setting and report it:**
   ```bash
   grep "dry_run" config/business.yaml 2>/dev/null
   ```

5. **Validate timezone is set (Rule 50 -- no hardcoded timezones):**
   ```bash
   grep "timezone" config/content_calendar.yaml 2>/dev/null
   ```

**Stop condition:** If any FAIL in step 1 or 2, do not proceed. Report what is missing and how to fix it. Suggest running `python setup.py` if configs are missing.

---

## Phase 2: Run Tests

1. **Check if tests exist:**
   ```bash
   find . -name "test_*.py" -o -name "*_test.py" | head -10
   ls tests/ 2>/dev/null
   ```

2. **If tests exist, run them:**
   ```bash
   python -m pytest tests/ -v --tb=short 2>&1 | tail -30
   ```

3. **If no tests exist**, note it but do not block deployment: "No test suite found. Proceeding with deployment. Consider adding tests."

4. **Check Python dependencies:**
   ```bash
   pip check 2>&1 | head -10
   ```

**Stop condition:** If tests exist and fail, do not proceed to Phase 3. Fix the tests first (Rule 8 -- mandatory testing).

---

## Phase 3: Build Docker Image

1. **Verify Docker is available:**
   ```bash
   docker --version 2>/dev/null && echo "DOCKER_AVAILABLE" || echo "DOCKER_NOT_AVAILABLE"
   docker-compose --version 2>/dev/null || docker compose version 2>/dev/null
   ```

2. **If Docker is available, build:**
   ```bash
   docker-compose build --no-cache 2>&1 | tail -20
   ```

3. **If Docker is not available**, fall back to local deployment instructions:
   ```bash
   echo "Docker not available. For local deployment:"
   echo "  pip install -r requirements.txt"
   echo "  python main.py"
   ```

**Stop condition:** If the Docker build fails, read the error output and diagnose. Common issues: missing requirements, Dockerfile syntax, base image unavailable.

---

## Phase 4: Deploy

1. **Start the services:**
   ```bash
   docker-compose up -d 2>&1
   ```

2. **Check container status:**
   ```bash
   docker-compose ps
   ```

3. **Check for startup errors:**
   ```bash
   docker-compose logs --tail=50 2>&1
   ```

**Stop condition:** If containers are not in "Up" state, read the logs and diagnose. Do not proceed to verification with failing containers.

---

## Phase 5: Verify Scheduler Is Running

1. **Check the scheduler process:**
   ```bash
   docker-compose logs --tail=30 2>&1 | grep -i "scheduler\|job\|cron"
   ```

2. **Verify the dashboard** (if applicable):
   ```bash
   curl -s -o /dev/null -w "%{http_code}" http://localhost:8080 2>/dev/null || echo "Dashboard not reachable"
   ```

3. **Confirm scheduled jobs are registered:**
   ```bash
   docker-compose logs --tail=50 2>&1 | grep -i "added job\|next run"
   ```

---

## Phase 6: Check First Cycle

1. **Wait for initial log activity** (scheduler should show next run times):
   ```bash
   docker-compose logs --tail=20 2>&1
   ```

2. **Verify data directories are being created:**
   ```bash
   ls -la data/ 2>/dev/null
   ```

3. **Report the deployment status:**

```
DEPLOYMENT REPORT
================================================================
Config validation:  [PASS/FAIL]
Tests:              [PASS/SKIP/FAIL]
Docker build:       [PASS/FAIL/N/A]
Container status:   [RUNNING/FAILED]
Scheduler:          [ACTIVE/INACTIVE]
Dashboard:          [REACHABLE/UNREACHABLE/N/A]
Dry run mode:       [ACTIVE/INACTIVE]
Timezone:           [configured timezone]

Next scheduled runs:
  Content production: [time]
  Engagement cycle:   [time]
  Campaign analysis:  [time]
================================================================
```

---

## Verification

Before reporting completion:

- [ ] All required configs validated
- [ ] Tests passed (or noted as absent)
- [ ] Docker image built successfully
- [ ] Containers running
- [ ] Scheduler active with registered jobs
- [ ] Dry run mode status clearly reported
- [ ] No hardcoded timezones (Rule 50)
- [ ] Deployment report output with all statuses

---

## Completion Status

- **DONE** -- Deployed and verified. Scheduler running. All checks passed.
- **DONE_WITH_CONCERNS** -- Deployed but with warnings (e.g., no tests, optional API keys missing, dry run still active).
- **BLOCKED** -- Config validation failed or Docker build failed. Specific errors reported.
- **NEEDS_CONTEXT** -- Missing config files. User needs to run setup.py first.
