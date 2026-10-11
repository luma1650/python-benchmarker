import time
from typing import Any
from collections.abc import Callable
import statistics


def benchmark(
    func: Callable[..., Any],
    *args: Any,
    repeats: int = 100,
    samples: int = 10,
    warmup: int = 10,
    **kwargs: Any
) -> list[float]:

    # Validations

    if repeats <= 0:
        raise ValueError("repeats must be positive")

    if samples <= 0:
        raise ValueError("samples must be positive")

    if warmup < 0:
        raise ValueError("warmup cannot be negative")

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

    return results


def analyze(results: list[float]) -> dict[str, float]:
    return {
        "mean": statistics.mean(results),
        "median": statistics.median(results),
        "min": min(results),
        "max": max(results),
        "stdev": statistics.stdev(results)
                 if len(results) > 1 else 0.0
    }

def main():
    import statistics

    # O(log n)
    def logarithmic(n):
        while n > 1:
            n //= 2

    # O(n)
    def linear(n):
        return sum(range(n))

    # O(n²)
    def quadratic(n):
        total = 0
        for i in range(n):
            for j in range(n):
                total += i + j
        return total

    algorithms = {
        "O(log n)": logarithmic,
        "O(n)": linear,
        "O(n²)": quadratic,
    }

    sizes = [100, 1000, 10000, 100000]

    for name, func in algorithms.items():
        print(f"\n{'=' * 55}")
        print(f"Algorithm: {name}")
        print(f"{'=' * 55}")

        for n in sizes:
            # Evitar ejecuciones excesivamente largas
            if name == "O(n²)" and n > 1000:
                continue

            repeats = 5 if name == "O(n²)" else 1000

            results = benchmark(
                func,
                n,
                repeats=repeats,
                samples=10,
                warmup=10
            )

            print(f"\nn = {n:,}")
            print(f"  Mean:   {statistics.mean(results):12.2f} ns")
            print(f"  Median: {statistics.median(results):12.2f} ns")
            print(f"  Min:    {min(results):12.2f} ns")
            print(f"  Max:    {max(results):12.2f} ns")
            print(f"  Stdev:  {statistics.stdev(results):12.2f} ns")


if __name__ == "__main__":
    main()


if __name__ == '__main__':
   main()
