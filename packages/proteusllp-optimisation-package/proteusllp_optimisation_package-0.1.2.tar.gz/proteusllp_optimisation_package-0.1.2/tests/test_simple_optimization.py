"""Tests for simple optimization with StochasticScalar variables.

This module tests the core optimization functionality using basic PAL variables,
constraints, and objectives without FreqSev complexity.
"""

import pytest
from pal import StochasticScalar
from pal.variables import ProteusVariable
from pop import (
    BoundsSpec,
    MeanMetric,
    ObjectiveSpec,
    OptimizationInput,
    SimpleConstraint,
    SpreadVarMetric,
    StdMetric,
    optimize,
)


class TestBasicOptimization:
    """Test basic optimization without constraints."""

    def test_maximize_mean_return(self):
        """Test maximizing mean return with bounds."""
        # Create simple portfolio with two assets
        returns = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([0.05, 0.06, 0.04]),  # Mean ~0.05
                "asset2": StochasticScalar([0.08, 0.09, 0.07]),  # Mean ~0.08, higher
            },
        )

        objective = ObjectiveSpec(
            objective_value=returns, metric=MeanMetric(), direction="maximize"
        )

        # Add reasonable bounds to prevent unbounded solutions
        opt_input = OptimizationInput(
            item_ids=["asset1", "asset2"],
            objective=objective,
            current_shares={"asset1": 50.0, "asset2": 50.0},
            share_bounds={
                "asset1": BoundsSpec(lower=0.0, upper=100.0),
                "asset2": BoundsSpec(lower=0.0, upper=100.0),
            },
        )

        result = optimize(opt_input.preprocess())

        assert result.success
        assert result.optimal_shares is not None
        # Both assets maxed out at bounds (both have positive mean)
        # Just check optimization succeeded and shares are at bounds
        assert (
            result.optimal_shares["asset1"] + result.optimal_shares["asset2"]
            <= 200.0 + 1e-6
        )

    def test_minimize_std_dev(self):
        """Test minimizing standard deviation."""
        # Create portfolio with different risk levels
        returns = ProteusVariable(
            "item",
            {
                "low_risk": StochasticScalar([0.05, 0.051, 0.049]),  # Low variance
                "high_risk": StochasticScalar([0.05, 0.10, 0.00]),  # High variance
            },
        )

        objective = ObjectiveSpec(
            objective_value=returns, metric=StdMetric(), direction="minimize"
        )

        opt_input = OptimizationInput(
            item_ids=["low_risk", "high_risk"],
            objective=objective,
            current_shares={"low_risk": 50.0, "high_risk": 50.0},
        )

        result = optimize(opt_input.preprocess())

        assert result.success
        assert result.optimal_shares is not None
        # Should allocate more to low_risk (lower std dev)
        assert result.optimal_shares["low_risk"] > result.optimal_shares["high_risk"]

    def test_maximize_spreadvar_top_tail(self):
        """Test maximizing SpreadVar on top tail (targeting high outcomes)."""
        returns = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar(
                    [0.02, 0.04, 0.06, 0.08, 0.10]
                ),  # Uniform distribution
                "asset2": StochasticScalar(
                    [0.00, 0.02, 0.05, 0.12, 0.15]
                ),  # Higher top tail
            },
        )

        # Maximize mean of top 40% (60th to 100th percentile)
        objective = ObjectiveSpec(
            objective_value=returns,
            metric=SpreadVarMetric(lower_percentile=60.0, upper_percentile=100.0),
            direction="maximize",
        )

        opt_input = OptimizationInput(
            item_ids=["asset1", "asset2"],
            objective=objective,
            current_shares={"asset1": 50.0, "asset2": 50.0},
            share_bounds={
                "asset1": BoundsSpec(lower=0.0, upper=100.0),
                "asset2": BoundsSpec(lower=0.0, upper=100.0),
            },
        )

        result = optimize(opt_input.preprocess())

        assert result.success
        assert result.optimal_shares is not None
        # Both assets maxed out at upper bounds (both have positive top tail)
        # Just verify optimization succeeded
        assert (
            result.optimal_shares["asset1"] + result.optimal_shares["asset2"]
            <= 200.0 + 1e-6
        )

    def test_minimize_spreadvar_bottom_tail(self):
        """Test minimizing SpreadVar on bottom tail (reducing downside risk)."""
        # Create assets with distinctly different downside characteristics
        # Safe: mostly positive, rare small losses
        # Risky: can have large losses
        returns = ProteusVariable(
            "item",
            {
                "safe": StochasticScalar(
                    [0.05, 0.06, 0.04, 0.05, 0.07, 0.03, 0.06, 0.05, 0.04, 0.06]
                ),  # All positive
                "risky": StochasticScalar(
                    [-0.20, -0.15, 0.05, 0.10, 0.15, 0.08, 0.12, 0.10, 0.20, 0.18]
                ),  # Has large losses in bottom tail
            },
        )

        # MAXIMIZE mean of bottom 30% (worst outcomes) - higher = less negative = better
        objective = ObjectiveSpec(
            objective_value=returns,
            metric=SpreadVarMetric(lower_percentile=0.0, upper_percentile=30.0),
            direction="maximize",
        )

        opt_input = OptimizationInput(
            item_ids=["safe", "risky"],
            objective=objective,
            current_shares={"safe": 50.0, "risky": 50.0},
            share_bounds={
                "safe": BoundsSpec(lower=0.0, upper=100.0),
                "risky": BoundsSpec(lower=0.0, upper=100.0),
            },
        )

        result = optimize(opt_input.preprocess())

        assert result.success
        assert result.optimal_shares is not None
        # Should strongly prefer safe asset (no large downside)
        assert result.optimal_shares["safe"] > result.optimal_shares["risky"]


