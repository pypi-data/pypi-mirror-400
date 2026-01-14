"""Scipy optimization interface for the portfolio optimizer.

This module provides the main optimization entry point that orchestrates
the transformation from Pydantic models to scipy.optimize.minimize() and
back to optimization results.

Key Functions:
- optimize(): Main optimization orchestrator
- get_initial_guess(): Generate starting points for optimization
- bounds_to_scipy_bounds(): Convert BoundsSpec to scipy format
- process_scipy_result(): Transform scipy results back to Pydantic models
"""

import time

import numpy as np
from scipy.optimize import OptimizeResult, minimize  # type: ignore

from .config import DEFAULT_CONFIG, DEFAULT_TOLERANCES, MAX_ITERATIONS
from .models import BoundsSpec, ConstraintResult, OptimizationInput, OptimizationResult
from .transforms import constraint_wrapper, create_metric_calculator, objective_wrapper


def optimize(optimization_input: OptimizationInput) -> OptimizationResult:
    """Main optimization entry point.

    Transforms OptimizationInput (Pydantic) → scipy.optimize.minimize()
    → OptimizationResult

    Args:
        optimization_input: Complete optimization problem specification

    Returns:
        OptimizationResult with optimal solution and constraint evaluations

    Raises:
        ValueError: If optimization_input is not ready for optimization

    Flow:
        1. Validate input readiness
        2. Transform objective → scipy objective function + gradient
        3. Transform constraints → scipy constraint dicts
        4. Transform bounds → scipy bounds array
        5. Generate initial guess
        6. Call scipy.optimize.minimize()
        7. Evaluate constraints at optimal solution
        8. Build and return OptimizationResult
    """
    start_time = time.time()

    try:
        # Step 1: Validate input readiness
        if not optimization_input.is_preprocessed:
            raise ValueError(
                "OptimizationInput is not ready for optimization. "
                "Please call preprocess() first."
            )

        # Get config early to use verbose flag
        config = optimization_input.config or DEFAULT_CONFIG
        verbose = config.get("verbose", False)

        # Step 2: Transform objective to scipy functions
        obj_value_func, obj_grad_func = create_metric_calculator(
            optimization_input.objective.metric,
            optimization_input.objective.objective_value,
            optimization_input.item_ids,
        )

        scipy_objective, scipy_obj_gradient = objective_wrapper(
            obj_value_func, obj_grad_func, optimization_input.objective.direction
        )

        # Step 3: Transform constraints to scipy constraint dicts
        scipy_constraints = []

        # Process SimpleConstraints
        for constraint in optimization_input.simple_constraints:
            const_value_func, const_grad_func = create_metric_calculator(
                constraint.metric,
                constraint.constraint_value,
                optimization_input.item_ids,
            )

            constraint_dict = constraint_wrapper(
                const_value_func,
                const_grad_func,
                constraint.threshold,
                constraint.direction,
            )
            scipy_constraints.append(constraint_dict)

        # Process FreqSevConstraints
        for freqsev_constraint in optimization_input.freqsev_constraints:
            const_value_func, const_grad_func = create_metric_calculator(
                freqsev_constraint.metric,
                freqsev_constraint.constraint_value,
                optimization_input.item_ids,
            )

            constraint_dict = constraint_wrapper(
                const_value_func,
                const_grad_func,
                freqsev_constraint.threshold,
                freqsev_constraint.direction,
            )
            scipy_constraints.append(constraint_dict)

        # Step 4: Transform bounds to scipy format
        scipy_bounds = bounds_to_scipy_bounds(
            optimization_input.share_bounds, optimization_input.item_ids
        )

        # Step 5: Generate initial guess
        # After readiness check, current_shares is guaranteed to be populated
        initial_guess = get_initial_guess(
            optimization_input.current_shares,
            optimization_input.item_ids,  # type: ignore
        )

        # Step 6: Call scipy.optimize.minimize
        # Use only user-specified constraints (no automatic budget constraint)
        all_constraints = scipy_constraints.copy() if scipy_constraints else []

        # Get remaining config values
        max_iter = config.get("max_iterations", MAX_ITERATIONS)
        tolerances = config.get("tolerances", DEFAULT_TOLERANCES)

        # Callback to track iterations (only if verbose)
        iteration_data = {"count": 0, "obj_values": [], "grad_norms": []}

        def callback(xk):
            iteration_data["count"] += 1
            obj_val = scipy_objective(xk)
            grad = scipy_obj_gradient(xk)
            grad_norm = np.linalg.norm(grad)
            iteration_data["obj_values"].append(obj_val)
            iteration_data["grad_norms"].append(grad_norm)
            if verbose and (
                iteration_data["count"] <= 5 or iteration_data["count"] % 10 == 0
            ):
                print(
                    f"  Iter {iteration_data['count']}: obj={obj_val:.8f}, "
                    f"|grad|={grad_norm:.8f}"
                )

        scipy_result = minimize(
            fun=scipy_objective,
            jac=scipy_obj_gradient,
            x0=initial_guess,
            bounds=scipy_bounds,
            constraints=all_constraints,
            method="SLSQP",  # Sequential Least Squares Programming
            options={
                "maxiter": max_iter,
                "ftol": tolerances["ftol"],
                "disp": verbose,
            },
            tol=0.0001,  # Constraint tolerance - old optimizer compatibility
            callback=callback,
        )

        # Log summary if few iterations (only if verbose)
        if verbose and iteration_data["count"] <= 3:
            print(
                f"\n⚠️  Optimization exited after only "
                f"{iteration_data['count']} iterations"
            )
            obj_initial = (
                iteration_data["obj_values"][0]
                if iteration_data["obj_values"]
                else "N/A"
            )
            print(f"   Initial obj: {obj_initial:.8f}")
            print(f"   Final obj: {scipy_result.fun:.8f}")
            grad_initial = (
                iteration_data["grad_norms"][0]
                if iteration_data["grad_norms"]
                else "N/A"
            )
            print(f"   Initial |grad|: {grad_initial:.8f}")
            if iteration_data["grad_norms"]:
                print(f"   Final |grad|: {iteration_data['grad_norms'][-1]:.8f}")

        # Step 7: Process results and evaluate constraints
        optimization_time = time.time() - start_time

        return process_scipy_result(
            scipy_result,
            optimization_input,
            optimization_time,
        )

    except Exception as e:
        # Return failed optimization result
        optimization_time = time.time() - start_time
        return OptimizationResult(
            success=False,
            optimal_shares=dict.fromkeys(optimization_input.item_ids, 0.0),
            objective_value=float("nan"),
            constraint_results=[],
            status=9,  # Error status
            message=f"Optimization failed: {str(e)}",
            n_iterations=0,
            optimization_time=optimization_time,
        )


