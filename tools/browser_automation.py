"""
LinkedIn Browser Automation Layer
Supports two backends: Airtop (cloud-based) and Browser Use (local agent)
Configure via .env: BROWSER_BACKEND=airtop|browser_use
"""

import os
import json
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Rate limiter — shared across all browser actions
# ---------------------------------------------------------------------------

class RateLimiter:
    """Simple sliding-window rate limiter for browser actions."""

    def __init__(self, config: dict | None = None):
        config = config or {}
        self.comments_per_hour = config.get("comments_per_hour", 5)
        self.replies_per_hour = config.get("replies_per_hour", 10)
        self.dms_per_day = config.get("dms_per_day", 20)
        self._action_log: list[dict] = []

    def _prune(self):
        """Remove entries older than 24 hours."""
        cutoff = time.time() - 86400
        self._action_log = [e for e in self._action_log if e["ts"] > cutoff]

    def _count(self, action: str, window_seconds: int) -> int:
        cutoff = time.time() - window_seconds
        return sum(1 for e in self._action_log if e["action"] == action and e["ts"] > cutoff)

    def check(self, action: str) -> bool:
        """Return True if the action is allowed under current limits."""
        self._prune()
        if action == "comment":
            return self._count("comment", 3600) < self.comments_per_hour
        if action == "reply":
            return self._count("reply", 3600) < self.replies_per_hour
        if action == "dm":
            return self._count("dm", 86400) < self.dms_per_day
        return True

    def record(self, action: str):
        self._action_log.append({"action": action, "ts": time.time()})


# ---------------------------------------------------------------------------
# Unified interface
# ---------------------------------------------------------------------------

class LinkedInBrowser:
    """Unified interface for LinkedIn browser automation.

    Supports two backends:
    - Airtop: Cloud-based browser sessions with anti-detection, proxy rotation,
      and LinkedIn-specific session management. Better for scale and reliability.
    - Browser Use: Local AI-powered browser agent that can navigate LinkedIn
      autonomously. Better for complex multi-step flows and debugging.

    Usage:
        browser = LinkedInBrowser()
        browser.post_comment(post_url, comment_text)
        browser.reply_to_comment(post_url, comment_id, reply_text)
        comments = browser.scrape_post_comments(post_url)
        posts = browser.scrape_influencer_posts(profile_url, count=5)
    """

    def __init__(self, backend: str | None = None, rate_limit_config: dict | None = None):
        self.backend = backend or os.getenv("BROWSER_BACKEND", "airtop")
        self.rate_limiter = RateLimiter(rate_limit_config)

        if self.backend == "airtop":
            self.driver = AirtopDriver()
        elif self.backend == "browser_use":
            self.driver = BrowserUseDriver()
        else:
            raise ValueError(
                f"Unknown browser backend: {self.backend}. Use 'airtop' or 'browser_use'"
            )

        logger.info(f"LinkedIn browser initialized with backend: {self.backend}")

    # --- Public API ---------------------------------------------------------

    def post_comment(self, post_url: str, comment_text: str) -> dict:
        """Post a comment on a LinkedIn post. Returns success status and comment ID."""
        if not self.rate_limiter.check("comment"):
            logger.warning("[browser] Rate limit reached for comments — skipping")
            return {"error": "rate_limit", "message": "Comment rate limit reached"}
        result = self.driver.post_comment(post_url, comment_text)
        if not result.get("error"):
            self.rate_limiter.record("comment")
        return result

    def reply_to_comment(self, post_url: str, comment_id: str, reply_text: str) -> dict:
        """Reply to a specific comment on a LinkedIn post."""
        if not self.rate_limiter.check("reply"):
            logger.warning("[browser] Rate limit reached for replies — skipping")
            return {"error": "rate_limit", "message": "Reply rate limit reached"}
        result = self.driver.reply_to_comment(post_url, comment_id, reply_text)
        if not result.get("error"):
            self.rate_limiter.record("reply")
        return result

    def scrape_post_comments(self, post_url: str, max_comments: int = 50) -> list:
        """Scrape comments from a LinkedIn post. Returns list of comment dicts."""
        return self.driver.scrape_post_comments(post_url, max_comments)

    def scrape_influencer_posts(self, profile_url: str, count: int = 5) -> list:
        """Scrape recent posts from an influencer's LinkedIn profile."""
        return self.driver.scrape_influencer_posts(profile_url, count)

    def scrape_post_engagement(self, post_url: str) -> dict:
        """Get engagement metrics for a post (likes, comments, reposts, impressions)."""
        return self.driver.scrape_post_engagement(post_url)

    def check_notifications(self) -> list:
        """Check LinkedIn notifications for new comments on our posts."""
        return self.driver.check_notifications()

    def send_dm(self, profile_url: str, message: str) -> dict:
        """Send a direct message to a LinkedIn user."""
        if not self.rate_limiter.check("dm"):
            logger.warning("[browser] Rate limit reached for DMs — skipping")
            return {"error": "rate_limit", "message": "DM rate limit reached"}
        result = self.driver.send_dm(profile_url, message)
        if not result.get("error"):
            self.rate_limiter.record("dm")
        return result

    def get_session_status(self) -> dict:
        """Check if the browser session is active and authenticated."""
        return self.driver.get_session_status()


