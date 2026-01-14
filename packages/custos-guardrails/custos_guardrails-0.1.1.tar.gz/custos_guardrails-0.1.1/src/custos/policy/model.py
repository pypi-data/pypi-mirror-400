from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Mapping

from custos.enums import JsonArrayHandling, JsonCollision, MaskStyle, OnCastFail, OnConflict, OnMissing, OnQualityFail, PiiAction
from custos.errors import PolicyError


@dataclass(frozen=True)
class CastPolicy:
    on_cast_fail: OnCastFail = OnCastFail.ERROR
    datetime_format: str | None = None

@dataclass(frozen=True)
class QualityRule:
    column: str
    name: str | None = None
    not_null: bool | None = None
    min: float | int | None = None
    max: float | int | None = None
    accepted_values: list[str] | list[int] | list[float] | None = None
    on_fail: OnQualityFail = OnQualityFail.DROP_ROW


@dataclass(frozen=True)
class QualityPolicy:
    rules: tuple[QualityRule, ...] = ()
    default_on_fail: OnQualityFail = OnQualityFail.DROP_ROW

@dataclass(frozen=True)
class HashPolicy:
    algorithm: str = "sha256"
    salt_env: str | None = None


@dataclass(frozen=True)
class PiiRule:
    column: str
    action: PiiAction
    mask_style: MaskStyle | None = None
    hash: HashPolicy | None = None


@dataclass(frozen=True)
class PiiPolicy:
    rules: tuple[PiiRule, ...] = ()
    on_missing: OnMissing = OnMissing.WARN   

@dataclass(frozen=True)
class JsonFlattenRule:
    column: str
    prefix: str | None = None
    separator: str = "."
    max_depth: int = 2
    arrays: JsonArrayHandling = JsonArrayHandling.STRINGIFY
    collision: JsonCollision = JsonCollision.ERROR
    drop_source: bool = False


@dataclass(frozen=True)
class JsonFlattenPolicy:
    rules: tuple[JsonFlattenRule, ...] = ()
    on_missing: OnMissing = OnMissing.WARN

@dataclass(frozen=True)
class SchemaPolicy:
    rename: dict[str, str] = field(default_factory=dict)
    types: dict[str, str] = field(default_factory=dict)  # e.g. {"order_id": "int"}
    cast: CastPolicy = field(default_factory=CastPolicy)
    quality: QualityPolicy = field(default_factory=QualityPolicy)
    pii: PiiPolicy = field(default_factory=PiiPolicy)
    json_flatten: JsonFlattenPolicy = field(default_factory=JsonFlattenPolicy)
    on_missing: OnMissing = OnMissing.WARN
    on_conflict: OnConflict = OnConflict.ERROR


@dataclass(frozen=True)
class Policy:
    version: int = 1
    schema: SchemaPolicy = field(default_factory=SchemaPolicy)


_ALLOWED_TYPES = {"int", "float", "string", "bool", "datetime", "date"}


