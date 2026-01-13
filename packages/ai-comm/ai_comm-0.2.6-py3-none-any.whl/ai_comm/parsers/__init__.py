"""Response parsers - low-level parsing utilities.

For AI CLI adapters, use ai_comm.adapters instead.
"""

from __future__ import annotations

from .base import ResponseCollector, ResponseParser
from .utils import (
    clean_response_lines,
    is_separator_line,
    join_response,
    remove_base_indent,
    strip_leading_empty,
    strip_trailing_empty,
)

__all__ = [
    "ResponseCollector",
    "ResponseParser",
    "clean_response_lines",
    "is_separator_line",
    "join_response",
    "remove_base_indent",
    "strip_leading_empty",
    "strip_trailing_empty",
]
