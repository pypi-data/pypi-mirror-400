"""Metric-centric transformation functions for optimization.

This module implements the core mathematical transformations that convert
Pydantic models (ObjectiveSpec, Constraints) into scipy-compatible functions
using a metric-centric approach where the same mathematical logic is shared
between objectives and constraints.

Architecture:
- Core calculators: Pure mathematical functions for each metric type
- Wrappers: Context-specific scipy integration
- Dispatcher: Automatic calculator selection based on metric + data type

Key Components:
- create_metric_calculator(): Main dispatcher function
- create_scalar_*(): StochasticScalar-based calculators (Phase 2A)
- create_freqsev_*(): FreqSevSims-based calculators (Phase 2B)
- objective_wrapper(), constraint_wrapper(): Context handling
"""

from collections.abc import Callable
from typing import Any

import numpy as np
from pal import FreqSevSims, StochasticScalar
from pal.variables import ProteusVariable

from .models import (
    DifferenceMetric,
    MeanMetric,
    ProductMetric,
    RatioMetric,
    SpreadVarMetric,
    StdMetric,
    SumMetric,
)

# ============================================================================
# SHARED HELPER FUNCTIONS
# ============================================================================


def calculate_percentile_mask(
    values: np.ndarray,
    lower_percentile: float,
    upper_percentile: float,
) -> np.ndarray:
    """Calculate mask for values in a percentile range.

    This is the expensive operation (O(n log n)) due to ranking.
    Should be cached to avoid redundant computation.

    Args:
        values: 1D array of aggregated values (e.g., weighted sum of items)
        lower_percentile: Lower percentile bound (0-100 scale)
        upper_percentile: Upper percentile bound (0-100 scale)

    Returns:
        Boolean mask array, True for values in percentile range
    """
    n = len(values)

    # Get ranks (0-indexed, from 0 to n-1)
    # This is the expensive O(n log n) operation
    ranks = np.argsort(np.argsort(values))

    # Calculate bounds: percentile maps to position in [0, n-1]
    lower_bound = lower_percentile / 100.0 * (n - 1)
    upper_bound = upper_percentile / 100.0 * (n - 1)

    # Create mask for values in percentile range
    mask = (ranks >= lower_bound) & (ranks <= upper_bound)

    return mask


def calculate_spreadvar_on_values(
    values: np.ndarray,
    lower_percentile: float,
    upper_percentile: float,
) -> float:
    """Calculate SpreadVar for a 1D array.

    Mean of values in percentile range. This is a shared helper used
    by both StochasticScalar and FreqSevSims spreadvar calculators.

    Args:
        values: 1D array of simulation values (e.g., portfolio
        returns or occurrence values)
        lower_percentile: Lower percentile bound (0-100 scale)
        upper_percentile: Upper percentile bound (0-100 scale)

    Returns:
        Mean of values in the percentile range
    """
    n_sims = len(values)

    # Get ranks (0-indexed, from 0 to n_sims-1)
    ranks = np.argsort(np.argsort(values))

    # Calculate bounds: percentile maps to position in [0, n_sims-1]
    lower_bound = lower_percentile / 100.0 * (n_sims - 1)
    upper_bound = upper_percentile / 100.0 * (n_sims - 1)

    # Create mask for simulations in percentile range
    mask = (ranks >= lower_bound) & (ranks <= upper_bound)

    # Return mean of values in this range
    if np.any(mask):
        return float(np.mean(values[mask]))
    else:
        # Empty mask - return mean of all values as fallback
        return float(np.mean(values))


