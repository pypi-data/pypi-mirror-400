# poe-research-cli

CLI for Poe Deep Research with retry/resume support.

## Installation

```bash
# Via uvx (recommended, no install needed)
uvx poe-research-cli -p "Your research prompt"

# Or install globally
pip install poe-research-cli
```

## Environment Variables

```bash
# Required for Poe models (o4-mini, o3)
export POE_API_KEY="your-poe-api-key"
export POE_BASE_URL="https://api.poe.com/v1"  # optional, this is default

# Required for Gemini model
export GEMINI_API_KEY="your-gemini-api-key"
export GEMINI_BASE_URL="https://generativelanguage.googleapis.com"  # optional
```

## Usage

```bash
# Simple research with default model (o4-mini)
poe-research -p "What are the latest AI developments?"

# Use specific model
poe-research -m gemini -p "Research quantum computing trends"
poe-research -m o3 -p "Deep analysis of supply chain risks"

# Resume interrupted task
poe-research --resume

# Resume specific task
poe-research -t 2026-01-08_123456_abc12345

# List cached tasks
poe-research -l
```

## Models

| Shortcut | Full Name | API | Best For |
|----------|-----------|-----|----------|
| `o4-mini` | o4-mini-deep-research | Poe | Visual analysis, code review, second opinions |
| `o3` | o3-deep-research | Poe | High-value research with citations |
| `gemini` | gemini-2.0-flash | Google | Balanced research, good citations |

You can also use any full model name directly:
```bash
poe-research -m some-future-model -p "..."
```

## Cache Location

Results are saved to `~/.cache/poe-research/`:
```
~/.cache/poe-research/
├── 2026-01-08_123456_abc12345/
│   ├── result.md      # Full research result
│   └── state.json     # Task state (for resume)
```

## Claude Code Subagent

This CLI is designed to work with Claude Code's subagent system. See the `poe-researcher` subagent configuration for integration.
