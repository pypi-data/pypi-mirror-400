# tests/test_profiler.py
import pandas as pd
import mlready as mr


def make_df():
    return pd.DataFrame(
        {
            "TransactionID": ["ID_001", "ID_002", "ID_003", "ID_004"],
            "Date": ["2024-01-01", "2024-01-02", "2024-01-02", "2024-01-03"],
            "Product_Category": ["Electronics", "Clothing", "Electronics", "Home"],
            "Price": ["$1,200", "$50", "$1,100", "$300"],
            "Membership": ["Yes", "no", "YES", "n"],
        }
    )


def test_profile_basic_keys_and_types():
    df = make_df()
    p = mr.profile(df, top_k=5)

    assert "rows" in p and p["rows"] == 4
    assert "columns" in p and p["columns"] == 5
    assert "columns_profile" in p and isinstance(p["columns_profile"], dict)

    cols = p["columns_profile"]
    assert "Price" in cols
    assert "Membership" in cols
    assert "Date" in cols

    # pattern detection should show up for object-like cols
    assert "currency_like" in cols["Price"]
    assert "boolean_like" in cols["Membership"]
    assert "datetime_like" in cols["Date"]
