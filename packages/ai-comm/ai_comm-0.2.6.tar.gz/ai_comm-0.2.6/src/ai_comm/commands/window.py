"""Window listing commands."""

from __future__ import annotations

import json
from typing import Annotated

import typer
from wcwidth import wcswidth, wcwidth

from ai_comm.kitten_client import KittenClient, KittenError


def _truncate_to_width(s: str, max_width: int) -> str:
    """Truncate string to fit within max display width."""
    width = 0
    for i, char in enumerate(s):
        char_width = max(wcwidth(char), 0)
        if width + char_width > max_width - 3:
            return s[:i] + "..."
        width += char_width
    return s


def _display_width(s: str) -> int:
    """Calculate display width of string."""
    return int(max(wcswidth(s), 0))


def _pad_to_width(s: str, target_width: int) -> str:
    """Pad string with spaces to reach target display width."""
    return s + " " * (target_width - _display_width(s))


LIST_HELP = """\
List Kitty windows running AI CLIs.

Output columns: ID (window ID for -w option), CLI (detected AI type), TITLE, CWD.

Examples:
  ai-comm list-ai-windows
  ai-comm list-ai-windows --json
"""


def list_ai_windows(
    as_json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """List windows running AI CLIs."""
    try:
        client = KittenClient()
        ai_windows = client.list_ai_windows()
    except KittenError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None

    if as_json:
        typer.echo(json.dumps(ai_windows, indent=2))
    else:
        if not ai_windows:
            typer.echo("No AI CLI windows found")
            return
        typer.echo(f"{'ID':>4}  {'CLI':10s}  {'TITLE':30s}  CWD")
        for w in ai_windows:
            title = w.get("title", "")
            if _display_width(title) > 30:
                title = _truncate_to_width(title, 30)
            title = _pad_to_width(title, 30)
            typer.echo(f"{w['id']:4d}  {w['cli']:10s}  {title}  {w.get('cwd', '')}")
