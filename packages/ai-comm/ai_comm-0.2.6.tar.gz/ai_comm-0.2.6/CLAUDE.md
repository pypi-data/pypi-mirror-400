# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ai-comm is a cross-AI CLI communication tool for Kitty terminal. It enables AI assistants (Claude Code, Codex CLI, Gemini CLI, Aider, Cursor, OpenCode) running in separate Kitty windows to communicate with each other programmatically.

## Commands

```bash
# Install dependencies
uv sync

# Run CLI
uv run ai-comm --help
uv run ai-comm list-ai-windows
uv run ai-comm send "message" -w <window_id>

# Lint and type check
uv run ruff check src/
uv run ruff check --fix src/
uv run mypy src/
```

## Architecture

```
src/ai_comm/
├── cli.py              # Typer CLI entry point
├── registry.py         # Unified CLI registry (single source of truth)
├── kitten_client.py    # Wrapper for kitty @ kitten subprocess calls
├── polling.py          # wait_for_idle() and poll_until() functions
├── adapters/           # CLI-specific adapters (message formatting + response parsing)
│   ├── base.py         # AIAdapter ABC
│   └── {claude,codex,gemini,aider,cursor,opencode,generic}.py
├── services/
│   └── interaction.py  # InteractionService (unified send/wait/fetch logic)
├── commands/
│   ├── send.py         # send command (uses InteractionService)
│   ├── response.py     # get-response, wait-idle, get-text commands
│   └── window.py       # list-ai-windows command
├── kitten/
│   └── ai_comm_kitten.py  # Runs inside Kitty process via Boss API
└── parsers/
    ├── base.py         # ResponseParser ABC, ResponseCollector helper
    └── utils.py        # Shared parsing utilities
```

**Key data flow:**

1. `ai-comm send` → `InteractionService` → `AIAdapter.format_message()`
2. `KittenClient` → subprocess `kitty @ kitten ai_comm_kitten.py`
3. Kitten runs inside Kitty process, accesses Boss API for window operations
4. `polling.wait_for_idle()` polls until terminal content stabilizes
5. `AIAdapter.fetch_response()` extracts response (some adapters like OpenCode use special methods)

## Adding a New CLI

1. Add entry in `src/ai_comm/registry.py` → `CLI_REGISTRY`
2. Create `src/ai_comm/adapters/<cli_name>.py` with class `{Name}Adapter` extending `AIAdapter`:
   - Set `name` class variable
   - Optionally set `STATUS_INDICATORS`, `BASE_INDENT`
   - Override `extract_last_response()` for parsing logic
   - Optionally override `format_message()` for CLI-specific prefixes (e.g., Aider's `/ask`)
   - Optionally override `fetch_response()` for alternative data sources (e.g., OpenCode's export)
3. Add CLI detection in `src/ai_comm/kitten/ai_comm_kitten.py` → `AI_CLI_NAMES`

Note: Adapters are loaded dynamically from registry. Class name must follow convention: `{name.capitalize()}Adapter`.