def calculate_spreadvar_gradient_on_matrix(
    sim_matrix: np.ndarray,
    weights: np.ndarray,
    lower_percentile: float,
    upper_percentile: float,
) -> np.ndarray:
    """Calculate SpreadVar gradient using rank-based masking.

    This is a shared helper used by both StochasticScalar and
    FreqSevSims spreadvar calculators.

    Args:
        sim_matrix: 2D array [n_sims x n_items] of item simulations
        weights: 1D array [n_items] of portfolio weights
        lower_percentile: Lower percentile bound (0-100 scale)
        upper_percentile: Upper percentile bound (0-100 scale)

    Returns:
        Gradient array [n_items] where each element is the mean contribution
        of that item in the percentile range
    """
    n_sims = sim_matrix.shape[0]
    n_items = sim_matrix.shape[1]

    # Compute portfolio values
    portfolio_values = np.dot(sim_matrix, weights)

    # Get ranks (0-indexed, from 0 to n_sims-1)
    ranks = np.argsort(np.argsort(portfolio_values))

    # Calculate bounds: percentile maps to position in [0, n_sims-1]
    lower_bound = lower_percentile / 100.0 * (n_sims - 1)
    upper_bound = upper_percentile / 100.0 * (n_sims - 1)

    # Create mask for simulations in percentile range
    mask = (ranks >= lower_bound) & (ranks <= upper_bound)

    # Calculate gradient as mean of item values in this range
    if np.any(mask):
        gradient = np.mean(sim_matrix[mask], axis=0)
    else:
        gradient = np.zeros(n_items)

    return gradient


# ============================================================================
# CORE METRIC CALCULATORS - StochasticScalar (Phase 2A)
# ============================================================================


def create_scalar_mean(
    pal_variable: ProteusVariable, item_ids: list[str]
) -> tuple[Callable[[np.ndarray], float], Callable[[np.ndarray], np.ndarray]]:
    """Create portfolio mean calculator for StochasticScalar data.

    Args:
        pal_variable: ProteusVariable containing StochasticScalar objects
        item_ids: List of item identifiers in optimization order

    Returns:
        Tuple of (value_function, gradient_function) where:
        - value_function(weights) → portfolio expected return
        - gradient_function(weights) → ∂(portfolio_mean)/∂(each_weight)

    Mathematical Foundation:
        Portfolio Mean = E[w₁R₁ + w₂R₂ + ... + wₙRₙ] = w₁E[R₁] + w₂E[R₂] + ... + wₙE[Rₙ]
        Gradient = [E[R₁], E[R₂], ..., E[Rₙ]]  (analytical - very efficient!)
    """
    # Extract mean returns for each asset (pre-compute for efficiency)
    asset_means = {}
    for item_id in item_ids:
        stoch_scalar = pal_variable.values[item_id]  # type: ignore
        # Minimal type check for runtime safety
        if not isinstance(stoch_scalar, StochasticScalar):
            raise ValueError(
                f"Expected StochasticScalar for item '{item_id}', "
                f"got {type(stoch_scalar).__name__}"
            )
        asset_means[item_id] = float(np.mean(stoch_scalar.values))

    # Create ordered array for efficient computation
    means_array = np.array([asset_means[item_id] for item_id in item_ids])

    def portfolio_mean_value(weights: np.ndarray) -> float:
        """Compute portfolio expected return: Σ(wᵢ * E[Rᵢ])."""
        return float(np.dot(weights, means_array))

    def portfolio_mean_gradient(weights: np.ndarray) -> np.ndarray:
        """Compute gradient of portfolio mean.

        Since ∂(Σ wᵢ * E[Rᵢ])/∂wⱼ = E[Rⱼ], gradient is just the asset means.
        Note: weights parameter unused but kept for consistent signature.
        """
        return means_array.copy()

    return portfolio_mean_value, portfolio_mean_gradient


