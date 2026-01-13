"""Generic adapter using common prompt patterns."""

from __future__ import annotations

import re
from typing import ClassVar

from .base import AIAdapter


class GenericAdapter(AIAdapter):
    """Generic adapter that tries to extract the last response block."""

    name: ClassVar[str] = "generic"

    PROMPT_PATTERN = re.compile(r"^[>$%›»❯➜]\s*", re.MULTILINE)
    EMPTY_PROMPT_PATTERN = re.compile(r"^[>$%›»❯➜]\s*$", re.MULTILINE)

    def extract_last_response(self, text: str) -> str:
        """Extract content after the last prompt-like pattern."""
        lines = text.strip().split("\n")

        prompt_lines: list[tuple[int, bool]] = []
        for i, line in enumerate(lines):
            normalized = line.replace("\u00a0", " ").strip()
            if self.PROMPT_PATTERN.match(normalized):
                is_empty = bool(self.EMPTY_PROMPT_PATTERN.fullmatch(normalized))
                prompt_lines.append((i, is_empty))

        if not prompt_lines:
            non_empty = [line for line in lines if line.strip()]
            return self.finalize_response(non_empty[-10:]) if non_empty else ""

        last_idx, last_is_empty = prompt_lines[-1]

        if last_is_empty:
            if len(prompt_lines) < 2:
                return self.finalize_response(lines[last_idx + 1 :])
            second_last_idx = prompt_lines[-2][0]
            return self.finalize_response(lines[second_last_idx + 1 : last_idx])

        return self.finalize_response(lines[last_idx + 1 :])
