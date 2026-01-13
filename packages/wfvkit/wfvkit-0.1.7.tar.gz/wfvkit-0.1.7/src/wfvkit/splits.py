# src/wfvkit/splits.py
from __future__ import annotations

import datetime as dt
from collections.abc import Iterator, Sequence


def naive_time_split(
    times: Sequence[dt.datetime], train_end: dt.datetime | int
) -> tuple[list[int], list[int]]:
    """
    Naive time split.

    Parameters
    ----------
    times:
        Sequence of datetimes, ordered.
    train_end:
        Either:
        - int: index cutoff (exclusive). Example: 6 -> train [0..5], test [6..end]
        - datetime: time cutoff. Train times strictly before it, test times at/after it.

    Returns
    -------
    (train_idx, test_idx)
        Lists of indices into `times`.
    """
    n = len(times)

    # Index cutoff mode
    if isinstance(train_end, int):
        cut = train_end
        if cut < 0 or cut > n:
            raise ValueError(f"train_end index must be in [0, {n}], got {cut}")
        return list(range(0, cut)), list(range(cut, n))

    # Datetime cutoff mode
    train_idx = [i for i, t in enumerate(times) if t < train_end]
    test_idx = [i for i, t in enumerate(times) if t >= train_end]
    return train_idx, test_idx


def walk_forward_splits(
    times: Sequence[dt.datetime],
    train_size: int,
    test_size: int,
    step: int,
    embargo: int = 0,
) -> Iterator[tuple[list[int], list[int]]]:
    """
    Generate walk-forward splits on an index basis.

    Yields (train_idx, test_idx). If `embargo > 0`, later utilities can use the embargo
    after each test segment (we also pass it through in demos, but the split itself
    does not remove embargo indices from the test set).

    Notes
    -----
    - train_size, test_size, step are in *number of samples* (indices)
    - `times` is used only for length/shape consistency; it is assumed ordered.
    """
    n = len(times)
    if train_size <= 0:
        raise ValueError("train_size must be > 0")
    if test_size <= 0:
        raise ValueError("test_size must be > 0")
    if step <= 0:
        raise ValueError("step must be > 0")
    if embargo < 0:
        raise ValueError("embargo must be >= 0")

    start = 0
    while True:
        train_start = start
        train_end = train_start + train_size
        test_start = train_end
        test_end = test_start + test_size

        if test_end > n:
            break

        train_idx = list(range(train_start, train_end))
        test_idx = list(range(test_start, test_end))
        yield train_idx, test_idx

        start += step
