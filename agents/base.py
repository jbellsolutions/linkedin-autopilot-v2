"""BaseAgent — shared foundation for all LinkedIn Autopilot agents.

Provides prompt loading with template rendering, Claude API calls,
and common file I/O helpers.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path

import anthropic
import yaml

logger = logging.getLogger(__name__)

# Project root is one level up from agents/
PROJECT_DIR = Path(__file__).resolve().parent.parent


class BaseAgent:
    """Base class that every agent inherits from."""

    def __init__(self, name: str, prompt_file: str | None = None):
        self.name = name
        self.client = anthropic.Anthropic()
        self.model = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-20250514")
        self.system_prompt = ""

        if prompt_file:
            self.system_prompt = self._load_prompt(prompt_file)

    # ------------------------------------------------------------------
    # Config helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _find_config(filename: str) -> Path | None:
        """Find a config file, checking config/ first then config_examples/."""
        for directory in ("config", "config_examples"):
            path = PROJECT_DIR / directory / filename
            if path.exists():
                return path
        return None

    @staticmethod
    def _load_yaml(filename: str) -> dict:
        """Load a YAML config file using the config search order."""
        path = BaseAgent._find_config(filename)
        if path is None:
            return {}
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}

    # ------------------------------------------------------------------
    # Prompt loading + template rendering
    # ------------------------------------------------------------------

    def _load_prompt(self, filename: str) -> str:
        """Load a prompt .md file from the prompts/ directory and render templates."""
        prompt_path = PROJECT_DIR / "prompts" / filename
        if not prompt_path.exists():
            logger.warning(f"[{self.name}] prompt file not found: {prompt_path}")
            return ""
        raw_text = prompt_path.read_text()
        return self._render_prompt(raw_text)

    def _render_prompt(self, raw_text: str) -> str:
        """Replace {{token}} placeholders with values from business.yaml.

        Looks for config/business.yaml first, then config_examples/business.yaml.
        If neither exists, returns the raw text unchanged.
        """
        biz = self._load_yaml("business.yaml")
        if not biz:
            return raw_text

        # Dig into nested keys safely
        business = biz.get("business", biz)  # support top-level or nested
        primary_offer = business.get("primary_offer", {})

        owner_name = business.get("owner_name", "")
        owner_first = owner_name.split()[0] if owner_name else ""

        replacements = {
            "{{owner_name}}": owner_name,
            "{{owner_first_name}}": owner_first,
            "{{brand}}": business.get("brand", ""),
            "{{business_name}}": business.get("business_name", ""),
            "{{primary_product}}": primary_offer.get("product", ""),
            "{{contact_email}}": business.get("contact", ""),
            "{{website}}": business.get("website", ""),
            "{{linkedin_url}}": business.get("linkedin", ""),
            "{{future_brand}}": business.get("future_brand", business.get("brand", "")),
        }

        text = raw_text
        for token, value in replacements.items():
            if value:
                text = text.replace(token, value)

        return text

    # ------------------------------------------------------------------
    # Claude API helpers
    # ------------------------------------------------------------------

    def call(self, prompt: str, max_tokens: int = 4096) -> str:
        """Send a prompt to Claude and return the text response."""
        messages = [{"role": "user", "content": prompt}]
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=self.system_prompt,
            messages=messages,
        )
        return response.content[0].text

    def call_json(self, prompt: str, max_tokens: int = 4096) -> dict | list:
        """Send a prompt and parse the JSON from the response."""
        raw = self.call(prompt, max_tokens=max_tokens)

        # Strip markdown fences if present
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            logger.error(f"[{self.name}] failed to parse JSON response:\n{raw[:500]}")
            return {"error": "JSON parse failed", "raw": raw}

    # ------------------------------------------------------------------
    # File I/O helpers
    # ------------------------------------------------------------------

    @staticmethod
    def today_str() -> str:
        return datetime.now().strftime("%Y-%m-%d")

    def save_output(self, data: dict | list, subdir: str, filename: str) -> Path:
        """Save JSON output to data/<subdir>/<filename>."""
        out_dir = PROJECT_DIR / "data" / subdir
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / filename
        with open(out_path, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"[{self.name}] saved output → {out_path}")
        return out_path
