class CustosError(Exception):
    """Base exception for Custos."""


class PolicyError(CustosError):
    """Raised when a policy is invalid."""


class PlanningError(CustosError):
    """Raised when planning a transformation fails."""


class ExecutionError(CustosError):
    """Raised when applying a plan to data fails."""
