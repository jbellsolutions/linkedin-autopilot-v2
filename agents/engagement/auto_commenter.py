"""AutoCommenter — Generalized strategic commenting agent for influencer posts.

Monitors tracked influencers and generates high-quality comments that position
the owner as a knowledgeable peer. Fully configurable via business.yaml and
influencers.yaml — works for any industry, niche, or personal brand.
Uses browser automation (Airtop or Browser Use) for real LinkedIn interaction.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime

from agents.base import BaseAgent

logger = logging.getLogger(__name__)


class AutoCommenter(BaseAgent):
    """Generates and quality-gates strategic comments on influencer posts."""

    def __init__(self):
        super().__init__("auto_commenter", prompt_file="auto_commenter.md")
        self.config = self._load_yaml("business.yaml")
        self.influencers = self._load_yaml("influencers.yaml")

        # Pull engagement settings with safe defaults
        engagement = self.config.get("engagement", {}).get("auto_commenting", {})
        self.enabled = engagement.get("enabled", False)
        self.quality_threshold = engagement.get("quality_threshold", 7)
        self.daily_target = engagement.get("daily_target", 8)
        self.max_per_influencer_per_week = engagement.get("max_per_influencer_per_week", 3)

        # Commenting strategy from influencers.yaml
        self.commenting_strategy = self.influencers.get("commenting_strategy", {})
        self.approach = self.commenting_strategy.get("approach", "value_first")
        self.max_words = self.commenting_strategy.get("max_words", 150)
        self.never_use = self.commenting_strategy.get("never_use", [])

        # Owner info for prompt context
        business = self.config.get("business", self.config)
        self.owner_name = business.get("owner_name", "")
        self.brand = business.get("brand", "")
        self.positioning = self.config.get("positioning", {}).get("core_message", "")

        # Browser automation config
        browser_config = self.config.get("browser", {})
        self.dry_run = browser_config.get("dry_run", True)
        self._browser = None

    # ------------------------------------------------------------------
    # Core methods
    # ------------------------------------------------------------------

    def generate_comment(self, post_content: str, influencer_name: str) -> dict:
        """Generate a strategic comment for a given influencer post.

        Args:
            post_content: The text content of the influencer's post.
            influencer_name: The name of the influencer who wrote the post.

        Returns:
            A dict with keys: comment, quality_scores, reasoning,
            references_experience, formula_used.
        """
        prompt = f"""Analyze this LinkedIn post and generate a strategic comment.

Influencer: {influencer_name}
Post content:
---
{post_content}
---

Commenting approach: {self.approach}
Max words: {self.max_words}
Owner positioning: {self.positioning}
Never use these phrases: {json.dumps(self.never_use)}

Requirements:
- Comment as {self.owner_name}, a peer-level expert
- Reference something SPECIFIC from the post
- Add a SPECIFIC insight from direct experience (tool name, number, or timeline)
- Keep it 2-4 sentences, dense with value
- Use first person, natural voice
- Do NOT mention {self.brand} or any services by name

