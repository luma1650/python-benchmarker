import random

from benchmarker.core import Benchmarker, BenchmarkTest


def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1

        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1

        arr[j + 1] = key


def main():
    rng = random.Random(42)
    original = [rng.randrange(100000) for _ in range(1000)]

    bench = Benchmarker(
        repeats="auto",
        samples=10,
        warmup=10,
        target_ns=100_000_000
    )

    tests = [
        BenchmarkTest(
            name="Insertion Sort",
            func=insertion_sort,
            setup=lambda: ((original.copy(),), {})
        ),
        BenchmarkTest(
            name="Python Sort",
            func=list.sort,
            setup=lambda: ((original.copy(),), {})
        )
    ]

    for test in tests:
        result = bench.run(test)

        print(f"\n{test.name}")
        print(f"Repeats: {result.repeats:,}")
        print(f"Median:  {result.median / 1000:.2f} µs")
        print(f"CV:      {result.stdev / result.mean * 100:.2f}%")


if __name__ == "__main__":
    main()