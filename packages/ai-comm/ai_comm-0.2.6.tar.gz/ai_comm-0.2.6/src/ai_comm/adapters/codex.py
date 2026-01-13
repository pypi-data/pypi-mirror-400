"""Adapter for OpenAI Codex CLI."""

from __future__ import annotations

from typing import ClassVar

from .base import AIAdapter


class CodexAdapter(AIAdapter):
    """Adapter for OpenAI Codex CLI responses."""

    name: ClassVar[str] = "codex"
    BASE_INDENT: ClassVar[int] = 2

    def extract_last_response(self, text: str) -> str:
        """Extract the last response block starting with bullet."""
        lines = text.split("\n")

        response_start_indices = [
            i for i, line in enumerate(lines) if line.strip().startswith("•")
        ]

        if not response_start_indices:
            return ""

        last_start = response_start_indices[-1]
        response_lines: list[str] = []

        for i in range(last_start, len(lines)):
            line = lines[i]
            stripped = line.strip()

            if i == last_start:
                response_lines.append(stripped[1:].strip())
            elif line.startswith(" " * self.BASE_INDENT) and not stripped.startswith(
                "›"
            ):
                response_lines.append(self.strip_indent(line))
            elif stripped.startswith("›"):
                break
            elif stripped == "":
                remaining = lines[i + 1 :] if i + 1 < len(lines) else []
                next_content = next((ln for ln in remaining if ln.strip()), "")
                if next_content.strip().startswith("›"):
                    break
            else:
                break

        return self.finalize_response(response_lines)
