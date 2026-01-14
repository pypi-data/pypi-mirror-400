import os
import pandas as pd
from custos import PolicyTransformer


def test_pii_drop_column():
    df = pd.DataFrame({"email": ["a@test.com"], "x": [1]})
    policy = {
        "version": 1,
        "pii": {"rules": [{"column": "email", "action": "drop"}]},
    }

    t = PolicyTransformer(policy=policy, mode="strict")
    out, report = t.apply(df)

    assert "email" not in out.columns
    assert "x" in out.columns
    assert any(a.kind == "pii_dropped" for a in report.actions)


def test_pii_mask_email():
    df = pd.DataFrame({"email": ["john@test.com", None]})
    policy = {
        "version": 1,
        "pii": {"rules": [{"column": "email", "action": "mask", "mask_style": "email"}]},
    }

    t = PolicyTransformer(policy=policy, mode="strict")
    out, report = t.apply(df)

    assert out["email"].iloc[0].endswith("@test.com")
    assert out["email"].iloc[0].startswith("j")
    assert any(a.kind == "pii_masked" for a in report.actions)


def test_pii_hash_sha256_with_salt_env(monkeypatch):
    df = pd.DataFrame({"name": ["Alice", "Bob"]})
    monkeypatch.setenv("PII_SALT", "salt123")

    policy = {
        "version": 1,
        "pii": {
            "rules": [
                {"column": "name", "action": "hash", "hash": {"algorithm": "sha256", "salt_env": "PII_SALT"}}
            ]
        },
    }

    t = PolicyTransformer(policy=policy, mode="strict")
    out, report = t.apply(df)

    assert out["name"].iloc[0] != "Alice"
    assert len(out["name"].iloc[0]) == 64
    assert any(a.kind == "pii_hashed" for a in report.actions)


def test_pii_dry_run_no_change():
    df = pd.DataFrame({"email": ["a@test.com"]})
    policy = {"version": 1, "pii": {"rules": [{"column": "email", "action": "drop"}]}}

    t = PolicyTransformer(policy=policy, mode="dry_run")
    out, report = t.apply(df)

    assert out.equals(df)
    assert any(a.kind == "pii_dry_run" for a in report.actions)
