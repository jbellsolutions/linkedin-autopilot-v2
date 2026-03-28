# CONTRIBUTING.md -- LinkedIn Autopilot V2

> How to add agents, prompts, swipe entries, config presets, and integrations.

---

## Before You Start

Read these files first. They are non-negotiable context:

- `CLAUDE.md` -- The 52 operational rules that govern all agent behavior.
- `rules/RULES.md` -- Expanded rule explanations with root cause context.
- `ETHOS.md` -- The philosophy behind the system. Quality over quantity. Authority over volume.
- `ARCHITECTURE.md` -- System architecture, data flow, and component map.

Key rules that affect all contributions:

- **Rule 8**: Every build/fix must be tested as a hard pass/fail. No untested work ships.
- **Rule 47**: Present design before writing code. Every project.
- **Rule 49**: When replacing code, delete the old version in the same pass. No orphans.
- **Rule 50**: Never hardcode timezones. Read from config dynamically.

---

## Adding a New Agent

### Step 1: Create the Prompt

All agent behavior is defined by prompts in `prompts/`. Create a new `.md` file:

```
prompts/your_agent_name.md
```

**Required sections in every prompt:**

1. **Identity** -- Who the agent is, what persona it operates under.
2. **Core Philosophy** -- What drives its decisions. Link back to the content philosophy (authority over promotion).
3. **Instructions** -- What specifically the agent does, step by step.
4. **Quality Criteria** -- How the agent's output is evaluated.
5. **Hard Rules** -- Non-negotiable constraints (NEVER/ALWAYS lists).
6. **Output Format** -- JSON schema for structured output. Every agent must return valid JSON.

**Template variables available:**

| Variable | Source | Example |
|---|---|---|
| `{{owner_name}}` | `business.yaml` | "Josh Bell" |
| `{{owner_first_name}}` | `business.yaml` | "Josh" |
| `{{brand}}` | `business.yaml` | "JBell Solutions" |
| `{{business_name}}` | `business.yaml` | "JBell Solutions" |

Add new variables by extending the template context in `BaseAgent._load_prompt()`.

### Step 2: Create the Agent Class

Create a Python file in the appropriate subdirectory:

```
agents/
  engagement/your_agent.py     # For engagement agents
  learning/your_agent.py       # For learning/analytics agents
  influencer/your_agent.py     # For influencer-related agents
  your_agent.py                # For content pipeline agents
```

**Inherit from BaseAgent:**

```python
from agents.base import BaseAgent

class YourAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="your_agent",
            prompt_file="your_agent_name.md"  # Matches prompts/ filename
        )

    def run(self, **kwargs):
        """Main execution method. Called by scheduler or manual runner."""
        # Load config
        config = self._load_yaml("business.yaml")

        # Call Claude
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=self.system_prompt,
            messages=[{"role": "user", "content": "Your input here"}]
        )

        # Parse structured JSON output
        result = self._parse_json(response.content[0].text)

        # Save output
        self._save_json(f"data/your_output/{self._today()}.json", result)

        return result
```

**Requirements:**
- Every agent MUST have a `run()` method.
- Every agent MUST return structured data (dict or list).
- Every agent MUST save its output to the appropriate `data/` subdirectory.
- Every agent MUST handle errors gracefully (try/except with logging, not silent failures).

### Step 3: Wire Into a Team

Teams orchestrate multiple agents. Edit the appropriate team file in `teams/`:

```python
# teams/content_team.py or teams/engagement_team.py
from agents.your_agent import YourAgent

def run_your_pipeline():
    agent = YourAgent()
    return agent.run()
```

### Step 4: Register the Schedule

Add a cron job in the appropriate scheduler:

- Content pipeline agents go in `scheduler.py`
- Engagement and learning agents go in `scheduler_engagement.py`

```python
from teams.your_team import run_your_pipeline

scheduler.add_job(
    run_your_pipeline,
    CronTrigger(hour=10, minute=0, timezone=tz),  # NEVER hardcode timezone
    id="your_pipeline",
    name="Your Pipeline (description)",
    misfire_grace_time=1800,
    replace_existing=True,
)
```

### Step 5: Add Manual Runner

Update `main.py` to support `--run your_agent`:

```python
# In the runners dict inside run_team()
"your_agent": ("Your Agent Name", run_your_pipeline),
```

### Step 6: Test

```bash
python main.py --run your_agent
```

Verify:
- Agent loads its prompt without template errors.
- Agent calls Claude and gets a valid response.
- Output is valid JSON matching the prompt's schema.
- Output is saved to the correct `data/` directory.
- No hardcoded timezones, API keys, or file paths.

---

## Adding a New Prompt

If you are modifying an existing agent's behavior (not creating a new agent):

1. Edit the `.md` file in `prompts/`.
2. Test the agent with `python main.py --run <team>`.
3. Compare output quality before and after.
4. If the prompt change affects content quality scoring, run a batch test and verify scores.

**Prompt writing rules:**

- Use `{{variable}}` syntax for all dynamic values. Never hardcode business names, owner names, or config values.
- Every prompt must specify an output format as a JSON schema in a code block.
- Include a "Hard Rules" section with explicit NEVER/ALWAYS constraints.
- Include quality criteria with scoring dimensions and thresholds.
- Follow the Anti-Slop Writing Protocol: ban AI-telltale phrases, require contractions, enforce human writing patterns.

