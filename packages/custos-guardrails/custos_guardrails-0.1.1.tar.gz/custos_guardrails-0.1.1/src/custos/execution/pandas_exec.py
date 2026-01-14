from __future__ import annotations

import hashlib
import json
import logging
import os
from typing import Any

import pandas as pd

from custos.enums import JsonArrayHandling, JsonCollision, MaskStyle, OnCastFail, OnConflict, OnMissing, OnQualityFail, PiiAction
from custos.errors import ExecutionError
from custos.execution.base import Executor
from custos.planning.plan import Plan
from custos.planning.steps import CastTypesStep, JsonFlattenStep, PiiStep, QualityRulesStep, RenameColumnsStep
from custos.report.models import Report

log = logging.getLogger(__name__)


class PandasExecutor(Executor):
    engine_name = "pandas"

    def execute(self, df: Any, plan: Plan, mode: str) -> tuple[pd.DataFrame, Report]:
        if not isinstance(df, pd.DataFrame):
            raise ExecutionError("PandasExecutor expects a pandas.DataFrame")

        rows_in = int(df.shape[0])
        cols_in = list(df.columns)

        out = df.copy()

        report = Report(
            engine=self.engine_name,
            mode=mode,
            rows_in=rows_in,
            rows_out=rows_in,
            columns_in=cols_in,
            columns_out=list(out.columns),
        )

        for step in plan.steps:
            if isinstance(step, JsonFlattenStep):
                out = self._json_flatten(out, step, report, mode)
            elif isinstance(step, RenameColumnsStep):
                out = self._rename(out, step, report, mode)
            elif isinstance(step, CastTypesStep):
                out = self._cast_types(out, step, report, mode)
            elif isinstance(step, PiiStep):
                out = self._pii(out, step, report, mode)
            elif isinstance(step, QualityRulesStep):
                out = self._quality(out, step, report, mode)
            else:
                raise ExecutionError(f"Unsupported step type for pandas: {type(step)}")

        report.rows_out = int(out.shape[0])
        report.columns_out = list(out.columns)
        return out, report

    def _rename(
        self,
        df: pd.DataFrame,
        step: RenameColumnsStep,
        report: Report,
        mode: str,
    ) -> pd.DataFrame:
        mapping = step.mapping

        missing = [src for src in mapping.keys() if src not in df.columns]
        if missing:
            msg = f"Missing source columns for rename: {missing}"
            if step.on_missing == OnMissing.ERROR:
                raise ExecutionError(msg)
            if step.on_missing == OnMissing.WARN:
                log.warning(msg)
                report.add("rename_missing_sources", missing=missing)
            else:
                report.add("rename_missing_sources_ignored", missing=missing)

        effective = {src: tgt for src, tgt in mapping.items() if src in df.columns}

        conflicts = []
        for src, tgt in effective.items():
            if tgt in df.columns and tgt != src:
                conflicts.append({"source": src, "target": tgt})

        if conflicts:
            msg = f"Rename conflicts (target already exists): {conflicts}"
            if step.on_conflict == OnConflict.ERROR:
                raise ExecutionError(msg)
            if step.on_conflict == OnConflict.OVERWRITE:
                log.warning(msg + " (overwriting targets)")
                report.add("rename_conflicts_overwrite", conflicts=conflicts)
            else:
                raise ExecutionError(msg)

        if mode == "dry_run":
            report.add("rename_dry_run", mapping=effective)
            return df

        df2 = df.rename(columns=effective)
        report.add("rename_applied", mapping=effective)
        return df2

    def _cast_types(
        self,
        df: pd.DataFrame,
        step: CastTypesStep,
        report: Report,
        mode: str,
    ) -> pd.DataFrame:
        
        if mode == "dry_run":
            missing_cols = [c for c in step.types.keys() if c not in df.columns]
            report.add(
            "cast_dry_run",
            types=step.types,
            on_cast_fail=step.on_cast_fail.value,
            datetime_format=step.datetime_format,
            missing_columns=missing_cols,
            )
            return df



        # Only apply casts for columns that exist
        missing_cols = [c for c in step.types.keys() if c not in df.columns]
        if missing_cols:
            # Casting missing columns is a policy/config issue; fail loudly.
            raise ExecutionError(f"Cast requested for missing columns: {missing_cols}")


        out = df.copy()

        failures: dict[str, dict[str, Any]] = {}
        any_failed_mask = pd.Series(False, index=out.index)

        for col, target in step.types.items():
            s = out[col]
            failed_mask = pd.Series(False, index=out.index)

            # We'll create a candidate converted series; any conversion error becomes NaN/NaT, tracked via mask.
            if target == "string":
                converted = s.astype("string")
                # string conversion rarely "fails"; treat nulls as-is
            elif target == "int":
                numeric = pd.to_numeric(s, errors="coerce")
                failed_mask = numeric.isna() & s.notna()
                converted = numeric.astype("Int64")  # nullable integer
            elif target == "float":
                numeric = pd.to_numeric(s, errors="coerce")
                failed_mask = numeric.isna() & s.notna()
                converted = numeric.astype("Float64")  # nullable float
            elif target == "bool":
                # Conservative bool casting: accept actual bools, or strings like true/false/1/0/yes/no
                converted, failed_mask = self._to_bool_series(s)
            elif target == "datetime":
                converted = pd.to_datetime(s, errors="coerce", format=step.datetime_format)
                failed_mask = converted.isna() & s.notna()
            elif target == "date":
                dt = pd.to_datetime(s, errors="coerce", format=step.datetime_format)
                failed_mask = dt.isna() & s.notna()
                converted = dt.dt.date
            else:
                raise ExecutionError(f"Unsupported cast type in pandas executor: {target}")

            fail_count = int(failed_mask.sum())
            if fail_count > 0:
                any_failed_mask = any_failed_mask | failed_mask
                # capture up to 5 sample bad values
                bad_values = s[failed_mask].head(5).tolist()
                failures[col] = {"type": target, "count": fail_count, "samples": bad_values}

            # Apply based on policy
            if fail_count > 0 and step.on_cast_fail == OnCastFail.SET_NULL:
                # null out bad entries only
                converted = converted.copy()
                converted[failed_mask] = pd.NA

            out[col] = converted

        if failures:
            report.add(
                "cast_failures",
                failures=failures,
                on_cast_fail=step.on_cast_fail.value,
            )

        if failures and step.on_cast_fail == OnCastFail.ERROR:
            raise ExecutionError(f"Cast failures encountered: {failures}")

        if failures and step.on_cast_fail == OnCastFail.DROP_ROW:
            before = int(out.shape[0])
            out = out.loc[~any_failed_mask].copy()
            dropped = before - int(out.shape[0])
            report.add("rows_dropped_due_to_cast", dropped=dropped)

        report.add("cast_applied", types=step.types)
        return out
    
    def _pii(self, df: pd.DataFrame, step: PiiStep, report: Report, mode: str) -> pd.DataFrame:
        rules = list(step.rules)

        missing_cols = [r["column"] for r in rules if r["column"] not in df.columns]
        if missing_cols:
            msg = f"PII rules reference missing columns: {missing_cols}"
            if step.on_missing == OnMissing.ERROR.value:
                raise ExecutionError(msg)
            if step.on_missing == OnMissing.WARN.value:
                log.warning(msg)
                report.add("pii_missing_columns", missing=missing_cols)
            else:
                report.add("pii_missing_columns_ignored", missing=missing_cols)

        # Filter to existing columns only
        rules = [r for r in rules if r["column"] in df.columns]

        if mode == "dry_run":
            report.add("pii_dry_run", rules=rules)
            return df

        out = df.copy()

        dropped, masked, hashed = [], [], []

        for r in rules:
            col = r["column"]
            action = PiiAction(r["action"])

            if action == PiiAction.DROP:
                out = out.drop(columns=[col])
                dropped.append(col)
                continue

            if action == PiiAction.MASK:
                ms = r.get("mask_style") or "fixed"
                ms_enum = MaskStyle(ms)

                out[col] = self._mask_series(out[col], ms_enum)
                masked.append({"column": col, "mask_style": ms_enum.value})
                continue

            if action == PiiAction.HASH:
                h = r.get("hash") or {}
                algo = (h.get("algorithm") or "sha256").lower()
                if algo != "sha256":
                    raise ExecutionError("v1 supports only sha256 hashing.")

                salt_env = h.get("salt_env")
                salt = None
                if salt_env:
                    salt = os.getenv(salt_env)
                    if salt is None:
                        # fail loudly: hashing without salt is allowed, but missing requested salt env is a config error
                        raise ExecutionError(f"PII hash salt env var not set: {salt_env}")

                out[col] = self._hash_series_sha256(out[col], salt=salt)
                hashed.append({"column": col, "salt_env": salt_env})
                continue

            raise ExecutionError(f"Unsupported PII action: {action}")

        if dropped:
            report.add("pii_dropped", columns=dropped)
        if masked:
            report.add("pii_masked", columns=masked)
        if hashed:
            report.add("pii_hashed", columns=hashed)

        report.add("pii_applied", rule_count=len(rules))
        return out

    def _mask_series(self, s: pd.Series, style: MaskStyle) -> pd.Series:
        if style == MaskStyle.FIXED:
            return s.apply(lambda v: "***REDACTED***" if pd.notna(v) else v)

        if style == MaskStyle.EMAIL:
            def mask_email(v):
                if pd.isna(v):
                    return v
                if not isinstance(v, str) or "@" not in v:
                    return "***REDACTED***"
                local, domain = v.split("@", 1)
                if len(local) <= 1:
                    return "*" + "@" + domain
                return local[0] + "***@" + domain

            return s.apply(mask_email)

        if style == MaskStyle.LAST4:
            def last4(v):
                if pd.isna(v):
                    return v
                txt = str(v)
                digits = "".join(ch for ch in txt if ch.isdigit())
                if len(digits) < 4:
                    return "***REDACTED***"
                return "***" + digits[-4:]

            return s.apply(last4)

        raise ExecutionError(f"Unsupported mask style: {style}")

    def _hash_series_sha256(self, s: pd.Series, salt: str | None) -> pd.Series:
        def h(v):
            if pd.isna(v):
                return v
            raw = str(v)
            payload = raw if salt is None else (salt + raw)
            return hashlib.sha256(payload.encode("utf-8")).hexdigest()

        return s.apply(h)


    def _quality(self, df: pd.DataFrame, step: QualityRulesStep, report: Report, mode: str) -> pd.DataFrame:
        # Validate referenced columns exist (in non-dry_run)
        referenced = sorted({r["column"] for r in step.rules})
        missing_cols = [c for c in referenced if c not in df.columns]

        if mode == "dry_run":
            report.add(
                "quality_dry_run",
                rule_count=len(step.rules),
                referenced_columns=referenced,
                missing_columns=missing_cols,
            )
            return df

        if missing_cols:
            raise ExecutionError(f"Quality rules reference missing columns: {missing_cols}")

        # Evaluate rules
        violations: list[dict] = []
        drop_mask = pd.Series(False, index=df.index)

        for idx, r in enumerate(step.rules):
            col = r["column"]
            s = df[col]
            rule_id = r.get("name") or f"{col}#{idx}"

            # Determine rule's on_fail
            on_fail = r.get("on_fail", None) or step.default_on_fail.value
            on_fail_enum = OnQualityFail(on_fail)

            rule_fail_mask = pd.Series(False, index=df.index)

            if r.get("not_null") is True:
                rule_fail_mask = rule_fail_mask | s.isna()

            if r.get("min") is not None:
                # assume numeric-compatible columns; cast already handled earlier
                rule_fail_mask = rule_fail_mask | (s < r["min"])

            if r.get("max") is not None:
                rule_fail_mask = rule_fail_mask | (s > r["max"])

            if r.get("accepted_values") is not None:
                allowed = set(r["accepted_values"])
                rule_fail_mask = rule_fail_mask | (~s.isin(list(allowed)) & s.notna())

            count = int(rule_fail_mask.sum())
            if count > 0:
                samples = df.loc[rule_fail_mask, [col]].head(5).to_dict(orient="records")
                violations.append(
                    {
                        "rule_id": rule_id,
                        "column": col,
                        "count": count,
                        "on_fail": on_fail_enum.value,
                        "checks": {k: v for k, v in r.items() if k not in ("column", "on_fail") and v is not None},
                        "samples": samples,
                    }
                )

                if on_fail_enum == OnQualityFail.ERROR:
                    # fail fast with details
                    report.add("quality_violations", violations=violations)
                    raise ExecutionError(f"Quality rule failed: {violations[-1]}")

                if on_fail_enum == OnQualityFail.DROP_ROW:
                    drop_mask = drop_mask | rule_fail_mask

        if violations:
            report.add("quality_violations", violations=violations)

        if drop_mask.any():
            before = int(df.shape[0])
            out = df.loc[~drop_mask].copy()
            dropped = before - int(out.shape[0])
            report.add("rows_dropped_due_to_quality", dropped=dropped)
        else:
            out = df

        report.add("quality_applied", rule_count=len(step.rules))
        return out

    def _json_flatten(self, df: pd.DataFrame, step: JsonFlattenStep, report: Report, mode: str) -> pd.DataFrame:
        rules = list(step.rules)
        missing_cols = [r["column"] for r in rules if r["column"] not in df.columns]

        if missing_cols:
            msg = f"JSON flatten rules reference missing columns: {missing_cols}"
            if step.on_missing == OnMissing.ERROR.value:
                raise ExecutionError(msg)
            if step.on_missing == OnMissing.WARN.value:
                log.warning(msg)
                report.add("json_flatten_missing_columns", missing=missing_cols)
            else:
                report.add("json_flatten_missing_columns_ignored", missing=missing_cols)

        rules = [r for r in rules if r["column"] in df.columns]

        if mode == "dry_run":
            report.add("json_flatten_dry_run", rules=rules)
            return df

        out = df.copy()

        for r in rules:
            col = r["column"]
            prefix = r.get("prefix")
            sep = r.get("separator", ".")
            max_depth = int(r.get("max_depth", 2))
            arrays = JsonArrayHandling(r.get("arrays", "stringify"))
            collision = JsonCollision(r.get("collision", "error"))
            drop_source = bool(r.get("drop_source", False))

            records = []
            for v in out[col].tolist():
                if pd.isna(v):
                    records.append({})
                    continue
                if isinstance(v, dict):
                    records.append(v)
                    continue
                if isinstance(v, str):
                    try:
                        parsed = json.loads(v)
                    except Exception:
                        parsed = v
                    if isinstance(parsed, dict):
                        records.append(parsed)
                    elif isinstance(parsed, list):
                        # arrays in the root
                        records.append({"_array": parsed})
                    else:
                        records.append({"_value": parsed})
                    continue
                if isinstance(v, list):
                    records.append({"_array": v})
                    continue
                records.append({"_value": v})

            # Normalize nested dicts
            norm = pd.json_normalize(records, sep=sep, max_level=max_depth if max_depth >= 0 else None)

            # Handle arrays: stringify any list values inside normalized frame
            if arrays == JsonArrayHandling.STRINGIFY:
                for c in norm.columns:
                    norm[c] = norm[c].apply(lambda x: json.dumps(x) if isinstance(x, list) else x)

            # Apply prefix
            if prefix:
                norm.columns = [f"{prefix}{sep}{c}" for c in norm.columns]

            # Merge into out with collision handling
            new_cols = []
            for c in norm.columns:
                target = c
                if target in out.columns:
                    if collision == JsonCollision.ERROR:
                        raise ExecutionError(f"JSON flatten column collision: '{target}' already exists")
                    if collision == JsonCollision.OVERWRITE:
                        pass
                    if collision == JsonCollision.SUFFIX:
                        base = target
                        k = 1
                        while target in out.columns:
                            target = f"{base}_{k}"
                            k += 1
                out[target] = norm[c].values
                new_cols.append(target)

            if drop_source:
                out = out.drop(columns=[col])

            report.add(
                "json_flatten_applied",
                column=col,
                created_columns=new_cols,
                drop_source=drop_source,
                max_depth=max_depth,
                separator=sep,
                arrays=arrays.value,
                collision=collision.value,
            )

        return out
  

    def _to_bool_series(self, s: pd.Series) -> tuple[pd.Series, pd.Series]:
        """
        Conservative boolean conversion.
        Accepts booleans, 1/0, and strings: true/false/yes/no/y/n/t/f.
        Everything else fails.
        """
        failed = pd.Series(False, index=s.index)

        # Start with NA
        out = pd.Series(pd.NA, index=s.index, dtype="boolean")

        # Already bool
        is_bool = s.apply(lambda x: isinstance(x, bool))
        out[is_bool] = s[is_bool].astype("boolean")

        # Numeric 1/0
        is_num = s.apply(lambda x: isinstance(x, (int, float)) and not isinstance(x, bool))
        num = pd.to_numeric(s[is_num], errors="coerce")
        ok_num = num.isin([0, 1])
        out.loc[num.index[ok_num]] = num[ok_num].astype(int).astype("boolean")
        failed.loc[num.index[~ok_num & num.notna()]] = True

        # Strings
        is_str = s.apply(lambda x: isinstance(x, str))
        if is_str.any():
            lowered = s[is_str].str.strip().str.lower()
            true_set = {"true", "t", "yes", "y", "1"}
            false_set = {"false", "f", "no", "n", "0"}
            is_true = lowered.isin(list(true_set))
            is_false = lowered.isin(list(false_set))
            out.loc[lowered.index[is_true]] = True
            out.loc[lowered.index[is_false]] = False
            failed.loc[lowered.index[~(is_true | is_false) & lowered.notna()]] = True

        # Anything non-null that still NA is a failure (e.g., objects)
        failed = failed | (out.isna() & s.notna())
        return out, failed
