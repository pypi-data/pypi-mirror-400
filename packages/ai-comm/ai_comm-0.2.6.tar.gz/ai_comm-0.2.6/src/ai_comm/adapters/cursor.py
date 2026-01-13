"""Adapter for Cursor Agent CLI."""

from __future__ import annotations

from typing import ClassVar

from ai_comm.parsers.utils import strip_trailing_empty

from .base import AIAdapter


class CursorAdapter(AIAdapter):
    """Adapter for Cursor Agent CLI responses."""

    name: ClassVar[str] = "cursor"
    STATUS_INDICATORS: ClassVar[list[str]] = [
        "Composer",
        "/ commands",
        "@ files",
        "! shell",
    ]

    def _is_box_end(self, line: str) -> bool:
        """Check if line is a box end."""
        stripped = line.strip()
        return stripped.startswith("└") and "─" in stripped and stripped.endswith("┘")

    def _is_box_start(self, line: str) -> bool:
        """Check if line is a box start."""
        stripped = line.strip()
        return stripped.startswith("┌") and "─" in stripped

    def extract_last_response(self, text: str) -> str:
        """Extract the last response from Cursor Agent output."""
        lines = text.split("\n")

        box_ends = [i for i, line in enumerate(lines) if self._is_box_end(line)]

        if not box_ends:
            return ""

        user_input_end = -1
        for end_idx in box_ends:
            is_prompt_box = any(
                "→" in lines[j] for j in range(max(0, end_idx - 5), end_idx)
            )
            if not is_prompt_box:
                user_input_end = end_idx

        if user_input_end == -1:
            return ""

        response_lines: list[str] = []
        in_response = False

        for i in range(user_input_end + 1, len(lines)):
            line = lines[i]
            stripped = line.strip()

            if not in_response and not stripped:
                continue

            if self._is_box_start(line):
                break
            if self.is_status_line(line):
                break

            in_response = True
            response_lines.append(line)

        return self.finalize_response(strip_trailing_empty(response_lines))
