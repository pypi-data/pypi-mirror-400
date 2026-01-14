import pandas as pd
import pytest
from custos import PolicyTransformer


def test_quality_drop_row_drops_violating_rows():
    df = pd.DataFrame({
        "total_price": [10.0, -1.0, 5.0],
        "status": ["paid", "paid", "weird"],
    })

    policy = {
        "version": 1,
        "schema": {
            "types": {"total_price": "float"},
            "cast": {"on_cast_fail": "error"},
        },
        "quality": {
            "default_on_fail": "drop_row",
            "rules": [
                {"column": "total_price", "min": 0},
                {"column": "status", "accepted_values": ["paid", "pending", "refunded"]},
            ],
        },
    }

    t = PolicyTransformer(policy=policy, mode="strict")
    out, report = t.apply(df)

    # only first row should survive
    assert out.shape[0] == 1
    assert float(out["total_price"].iloc[0]) == 10.0
    assert out["status"].iloc[0] == "paid"

    kinds = [a.kind for a in report.actions]
    assert "quality_violations" in kinds
    assert "rows_dropped_due_to_quality" in kinds
    assert "quality_applied" in kinds


def test_quality_error_raises_on_violation():
    df = pd.DataFrame({"status": ["paid", "weird"]})

    policy = {
        "version": 1,
        "quality": {
            "rules": [
                {"column": "status", "accepted_values": ["paid"], "on_fail": "error"}
            ]
        },
    }

    t = PolicyTransformer(policy=policy, mode="strict")
    with pytest.raises(Exception):
        t.apply(df)


def test_quality_dry_run_does_not_change_df():
    df = pd.DataFrame({"x": [1, None, 3]})
    policy = {
        "version": 1,
        "quality": {"rules": [{"column": "x", "not_null": True}]},
    }

    t = PolicyTransformer(policy=policy, mode="dry_run")
    out, report = t.apply(df)

    assert out.equals(df)

    kinds = [a.kind for a in report.actions]
    assert "quality_dry_run" in kinds

def test_quality_named_rule_uses_name():
    df = pd.DataFrame({"x": [1, -1]})
    policy = {
        "version": 1,
        "quality": {
            "rules": [
                {"name": "x_non_negative", "column": "x", "min": 0}
            ]
        },
    }

    t = PolicyTransformer(policy=policy, mode="strict")
    out, report = t.apply(df)

    violations = next(a.details["violations"] for a in report.actions if a.kind == "quality_violations")
    assert violations[0]["rule_id"] == "x_non_negative"
