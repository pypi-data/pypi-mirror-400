import pandas as pd
from custos import PolicyTransformer

def test_rename_columns_applies():
    df = pd.DataFrame({"Total Price": [10.0, 20.0], "Order ID": [1, 2]})

    policy = {
        "version": 1,
        "schema": {
            "rename": {
                "Total Price": "total_price",
                "Order ID": "order_id",
            }
        },
    }

    t = PolicyTransformer(policy=policy)
    out, report = t.apply(df)

    assert "total_price" in out.columns
    assert "order_id" in out.columns
    assert "Total Price" not in out.columns
    assert "Order ID" not in out.columns
    assert report.rows_in == 2
    assert report.rows_out == 2

def test_rename_dry_run_does_not_modify():
    df = pd.DataFrame({"A": [1]})
    policy = {"schema": {"rename": {"A": "a"}}}

    t = PolicyTransformer(policy, mode="dry_run")
    out, report = t.apply(df)

    assert "A" in out.columns
    assert "a" not in out.columns