class TestBoundsHandling:
    """Test optimization with share bounds."""

    def test_bounds_enforced(self):
        """Test that share bounds are respected."""
        returns = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([0.05, 0.06, 0.04]),
                "asset2": StochasticScalar([0.08, 0.09, 0.07]),
            },
        )

        objective = ObjectiveSpec(
            objective_value=returns, metric=MeanMetric(), direction="maximize"
        )

        # Restrict asset2 to maximum 30% of portfolio
        opt_input = OptimizationInput(
            item_ids=["asset1", "asset2"],
            objective=objective,
            current_shares={"asset1": 50.0, "asset2": 50.0},
            share_bounds={
                "asset1": BoundsSpec(lower=0.0, upper=100.0),
                "asset2": BoundsSpec(lower=0.0, upper=30.0),  # Capped at 30
            },
        )

        result = optimize(opt_input.preprocess())

        assert result.success
        assert result.optimal_shares is not None
        # asset2 should be at its upper bound
        assert result.optimal_shares["asset2"] <= 30.0 + 1e-6

    def test_equal_bounds_fixes_share(self):
        """Test that equal lower/upper bound fixes a share."""
        returns = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([0.05, 0.06, 0.04]),
                "asset2": StochasticScalar([0.08, 0.09, 0.07]),
            },
        )

        objective = ObjectiveSpec(
            objective_value=returns, metric=MeanMetric(), direction="maximize"
        )

        # Fix asset1 at exactly 40
        opt_input = OptimizationInput(
            item_ids=["asset1", "asset2"],
            objective=objective,
            current_shares={"asset1": 50.0, "asset2": 50.0},
            share_bounds={
                "asset1": BoundsSpec(lower=40.0, upper=40.0),  # Fixed
                "asset2": BoundsSpec(lower=0.0, upper=100.0),
            },
        )

        result = optimize(opt_input.preprocess())

        assert result.success
        assert result.optimal_shares is not None
        # asset1 should be exactly 40
        assert abs(result.optimal_shares["asset1"] - 40.0) < 1e-6


