from __future__ import annotations

from custos.planning.plan import Plan
from custos.planning.steps import CastTypesStep, JsonFlattenStep, PiiStep, QualityRulesStep, RenameColumnsStep
from custos.policy.model import Policy


class Planner:
    def __init__(self, policy: Policy):
        self.policy = policy

    def build(self) -> Plan:
        steps = []

        # 0) json flatten first
        jf = self.policy.schema.json_flatten
        if jf.rules:
            steps.append(
                JsonFlattenStep(
                    rules=tuple(
                        {
                            "column": r.column,
                            "prefix": r.prefix,
                            "separator": r.separator,
                            "max_depth": r.max_depth,
                            "arrays": r.arrays.value,
                            "collision": r.collision.value,
                            "drop_source": r.drop_source,
                        }
                        for r in jf.rules
                    ),
                    on_missing=jf.on_missing.value,
                )
            )

        # 1) rename first
        if self.policy.schema.rename:
            steps.append(
                RenameColumnsStep(
                    mapping=self.policy.schema.rename,
                    on_missing=self.policy.schema.on_missing,
                    on_conflict=self.policy.schema.on_conflict,
                )
            )

        # 2) then cast
        if self.policy.schema.types:
            steps.append(
                CastTypesStep(
                    types=self.policy.schema.types,
                    on_cast_fail=self.policy.schema.cast.on_cast_fail,
                    datetime_format=self.policy.schema.cast.datetime_format,
                )
            )
  # 3) pii
        pp = self.policy.schema.pii
        if pp.rules:
            steps.append(
                PiiStep(
                    rules=tuple(
                        {
                            "column": r.column,
                            "action": r.action.value,
                            "mask_style": (r.mask_style.value if r.mask_style else None),
                            "hash": (
                                {"algorithm": r.hash.algorithm, "salt_env": r.hash.salt_env}
                                if r.hash else None
                            ),
                        }
                        for r in pp.rules
                    ),
                    on_missing=pp.on_missing.value,
                )
            )
        # 4) then quality
        qp = self.policy.schema.quality
        if qp.rules:
            steps.append(
                QualityRulesStep(
                    rules=tuple(
                        {
                            "name": r.name,
                            "column": r.column,
                            "not_null": r.not_null,
                            "min": r.min,
                            "max": r.max,
                            "accepted_values": r.accepted_values,
                            "on_fail": r.on_fail.value,
                        }
                        for r in qp.rules
                    ),
                    default_on_fail=qp.default_on_fail,
                )
            )

        return Plan(steps=tuple(steps))
