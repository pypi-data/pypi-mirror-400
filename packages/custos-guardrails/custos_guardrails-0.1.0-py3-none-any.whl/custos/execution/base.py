from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

from custos.errors import ExecutionError
from custos.planning.plan import Plan
from custos.report.models import Report

DEFAULT_ENGINE = "pandas"


class Executor(ABC):
    engine_name: str

    @abstractmethod
    def execute(self, df: Any, plan: Plan, mode: str) -> tuple[Any, Report]:
        raise NotImplementedError


_EXECUTORS: dict[str, Executor] = {}


def register_executor(executor: Executor) -> None:
    _EXECUTORS[executor.engine_name] = executor


def get_executor(engine: str) -> Executor:
    try:
        return _EXECUTORS[engine]
    except KeyError as e:
        raise ExecutionError(f"Unsupported engine: {engine}") from e
