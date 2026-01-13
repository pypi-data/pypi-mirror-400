"""
examples/leakage_demo.py

Demonstration of *label leakage* in time-ordered ML when labels use a forward
horizon (e.g., forward returns). Even with a simple time split, the last
`horizon` training labels can "peek" into the future test period.

This script shows:
1) naive time split accuracy (leaky near the boundary)
2) "purged-by-horizon" accuracy (drops last `horizon` train samples before test)
3) optional walk-forward summary (naive vs purged-by-horizon)

Requires: numpy
Uses wfvkit: naive_time_split, walk_forward_splits, purge_overlap, embargo_after
"""

from __future__ import annotations

import datetime as dt

import numpy as np

from wfvkit import embargo_after, naive_time_split, purge_overlap, walk_forward_splits


# ----------------------------
# Data + label construction
# ----------------------------
def make_series(n: int = 2000, seed: int = 7) -> tuple[list[dt.datetime], np.ndarray]:
    """
    Synthetic returns with a regime shift:
      - first part has slightly negative drift
      - second part has slightly positive drift
    This makes a forward-looking label "flip" around the boundary, which makes
    leakage effects easy to see.
    """
    rng = np.random.default_rng(seed)

    # regime change point
    split = int(n * 0.7)

    r1 = rng.normal(loc=-0.0010, scale=0.01, size=split)
    r2 = rng.normal(loc=+0.0010, scale=0.01, size=n - split)
    returns = np.concatenate([r1, r2])

    start = dt.datetime(2025, 1, 1, 0, 0, 0)
    times = [start + dt.timedelta(minutes=i) for i in range(n)]
    return times, returns


def make_label(returns: np.ndarray, horizon: int = 50) -> np.ndarray:
    """
    Forward-looking label:
      y[i] = 1 if sum of next `horizon` returns is positive else 0
    """
    y = np.zeros(len(returns), dtype=int)
    for i in range(len(returns) - horizon):
        y[i] = int(returns[i + 1 : i + 1 + horizon].sum() > 0)
    # last `horizon` labels are undefined (no future). Keep as 0.
    return y


def make_features(returns: np.ndarray, lags: int = 25) -> np.ndarray:
    """
    Simple features available at time i:
      - last `lags` returns
      - mean of last `lags` returns
      - std  of last `lags` returns
      - time index fraction (helps model detect regime)
    """
    n = len(returns)
    X = np.zeros((n, lags + 3), dtype=float)

    for i in range(n):
        start = max(0, i - lags)
        window = returns[start:i]  # strictly past
        # pad left with zeros if not enough history
        padded = np.zeros(lags, dtype=float)
        if len(window) > 0:
            padded[-len(window) :] = window

        X[i, :lags] = padded
        X[i, lags] = padded.mean()
        X[i, lags + 1] = padded.std()
        X[i, lags + 2] = i / max(1, (n - 1))  # time fraction

    return X


