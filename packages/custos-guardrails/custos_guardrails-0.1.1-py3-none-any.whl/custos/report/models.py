from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ActionEvent:
    kind: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class Report:
    engine: str
    mode: str
    rows_in: int
    rows_out: int
    columns_in: list[str]
    columns_out: list[str]
    actions: list[ActionEvent] = field(default_factory=list)

    def add(self, kind: str, **details: Any) -> None:
        self.actions.append(ActionEvent(kind=kind, details=details))
