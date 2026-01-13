"""Adapter for Aider CLI."""

from __future__ import annotations

import re
from typing import ClassVar

from ai_comm.parsers.utils import is_separator_line, strip_trailing_empty

from .base import AIAdapter


class AiderAdapter(AIAdapter):
    """Adapter for Aider CLI responses."""

    name: ClassVar[str] = "aider"

    TOKEN_PATTERN = re.compile(r"^Tokens:\s+[\d.]+[kM]?\s+sent")

    def format_message(self, message: str, sender: str | None = None) -> str:
        """Prepend /ask to prevent automatic file edits."""
        base_message = super().format_message(message, sender)
        return "/ask " + base_message

    def extract_last_response(self, text: str) -> str:
        """Extract the last response from Aider CLI output."""
        lines = text.split("\n")

        input_end_indices: list[int] = []
        in_input = False

        for i, line in enumerate(lines):
            if line.startswith("> ") and line.strip() != ">":
                in_input = True
            elif in_input:
                input_end_indices.append(i)
                in_input = False

        if not input_end_indices:
            return ""

        last_input_end = input_end_indices[-1]
        response_lines: list[str] = []

        for i in range(last_input_end, len(lines)):
            line = lines[i]
            stripped = line.strip()

            if not response_lines and not stripped:
                continue

            if is_separator_line(stripped):
                break
            if self.TOKEN_PATTERN.match(stripped):
                break
            if stripped == ">":
                break
            if line.startswith("> "):
                break

            response_lines.append(line)

        return self.finalize_response(strip_trailing_empty(response_lines))
