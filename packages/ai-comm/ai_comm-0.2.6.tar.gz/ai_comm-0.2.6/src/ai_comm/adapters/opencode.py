"""Adapter for OpenCode CLI."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from ai_comm.parsers.utils import clean_response_lines

from .base import AIAdapter, ResponseCollector

if TYPE_CHECKING:
    from ai_comm.kitten_client import KittenClient


class OpenCodeAdapter(AIAdapter):
    """Adapter for OpenCode CLI responses."""

    name: ClassVar[str] = "opencode"
    STATUS_INDICATORS: ClassVar[list[str]] = [
        "OpenCode",
        "tab switch agent",
        "ctrl+p commands",
    ]

    RIGHT_PANEL_MARKERS: ClassVar[list[str]] = [
        "Greeting",
        "Context",
        r"[\d,]+\s*tokens",
        r"\d+%\s*used",
        r"\$[\d.]+\s*spent",
        "LSP",
        "LSPs will activate",
    ]

    def fetch_response(
        self,
        client: KittenClient,
        window_id: int,
        extent: str = "all",
    ) -> str:
        """Use OpenCode export command for complete response with fallback."""
        export_response = self._get_via_export()
        if export_response:
            return export_response

        return super().fetch_response(client, window_id, extent)

    def _get_via_export(self) -> str | None:
        """Get last response via opencode export command."""
        session_dir = Path.home() / ".local/share/opencode/storage/session/global"
        if not session_dir.exists():
            return None

        session_files = sorted(
            session_dir.glob("ses_*.json"), key=lambda p: p.stat().st_mtime
        )
        if not session_files:
            return None

        session_id = session_files[-1].stem

        try:
            result = subprocess.run(
                ["opencode", "export", session_id],
                check=False,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                return None

            output = result.stdout
            json_start = output.find("{")
            if json_start == -1:
                return None

            data = json.loads(output[json_start:])
            messages = data.get("messages", [])

            for msg in reversed(messages):
                if msg.get("info", {}).get("role") != "assistant":
                    continue
                for part in msg.get("parts", []):
                    if part.get("type") == "text":
                        text: str = part.get("text", "")
                        return text

        except (subprocess.TimeoutExpired, json.JSONDecodeError, KeyError):
            pass

        return None

    def _detect_right_panel_column(self, lines: list[str]) -> int:
        """Detect the starting column of the right panel."""
        min_col = float("inf")

        for line in lines:
            for marker in self.RIGHT_PANEL_MARKERS:
                match = re.search(marker, line)
                if match:
                    col = match.start()
                    if col > 20 and line[col - 1] == " ":
                        min_col = min(min_col, col)

        return int(min_col) if min_col != float("inf") else -1

    def _strip_right_panel(self, line: str, panel_col: int) -> str:
        """Remove right panel by truncating at detected column."""
        if panel_col > 0 and len(line) > panel_col:
            return line[:panel_col].rstrip()
        return line.rstrip()

    def extract_last_response(self, text: str) -> str:
        """Extract the last response from OpenCode output."""
        lines = text.split("\n")
        panel_col = self._detect_right_panel_column(lines)
        collector = ResponseCollector()

        for line in lines:
            stripped = line.strip()

            if self.is_status_line(line):
                continue

            if "╹" in stripped or "▀" in stripped:
                continue

            if stripped.startswith("▣"):
                collector.end_current()
                continue

            if stripped.startswith("┃"):
                collector.end_current()
                continue

            if not stripped:
                collector.add_empty()
                continue

            if not collector.in_response:
                collector.start_new()
            collector.add_line(self._strip_right_panel(line, panel_col))

        result = collector.finalize()
        cleaned = clean_response_lines(result)
        return "\n".join(cleaned) if cleaned else ""
