"""Adapter for Claude Code CLI."""

from __future__ import annotations

import re
from typing import ClassVar

from ai_comm.parsers.utils import is_separator_line

from .base import AIAdapter, ResponseCollector


class ClaudeAdapter(AIAdapter):
    """Adapter for Claude Code CLI responses."""

    name: ClassVar[str] = "claude"
    BASE_INDENT: ClassVar[int] = 2
    STATUS_INDICATORS: ClassVar[list[str]] = ["tokens", "§", "☉", "$", "◔", "⎇"]

    TOOL_CALL_PATTERN = re.compile(
        r"^⏺\s*(Read|Write|Edit|Bash|Glob|Grep|Task|WebFetch|WebSearch|"
        r"TodoWrite|NotebookEdit|AskUserQuestion|KillShell|TaskOutput)\s*\("
    )

    SPINNER_CHARS = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

    def _is_control_element(self, stripped: str) -> bool:
        """Check if line is a control element that ends a response."""
        if stripped.startswith(">"):
            return True
        if stripped.startswith("∴"):
            return True
        if stripped.startswith("⎿"):
            return True
        if stripped.startswith(("╭", "╰")):
            return True
        return is_separator_line(stripped)

    def extract_last_response(self, text: str) -> str:
        """Extract the last response from Claude Code output."""
        lines = text.split("\n")
        collector = ResponseCollector()

        for line in lines:
            stripped = line.strip()

            if self.is_status_line(line):
                continue

            if stripped and stripped[0] in self.SPINNER_CHARS:
                continue

            if stripped.startswith("⏺"):
                if self.TOOL_CALL_PATTERN.match(stripped):
                    collector.end_current()
                    continue

                content = stripped[1:].strip()
                collector.start_new(content if content else None)
                continue

            if self._is_control_element(stripped):
                collector.end_current()
                continue

            if collector.in_response:
                if not stripped:
                    collector.add_empty()
                else:
                    collector.add_line(self.strip_indent(line))

        return self.finalize_response(collector.finalize())
