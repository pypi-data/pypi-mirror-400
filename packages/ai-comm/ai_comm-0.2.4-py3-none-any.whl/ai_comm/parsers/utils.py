"""Common utilities for response parsers."""

from __future__ import annotations


def is_separator_line(line: str) -> bool:
    """Check if line is a separator (all ─ characters)."""
    stripped = line.strip()
    return bool(stripped) and all(c == "─" for c in stripped)


def strip_trailing_empty(lines: list[str]) -> list[str]:
    """Remove trailing empty lines from a list."""
    result = lines.copy()
    while result and not result[-1].strip():
        result.pop()
    return result


def strip_leading_empty(lines: list[str]) -> list[str]:
    """Remove leading empty lines from a list."""
    result = lines.copy()
    while result and not result[0].strip():
        result.pop(0)
    return result


def clean_response_lines(lines: list[str]) -> list[str]:
    """Strip leading and trailing empty lines."""
    return strip_leading_empty(strip_trailing_empty(lines))


def remove_base_indent(line: str, indent: int) -> str:
    """Remove base indentation while preserving relative indent."""
    if indent > 0 and line.startswith(" " * indent):
        return line[indent:]
    return line


def join_response(lines: list[str]) -> str:
    """Join response lines and strip result."""
    return "\n".join(lines).strip()
