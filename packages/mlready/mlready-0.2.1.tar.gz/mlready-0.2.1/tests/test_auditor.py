# tests/test_auditor.py
import pandas as pd
import mlready as mr


def make_train_test():
    train = pd.DataFrame(
        {
            "City": ["NY", "NY", "SF", "LA"],
            "Category": ["A", "B", "A", "B"],
            "y": [0, 1, 0, 1],
        }
    )
    test = pd.DataFrame(
        {
            "City": ["NY", "CHI", "SF", "CHI"],  # CHI unseen
            "Category": ["A", "B", "A", "B"],
            "y": [0, 1, 0, 1],
        }
    )
    return train, test


def test_audit_ghost_categories_detected():
    train, test = make_train_test()
    rep = mr.audit(test, target="y", reference_df=train)

    warnings = rep["warnings"]
    ghost = [w for w in warnings if w["rule"] == "ghost_categories" and w["column"] == "City"]
    assert len(ghost) == 1
    assert ghost[0]["severity"] in ("warning", "high")
    assert ghost[0]["evidence"]["unseen_count"] >= 1


def test_audit_zero_variance_detected():
    df = pd.DataFrame({"a": [1, 1, 1, 1], "b": [1, 2, 3, 4]})
    rep = mr.audit(df)
    zero = [w for w in rep["warnings"] if w["rule"] == "zero_variance" and w["column"] == "a"]
    assert len(zero) == 1
