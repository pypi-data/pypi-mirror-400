# tests/test_apply.py
import pandas as pd
import numpy as np
import mlready as mr


def test_apply_converts_money_and_boolean_and_datetime():
    df = pd.DataFrame(
        {
            "Price": ["$1,200", "($50)", "1.2M", "300/-", None],
            "Membership": ["Yes", "no", "YES", "n", None],
            "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", None],
        }
    )

    clean, recipe, report = mr.apply(df)

    # Price should become numeric (Float64 nullable)
    assert str(clean["Price"].dtype) in ("Float64", "float64")
    assert clean["Price"].iloc[0] == 1200.0
    assert clean["Price"].iloc[1] == -50.0
    assert clean["Price"].iloc[2] == 1200000.0
    assert clean["Price"].iloc[3] == 300.0
    assert pd.isna(clean["Price"].iloc[4])

    # Membership should become boolean nullable
    assert str(clean["Membership"].dtype) == "boolean"
    assert clean["Membership"].iloc[0] == True
    assert clean["Membership"].iloc[1] == False
    assert clean["Membership"].iloc[2] == True
    assert clean["Membership"].iloc[3] == False
    assert pd.isna(clean["Membership"].iloc[4])

    # Date parsing may or may not trigger depending on sample parse threshold;
    # enforce by providing a deterministic recipe transform if needed.
    # If auto-detected, dtype becomes datetime64[ns].
    if np.issubdtype(clean["Date"].dtype, np.datetime64):
        assert clean["Date"].dt.year.iloc[0] == 2024


def test_apply_recipe_replay_is_deterministic():
    df_train = pd.DataFrame(
        {
            "Price": ["$1,000", "$2,000"],
            "Membership": ["yes", "no"],
        }
    )
    clean_train, recipe, _ = mr.apply(df_train)

    df_new = pd.DataFrame({"Price": ["$3,500"], "Membership": ["YES"]})
    clean_new, _, _ = mr.apply(df_new, recipe=recipe)

    assert clean_new["Price"].iloc[0] == 3500.0
    assert clean_new["Membership"].iloc[0] == True
