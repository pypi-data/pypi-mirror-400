"""Send message commands."""

from __future__ import annotations

import json
from typing import Annotated

import typer

from ai_comm.commands import handle_error
from ai_comm.kitten_client import KittenClient, KittenError
from ai_comm.polling import PollingTimeoutError
from ai_comm.services import InteractionService

SEND_HELP = """\
Send message to AI window and wait for response.

The message is automatically wrapped with sender metadata. For Aider, /ask is
prepended to prevent automatic file edits.

Notes:
  - For long responses, ask AI to write to a file in the project directory
    (/tmp and other external paths require manual approval on target AI — avoid).
  - Timed-out commands auto-move to background.

Examples:
  ai-comm send "review this function" -w 5
  ai-comm send "write to out_$(date +%Y%m%d_%H%M%S).md" -w 8
"""


DEBUG_PANEL = "Debug Options (HUMAN ONLY - AI agents must not use)"


def send(
    message: Annotated[str, typer.Argument(help="Message to send to the AI")],
    window: Annotated[
        int,
        typer.Option("--window", "-w", help="Target window ID (from list-ai-windows)"),
    ],
    timeout: Annotated[
        int,
        typer.Option(
            "--timeout", "-t", help="Timeout in seconds", rich_help_panel=DEBUG_PANEL
        ),
    ] = 1800,
    idle_time: Annotated[
        int,
        typer.Option(
            "--idle-time", help="Idle time in seconds", rich_help_panel=DEBUG_PANEL
        ),
    ] = 3,
    parser: Annotated[
        str,
        typer.Option(
            "--parser",
            "-p",
            help="Response parser (auto, claude, codex, gemini, aider...)",
            rich_help_panel=DEBUG_PANEL,
        ),
    ] = "auto",
    raw: Annotated[
        bool,
        typer.Option(
            "--raw",
            help="Return raw terminal text instead of parsed response",
            rich_help_panel=DEBUG_PANEL,
        ),
    ] = False,
    no_wait: Annotated[
        bool,
        typer.Option(
            "--no-wait",
            help="Send without waiting for response",
            rich_help_panel=DEBUG_PANEL,
        ),
    ] = False,
    as_json: Annotated[
        bool,
        typer.Option("--json", help="Output as JSON", rich_help_panel=DEBUG_PANEL),
    ] = False,
) -> None:
    """Send message to AI window and wait for response."""
    try:
        client = KittenClient()
        service = InteractionService(client)

        service.send_message(window, message)

        if no_wait:
            if as_json:
                typer.echo(json.dumps({"status": "sent", "window": window}))
            else:
                typer.echo(f"Message sent to window {window}")
            return

        elapsed = service.wait_for_response(window, idle_time, float(timeout))

        response, effective_parser = service.get_response(
            window, parser=parser, raw=raw
        )

        if as_json:
            typer.echo(
                json.dumps(
                    {
                        "response": response,
                        "elapsed": elapsed,
                        "parser": effective_parser if not raw else None,
                    }
                )
            )
        else:
            typer.echo(response)

    except PollingTimeoutError as e:
        typer.echo(f"Timeout: {e}", err=True)
        raise typer.Exit(1) from None
    except KittenError as e:
        handle_error(e)