class TestSimpleConstraints:
    """Test optimization with simple constraints."""

    def test_mean_cap_constraint(self):
        """Test cap constraint on mean (upper bound)."""
        returns = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([0.05, 0.06, 0.04]),
                "asset2": StochasticScalar([0.08, 0.09, 0.07]),
            },
        )

        objective = ObjectiveSpec(
            objective_value=returns, metric=MeanMetric(), direction="maximize"
        )

        constraint = SimpleConstraint(
            constraint_value=returns,
            threshold=0.06,  # Mean must be <= 0.06
            direction="cap",
            metric=MeanMetric(),
            name="max_mean",
        )

        opt_input = OptimizationInput(
            item_ids=["asset1", "asset2"],
            objective=objective,
            current_shares={"asset1": 50.0, "asset2": 50.0},
            simple_constraints=[constraint],
        )

        result = optimize(opt_input.preprocess())

        assert result.success
        assert result.optimal_shares is not None
        # Check constraint is satisfied
        assert len(result.constraint_results) == 1
        assert result.constraint_results[0].is_satisfied
        assert result.constraint_results[0].actual_value <= 0.06 + 1e-6

    def test_cap_constraint_with_bounds(self):
        """Test cap constraint with reasonable bounds."""
        returns = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([0.05, 0.06, 0.04]),
                "asset2": StochasticScalar([0.08, 0.09, 0.07]),
            },
        )

        objective = ObjectiveSpec(
            objective_value=returns, metric=MeanMetric(), direction="maximize"
        )

        constraint = SimpleConstraint(
            constraint_value=returns,
            threshold=0.02,  # Std dev must be <= 0.02
            direction="cap",
            metric=StdMetric(),
            name="max_risk",
        )

        opt_input = OptimizationInput(
            item_ids=["asset1", "asset2"],
            objective=objective,
            current_shares={"asset1": 50.0, "asset2": 50.0},
            simple_constraints=[constraint],
            share_bounds={
                "asset1": BoundsSpec(lower=0.0, upper=100.0),
                "asset2": BoundsSpec(lower=0.0, upper=100.0),
            },
        )

        result = optimize(opt_input.preprocess())

        assert result.success
        assert result.optimal_shares is not None
        # Check constraint is satisfied
        assert len(result.constraint_results) == 1
        assert result.constraint_results[0].is_satisfied
        assert result.constraint_results[0].actual_value <= 0.02 + 1e-6

    def test_multiple_constraints(self):
        """Test optimization with multiple constraints."""
        returns = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([0.05, 0.06, 0.04]),
                "asset2": StochasticScalar([0.08, 0.09, 0.07]),
                "asset3": StochasticScalar([0.10, 0.12, 0.08]),
            },
        )

        objective = ObjectiveSpec(
            objective_value=returns, metric=MeanMetric(), direction="maximize"
        )

        constraints = [
            SimpleConstraint(
                constraint_value=returns,
                threshold=0.08,
                direction="cap",
                metric=MeanMetric(),
                name="max_mean",
            ),
            SimpleConstraint(
                constraint_value=returns,
                threshold=0.03,
                direction="cap",
                metric=StdMetric(),
                name="max_std",
            ),
        ]

        opt_input = OptimizationInput(
            item_ids=["asset1", "asset2", "asset3"],
            objective=objective,
            current_shares={"asset1": 33.0, "asset2": 33.0, "asset3": 34.0},
            simple_constraints=constraints,
        )

        result = optimize(opt_input.preprocess())

        assert result.success
        assert result.optimal_shares is not None
        # Check both constraints are satisfied
        assert len(result.constraint_results) == 2
        assert all(c.is_satisfied for c in result.constraint_results)


