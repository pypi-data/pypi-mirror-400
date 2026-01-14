from __future__ import annotations

from typing import Any, Dict, Optional
import numpy as np
import pandas as pd

from .sampling import sample_df
from .utils import missing_stats, unique_stats, numeric_basic_stats, safe_top_k_value_counts, is_object_like
from .patterns import detect_currency_like, detect_boolean_like, detect_datetime_like, detect_date_range_hint


def profile(
    df: pd.DataFrame,
    target: Optional[str] = None,
    sample_frac: float = 0.05,
    sample_n_max: int = 5000,
    sample_n_min: int = 200,
    top_k: int = 20,
    random_state: int = 42,
) -> Dict[str, Any]:
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    smp = sample_df(df, target=target, sample_frac=sample_frac, sample_n_max=sample_n_max, sample_n_min=sample_n_min, random_state=random_state)

    out: Dict[str, Any] = {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "memory_bytes": int(df.memory_usage(deep=True).sum()),
        "duplicate_rows": int(df.duplicated().sum()) if df.shape[0] else 0,
        "sample": {"rows": int(smp.shape[0]), "sample_frac": float(sample_frac), "sample_n_max": int(sample_n_max), "sample_n_min": int(sample_n_min),},
        "columns_profile": {},
        "target_summary": None,
    }

    for col in df.columns:
        s = df[col]
        ss = smp[col] if col in smp.columns else s

        col_prof: Dict[str, Any] = {
            "dtype": str(s.dtype),
            **missing_stats(s),
            **unique_stats(s),
        }

        # stats
        if pd.api.types.is_numeric_dtype(s):
            col_prof.update(numeric_basic_stats(s))
            col_prof["logical_type"] = "numeric"
        else:
            # lightweight detection on sample
            if is_object_like(s):
                is_money = detect_currency_like(s, ss)
                is_bool = detect_boolean_like(s, ss)
                is_dt, dt_rate = detect_datetime_like(s, ss)
                has_range_hint = detect_date_range_hint(s, ss)

                col_prof["currency_like"] = bool(is_money)
                col_prof["boolean_like"] = bool(is_bool)
                col_prof["datetime_like"] = bool(is_dt)
                col_prof["datetime_parse_rate_sample"] = float(dt_rate)
                col_prof["date_range_hint"] = bool(has_range_hint)

                # logical type inference (simple)
                if is_bool:
                    col_prof["logical_type"] = "boolean"
                elif is_dt:
                    col_prof["logical_type"] = "datetime"
                elif is_money:
                    col_prof["logical_type"] = "numeric_string"
                else:
                    col_prof["logical_type"] = "categorical_or_text"
            else:
                col_prof["logical_type"] = "other"

        # top-k value counts (bounded; use sample for large object cols)
        if col != target:
            if is_object_like(s) and df.shape[0] > 200_000:
                col_prof["top_values"] = safe_top_k_value_counts(ss, top_k=top_k)
                col_prof["top_values_on"] = "sample"
            else:
                col_prof["top_values"] = safe_top_k_value_counts(s, top_k=top_k)
                col_prof["top_values_on"] = "full"

        out["columns_profile"][str(col)] = col_prof

    if target is not None and target in df.columns:
        y = df[target]
        if pd.api.types.is_numeric_dtype(y):
            out["target_summary"] = {"type": "numeric", **numeric_basic_stats(y)}
        else:
            vc = y.astype("string").value_counts(dropna=False)
            out["target_summary"] = {
                "type": "categorical",
                "classes": int(vc.shape[0]),
                "class_counts_top": {str(k): int(v) for k, v in vc.head(30).items()},
            }

    return out
