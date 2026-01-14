"""Tests for efficient frontier generation.

Tests the generate_efficient_frontier() function with various constraint
variation scenarios.
"""

import numpy as np
import pytest
from pal import FreqSevSims, StochasticScalar
from pal.variables import ProteusVariable
from pop import (
    BoundsSpec,
    ConstraintVariation,
    EfficientFrontierInput,
    FreqSevConstraint,
    MeanMetric,
    ObjectiveSpec,
    OptimizationInput,
    SimpleConstraint,
    StdMetric,
    generate_efficient_frontier,
)


class TestBasicEfficientFrontier:
    """Test basic efficient frontier generation with single constraint variation."""

    def test_single_constraint_variation(self):
        """Test generating frontier by varying a single risk constraint.

        This tests the classic efficient frontier: maximize return subject to
        varying maximum risk levels. Should produce a series of portfolios
        with increasing risk and return.
        """
        # Create portfolio with two assets: high return/high risk, low return/low risk
        returns = ProteusVariable(
            "item",
            {
                "risky": StochasticScalar(
                    [0.08, 0.12, 0.15, 0.10, 0.14]
                ),  # Mean ~0.118, Std ~0.029
                "safe": StochasticScalar(
                    [0.03, 0.04, 0.05, 0.04, 0.04]
                ),  # Mean ~0.04, Std ~0.007
            },
        )

        # Objective: maximize mean return
        objective = ObjectiveSpec(
            objective_value=returns, metric=MeanMetric(), direction="maximize"
        )

        # Constraint: risk (std) must be below varying threshold
        risk_constraint = SimpleConstraint(
            constraint_value=returns,
            threshold=0.015,  # Base threshold (will be varied)
            direction="cap",
            metric=StdMetric(),
            name="max_risk",
        )

        # Base optimization
        base_opt = OptimizationInput(
            item_ids=["risky", "safe"],
            objective=objective,
            simple_constraints=[risk_constraint],
            share_bounds={
                "risky": BoundsSpec(lower=0.0, upper=100.0),
                "safe": BoundsSpec(lower=0.0, upper=100.0),
            },
        )

        # Create efficient frontier input
        # Vary risk from very low (0.008, nearly all safe) to high
        # (0.025, nearly all risky)
        frontier_input = EfficientFrontierInput(
            base_optimization=base_opt,
            constraint_variations=[
                ConstraintVariation(
                    constraint_type="simple",
                    constraint_name="max_risk",
                    min_threshold=0.008,  # Very conservative (should favor safe asset)
                    max_threshold=0.025,  # More risk (should favor risky asset)
                )
            ],
            n_points=5,  # Just 5 points for initial test
        )

        # Generate efficient frontier
        result = generate_efficient_frontier(frontier_input)

        # Basic validation
        assert len(result.optimization_results) == 5, "Should have 5 frontier points"

        # All optimizations should succeed for this simple case
        assert result.n_successful == 5, "All optimizations should succeed"
        assert len(result.successful_results) == 5
        assert len(result.failed_results) == 0
        assert result.n_failed == 0

        # Extract returns and risks for each point
        returns_list = []
        risks_list = []
        risky_weights = []

        for idx, opt_result in enumerate(result.optimization_results):
            if not opt_result.success:
                print(f"\nPoint {idx} failed: {opt_result.message}")
                continue

            assert opt_result.optimal_shares is not None

            # Extract weights
            risky_weight = opt_result.optimal_shares["risky"]
            safe_weight = opt_result.optimal_shares["safe"]

            print(
                f"\nPoint {idx}: risky={risky_weight:.4f}, "
                f"safe={safe_weight:.4f}, "
                f"sum={risky_weight + safe_weight:.4f}"
            )

            risky_weights.append(risky_weight)

            # Calculate actual return and risk
            risky_sims = np.array([0.08, 0.12, 0.15, 0.10, 0.14])
            safe_sims = np.array([0.03, 0.04, 0.05, 0.04, 0.04])
            portfolio_sims = risky_sims * risky_weight + safe_sims * safe_weight

            portfolio_return = np.mean(portfolio_sims)
            portfolio_risk = np.std(portfolio_sims, ddof=1)

            returns_list.append(portfolio_return)
            risks_list.append(portfolio_risk)

        # Validate efficient frontier properties
        # Note: Since both assets have positive returns and we're maximizing,
        # the optimizer will allocate as much as possible within bounds.
        # The efficient frontier is created by varying the risk
        # constraint.

        # 1. As risk constraint relaxes, allocated amount should
        # increase (more risky asset)
        safe_weights = [
            opt_result.optimal_shares["safe"]
            for opt_result in result.optimization_results
        ]
        for i in range(1, len(safe_weights)):
            # Safe weight should increase as we allow more risk
            assert safe_weights[i] >= safe_weights[i - 1] - 1e-4, (
                f"Total allocation should increase: "
                f"{safe_weights[i]} >= {safe_weights[i - 1]}"
            )

        # 2. With tighter risk constraints, should allocate only to safe asset
        assert risky_weights[0] < 0.1, (
            "First point (lowest risk) should be all safe asset"
        )

        # 3. Returns should increase as we relax risk constraint
        for i in range(1, len(returns_list)):
            assert returns_list[i] >= returns_list[i - 1] - 1e-6, (
                f"Return should increase along frontier: "
                f"{returns_list[i]} >= {returns_list[i - 1]}"
            )

        print("\nEfficient Frontier Results:")
        print(f"{'Risk Cap':<12} {'Actual Risk':<12} {'Return':<12} {'Risky %':<10}")
        print("-" * 50)

        thresholds = np.linspace(0.008, 0.025, 5)
        for threshold, risk, ret, weight in zip(
            thresholds, risks_list, returns_list, risky_weights, strict=True
        ):
            print(
                f"{threshold:>10.4f}   {risk:>10.4f}   {ret:>10.4f}   {weight:>8.1f}%"
            )


