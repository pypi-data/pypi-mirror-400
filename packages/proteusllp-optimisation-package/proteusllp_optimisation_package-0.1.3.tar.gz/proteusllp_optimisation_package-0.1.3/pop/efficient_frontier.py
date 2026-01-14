"""Efficient Frontier Generation.

This module provides functionality to generate efficient frontiers by varying
constraint thresholds in parallel across multiple optimization runs.
"""

import numpy as np

from .models import EfficientFrontierInput, EfficientFrontierResult
from .scipy_interface import optimize


def generate_efficient_frontier(
    frontier_input: EfficientFrontierInput,
) -> EfficientFrontierResult:
    """Generate efficient frontier by varying constraints in parallel.

    This function creates a series of optimization problems by varying the thresholds
    of specified constraints in parallel. For each point on the frontier, all varied
    constraints are updated together, and a new optimization is performed.

    Args:
        frontier_input: Specification of constraints to vary and base optimization.
                       Contains the base optimization problem, list of constraints
                       to vary, and number of frontier points to generate.

    Returns:
        EfficientFrontierResult containing a list of OptimizationResult objects,
        one for each point on the frontier.

    Example:
        >>> from pop import (
        ...     EfficientFrontierInput, ConstraintVariation,
        ...     OptimizationInput, SimpleConstraint
        ... )
        >>> frontier_input = EfficientFrontierInput(
        ...     base_optimization=my_optimization,
        ...     constraint_variations=[
        ...         ConstraintVariation(
        ...             constraint_type="simple",
        ...             constraint_name="max_loss",
        ...             min_threshold=10.0,
        ...             max_threshold=20.0
        ...         ),
        ...     ],
        ...     n_points=11
        ... )
        >>> result = generate_efficient_frontier(frontier_input)
        >>> print(f"Generated {result.n_successful} successful optimizations")
    """
    # Preprocess base optimization once (validates and aligns all data)
    preprocessed_base = frontier_input.base_optimization.preprocess()

    # Generate threshold values for each constraint using numpy's linspace
    thresholds_by_constraint = []
    for variation in frontier_input.constraint_variations:
        thresholds = np.linspace(
            variation.min_threshold, variation.max_threshold, frontier_input.n_points
        )
        thresholds_by_constraint.append(thresholds)

    # Run optimization for each frontier point
    results = []
    for i in range(frontier_input.n_points):
        # Create modified optimization input with updated constraint thresholds
        # Start from preprocessed base to preserve all preprocessing
        modified_opt = preprocessed_base.model_copy(deep=True)

        # Update each varied constraint's threshold
        for variation, thresholds in zip(
            frontier_input.constraint_variations,
            thresholds_by_constraint,
            strict=True,
        ):
            new_threshold = thresholds[i]

            # Find and update the constraint
            if variation.constraint_type == "simple":
                constraints = modified_opt.simple_constraints
            else:  # "freqsev"
                constraints = modified_opt.freqsev_constraints  # type: ignore

            # Find constraint by name and update threshold
            for j, constraint in enumerate(constraints):
                if constraint.name == variation.constraint_name:
                    # Create new constraint with updated threshold
                    updated_constraint = constraint.model_copy(
                        update={"threshold": new_threshold}
                    )
                    constraints[j] = updated_constraint
                    break

        # Run optimization with modified constraints (already preprocessed)
        result = optimize(modified_opt)
        results.append(result)

    return EfficientFrontierResult(optimization_results=results)
