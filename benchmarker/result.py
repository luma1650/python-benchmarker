import statistics
from dataclasses import dataclass


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