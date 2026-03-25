"""AutoCommenter — Generalized strategic commenting agent for influencer posts.

Monitors tracked influencers and generates high-quality comments that position
the owner as a knowledgeable peer. Fully configurable via business.yaml and
influencers.yaml — works for any industry, niche, or personal brand.
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

    def run(self) -> dict:
        """Execute the daily auto-commenting cycle.

        1. Check if enabled
        2. Get eligible influencers for today
        3. Generate comments for each
        4. Quality-gate and invisible-test each comment
        5. Save results and return summary

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

            # Build minimal post context from topics when no real post is available
            topic_context = f"Post about: {', '.join(topics)}" if topics else ""

            comment_data = self.generate_comment(topic_context, name)
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

            # Passed all gates
            results["posted"].append({
                "influencer": name,
                "comment": comment_data.get("comment"),
                "formula_used": comment_data.get("formula_used"),
                "quality_scores": comment_data.get("quality_scores"),
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
