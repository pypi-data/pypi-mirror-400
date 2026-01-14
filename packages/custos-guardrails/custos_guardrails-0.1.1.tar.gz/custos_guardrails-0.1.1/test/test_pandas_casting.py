import pandas as pd
import pytest
from custos import PolicyTransformer


def test_cast_drop_row_drops_bad_rows():
    df = pd.DataFrame({"order_id": ["1", "x", "3"], "total_price": ["10.5", "20.0", "oops"]})

    policy = {
        "version": 1,
        "schema": {
            "types": {"order_id": "int", "total_price": "float"},
            "cast": {"on_cast_fail": "drop_row"},
        },
    }

    t = PolicyTransformer(policy=policy, mode="strict")
    out, report = t.apply(df)

    # row 0 ok, row 1 fails order_id, row 2 fails total_price => only 1 row remains
    assert out.shape[0] == 1
    assert int(out["order_id"].iloc[0]) == 1
    assert float(out["total_price"].iloc[0]) == 10.5

    # report contains cast actions
    kinds = [a.kind for a in report.actions]
    assert "cast_failures" in kinds
    assert "rows_dropped_due_to_cast" in kinds
    assert "cast_applied" in kinds


def test_cast_error_raises():
    df = pd.DataFrame({"order_id": ["1", "x"]})

    policy = {
        "version": 1,
        "schema": {
            "types": {"order_id": "int"},
            "cast": {"on_cast_fail": "error"},
        },
    }

    t = PolicyTransformer(policy=policy, mode="strict")
    with pytest.raises(Exception):
        t.apply(df)


def test_cast_set_null_sets_only_bad_values_to_null():
    df = pd.DataFrame({"order_id": ["1", "x", "3"]})

    policy = {
        "version": 1,
        "schema": {
            "types": {"order_id": "int"},
            "cast": {"on_cast_fail": "set_null"},
        },
    }

    t = PolicyTransformer(policy=policy, mode="strict")
    out, report = t.apply(df)

    assert out.shape[0] == 3
    assert str(out["order_id"].dtype).lower().startswith("int")
    assert pd.isna(out["order_id"].iloc[1])
    assert int(out["order_id"].iloc[0]) == 1
    assert int(out["order_id"].iloc[2]) == 3
