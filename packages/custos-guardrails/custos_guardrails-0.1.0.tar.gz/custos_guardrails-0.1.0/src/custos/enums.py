from __future__ import annotations
from enum import Enum


class Mode(str, Enum):
    STRICT = "strict"
    DROP = "drop"
    DRY_RUN = "dry_run"


class OnMissing(str, Enum):
    ERROR = "error"
    WARN = "warn"
    IGNORE = "ignore"


class OnConflict(str, Enum):
    ERROR = "error"
    OVERWRITE = "overwrite"

class OnCastFail(str, Enum):
    ERROR = "error"
    DROP_ROW = "drop_row"
    SET_NULL = "set_null"

class OnQualityFail(str, Enum):
    ERROR = "error"
    DROP_ROW = "drop_row"

class PiiAction(str, Enum):
    DROP = "drop"
    MASK = "mask"
    HASH = "hash"


class MaskStyle(str, Enum):
    EMAIL = "email"
    FIXED = "fixed"
    LAST4 = "last4"

class JsonArrayHandling(str, Enum):
    STRINGIFY = "stringify"
    KEEP = "keep"


class JsonCollision(str, Enum):
    ERROR = "error"
    OVERWRITE = "overwrite"
    SUFFIX = "suffix"
