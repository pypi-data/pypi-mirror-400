from __future__ import annotations

from wfvkit.leakage import embargo_after, purge_overlap


def test_embargo_after_basic():
    test_idx = [10, 11]
    embargoed = embargo_after(test_idx=test_idx, embargo=2)
    assert embargoed == {12, 13}


def test_purge_overlap_basic():
    # train labels overlap with test labels → must be removed
    train_idx = [0, 1, 2, 3, 4, 5]
    test_idx = [3, 4]
    purged = purge_overlap(train_idx=train_idx, test_idx=test_idx)
    assert purged == [0, 1, 2, 5]