---

## Adding Swipe Library Entries

The swipe library lives in `swipe_library/` with author-specific codexes in `swipe_library/codex/`.

### Adding Entries to an Existing Author

1. Navigate to the author's directory: `swipe_library/codex/<author_name>/`
2. Add entries following the existing format (JSON array of pattern objects).
3. Run the library rebuild: `python3 scripts/build_library.py` (if available) or update `swipe_database.json` directly.
4. Update `SWIPE_FILE_CONTEXT.md` with the new entry count.

### Adding a New Author

1. Create a new directory: `swipe_library/codex/<author_name>/`
2. Add the raw content files following the existing author structure.
3. Add the author profile to `swipe_library/configs/authors.json`:
   ```json
   {
     "key": "author_name",
     "name": "Full Name",
     "entries": 0,
     "specialties": ["specialty1", "specialty2"],
     "style_traits": {
       "tone": "description",
       "sentence_length": "short|medium|long|varied",
       "hook_patterns": ["pattern1", "pattern2"],
       "persuasion_techniques": ["technique1", "technique2"]
     },
     "best_for": ["use_case_1", "use_case_2"]
   }
   ```
4. Add a style analysis entry to `swipe_library/style_analysis.json`.
5. Update the agent context in `swipe_library/swipe_file_agent_context.json`.
6. Update `SWIPE_FILE_CONTEXT.md` with the new author, entry count, and specialties.
7. Update the Swipe Strategist prompt (`prompts/swipe_strategist.md`) if the new author's patterns warrant specific matching rules.

---

## Adding Config Presets

Industry presets live in `setup/industry_presets/` and are used by the setup wizard.

### Creating a New Preset

1. Create a new YAML file: `setup/industry_presets/<industry>.yaml`
2. Include ALL of the following sections:

```yaml
# Industry name and description
industry: "Your Industry Name"
description: "One-line description"

# Content themes specific to this industry
content_themes:
  - theme: "Theme Name"
    description: "What this theme covers"
    content_mix: "pure_value_40"  # Which category it maps to

# Pre-configured influencer list
influencers:
  - name: "Influencer Name"
    linkedin_url: "https://linkedin.com/in/handle"
    topics: ["topic1", "topic2"]

# Trend search queries
trend_queries:
  - query: "industry-specific search query"
    category: "ai_tools|industry_move|etc"

# Tone and voice defaults
tone_defaults:
  formality: "casual|professional|mixed"
  personality_traits: ["trait1", "trait2"]

# Engagement defaults
engagement_defaults:
  commenting_frequency: "2x_daily"
  reply_style: "peer|mentor|contributor"

# Sample case studies (for the Post Writer to reference)
sample_case_studies:
  - title: "Case study title"
    summary: "Brief summary"
    specificity_stack:
      tools: ["Tool1"]
      timeline: "2 weeks"
      result: "Specific outcome"
```

3. Register the preset in `setup/wizard.py` so it appears in the interactive wizard.
4. Test by running `python setup.py` and selecting the new preset.

---

## Adding Integrations (Tools)

New integrations go in `tools/`. Each integration is a standalone module.

### Structure

```python
# tools/your_integration.py

"""Your Integration -- one-line description of what it does.

Requires:
  YOUR_API_KEY env var from https://provider.com

Used by:
  - agents/engagement/your_agent.py
  - teams/engagement_team.py
"""

import os
import logging

logger = logging.getLogger(__name__)


def is_available() -> bool:
    """Check if this integration is configured and available."""
    return bool(os.environ.get("YOUR_API_KEY"))


def your_function(**kwargs):
    """Main function. Gracefully degrades if API key is missing."""
    if not is_available():
        logger.warning("YOUR_API_KEY not set -- skipping integration")
        return None

    # Implementation here
```

**Requirements:**
- Every integration MUST have an `is_available()` function that checks for required env vars.
- Every integration MUST gracefully degrade when its API key is missing. The system works with just `ANTHROPIC_API_KEY` -- everything else is optional.
- Every integration MUST log its actions at INFO level and errors at ERROR level.
- Add the new env var to `.env.example` (when it exists) and to the API Keys table in `README.md`.

---

## Code Style

- Python 3.12+ with type hints.
- `pathlib.Path` for file paths, never string concatenation.
- `logging` module, never `print()`.
- YAML for config, JSON for data, Markdown for prompts.
- Every function has a docstring.
- No hardcoded values -- config files or env vars only.

---

## Pull Request Checklist

Before submitting:

- [ ] Read and followed the 52 Rules in `CLAUDE.md`.
- [ ] Tested with `python main.py --run <relevant_team>`.
- [ ] Output is valid JSON matching the prompt schema.
- [ ] No hardcoded timezones, API keys, file paths, or business names.
- [ ] New env vars documented in README API Keys table.
- [ ] New agents registered in scheduler and manual runner.
- [ ] New prompts include Identity, Philosophy, Instructions, Quality Criteria, Hard Rules, and Output Format sections.
- [ ] No orphaned files -- old code deleted in the same pass as replacement.
- [ ] `ARCHITECTURE.md` updated if system structure changed.
- [ ] `CHANGELOG.md` updated with the change.
