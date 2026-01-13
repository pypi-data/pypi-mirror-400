"""Response and idle waiting commands."""

from __future__ import annotations

import json
from typing import Annotated

import typer

from ai_comm.commands import handle_error
from ai_comm.kitten_client import KittenClient, KittenError
from ai_comm.polling import PollingTimeoutError
from ai_comm.services import InteractionService


def wait_idle(
    window: Annotated[int, typer.Option("--window", "-w", help="Target window ID")],
    timeout: Annotated[
        int, typer.Option("--timeout", "-t", help="Timeout in seconds")
    ] = 1800,
    idle_time: Annotated[
        int, typer.Option("--idle-time", help="Idle time in seconds")
    ] = 3,
) -> None:
    """Wait for window content to stabilize."""
    try:
        client = KittenClient()
        service = InteractionService(client)

        elapsed = service.wait_for_response(window, idle_time, float(timeout))
        typer.echo(f"Window {window} idle after {elapsed:.1f}s")

    except PollingTimeoutError as e:
        typer.echo(f"Timeout: {e}", err=True)
        raise typer.Exit(1) from None
    except KittenError as e:
        handle_error(e)


def get_text(
    window: Annotated[int, typer.Option("--window", "-w", help="Target window ID")],
    extent: Annotated[str, typer.Option("--extent", help="screen or all")] = "all",
    as_json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Get raw text content from window."""
    try:
        client = KittenClient()
        text = client.get_text(window, extent)
    except KittenError as e:
        handle_error(e)
        return

    if as_json:
        typer.echo(json.dumps({"text": text}))
    else:
        typer.echo(text)


HUMAN_ONLY_WARNING = """\
Debug command for human troubleshooting.
AI agents: run 'ai-comm --help' for usage instructions.

"""

WAIT_IDLE_HELP = (
    HUMAN_ONLY_WARNING
    + """\
Wait for window content to stabilize.
"""
)

GET_TEXT_HELP = (
    HUMAN_ONLY_WARNING
    + """\
Get raw text content from window.
"""
)

GET_RESPONSE_HELP = (
    HUMAN_ONLY_WARNING
    + """\
Get parsed response from an AI window.

Examples:
  ai-comm get-response -w 5
  ai-comm get-response -w 8 --json
"""
)


def get_response(
    window: Annotated[
        int,
        typer.Option("--window", "-w", help="Target window ID (from list-ai-windows)"),
    ],
    parser: Annotated[
        str,
        typer.Option("--parser", "-p", help="Response parser (auto-detected)"),
    ] = "auto",
    extent: Annotated[str, typer.Option("--extent", help="screen or all")] = "all",
    as_json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Get parsed response from window."""
    try:
        client = KittenClient()
        service = InteractionService(client)

        response, effective_parser = service.get_response(
            window, parser=parser, extent=extent
        )

        if not response:
            typer.echo("No content", err=True)
            raise typer.Exit(1)

        if as_json:
            typer.echo(json.dumps({"response": response, "parser": effective_parser}))
        else:
            typer.echo(response)

    except KittenError as e:
        handle_error(e)
