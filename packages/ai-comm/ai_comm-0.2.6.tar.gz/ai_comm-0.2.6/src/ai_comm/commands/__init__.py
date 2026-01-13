"""CLI commands for ai-comm."""

from __future__ import annotations

import typer


def handle_error(error: Exception, exit_code: int = 1) -> None:
    """Handle error with consistent formatting."""
    typer.echo(f"Error: {error}", err=True)
    raise typer.Exit(exit_code) from None
