# ETHOS.md -- LinkedIn Autopilot V2

> The philosophy, principles, and non-negotiable values behind this system.

---

## Why This Exists

LinkedIn Autopilot was built for people who would rather build their business than spend two hours a day writing posts and commenting on everyone else's. But it was NOT built to flood LinkedIn with AI slop. The entire system is designed around one principle: **produce content so good that a human would save it, even knowing a machine helped write it.**

Every architectural decision, every quality gate, every prompt instruction traces back to that principle.

---

## Core Beliefs

### 1. Authority Is Earned, Not Manufactured

This is not a content machine. It is an authority engine. The difference matters.

A content machine optimizes for volume -- more posts, more comments, more impressions. An authority engine optimizes for signal -- fewer posts, higher quality, deeper trust. One great post that earns saves and builds reputation is worth more than ten mediocre posts that scroll past.

The system produces ONE post per day. Not three. Not five. One. And it passes through multiple quality gates before it reaches LinkedIn.

### 2. Business Outcomes Are a Byproduct

Every agent in this system operates under the same rule: business outcomes (leads, DMs, clients) are a BYPRODUCT of consistently excellent content. They are never the goal of any individual post.

The content mix enforces this structurally:
- **40% Pure Value** -- AI discoveries, experiments, tool reviews. Zero mention of the business.
- **25% Use Cases and Stories** -- Real projects with specific details. Business context is natural, not promotional.
- **20% Industry Insight** -- Trends and contrarian takes through the owner's lens.
- **15% Hiring/Business** -- The ONLY posts where services or placement are mentioned.

If more than 25% of a batch has a business angle, the Quality Editor rejects the entire batch.

### 3. Titan Genome Voice DNA

The swipe library is not a template bank. It is a voice DNA system.

Nine (now eighteen) legendary copywriters -- Hormozi, Halbert, Ogilvy, Mueller, Schwartz, Brown, Abraham, Kurtz, Buchan -- have been studied, deconstructed, and encoded into style profiles. The agents do not copy these writers. They extract the underlying patterns -- hook structures, persuasion frameworks, narrative arcs, rhythm patterns -- and synthesize them into the owner's authentic voice.

The Mueller Storytelling Framework is the primary writing system:
1. Open with scene, not lesson.
2. One story, one insight. Go deeper, not wider.
3. Stay in "I" longer than comfortable.
4. Use parenthetical asides to reveal character.
5. Trust the reader to scale the story.
6. Find uncontrived spectacles.
7. Discernment over volume.

Every post is measured against this framework. The Quality Editor checks each of the seven principles explicitly.

### 4. The Invisible Test

Every piece of automated engagement -- comments, replies, interactions -- must pass the Invisible Test:

> "If someone read this comment knowing NOTHING about the owner's business, would they still think this person is smart and worth following?"

If yes, the comment ships. If no, it gets rewritten with more substance and less implicit self-promotion. This test is the firewall between strategic engagement and spam.

### 5. Quality Over Quantity, Always

The system has four layers of quality gates, and content must pass ALL of them:

1. **AI Quality Scoring** -- Four-dimension scoring (relevance, voice alignment, substance, specificity) with a minimum threshold of 7.0/10.
2. **The Invisible Test** -- Scans for promotional language and forbidden phrases.
3. **Forbidden Phrase Detection** -- Configurable blocklist prevents self-promotion from ever appearing in automated engagement.
4. **Lead Detection** -- AI plus keyword dual detection flags buying signals WITHOUT changing the reply tone. The reply stays valuable whether or not the commenter is a lead.

The Quality Editor scores content 0-100 with explicit penalties:
- Markdown artifacts in text: -5 per instance
- AI-telltale phrases: -3 per instance
- Missing contractions: -2
- Walls of text in posts: -3

Below 60 is an automatic rejection. Between 60-70 requires significant rework. Only content scoring 80+ ships with minor edits.

### 6. Anti-Slop by Design

