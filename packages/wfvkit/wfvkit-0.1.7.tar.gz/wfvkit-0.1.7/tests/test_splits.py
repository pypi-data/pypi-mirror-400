# tests/test_splits.py
import datetime as dt

import pytest

from wfvkit.splits import naive_time_split, walk_forward_splits


def test_naive_time_split_with_datetime_cutoff():
    times = [dt.datetime(2025, 1, 1, 0, 0) + dt.timedelta(minutes=i) for i in range(10)]
    tr, te = naive_time_split(times, times[6])  # cutoff at index 6 time
    assert tr == [0, 1, 2, 3, 4, 5]
    assert te == [6, 7, 8, 9]


def test_naive_time_split_with_index_cutoff():
    times = [dt.datetime(2025, 1, 1, 0, 0) + dt.timedelta(minutes=i) for i in range(10)]
    tr, te = naive_time_split(times, 6)  # index cutoff (exclusive)
    assert tr == [0, 1, 2, 3, 4, 5]
    assert te == [6, 7, 8, 9]


def test_naive_time_split_rejects_out_of_range_index():
    times = [dt.datetime(2025, 1, 1, 0, 0) + dt.timedelta(minutes=i) for i in range(10)]
    with pytest.raises(ValueError):
        naive_time_split(times, 11)
    with pytest.raises(ValueError):
        naive_time_split(times, -1)


def test_walk_forward_splits_basic():
    times = [dt.datetime(2025, 1, 1, 0, 0) + dt.timedelta(minutes=i) for i in range(10)]
    splits = list(walk_forward_splits(times, train_size=5, test_size=2, step=2, embargo=1))
    assert splits == [([0, 1, 2, 3, 4], [5, 6]), ([2, 3, 4, 5, 6], [7, 8])]
