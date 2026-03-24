from __future__ import annotations

from typing import Callable, TypeVar


T = TypeVar("T")


def retry(times: int, fn: Callable[[], T], on_retry: Callable[[int, Exception], None] | None = None) -> T:
    last_error: Exception | None = None
    for attempt in range(1, times + 1):
        try:
            return fn()
        except Exception as exc:
            last_error = exc
            if attempt < times and on_retry:
                on_retry(attempt, exc)
    raise RuntimeError(f"retry exhausted after {times} attempts: {last_error}")
