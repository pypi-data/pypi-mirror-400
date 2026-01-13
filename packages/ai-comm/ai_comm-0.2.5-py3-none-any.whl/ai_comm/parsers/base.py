"""Base class for response parsers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from .utils import clean_response_lines, join_response, remove_base_indent


class ResponseParser(ABC):
    """Abstract base class for AI CLI response parsers.

    Subclasses should override:
    - name: Parser identifier
    - STATUS_INDICATORS: Strings that indicate status bar lines (filtered out)
    - BASE_INDENT: Number of spaces for base indentation (stripped from content)
    - extract_last_response(): Main parsing logic
    """

    name: str = "base"

    # Override in subclasses: strings that indicate status bar lines
    STATUS_INDICATORS: ClassVar[list[str]] = []

    # Override in subclasses: base indentation to strip (0 = no stripping)
    BASE_INDENT: ClassVar[int] = 0

    @abstractmethod
    def extract_last_response(self, text: str) -> str:
        """Extract the last response from the terminal output.

        Args:
            text: Full terminal text content (screen + scrollback)

        Returns:
            The extracted response text
        """
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

    Common pattern used by most parsers:
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
        # Don't forget current block
        if self.in_response and self.current:
            self.responses.append(self.current)
            self.current = []
            self.in_response = False

        if self.responses:
            return self.responses[-1]
        return []
