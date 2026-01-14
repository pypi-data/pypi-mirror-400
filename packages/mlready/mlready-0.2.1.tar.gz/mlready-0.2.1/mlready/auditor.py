from __future__ import annotations

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from .sampling import sample_df
from .patterns import detect_currency_like, detect_boolean_like, detect_datetime_like, detect_date_range_hint
from .utils import is_object_like


def _warn(rule: str, column: Optional[str], severity: str, confidence: float, evidence: Dict[str, Any], recommendation: str):
    return {
        "rule": rule,
        "column": column,
        "severity": severity,
        "confidence": float(max(0.0, min(1.0, confidence))),
        "evidence": evidence,
        "recommendation": recommendation,
    }


def audit(
    df: pd.DataFrame,
    target: Optional[str] = None,
    reference_df: Optional[pd.DataFrame] = None,
    sample_frac: float = 0.05,
    sample_n_max: int = 5000,
    sample_n_min: int = 200,
    random_state: int = 42,
    top_new_categories: int = 20,
) -> Dict[str, Any]:
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    smp = sample_df(df, target=target, sample_frac=sample_frac, sample_n_max=sample_n_max,  sample_n_min=sample_n_min, random_state=random_state)
    warnings: List[Dict[str, Any]] = []

    n_rows = int(df.shape[0])

    # Basic column checks
    for col in df.columns:
        if col == target:
            continue

        s = df[col]
        ss = smp[col] if col in smp.columns else s

        nunique = int(s.nunique(dropna=True))
        unique_ratio = float(nunique / n_rows) if n_rows else 0.0

        # zero variance
        if nunique <= 1:
            warnings.append(_warn(
                "zero_variance",
                str(col),
                "warning",
                0.95,
                {"unique_count": nunique},
                "Column has 0 variance; consider dropping for ML.",
            ))
            continue

        # ID-like detection (near unique + string/object)
        if unique_ratio >= 0.98 and is_object_like(s):
            warnings.append(_warn(
                "id_like",
                str(col),
                "warning",
                0.85,
                {"unique_pct": unique_ratio, "unique_count": nunique},
                "Looks like an identifier (near-unique). Avoid using as a feature.",
            ))

        # high-cardinality categoricals
        if is_object_like(s) and 0.2 <= unique_ratio < 0.98:
            warnings.append(_warn(
                "high_cardinality",
                str(col),
                "info",
                0.7,
                {"unique_pct": unique_ratio, "unique_count": nunique},
                "High-cardinality category risk. One-hot may overfit or explode dimensions.",
            ))

        # pattern hints (sampled)
        if is_object_like(s):
            if detect_currency_like(s, ss):
                warnings.append(_warn(
                    "money_like",
                    str(col),
                    "info",
                    0.8,
                    {"checked_on": "sample", "sample_rows": int(ss.shape[0])},
                    "Column looks like money/numeric string; consider numeric normalization.",
                ))
            if detect_boolean_like(s, ss):
                warnings.append(_warn(
                    "boolean_like",
                    str(col),
                    "info",
                    0.85,
                    {"checked_on": "sample", "sample_rows": int(ss.shape[0])},
                    "Column looks boolean-like; consider mapping to boolean dtype.",
                ))
            is_dt, rate = detect_datetime_like(s, ss)
            if is_dt:
                warnings.append(_warn(
                    "datetime_like",
                    str(col),
                    "info",
                    min(0.95, max(0.6, rate)),
                    {"parse_rate_sample": rate, "checked_on": "sample"},
                    "Column looks datetime-like; consider parsing to datetime.",
                ))
            if detect_date_range_hint(s, ss):
                warnings.append(_warn(
                    "date_range_hint",
                    str(col),
                    "info",
                    0.6,
                    {"checked_on": "sample"},
                    "Column may contain date ranges; do not force single-date conversion in v1.",
                ))

    # Target leakage sentinel (warn-only; simple correlation for numeric targets)
    if target is not None and target in df.columns:
        y = df[target]
        if pd.api.types.is_numeric_dtype(y):
            y_num = pd.to_numeric(y, errors="coerce")
            if y_num.notna().sum() > 0:
                for col in df.columns:
                    if col == target:
                        continue
                    x = df[col]
                    if pd.api.types.is_numeric_dtype(x):
                        x_num = pd.to_numeric(x, errors="coerce")
                        if x_num.notna().sum() > 0:
                            corr = float(x_num.corr(y_num))
                            if np.isfinite(corr) and abs(corr) >= 0.99:
                                warnings.append(_warn(
                                    "possible_leakage",
                                    str(col),
                                    "high",
                                    0.9,
                                    {"corr": corr},
                                    "Feature is almost identical to target (|corr|>=0.99). Investigate leakage.",
                                ))

    # reference_df comparisons (category mismatch + schema drift)
    if reference_df is not None:
        if not isinstance(reference_df, pd.DataFrame):
            raise TypeError("reference_df must be a pandas DataFrame")

        # columns missing/extra
        ref_cols = set(reference_df.columns)
        cur_cols = set(df.columns)

        missing_cols = sorted(list(ref_cols - cur_cols))
        extra_cols = sorted(list(cur_cols - ref_cols))
        if missing_cols:
            warnings.append(_warn(
                "schema_missing_columns",
                None,
                "high",
                0.95,
                {"missing_columns": missing_cols},
                "Test/production data is missing columns present in reference_df.",
            ))
        if extra_cols:
            warnings.append(_warn(
                "schema_extra_columns",
                None,
                "info",
                0.7,
                {"extra_columns": extra_cols},
                "Data has extra columns not in reference_df. Ensure pipeline handles them.",
            ))

        # dtype drift + ghost categories
        common = sorted(list(ref_cols & cur_cols))
        for col in common:
            if col == target:
                continue
            ref_s = reference_df[col]
            cur_s = df[col]

            if str(ref_s.dtype) != str(cur_s.dtype):
                warnings.append(_warn(
                    "dtype_drift",
                    str(col),
                    "warning",
                    0.8,
                    {"reference_dtype": str(ref_s.dtype), "current_dtype": str(cur_s.dtype)},
                    "Column dtype differs from reference_df; may break downstream transformers.",
                ))

            # category mismatch for object-like columns (top priority)
            if is_object_like(ref_s) and is_object_like(cur_s):
                ref_vals = set(reference_df[col].dropna().astype(str).unique().tolist())
                cur_vals = df[col].dropna().astype(str).unique()
                unseen = [v for v in cur_vals.tolist() if v not in ref_vals]
                if unseen:
                    # show top unseen by frequency
                    unseen_series = df.loc[df[col].astype(str).isin(unseen), col].astype(str)
                    top_unseen = unseen_series.value_counts().head(top_new_categories)
                    affected_pct = float(unseen_series.shape[0] / max(1, df.shape[0]))
                    warnings.append(_warn(
                        "ghost_categories",
                        str(col),
                        "high" if affected_pct >= 0.05 else "warning",
                        0.9,
                        {
                            "unseen_count": int(len(unseen)),
                            "affected_rows_pct": affected_pct,
                            "top_unseen": {str(k): int(v) for k, v in top_unseen.items()},
                        },
                        "Found categories in df not present in reference_df. One-hot/encoders may fail.",
                    ))

    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "sample": {"rows": int(smp.shape[0]), "sample_frac": float(sample_frac), "sample_n_max": int(sample_n_max), "sample_n_min": int(sample_n_min),},
        "warnings": warnings,
    }
