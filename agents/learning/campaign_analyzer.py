"""CampaignAnalyzer — Self-learning agent that analyzes content performance
and generates actionable strategy recommendations.

Collects engagement metrics, identifies what works and what doesn't,
and produces weekly reports with concrete adjustments to the content
strategy. Designed to close the feedback loop between publishing and planning.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

from agents.base import BaseAgent

logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent


class CampaignAnalyzer(BaseAgent):
    """Analyzes campaign performance and generates strategy updates."""

    def __init__(self):
        super().__init__("campaign_analyzer", prompt_file="campaign_analyzer.md")
        self.config = self._load_yaml("business.yaml")

        # Learning settings from business.yaml
        learning = self.config.get("engagement", {}).get("campaign_learning", {})
        self.enabled = learning.get("enabled", False)
        self.analysis_window_days = learning.get("analysis_window_days", 7)
        self.min_posts_for_analysis = learning.get("min_posts_for_analysis", 3)
        self.track_metrics = learning.get("track_metrics", [
            "impressions", "likes", "comments", "shares", "saves", "click_through_rate",
        ])
        self.optimization_targets = learning.get("optimization_targets", [
            "saves", "comments", "shares",
        ])

        # Content philosophy from config (baseline to compare against)
        self.content_philosophy = self.config.get("content_philosophy", {})
        self.content_themes = self.config.get("content_themes", [])

        # Owner info
        business = self.config.get("business", self.config)
        self.owner_name = business.get("owner_name", "")

        # Browser automation for scraping engagement
        self._browser = None

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

    def scrape_post_engagement(self, post_url: str) -> dict:
        """Scrape engagement metrics for a specific post via browser automation."""
        try:
            browser = self._get_browser()
            engagement = browser.scrape_post_engagement(post_url)
            logger.info(f"[campaign_analyzer] Scraped engagement for {post_url}: {engagement}")
            return engagement
        except Exception as e:
            logger.error(f"[campaign_analyzer] Failed to scrape engagement for {post_url}: {e}")
            return {}

    def enrich_metrics_with_browser(self, metrics: list[dict]) -> list[dict]:
        """Enrich post metrics with live engagement data from LinkedIn.

        For any post that has a 'post_url' field, scrapes current engagement
        numbers and merges them into the metrics.
        """
        enriched_count = 0
        for post in metrics:
            post_url = post.get("post_url", "")
            if not post_url:
                continue
            engagement = self.scrape_post_engagement(post_url)
            if engagement:
                post["scraped_likes"] = engagement.get("likes", 0)
                post["scraped_comments"] = engagement.get("comments", 0)
                post["scraped_reposts"] = engagement.get("reposts", 0)
                post["scraped_impressions"] = engagement.get("impressions", 0)
                enriched_count += 1

        if enriched_count:
            logger.info(f"[campaign_analyzer] Enriched {enriched_count} posts with scraped data")
        return metrics

    # ------------------------------------------------------------------
    # Data collection
    # ------------------------------------------------------------------

    def collect_metrics(self, posts: list[dict] | None = None) -> list[dict]:
        """Collect performance metrics for recent posts.

        In production, this would pull from LinkedIn API, Airtable, or
        an analytics database. Accepts posts as input for flexibility.

        Args:
            posts: Optional list of post dicts with engagement data.
                   Each should have: title, content_type, theme, post_date,
                   and metric fields (impressions, likes, comments, etc.)

        Returns:
            Enriched list of post metrics with computed fields.
        """
        if posts is None:
            # Attempt to load from data/analytics/ directory
            analytics_dir = PROJECT_DIR / "data" / "analytics"
            posts = []
            if analytics_dir.exists():
                cutoff = datetime.now() - timedelta(days=self.analysis_window_days)
                for f in sorted(analytics_dir.glob("*.json"), reverse=True):
                    try:
                        with open(f) as fh:
                            post = json.load(fh)
                        post_date = post.get("post_date", "")
                        if post_date and datetime.fromisoformat(post_date) >= cutoff:
                            posts.append(post)
                    except (json.JSONDecodeError, ValueError):
                        continue

        if not posts:
            logger.info("[campaign_analyzer] no post data available for analysis")
            return []

        # Enrich with computed metrics
        for post in posts:
            impressions = post.get("impressions", 0)
            if impressions > 0:
                post["engagement_rate"] = round(
                    (post.get("likes", 0) + post.get("comments", 0) + post.get("shares", 0))
                    / impressions * 100, 2
                )
                post["save_rate"] = round(post.get("saves", 0) / impressions * 100, 2)
            else:
                post["engagement_rate"] = 0.0
                post["save_rate"] = 0.0

        logger.info(f"[campaign_analyzer] collected metrics for {len(posts)} posts")
        return posts

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    def analyze_performance(self, metrics: list[dict]) -> dict:
        """Analyze collected metrics and identify patterns.

        Uses Claude to generate insights about what content types,
        themes, formats, and posting times perform best.

        Args:
            metrics: Enriched post metrics from collect_metrics().

        Returns:
            Analysis dict with top_performers, underperformers, patterns,
            and theme_breakdown.
        """
        if len(metrics) < self.min_posts_for_analysis:
            return {
                "status": "insufficient_data",
                "message": f"Need at least {self.min_posts_for_analysis} posts, have {len(metrics)}",
            }

        metrics_summary = json.dumps(metrics, indent=2, default=str)

        prompt = f"""Analyze these LinkedIn post performance metrics for {self.owner_name}.

