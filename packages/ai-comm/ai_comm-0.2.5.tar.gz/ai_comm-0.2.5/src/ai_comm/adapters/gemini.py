"""Adapter for Gemini CLI."""

from __future__ import annotations

from typing import ClassVar

from .base import AIAdapter, ResponseCollector


class GeminiAdapter(AIAdapter):
    """Adapter for Gemini CLI responses."""

    name: ClassVar[str] = "gemini"
    BASE_INDENT: ClassVar[int] = 2
    STATUS_INDICATORS: ClassVar[list[str]] = [
        "no sandbox",
        "/model",
        "Type your message",
        "accepting edits",
    ]

    def extract_last_response(self, text: str) -> str:
        """Extract the last response from Gemini CLI output."""
        lines = text.split("\n")
        collector = ResponseCollector()

        for line in lines:
            stripped = line.strip()

            if not stripped:
                collector.add_empty()
                continue

            if self.is_status_line(line):
                continue

            if not collector.in_response and stripped.startswith(("╭", "╰", "│", "ℹ")):
                continue

            if collector.in_response and stripped.startswith("╭─"):
                collector.end_current()
                continue

            if stripped.startswith("✦"):
                content = stripped[1:].strip()
                collector.start_new(content if content else None)
                continue

            if stripped.startswith(">"):
                collector.end_current()
                continue

            if collector.in_response:
                collector.add_line(self.strip_indent(line))

        return self.finalize_response(collector.finalize())
