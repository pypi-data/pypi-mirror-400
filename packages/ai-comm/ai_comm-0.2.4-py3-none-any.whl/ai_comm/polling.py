"""Polling logic for waiting on window content changes."""

from __future__ import annotations

import time
from collections.abc import Callable


class PollingTimeoutError(Exception):
    """Raised when polling times out."""

    def __init__(self, timeout: float, elapsed: float) -> None:
        super().__init__(f"Timeout after {elapsed:.1f}s (limit: {timeout}s)")
        self.timeout = timeout
        self.elapsed = elapsed


def wait_for_idle(
    check_fn: Callable[[str], tuple[bool, str]],
    idle_seconds: int = 3,
    timeout: float = 1800,
    poll_interval: float = 1.0,
) -> float:
    """Wait for content to stabilize.

    Args:
        check_fn: Function that takes last_hash and returns (is_same, current_hash)
        idle_seconds: Number of consecutive stable checks required
        timeout: Maximum wait time in seconds
        poll_interval: Time between checks in seconds

    Returns:
        Total elapsed time in seconds

    Raises:
        PollingTimeoutError: If timeout is reached
    """
    start_time = time.time()
    last_hash = ""
    stable_count = 0

    while True:
        elapsed = time.time() - start_time
        if elapsed >= timeout:
            raise PollingTimeoutError(timeout, elapsed)

        is_same, current_hash = check_fn(last_hash)

        if is_same and last_hash:
            stable_count += 1
            if stable_count >= idle_seconds:
                return elapsed
        else:
            stable_count = 0
            last_hash = current_hash

        time.sleep(poll_interval)


def poll_until(
    condition_fn: Callable[[], bool],
    timeout: float = 1800,
    poll_interval: float = 1.0,
) -> float:
    """Poll until condition is true.

    Args:
        condition_fn: Function that returns True when done
        timeout: Maximum wait time in seconds
        poll_interval: Time between checks in seconds

    Returns:
        Total elapsed time in seconds

    Raises:
        PollingTimeoutError: If timeout is reached
    """
    start_time = time.time()

    while True:
        elapsed = time.time() - start_time
        if elapsed >= timeout:
            raise PollingTimeoutError(timeout, elapsed)

        if condition_fn():
            return elapsed

        time.sleep(poll_interval)
