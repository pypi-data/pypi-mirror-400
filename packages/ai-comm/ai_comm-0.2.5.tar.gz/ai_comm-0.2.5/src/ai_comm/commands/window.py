"""Window listing commands."""

from __future__ import annotations

import json
from typing import Annotated

import typer

from ai_comm.kitten_client import KittenClient, KittenError

LIST_HELP = """\
List Kitty windows running AI CLIs.

Output columns: ID (window ID for -w option), CLI (detected AI type), CWD.

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
        typer.echo(f"{'ID':>4}  {'CLI':10s}  CWD")
        for w in ai_windows:
            typer.echo(f"{w['id']:4d}  {w['cli']:10s}  {w.get('cwd', '')}")