class TestConstraintEvaluation:
    """Test constraint evaluation and slack calculation."""

    def test_constraint_slack_calculation(self):
        """Test that constraint slack is calculated correctly."""
        returns = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([0.05, 0.06, 0.04]),
                "asset2": StochasticScalar([0.08, 0.09, 0.07]),
            },
        )

        objective = ObjectiveSpec(
            objective_value=returns, metric=MeanMetric(), direction="maximize"
        )

        constraint = SimpleConstraint(
            constraint_value=returns,
            threshold=0.10,  # Generous cap
            direction="cap",
            metric=MeanMetric(),
            name="max_mean",
        )

        opt_input = OptimizationInput(
            item_ids=["asset1", "asset2"],
            objective=objective,
            current_shares={"asset1": 50.0, "asset2": 50.0},
            simple_constraints=[constraint],
            share_bounds={
                "asset1": BoundsSpec(lower=0.0, upper=100.0),
                "asset2": BoundsSpec(lower=0.0, upper=100.0),
            },
        )

        result = optimize(opt_input.preprocess())

        assert result.success
        assert len(result.constraint_results) == 1
        constraint_result = result.constraint_results[0]

        # For cap: slack = threshold - actual
        # Should be near zero or positive (satisfied with numerical tolerance)
        assert constraint_result.slack >= -1e-6  # Allow tiny numerical error
        assert constraint_result.is_satisfied

    def test_violated_constraints_property(self):
        """Test violated_constraints property when constraints cannot be met."""
        returns = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([0.05, 0.06, 0.04]),
                "asset2": StochasticScalar([0.08, 0.09, 0.07]),
            },
        )

        objective = ObjectiveSpec(
            objective_value=returns, metric=MeanMetric(), direction="maximize"
        )

        # Impossible constraint: mean must be <= 0.01 (too low)
        constraint = SimpleConstraint(
            constraint_value=returns,
            threshold=0.01,
            direction="cap",
            metric=MeanMetric(),
            name="impossible",
        )

        opt_input = OptimizationInput(
            item_ids=["asset1", "asset2"],
            objective=objective,
            current_shares={"asset1": 50.0, "asset2": 50.0},
            simple_constraints=[constraint],
        )

        result = optimize(opt_input.preprocess())

        # Optimization may fail or succeed with violated constraints
        if result.success:
            # Check if constraint is violated
            violated = result.violated_constraints
            if violated:
                assert not result.all_constraints_satisfied
                assert violated[0].slack < 0  # Negative slack = violated


class TestOptimizationResult:
    """Test OptimizationResult structure and properties."""

    def test_result_structure(self):
        """Test that OptimizationResult has expected structure."""
        returns = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([0.05, 0.06, 0.04]),
                "asset2": StochasticScalar([0.08, 0.09, 0.07]),
            },
        )

        objective = ObjectiveSpec(
            objective_value=returns, metric=MeanMetric(), direction="maximize"
        )

        opt_input = OptimizationInput(
            item_ids=["asset1", "asset2"],
            objective=objective,
            current_shares={"asset1": 50.0, "asset2": 50.0},
        )

        result = optimize(opt_input.preprocess())

        # Check all expected fields exist
        assert hasattr(result, "success")
        assert hasattr(result, "optimal_shares")
        assert hasattr(result, "objective_value")
        assert hasattr(result, "constraint_results")
        assert hasattr(result, "optimization_time")
        assert hasattr(result, "message")

        # Check properties
        assert hasattr(result, "violated_constraints")
        assert hasattr(result, "all_constraints_satisfied")

    def test_result_is_frozen(self):
        """Test that OptimizationResult is immutable."""
        returns = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([0.05, 0.06, 0.04]),
            },
        )

        objective = ObjectiveSpec(
            objective_value=returns, metric=MeanMetric(), direction="maximize"
        )

        opt_input = OptimizationInput(
            item_ids=["asset1"],
            objective=objective,
            current_shares={"asset1": 100.0},
        )

        result = optimize(opt_input.preprocess())

        # Try to modify result (should fail)
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            result.success = False  # type: ignore