def create_scalar_std(
    pal_variable: ProteusVariable, item_ids: list[str]
) -> tuple[Callable[[np.ndarray], float], Callable[[np.ndarray], np.ndarray]]:
    """Create portfolio standard deviation calculator for StochasticScalar data.

    Args:
        pal_variable: ProteusVariable containing StochasticScalar objects
        item_ids: List of item identifiers in optimization order

    Returns:
        Tuple of (value_function, gradient_function) where:
        - value_function(weights) → portfolio standard deviation
        - gradient_function(weights) → ∂(portfolio_std)/∂(each_weight)

    Mathematical Foundation:
        Portfolio Std = √(w'Σw) where Σ is the covariance matrix
        Gradient = (Σw) / √(w'Σw)  (normalized covariance terms)
    """
    # Extract simulation data and compute covariance matrix
    simulation_data = {}
    for item_id in item_ids:
        stoch_scalar = pal_variable.values[item_id]  # type: ignore
        if not isinstance(stoch_scalar, StochasticScalar):
            raise ValueError(
                f"create_scalar_std expects StochasticScalar for item '{item_id}', "
                f"got {type(stoch_scalar).__name__}"
            )
        simulation_data[item_id] = stoch_scalar.values

    # Create simulation matrix: [n_sims x n_assets]
    sim_matrix = np.column_stack([simulation_data[item_id] for item_id in item_ids])

    # Compute covariance matrix (pre-compute for efficiency)
    cov_matrix = np.cov(sim_matrix, rowvar=False)

    def portfolio_std_value(weights: np.ndarray) -> float:
        """Compute portfolio standard deviation: √(w'Σw)."""
        portfolio_variance = np.dot(weights, np.dot(cov_matrix, weights))

        # Handle numerical edge cases
        if portfolio_variance <= 0:
            return 0.0

        return float(np.sqrt(portfolio_variance))

    def portfolio_std_gradient(weights: np.ndarray) -> np.ndarray:
        """Compute gradient of portfolio standard deviation.

        ∂√(w'Σw)/∂wᵢ = (Σw)ᵢ / √(w'Σw)
        """
        portfolio_variance = np.dot(weights, np.dot(cov_matrix, weights))

        # Handle edge case where variance is zero
        if portfolio_variance <= 0:
            return np.zeros_like(weights)

        portfolio_std = np.sqrt(portfolio_variance)
        cov_weights = np.dot(cov_matrix, weights)

        return cov_weights / portfolio_std

    return portfolio_std_value, portfolio_std_gradient


def create_scalar_spreadvar(
    pal_variable: ProteusVariable, item_ids: list[str], lower: float, upper: float
) -> tuple[Callable[[np.ndarray], float], Callable[[np.ndarray], np.ndarray] | None]:
    """Create SpreadVar calculator for StochasticScalar data with mask caching.

    Args:
        pal_variable: ProteusVariable containing StochasticScalar objects
        item_ids: List of item identifiers in optimization order
        lower: Lower percentile for SpreadVar calculation (0-100)
        upper: Upper percentile for SpreadVar calculation (0-100)

    Returns:
        Tuple of (value_function, gradient_function) where both use cached
        mask calculation to avoid redundant O(n log n) ranking operations.

    Mathematical Foundation:
        SpreadVar = Mean of aggregated values in percentile range [lower, upper]
        Gradient uses rank-based masking: average item contribution in percentile range

        This matches the old optimizer's risk metric calculation:
        - Value: weighted_mean(agg_values[mask])
        - Gradient: weighted_mean(item_sims[mask])

    Note:
        For aggregated StochasticScalar data, this calculates mean of values in
        the percentile range of the aggregated distribution. For more accurate
        results with frequency-severity data, use create_freqsev_spreadvar() instead.
    """
    # Extract simulation data
    simulation_data = {}
    for item_id in item_ids:
        stoch_scalar = pal_variable.values[item_id]  # type: ignore
        if not isinstance(stoch_scalar, StochasticScalar):
            raise ValueError(
                f"create_scalar_spreadvar expects StochasticScalar "
                f"for item '{item_id}', got "
                f"{type(stoch_scalar).__name__}"
            )
        simulation_data[item_id] = stoch_scalar.values

    # Create simulation matrix: [n_sims x n_items]
    sim_matrix = np.column_stack([simulation_data[item_id] for item_id in item_ids])

    # Single-entry cache for mask
    _cached_weights: tuple | None = None
    _cached_mask: np.ndarray | None = None

    def _get_cached_mask(agg_values: np.ndarray, weights: np.ndarray) -> np.ndarray:
        """Get or compute mask for given aggregated values and weights."""
        nonlocal _cached_weights, _cached_mask

        key = tuple(weights)

        # Check if we have cached mask for these weights
        if _cached_weights != key:
            # Weights changed - recalculate mask using the aggregated values
            mask = calculate_percentile_mask(agg_values, lower, upper)

            # Store in cache
            _cached_weights = key
            _cached_mask = mask

        return _cached_mask  # type: ignore

    def value_function(weights: np.ndarray) -> float:
        """Compute SpreadVar value (mean of aggregated values in percentile range)."""
        agg_values = np.dot(sim_matrix, weights)
        mask = _get_cached_mask(agg_values, weights)

        if np.any(mask):
            return float(np.mean(agg_values[mask]))
        else:
            return float(np.mean(agg_values))

    def gradient_function(weights: np.ndarray) -> np.ndarray:
        """Compute SpreadVar gradient (mean item contribution in percentile range)."""
        agg_values = np.dot(sim_matrix, weights)
        mask = _get_cached_mask(agg_values, weights)

        if np.any(mask):
            return np.mean(sim_matrix[mask], axis=0)
        else:
            return np.zeros(len(item_ids))

    return value_function, gradient_function


