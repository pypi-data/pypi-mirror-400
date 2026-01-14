from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
import numpy as np
import pandas as pd

from .sampling import sample_df
from .patterns import detect_currency_like, detect_boolean_like, detect_datetime_like, parse_money_to_float, normalize_boolean
from .recipe import CleaningRecipe
from .utils import is_object_like


def _choose_nullable_int_dtype(minv: int, maxv: int) -> str:
    if -128 <= minv <= 127 and -128 <= maxv <= 127:
        return "Int8"
    if -32768 <= minv <= 32767 and -32768 <= maxv <= 32767:
        return "Int16"
    if -(2**31) <= minv <= (2**31 - 1) and -(2**31) <= maxv <= (2**31 - 1):
        return "Int32"
    return "Int64"


def apply(
    df: pd.DataFrame,
    recipe: Optional[CleaningRecipe] = None,
    mode: str = "safe",
    target: Optional[str] = None,
    sample_frac: float = 0.05,
    sample_n_max: int = 5000,
    sample_n_min: int = 200,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, CleaningRecipe, Dict[str, Any]]:
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    if mode not in ("safe",):
        raise ValueError("Only mode='safe' is supported in v1")

    # If recipe provided, just transform deterministically
    if recipe is not None:
        clean_df, transform_report = recipe.transform(df)
        return clean_df, recipe, {"mode": mode, **transform_report}

    # Otherwise, build recipe (fit) from df (train-only in a real workflow)
    smp = sample_df(df, target=target, sample_frac=sample_frac, sample_n_max=sample_n_max, sample_n_min=sample_n_min, random_state=random_state)

    actions: Dict[str, Dict[str, Any]] = {}
    report: Dict[str, Any] = {"mode": mode, "fitted_on_rows": int(df.shape[0]), "decisions": []}

    clean = df.copy()

    for col in df.columns:
        if col == target:
            continue

        s = df[col]
        ss = smp[col] if col in smp.columns else s

        # boolean normalization (object-like only)
        if is_object_like(s) and detect_boolean_like(s, ss):
            actions[str(col)] = {"action": "bool_normalize"}
            clean[col] = normalize_boolean(clean[col])
            report["decisions"].append({"column": str(col), "action": "bool_normalize"})
            continue

        # money/numeric string
        if is_object_like(s) and detect_currency_like(s, ss):
            actions[str(col)] = {"action": "money_to_float"}
            clean[col] = parse_money_to_float(clean[col])
            report["decisions"].append({"column": str(col), "action": "money_to_float"})
            continue

        # datetime-like (unambiguous enough)
        if is_object_like(s):
            is_dt, rate = detect_datetime_like(s, ss)
            if is_dt and rate >= 0.85:
                actions[str(col)] = {"action": "datetime_parse"}
                clean[col] = pd.to_datetime(clean[col], errors="coerce")
                report["decisions"].append({"column": str(col), "action": "datetime_parse", "sample_parse_rate": rate})
                continue

        # integer downcast (nullable-safe) for numeric columns
        if pd.api.types.is_integer_dtype(s):
            # pandas int w/out NA can downcast; but we keep nullable safety consistent
            mn, mx = int(s.min()), int(s.max())
            dtype = _choose_nullable_int_dtype(mn, mx)
            if dtype != "Int64":
                actions[str(col)] = {"action": "int_downcast_nullable", "dtype": dtype}
                clean[col] = clean[col].astype(dtype)
                report["decisions"].append({"column": str(col), "action": "int_downcast_nullable", "dtype": dtype})
            continue

        # float columns that are integer-like (nullable)
        if pd.api.types.is_float_dtype(s):
            # check integer-like without scanning everything expensively: still needs dropna mod 1 check
            nonnull = s.dropna()
            if len(nonnull) > 0 and (nonnull % 1 == 0).all():
                mn, mx = int(nonnull.min()), int(nonnull.max())
                dtype = _choose_nullable_int_dtype(mn, mx)
                actions[str(col)] = {"action": "int_downcast_nullable", "dtype": dtype}
                clean[col] = pd.to_numeric(clean[col], errors="coerce").astype(dtype)
                report["decisions"].append({"column": str(col), "action": "int_downcast_nullable", "dtype": dtype, "from": "float"})
            continue

    recipe_out = CleaningRecipe(
        actions=actions,
        meta={
            "mode": mode,
            "sample_frac": float(sample_frac),
            "sample_n_max": int(sample_n_max),
            "random_state": int(random_state),
            "sample_n_min": int(sample_n_min),
        },
    )
    return clean, recipe_out, report
