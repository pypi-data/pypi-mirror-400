"""Kitten client - wrapper for calling the simplified kitten via subprocess."""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class KittenError(Exception):
    """Base exception for kitten errors."""

    pass


class WindowNotFoundError(KittenError):
    """Window not found."""

    pass


class KittenCallError(KittenError):
    """Failed to call kitten."""

    pass


@dataclass
class KittenResult:
    """Result from kitten call."""

    status: str
    data: dict[str, Any]


class KittenClient:
    """Client for calling the simplified ai_comm_kitten."""

    # Default kitten path - bundled within the package
    KITTEN_PATH = Path(__file__).parent / "kitten" / "ai_comm_kitten.py"

    def __init__(self, socket: str | None = None) -> None:
        """Initialize client.

        Args:
            socket: Optional kitty socket path. If None, uses KITTY_LISTEN_ON env var.
        """
        self.socket = socket or os.environ.get("KITTY_LISTEN_ON")
        self._kitten_path = str(self.KITTEN_PATH.resolve())

    def _call(self, *args: str, timeout: float = 15) -> KittenResult:
        """Call kitten and return result.

        Args:
            *args: Arguments to pass to kitten
            timeout: Subprocess timeout in seconds

        Returns:
            KittenResult with status and data

        Raises:
            KittenCallError: If call fails
            WindowNotFoundError: If window not found
        """
        cmd = ["kitty", "@"]
        if self.socket:
            cmd.extend(["--to", self.socket])
        cmd.extend(["kitten", self._kitten_path, *args])

        try:
            result = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as e:
            raise KittenCallError(f"Kitten call timed out after {timeout}s") from e
        except Exception as e:
            raise KittenCallError(f"Failed to call kitten: {e}") from e

        if result.returncode != 0:
            stderr = result.stderr.strip()
            if "i/o timeout" in stderr.lower():
                raise KittenCallError("Kitty I/O timeout - kitten took too long")
            raise KittenCallError(f"Kitten failed: {stderr or result.stdout}")

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise KittenCallError(f"Invalid JSON from kitten: {result.stdout}") from e

        if data.get("status") == "error":
            msg = data.get("message", "Unknown error")
            if "not found" in msg.lower():
                raise WindowNotFoundError(msg)
            raise KittenCallError(msg)

        return KittenResult(status=data["status"], data=data)

    def get_text(self, window_id: int, extent: str = "all") -> str:
        """Get text content from window.

        Args:
            window_id: Target window ID
            extent: "all" or "screen"

        Returns:
            Window text content
        """
        result = self._call("get-text", "--window", str(window_id), "--extent", extent)
        text: str = result.data.get("text", "")
        return text

    def get_text_hash(self, window_id: int, extent: str = "all") -> tuple[str, str]:
        """Get text content and hash from window.

        Args:
            window_id: Target window ID
            extent: "all" or "screen"

        Returns:
            Tuple of (text, hash)
        """
        result = self._call("get-text", "--window", str(window_id), "--extent", extent)
        text: str = result.data.get("text", "")
        hash_val: str = result.data.get("hash", "")
        return text, hash_val

    def send_text(self, window_id: int, text: str) -> bool:
        """Send text to window.

        Args:
            window_id: Target window ID
            text: Text to send

        Returns:
            True if successful
        """
        result = self._call("send-text", "--window", str(window_id), text)
        return result.status == "ok"

    def send_key(self, window_id: int, key: str) -> bool:
        """Send key press to window.

        Args:
            window_id: Target window ID
            key: Key name (e.g., "enter", "escape")

        Returns:
            True if successful
        """
        result = self._call("send-key", "--window", str(window_id), key)
        return result.status == "ok"

    def check_idle(self, window_id: int, last_hash: str = "") -> tuple[bool, str]:
        """Check if window content has changed.

        Args:
            window_id: Target window ID
            last_hash: Previous content hash

        Returns:
            Tuple of (is_idle, current_hash)
        """
        result = self._call(
            "check-idle", "--window", str(window_id), "--last-hash", last_hash
        )
        return result.data.get("idle", False), result.data.get("hash", "")

    def list_ai_windows(self) -> list[dict[str, Any]]:
        """List windows running AI CLIs.

        Returns:
            List of AI window info dicts with id, cli, cwd
        """
        result = self._call("list-ai-windows")
        ai_windows: list[dict[str, Any]] = result.data.get("ai_windows", [])
        return ai_windows

    def get_window_cli(self, window_id: int) -> str | None:
        """Get CLI type for a window.

        Args:
            window_id: Target window ID

        Returns:
            CLI name (e.g., "claude", "codex") or None if not an AI window
        """
        ai_windows = self.list_ai_windows()
        for w in ai_windows:
            if w["id"] == window_id:
                cli: str = w["cli"]
                return cli
        return None
