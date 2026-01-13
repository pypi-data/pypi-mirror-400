from __future__ import annotations

import datetime as dt

from wfvkit import embargo_after, naive_time_split, purge_overlap, walk_forward_splits


def main():
    # Create a tiny timeline (10 points, 1-minute apart)
    start = dt.datetime(2025, 1, 1, 0, 0, 0)
    times = [start + dt.timedelta(minutes=i) for i in range(10)]

    print("TIMES:")
    for i, t in enumerate(times):
        print(f"  {i:02d}  {t}")

    print("\n1) Naive split (train_end = index 6 time):")
    train_end = times[6]
    train_idx, test_idx = naive_time_split(times, train_end=train_end)
    print("  train_idx:", train_idx)
    print("  test_idx :", test_idx)

    print("\n2) Walk-forward splits + purge + embargo demo:")
    train_size = 5
    test_size = 2
    step = 2
    embargo = 1

    for k, (tr, te) in enumerate(
        walk_forward_splits(
            times, train_size=train_size, test_size=test_size, step=step, embargo=embargo
        ),
        start=1,
    ):
        purged_tr = purge_overlap(tr, te)
        emb = embargo_after(te, embargo=embargo)

        print(f"\n  Split {k}:")
        print("    raw train:", tr)
        print("    test     :", te)
        print("    purged   :", purged_tr)
        print("    embargo  :", sorted(emb))


if __name__ == "__main__":
    main()