# ============================================================================
# FREQSEV CALCULATORS (Phase 2B)
# ============================================================================


def create_freqsev_mean(
    freqsev_items: list[FreqSevSims], item_ids: list[str]
) -> tuple[Callable[[np.ndarray], float], Callable[[np.ndarray], np.ndarray]]:
    """Create value and gradient functions for mean of FreqSevSims occurrence.

    Uses analytical gradients via indicator approach:
    - Value: weight items → sum → occurrence → mean
    - Gradient: create indicator where combined==max → multiply by
      original → aggregate → mean

    Args:
        freqsev_items: List of FreqSevSims objects
        (one per portfolio item)
        item_ids: List of item identifiers (for error messages)

    Returns:
        Tuple of (value_function, gradient_function)
    """
    n_items = len(freqsev_items)

    def value_function(weights: np.ndarray) -> float:
        """Compute mean occurrence value."""
        # Weight and sum all items
        combined = sum(item * weights[i] for i, item in enumerate(freqsev_items))
        # Get occurrence (max event per simulation)
        occurrence = combined.occurrence()
        return float(occurrence.mean())

    def gradient_function(weights: np.ndarray) -> np.ndarray:
        """Compute gradient of mean occurrence w.r.t. weights."""
        # Step 1-3: Get combined occurrence (same as value calculation)
        combined = sum(item * weights[i] for i, item in enumerate(freqsev_items))
        occurrence = combined.occurrence()

        # Step 4: Create max values as FreqSevSims for proper comparison
        max_values_array = occurrence.values[combined.sim_index]
        max_values_freqsev = FreqSevSims(
            sim_index=combined.sim_index,
            values=max_values_array,
            n_sims=combined.n_sims,
        )

        # Step 5: Calculate gradient for each item using indicator approach
        gradient = np.zeros(n_items)
        for i in range(n_items):
            # Create indicator: 1 where combined event equals max for its sim
            indicator = combined == max_values_freqsev
            # Multiply by original unweighted item
            contribution = indicator * freqsev_items[i]
            # Aggregate to get StochasticScalar (sum all events per sim)
            aggregated = contribution.aggregate()
            # Calculate mean
            gradient[i] = aggregated.mean()

        return gradient

    return value_function, gradient_function


def create_freqsev_std(
    freqsev_items: list[FreqSevSims], item_ids: list[str]
) -> tuple[Callable[[np.ndarray], float], Callable[[np.ndarray], np.ndarray]]:
    """Create value and gradient functions for std of FreqSevSims occurrence.

    Uses analytical gradients via indicator approach with chain rule for std.

    Args:
        freqsev_items: List of FreqSevSims objects (one per portfolio item)
        item_ids: List of item identifiers (for error messages)

    Returns:
        Tuple of (value_function, gradient_function)
    """
    n_items = len(freqsev_items)

    def value_function(weights: np.ndarray) -> float:
        """Compute std of occurrence value."""
        combined = sum(item * weights[i] for i, item in enumerate(freqsev_items))
        occurrence = combined.occurrence()
        return float(occurrence.std())

    def gradient_function(weights: np.ndarray) -> np.ndarray:
        """Compute gradient of std occurrence w.r.t. weights using chain rule."""
        # Get combined occurrence
        combined = sum(item * weights[i] for i, item in enumerate(freqsev_items))
        occurrence = combined.occurrence()

        # Get occurrence values and calculate std components
        occ_values = occurrence.values
        mean_occ = np.mean(occ_values)
        std_occ = np.std(occ_values)

        # Handle zero std case
        if std_occ == 0:
            return np.zeros(n_items)

        # Create max values as FreqSevSims for proper comparison
        max_values_array = occ_values[combined.sim_index]
        max_values_freqsev = FreqSevSims(
            sim_index=combined.sim_index,
            values=max_values_array,
            n_sims=combined.n_sims,
        )

        # Calculate gradient for each item
        gradient = np.zeros(n_items)
        for i in range(n_items):
            # Create indicator and get contribution
            indicator = combined == max_values_freqsev
            contribution = indicator * freqsev_items[i]
            aggregated_contrib = contribution.aggregate()

            # Gradient of occurrence w.r.t. weights
            grad_occurrence = aggregated_contrib.values  # (n_sims,)

            # Chain rule: d(std)/d(weight) =
            #   d(std)/d(occurrence) * d(occurrence)/d(weight)
            # d(std)/d(occurrence_i) = (occurrence_i - mean) / std
            gradient[i] = np.mean((occ_values - mean_occ) * grad_occurrence) / std_occ

        return gradient

    return value_function, gradient_function


