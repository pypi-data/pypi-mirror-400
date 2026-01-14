from __future__ import annotations
from typing import Any

from custos.enums import Mode
from custos.execution.base import DEFAULT_ENGINE, get_executor, register_executor
from custos.execution.pandas_exec import PandasExecutor
from custos.planning.planner import Planner
from custos.policy.loader import load_policy
from custos.report.models import Report


# Register default executor(s) on import
register_executor(PandasExecutor())


class PolicyTransformer:
    def __init__(
        self,
        policy: Any,
        mode: str | Mode = Mode.STRICT,
        engine: str = DEFAULT_ENGINE,
    ):
        self.policy = load_policy(policy)
        self.mode = Mode(mode) if not isinstance(mode, Mode) else mode
        self.engine = engine

        self._planner = Planner(self.policy)

    def plan(self):
        return self._planner.build()

    def apply(self, df: Any) -> tuple[Any, Report]:
        plan = self.plan()
        executor = get_executor(self.engine)
        return executor.execute(df, plan, mode=self.mode.value)
