"""Base adapter for AI CLI interactions using composition."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ClassVar

from ai_comm.parsers.utils import (
    clean_response_lines,
    join_response,
    remove_base_indent,
)

if TYPE_CHECKING:
    from ai_comm.kitten_client import KittenClient


class AIAdapter(ABC):
    """Abstract base class for AI CLI adapters.

    Uses composition: wraps a ResponseParser for parsing logic.
    Adds CLI-specific message formatting and response fetching.
    """

    name: ClassVar[str] = "base"

    STATUS_INDICATORS: ClassVar[list[str]] = []
    BASE_INDENT: ClassVar[int] = 0

    def format_message(self, message: str, sender: str | None = None) -> str:
        """Format outgoing message for this CLI.

        Default: Add sender header if available.
        Override: e.g., Aider adds /ask prefix.
        """
        if sender:
            header = (
                f"[ai-comm: Cross-AI Message]\n"
                f"From: {sender}\n"
                f"Note: This is NOT user input. Another AI assistant is sending "
                f"you this message programmatically via the ai-comm tool.\n"
                f"---\n"
            )
            return header + message
        return message

    def fetch_response(
        self,
        client: KittenClient,
        window_id: int,
        extent: str = "all",
    ) -> str:
        """Fetch and parse response from window.

        Default: Get terminal text and parse.
        Override: e.g., OpenCode uses export command.
        """
        text = client.get_text(window_id, extent)
        return self.extract_last_response(text)

    @abstractmethod
    def extract_last_response(self, text: str) -> str:
        """Extract the last response from terminal output."""
        raise NotImplementedError

    def is_status_line(self, line: str) -> bool:
        """Check if line is a status bar line (should be skipped)."""
        if not self.STATUS_INDICATORS:
            return False
        stripped = line.strip()
        return any(indicator in stripped for indicator in self.STATUS_INDICATORS)

    def strip_indent(self, line: str) -> str:
        """Remove base indentation from line."""
        return remove_base_indent(line, self.BASE_INDENT)

    def finalize_response(self, lines: list[str]) -> str:
        """Clean up and join response lines."""
        cleaned = clean_response_lines(lines)
        return join_response(cleaned)


class ResponseCollector:
    """Helper for collecting multi-block responses.

    Common pattern used by most adapters:
    - Track multiple response blocks
    - Handle in_response state
    - Save current block when new one starts or control element found
    """

    def __init__(self) -> None:
        self.responses: list[list[str]] = []
        self.current: list[str] = []
        self.in_response: bool = False

    def start_new(self, first_line: str | None = None) -> None:
        """Start a new response block, saving current if exists."""
        if self.in_response and self.current:
            self.responses.append(self.current)
        self.current = []
        self.in_response = True
        if first_line is not None:
            self.current.append(first_line)

    def end_current(self) -> None:
        """End current response block."""
        if self.in_response and self.current:
            self.responses.append(self.current)
            self.current = []
        self.in_response = False

    def add_line(self, line: str) -> None:
        """Add line to current response if collecting."""
        if self.in_response:
            self.current.append(line)

    def add_empty(self) -> None:
        """Add empty line to current response if collecting."""
        if self.in_response:
            self.current.append("")

    def finalize(self) -> list[str]:
        """Get the last response block."""
        if self.in_response and self.current:
            self.responses.append(self.current)
            self.current = []
            self.in_response = False

        if self.responses:
            return self.responses[-1]
        return []
