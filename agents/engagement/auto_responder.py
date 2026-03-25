"""AutoResponder — Generalized reply agent for comments on the owner's posts.

Monitors incoming comments, classifies them, generates personalized replies,
and flags high-intent leads for follow-up. Works for any industry or niche
via business.yaml configuration.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime

from agents.base import BaseAgent

logger = logging.getLogger(__name__)


class AutoResponder(BaseAgent):
    """Analyzes comments on the owner's posts and generates quality replies."""

    def __init__(self):
        super().__init__("auto_responder", prompt_file="auto_responder.md")
        self.config = self._load_yaml("business.yaml")

        # Responding settings from business.yaml
        responding = self.config.get("engagement", {}).get("auto_responding", {})
        self.enabled = responding.get("enabled", False)
        self.reply_speed = responding.get("reply_speed", "within_2hrs")
        self.skip_generic = responding.get("skip_generic_thanks", True)
        self.lead_detection = responding.get("lead_detection", True)
        self.max_replies_per_cycle = responding.get("max_replies_per_cycle", 20)
        self.quality_threshold = responding.get("quality_threshold", 7)

        # Lead detection keywords from config
        self.lead_signals = responding.get("lead_signals", [
            "how much",
            "pricing",
            "do you offer",
            "can you help",
            "looking for",
            "need help with",
            "interested in",
            "where can I",
            "how do I hire",
            "take on clients",
        ])

        # Owner info
        business = self.config.get("business", self.config)
        self.owner_name = business.get("owner_name", "")
        self.brand = business.get("brand", "")

    # ------------------------------------------------------------------
    # Core methods
    # ------------------------------------------------------------------

    def analyze_comment(self, comment: dict) -> dict:
        """Classify an incoming comment and determine the best reply strategy.

        Args:
            comment: Dict with keys like author, text, post_title, timestamp.

        Returns:
            Dict with comment_type, priority, is_lead, suggested_approach.
        """
        text = comment.get("text", "")
        author = comment.get("author", "Unknown")

        prompt = f"""Analyze this comment on {self.owner_name}'s LinkedIn post and classify it.

Comment author: {author}
Comment text: "{text}"
Post title: {comment.get('post_title', 'N/A')}

Classify the comment and determine the best response strategy.

Return valid JSON:
{{
  "comment_type": "supportive|question|experience|disagreement|thoughtful|generic|spam",
  "priority": "high|medium|low|skip",
  "is_lead": true/false,
  "lead_signals": ["list of detected buying signals if any"],
  "sentiment": "positive|neutral|negative",
  "key_points": ["what the commenter is saying"],
  "suggested_approach": "brief description of how to reply",
  "skip_reason": "reason if priority is skip, null otherwise"
}}"""
        try:
            return self.call_json(prompt)
        except Exception as e:
            logger.error(f"[auto_responder] failed to analyze comment from {author}: {e}")
            return {"comment_type": "unknown", "priority": "low", "is_lead": False, "error": str(e)}

    def generate_reply(self, comment: dict, analysis: dict) -> dict:
        """Generate a personalized reply based on comment analysis.

        Args:
            comment: The original comment dict.
            analysis: Output from analyze_comment().

        Returns:
            Dict with reply_text, quality_score, reasoning.
        """
        text = comment.get("text", "")
        author = comment.get("author", "Unknown")
        comment_type = analysis.get("comment_type", "unknown")
        approach = analysis.get("suggested_approach", "be genuine and add value")

        prompt = f"""Write a reply to this comment on {self.owner_name}'s LinkedIn post.

Comment author: {author}
Comment text: "{text}"
Comment type: {comment_type}
Suggested approach: {approach}

Rules:
- Reply as {self.owner_name} in first person
- 1-3 sentences maximum
- NEVER pitch, sell, or use "DM me" / "check out" / "we offer"
- NO generic openers like "Great question!" or "Thanks for sharing!"
- Reference something SPECIFIC from their comment
- Add genuine value — a detail, insight, or question they didn't have before
- Use contractions (I'm, we've, that's, don't)
- Be direct — no filler, no preamble

Return valid JSON:
{{
  "reply_text": "The actual reply to post",
  "quality_score": <0-10>,
  "reasoning": "Why this reply works (1 sentence)",
  "reply_type": "{comment_type}",
  "word_count": <number>
}}"""
        try:
            return self.call_json(prompt)
        except Exception as e:
            logger.error(f"[auto_responder] failed to generate reply to {author}: {e}")
            return {"error": str(e)}

    def flag_lead(self, comment: dict, analysis: dict) -> dict | None:
        """Flag a comment as a potential lead for follow-up.

        Checks both the AI analysis and keyword-based lead signals.

        Args:
            comment: The original comment dict.
            analysis: Output from analyze_comment().

        Returns:
            Lead record dict if flagged, None otherwise.
        """
        if not self.lead_detection:
            return None

        is_lead = analysis.get("is_lead", False)
        ai_signals = analysis.get("lead_signals", [])

        # Also check keyword-based signals
        text_lower = comment.get("text", "").lower()
        keyword_signals = [s for s in self.lead_signals if s.lower() in text_lower]

        if not is_lead and not keyword_signals:
            return None

        lead = {
            "author": comment.get("author", "Unknown"),
            "author_profile": comment.get("author_profile", ""),
            "comment_text": comment.get("text", ""),
            "post_title": comment.get("post_title", ""),
            "detected_signals": list(set(ai_signals + keyword_signals)),
            "priority": "high" if len(ai_signals) + len(keyword_signals) >= 2 else "medium",
            "flagged_at": datetime.now().isoformat(),
            "status": "new",
            "follow_up_action": "Review and send personalized DM within 24 hours",
        }

        logger.info(
            f"[auto_responder] LEAD flagged: {lead['author']} "
            f"(signals: {lead['detected_signals']})"
        )

        # Save lead to data/leads/
        safe_author = lead["author"].replace(" ", "_").lower()
        self.save_output(lead, "leads", f"{safe_author}_{self.today_str()}.json")

        return lead

    def _should_skip(self, comment: dict, analysis: dict) -> str | None:
        """Determine if a comment should be skipped.

        Returns:
            Reason string if should skip, None if should reply.
        """
        if analysis.get("priority") == "skip":
            return analysis.get("skip_reason", "Marked as skip by analysis")

        if analysis.get("comment_type") == "spam":
            return "Spam detected"

        if self.skip_generic and analysis.get("comment_type") == "generic":
            text = comment.get("text", "").strip()
            # Skip very short generic comments like "Great post!" or emoji-only
            if len(text) < 20:
                return "Generic short comment (skip_generic_thanks enabled)"

        return None

    def run(self, comments: list[dict] | None = None) -> dict:
        """Execute the auto-responding cycle.

        Args:
            comments: Optional list of comment dicts. If None, would normally
                      fetch from LinkedIn API / monitoring system.

        Returns:
            Summary dict with replies, leads, and skipped counts.
        """
        if not self.enabled:
            logger.info("[auto_responder] auto-responding is disabled in config")
            return {"status": "disabled", "message": "Auto-responding is disabled in business.yaml"}

        # In production, this would fetch new comments from the monitoring system.
        # For now, accept comments as input or return empty.
        if comments is None:
            logger.info("[auto_responder] no comments provided for this cycle")
            return {"status": "success", "message": "No new comments to process", "replies": 0}

        results = {
            "status": "success",
            "replies_posted": [],
            "leads_flagged": [],
            "skipped": [],
            "total_processed": 0,
            "run_timestamp": datetime.now().isoformat(),
        }

        for comment in comments[: self.max_replies_per_cycle]:
            results["total_processed"] += 1
            author = comment.get("author", "Unknown")

            # Step 1: Analyze the comment
            analysis = self.analyze_comment(comment)

            # Step 2: Check for leads (even if we skip the reply)
            lead = self.flag_lead(comment, analysis)
            if lead:
                results["leads_flagged"].append(lead)

            # Step 3: Check if we should skip
            skip_reason = self._should_skip(comment, analysis)
            if skip_reason:
                results["skipped"].append({"author": author, "reason": skip_reason})
                continue

            # Step 4: Generate reply
            reply_data = self.generate_reply(comment, analysis)

            if "error" in reply_data:
                results["skipped"].append({
                    "author": author,
                    "reason": f"Reply generation error: {reply_data['error']}",
                })
                continue

            # Step 5: Quality check
            quality = reply_data.get("quality_score", 0)
            if quality < self.quality_threshold:
                results["skipped"].append({
                    "author": author,
                    "reason": f"Below quality threshold ({quality}/{self.quality_threshold})",
                })
                continue

            # Passed all gates
            results["replies_posted"].append({
                "author": author,
                "reply": reply_data.get("reply_text"),
                "quality_score": quality,
                "reply_type": reply_data.get("reply_type"),
                "is_lead": lead is not None,
            })

        # Save cycle summary
        self.save_output(
            results,
            "replies",
            f"responder_cycle_{self.today_str()}_{datetime.now().strftime('%H%M')}.json",
        )

        posted = len(results["replies_posted"])
        leads = len(results["leads_flagged"])
        skipped = len(results["skipped"])
        logger.info(
            f"[auto_responder] cycle complete: {posted} replies, "
            f"{leads} leads flagged, {skipped} skipped "
            f"(out of {results['total_processed']} processed)"
        )
        return results