def create_freqsev_spreadvar(
    freqsev_items: list[FreqSevSims],
    item_ids: list[str],
    lower_percentile: float,
    upper_percentile: float,
) -> tuple[Callable[[np.ndarray], float], Callable[[np.ndarray], np.ndarray]]:
    """Create value and gradient functions for SpreadVar of FreqSevSims occurrence.

    Uses analytical gradients via indicator approach with cached mask.

    Args:
        freqsev_items: List of FreqSevSims objects (one per portfolio item)
        item_ids: List of item identifiers (for error messages)
        lower_percentile: Lower percentile bound (0-100)
        upper_percentile: Upper percentile bound (0-100)

    Returns:
        Tuple of (value_function, gradient_function)
    """
    n_items = len(freqsev_items)

    # Cache for mask calculation (single-entry cache)
    _cached_weights: tuple[float, ...] | None = None
    _cached_mask: np.ndarray | None = None

    def _get_cached_mask(
        occurrence_values: np.ndarray, weights: np.ndarray
    ) -> np.ndarray:
        """Get cached mask or recalculate if weights changed."""
        nonlocal _cached_weights, _cached_mask

        weights_tuple = tuple(weights)
        if _cached_weights != weights_tuple:
            # Recalculate mask using helper function
            _cached_mask = calculate_percentile_mask(
                occurrence_values, lower_percentile, upper_percentile
            )
            _cached_weights = weights_tuple

        return _cached_mask  # type: ignore

    def value_function(weights: np.ndarray) -> float:
        """Compute SpreadVar of occurrence (mean in percentile range)."""
        combined = sum(item * weights[i] for i, item in enumerate(freqsev_items))
        occurrence = combined.occurrence()
        occurrence_values = occurrence.values

        mask = _get_cached_mask(occurrence_values, weights)

        if np.any(mask):
            return float(np.mean(occurrence_values[mask]))
        else:
            return float(np.mean(occurrence_values))

    def gradient_function(weights: np.ndarray) -> np.ndarray:
        """Compute SpreadVar gradient using cached mask and indicator approach."""
        # Get combined occurrence
        combined = sum(item * weights[i] for i, item in enumerate(freqsev_items))
        occurrence = combined.occurrence()
        occurrence_values = occurrence.values

        # Get cached mask (same mask as value function)
        mask = _get_cached_mask(occurrence_values, weights)

        if not np.any(mask):
            return np.zeros(n_items)

        # Create max values as FreqSevSims for proper comparison
        max_values_array = occurrence_values[combined.sim_index]
        max_values_freqsev = FreqSevSims(
            sim_index=combined.sim_index,
            values=max_values_array,
            n_sims=combined.n_sims,
        )

        # Calculate gradient for each item
        gradient = np.zeros(n_items)
        for i in range(n_items):
            # Create indicator and get contribution
            indicator = combined == max_values_freqsev
            contribution = indicator * freqsev_items[i]
            aggregated_contrib = contribution.aggregate()

            # Apply mask and calculate mean in percentile range
            gradient[i] = np.mean(aggregated_contrib.values[mask])

        return gradient

    return value_function, gradient_function


