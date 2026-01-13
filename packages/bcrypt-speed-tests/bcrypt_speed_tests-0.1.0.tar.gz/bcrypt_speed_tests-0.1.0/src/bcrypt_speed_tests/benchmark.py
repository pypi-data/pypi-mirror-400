"""bcrypt cost-factor benchmark helpers."""

import statistics
import time

import bcrypt

PASSWORD = b"correct horse battery staple"
ITERATIONS = 3  # hashes per cost factor
COSTS = range(10, 15)  # adjust as needed


def benchmark_cost(cost: int, iterations: int) -> float:
    """Return the average time in seconds for a bcrypt cost factor.

    Args:
        cost: Bcrypt cost factor to benchmark.
        iterations: Number of hashes to run for the cost factor.

    Returns:
        The average time in seconds.

    """
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        bcrypt.hashpw(PASSWORD, bcrypt.gensalt(rounds=cost))
        end = time.perf_counter()
        times.append(end - start)
    return statistics.mean(times)
