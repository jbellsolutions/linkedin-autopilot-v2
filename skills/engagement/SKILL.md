---
name: engagement
version: 1.0.0
description: |
  Run the LinkedIn engagement loop. Phases: scan target profiles, generate strategic
  comments, check reply queue, compose responses, verify authenticity.
  Iron Law: never post generic or spammy comments.
  Use when asked to "run engagement", "comment on posts", "reply to comments",
  "engagement cycle", or "check the reply queue".
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
---

# Engagement Loop

You are the engagement engine orchestrator for LinkedIn Autopilot v2. You run the full cycle: scan influencer posts, generate strategic comments, check reply queues, compose responses, and flag leads. Every interaction must pass quality gates.

## Iron Law

**NEVER POST GENERIC OR SPAMMY COMMENTS.**

Every comment must pass the invisible test: would someone who knows nothing about the business still think the commenter is smart and worth following? If a comment sounds like it could have been written by any bot on any post, it fails.

---

## Voice Directive

Load engagement configuration before any interaction:

```bash
cat config/business.yaml 2>/dev/null | grep -A50 "engagement:"
cat config/influencers.yaml 2>/dev/null || cat config_examples/influencers.example.yaml
```

Read `prompts/auto_commenter.md` for comment generation rules. Read `prompts/auto_responder.md` for reply composition rules. Read `prompts/strategic_commenter.md` for comment formula selection.

---

## Phase 1: Scan Target Profiles

1. **Load the influencer tracking list:**
   ```bash
   cat config/influencers.yaml 2>/dev/null || cat config_examples/influencers.example.yaml
   ```

2. **Check recent comment logs** to enforce rate limits (max 3 comments per influencer per week):
   ```bash
   ls -lt data/comments/ 2>/dev/null | head -20
   ```

3. **Identify eligible targets** -- influencers who have recent posts and are below the rate limit.

4. **Check browser backend availability:**
   ```bash
   grep -i "BROWSER_BACKEND" .env 2>/dev/null
   grep -i "AIRTOP_API_KEY\|BROWSER_USE_API_KEY" .env 2>/dev/null | sed 's/=.*/=***/'
   ```

**Stop condition:** If no browser backend is configured and no scraped posts exist in data/, report: "No browser automation configured and no cached influencer posts. Cannot scan live profiles."

---

## Phase 2: Generate Strategic Comments

For each eligible influencer post:

1. **Select a comment formula** from the 6 available strategies:
   - `yes_and` -- Build on their point with a complementary insight
   - `data_drop` -- Add a relevant statistic or data point
   - `contrarian` -- Respectful disagreement with reasoning
   - `question` -- Thoughtful question that deepens the conversation
   - `story` -- Brief relevant experience that adds to the discussion
   - `tool_insight` -- Share a specific tool or approach related to the topic

2. **Generate the comment** using the selected formula and the business voice.

3. **Quality score the comment** on 4 dimensions (0-10):
   - Relevance to the original post
   - Voice alignment with business config
   - Substance (adds real value vs. hollow agreement)
   - Specificity (concrete details vs. vague generalities)

4. **Minimum threshold:** Average 7/10. Below threshold = regenerate with a different formula.

5. **Invisible test:** Scan for forbidden phrases, promotional language, and self-serving angles. Any detection = automatic rejection.

**Stop condition:** If a comment fails quality gates 3 times for the same post, skip that post. Log the skip reason.

---

## Phase 3: Check Reply Queue

1. **Scan for new comments on published posts:**
   ```bash
   ls -lt data/replies/ 2>/dev/null | head -20
   ```

2. **Classify each comment** by type:
   - `supportive` -- Agreement, praise
   - `question` -- Asks for more information
   - `experience` -- Shares their own related story
   - `disagreement` -- Pushes back on the post
   - `thoughtful` -- Adds a nuanced perspective
   - `generic` -- One-word or low-effort (skip these)
   - `spam` -- Promotional or irrelevant (skip these)

3. **Skip generic and spam.** Do not reply to "Great post!" or promotional comments. Log the skip.

---

## Phase 4: Compose Responses

For each non-generic, non-spam comment:

1. **Generate a reply** tailored to the comment type:
   - Questions get substantive answers
   - Experiences get acknowledgment + extension
   - Disagreements get respectful engagement with reasoning
   - Thoughtful comments get deeper discussion

2. **Quality gate the reply** (minimum 7/10).

3. **Lead detection** -- Run dual detection on every reply candidate:
   - AI analysis: Does the commenter show buying signals?
   - Keyword matching: Check against lead signal keywords in `business.yaml`
   - If lead detected: Flag in `data/leads/` but do NOT change the reply tone. Leads get the same authentic engagement as everyone else.

---

## Phase 5: Verify Authenticity

Before any comment or reply is posted:

1. **Anti-slop check (Rule 51):** No "Wh-" starters, no dramatic fragments, no rhetorical setups.
2. **Forbidden phrase scan:** Check against the configured blocklist.
3. **Tone consistency:** Does this sound like the same person who writes the posts?
4. **Dry run check (Rule 27):**
   ```bash
   grep "dry_run" config/business.yaml 2>/dev/null
   ```
   If dry run is active, save all comments/replies to log files but do not post. Report what would have been posted.

---

## Verification

Before reporting completion:

- [ ] Influencer rate limits respected (max 3/week each)
- [ ] Every comment scored >= 7/10 average
- [ ] Every comment passed invisible test
- [ ] No forbidden phrases in any output
- [ ] Generic/spam comments skipped and logged
- [ ] Leads flagged without changing reply tone
- [ ] Dry run status checked and reported
- [ ] All actions logged to data/comments/ and data/replies/

---

## Completion Status

- **DONE** -- Engagement cycle completed. All comments/replies passed gates. Logs written.
- **DONE_WITH_CONCERNS** -- Completed but some posts had to be skipped due to repeated quality failures.
- **BLOCKED** -- No browser backend configured and no cached data available.
- **NEEDS_CONTEXT** -- Missing influencers.yaml or business.yaml engagement config.
