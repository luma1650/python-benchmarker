import math

from benchmarker.core import Benchmarker


def main():

    # Test algorithms

    def logarithmic(n: int):
        while n > 1:
            n //= 2

    def linear(n: int):
        return sum(range(n))

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

    # Automatic calibration

    bench = Benchmarker(
        repeats="auto",
        samples=10,
        warmup=10,
        target_ns=100_000_000
    )

    for name, func, sizes in algorithms:
        print(f"\n{'=' * 60}")
        print(f"Algorithm: {name}")
        print(f"{'=' * 60}")

        previous_n = None
        previous_median = None

        for n in sizes:
            result = bench.run(func, n)

            cv = (
                result.stdev / result.mean * 100
                if result.mean > 0 else 0
            )

            print(f"\nn = {n:,}")
            print(f"  Repeats:  {result.repeats:12,}")
            print(f"  Mean:     {result.mean:12.2f} ns")
            print(f"  Median:   {result.median:12.2f} ns")
            print(f"  Min:      {result.minimum:12.2f} ns")
            print(f"  Max:      {result.maximum:12.2f} ns")
            print(f"  Stdev:    {result.stdev:12.2f} ns")
            print(f"  CV:       {cv:12.2f} %")

            if previous_median is not None and previous_median > 0:
                growth = result.median / previous_median
                n_ratio = n / previous_n

                if growth > 0:
                    exponent = math.log(growth) / math.log(n_ratio)
                else:
                    exponent = float("nan")

                print(f"  Growth:   {growth:12.2f}x")
                print(f"  n ratio:  {n_ratio:12.2f}x")
                print(f"  Exponent: {exponent:12.3f}")

            previous_n = n
            previous_median = result.median

    # Manual repetitions

    print(f"\n{'=' * 60}")
    print("Manual repetitions test")
    print(f"{'=' * 60}")

    manual = Benchmarker(
        repeats=100,
        samples=5,
        warmup=5
    )

    result = manual.run(linear, 10000)

    print(f"Repeats: {result.repeats}")
    print(f"Samples: {len(result.times)}")
    print(f"Median:  {result.median:.2f} ns")

    assert result.repeats == 100
    assert len(result.times) == 5

    # Validation tests

    print(f"\n{'=' * 60}")
    print("Validation tests")
    print(f"{'=' * 60}")

    invalid_configs = [
        {"repeats": 0},
        {"repeats": -10},
        {"repeats": "invalid"},
        {"samples": 0},
        {"warmup": -1},
        {"target_ns": 0},
    ]

    for config in invalid_configs:
        try:
            Benchmarker(**config).run(linear, 100)
        except ValueError:
            print(f"PASS: {config}")
        else:
            print(f"FAIL: {config}")

    print(f"\n{'=' * 60}")
    print("Benchmark completed!")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()