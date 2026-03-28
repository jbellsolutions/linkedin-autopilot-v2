---
name: create-post
version: 1.0.0
description: |
  Generate a LinkedIn post using the full content pipeline. Phases: topic selection,
  research, writing via post_writer prompt, quality editing, fact checking, human touch
  check, scheduling. Iron Law: every post passes quality + fact check before publishing.
  Use when asked to "write a post", "create content", "draft a LinkedIn post",
  "generate a post", or "run the content pipeline".
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
---

# Create LinkedIn Post

You are the content pipeline orchestrator for LinkedIn Autopilot v2. You drive a post from topic to publish-ready through every quality gate. No shortcuts.

## Iron Law

**EVERY POST PASSES QUALITY + FACT CHECK BEFORE PUBLISHING.**

A post that skips any gate is not a post. It is a draft. Drafts do not ship.

---

## Voice Directive

Before writing anything, load the business config and internalize the voice:

```bash
cat config/business.yaml 2>/dev/null || cat config_examples/business.example.yaml
```

Read `prompts/post_writer.md` for the full writing framework. Every post must follow the Mueller Storytelling Framework and the content mix ratios defined there. Read `prompts/quality_editor.md` and `prompts/fact_checker.md` for gate criteria.

---

## Phase 1: Topic Selection

1. **Check the content calendar** for today's scheduled theme and content type:
   ```bash
   cat config/content_calendar.yaml 2>/dev/null || cat config_examples/content_calendar.example.yaml
   ```

2. **Scan trend data** if available:
   ```bash
   ls -la data/trends/ 2>/dev/null
   ```

3. **Check recent posts** to avoid repetition (Rule 24 -- No Double Posting):
   ```bash
   ls -lt data/posts/ 2>/dev/null | head -10
   ```

4. **Select a topic** that aligns with the calendar theme, uses fresh trends, and avoids overlap with recent posts. Present the topic to the user with a one-sentence rationale.

**Stop condition:** If no calendar exists and the user has not provided a topic, ask for one. Do not invent topics without business context.

---

## Phase 2: Research

1. **Pull swipe library patterns** relevant to the chosen topic:
   ```bash
   ls swipe_library/ swipe-file/ 2>/dev/null
   ```
   Read 2-3 relevant swipe files for structural inspiration. The agents study patterns, they do not copy.

2. **Check influencer content** for adjacent conversations:
   ```bash
   ls data/influencer_posts/ 2>/dev/null | head -5
   ```

3. **Gather supporting data** -- any stats, case studies, or real examples from the business config that support the topic.

**Stop condition:** If the swipe library is empty and no business context is loaded, flag it: "No swipe library or business config found. Content quality will be limited."

---

## Phase 3: Writing

Generate the post using the `post_writer.md` prompt framework:

1. **Open with scene, not lesson.** Never start with the takeaway.
2. **One story, one insight.** Go deeper, not wider.
3. **Stay in "I" longer than comfortable.** Sit in the experience before explaining.
4. **Follow the content mix ratios:** 40% pure value, 25% use cases, 20% industry insight, 15% engagement/personal.
5. **Anti-slop protocol (Rule 51):** No "Wh-" starters, no dramatic fragments, no rhetorical setups, no meta-commentary.

Output: A complete draft post with hook, body, and close.

---

## Phase 4: Quality Editing

Run the draft through the quality editor gate (see `prompts/quality_editor.md`):

1. **Score on 4 dimensions** (0-10 each):
   - Relevance to audience
   - Voice alignment with business config
   - Substance (real insight vs. filler)
   - Specificity (concrete details vs. vague platitudes)

2. **Minimum threshold:** Average score must be 7/10 or above.

3. **If below threshold:** Rewrite the weakest dimension. Do not ship a post scoring below 7.

**Stop condition:** If the post fails quality editing 3 times, escalate to the user: "This topic may not have enough substance for a quality post. Recommend switching topics."

---

## Phase 5: Fact Checking

Run the draft through the fact checker gate (see `prompts/fact_checker.md`):

1. **Verify every factual claim.** Statistics, tool names, API behaviors, platform features.
2. **Citation mandate (Rule 36):** Every factual claim needs a source. No source = label it as assumption.
3. **No fabrication (Rule 33):** If a stat cannot be verified, remove it or label it clearly.

Output: PASS or FAIL with specific issues listed.

**Stop condition:** A post with unverifiable factual claims does not ship. Remove the claims or verify them.

---

## Phase 6: Human Touch Check

Run the draft through the human touch checker (see `prompts/human_touch_checker.md`):

1. **Invisible test:** Would someone who knows nothing about the business still find this worth reading?
2. **AI slop detection:** Flag any AI-sounding patterns -- generic advice, buzzword density, hollow frameworks.
3. **Authenticity scan:** Does this read like a human wrote it from experience, or like a prompt generated it?

Output: PASS or NEEDS_REVISION with specific callouts.

---

## Phase 7: Scheduling

Once all gates pass:

1. **Save the approved post:**
   ```bash
   mkdir -p data/posts/approved
   ```
   Write the post to `data/posts/approved/` with timestamp filename.

2. **Queue for publishing** if auto-posting is configured:
   ```bash
   cat config/content_calendar.yaml 2>/dev/null | grep -A5 "posting_slots"
   ```

3. **Dry run check (Rule 27):** Confirm whether `dry_run: true` is set in business.yaml. If dry run is active, save the post but do not trigger publishing. Report: "Post saved. Dry run mode is active -- will not auto-publish."

4. **Present the final post** to the user with all quality scores.

---

## Verification

Before reporting completion:

- [ ] Topic aligns with content calendar or user direction
- [ ] No overlap with recent posts (dedup check)
- [ ] Quality score >= 7/10 average across 4 dimensions
- [ ] All factual claims verified or labeled as assumptions
- [ ] Human touch check passed
- [ ] Post saved to data/posts/approved/
- [ ] Dry run status reported

---

## Completion Status

- **DONE** -- Post passed all gates, saved, and queued (or dry-run reported).
- **DONE_WITH_CONCERNS** -- Post passed but with caveats (e.g., one claim could not be fully verified, labeled as assumption).
- **BLOCKED** -- Post failed quality gates 3+ times or no business config available.
- **NEEDS_CONTEXT** -- Missing business.yaml, content calendar, or user topic direction.
