import time
from collections.abc import Callable
from enum import Enum
from typing import Any
from benchmarker.calibration import calibrate, calibrate_test
from benchmarker.result import BenchmarkResult
from dataclasses import dataclass, field

type Arguments = tuple[tuple[Any, ...], dict[str, Any]]
type Setup = Callable[[], Arguments]
type Validator = Callable[[Any, Arguments, Arguments], bool]


class MeasurementMode(str, Enum):
    BLOCK = "block"
    INDIVIDUAL = "individual"


@dataclass
class BenchmarkTest:
    name: str
    func: Callable[..., Any]
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] = field(default_factory=dict)
    setup: Setup | None = None
    measurement_mode: MeasurementMode = MeasurementMode.BLOCK



class Benchmarker:
    def __init__(
        self,
        repeats: int | str = "auto",
        samples: int = 10,
        warmup: int = 10,
        target_ns: int = 100_000_000,
        max_repeats: int = 10_000_000,
    ):
        self.elapsed_ns: int = 0
        self.max_repeats = max_repeats
        self.repeats = repeats
        self.samples = samples
        self.warmup = warmup
        self.target_ns = target_ns
        self._validate()

    def _validate(self) -> None:
        if self.samples <= 0:
            raise ValueError("samples must be positive")

        if self.warmup < 0:
            raise ValueError("warmup cannot be negative")

        if self.target_ns <= 0:
            raise ValueError("target_ns must be positive")

        if self.max_repeats <= 0:
            raise ValueError("max_repeats must be positive")

        if self.repeats != "auto" and (
                not isinstance(self.repeats, int)
                or isinstance(self.repeats, bool)
                or self.repeats <= 0
        ):
            raise ValueError("invalid repeats")

    def _get_args(self, test: BenchmarkTest) -> Arguments:
        if test.setup is None:
            args, kwargs = test.args, test.kwargs
        else:
            args, kwargs = test.setup()

        return args, kwargs

    def measure(self, test: BenchmarkTest, repeats: int) -> int:
        if repeats <= 0:
            raise ValueError("repeats must be positive")

        if test.measurement_mode == MeasurementMode.BLOCK:
            args, kwargs = self._get_args(test)
            start = time.perf_counter_ns()
            for _ in range(repeats):
                test.func(*args, **kwargs)

            return time.perf_counter_ns() - start
        elif test.measurement_mode == MeasurementMode.INDIVIDUAL:
            elapsed_ns = 0
            for _ in range(repeats):
                args, kwargs = self._get_args(test)
                start = time.perf_counter_ns()
                test.func(*args, **kwargs)
                elapsed_ns += time.perf_counter_ns() - start

            return elapsed_ns
        else:
            raise ValueError("invalid measurement mode")


    def run(
            self,
            test: BenchmarkTest,
    ) -> BenchmarkResult:
        # Warm-up
        if self.warmup > 0:
            self.measure(test, self.warmup)

        # Calibration
        if self.repeats == "auto":
            repeats = calibrate_test(
                test,
                self,
                target_ns=self.target_ns,
                max_repeats=self.max_repeats
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
            # Timer per execution

            elapsed_ns = self.measure(test, repeats)

            results.append(elapsed_ns / repeats)

        return BenchmarkResult(
            times=results,
            repeats=repeats,
            warmup=self.warmup
        )

@dataclass
class BenchmarkSuite:
    name: str
    tests: list[BenchmarkTest] = field(default_factory=list)
    results: dict[str, BenchmarkResult] = field(default_factory=dict)

    def add(self, test: BenchmarkTest) -> None:
        if any(t.name == test.name for t in self.tests):
            raise ValueError(f"Duplicate test name: {test.name}")

        self.tests.append(test)

    def run(self, benchmarker: Benchmarker) -> dict[str, BenchmarkResult]:
        self.results.clear()

        for test in self.tests:
            print(f"Running: {test.name}")

            result = benchmarker.run(test)
            self.results[test.name] = result

        return self.results.copy()

    def summary(self) -> None:
        if not self.results:
            print("No benchmark results available.")
            return

        print(f"\n{'=' * 75}")
        print(f"Suite: {self.name}")
        print(f"{'=' * 75}")

        print(
            f"{'Algorithm':<30}"
            f"{'Median (µs)':>15}"
            f"{'Mean (µs)':>15}"
            f"{'CV (%)':>12}"
        )

        print("-" * 75)

        for name, result in self.results.items():
            cv = (
                result.stdev / result.mean * 100
                if result.mean > 0 else 0.0
            )

            print(
                f"{name:<30}"
                f"{result.median / 1000:>15.2f}"
                f"{result.mean / 1000:>15.2f}"
                f"{cv:>12.2f}"
            )