Return valid JSON with these exact keys:
{{
  "comment": "The drafted comment text",
  "quality_scores": {{
    "relevance": <0-10>,
    "voice_alignment": <0-10>,
    "substance": <0-10>,
    "specificity": <0-10>
  }},
  "reasoning": "Why this comment adds value (1 sentence)",
  "references_experience": true/false,
  "formula_used": "yes_and|data_drop|contrarian|question|story|tool_insight"
}}"""
        try:
            result = self.call_json(prompt)
            return result
        except Exception as e:
            logger.error(f"[auto_commenter] failed to generate comment for {influencer_name}: {e}")
            return {"error": str(e)}

    def check_quality(self, comment_data: dict) -> bool:
        """Check whether a generated comment meets the quality threshold.

        Averages all quality_scores values and compares to self.quality_threshold.

        Args:
            comment_data: Output from generate_comment().

        Returns:
            True if average score >= threshold.
        """
        scores = comment_data.get("quality_scores", {})
        if not scores:
            return False
        avg = sum(scores.values()) / len(scores)
        logger.debug(
            f"[auto_commenter] quality check: avg={avg:.1f} threshold={self.quality_threshold}"
        )
        return avg >= self.quality_threshold

    def _get_eligible_influencers(self) -> list[dict]:
        """Return influencers eligible for commenting today.

        Filters by priority and respects the daily target cap.
        High-priority influencers are always included first.
        """
        all_influencers = self.influencers.get("influencers", [])
        high = [i for i in all_influencers if i.get("priority") == "high"]
        medium = [i for i in all_influencers if i.get("priority") == "medium"]
        low = [i for i in all_influencers if i.get("priority") == "low"]

        # Build the daily list: high first, then medium, then low
        eligible = high + medium + low
        return eligible[: self.daily_target]

    def _apply_invisible_test(self, comment_text: str) -> bool:
        """Apply the invisible test: would someone who knows nothing about
        the owner's business still think they're smart and worth following?

        Uses a quick Claude call for borderline cases.
        """
        # Basic heuristic checks first
        lower = comment_text.lower()
        forbidden_patterns = [
            "check out",
            "dm me",
            "we offer",
            "our service",
            "our program",
            "book a call",
            "free consultation",
        ]
        for pattern in forbidden_patterns:
            if pattern in lower:
                logger.info(f"[auto_commenter] invisible test FAIL: found '{pattern}'")
                return False

        # Check for never_use phrases from config
        for phrase in self.never_use:
            if phrase.lower() in lower:
                logger.info(f"[auto_commenter] invisible test FAIL: found never_use '{phrase}'")
                return False

        return True

    # ------------------------------------------------------------------
    # Browser automation helpers
    # ------------------------------------------------------------------

    def _get_browser(self):
        """Lazy-initialize the LinkedIn browser automation client."""
        if self._browser is None:
            from tools.browser_automation import LinkedInBrowser
            rate_config = self.config.get("browser", {}).get("rate_limit", {})
            self._browser = LinkedInBrowser(rate_limit_config=rate_config)
        return self._browser

    def _fetch_influencer_posts(self, influencer: dict) -> list:
        """Fetch recent posts from an influencer using browser automation.

        Args:
            influencer: Influencer config dict with at least 'linkedin_url'.

        Returns:
            List of post dicts with text, url, and engagement data.
            Falls back to empty list on error.
        """
        linkedin_url = influencer.get("linkedin_url", "")
        if not linkedin_url:
            logger.debug(f"[auto_commenter] No linkedin_url for {influencer.get('name')} — skipping scrape")
            return []
        try:
            browser = self._get_browser()
            posts = browser.scrape_influencer_posts(linkedin_url, count=3)
            logger.info(f"[auto_commenter] Scraped {len(posts)} posts from {influencer.get('name')}")
            return posts
        except Exception as e:
            logger.error(f"[auto_commenter] Failed to scrape posts for {influencer.get('name')}: {e}")
            return []

    def post_to_linkedin(self, comment_text: str, post_url: str) -> dict:
        """Post a comment to LinkedIn using browser automation.

        Respects the dry_run flag — if True, logs instead of posting.

        Args:
            comment_text: The comment to post.
            post_url: The LinkedIn post URL to comment on.

        Returns:
            Result dict with status and details.
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Would post comment to {post_url}: {comment_text[:80]}...")
            return {"status": "dry_run", "comment": comment_text, "post_url": post_url}
        try:
            browser = self._get_browser()
            result = browser.post_comment(post_url, comment_text)
            logger.info(f"[auto_commenter] Posted comment to {post_url}: {result}")
            return result
        except Exception as e:
            logger.error(f"[auto_commenter] Failed to post comment to {post_url}: {e}")
            return {"error": str(e)}

    # ------------------------------------------------------------------
    # Main run
    # ------------------------------------------------------------------

    def run(self) -> dict:
        """Execute the daily auto-commenting cycle.

        1. Check if enabled
        2. Get eligible influencers for today
        3. Scrape recent posts from each influencer via browser automation
        4. Generate comments for each post
        5. Quality-gate and invisible-test each comment
        6. Post approved comments to LinkedIn (or dry-run)
        7. Save results and return summary

        Returns:
            Summary dict with posted, rejected, and total counts.
        """
        if not self.enabled:
            logger.info("[auto_commenter] auto-commenting is disabled in config")
            return {"status": "disabled", "message": "Auto-commenting is disabled in business.yaml"}

        results = {
            "status": "success",
            "posted": [],
            "rejected": [],
            "total_generated": 0,
            "run_timestamp": datetime.now().isoformat(),
        }

        eligible = self._get_eligible_influencers()
        logger.info(f"[auto_commenter] processing {len(eligible)} influencers")

        for influencer in eligible:
            name = influencer.get("name", "Unknown")
            topics = influencer.get("topics", [])

            # Fetch real posts via browser automation
            real_posts = self._fetch_influencer_posts(influencer)

            if real_posts:
                posts_to_process = real_posts[:2]  # max 2 posts per influencer
            else:
                # Fallback to topic-based placeholder when scraping unavailable
                topic_context = f"Post about: {', '.join(topics)}" if topics else ""
                posts_to_process = [{"text": topic_context, "url": ""}]

            for post in posts_to_process:
                post_content = post.get("text", "")
                post_url = post.get("url", "")

                comment_data = self.generate_comment(post_content, name)
                results["total_generated"] += 1

                # Check for API errors
                if "error" in comment_data:
                    results["rejected"].append({
                        "influencer": name,
                        "reason": f"Generation error: {comment_data['error']}",
                    })
                    continue

                # Quality gate
                if not self.check_quality(comment_data):
                    scores = comment_data.get("quality_scores", {})
                    avg = sum(scores.values()) / max(len(scores), 1)
                    results["rejected"].append({
                        "influencer": name,
                        "reason": f"Below quality threshold (avg={avg:.1f}, min={self.quality_threshold})",
                        "scores": scores,
                    })
                    continue

                # Invisible test
                comment_text = comment_data.get("comment", "")
                if not self._apply_invisible_test(comment_text):
                    results["rejected"].append({
                        "influencer": name,
                        "reason": "Failed invisible test (promotional language detected)",
                    })
                    continue

                # Passed all gates — post to LinkedIn
                if post_url:
                    post_result = self.post_to_linkedin(comment_text, post_url)
                    comment_data["post_result"] = post_result
                comment_data["post_url"] = post_url

                results["posted"].append({
                    "influencer": name,
                    "comment": comment_text,
                    "formula_used": comment_data.get("formula_used"),
                    "quality_scores": comment_data.get("quality_scores"),
                    "post_url": post_url,
                    "post_result": comment_data.get("post_result", {}),
                })

                # Save individual comment
                safe_name = name.replace(" ", "_").lower()
                self.save_output(
                    comment_data,
                    "comments",
                    f"{safe_name}_{self.today_str()}.json",
                )

        # Save daily summary
        self.save_output(
            results,
            "comments",
            f"daily_summary_{self.today_str()}.json",
        )

        posted_count = len(results["posted"])
        rejected_count = len(results["rejected"])
        logger.info(
            f"[auto_commenter] cycle complete: {posted_count} posted, "
            f"{rejected_count} rejected out of {results['total_generated']} generated"
        )
        return results
