"""Interaction service - unified send and response logic."""

from __future__ import annotations

import os
import time
from typing import TYPE_CHECKING

from ai_comm.adapters import get_adapter
from ai_comm.polling import wait_for_idle
from ai_comm.registry import get_display_name

if TYPE_CHECKING:
    from ai_comm.kitten_client import KittenClient


class InteractionService:
    """Unified service for AI CLI interactions.

    Handles message formatting, sending, waiting, and response fetching.
    Accepts KittenClient via dependency injection.
    """

    def __init__(self, client: KittenClient) -> None:
        """Initialize with injected client."""
        self.client = client

    def get_sender_name(self) -> str | None:
        """Get the sender CLI name from current window."""
        window_id_str = os.environ.get("KITTY_WINDOW_ID")
        if not window_id_str:
            return None
        try:
            window_id = int(window_id_str)
            cli_type = self.client.get_window_cli(window_id)
            if cli_type:
                return get_display_name(cli_type)
        except (ValueError, Exception):
            pass
        return None

    def send_message(
        self,
        window_id: int,
        message: str,
        add_sender_header: bool = True,
    ) -> None:
        """Format and send message to target window."""
        cli_type = self.client.get_window_cli(window_id)
        adapter = get_adapter(cli_type or "generic")

        sender = self.get_sender_name() if add_sender_header else None
        formatted = adapter.format_message(message, sender)

        self.client.send_text(window_id, formatted)
        time.sleep(0.1)
        self.client.send_key(window_id, "enter")

    def wait_for_response(
        self,
        window_id: int,
        idle_seconds: int = 3,
        timeout: float = 1800,
    ) -> float:
        """Wait for window content to stabilize."""
        time.sleep(0.5)

        def check_fn(last_hash: str) -> tuple[bool, str]:
            return self.client.check_idle(window_id, last_hash)

        return wait_for_idle(check_fn, idle_seconds=idle_seconds, timeout=timeout)

    def get_response(
        self,
        window_id: int,
        parser: str = "auto",
        extent: str = "all",
        raw: bool = False,
    ) -> tuple[str, str]:
        """Get parsed response from window.

        Returns:
            Tuple of (response_text, effective_parser_name)
        """
        effective_parser = parser
        if parser == "auto":
            cli_type = self.client.get_window_cli(window_id)
            effective_parser = cli_type or "generic"

        if raw:
            return self.client.get_text(window_id, extent), effective_parser

        adapter = get_adapter(effective_parser)
        response = adapter.fetch_response(self.client, window_id, extent)

        return response, effective_parser

    def send_and_wait(
        self,
        window_id: int,
        message: str,
        idle_seconds: int = 3,
        timeout: float = 1800,
        parser: str = "auto",
        raw: bool = False,
    ) -> tuple[str, float, str]:
        """Send message and wait for response.

        Returns:
            Tuple of (response_text, elapsed_time, effective_parser_name)
        """
        self.send_message(window_id, message)
        elapsed = self.wait_for_response(window_id, idle_seconds, timeout)
        response, effective_parser = self.get_response(window_id, parser, raw=raw)
        return response, elapsed, effective_parser
