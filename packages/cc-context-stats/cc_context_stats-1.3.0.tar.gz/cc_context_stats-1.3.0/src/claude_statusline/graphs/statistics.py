"""Statistical calculations for token data."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Stats:
    """Statistical summary of a data series."""

    min_val: int
    max_val: int
    avg_val: int
    total: int
    count: int


def calculate_stats(data: list[int]) -> Stats:
    """Calculate basic statistics for a list of integers.

    Args:
        data: List of integer values

    Returns:
        Stats object with min, max, avg, total, and count
    """
    if not data:
        return Stats(min_val=0, max_val=0, avg_val=0, total=0, count=0)

    min_val = min(data)
    max_val = max(data)
    total = sum(data)
    count = len(data)
    avg_val = total // count if count > 0 else 0

    return Stats(min_val=min_val, max_val=max_val, avg_val=avg_val, total=total, count=count)


def calculate_deltas(values: list[int]) -> list[int]:
    """Calculate deltas between consecutive values.

    Args:
        values: List of values (e.g., cumulative token counts)

    Returns:
        List of deltas (length = len(values) - 1)
    """
    if len(values) < 2:
        return []

    deltas = []
    for i in range(1, len(values)):
        delta = values[i] - values[i - 1]
        # Handle negative deltas (session reset) by showing 0
        deltas.append(max(0, delta))

    return deltas
