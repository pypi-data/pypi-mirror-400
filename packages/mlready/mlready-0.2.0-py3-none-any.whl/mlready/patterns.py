from __future__ import annotations

import warnings
import re
from typing import Any, Dict, Optional, Tuple
import numpy as np
import pandas as pd

_CURRENCY_RE = re.compile(r"[\$\€\£\₹]")
_SCALE_RE = re.compile(r"^\s*([-+]?\d+(?:\.\d+)?)\s*([kKmMbB])\s*$")
_PARENS_NEG_RE = re.compile(r"^\s*\(\s*.+\s*\)\s*$")
_NUMERIC_LIKE_RE = re.compile(r"^\s*[-+]?[\d,]+(\.\d+)?\s*$")

_BOOL_TRUE = {"true", "t", "yes", "y", "1"}
_BOOL_FALSE = {"false", "f", "no", "n", "0"}

_DATE_RANGE_HINT_RE = re.compile(
    r"\b(?:to|–|-)\b", re.IGNORECASE
)  # weak signal; used only as flag


def detect_currency_like(series: pd.Series, sample: pd.Series) -> bool:
    if sample.dropna().empty:
        return False
    s = sample.dropna().astype(str).head(2000)
    hits = s.str.contains(_CURRENCY_RE).mean()
    return bool(hits >= 0.2)


def detect_boolean_like(series: pd.Series, sample: pd.Series) -> bool:
    if sample.dropna().empty:
        return False
    s = sample.dropna().astype(str).str.strip().str.lower()
    vals = set(s.unique().tolist())
    if not vals:
        return False
    # boolean-like if values are subset of known tokens (allow small noise)
    good = sum(v in (_BOOL_TRUE | _BOOL_FALSE) for v in vals)
    return (good / max(1, len(vals))) >= 0.8


def detect_datetime_like(series: pd.Series, sample: pd.Series) -> Tuple[bool, float]:
    if sample.dropna().empty:
        return (False, 0.0)
    s = sample.dropna().astype(str).head(2000)

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="Could not infer format, so each element will be parsed individually",
            category=UserWarning,
        )
        dt = pd.to_datetime(s, errors="coerce")

    rate = float(dt.notna().mean())
    return (rate >= 0.7, rate)



def detect_date_range_hint(series: pd.Series, sample: pd.Series) -> bool:
    if sample.dropna().empty:
        return False
    s = sample.dropna().astype(str).head(2000)
    # Just a hint flag; do not parse ranges in v1
    hits = s.str.contains(_DATE_RANGE_HINT_RE).mean()
    return bool(hits >= 0.3)


def parse_money_to_float(series: pd.Series) -> pd.Series:
    """
    Safe-ish numeric normalization:
    - handles currency symbols
    - commas
    - accounting negatives (parentheses)
    - K/M/B suffix (1.2M -> 1200000)
    """
    s = series.astype("string")

    # mark accounting negatives
    is_parens = s.str.match(_PARENS_NEG_RE, na=False)
    s_clean = s.str.replace(r"[()\s]", "", regex=True)

    # strip currency symbols and common suffix "/-"
    s_clean = s_clean.str.replace(_CURRENCY_RE, "", regex=True)
    s_clean = s_clean.str.replace(r"/-\s*$", "", regex=True)

    # handle scale suffix K/M/B
    scale = s_clean.str.extract(_SCALE_RE, expand=True)
    num_part = scale[0]
    suf_part = scale[1]

    # fallback: plain numeric-like values
    plain_mask = s_clean.str.match(_NUMERIC_LIKE_RE, na=False)

    out = pd.Series([pd.NA] * len(s_clean), index=s_clean.index, dtype="Float64")

    # scaled values
    scaled_mask = num_part.notna() & suf_part.notna()
    if scaled_mask.any():
        nums = pd.to_numeric(num_part[scaled_mask].str.replace(",", "", regex=False), errors="coerce")
        mult = suf_part[scaled_mask].str.lower().map({"k": 1e3, "m": 1e6, "b": 1e9}).astype(float)
        out.loc[scaled_mask] = (nums * mult).astype("Float64")

    # plain values
    if plain_mask.any():
        nums = pd.to_numeric(s_clean[plain_mask].str.replace(",", "", regex=False), errors="coerce")
        out.loc[plain_mask] = nums.astype("Float64")

    # apply negatives for parenthesis
    out.loc[is_parens & out.notna()] = -out.loc[is_parens & out.notna()]

    return out


def normalize_boolean(series: pd.Series) -> pd.Series:
    s = series.astype("string").str.strip().str.lower()
    out = pd.Series([pd.NA] * len(s), index=s.index, dtype="boolean")
    out.loc[s.isin(_BOOL_TRUE)] = True
    out.loc[s.isin(_BOOL_FALSE)] = False
    return out
