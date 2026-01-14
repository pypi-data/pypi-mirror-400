from __future__ import annotations
from pathlib import Path
from typing import Any, Mapping, Union

import yaml

from custos.errors import PolicyError
from custos.policy.model import Policy, policy_from_dict


PolicyInput = Union[str, Path, Mapping[str, Any]]


def load_policy(policy: PolicyInput) -> Policy:
    if isinstance(policy, (str, Path)):
        path = Path(policy)
        if not path.exists():
            raise PolicyError(f"Policy file not found: {path}")
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as e:
            raise PolicyError(f"Failed to read policy YAML: {e}") from e
        if raw is None:
            raw = {}
        return policy_from_dict(raw)

    if isinstance(policy, Mapping):
        return policy_from_dict(policy)

    raise PolicyError("Policy must be a file path (str/Path) or a dict-like mapping.")