# ============================================================================
# COMPOSITE METRIC CALCULATORS (Phase 2C)
# ============================================================================


def create_ratio_calculator(
    metric: RatioMetric,
    variable: ProteusVariable,
    item_ids: list[str],
) -> tuple[Callable[[np.ndarray], float], Callable[[np.ndarray], np.ndarray]]:
    """Create calculator for ratio metric using quotient rule.

    Computes numerator / denominator where both metrics evaluate on the same variable.
    Uses quotient rule for gradient: d(u/v) = (v·du - u·dv)/v²

    Args:
        metric: RatioMetric specification
        variable: ProteusVariable containing simulation data
        item_ids: List of item identifiers in optimization order

    Returns:
        Tuple of (value_function, gradient_function)
    """
    val_func_num, grad_func_num = create_metric_calculator(
        metric.numerator, variable, item_ids
    )
    val_func_den, grad_func_den = create_metric_calculator(
        metric.denominator, variable, item_ids
    )

    def value_function(weights: np.ndarray) -> float:
        u = val_func_num(weights)
        v = val_func_den(weights)
        return u / v

    def gradient_function(weights: np.ndarray) -> np.ndarray:
        u = val_func_num(weights)
        v = val_func_den(weights)
        du = grad_func_num(weights) if grad_func_num else np.zeros_like(weights)
        dv = grad_func_den(weights) if grad_func_den else np.zeros_like(weights)
        return (v * du - u * dv) / (v * v)

    return value_function, gradient_function


def create_product_calculator(
    metric: ProductMetric,
    variable: ProteusVariable,
    item_ids: list[str],
) -> tuple[Callable[[np.ndarray], float], Callable[[np.ndarray], np.ndarray]]:
    """Create calculator for product metric using product rule.

    Computes factor1 × factor2 where both metrics evaluate on the same variable.
    Uses product rule for gradient: d(u·v) = u·dv + v·du

    Args:
        metric: ProductMetric specification
        variable: ProteusVariable containing simulation data
        item_ids: List of item identifiers in optimization order

    Returns:
        Tuple of (value_function, gradient_function)
    """
    val_func1, grad_func1 = create_metric_calculator(metric.factor1, variable, item_ids)
    val_func2, grad_func2 = create_metric_calculator(metric.factor2, variable, item_ids)

    def value_function(weights: np.ndarray) -> float:
        u = val_func1(weights)
        v = val_func2(weights)
        return u * v

    def gradient_function(weights: np.ndarray) -> np.ndarray:
        u = val_func1(weights)
        v = val_func2(weights)
        du = grad_func1(weights) if grad_func1 else np.zeros_like(weights)
        dv = grad_func2(weights) if grad_func2 else np.zeros_like(weights)
        return u * dv + v * du

    return value_function, gradient_function


def create_sum_calculator(
    metric: SumMetric,
    variable: ProteusVariable,
    item_ids: list[str],
) -> tuple[Callable[[np.ndarray], float], Callable[[np.ndarray], np.ndarray]]:
    """Create calculator for sum metric.

    Computes metric1 + metric2 where both metrics evaluate on the same variable.
    Gradient: d(u+v) = du + dv

    Args:
        metric: SumMetric specification
        variable: ProteusVariable containing simulation data
        item_ids: List of item identifiers in optimization order

    Returns:
        Tuple of (value_function, gradient_function)
    """
    val_func1, grad_func1 = create_metric_calculator(metric.metric1, variable, item_ids)
    val_func2, grad_func2 = create_metric_calculator(metric.metric2, variable, item_ids)

    def value_function(weights: np.ndarray) -> float:
        return val_func1(weights) + val_func2(weights)

    def gradient_function(weights: np.ndarray) -> np.ndarray:
        grad1 = grad_func1(weights) if grad_func1 else np.zeros_like(weights)
        grad2 = grad_func2(weights) if grad_func2 else np.zeros_like(weights)
        return grad1 + grad2

    return value_function, gradient_function