# ---------------------------------------------------------------------------
# Airtop backend
# ---------------------------------------------------------------------------

class AirtopDriver:
    """Airtop cloud browser backend.

    Requires: AIRTOP_API_KEY in .env

    Airtop provides:
    - Cloud-hosted browser sessions with anti-detection
    - Proxy rotation and residential IPs
    - LinkedIn session persistence
    - Built-in rate limiting
    - API-driven interactions
    """

    def __init__(self):
        self.api_key = os.getenv("AIRTOP_API_KEY")
        if not self.api_key:
            raise ValueError("AIRTOP_API_KEY not set in .env")
        self.base_url = "https://api.airtop.ai/v1"
        self.session_id: str | None = None
        self._init_session()

    # --- Session management --------------------------------------------------

    def _init_session(self):
        """Initialize or resume an Airtop browser session."""
        import requests

        try:
            resp = requests.post(
                f"{self.base_url}/sessions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "configuration": {
                        "persistSession": True,
                        "profileName": "linkedin_autopilot",
                        "proxy": {"type": "residential"},
                        "timeoutMinutes": 30,
                    }
                },
                timeout=30,
            )
            if resp.status_code == 200:
                self.session_id = resp.json().get("data", {}).get("id")
                logger.info(f"Airtop session initialized: {self.session_id}")
            else:
                logger.error(f"Airtop session init failed: {resp.status_code} {resp.text}")
        except Exception as e:
            logger.error(f"Airtop connection error: {e}")

    def _execute(self, action: str, params: dict) -> dict:
        """Execute a browser action via the Airtop API."""
        import requests

        if not self.session_id:
            self._init_session()
            if not self.session_id:
                return {"error": "No active Airtop session"}

        try:
            resp = requests.post(
                f"{self.base_url}/sessions/{self.session_id}/actions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={"action": action, "params": params},
                timeout=60,
            )
            if resp.status_code == 200:
                return resp.json()
            return {"error": resp.text, "status": resp.status_code}
        except Exception as e:
            return {"error": str(e)}

    # --- LinkedIn actions ----------------------------------------------------

    def post_comment(self, post_url: str, comment_text: str) -> dict:
        return self._execute("linkedin_comment", {
            "url": post_url,
            "text": comment_text,
            "humanize_typing": True,
            "delay_range_ms": [500, 2000],
        })

    def reply_to_comment(self, post_url: str, comment_id: str, reply_text: str) -> dict:
        return self._execute("linkedin_reply", {
            "url": post_url,
            "comment_id": comment_id,
            "text": reply_text,
            "humanize_typing": True,
        })

    def scrape_post_comments(self, post_url: str, max_comments: int = 50) -> list:
        result = self._execute("linkedin_scrape_comments", {
            "url": post_url,
            "max_items": max_comments,
        })
        return result.get("data", {}).get("comments", [])

    def scrape_influencer_posts(self, profile_url: str, count: int = 5) -> list:
        result = self._execute("linkedin_scrape_posts", {
            "url": profile_url,
            "max_items": count,
            "include_engagement": True,
        })
        return result.get("data", {}).get("posts", [])

    def scrape_post_engagement(self, post_url: str) -> dict:
        result = self._execute("linkedin_scrape_engagement", {"url": post_url})
        return result.get("data", {})

    def check_notifications(self) -> list:
        result = self._execute("linkedin_notifications", {"filter": "comments"})
        return result.get("data", {}).get("notifications", [])

    def send_dm(self, profile_url: str, message: str) -> dict:
        return self._execute("linkedin_dm", {
            "url": profile_url,
            "text": message,
            "humanize_typing": True,
        })

    def get_session_status(self) -> dict:
        import requests

        if not self.session_id:
            return {"status": "no_session"}
        try:
            resp = requests.get(
                f"{self.base_url}/sessions/{self.session_id}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=15,
            )
            if resp.status_code == 200:
                return resp.json()
            return {"status": "error", "code": resp.status_code}
        except Exception:
            return {"status": "disconnected"}