def policy_from_dict(raw: Mapping[str, Any]) -> Policy:
    if not isinstance(raw, Mapping):
        raise PolicyError("Policy must be a mapping (dict-like).")

    version = raw.get("version", 1)
    if version != 1:
        raise PolicyError(f"Unsupported policy version: {version}")

    schema_raw = raw.get("schema", {}) or {}
    if not isinstance(schema_raw, Mapping):
        raise PolicyError("`schema` must be a mapping.")

    # --- rename ---
    rename_raw = schema_raw.get("rename", {}) or {}
    if not isinstance(rename_raw, Mapping):
        raise PolicyError("`schema.rename` must be a mapping of source->target.")

    rename: dict[str, str] = {}
    for k, v in rename_raw.items():
        if not isinstance(k, str) or not isinstance(v, str):
            raise PolicyError("`schema.rename` must map string keys to string values.")
        if not k.strip() or not v.strip():
            raise PolicyError("`schema.rename` keys/values cannot be empty.")
        rename[k] = v

    # --- types ---
    types_raw = schema_raw.get("types", {}) or {}
    if not isinstance(types_raw, Mapping):
        raise PolicyError("`schema.types` must be a mapping of column->type.")

    types: dict[str, str] = {}
    for col, typ in types_raw.items():
        if not isinstance(col, str) or not isinstance(typ, str):
            raise PolicyError("`schema.types` must map string column names to string type names.")
        t = typ.strip().lower()
        if t not in _ALLOWED_TYPES:
            raise PolicyError(f"Unsupported type '{typ}' for column '{col}'. Allowed: {sorted(_ALLOWED_TYPES)}")
        types[col] = t

    # --- behaviors ---
    on_missing = OnMissing(schema_raw.get("on_missing", OnMissing.WARN))
    on_conflict = OnConflict(schema_raw.get("on_conflict", OnConflict.ERROR))

    cast_raw = schema_raw.get("cast", {}) or {}
    if not isinstance(cast_raw, Mapping):
        raise PolicyError("`schema.cast` must be a mapping.")

    on_cast_fail = OnCastFail(cast_raw.get("on_cast_fail", OnCastFail.ERROR))
    datetime_format = cast_raw.get("datetime_format", None)
    if datetime_format is not None and not isinstance(datetime_format, str):
        raise PolicyError("`schema.cast.datetime_format` must be a string or null.")
    
    # --- quality ---
    quality_raw = raw.get("quality", {}) or {}
    if not isinstance(quality_raw, Mapping):
        raise PolicyError("`quality` must be a mapping.")

    default_on_fail = OnQualityFail(quality_raw.get("default_on_fail", OnQualityFail.DROP_ROW))

    rules_raw = quality_raw.get("rules", []) or []
    if not isinstance(rules_raw, list):
        raise PolicyError("`quality.rules` must be a list.")

    parsed_rules: list[QualityRule] = []
    for i, rr in enumerate(rules_raw):
        if not isinstance(rr, Mapping):
            raise PolicyError(f"`quality.rules[{i}]` must be a mapping.")
        
        name = rr.get("name")
        if name is not None and not isinstance(name, str):
           raise PolicyError(f"`quality.rules[{i}].name` must be a string or null.")
        
        col = rr.get("column")
        if not isinstance(col, str) or not col.strip():
            raise PolicyError(f"`quality.rules[{i}].column` must be a non-empty string.")

        on_fail = OnQualityFail(rr.get("on_fail", default_on_fail))

        not_null = rr.get("not_null", None)
        if not_null is not None and not isinstance(not_null, bool):
            raise PolicyError(f"`quality.rules[{i}].not_null` must be boolean or null.")

        min_v = rr.get("min", None)
        max_v = rr.get("max", None)
        if min_v is not None and not isinstance(min_v, (int, float)):
            raise PolicyError(f"`quality.rules[{i}].min` must be a number or null.")
        if max_v is not None and not isinstance(max_v, (int, float)):
            raise PolicyError(f"`quality.rules[{i}].max` must be a number or null.")

        accepted = rr.get("accepted_values", None)
        if accepted is not None and not isinstance(accepted, list):
            raise PolicyError(f"`quality.rules[{i}].accepted_values` must be a list or null.")

        # Require at least one constraint per rule
        if not any([not_null is not None, min_v is not None, max_v is not None, accepted is not None]):
            raise PolicyError(f"`quality.rules[{i}]` must specify at least one check (not_null/min/max/accepted_values).")

        parsed_rules.append(
            QualityRule(
                name=name,
                column=col,
                not_null=not_null,
                min=min_v,
                max=max_v,
                accepted_values=accepted,
                on_fail=on_fail,
            )
        )

    quality_policy = QualityPolicy(rules=tuple(parsed_rules), default_on_fail=default_on_fail)

    # --- pii ---
    pii_raw = raw.get("pii", {}) or {}
    if not isinstance(pii_raw, Mapping):
        raise PolicyError("`pii` must be a mapping.")

    pii_on_missing = OnMissing(pii_raw.get("on_missing", OnMissing.WARN))

    pii_rules_raw = pii_raw.get("rules", []) or []
    if not isinstance(pii_rules_raw, list):
        raise PolicyError("`pii.rules` must be a list.")

    pii_rules: list[PiiRule] = []
    for i, rr in enumerate(pii_rules_raw):
        if not isinstance(rr, Mapping):
            raise PolicyError(f"`pii.rules[{i}]` must be a mapping.")

        col = rr.get("column")
        if not isinstance(col, str) or not col.strip():
            raise PolicyError(f"`pii.rules[{i}].column` must be a non-empty string.")

        action = rr.get("action")
        if not isinstance(action, str):
            raise PolicyError(f"`pii.rules[{i}].action` must be a string (drop/mask/hash).")

        action_enum = PiiAction(action.strip().lower())

        mask_style = None
        hash_policy = None

        if action_enum == PiiAction.MASK:
            ms = rr.get("mask_style", "fixed")
            if not isinstance(ms, str):
                raise PolicyError(f"`pii.rules[{i}].mask_style` must be a string.")
            mask_style = MaskStyle(ms.strip().lower())

        if action_enum == PiiAction.HASH:
            h = rr.get("hash", {}) or {}
            if not isinstance(h, Mapping):
                raise PolicyError(f"`pii.rules[{i}].hash` must be a mapping.")
            algo = h.get("algorithm", "sha256")
            if not isinstance(algo, str) or algo.strip().lower() != "sha256":
                raise PolicyError("v1 supports only sha256 hashing.")
            salt_env = h.get("salt_env", None)
            if salt_env is not None and not isinstance(salt_env, str):
                raise PolicyError(f"`pii.rules[{i}].hash.salt_env` must be a string or null.")
            hash_policy = HashPolicy(algorithm="sha256", salt_env=salt_env)

        pii_rules.append(
            PiiRule(
                column=col,
                action=action_enum,
                mask_style=mask_style,
                hash=hash_policy,
            )
        )

    pii_policy = PiiPolicy(rules=tuple(pii_rules), on_missing=pii_on_missing)

    # --- json_flatten ---
    jf_raw = raw.get("json_flatten", {}) or {}
    if not isinstance(jf_raw, Mapping):
        raise PolicyError("`json_flatten` must be a mapping.")

    jf_on_missing = OnMissing(jf_raw.get("on_missing", OnMissing.WARN))

    rules_raw = jf_raw.get("rules", []) or []
    if not isinstance(rules_raw, list):
        raise PolicyError("`json_flatten.rules` must be a list.")

    jf_rules: list[JsonFlattenRule] = []
    for i, rr in enumerate(rules_raw):
        if not isinstance(rr, Mapping):
            raise PolicyError(f"`json_flatten.rules[{i}]` must be a mapping.")

        col = rr.get("column")
        if not isinstance(col, str) or not col.strip():
            raise PolicyError(f"`json_flatten.rules[{i}].column` must be a non-empty string.")

        prefix = rr.get("prefix", None)
        if prefix is not None and not isinstance(prefix, str):
            raise PolicyError(f"`json_flatten.rules[{i}].prefix` must be a string or null.")

        sep = rr.get("separator", ".")
        if not isinstance(sep, str) or not sep:
            raise PolicyError(f"`json_flatten.rules[{i}].separator` must be a non-empty string.")

        max_depth = rr.get("max_depth", 2)
        if not isinstance(max_depth, int) or max_depth < 0:
            raise PolicyError(f"`json_flatten.rules[{i}].max_depth` must be an int >= 0.")

        arrays = JsonArrayHandling(str(rr.get("arrays", "stringify")).lower())
        collision = JsonCollision(str(rr.get("collision", "error")).lower())

        drop_source = rr.get("drop_source", False)
        if not isinstance(drop_source, bool):
            raise PolicyError(f"`json_flatten.rules[{i}].drop_source` must be boolean.")

        jf_rules.append(
            JsonFlattenRule(
                column=col,
                prefix=prefix,
                separator=sep,
                max_depth=max_depth,
                arrays=arrays,
                collision=collision,
                drop_source=drop_source,
            )
        )

    json_flatten_policy = JsonFlattenPolicy(rules=tuple(jf_rules), on_missing=jf_on_missing)



    return Policy(
        version=version,
        schema=SchemaPolicy(
            rename=rename,
            types=types,
            cast=CastPolicy(on_cast_fail=on_cast_fail, datetime_format=datetime_format),
            quality=quality_policy,
            pii=pii_policy,
            json_flatten=json_flatten_policy,
            on_missing=on_missing,
            on_conflict=on_conflict,
        ),
    )
