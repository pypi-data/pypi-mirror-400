"""Generic Optimization API using PAL (Proteus Analytics Library).

This package provides a domain-agnostic optimization framework that can work
with any PAL variables and metrics, making it suitable for portfolio optimization,
risk analysis, and other stochastic optimization problems.

Key Components:
- ObjectiveSpec: Define what to optimize using PAL ProteusVariable
- SimpleConstraint: Define portfolio-level constraints
  (auto-converts FreqSevSims → aggregate)
- FreqSevConstraint: Define OEP-based constraints preserving
  frequency-severity structure (operates on max event loss per
  simulation, not aggregate)
- OptimizationInput: Complete optimization problem specification
- OptimizationResult: Comprehensive optimization results
- EfficientFrontierInput: Specify constraint variations for
  efficient frontier generation
- EfficientFrontierResult: Collection of optimization results
  across constraint variations
- Configuration: Optimization settings and constants

Main Functions:
- optimize(): Single-point optimization for given objective and
  constraints
- generate_efficient_frontier(): Multi-point optimization by varying
  constraint thresholds

Available Metrics:
- MeanMetric: Expected value (use for return objectives, loss constraints)
- StdMetric: Standard deviation (use for volatility/risk objectives)
- SpreadVarMetric: Mean of percentile range (use for tail risk analysis)
- RatioMetric, ProductMetric, SumMetric, DifferenceMetric: Composite metrics
  (e.g., Sharpe ratio = RatioMetric(MeanMetric(), StdMetric()))

Example Usage:
    from pop import (
        ObjectiveSpec, OptimizationInput, MeanMetric, optimize
    )
    from pal.variables import ProteusVariable
    from pal import StochasticScalar

    # Create objective using PAL ProteusVariable
    # Note: Use "item" as dimension name consistently across all ProteusVariables
    # in your optimization problem (objectives, constraints, etc.)
    proteus_var = ProteusVariable("item", {
        "item1": StochasticScalar([1.0, 1.1, 0.9]),  # Return simulations
        "item2": StochasticScalar([2.0, 2.2, 1.8])
    })

    objective = ObjectiveSpec(
        objective_value=proteus_var,
        metric=MeanMetric(),
        direction="maximize"
    )

    # Create and run optimization (current_shares required)
    input_spec = OptimizationInput(
        item_ids=["item1", "item2"],
        # Required: current allocations
        current_shares={"item1": 100.0, "item2": 200.0},
        objective=objective
    )

    # Preprocess and optimize
    preprocessed = input_spec.preprocess()
    result = optimize(preprocessed)
"""

# Import all Pydantic models for external use
# Import configuration
from .config import (
    DEFAULT_TOLERANCES,
    MAX_ITERATIONS,
    STATUS_DESCRIPTIONS,
    VALID_CONSTRAINT_DIRECTIONS,
    VALID_DIRECTIONS,
    ConstraintDirection,
    OptimizationDirection,
    OptimizationStatus,
)

# Import efficient frontier function
from .efficient_frontier import generate_efficient_frontier
from .models import (
    BoundsSpec,
    ConstraintResult,
    ConstraintVariation,
    DifferenceMetric,
    EfficientFrontierInput,
    EfficientFrontierResult,
    FreqSevConstraint,
    MeanMetric,
    ObjectiveSpec,
    OptimizationInput,
    OptimizationResult,
    ProductMetric,
    RatioMetric,
    SimpleConstraint,
    SpreadVarMetric,
    StdMetric,
    SumMetric,
)

# Import main optimization function
from .scipy_interface import optimize

# Import transform functions for advanced users
from .transforms import create_metric_calculator

# Version info
__version__ = "1.0.0"
__phase__ = "v1.0 - Production Ready"

# Public API
__all__ = [
    # Core Models
    "ObjectiveSpec",
    "SimpleConstraint",
    "FreqSevConstraint",
    "OptimizationInput",
    "OptimizationResult",
    "ConstraintResult",
    "BoundsSpec",
    # Efficient Frontier Models
    "ConstraintVariation",
    "EfficientFrontierInput",
    "EfficientFrontierResult",
    # Metric Models
    "MeanMetric",
    "StdMetric",
    "SpreadVarMetric",
    "RatioMetric",
    "ProductMetric",
    "SumMetric",
    "DifferenceMetric",
    # Main Functions
    "optimize",
    "generate_efficient_frontier",
    # Advanced Functions
    "create_metric_calculator",
    # Configuration
    "OptimizationDirection",
    "ConstraintDirection",
    "OptimizationStatus",
    "MAX_ITERATIONS",
    "VALID_DIRECTIONS",
    "VALID_CONSTRAINT_DIRECTIONS",
    "DEFAULT_TOLERANCES",
    "STATUS_DESCRIPTIONS",
    # Metadata
    "__version__",
    "__phase__",
]
