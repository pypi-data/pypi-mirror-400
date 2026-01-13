"""Unified CLI registry - single source of truth for CLI metadata."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CLIInfo:
    """Metadata for a supported AI CLI."""

    name: str
    display_name: str
    aliases: tuple[str, ...]
    adapter_module: str


CLI_REGISTRY: dict[str, CLIInfo] = {
    "claude": CLIInfo(
        name="claude",
        display_name="Claude Code",
        aliases=("claude",),
        adapter_module="ai_comm.adapters.claude",
    ),
    "codex": CLIInfo(
        name="codex",
        display_name="Codex CLI",
        aliases=("codex",),
        adapter_module="ai_comm.adapters.codex",
    ),
    "gemini": CLIInfo(
        name="gemini",
        display_name="Gemini CLI",
        aliases=("gemini",),
        adapter_module="ai_comm.adapters.gemini",
    ),
    "aider": CLIInfo(
        name="aider",
        display_name="Aider",
        aliases=("aider",),
        adapter_module="ai_comm.adapters.aider",
    ),
    "cursor": CLIInfo(
        name="cursor",
        display_name="Cursor",
        aliases=("cursor", "cursor-cli", "cursor-agent"),
        adapter_module="ai_comm.adapters.cursor",
    ),
    "opencode": CLIInfo(
        name="opencode",
        display_name="OpenCode",
        aliases=("opencode",),
        adapter_module="ai_comm.adapters.opencode",
    ),
}


def get_display_name(cli_name: str) -> str:
    """Get human-readable display name for CLI."""
    info = CLI_REGISTRY.get(cli_name)
    return info.display_name if info else cli_name.capitalize()


def get_canonical_name(process_name: str) -> str | None:
    """Map process name/alias to canonical CLI name."""
    process_lower = process_name.lower()
    for name, info in CLI_REGISTRY.items():
        if process_lower in info.aliases:
            return name
    return None


def list_cli_names() -> list[str]:
    """List all registered CLI names."""
    return list(CLI_REGISTRY.keys())
