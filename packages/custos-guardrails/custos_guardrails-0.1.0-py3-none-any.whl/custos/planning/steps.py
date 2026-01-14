from __future__ import annotations
from dataclasses import dataclass

from custos.enums import OnCastFail, OnConflict, OnMissing, OnQualityFail


@dataclass(frozen=True)
class RenameColumnsStep:
    mapping: dict[str, str]              # old_name -> new_name
    on_missing: OnMissing
    on_conflict: OnConflict

@dataclass(frozen=True)
class CastTypesStep:
    types: dict[str, str]                 # column -> type string (engine-agnostic)
    on_cast_fail: OnCastFail
    datetime_format: str | None = None

@dataclass(frozen=True)
class QualityRulesStep:
    rules: tuple[dict, ...]               # keep engine-agnostic (plain dicts)
    default_on_fail: OnQualityFail   

@dataclass(frozen=True)
class PiiStep:
    rules: tuple[dict, ...]   # dicts keep it engine-agnostic + serializable
    on_missing: str

@dataclass(frozen=True)
class JsonFlattenStep:
    rules: tuple[dict, ...]   # engine-agnostic dicts
    on_missing: str