# ----------------------------
# Tiny model (no sklearn)
# ----------------------------
def _standardize_fit(X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mu = X.mean(axis=0)
    sd = X.std(axis=0)
    sd[sd == 0] = 1.0
    return mu, sd


def _standardize_apply(X: np.ndarray, mu: np.ndarray, sd: np.ndarray) -> np.ndarray:
    return (X - mu) / sd


def ridge_fit(X: np.ndarray, y: np.ndarray, alpha: float = 1e-2) -> np.ndarray:
    """
    Very small ridge regression "classifier":
      w = argmin ||Xw - y||^2 + alpha||w||^2
    Then predict y_hat = 1 if Xw >= 0.5 else 0
    """
    Xb = np.c_[np.ones(len(X)), X]
    A = Xb.T @ Xb + alpha * np.eye(Xb.shape[1])
    w = np.linalg.solve(A, Xb.T @ y)
    return w


def ridge_predict(X: np.ndarray, w: np.ndarray) -> np.ndarray:
    Xb = np.c_[np.ones(len(X)), X]
    s = Xb @ w
    return (s >= 0.5).astype(int)


def accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if len(y_true) == 0:
        return float("nan")
    return float((y_true == y_pred).mean())


# ----------------------------
# Leakage guards (demo)
# ----------------------------
def purge_by_horizon(train_idx: list[int], test_idx: list[int], horizon: int) -> list[int]:
    """
    IMPORTANT: This is the key label-leakage fix when labels use a forward horizon.

    If test starts at k = min(test_idx), then any training sample i where
    i + horizon >= k has a label that uses returns inside the test window.

    So we drop training indices i >= k - horizon.
    """
    if not test_idx:
        return train_idx
    k = min(test_idx)
    cutoff = k - horizon
    return [i for i in train_idx if i < cutoff]


def apply_embargo_to_train(train_idx: list[int], embargo_idx: set[int]) -> list[int]:
    return [i for i in train_idx if i not in embargo_idx]


# ----------------------------
# Experiments
# ----------------------------
def evaluate_split(
    X: np.ndarray,
    y: np.ndarray,
    train_idx: list[int],
    test_idx: list[int],
) -> float:
    Xtr = X[train_idx]
    ytr = y[train_idx]
    Xte = X[test_idx]
    yte = y[test_idx]

    mu, sd = _standardize_fit(Xtr)
    Xtr = _standardize_apply(Xtr, mu, sd)
    Xte = _standardize_apply(Xte, mu, sd)

    w = ridge_fit(Xtr, ytr, alpha=1e-2)
    yp = ridge_predict(Xte, w)
    return accuracy(yte, yp)


def main() -> None:
    # knobs
    n = 2000
    lags = 25
    horizon = 50

    times, returns = make_series(n=n, seed=7)
    y = make_label(returns, horizon=horizon)
    X = make_features(returns, lags=lags)

    # valid indices: need enough past for features and enough future for label
    valid = list(range(lags, n - horizon))
    times_v = [times[i] for i in valid]
    Xv = X[valid]
    yv = y[valid]

    # --- 1) Naive time split (by datetime cutoff) ---
    cut_dt = times_v[int(len(times_v) * 0.70)]
    train_idx, test_idx = naive_time_split(times_v, train_end=cut_dt)

    acc_naive = evaluate_split(Xv, yv, train_idx, test_idx)

    # Apply package helpers (may do nothing here, but shown for completeness)
    train_no_overlap = purge_overlap(train_idx, test_idx)
    embargo_idx = set(embargo_after(test_idx, embargo=horizon))
    train_pkg = apply_embargo_to_train(train_no_overlap, embargo_idx)
    acc_pkg = evaluate_split(Xv, yv, train_pkg, test_idx)

    # --- 2) Purge-by-horizon (the real label-leakage guard) ---
    train_purged = purge_by_horizon(train_idx, test_idx, horizon=horizon)
    train_purged = apply_embargo_to_train(train_purged, embargo_idx)
    acc_purged = evaluate_split(Xv, yv, train_purged, test_idx)

    print("=== Single split ===")
    print(f"Total samples (valid): {len(times_v)}")
    print(f"Train size (naive):    {len(train_idx)}")
    print(f"Test size:             {len(test_idx)}")
    print(f"Label horizon:         {horizon}")
    print()
    print(f"Accuracy (naive split):                 {acc_naive:.3f}")
    print(f"Accuracy (+ purge_overlap + embargo):   {acc_pkg:.3f}")
    print(f"Accuracy (+ purge_by_horizon + embargo): {acc_purged:.3f}")
    print()

    # --- 3) Walk-forward (optional summary) ---
    train_size = 800
    test_size = 200
    step = 200
    embargo = 0  # we'll handle embargo explicitly via embargo_after()

    accs_naive = []
    accs_purged = []

    for tr_i, te_i in walk_forward_splits(
        times_v,
        train_size=train_size,
        test_size=test_size,
        step=step,
        embargo=embargo,
    ):
        # naive
        a0 = evaluate_split(Xv, yv, tr_i, te_i)
        accs_naive.append(a0)

        # purged-by-horizon + embargo
        tr_p = purge_by_horizon(tr_i, te_i, horizon=horizon)
        emb = set(embargo_after(te_i, embargo=horizon))
        tr_p = apply_embargo_to_train(tr_p, emb)
        a1 = evaluate_split(Xv, yv, tr_p, te_i)
        accs_purged.append(a1)

    print("=== Walk-forward summary ===")
    print(f"Splits: {len(accs_naive)}  (train={train_size}, test={test_size}, step={step})")
    print(f"Mean accuracy (naive):   {np.mean(accs_naive):.3f}")
    print(f"Mean accuracy (purged):  {np.mean(accs_purged):.3f}")
    print()
    print("Note: purge_by_horizon is the key guard when labels use forward horizons.")


if __name__ == "__main__":
    main()