def create_difference_calculator(
    metric: DifferenceMetric,
    variable: ProteusVariable,
    item_ids: list[str],
) -> tuple[Callable[[np.ndarray], float], Callable[[np.ndarray], np.ndarray]]:
    """Create calculator for difference metric.

    Computes metric1 - metric2 where both metrics evaluate on the same variable.
    Gradient: d(u-v) = du - dv

    Example: spreadvar(90-100) - mean() gives deviation from mean.

    Args:
        metric: DifferenceMetric specification
        variable: ProteusVariable containing simulation data
        item_ids: List of item identifiers in optimization order

    Returns:
        Tuple of (value_function, gradient_function)
    """
    val_func1, grad_func1 = create_metric_calculator(metric.metric1, variable, item_ids)
    val_func2, grad_func2 = create_metric_calculator(metric.metric2, variable, item_ids)

    def value_function(weights: np.ndarray) -> float:
        return val_func1(weights) - val_func2(weights)

    def gradient_function(weights: np.ndarray) -> np.ndarray:
        grad1 = grad_func1(weights) if grad_func1 else np.zeros_like(weights)
        grad2 = grad_func2(weights) if grad_func2 else np.zeros_like(weights)
        return grad1 - grad2

    return value_function, gradient_function


# ============================================================================
# METRIC CALCULATOR DISPATCHER
# ============================================================================


def create_metric_calculator(
    metric: MeanMetric
    | StdMetric
    | SpreadVarMetric
    | RatioMetric
    | ProductMetric
    | SumMetric
    | DifferenceMetric,
    pal_variable: ProteusVariable,
    item_ids: list[str],
) -> tuple[Callable[[np.ndarray], float], Callable[[np.ndarray], np.ndarray] | None]:
    """Factory function to choose the appropriate calculator.

    Chooses calculator based on metric type and data type.
    This is the main entry point that handles:
    - 3 base metric types: MeanMetric, StdMetric, SpreadVarMetric
    - 4 composite metric types: RatioMetric, ProductMetric,
      SumMetric, DifferenceMetric
    - 2 data types: StochasticScalar, FreqSevSims

    Composite metrics recursively call this function for their sub-metrics.

    Args:
        metric: Metric specification (base or composite)
        pal_variable: ProteusVariable containing simulation data
        item_ids: List of item identifiers in optimization order

    Returns:
        Tuple of (value_function, gradient_function)

    Raises:
        ValueError: If metric type is unsupported or data types are mixed
    """
    # Handle composite metrics first (they recursively call this function)
    if isinstance(metric, RatioMetric):
        return create_ratio_calculator(metric, pal_variable, item_ids)
    elif isinstance(metric, ProductMetric):
        return create_product_calculator(metric, pal_variable, item_ids)
    elif isinstance(metric, SumMetric):
        return create_sum_calculator(metric, pal_variable, item_ids)
    elif isinstance(metric, DifferenceMetric):
        return create_difference_calculator(metric, pal_variable, item_ids)

    # Handle base metrics with data type detection
    # Determine data type by inspecting first item
    first_item = next(iter(pal_variable.values.values()))  # type: ignore
    is_freqsev = isinstance(first_item, FreqSevSims)

    # Dispatch to appropriate calculator
    if isinstance(metric, MeanMetric):
        if is_freqsev:
            # Extract FreqSevSims items in correct order
            freqsev_items: list[FreqSevSims] = [
                pal_variable.values[item_id] for item_id in item_ids
            ]  # type: ignore
            return create_freqsev_mean(freqsev_items, item_ids)
        else:
            return create_scalar_mean(pal_variable, item_ids)

    elif isinstance(metric, StdMetric):
        if is_freqsev:
            # Extract FreqSevSims items in correct order
            freqsev_items: list[FreqSevSims] = [
                pal_variable.values[item_id] for item_id in item_ids
            ]  # type: ignore
            return create_freqsev_std(freqsev_items, item_ids)
        else:
            return create_scalar_std(pal_variable, item_ids)

    elif isinstance(metric, SpreadVarMetric):
        if is_freqsev:
            # Extract FreqSevSims items in correct order
            freqsev_items: list[FreqSevSims] = [
                pal_variable.values[item_id] for item_id in item_ids
            ]  # type: ignore
            return create_freqsev_spreadvar(
                freqsev_items,
                item_ids,
                metric.lower_percentile,
                metric.upper_percentile,
            )

        else:
            # Use scalar SpreadVar calculation (mean of values in percentile range)
            return create_scalar_spreadvar(
                pal_variable, item_ids, metric.lower_percentile, metric.upper_percentile
            )

    else:
        raise ValueError(f"Unsupported metric type: {type(metric).__name__}")