The system has a comprehensive anti-AI-detection protocol baked into every writing prompt:

**Banned patterns:**
- "In today's rapidly evolving..." / "It's worth noting..." / "Let's dive in"
- "Moreover," / "Furthermore," / "Additionally," / "Consequently,"
- "seamless" / "holistic" / "paradigm shift" / "groundbreaking" / "supercharge"
- "What are your thoughts?" / "I'd love to hear your thoughts"

**Required human patterns:**
- Contractions always ("don't" not "do not")
- Varied sentence length (3-word mixed with 25-word)
- Fragments for rhythm ("Huge difference." / "Every single time.")
- Em dashes for parenthetical thoughts
- Specific times and dates ("Last Tuesday at 3pm" not "recently")
- Parenthetical asides that reveal character

If any part reads like it could be ChatGPT output, the Human Touch Checker rewrites it in the owner's voice.

### 7. Strategic Engagement, Not Vanity Engagement

Comments on influencer posts are not about getting noticed. They are about adding genuine value to the conversation.

The Auto Commenter operates under strict rules:
- NEVER mention the business, any product, or any service by name.
- NEVER pitch, promote, or include any call-to-action.
- NEVER say "Great post!" or any content-free opener.
- NEVER be sycophantic, fan-like, or obsequious.
- ALWAYS reference something specific from their post.
- ALWAYS add a specific insight from direct experience.
- Rate limited to max 3 comments per week per influencer.

The goal is double specificity: reference a specific point from their post AND add a specific detail from your own experience. Vague agreement is worthless. Specific agreement with an added layer is gold.

### 8. Self-Improvement Through Data

The Campaign Analyzer closes the feedback loop every week:

Create content --> Measure performance --> Analyze patterns --> Adjust strategy --> Repeat

This is not a set-and-forget system. It learns. Saves are weighted at 40% (highest signal), comments at 30%, engagement rate at 20%, consistency at 10%. Strategy adjustments are conservative -- max 10% swing per week in any direction -- because overcorrection kills consistency.

What works gets protected. What fails for 3+ consecutive weeks gets killed. Everything in between gets tested with clear hypotheses and success metrics.

### 9. Dry Run by Default

The system ships with `dry_run: true`. All engagement -- comments, replies, posts -- is generated, scored, and logged but NOT published until explicitly enabled. This is not optional safety theater. This is the default state.

You review the output. You verify the quality. You enable live mode only when you trust the system.

### 10. The 52 Rules

This project is governed by 52 operational rules. Every rule exists because something broke in production. Every rule has a scar behind it. Key principles from the rules:

- **No untested work ships.** Every build/fix must be tested as a hard pass/fail.
- **No fixes without root cause investigation.** Lazy fixes (timeouts, retries) only after root cause is resolved.
- **No fabricated data.** "I don't know" beats a wrong confident answer.
- **No duplicate content.** Verified via live screenshot or hard visual check.
- **No hardcoded timezones.** Read from config dynamically.
- **No orphaned code.** When replacing code, delete the old version in the same pass.
- **Anti-hallucination protocol.** Before claiming any status -- identify the proof command, run it, read the output, verify.

---

## What This System Is NOT

- It is NOT a content machine that pumps out volume.
- It is NOT a growth hack or engagement farming tool.
- It is NOT a replacement for genuine expertise and real experience.
- It is NOT a bot that posts generic AI advice.
- It is NOT a set-and-forget system that runs without oversight.

It is a force multiplier for someone who has real expertise, real stories, and real value to share -- but not enough hours in the day to write, edit, post, engage, analyze, and optimize manually.

---

## The Quality Bar

The example that sets the bar for every post this system generates:

> "I hired a developer two weeks ago. Last Friday he quit. This morning I finished his work in 30 minutes."

A real story told simply. Scene first. Tension. Resolution. Insight emerges from the experience. No hype. No pitch. The reader draws their own conclusions.

Every post should hit that bar. If it does not make you think "I'd save this myself," it does not ship.
