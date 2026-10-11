import time
from collections.abc import Callable
from typing import Any

from benchmarker.calibration import calibrate
from benchmarker.result import BenchmarkResult


class Benchmarker:
    def __init__(
        self,
        repeats: int | str = "auto",
        samples: int = 10,
        warmup: int = 10,
        target_ns: int = 100_000_000
    ):
        self.repeats = repeats
        self.samples = samples
        self.warmup = warmup
        self.target_ns = target_ns

    def run(
            self,
            func: Callable[..., Any],
            *args: Any,
            **kwargs: Any
    ) -> BenchmarkResult:

        # Validations
        if self.samples <= 0:
            raise ValueError("samples must be positive")

        if self.warmup < 0:
            raise ValueError("warmup cannot be negative")

        if self.target_ns <= 0:
            raise ValueError("target_ns must be positive")

        # Warmup
        for _ in range(self.warmup):
            func(*args, **kwargs)

        # Calibration
        if self.repeats == "auto":
            repeats = calibrate(
                func,
                *args,
                target_ns=self.target_ns,
                **kwargs
            )
        elif (
                not isinstance(self.repeats, int)
                or isinstance(self.repeats, bool)
                or self.repeats <= 0
        ):
            raise ValueError(
                "repeats must be a positive integer or 'auto'"
            )
        else:
            repeats = self.repeats

        # Sampling
        results: list[float] = []

        for _ in range(self.samples):
            start = time.perf_counter_ns()

            for _ in range(repeats):
                func(*args, **kwargs)

            end = time.perf_counter_ns()

            results.append((end - start) / repeats)

        return BenchmarkResult(
            times=results,
            repeats=repeats,
            warmup=self.warmup
        )