def get_initial_guess(
    current_shares: dict[str, float], item_ids: list[str]
) -> np.ndarray:
    """Generate initial guess for optimization.

    Args:
        current_shares: Dict of current shares by item_id (guaranteed by preprocessing)
        item_ids: List of item identifiers

    Returns:
        Initial guess array for scipy optimization

    Note:
        Preprocessing ensures current_shares is never None and contains all item_ids
    """
    # Use provided current shares directly (no automatic normalization)
    weights = np.array([current_shares[item_id] for item_id in item_ids])
    return weights


def bounds_to_scipy_bounds(
    share_bounds: dict[str, BoundsSpec] | None, item_ids: list[str]
) -> list[tuple[float, float]] | None:
    """Convert BoundsSpec to scipy bounds format.

    Args:
        share_bounds: Bounds specification per item (may be None)
        item_ids: List of item identifiers in optimization order

    Returns:
        List of (lower, upper) tuples for scipy, or None if no bounds

    Format:
        scipy bounds: [(lower1, upper1), (lower2, upper2), ...]
    """
    if share_bounds is None:
        return None

    scipy_bounds = []
    for item_id in item_ids:
        if item_id in share_bounds:
            bounds_spec = share_bounds[item_id]
            scipy_bounds.append((bounds_spec.lower, bounds_spec.upper))
        else:
            # No bounds specified for this item - use (-inf, inf)
            scipy_bounds.append((float("-inf"), float("inf")))

    return scipy_bounds