class TestMultipleConstraintVariations:
    """Test efficient frontier with multiple constraints varying in parallel."""

    def test_two_constraints_in_parallel(self):
        """Test varying two constraints simultaneously (risk cap and return floor)."""
        returns = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([0.03, 0.05, 0.07, 0.04, 0.06]),
                "asset2": StochasticScalar([0.08, 0.10, 0.12, 0.09, 0.11]),
            },
        )

        objective = ObjectiveSpec(
            objective_value=returns, metric=MeanMetric(), direction="maximize"
        )

        # Two constraints that will vary together
        risk_constraint = SimpleConstraint(
            constraint_value=returns,
            threshold=0.02,
            direction="cap",
            metric=StdMetric(),
            name="max_risk",
        )

        min_return_constraint = SimpleConstraint(
            constraint_value=returns,
            threshold=0.05,
            direction="floor",
            metric=MeanMetric(),
            name="min_return",
        )

        base_opt = OptimizationInput(
            item_ids=["asset1", "asset2"],
            objective=objective,
            current_shares={"asset1": 25.0, "asset2": 25.0},
            simple_constraints=[risk_constraint, min_return_constraint],
            share_bounds={
                "asset1": BoundsSpec(lower=0.0, upper=50.0),
                "asset2": BoundsSpec(lower=0.0, upper=50.0),
            },
        )

        # Vary both constraints in parallel
        frontier_input = EfficientFrontierInput(
            base_optimization=base_opt,
            constraint_variations=[
                ConstraintVariation(
                    constraint_type="simple",
                    constraint_name="max_risk",
                    min_threshold=0.015,
                    max_threshold=0.030,
                ),
                ConstraintVariation(
                    constraint_type="simple",
                    constraint_name="min_return",
                    min_threshold=0.04,
                    max_threshold=0.08,
                ),
            ],
            n_points=4,
        )

        result = generate_efficient_frontier(frontier_input)

        assert len(result.optimization_results) == 4
        # Should have at least some successes
        assert result.n_successful >= 1


class TestFreqSevEfficientFrontier:
    """Test efficient frontier with FreqSev constraints."""

    def test_freqsev_constraint_variation(self):
        """Test varying a FreqSev constraint threshold."""
        # Create FreqSev data using proper format
        n_sims = 5
        sim_index = np.array([0, 1, 2, 3, 4], dtype=int)

        # Asset1: lower losses
        values1 = np.array([400.0, 500.0, 450.0, 550.0, 480.0], dtype=float)
        # Asset2: higher losses
        values2 = np.array([800.0, 1000.0, 900.0, 1100.0, 950.0], dtype=float)

        losses = ProteusVariable(
            "item",
            {
                "asset1": FreqSevSims(
                    sim_index=sim_index, values=values1, n_sims=n_sims
                ),
                "asset2": FreqSevSims(
                    sim_index=sim_index, values=values2, n_sims=n_sims
                ),
            },
        )

        # Portfolio objective (use simple returns for objective)
        returns = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([0.05, 0.06, 0.04, 0.055, 0.045]),
                "asset2": StochasticScalar([0.08, 0.09, 0.07, 0.085, 0.075]),
            },
        )

        # Maximize returns
        objective = ObjectiveSpec(
            objective_value=returns, metric=MeanMetric(), direction="maximize"
        )

        # Cap on mean losses (will vary)
        loss_cap = FreqSevConstraint(
            constraint_value=losses,
            threshold=800.0,
            direction="cap",
            metric=MeanMetric(),
            name="max_loss",
        )

        base_opt = OptimizationInput(
            item_ids=["asset1", "asset2"],
            objective=objective,
            current_shares={"asset1": 50.0, "asset2": 50.0},
            freqsev_constraints=[loss_cap],
            share_bounds={
                "asset1": BoundsSpec(lower=0.0, upper=100.0),
                "asset2": BoundsSpec(lower=0.0, upper=100.0),
            },
        )

        frontier_input = EfficientFrontierInput(
            base_optimization=base_opt,
            constraint_variations=[
                ConstraintVariation(
                    constraint_type="freqsev",
                    constraint_name="max_loss",
                    min_threshold=500.0,
                    max_threshold=900.0,
                )
            ],
            n_points=3,
        )

        result = generate_efficient_frontier(frontier_input)

        assert len(result.optimization_results) == 3
        assert result.n_successful >= 1


