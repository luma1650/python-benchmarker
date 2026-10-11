import time
from typing import Any
from collections.abc import Callable
import statistics
from dataclasses import dataclass
import statistics

@dataclass
class BenchmarkResult:
    times: list[float]
    repeats: int
    warmup: int

    @property
    def mean(self) -> float:
        return statistics.mean(self.times)

    @property
    def median(self) -> float:
        return statistics.median(self.times)

    @property
    def stdev(self) -> float:
        if len(self.times) < 2:
            return 0.0
        return statistics.stdev(self.times)

    @property
    def minimum(self) -> float:
        return min(self.times)

    @property
    def maximum(self) -> float:
        return max(self.times)


def benchmark(
    func: Callable[..., Any],
    *args: Any,
    repeats: int | str = "auto",
    samples: int = 10,
    warmup: int = 10,
    **kwargs: Any
) -> BenchmarkResult:

    # Validations

    if samples <= 0:
        raise ValueError("samples must be positive")

    if warmup < 0:
        raise ValueError("warmup cannot be negative")

    if repeats == "auto":
        repeats = calibrate(func, *args, **kwargs)
    elif not isinstance(repeats, int) or isinstance(repeats, bool) or repeats <= 0:
        raise ValueError("repeats must be a positive integer or 'auto'")

    # Warm-up repetitions

    for _ in range(warmup):
        func(*args, **kwargs)

    # Sampling

    results: list[float] = []

    for _ in range(samples):

        # Executions
        start = time.perf_counter_ns()
        for _ in range(repeats):
            func(*args, **kwargs)
        end = time.perf_counter_ns()

        results.append((end - start) / repeats)

    return BenchmarkResult(
        times=results,
        repeats=repeats,
        warmup=warmup
    )


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


def main():
    import math

    # O(log n)
    def logarithmic(n: int):
        while n > 1:
            n //= 2

    # O(n)
    def linear(n: int):
        return sum(range(n))

    # O(n²)
    def quadratic(n: int):
        total = 0
        for i in range(n):
            for j in range(n):
                total += i + j
        return total

    algorithms = [
        ("O(log n)", logarithmic, [100, 1000, 10000, 100000]),
        ("O(n)", linear, [100, 1000, 10000, 100000]),
        ("O(n²)", quadratic, [100, 300, 1000]),
    ]

    for name, func, sizes in algorithms:
        print(f"\n{'=' * 60}")
        print(f"Algorithm: {name}")
        print(f"{'=' * 60}")

        previous_n = None
        previous_median = None

        for n in sizes:
            result = benchmark(
                func,
                n,
                repeats="auto",
                samples=10,
                warmup=10
            )

            cv = (
                result.stdev / result.mean * 100
                if result.mean > 0 else 0
            )

            print(f"\nn = {n:,}")
            print(f"  Repeats: {result.repeats:12,}")
            print(f"  Mean:    {result.mean:12.2f} ns")
            print(f"  Median:  {result.median:12.2f} ns")
            print(f"  Min:     {result.minimum:12.2f} ns")
            print(f"  Max:     {result.maximum:12.2f} ns")
            print(f"  Stdev:   {result.stdev:12.2f} ns")
            print(f"  CV:      {cv:12.2f} %")

            if previous_median is not None:
                growth = result.median / previous_median
                n_ratio = n / previous_n

                if growth > 0:
                    exponent = math.log(growth) / math.log(n_ratio)
                else:
                    exponent = float("nan")

                print(f"  Growth:  {growth:12.2f}x")
                print(f"  n ratio: {n_ratio:12.2f}x")
                print(f"  Exponent:{exponent:12.3f}")

            previous_n = n
            previous_median = result.median

    print(f"\n{'=' * 60}")
    print("Benchmark completed!")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()