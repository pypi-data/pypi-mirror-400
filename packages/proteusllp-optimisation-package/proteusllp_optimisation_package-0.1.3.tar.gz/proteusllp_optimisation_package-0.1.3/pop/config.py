"""Configuration constants and settings for the generic optimization API.

This module defines the foundational constants, valid values, and configuration
options that govern the behavior of the optimization system.
"""

from enum import Enum
from typing import Any


class OptimizationDirection(Enum):
    """Direction of optimization for objective functions."""

    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"


class ConstraintDirection(Enum):
    """Direction of constraint evaluation."""

    CAP = "cap"  # Upper bound constraint (≤)
    FLOOR = "floor"  # Lower bound constraint (≥)


class OptimizationStatus(Enum):
    """Optimization result status codes based on scipy.optimize."""

    SUCCESS = 0
    MAX_ITERATIONS = 1
    XTOL_REACHED = 2
    FTOL_REACHED = 3
    GTOL_REACHED = 4
    USER_REQUESTED = 9


# Maximum number of iterations allowed
MAX_ITERATIONS: int = 1000

# Valid optimization directions
VALID_DIRECTIONS: set[str] = {direction.value for direction in OptimizationDirection}

# Valid constraint directions
VALID_CONSTRAINT_DIRECTIONS: set[str] = {
    direction.value for direction in ConstraintDirection
}

# Default tolerance values for scipy optimization
DEFAULT_TOLERANCES: dict[str, float] = {
    "ftol": 1e-8,  # Relative tolerance on function values
}

# Valid percentile range for spread VaR calculations
VALID_PERCENTILE_RANGE: tuple[float, float] = (0.0, 100.0)

# Note: Spread VaR requires both lower and upper percentile parameters
# Example: metric="spread_var", spread_var_lower=5.0, spread_var_upper=10.0

# Status code descriptions for user feedback
STATUS_DESCRIPTIONS: dict[int, str] = {
    OptimizationStatus.SUCCESS.value: "Optimization terminated successfully",
    OptimizationStatus.MAX_ITERATIONS.value: "Maximum number of iterations reached",
    OptimizationStatus.XTOL_REACHED.value: "Tolerance in decision variables reached",
    OptimizationStatus.FTOL_REACHED.value: "Tolerance in function values reached",
    OptimizationStatus.GTOL_REACHED.value: "Tolerance in gradient norm reached",
    OptimizationStatus.USER_REQUESTED.value: "User requested termination",
}

# Default configuration values
DEFAULT_CONFIG: dict[str, Any] = {
    "max_iterations": MAX_ITERATIONS,
    "tolerances": DEFAULT_TOLERANCES,
    "verbose": False,
    "autoscale": True,
}