# ============================================================================
# SCIPY WRAPPER FUNCTIONS
# ============================================================================


def objective_wrapper(
    value_func: Callable[[np.ndarray], float],
    gradient_func: Callable[[np.ndarray], np.ndarray] | None,
    direction: str,
) -> tuple[Callable[[np.ndarray], float], Callable[[np.ndarray], np.ndarray] | None]:
    """Wrap metric calculator for scipy objective function.

    Args:
        value_func: Portfolio metric calculator
        gradient_func: Portfolio metric gradient calculator
        (None for gradient-free optimization)
        direction: "maximize" or "minimize"

    Returns:
        Tuple of (scipy_objective, scipy_gradient) where scipy
        minimizes. scipy_gradient is None if gradient_func is None
        (gradient-free optimization)

    Note:
        Since scipy.optimize.minimize() minimizes functions, we negate
        the objective and gradient for maximization problems.
    """
    if direction == "maximize":

        def scipy_objective(weights: np.ndarray) -> float:
            return -value_func(weights)

        if gradient_func is not None:

            def scipy_gradient(weights: np.ndarray) -> np.ndarray:
                return -gradient_func(weights)

        else:
            scipy_gradient = None  # type: ignore

    elif direction == "minimize":

        def scipy_objective(weights: np.ndarray) -> float:
            return value_func(weights)

        if gradient_func is not None:

            def scipy_gradient(weights: np.ndarray) -> np.ndarray:
                return gradient_func(weights)

        else:
            scipy_gradient = None  # type: ignore
    else:
        raise ValueError(
            f"Invalid direction: {direction}. Must be 'maximize' or 'minimize'."
        )

    return scipy_objective, scipy_gradient


def constraint_wrapper(
    value_func: Callable[[np.ndarray], float],
    gradient_func: Callable[[np.ndarray], np.ndarray] | None,
    threshold: float,
    direction: str,
) -> dict[str, Any]:
    """Wrap metric calculator for scipy constraint.

    Args:
        value_func: Portfolio metric calculator (same as used for objective!)
        gradient_func: Portfolio metric gradient calculator
        threshold: Constraint threshold value
        direction: "cap" (≤) or "floor" (≥)

    Returns:
        Scipy constraint dictionary with 'fun' and 'jac' keys

    Note:
        Scipy constraints use the format g(x) ≥ 0. We transform:
        - "cap": constraint ≤ threshold → threshold - constraint ≥ 0
        - "floor": constraint ≥ threshold → constraint - threshold ≥ 0
    """
    if direction == "cap":
        # constraint ≤ threshold → threshold - constraint ≥ 0
        def constraint_func(weights: np.ndarray) -> float:
            return threshold - value_func(weights)

        def constraint_grad(weights: np.ndarray) -> np.ndarray:
            if gradient_func is not None:
                return -gradient_func(weights)
            else:
                return np.zeros_like(weights)  # Return zero gradient if none provided

    elif direction == "floor":
        # constraint ≥ threshold → constraint - threshold ≥ 0
        def constraint_func(weights: np.ndarray) -> float:
            return value_func(weights) - threshold

        def constraint_grad(weights: np.ndarray) -> np.ndarray:
            if gradient_func is not None:
                return gradient_func(weights)
            else:
                return np.zeros_like(weights)  # Return zero gradient if none provided

    else:
        raise ValueError(f"Invalid direction: {direction}. Must be 'cap' or 'floor'.")

    # Build scipy constraint dictionary
    constraint_dict: dict[str, Any] = {
        "type": "ineq",
        "fun": constraint_func,
    }  # Inequality constraint (g(x) ≥ 0)

    # Add gradient if available
    if gradient_func is not None:
        constraint_dict["jac"] = constraint_grad

    return constraint_dict
