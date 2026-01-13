from __future__ import annotations

from collections.abc import Iterable


def embargo_after(test_idx: Iterable[int], embargo: int) -> set[int]:
    """
    Return a set of indices that should be excluded *after* the test window,
    e.g. if test indices end at k, and embargo=2 -> exclude {k+1, k+2}.

    For multiple test indices, we embargo after each one, but effectively
    this is usually "after the max test index".
    """
    if embargo < 0:
        raise ValueError("embargo must be >= 0")

    test_idx_list = list(test_idx)
    if not test_idx_list or embargo == 0:
        return set()

    m = max(test_idx_list)
    return {m + i for i in range(1, embargo + 1)}


def purge_overlap(train_idx: list[int], test_idx: list[int]) -> list[int]:
    """
    Remove any training indices that overlap with the test indices.
    Keeps original order.
    """
    test_set = set(test_idx)
    return [i for i in train_idx if i not in test_set]