def process_scipy_result(
    scipy_result: OptimizeResult,
    optimization_input: OptimizationInput,
    optimization_time: float,
) -> OptimizationResult:
    """Process scipy optimization result and evaluate constraints.

    Args:
        scipy_result: Result from scipy.optimize.minimize()
        optimization_input: Original optimization problem specification
            (with scaling factors)
        optimization_time: Total optimization time in seconds

    Returns:
        OptimizationResult with optimal solution and constraint
        evaluations (unscaled to original units)

    Note:
        For maximization problems, we need to negate scipy_result.fun
        to get the true objective value (since we negated it for minimization).

        If autoscaling was applied during preprocessing, this function unscales:
        - optimal_shares: multiply by _share_scales
        - objective_value: multiply by _obj_scale (disabled, set to 1.0)
        - constraint results: multiply by _constraint_scales (disabled, 1.0)

        NOTE: Objective/constraint scaling is currently disabled due to
        scale-invariant composite metrics (e.g., RatioMetric).
        The scaling factors exist but are set to 1.0.
    """
    # Extract optimal weights (still in scaled units)
    optimal_weights = scipy_result.x

    # Unscale shares if autoscaling was applied
    if optimization_input._share_scales is not None:
        optimal_shares = {
            item_id: float(weight * optimization_input._share_scales[item_id])
            for item_id, weight in zip(
                optimization_input.item_ids, optimal_weights, strict=True
            )
        }
    else:
        optimal_shares = {
            item_id: float(weight)
            for item_id, weight in zip(
                optimization_input.item_ids, optimal_weights, strict=True
            )
        }

    # Get objective value (un-negate for maximization)
    if optimization_input.objective.direction == "maximize":
        objective_value = -scipy_result.fun  # Un-negate
    else:
        objective_value = scipy_result.fun

    # Unscale objective if autoscaling was applied
    if optimization_input._obj_scale is not None:
        objective_value = objective_value * optimization_input._obj_scale

    # Evaluate all constraints at optimal solution (returns scaled results)
    constraint_results = _evaluate_constraints(optimization_input, optimal_weights)

    # Unscale constraint results if autoscaling was applied
    if optimization_input._constraint_scales is not None:
        unscaled_constraint_results = []
        for i, result in enumerate(constraint_results):
            scale = optimization_input._constraint_scales[i]
            unscaled_constraint_results.append(
                ConstraintResult(
                    constraint_type=result.constraint_type,
                    constraint_index=result.constraint_index,
                    metric_type=result.metric_type,
                    name=result.name,  # Preserve constraint name
                    threshold=result.threshold * scale,
                    direction=result.direction,
                    actual_value=result.actual_value * scale,
                    slack=result.slack * scale,
                    is_satisfied=result.is_satisfied,
                )
            )
        constraint_results = unscaled_constraint_results

    return OptimizationResult(
        success=bool(scipy_result.success),
        optimal_shares=optimal_shares,
        objective_value=float(objective_value),
        constraint_results=constraint_results,
        status=int(scipy_result.status),
        message=scipy_result.message or "",
        n_iterations=int(getattr(scipy_result, "nit", 0)),
        optimization_time=optimization_time,
    )


def _evaluate_constraints(
    optimization_input: OptimizationInput,
    optimal_weights: np.ndarray,
) -> list[ConstraintResult]:
    """Evaluate all constraints at the optimal solution.

    Args:
        optimization_input: Optimization problem specification
        optimal_weights: Optimal weight array from scipy

    Returns:
        List of ConstraintResult objects with actual values and slack
    """
    constraint_results = []

    # Evaluate SimpleConstraints
    for idx, constraint in enumerate(optimization_input.simple_constraints):
        value_func, _ = create_metric_calculator(
            constraint.metric,
            constraint.constraint_value,
            optimization_input.item_ids,
        )
        actual_value = value_func(optimal_weights)

        # Calculate slack (positive = satisfied, negative = violated)
        if constraint.direction == "cap":
            # constraint ≤ threshold → slack = threshold - actual
            slack = constraint.threshold - actual_value
        else:  # floor
            # constraint ≥ threshold → slack = actual - threshold
            slack = actual_value - constraint.threshold

        constraint_results.append(
            ConstraintResult(
                constraint_type="simple",
                constraint_index=idx,
                metric_type=constraint.metric.type,
                name=constraint.name,  # Copy name from constraint definition
                threshold=constraint.threshold,
                direction=constraint.direction,
                actual_value=actual_value,
                slack=slack,
                is_satisfied=(slack >= -1e-6),  # Small tolerance for numerical errors
            )
        )

    # Evaluate FreqSevConstraints
    for idx, freqsev_constraint in enumerate(optimization_input.freqsev_constraints):
        value_func, _ = create_metric_calculator(
            freqsev_constraint.metric,
            freqsev_constraint.constraint_value,
            optimization_input.item_ids,
        )
        actual_value = value_func(optimal_weights)

        # Calculate slack
        if freqsev_constraint.direction == "cap":
            slack = freqsev_constraint.threshold - actual_value
        else:  # floor
            slack = actual_value - freqsev_constraint.threshold

        constraint_results.append(
            ConstraintResult(
                constraint_type="freqsev",
                constraint_index=idx,
                metric_type=freqsev_constraint.metric.type,
                name=freqsev_constraint.name,  # Copy name from constraint definition
                threshold=freqsev_constraint.threshold,
                direction=freqsev_constraint.direction,
                actual_value=actual_value,
                slack=slack,
                is_satisfied=(slack >= -1e-6),
            )
        )

    return constraint_results
