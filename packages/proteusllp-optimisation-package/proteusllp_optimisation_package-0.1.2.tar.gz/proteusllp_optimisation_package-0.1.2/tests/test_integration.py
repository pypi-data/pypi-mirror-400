"""Integration tests for end-to-end optimization workflows.

These tests validate realistic combinations of features that users would actually run,
testing the interaction between components rather than individual features in isolation.

Tests cover:
- Mixed constraint types (simple + FreqSev) in same optimization
- Composite metrics in both objectives and constraints
- Large portfolios with multiple constraints
- Full API workflow: input → preprocess → optimize → result
- Efficient frontier with complex setups
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
    RatioMetric,
    SimpleConstraint,
    SpreadVarMetric,
    StdMetric,
    generate_efficient_frontier,
    optimize,
)


class TestMixedConstraintTypes:
    """Test optimizations with both simple and FreqSev constraints together."""

    def test_simple_and_freqsev_constraints_combined(self):
        """Test optimization with both simple and FreqSev constraints."""
        # Portfolio with 3 assets
        portfolio = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([100.0, 110.0, 90.0, 105.0, 95.0]),
                "asset2": StochasticScalar([200.0, 220.0, 180.0, 210.0, 190.0]),
                "asset3": StochasticScalar([150.0, 165.0, 135.0, 157.5, 142.5]),
            },
        )

        # FreqSev losses (same sim_index for all assets)
        n_sims = 5
        sim_index = np.array([1, 2, 2, 3, 4], dtype=int)

        losses = ProteusVariable(
            "item",
            {
                "asset1": FreqSevSims(
                    sim_index=sim_index,
                    values=np.array([500.0, 700.0, 600.0, 800.0, 550.0], dtype=float),
                    n_sims=n_sims,
                ),
                "asset2": FreqSevSims(
                    sim_index=sim_index,
                    values=np.array(
                        [1500.0, 2000.0, 1800.0, 2200.0, 1600.0], dtype=float
                    ),
                    n_sims=n_sims,
                ),
                "asset3": FreqSevSims(
                    sim_index=sim_index,
                    values=np.array(
                        [1000.0, 1400.0, 1200.0, 1500.0, 1100.0], dtype=float
                    ),
                    n_sims=n_sims,
                ),
            },
        )

        objective = ObjectiveSpec(
            objective_value=portfolio, metric=MeanMetric(), direction="maximize"
        )

        # Simple constraint: cap on portfolio standard deviation
        simple_constraint = SimpleConstraint(
            constraint_value=portfolio,
            threshold=15.0,
            direction="cap",
            metric=StdMetric(),
            name="max_portfolio_risk",
        )

        # FreqSev constraint: cap on mean loss
        freqsev_constraint = FreqSevConstraint(
            constraint_value=losses,
            threshold=1200.0,
            direction="cap",
            metric=MeanMetric(),
            name="max_mean_loss",
        )

        opt_input = OptimizationInput(
            item_ids=["asset1", "asset2", "asset3"],
            objective=objective,
            current_shares={"asset1": 0.33, "asset2": 0.33, "asset3": 0.34},
            simple_constraints=[simple_constraint],
            freqsev_constraints=[freqsev_constraint],
            share_bounds={
                "asset1": BoundsSpec(lower=0.0, upper=1.0),
                "asset2": BoundsSpec(lower=0.0, upper=1.0),
                "asset3": BoundsSpec(lower=0.0, upper=1.0),
            },
        )

        result = optimize(opt_input.preprocess())

        assert result.optimal_shares is not None

        # Should have 2 constraints: 1 simple + 1 FreqSev
        assert len(result.constraint_results) == 2

        # Check constraints (may not all be satisfied if optimizer
        # didn't converge fully)
        if result.success:
            for constraint_result in result.constraint_results:
                assert constraint_result.is_satisfied, (
                    f"Constraint {constraint_result.name} violated"
                )

    def test_multiple_constraints_of_each_type(self):
        """Test optimization with multiple simple AND multiple FreqSev constraints."""
        portfolio = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([100.0, 110.0, 90.0, 105.0, 95.0]),
                "asset2": StochasticScalar([200.0, 220.0, 180.0, 210.0, 190.0]),
            },
        )

        n_sims = 5
        sim_index = np.array([1, 2, 2, 3, 4], dtype=int)

        losses = ProteusVariable(
            "item",
            {
                "asset1": FreqSevSims(
                    sim_index=sim_index,
                    values=np.array([500.0, 700.0, 600.0, 800.0, 550.0], dtype=float),
                    n_sims=n_sims,
                ),
                "asset2": FreqSevSims(
                    sim_index=sim_index,
                    values=np.array(
                        [1500.0, 2000.0, 1800.0, 2200.0, 1600.0], dtype=float
                    ),
                    n_sims=n_sims,
                ),
            },
        )

        objective = ObjectiveSpec(
            objective_value=portfolio, metric=MeanMetric(), direction="maximize"
        )

        # Two simple constraints
        simple_constraint1 = SimpleConstraint(
            constraint_value=portfolio,
            threshold=15.0,
            direction="cap",
            metric=StdMetric(),
            name="max_std",
        )

        simple_constraint2 = SimpleConstraint(
            constraint_value=portfolio,
            threshold=100.0,
            direction="floor",
            metric=MeanMetric(),
            name="min_mean",
        )

        # Two FreqSev constraints
        freqsev_constraint1 = FreqSevConstraint(
            constraint_value=losses,
            threshold=1500.0,
            direction="cap",
            metric=MeanMetric(),
            name="max_mean_loss",
        )

        freqsev_constraint2 = FreqSevConstraint(
            constraint_value=losses,
            threshold=500.0,
            direction="cap",
            metric=StdMetric(),
            name="max_loss_volatility",
        )

        opt_input = OptimizationInput(
            item_ids=["asset1", "asset2"],
            objective=objective,
            current_shares={"asset1": 0.5, "asset2": 0.5},
            simple_constraints=[simple_constraint1, simple_constraint2],
            freqsev_constraints=[freqsev_constraint1, freqsev_constraint2],
            share_bounds={
                "asset1": BoundsSpec(lower=0.0, upper=1.0),
                "asset2": BoundsSpec(lower=0.0, upper=1.0),
            },
        )

        result = optimize(opt_input.preprocess())

        assert result.optimal_shares is not None

        # Should have 4 constraints total
        assert len(result.constraint_results) == 4

        # Check constraints (may not all be satisfied if optimizer didn't converge)
        if result.success:
            for constraint_result in result.constraint_results:
                assert constraint_result.is_satisfied, (
                    f"Constraint {constraint_result.name} violated"
                )


class TestCompositeMetricsInConstraints:
    """Test composite metrics used in constraints, not just objectives."""

    def test_sharpe_ratio_constraint(self):
        """Test optimization with Sharpe ratio (mean/std) as a floor constraint."""
        portfolio = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([100.0, 110.0, 90.0, 105.0, 95.0]),
                "asset2": StochasticScalar([200.0, 220.0, 180.0, 210.0, 190.0]),
                "asset3": StochasticScalar([150.0, 165.0, 135.0, 157.5, 142.5]),
            },
        )

        # Maximize mean return
        objective = ObjectiveSpec(
            objective_value=portfolio, metric=MeanMetric(), direction="maximize"
        )

        # Constraint: Sharpe ratio must be >= 5.0
        sharpe_metric = RatioMetric(
            numerator=MeanMetric(), denominator=StdMetric(), name="sharpe_ratio"
        )
        sharpe_constraint = SimpleConstraint(
            constraint_value=portfolio,
            threshold=5.0,
            direction="floor",
            metric=sharpe_metric,
            name="min_sharpe_ratio",
        )

        opt_input = OptimizationInput(
            item_ids=["asset1", "asset2", "asset3"],
            objective=objective,
            current_shares={"asset1": 0.33, "asset2": 0.33, "asset3": 0.34},
            simple_constraints=[sharpe_constraint],
            share_bounds={
                "asset1": BoundsSpec(lower=0.0, upper=1.0),
                "asset2": BoundsSpec(lower=0.0, upper=1.0),
                "asset3": BoundsSpec(lower=0.0, upper=1.0),
            },
        )

        result = optimize(opt_input.preprocess())

        assert result.success
        assert result.optimal_shares is not None
        assert len(result.constraint_results) == 1

        constraint_result = result.constraint_results[0]
        assert constraint_result.is_satisfied
        assert constraint_result.actual_value >= 5.0 - 1e-6

    def test_composite_metric_objective_with_simple_constraints(self):
        """Test composite metric (Sharpe ratio) as objective with simple constraints."""
        portfolio = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([100.0, 110.0, 90.0, 105.0, 95.0]),
                "asset2": StochasticScalar([200.0, 220.0, 180.0, 210.0, 190.0]),
            },
        )

        # Maximize Sharpe ratio (mean/std)
        sharpe_metric = RatioMetric(
            numerator=MeanMetric(), denominator=StdMetric(), name="sharpe_ratio"
        )
        objective = ObjectiveSpec(
            objective_value=portfolio, metric=sharpe_metric, direction="maximize"
        )

        # Cap on portfolio mean (to make problem interesting)
        mean_constraint = SimpleConstraint(
            constraint_value=portfolio,
            threshold=180.0,
            direction="cap",
            metric=MeanMetric(),
            name="max_mean",
        )

        opt_input = OptimizationInput(
            item_ids=["asset1", "asset2"],
            objective=objective,
            current_shares={"asset1": 0.5, "asset2": 0.5},
            simple_constraints=[mean_constraint],
            share_bounds={
                "asset1": BoundsSpec(lower=0.0, upper=1.0),
                "asset2": BoundsSpec(lower=0.0, upper=1.0),
            },
        )

        result = optimize(opt_input.preprocess())

        assert result.success
        assert result.optimal_shares is not None
        assert len(result.constraint_results) == 1
        assert result.constraint_results[0].is_satisfied


class TestLargePortfolio:
    """Test optimization with larger portfolios (10+ assets) to validate scalability."""

    def test_ten_asset_portfolio_with_constraints(self):
        """Test optimization with 10 assets, multiple constraints."""
        n_assets = 10
        n_sims = 100

        # Create portfolio with 10 assets
        np.random.seed(42)
        portfolio_dict = {
            f"asset{i}": StochasticScalar(np.random.normal(100 + i * 10, 10, n_sims))
            for i in range(n_assets)
        }
        portfolio = ProteusVariable("item", portfolio_dict)

        # Maximize mean
        objective = ObjectiveSpec(
            objective_value=portfolio, metric=MeanMetric(), direction="maximize"
        )

        # Add a few constraints
        std_constraint = SimpleConstraint(
            constraint_value=portfolio,
            threshold=20.0,
            direction="cap",
            metric=StdMetric(),
            name="max_risk",
        )

        spreadvar_constraint = SimpleConstraint(
            constraint_value=portfolio,
            threshold=100.0,
            direction="floor",
            metric=SpreadVarMetric(lower_percentile=0.0, upper_percentile=50.0),
            name="min_bottom_half_mean",
        )

        # Initial shares: equal weight
        current_shares = {f"asset{i}": 1.0 / n_assets for i in range(n_assets)}

        # Bounds: each asset between 0 and 0.2 (20%)
        share_bounds = {
            f"asset{i}": BoundsSpec(lower=0.0, upper=0.2) for i in range(n_assets)
        }

        opt_input = OptimizationInput(
            item_ids=[f"asset{i}" for i in range(n_assets)],
            objective=objective,
            current_shares=current_shares,
            simple_constraints=[std_constraint, spreadvar_constraint],
            share_bounds=share_bounds,
        )

        result = optimize(opt_input.preprocess())

        assert result.success
        assert result.optimal_shares is not None
        assert len(result.optimal_shares) == n_assets

        # Check all constraints satisfied
        assert len(result.constraint_results) == 2
        for constraint_result in result.constraint_results:
            assert constraint_result.is_satisfied

        # Check bounds respected
        for i in range(n_assets):
            assert 0.0 - 1e-6 <= result.optimal_shares[f"asset{i}"] <= 0.2 + 1e-6


class TestFullAPIWorkflow:
    """Test complete API workflow from input creation to result analysis."""

    def test_full_workflow_input_to_result(self):
        """Test complete workflow: input validation, preprocess, optimize, analyze."""
        # Step 1: Create input data
        portfolio = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([100.0, 110.0, 90.0, 105.0, 95.0]),
                "asset2": StochasticScalar([200.0, 220.0, 180.0, 210.0, 190.0]),
            },
        )

        objective = ObjectiveSpec(
            objective_value=portfolio, metric=MeanMetric(), direction="maximize"
        )

        constraint = SimpleConstraint(
            constraint_value=portfolio,
            threshold=15.0,
            direction="cap",
            metric=StdMetric(),
            name="max_risk",
        )

        # Step 2: Create OptimizationInput (triggers validation)
        opt_input = OptimizationInput(
            item_ids=["asset1", "asset2"],
            objective=objective,
            current_shares={"asset1": 0.5, "asset2": 0.5},
            simple_constraints=[constraint],
            share_bounds={
                "asset1": BoundsSpec(lower=0.0, upper=1.0),
                "asset2": BoundsSpec(lower=0.0, upper=1.0),
            },
        )

        # Step 3: Preprocess (converts to optimization-ready format)
        preprocessed = opt_input.preprocess()
        assert preprocessed.is_preprocessed  # Check it's preprocessed
        assert len(preprocessed.item_ids) == 2
        assert preprocessed.current_shares is not None

        # Step 4: Optimize
        result = optimize(preprocessed)

        # Step 5: Analyze result
        assert result.success
        assert result.optimal_shares is not None
        assert len(result.optimal_shares) == 2
        assert result.objective_value is not None
        assert len(result.constraint_results) == 1
        assert result.constraint_results[0].is_satisfied
        assert (
            result.constraint_results[0].slack >= -1e-6
        )  # Non-negative slack for satisfied constraint

        # Test result is frozen (immutable)
        with pytest.raises(ValueError):  # Pydantic raises ValidationError
            result.success = False  # Should fail - result is frozen

    def test_workflow_with_validation_error(self):
        """Test that workflow catches validation errors early."""
        # PAL will catch this during ProteusVariable creation, not preprocessing
        with pytest.raises(ValueError, match="Number of simulations do not match"):
            ProteusVariable(
                "item",
                {
                    "asset1": StochasticScalar([100.0, 110.0, 90.0]),
                    "asset2": StochasticScalar(
                        [200.0, 220.0, 180.0, 210.0]
                    ),  # Different length!
                },
            )


class TestEfficientFrontierIntegration:
    """Test efficient frontier generation with complex setups."""

    def test_efficient_frontier_with_composite_objective(self):
        """Test efficient frontier with Sharpe ratio objective and risk constraint."""
        portfolio = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([100.0, 110.0, 90.0, 105.0, 95.0]),
                "asset2": StochasticScalar([200.0, 220.0, 180.0, 210.0, 190.0]),
            },
        )

        # Sharpe ratio objective
        sharpe_metric = RatioMetric(
            numerator=MeanMetric(), denominator=StdMetric(), name="sharpe_ratio"
        )
        objective = ObjectiveSpec(
            objective_value=portfolio, metric=sharpe_metric, direction="maximize"
        )

        # Varying risk constraint
        risk_constraint = SimpleConstraint(
            constraint_value=portfolio,
            threshold=10.0,  # Will be varied
            direction="cap",
            metric=StdMetric(),
            name="max_risk",
        )

        base_optimization = OptimizationInput(
            item_ids=["asset1", "asset2"],
            objective=objective,
            current_shares={"asset1": 0.5, "asset2": 0.5},
            simple_constraints=[risk_constraint],
            share_bounds={
                "asset1": BoundsSpec(lower=0.0, upper=1.0),
                "asset2": BoundsSpec(lower=0.0, upper=1.0),
            },
        )

        # Vary risk threshold from 8 to 20
        frontier_input = EfficientFrontierInput(
            base_optimization=base_optimization,
            constraint_variations=[
                ConstraintVariation(
                    constraint_type="simple",
                    constraint_name="max_risk",
                    min_threshold=8.0,
                    max_threshold=20.0,
                )
            ],
            n_points=5,
        )

        frontier_result = generate_efficient_frontier(frontier_input)

        assert len(frontier_result.optimization_results) == 5

        # Most optimizations should succeed (allow some failures with tight constraints)
        assert frontier_result.n_successful >= 3

    def test_efficient_frontier_with_mixed_constraints(self):
        """Test efficient frontier with simple and FreqSev constraints."""
        portfolio = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([100.0, 110.0, 90.0, 105.0, 95.0]),
                "asset2": StochasticScalar([200.0, 220.0, 180.0, 210.0, 190.0]),
            },
        )

        n_sims = 5
        sim_index = np.array([1, 2, 2, 3, 4], dtype=int)

        losses = ProteusVariable(
            "item",
            {
                "asset1": FreqSevSims(
                    sim_index=sim_index,
                    values=np.array([500.0, 700.0, 600.0, 800.0, 550.0], dtype=float),
                    n_sims=n_sims,
                ),
                "asset2": FreqSevSims(
                    sim_index=sim_index,
                    values=np.array(
                        [1500.0, 2000.0, 1800.0, 2200.0, 1600.0], dtype=float
                    ),
                    n_sims=n_sims,
                ),
            },
        )

        objective = ObjectiveSpec(
            objective_value=portfolio, metric=MeanMetric(), direction="maximize"
        )

        # Fixed simple constraint
        simple_constraint = SimpleConstraint(
            constraint_value=portfolio,
            threshold=15.0,
            direction="cap",
            metric=StdMetric(),
            name="max_std",
        )

        # Varying FreqSev constraint
        freqsev_constraint = FreqSevConstraint(
            constraint_value=losses,
            threshold=1200.0,  # Will be varied
            direction="cap",
            metric=MeanMetric(),
            name="max_mean_loss",
        )

        base_optimization = OptimizationInput(
            item_ids=["asset1", "asset2"],
            objective=objective,
            current_shares={"asset1": 0.5, "asset2": 0.5},
            simple_constraints=[simple_constraint],
            freqsev_constraints=[freqsev_constraint],
            share_bounds={
                "asset1": BoundsSpec(lower=0.0, upper=1.0),
                "asset2": BoundsSpec(lower=0.0, upper=1.0),
            },
        )

        # Vary loss threshold
        frontier_input = EfficientFrontierInput(
            base_optimization=base_optimization,
            constraint_variations=[
                ConstraintVariation(
                    constraint_type="freqsev",
                    constraint_name="max_mean_loss",
                    min_threshold=1000.0,
                    max_threshold=1500.0,
                )
            ],
            n_points=4,
        )

        frontier_result = generate_efficient_frontier(frontier_input)

        assert len(frontier_result.optimization_results) == 4

        # Most optimizations should succeed (allow some failures with tight constraints)
        assert frontier_result.n_successful >= 2

        # Each result should have 2 constraints (1 simple + 1 FreqSev)
        for result in frontier_result.optimization_results:
            assert len(result.constraint_results) == 2


class TestRealWorldScenarios:
    """Test scenarios that mimic real-world portfolio optimization use cases."""

    def test_risk_parity_style_allocation(self):
        """Test allocation seeking to equalize risk contributions (minimize std)."""
        # 3 assets with different risk levels
        portfolio = ProteusVariable(
            "item",
            {
                "low_risk": StochasticScalar(np.random.normal(100, 5, 100)),
                "medium_risk": StochasticScalar(np.random.normal(105, 10, 100)),
                "high_risk": StochasticScalar(np.random.normal(110, 20, 100)),
            },
        )

        # Minimize portfolio std deviation (risk parity objective)
        objective = ObjectiveSpec(
            objective_value=portfolio, metric=StdMetric(), direction="minimize"
        )

        # Floor on minimum return
        mean_constraint = SimpleConstraint(
            constraint_value=portfolio,
            threshold=100.0,
            direction="floor",
            metric=MeanMetric(),
            name="min_return",
        )

        opt_input = OptimizationInput(
            item_ids=["low_risk", "medium_risk", "high_risk"],
            objective=objective,
            current_shares={"low_risk": 0.33, "medium_risk": 0.33, "high_risk": 0.34},
            simple_constraints=[mean_constraint],
            share_bounds={
                "low_risk": BoundsSpec(lower=0.1, upper=0.5),
                "medium_risk": BoundsSpec(lower=0.1, upper=0.5),
                "high_risk": BoundsSpec(lower=0.1, upper=0.5),
            },
        )

        result = optimize(opt_input.preprocess())

        assert result.success
        assert result.optimal_shares is not None

        # Should allocate more to low risk asset
        assert result.optimal_shares["low_risk"] >= result.optimal_shares["high_risk"]

    def test_tail_risk_focused_allocation(self):
        """Test allocation focusing on tail risk (minimize bottom 10% losses)."""
        np.random.seed(123)
        portfolio = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar(np.random.normal(100, 15, 200)),
                "asset2": StochasticScalar(np.random.normal(110, 25, 200)),
                "asset3": StochasticScalar(np.random.normal(95, 10, 200)),
            },
        )

        # Maximize bottom 10% mean (minimize tail losses)
        objective = ObjectiveSpec(
            objective_value=portfolio,
            metric=SpreadVarMetric(lower_percentile=0.0, upper_percentile=10.0),
            direction="maximize",
        )

        # Cap on overall volatility
        risk_constraint = SimpleConstraint(
            constraint_value=portfolio,
            threshold=20.0,
            direction="cap",
            metric=StdMetric(),
            name="max_volatility",
        )

        opt_input = OptimizationInput(
            item_ids=["asset1", "asset2", "asset3"],
            objective=objective,
            current_shares={"asset1": 0.33, "asset2": 0.33, "asset3": 0.34},
            simple_constraints=[risk_constraint],
            share_bounds={
                "asset1": BoundsSpec(lower=0.0, upper=0.6),
                "asset2": BoundsSpec(lower=0.0, upper=0.6),
                "asset3": BoundsSpec(lower=0.0, upper=0.6),
            },
        )

        result = optimize(opt_input.preprocess())

        assert result.success
        assert result.optimal_shares is not None
        assert result.constraint_results[0].is_satisfied


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