Analysis window: last {self.analysis_window_days} days
Optimization targets: {json.dumps(self.optimization_targets)}
Current content philosophy: {json.dumps(self.content_philosophy)}
Current themes: {json.dumps(self.content_themes)}

Post metrics:
{metrics_summary}

Provide a thorough analysis. Return valid JSON:
{{
  "summary": "2-3 sentence executive summary of performance this period",
  "top_performers": [
    {{
      "post_title": "title",
      "why_it_worked": "specific reasons",
      "replicable_elements": ["list of elements to reuse"]
    }}
  ],
  "underperformers": [
    {{
      "post_title": "title",
      "why_it_underperformed": "specific reasons",
      "improvement_suggestions": ["list of fixes"]
    }}
  ],
  "patterns": {{
    "best_content_type": "type with highest avg engagement",
    "best_theme": "theme with highest avg engagement",
    "best_posting_time": "time pattern if detectable",
    "optimal_post_length": "short|medium|long based on data",
    "hook_patterns_that_work": ["list of effective hook styles"],
    "cta_patterns_that_work": ["list of effective CTA styles"]
  }},
  "theme_breakdown": {{
    "theme_name": {{
      "avg_engagement_rate": 0.0,
      "avg_saves": 0,
      "post_count": 0,
      "trending": "up|down|stable"
    }}
  }},
  "engagement_comment_quality": "assessment of comment depth and quality"
}}"""
        try:
            return self.call_json(prompt, max_tokens=6000)
        except Exception as e:
            logger.error(f"[campaign_analyzer] analysis failed: {e}")
            return {"status": "error", "error": str(e)}

    # ------------------------------------------------------------------
    # Report generation
    # ------------------------------------------------------------------

    def generate_report(self, analysis: dict, metrics: list[dict]) -> dict:
        """Generate a human-readable weekly report.

        Combines raw metrics and AI analysis into a structured report
        suitable for email digest or dashboard display.

        Args:
            analysis: Output from analyze_performance().
            metrics: Enriched post metrics.

        Returns:
            Report dict with sections, recommendations, and scores.
        """
        total_posts = len(metrics)
        avg_engagement = (
            sum(m.get("engagement_rate", 0) for m in metrics) / total_posts
            if total_posts > 0
            else 0
        )
        total_saves = sum(m.get("saves", 0) for m in metrics)
        total_comments = sum(m.get("comments", 0) for m in metrics)
        total_impressions = sum(m.get("impressions", 0) for m in metrics)

        report = {
            "report_type": "weekly_campaign_analysis",
            "generated_at": datetime.now().isoformat(),
            "period": {
                "days": self.analysis_window_days,
                "start": (datetime.now() - timedelta(days=self.analysis_window_days)).strftime("%Y-%m-%d"),
                "end": self.today_str(),
            },
            "headline_metrics": {
                "total_posts": total_posts,
                "total_impressions": total_impressions,
                "total_saves": total_saves,
                "total_comments": total_comments,
                "avg_engagement_rate": round(avg_engagement, 2),
            },
            "analysis": analysis,
            "health_score": self._calculate_health_score(metrics, analysis),
        }

        return report

    def _calculate_health_score(self, metrics: list[dict], analysis: dict) -> dict:
        """Calculate an overall content health score (0-100).

        Weighs saves (40%), comments (30%), engagement rate (20%), consistency (10%).
        """
        if not metrics:
            return {"score": 0, "grade": "N/A", "breakdown": {}}

        total = len(metrics)
        avg_saves = sum(m.get("saves", 0) for m in metrics) / total
        avg_comments = sum(m.get("comments", 0) for m in metrics) / total
        avg_engagement = sum(m.get("engagement_rate", 0) for m in metrics) / total

        # Normalize to 0-100 (benchmarks: saves>5 great, comments>10 great, engagement>3% great)
        save_score = min(avg_saves / 5 * 100, 100)
        comment_score = min(avg_comments / 10 * 100, 100)
        engagement_score = min(avg_engagement / 3 * 100, 100)
        consistency_score = min(total / self.analysis_window_days * 100, 100)

        weighted = (
            save_score * 0.40
            + comment_score * 0.30
            + engagement_score * 0.20
            + consistency_score * 0.10
        )

        grade_map = [(90, "A+"), (80, "A"), (70, "B+"), (60, "B"), (50, "C"), (0, "D")]
        grade = next(g for threshold, g in grade_map if weighted >= threshold)

        return {
            "score": round(weighted, 1),
            "grade": grade,
            "breakdown": {
                "saves": round(save_score, 1),
                "comments": round(comment_score, 1),
                "engagement": round(engagement_score, 1),
                "consistency": round(consistency_score, 1),
            },
        }

    # ------------------------------------------------------------------
    # Strategy update
    # ------------------------------------------------------------------

    def update_content_strategy(self, analysis: dict) -> dict:
        """Generate concrete content strategy adjustments based on analysis.

        Produces specific, actionable recommendations that can be fed back
        into the content creation pipeline.

        Args:
            analysis: Output from analyze_performance().

        Returns:
            Strategy update dict with adjusted ratios, theme changes,
            and tactical recommendations.
        """
        prompt = f"""Based on this LinkedIn content performance analysis, generate specific
