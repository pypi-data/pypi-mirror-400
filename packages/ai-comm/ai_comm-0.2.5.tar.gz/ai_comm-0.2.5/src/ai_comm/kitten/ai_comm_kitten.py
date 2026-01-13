#!/usr/bin/env python3
"""
Simplified ai-comm kitten providing atomic operations via Boss API.

This kitten is called by the ai-comm CLI tool. It provides low-level
operations that require access to kitty's Boss API.

Commands:
    get-text --window ID [--extent screen|all]
    send-text --window ID TEXT
    send-key --window ID KEY
    check-idle --window ID --last-hash HASH
    list-ai-windows
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import PurePath
from typing import TYPE_CHECKING, Any

from kittens.tui.handler import result_handler  # type: ignore[import-not-found]

if TYPE_CHECKING:
    from kitty.boss import Boss  # type: ignore[import-not-found]
    from kitty.window import Window  # type: ignore[import-not-found]

# Known AI CLI names and their canonical form
AI_CLI_NAMES: dict[str, str] = {
    "claude": "claude",
    "codex": "codex",
    "gemini": "gemini",
    "aider": "aider",
    "cursor": "cursor",
    "cursor-cli": "cursor",
    "cursor-agent": "cursor",
    "opencode": "opencode",
}

# Keywords that indicate non-CLI processes (status lines, themes, etc.)
EXCLUDE_KEYWORDS: list[str] = ["powerline", "statusline", "prompt", "theme"]


def parse_args(args: list[str]) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(prog="ai_comm_kitten")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # get-text
    get_text = subparsers.add_parser("get-text")
    get_text.add_argument("--window", "-w", type=int, required=True)
    get_text.add_argument("--extent", default="all", choices=["screen", "all"])

    # send-text
    send_text = subparsers.add_parser("send-text")
    send_text.add_argument("--window", "-w", type=int, required=True)
    send_text.add_argument("text", nargs="+")

    # send-key
    send_key = subparsers.add_parser("send-key")
    send_key.add_argument("--window", "-w", type=int, required=True)
    send_key.add_argument("key")

    # check-idle
    check_idle = subparsers.add_parser("check-idle")
    check_idle.add_argument("--window", "-w", type=int, required=True)
    check_idle.add_argument("--last-hash", default="")

    # list-ai-windows
    subparsers.add_parser("list-ai-windows")

    return parser.parse_args(args)


def compute_hash(text: str) -> str:
    """Compute short hash of text content."""
    return hashlib.md5(text.encode()).hexdigest()[:16]


def get_window(boss: Boss, window_id: int) -> Window | None:
    """Get window by ID."""
    return boss.window_id_map.get(window_id)


def get_text(boss: Boss, window_id: int, extent: str) -> dict[str, Any]:
    """Get text content from window."""
    window = get_window(boss, window_id)
    if window is None:
        return {"status": "error", "message": f"Window {window_id} not found"}

    result = boss.call_remote_control(
        window, ("get-text", "-m", f"id:{window_id}", "--extent", extent)
    )
    text = result if isinstance(result, str) else ""
    return {"status": "ok", "text": text, "hash": compute_hash(text)}


def send_text(boss: Boss, window_id: int, text: str) -> dict[str, Any]:
    """Send text to window using multiple methods."""
    window = get_window(boss, window_id)
    if window is None:
        return {"status": "error", "message": f"Window {window_id} not found"}

    # Try paste_text first (fastest)
    paste = getattr(window, "paste_text", None)
    if callable(paste):
        paste(text)
        return {"status": "ok", "method": "paste"}

    # Try write_to_child
    writer = getattr(window, "write_to_child", None)
    if callable(writer):
        try:
            writer(text.encode())
        except TypeError:
            writer(text)
        return {"status": "ok", "method": "write_to_child"}

    # Fallback to subprocess
    socket = getattr(boss, "listening_on", "") or ""
    cmd = ["kitty", "@"]
    if socket:
        cmd.extend(["--to", socket])
    cmd.extend(["send-text", "-m", f"id:{window_id}", "--", text])
    subprocess.run(cmd, check=False, capture_output=True)
    return {"status": "ok", "method": "subprocess"}


def send_key(boss: Boss, window_id: int, key: str) -> dict[str, Any]:
    """Send key press to window."""
    window = get_window(boss, window_id)
    if window is None:
        return {"status": "error", "message": f"Window {window_id} not found"}

    socket = getattr(boss, "listening_on", "") or ""
    cmd = ["kitty", "@"]
    if socket:
        cmd.extend(["--to", socket])
    cmd.extend(["send-key", "-m", f"id:{window_id}", key])
    subprocess.run(cmd, check=False, capture_output=True)
    return {"status": "ok"}


def check_idle(boss: Boss, window_id: int, last_hash: str) -> dict[str, Any]:
    """Check if window content has changed."""
    result = get_text(boss, window_id, "all")
    if result["status"] != "ok":
        return result

    current_hash = result["hash"]
    is_idle = current_hash == last_hash if last_hash else False
    return {"status": "ok", "idle": is_idle, "hash": current_hash}


def detect_ai_cli(cmdline_args: list[str]) -> str | None:
    """Detect AI CLI from cmdline arguments (for parser selection only)."""
    # Check exclusions first
    for arg in cmdline_args:
        arg_lower = arg.lower()
        for exclude in EXCLUDE_KEYWORDS:
            if exclude in arg_lower:
                return None

    for arg in cmdline_args:
        # Check basename (without extension)
        path = PurePath(arg)
        name = path.stem.lower()
        if name in AI_CLI_NAMES:
            return AI_CLI_NAMES[name]

        # Check path components (for wrappers like /path/to/cursor-cli/index.js)
        for part in path.parts:
            part_name = PurePath(part).stem.lower()
            if part_name in AI_CLI_NAMES:
                return AI_CLI_NAMES[part_name]

    return None


def list_ai_windows(boss: Boss) -> dict[str, Any]:
    """List windows running AI CLIs."""
    ai_windows: list[dict[str, Any]] = []

    for os_window in boss.os_window_map.values():
        for tab in os_window.tabs:
            for window in tab.windows:
                child = getattr(window, "child", None)
                if not child:
                    continue

                fg_processes = getattr(child, "foreground_processes", None)
                if callable(fg_processes):
                    fg_processes = fg_processes()
                if not fg_processes:
                    continue

                detected_cli: str | None = None
                detected_cwd: str = ""
                for proc in fg_processes:
                    cmdline = proc.get("cmdline", [])
                    cli = detect_ai_cli(cmdline)
                    if cli:
                        detected_cli = cli
                        detected_cwd = proc.get("cwd", "")
                        break

                if detected_cli:
                    ai_windows.append(
                        {"id": window.id, "cli": detected_cli, "cwd": detected_cwd}
                    )

    return {"status": "ok", "ai_windows": ai_windows}


def main(args: list[str]) -> str:
    """Main entry point - not used for no_ui kitten."""
    return ""


@result_handler(no_ui=True)
def handle_result(
    args: list[str], answer: str, target_window_id: int, boss: Boss
) -> str:
    """Handle kitten result, runs in kitty process."""
    try:
        parsed = parse_args(args[1:])
    except SystemExit:
        return json.dumps({"status": "error", "message": "Invalid arguments"})

    result: dict[str, Any]

    if parsed.command == "get-text":
        result = get_text(boss, parsed.window, parsed.extent)

    elif parsed.command == "send-text":
        text = " ".join(parsed.text)
        result = send_text(boss, parsed.window, text)

    elif parsed.command == "send-key":
        result = send_key(boss, parsed.window, parsed.key)

    elif parsed.command == "check-idle":
        result = check_idle(boss, parsed.window, parsed.last_hash)

    elif parsed.command == "list-ai-windows":
        result = list_ai_windows(boss)

    else:
        result = {"status": "error", "message": f"Unknown command: {parsed.command}"}

    return json.dumps(result, ensure_ascii=False)