class TestEfficientFrontierEdgeCases:
    """Test edge cases and failure scenarios."""

    def test_single_point_frontier(self):
        """Test frontier with just 1 point (very narrow range)."""
        returns = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([0.05, 0.06, 0.04]),
            },
        )

        objective = ObjectiveSpec(
            objective_value=returns, metric=MeanMetric(), direction="maximize"
        )

        constraint = SimpleConstraint(
            constraint_value=returns,
            threshold=0.10,
            direction="cap",
            metric=StdMetric(),
            name="risk",
        )

        base_opt = OptimizationInput(
            item_ids=["asset1"],
            objective=objective,
            current_shares={"asset1": 50.0},
            simple_constraints=[constraint],
            share_bounds={"asset1": BoundsSpec(lower=0.0, upper=100.0)},
        )

        # Very narrow range (minimum 3 points)
        frontier_input = EfficientFrontierInput(
            base_optimization=base_opt,
            constraint_variations=[
                ConstraintVariation(
                    constraint_type="simple",
                    constraint_name="risk",
                    min_threshold=0.049,
                    max_threshold=0.051,  # Very narrow range
                )
            ],
            n_points=3,  # Minimum allowed
        )

        result = generate_efficient_frontier(frontier_input)

        assert len(result.optimization_results) == 3
        assert result.n_successful == 3

    def test_impossible_constraints_cause_failures(self):
        """Test that impossible constraints result in failed optimizations."""
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

        # Impossible constraint: require mean > 0.20 when max possible per unit is ~0.08
        # With tight bounds, this becomes impossible
        constraint = SimpleConstraint(
            constraint_value=returns,
            threshold=0.20,
            direction="floor",
            metric=MeanMetric(),
            name="min_return",
        )

        base_opt = OptimizationInput(
            item_ids=["asset1", "asset2"],
            objective=objective,
            current_shares={"asset1": 0.5, "asset2": 0.5},
            simple_constraints=[constraint],
            share_bounds={
                "asset1": BoundsSpec(lower=0.0, upper=1.0),  # Tight bounds
                "asset2": BoundsSpec(lower=0.0, upper=1.0),  # Tight bounds
            },
        )

        frontier_input = EfficientFrontierInput(
            base_optimization=base_opt,
            constraint_variations=[
                ConstraintVariation(
                    constraint_type="simple",
                    constraint_name="min_return",
                    min_threshold=0.15,
                    max_threshold=0.25,
                )
            ],
            n_points=3,
        )

        result = generate_efficient_frontier(frontier_input)

        assert len(result.optimization_results) == 3
        # All should fail (impossible constraints with tight bounds)
        assert result.n_failed == 3
        assert result.n_successful == 0
        assert len(result.failed_results) == 3


class TestEfficientFrontierResultProperties:
    """Test result properties and helper methods."""

    def test_result_properties(self):
        """Test that result properties work correctly."""
        returns = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([0.05, 0.06, 0.04]),
            },
        )

        objective = ObjectiveSpec(
            objective_value=returns, metric=MeanMetric(), direction="maximize"
        )

        constraint = SimpleConstraint(
            constraint_value=returns,
            threshold=0.10,
            direction="cap",
            metric=StdMetric(),
            name="risk",
        )

        base_opt = OptimizationInput(
            item_ids=["asset1"],
            objective=objective,
            current_shares={"asset1": 50.0},
            simple_constraints=[constraint],
            share_bounds={"asset1": BoundsSpec(lower=0.0, upper=100.0)},
        )

        frontier_input = EfficientFrontierInput(
            base_optimization=base_opt,
            constraint_variations=[
                ConstraintVariation(
                    constraint_type="simple",
                    constraint_name="risk",
                    min_threshold=0.01,
                    max_threshold=0.10,
                )
            ],
            n_points=5,
        )

        result = generate_efficient_frontier(frontier_input)

        # Test all properties
        assert len(result.optimization_results) == 5
        assert result.n_successful + result.n_failed == 5
        assert len(result.successful_results) == result.n_successful
        assert len(result.failed_results) == result.n_failed
        assert result.total_time > 0

        # Check that successful_results are actually successful
        for r in result.successful_results:
            assert r.success

        # Check that failed_results are actually failed
        for r in result.failed_results:
            assert not r.success


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
