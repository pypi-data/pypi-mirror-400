from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple
import pandas as pd

from .exceptions import RecipeError
from .patterns import parse_money_to_float, normalize_boolean


@dataclass
class CleaningRecipe:
    version: str = "0.1.0"
    actions: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"version": self.version, "actions": self.actions, "meta": self.meta}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "CleaningRecipe":
        if not isinstance(d, dict) or "actions" not in d:
            raise RecipeError("Invalid recipe dict.")
        return cls(version=str(d.get("version", "0.1.0")), actions=dict(d["actions"]), meta=dict(d.get("meta", {})))

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> "CleaningRecipe":
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

    def transform(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        clean = df.copy()
        report: Dict[str, Any] = {"applied": []}

        for col, spec in self.actions.items():
            if col not in clean.columns:
                report["applied"].append({"column": col, "action": spec.get("action"), "status": "skipped_missing"})
                continue

            action = spec.get("action")
            if action == "money_to_float":
                clean[col] = parse_money_to_float(clean[col])
                report["applied"].append({"column": col, "action": action, "status": "ok"})
            elif action == "bool_normalize":
                clean[col] = normalize_boolean(clean[col])
                report["applied"].append({"column": col, "action": action, "status": "ok"})
            elif action == "datetime_parse":
                clean[col] = pd.to_datetime(clean[col], errors="coerce")
                report["applied"].append({"column": col, "action": action, "status": "ok"})
            elif action == "int_downcast_nullable":
                # expects the column already numeric/integer-like
                dtype = spec.get("dtype", "Int64")
                clean[col] = clean[col].astype(dtype)
                report["applied"].append({"column": col, "action": action, "status": "ok", "dtype": dtype})
            else:
                report["applied"].append({"column": col, "action": action, "status": "unknown_action"})

        return clean, report