strategy adjustments for {self.owner_name}'s content pipeline.

Current content philosophy (% distribution):
{json.dumps(self.content_philosophy, indent=2)}

Current themes: {json.dumps(self.content_themes)}

Performance analysis:
{json.dumps(analysis, indent=2, default=str)}

Generate concrete, actionable strategy adjustments. Return valid JSON:
{{
  "content_mix_adjustments": {{
    "value_posts": <new %>,
    "authority_posts": <new %>,
    "engagement_posts": <new %>,
    "promotional_posts": <new %>
  }},
  "theme_adjustments": [
    {{
      "action": "increase|decrease|add|remove",
      "theme": "theme name",
      "reason": "why"
    }}
  ],
  "tactical_recommendations": [
    {{
      "category": "hooks|cta|format|timing|topic",
      "recommendation": "specific actionable advice",
      "expected_impact": "what improvement to expect",
      "priority": "high|medium|low"
    }}
  ],
  "experiments_to_run": [
    {{
      "hypothesis": "what to test",
      "method": "how to test it",
      "success_metric": "how to measure",
      "duration_days": <number>
    }}
  ],
  "stop_doing": ["things to stop based on data"],
  "double_down_on": ["things to do more of based on data"]
}}"""
        try:
            return self.call_json(prompt, max_tokens=6000)
        except Exception as e:
            logger.error(f"[campaign_analyzer] strategy update failed: {e}")
            return {"status": "error", "error": str(e)}

    # ------------------------------------------------------------------
    # Main run
    # ------------------------------------------------------------------

    def run(self, posts: list[dict] | None = None) -> dict:
        """Execute the full campaign analysis cycle.

        1. Collect metrics
        2. Analyze performance
        3. Generate report
        4. Generate strategy updates
        5. Save everything

        Args:
            posts: Optional list of post dicts with engagement data.

        Returns:
            Complete analysis results with report and strategy updates.
        """
        if not self.enabled:
            logger.info("[campaign_analyzer] campaign learning is disabled in config")
            return {"status": "disabled", "message": "Campaign learning is disabled in business.yaml"}

        logger.info("[campaign_analyzer] starting weekly analysis cycle")
        start = datetime.now()

        # Step 1: Collect
        metrics = self.collect_metrics(posts)
        if not metrics:
            return {
                "status": "no_data",
                "message": "No post data available for the analysis window",
            }

        # Step 1b: Enrich with live LinkedIn engagement data
        try:
            metrics = self.enrich_metrics_with_browser(metrics)
        except Exception as e:
            logger.warning(f"[campaign_analyzer] Browser enrichment failed (continuing without): {e}")

        # Step 2: Analyze
        analysis = self.analyze_performance(metrics)
        if analysis.get("status") == "insufficient_data":
            return analysis

        # Step 3: Report
        report = self.generate_report(analysis, metrics)

        # Step 4: Strategy update
        strategy = self.update_content_strategy(analysis)

        # Step 5: Save outputs
        date_str = self.today_str()
        self.save_output(report, "reports", f"weekly_report_{date_str}.json")
        self.save_output(strategy, "reports", f"strategy_update_{date_str}.json")
        self.save_output(metrics, "analytics", f"metrics_snapshot_{date_str}.json")

        elapsed = (datetime.now() - start).total_seconds()
        logger.info(
            f"[campaign_analyzer] analysis complete in {elapsed:.1f}s — "
            f"health score: {report.get('health_score', {}).get('score', 'N/A')}"
        )

        return {
            "status": "success",
            "report": report,
            "strategy_update": strategy,
            "posts_analyzed": len(metrics),
            "health_score": report.get("health_score", {}),
            "elapsed_seconds": elapsed,
        }
