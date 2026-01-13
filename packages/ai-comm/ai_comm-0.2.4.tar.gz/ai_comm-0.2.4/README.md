# ai-comm

Cross-AI CLI communication tool for [Kitty terminal](https://sw.kovidgoyal.net/kitty/). Enables AI assistants running in separate Kitty windows to communicate with each other.

## Why ai-comm?

When working with multiple AI coding assistants, you may want them to collaborate—code review across models, second opinions on architecture, or delegating specialized tasks.

**Why terminal text instead of MCP or black magic?**

- **Stability**: AI CLI tools evolve rapidly, with many still at 0.x and frequently introducing breaking changes. Terminal UI, being user-facing, remains far more stable.
- **Lightweight**: MCP tools consume significant context (often tens of thousands of tokens at startup) and can cause attention dilution. ai-comm uses simple shell commands with minimal overhead.
- **No infrastructure**: Each AI CLI maintains its own context. No need for external services like Redis to synchronize state across tools.
- **Composability**: Shell pipelines and REPL patterns combine naturally, leveraging what CLIs already do well.

## Setup

### 1. Install ai-comm

```bash
# From PyPI
uv tool install ai-comm

# Or from GitHub
uv tool install git+https://github.com/a322655/ai-comm.git
```

### 2. Configure Kitty

Enable remote control in `~/.config/kitty/kitty.conf`:

```conf
allow_remote_control socket-only
listen_on unix:/tmp/kitty-${USER}
```

### 3. Configure Your AI

Add instructions to your AI’s project file (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, etc.) or skills system. An example Claude Code skill is provided in [`skills/ai-comm/`](skills/ai-comm/).

## Usage

1. **Open multiple AI CLIs** in separate Kitty windows:

   ```bash
   claude    # Window 1
   codex     # Window 2
   gemini    # Window 3
   ```

2. **Ask your AI to collaborate**:

   > “Use ai-comm to ask Codex to review src/main.py”

   The AI discovers available windows and sends the request:

   ```bash
   ai-comm list-ai-windows
   #   ID  CLI         CWD
   #   11  codex       /home/user/project
   #   21  gemini      /home/user/project

   ai-comm send "Review src/main.py for bugs" -w 11
   # Returns Codex's response
   ```

3. **For long responses**, instruct the target AI to write to a file:

   ```bash
   ai-comm send "Write analysis to report_$(date +%Y%m%d_%H%M%S).md" -w 11
   ```

## Supported CLIs

| CLI | Notes |
|-----|-------|
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | — |
| [Codex CLI](https://github.com/openai/codex) | — |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli) | — |
| [Aider](https://aider.chat/) | Auto-prefixes `/ask` |
| [Cursor Agent](https://cursor.sh/) | — |
| [OpenCode](https://github.com/opencode-ai/opencode) | Uses export for responses |

## Troubleshooting

**“Window not found”**: Ensure the AI CLI is running in Kitty and remote control is enabled. Run `ai-comm list-ai-windows` to verify.

**Empty responses**: For long outputs, ask the AI to write to a file instead of returning directly.

**“Kitty I/O timeout”**: Check if Kitty is responsive; try restarting it.

## Development

```bash
git clone https://github.com/a322655/ai-comm.git
cd ai-comm
uv sync

uv run ai-comm --help
uv run ruff check src/
uv run mypy src/
```

### Adding a New CLI

1. Add entry in `src/ai_comm/registry.py`
2. Create adapter in `src/ai_comm/adapters/<name>.py` (class `{Name}Adapter`)
3. Add detection in `src/ai_comm/kitten/ai_comm_kitten.py`

## License

MIT
