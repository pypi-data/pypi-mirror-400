from __future__ import annotations

from typing import Any, Dict
import numpy as np
import pandas as pd


def is_object_like(series: pd.Series) -> bool:
    return pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series)


def safe_top_k_value_counts(series: pd.Series, top_k: int = 20) -> Dict[str, int]:
    # Keep report bounded: convert keys to str for JSON compatibility
    vc = series.dropna().astype(str).value_counts(dropna=True).head(top_k)
    return {str(k): int(v) for k, v in vc.items()}


def missing_stats(series: pd.Series) -> Dict[str, Any]:
    n = int(series.shape[0])
    miss = int(series.isna().sum())
    return {"missing_count": miss, "missing_pct": float(miss / n) if n else 0.0}


def unique_stats(series: pd.Series) -> Dict[str, Any]:
    n = int(series.shape[0])
    nun = int(series.nunique(dropna=True))
    return {"unique_count": nun, "unique_pct": float(nun / n) if n else 0.0}


def numeric_basic_stats(series: pd.Series) -> Dict[str, Any]:
    s = pd.to_numeric(series, errors="coerce")
    if s.notna().sum() == 0:
        return {}
    return {
        "min": float(np.nanmin(s.values)),
        "max": float(np.nanmax(s.values)),
        "mean": float(np.nanmean(s.values)),
        "std": float(np.nanstd(s.values)),
    }