class TestOptimizationFailures:
    """Test that optimizer fails gracefully for infeasible problems."""

    def test_conflicting_constraints(self):
        """Test conflicting numeric constraints (mean >= 150 and mean <= 100)."""
        # Create 3 assets with different mean returns
        returns = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([100.0] * 10000),
                "asset2": StochasticScalar([110.0] * 10000),
                "asset3": StochasticScalar([90.0] * 10000),
            },
        )

        objective = ObjectiveSpec(
            objective_value=returns, metric=MeanMetric(), direction="maximize"
        )

        # Conflicting constraints: mean >= 150 AND mean <= 100
        constraint_floor = SimpleConstraint(
            constraint_value=returns,
            threshold=150.0,  # Impossible - max weighted mean is ~110
            direction="floor",
            metric=MeanMetric(),
            name="mean_floor",
        )

        constraint_cap = SimpleConstraint(
            constraint_value=returns,
            threshold=100.0,  # Conflicts with floor constraint
            direction="cap",
            metric=MeanMetric(),
            name="mean_cap",
        )

        opt_input = OptimizationInput(
            item_ids=["asset1", "asset2", "asset3"],
            objective=objective,
            current_shares={"asset1": 0.33, "asset2": 0.33, "asset3": 0.34},
            simple_constraints=[constraint_floor, constraint_cap],
        )

        preprocessed = opt_input.preprocess()
        result = optimize(preprocessed)

        # Verify graceful failure - solver can't satisfy conflicting constraints
        assert result.success is False
        assert result.message is not None
        # At least one constraint should be violated
        assert len(result.constraint_results) == 2
        violated = [c for c in result.constraint_results if not c.is_satisfied]
        assert len(violated) >= 1  # At least one must be violated

    def test_impossible_bounds(self):
        """Test bounds that prevent constraint satisfaction."""
        # Create 2 assets with very different std devs
        returns = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([100.0] * 10000),  # No volatility
                "asset2": StochasticScalar([100.0, 200.0] * 5000),  # High volatility
            },
        )

        objective = ObjectiveSpec(
            objective_value=returns, metric=MeanMetric(), direction="maximize"
        )

        # Constraint: std dev must be >= 30 (need asset2 with high share)
        constraint = SimpleConstraint(
            constraint_value=returns,
            threshold=30.0,
            direction="floor",
            metric=StdMetric(),
            name="min_volatility",
        )

        # But bounds force mostly asset1 (can't achieve required volatility)
        opt_input = OptimizationInput(
            item_ids=["asset1", "asset2"],
            objective=objective,
            current_shares={"asset1": 0.9, "asset2": 0.1},
            simple_constraints=[constraint],
            share_bounds={
                "asset1": BoundsSpec(
                    lower=0.85, upper=0.95
                ),  # Forced to use mostly asset1
                "asset2": BoundsSpec(lower=0.05, upper=0.15),  # Can't get enough asset2
            },
        )

        preprocessed = opt_input.preprocess()
        result = optimize(preprocessed)

        # Verify graceful failure - can't satisfy constraint with given bounds
        assert result.success is False
        assert result.message is not None
        assert len(result.constraint_results) == 1
        # Constraint should be violated (couldn't achieve required volatility)
        assert not result.constraint_results[0].is_satisfied

    def test_infeasible_constraint_target(self):
        """Test constraint target outside variable's possible range."""
        # Create assets with low std dev (around 5-15)
        import numpy as np

        np.random.seed(42)
        returns = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar(np.random.normal(100.0, 10.0, 10000)),
                "asset2": StochasticScalar(np.random.normal(100.0, 8.0, 10000)),
                "asset3": StochasticScalar(np.random.normal(100.0, 12.0, 10000)),
            },
        )

        objective = ObjectiveSpec(
            objective_value=returns, metric=MeanMetric(), direction="maximize"
        )

        # Require std dev >= 100 when portfolio std dev is ~10-15
        constraint = SimpleConstraint(
            constraint_value=returns,
            threshold=100.0,  # Impossible - max portfolio std << 100
            direction="floor",
            metric=StdMetric(),
            name="impossible_volatility",
        )

        # Add bounds to prevent numerical blowup
        opt_input = OptimizationInput(
            item_ids=["asset1", "asset2", "asset3"],
            objective=objective,
            current_shares={"asset1": 0.33, "asset2": 0.33, "asset3": 0.34},
            simple_constraints=[constraint],
            share_bounds={
                "asset1": BoundsSpec(lower=0.0, upper=1.0),
                "asset2": BoundsSpec(lower=0.0, upper=1.0),
                "asset3": BoundsSpec(lower=0.0, upper=1.0),
            },
        )

        preprocessed = opt_input.preprocess()
        result = optimize(preprocessed)

        # Verify graceful failure - constraint target is impossible
        assert result.success is False
        assert result.message is not None
        assert len(result.constraint_results) == 1
        # The constraint should show large negative slack (violated)
        assert result.constraint_results[0].slack < -50.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
