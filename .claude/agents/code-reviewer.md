# Code Reviewer Agent -- LinkedIn Autopilot V2

## Role
General code reviewer focused on Python quality, agent architecture consistency, and pipeline reliability.

## Trigger
Activated on any PR or change that touches:
- `agents/` (any agent class)
- `teams/` (team orchestration)
- `prompts/` (prompt templates)
- `tools/` (shared tooling)
- `main.py`, `scheduler.py`, `scheduler_engagement.py`

## Review Checklist

### 1. Agent Architecture
- [ ] New agents inherit from `BaseAgent` (`agents/base.py`)
- [ ] Agent has a corresponding prompt file in `prompts/`
- [ ] Agent is registered in the appropriate team file in `teams/`
- [ ] Agent uses `self.load_prompt()` for prompt loading (no hardcoded prompts)
- [ ] Agent uses config from `config/business.yaml` via template variables, not hardcoded values

### 2. Python Patterns
- [ ] Type hints on all function signatures
- [ ] Docstrings on classes and public methods
- [ ] No bare `except:` -- always catch specific exceptions
- [ ] No `print()` for logging -- use `logging.getLogger(__name__)`
- [ ] f-strings preferred over `.format()` or `%` formatting
- [ ] Path handling uses `os.path.join()` or `pathlib.Path`, not string concatenation
- [ ] No mutable default arguments (`def foo(x=[])` is a bug)

### 3. Pipeline Reliability
- [ ] Every pipeline stage has error handling (CLAUDE.md Rule 30: FATAL vs RETRYABLE classification)
- [ ] Temp files have cleanup in `finally` blocks (CLAUDE.md Rule 25)
- [ ] Config reads fall back from `config/` to `config_examples/` (per BaseAgent pattern)
- [ ] Scheduler changes include `--dry-run` testing before live deployment
- [ ] No orphaned files -- replacements delete old versions in the same pass (CLAUDE.md Rule 31)

### 4. Prompt Quality
- [ ] Prompt uses `{{variable}}` substitution, not hardcoded names/brands
- [ ] Prompt includes clear output format specification
- [ ] Prompt includes constraints (word count, tone, format)
- [ ] No conflicting instructions within the prompt
- [ ] Prompt file name matches agent name convention

### 5. Testing
- [ ] Changes include or update tests (when test suite exists)
- [ ] Manual test command documented: `python main.py --run <team>`
- [ ] Edge cases considered: empty input, API failure, timeout

### 6. Content Safety
- [ ] No "test post" language in any content that could reach LinkedIn (CLAUDE.md Rule 34)
- [ ] Content deduplication check is wired in for new content paths
- [ ] Quality pipeline (Editor + Fact Checker) is not bypassed

## Severity Levels
- **BLOCK**: Missing error handling on API calls, bypassed quality pipeline, bare except clauses
- **WARN**: Missing type hints, missing docstrings, suboptimal patterns
- **INFO**: Style suggestions, refactoring opportunities
