from collections.abc import Callable
from typing import Any
import time


def calibrate(
    func: Callable[..., Any],
    *args: Any,
    target_ns: int = 100_000_000,
    max_repeats: int = 10_000_000,
    **kwargs: Any
) -> int:

    if target_ns <= 0 or max_repeats <= 0:
        raise ValueError("target_ns and max_repeats must be positive")

    repeats = 1

    while True:
        start = time.perf_counter_ns()

        for _ in range(repeats):
            func(*args, **kwargs)

        elapsed = time.perf_counter_ns() - start

        if elapsed >= target_ns:
            estimated = round(repeats * target_ns / elapsed)
            return max(1, min(max_repeats, estimated))

        if repeats >= max_repeats:
            return repeats

        if elapsed == 0:
            multiplier = 10
        else:
            multiplier = max(2, min(10, target_ns // elapsed))

        repeats = min(max_repeats, repeats * multiplier)