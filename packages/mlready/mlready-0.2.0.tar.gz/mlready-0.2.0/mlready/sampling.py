from __future__ import annotations

from typing import Optional
import numpy as np
import pandas as pd


def compute_sample_n(n_rows: int, sample_frac: float, sample_n_max: int, sample_n_min: int) -> int:
    if n_rows <= 0:
        return 0
    n = int(max(sample_n_min, round(n_rows * sample_frac)))
    return int(min(n, sample_n_max, n_rows))


def sample_df(
    df: pd.DataFrame,
    target: Optional[str] = None,
    sample_frac: float = 0.05,
    sample_n_max: int = 5000,
    sample_n_min: int = 200,
    random_state: int = 42,
) -> pd.DataFrame:
    n_rows = int(df.shape[0])
    n = compute_sample_n(n_rows, sample_frac, sample_n_max, sample_n_min)
    if n_rows == 0 or n >= n_rows:
        return df

    if target is None or target not in df.columns:
        return df.sample(n=n, random_state=random_state)

    # Stratified sampling for classification targets (best-effort).
    y = df[target]
    # If too many unique values, stratification isn’t meaningful; fallback to random.
    if y.nunique(dropna=True) > 50:
        return df.sample(n=n, random_state=random_state)

    # Sample roughly proportional to class frequencies
    rng = np.random.default_rng(random_state)
    parts = []
    for label, group in df.groupby(target, dropna=False):
        k = max(1, int(round(len(group) * (n / n_rows))))
        k = min(k, len(group))
        idx = rng.choice(group.index.to_numpy(), size=k, replace=False)
        parts.append(df.loc[idx])

    out = pd.concat(parts, axis=0)
    # If rounding drift causes too many/few rows, fix by trimming or topping up randomly
    if len(out) > n:
        out = out.sample(n=n, random_state=random_state)
    elif len(out) < n:
        remaining = df.drop(index=out.index, errors="ignore")
        if len(remaining) > 0:
            add = remaining.sample(n=min(n - len(out), len(remaining)), random_state=random_state)
            out = pd.concat([out, add], axis=0)

    return out