# ---------------------------------------------------------------------------
# Browser Use backend
# ---------------------------------------------------------------------------

class BrowserUseDriver:
    """Browser Use local AI agent backend.

    Requires: BROWSER_USE_API_KEY or OPENAI_API_KEY in .env

    Browser Use provides:
    - Local AI-powered browser agent
    - Natural language task execution
    - Autonomous navigation and interaction
    - Screenshot-based verification
    - Better for complex multi-step flows
    """

    def __init__(self):
        self.api_key = os.getenv("BROWSER_USE_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning(
                "No BROWSER_USE_API_KEY or OPENAI_API_KEY set — Browser Use may not function"
            )
        self.browser = None
        self._agent_class = None
        self._setup_browser()

    def _setup_browser(self):
        """Initialize Browser Use agent."""
        try:
            from browser_use import Agent as BUAgent, Browser, BrowserConfig

            self.browser_config = BrowserConfig(
                headless=True,
                disable_security=False,
            )
            self.browser = Browser(config=self.browser_config)
            self._agent_class = BUAgent
            logger.info("Browser Use initialized successfully")
        except ImportError:
            logger.warning(
                "browser-use package not installed. Install with: pip install browser-use"
            )

    # --- Task execution ------------------------------------------------------

    async def _run_task(self, task: str) -> dict:
        """Run a natural language task via the Browser Use agent."""
        if not self._agent_class:
            return {"error": "browser-use not installed"}
        try:
            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(model="gpt-4o", api_key=self.api_key)
            agent = self._agent_class(task=task, llm=llm, browser=self.browser)
            result = await agent.run()
            return {"success": True, "result": str(result)}
        except Exception as e:
            logger.error(f"[browser_use] task failed: {e}")
            return {"error": str(e)}

    def _run_sync(self, task: str) -> dict:
        """Synchronous wrapper for async task execution."""
        import asyncio

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return pool.submit(asyncio.run, self._run_task(task)).result()
            else:
                return asyncio.run(self._run_task(task))
        except RuntimeError:
            # No event loop exists yet
            return asyncio.run(self._run_task(task))
        except Exception as e:
            return {"error": str(e)}

    def _parse_json_result(self, result: dict, fallback=None):
        """Try to parse a JSON string from the Browser Use result."""
        if not result.get("success"):
            return fallback if fallback is not None else result
        raw = result.get("result", "")
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            # Try to extract JSON from mixed text
            for start_char, end_char in [("[", "]"), ("{", "}")]:
                idx_start = raw.find(start_char)
                idx_end = raw.rfind(end_char)
                if idx_start != -1 and idx_end > idx_start:
                    try:
                        return json.loads(raw[idx_start : idx_end + 1])
                    except json.JSONDecodeError:
                        continue
            return fallback if fallback is not None else raw

    # --- LinkedIn actions ----------------------------------------------------

    def post_comment(self, post_url: str, comment_text: str) -> dict:
        return self._run_sync(
            f"Go to this LinkedIn post: {post_url}\n"
            f"Click the comment box, type this comment (with natural typing speed), "
            f"then click Post:\n"
            f"{comment_text}\n"
            f"Wait for the comment to appear. Return JSON: "
            f'{{"success": true/false, "message": "description of what happened"}}'
        )

    def reply_to_comment(self, post_url: str, comment_id: str, reply_text: str) -> dict:
        return self._run_sync(
            f"Go to this LinkedIn post: {post_url}\n"
            f"Find the comment with ID or matching text: {comment_id}\n"
            f"Click Reply on that comment, type this reply, then click Post:\n"
            f"{reply_text}\n"
            f"Return JSON: "
            f'{{"success": true/false, "message": "description of what happened"}}'
        )

    def scrape_post_comments(self, post_url: str, max_comments: int = 50) -> list:
        result = self._run_sync(
            f"Go to this LinkedIn post: {post_url}\n"
            f"Scroll through and collect up to {max_comments} comments.\n"
            f"For each comment, extract: author name, author headline, "
            f"comment text, timestamp, number of likes.\n"
            f"Return the results as a JSON array of objects with keys: "
            f"author, headline, text, timestamp, likes."
        )
        parsed = self._parse_json_result(result, fallback=[])
        return parsed if isinstance(parsed, list) else []

    def scrape_influencer_posts(self, profile_url: str, count: int = 5) -> list:
        result = self._run_sync(
            f"Go to this LinkedIn profile: {profile_url}\n"
            f"Scroll through their recent activity/posts.\n"
            f"Collect the {count} most recent posts.\n"
            f"For each post, extract: post text (first 500 chars), post URL, "
            f"engagement counts (likes, comments, reposts), timestamp.\n"
            f"Return as a JSON array of objects with keys: "
            f"text, url, likes, comments, reposts, timestamp."
        )
        parsed = self._parse_json_result(result, fallback=[])
        return parsed if isinstance(parsed, list) else []

    def scrape_post_engagement(self, post_url: str) -> dict:
        result = self._run_sync(
            f"Go to this LinkedIn post: {post_url}\n"
            f"Extract: number of likes/reactions, comments count, reposts count, "
            f"and impressions if visible.\n"
            f"Return as a JSON object with keys: likes, comments, reposts, impressions."
        )
        parsed = self._parse_json_result(result, fallback={})
        return parsed if isinstance(parsed, dict) else {}

    def check_notifications(self) -> list:
        result = self._run_sync(
            "Go to LinkedIn notifications page (linkedin.com/notifications).\n"
            "Filter for comment notifications.\n"
            "Collect the 20 most recent comment notifications.\n"
            "For each: extract post title/snippet, commenter name, comment preview, "
            "timestamp, post URL.\n"
            "Return as a JSON array of objects with keys: "
            "post_title, commenter, comment_preview, timestamp, post_url."
        )
        parsed = self._parse_json_result(result, fallback=[])
        return parsed if isinstance(parsed, list) else []

    def send_dm(self, profile_url: str, message: str) -> dict:
        return self._run_sync(
            f"Go to this LinkedIn profile: {profile_url}\n"
            f"Click the Message button to open the messaging window.\n"
            f"Type this message with natural typing speed, then click Send:\n"
            f"{message}\n"
            f"Return JSON: "
            f'{{"success": true/false, "message": "description of what happened"}}'
        )

    def get_session_status(self) -> dict:
        result = self._run_sync(
            "Go to linkedin.com. Check if we are logged in by looking for the "
            "profile icon or 'Sign In' button. "
            'Return JSON: {"authenticated": true/false, "profile_name": "name if logged in"}'
        )
        parsed = self._parse_json_result(result, fallback={"status": "unknown"})
        return parsed if isinstance(parsed, dict) else {"status": "unknown"}
