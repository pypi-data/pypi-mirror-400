import pandas as pd
from custos import PolicyTransformer


def test_json_flatten_creates_columns():
    df = pd.DataFrame({
        "payload": [
            {"user": {"name": "Ann", "age": 30}},
            {"user": {"name": "Bob", "age": 40}},
        ]
    })

    policy = {
        "version": 1,
        "json_flatten": {"rules": [{"column": "payload", "max_depth": 2}]},
    }

    t = PolicyTransformer(policy=policy, mode="strict")
    out, report = t.apply(df)

    assert "user.name" in out.columns
    assert "user.age" in out.columns
    assert any(a.kind == "json_flatten_applied" for a in report.actions)


def test_json_flatten_drop_source():
    df = pd.DataFrame({"payload": [{"a": 1}]})
    policy = {"version": 1, "json_flatten": {"rules": [{"column": "payload", "drop_source": True}]}}
    out, _ = PolicyTransformer(policy=policy, mode="strict").apply(df)
    assert "payload" not in out.columns
    assert "a" in out.columns
