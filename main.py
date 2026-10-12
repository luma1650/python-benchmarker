import random

from benchmarker.core import (
    Benchmarker,
    BenchmarkTest,
    BenchmarkSuite,
    MeasurementMode,
)


def insertion_sort(arr):
    for i in range(1, len(arr)):
        value = arr[i]
        j = i - 1

        while j >= 0 and arr[j] > value:
            arr[j + 1] = arr[j]
            j -= 1

        arr[j + 1] = value


def selection_sort(arr):
    n = len(arr)

    for i in range(n):
        minimum = i

        for j in range(i + 1, n):
            if arr[j] < arr[minimum]:
                minimum = j

        arr[i], arr[minimum] = arr[minimum], arr[i]


def bubble_sort(lista: list):
    n: int = len(lista)
    for i in range(n):
        swapped = False

        for j in range(n - i - 1):
            if lista[j] > lista[j + 1]:
                lista[j], lista[j + 1] = lista[j + 1], lista[j]
                swapped = True

        if not swapped:
            break


def main():
    rng = random.Random(42)
    original = [rng.randrange(100000) for _ in range(1000)]

    def setup():
        return ((original.copy(),), {})

    bench = Benchmarker(
        repeats="auto",
        samples=10,
        warmup=10,
        target_ns=50_000_000
    )

    suite = BenchmarkSuite("Sorting Algorithms")

    suite.add(BenchmarkTest(
        name="Insertion Sort",
        func=insertion_sort,
        setup=setup,
        measurement_mode=MeasurementMode.INDIVIDUAL
    ))

    suite.add(BenchmarkTest(
        name="Selection Sort",
        func=selection_sort,
        setup=setup,
        measurement_mode=MeasurementMode.INDIVIDUAL
    ))

    suite.add(BenchmarkTest(
        name="Bubble Sort",
        func=bubble_sort,
        setup=setup,
        measurement_mode=MeasurementMode.INDIVIDUAL
    ))

    suite.add(BenchmarkTest(
        name="Python Sort",
        func=list.sort,
        setup=setup,
        measurement_mode=MeasurementMode.INDIVIDUAL
    ))

    suite.run(bench)
    suite.summary()


if __name__ == "__main__":
    main()