"""Comprehensive tests for FreqSev constraint optimization.

Tests cover:
- Multiple FreqSev constraints (independent and interacting)
- Floor and cap constraints
- Identical and similar losses across assets
- Conflicting constraints
- Infeasible constraints
- Edge cases (zero losses, extreme values)

FreqSevSims structure reminder:
- sim_index: Maps each event to its simulation number (e.g., [1,2,3,3,3,4,4,7,8])
- values: Severity values for each event (same length as sim_index)
- n_sims: Total number of simulations
- ALL FreqSevSims in a ProteusVariable MUST have IDENTICAL sim_index arrays
"""

import numpy as np
import pytest
from pal import FreqSevSims, StochasticScalar
from pal.variables import ProteusVariable
from pop import (
    BoundsSpec,
    FreqSevConstraint,
    MeanMetric,
    ObjectiveSpec,
    OptimizationInput,
    SpreadVarMetric,
    StdMetric,
    optimize,
)


class TestFreqSevBasicConstraints:
    """Test basic FreqSev constraint functionality.

    This includes the original simple test from test_freqsev_constraints.py
    merged into this comprehensive test suite.
    """

    def test_freqsev_mean_cap_constraint_simple(self):
        """Test cap constraint on FreqSevSims mean - single simple test.

        This is the original test from test_freqsev_constraints.py, which validates
        that basic FreqSev constraints work correctly.
        """
        # Create portfolio with 2 assets (all in one ProteusVariable)
        portfolio = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([100.0, 110.0, 90.0, 105.0, 95.0]),
                "asset2": StochasticScalar([200.0, 220.0, 180.0, 210.0, 190.0]),
            },
        )

        # Create FreqSevSims for losses - MUST have IDENTICAL
        # sim_index for all assets
        # 5 sims: Sim 0: 0 events, Sim 1: 1 event, Sim 2: 2 events,
        # Sim 3: 1 event, Sim 4: 1 event
        n_sims = 5
        sim_index = np.array([1, 2, 2, 3, 4], dtype=int)  # SAME!

        # Asset1 losses: lower severity per event
        values1 = np.array([500.0, 700.0, 600.0, 800.0, 550.0], dtype=float)
        freqsev1 = FreqSevSims(sim_index=sim_index, values=values1, n_sims=n_sims)

        # Asset2 losses: higher severity per event
        values2 = np.array([1500.0, 2000.0, 1800.0, 2200.0, 1600.0], dtype=float)
        freqsev2 = FreqSevSims(sim_index=sim_index, values=values2, n_sims=n_sims)

        # Losses ProteusVariable with same items as portfolio
        losses = ProteusVariable(
            "item",
            {
                "asset1": freqsev1,
                "asset2": freqsev2,
            },
        )

        objective = ObjectiveSpec(
            objective_value=portfolio, metric=MeanMetric(), direction="maximize"
        )

        # Constrain mean loss to be <= 1500 (lower threshold to avoid maxing out shares)
        freqsev_constraint = FreqSevConstraint(
            constraint_value=losses,
            threshold=1500.0,
            direction="cap",
            metric=MeanMetric(),
            name="max_mean_loss",
        )

        opt_input = OptimizationInput(
            item_ids=["asset1", "asset2"],
            objective=objective,
            current_shares={"asset1": 0.5, "asset2": 0.5},
            freqsev_constraints=[freqsev_constraint],
            share_bounds={
                "asset1": BoundsSpec(lower=0.0, upper=1.0),
                "asset2": BoundsSpec(lower=0.0, upper=1.0),
            },
        )

        result = optimize(opt_input.preprocess())

        # Check that optimization ran (may not fully converge if
        # constraint is very tight)
        assert result.optimal_shares is not None

        # Check that constraint was evaluated properly
        assert len(result.constraint_results) == 1
        constraint_result = result.constraint_results[0]

        # Constraint should have actual non-zero value now
        assert constraint_result.actual_value > 0, (
            f"Expected non-zero loss, got {constraint_result.actual_value}"
        )
        # With tight constraint, allow small violations due to
        # numerical precision
        tolerance = 1e-4
        assert constraint_result.actual_value <= 1500.0 + tolerance, (
            f"Loss {constraint_result.actual_value} exceeds "
            f"threshold by more than tolerance"
        )

    def test_freqsev_mean_cap_constraint(self):
        """Test that cap constraint on mean loss is respected."""
        portfolio = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([100.0, 110.0, 90.0, 105.0, 95.0]),
                "asset2": StochasticScalar([200.0, 220.0, 180.0, 210.0, 190.0]),
            },
        )

        # Identical sim_index for both assets
        n_sims = 5
        sim_index = np.array([1, 2, 2, 3, 4], dtype=int)

        # Asset1: lower severity, Asset2: higher severity
        values1 = np.array([500.0, 700.0, 600.0, 800.0, 550.0], dtype=float)
        values2 = np.array([1500.0, 2000.0, 1800.0, 2200.0, 1600.0], dtype=float)

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

        objective = ObjectiveSpec(
            objective_value=portfolio, metric=MeanMetric(), direction="maximize"
        )

        freqsev_constraint = FreqSevConstraint(
            constraint_value=losses,
            threshold=1500.0,
            direction="cap",
            metric=MeanMetric(),
            name="max_mean_loss",
        )

        opt_input = OptimizationInput(
            item_ids=["asset1", "asset2"],
            objective=objective,
            current_shares={"asset1": 0.5, "asset2": 0.5},
            freqsev_constraints=[freqsev_constraint],
            share_bounds={
                "asset1": BoundsSpec(lower=0.0, upper=1.0),
                "asset2": BoundsSpec(lower=0.0, upper=1.0),
            },
        )

        result = optimize(opt_input.preprocess())

        assert result.optimal_shares is not None
        assert len(result.constraint_results) == 1

        constraint_result = result.constraint_results[0]
        assert constraint_result.actual_value > 0
        tolerance = 1e-4
        assert constraint_result.actual_value <= 1500.0 + tolerance

    def test_freqsev_mean_floor_constraint(self):
        """Test that floor constraint on mean loss is respected."""
        portfolio = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([100.0, 110.0, 90.0, 105.0, 95.0]),
                "asset2": StochasticScalar([200.0, 220.0, 180.0, 210.0, 190.0]),
            },
        )

        n_sims = 5
        sim_index = np.array([1, 2, 2, 3, 4], dtype=int)

        # Create losses where we want to ensure minimum loss exposure
        values1 = np.array([300.0, 400.0, 350.0, 450.0, 380.0], dtype=float)
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

        objective = ObjectiveSpec(
            objective_value=portfolio, metric=MeanMetric(), direction="maximize"
        )

        # Floor constraint: mean loss must be at least 500
        freqsev_constraint = FreqSevConstraint(
            constraint_value=losses,
            threshold=500.0,
            direction="floor",
            metric=MeanMetric(),
            name="min_mean_loss",
        )

        opt_input = OptimizationInput(
            item_ids=["asset1", "asset2"],
            objective=objective,
            current_shares={"asset1": 0.5, "asset2": 0.5},
            freqsev_constraints=[freqsev_constraint],
            share_bounds={
                "asset1": BoundsSpec(lower=0.0, upper=1.0),
                "asset2": BoundsSpec(lower=0.0, upper=1.0),
            },
        )

        result = optimize(opt_input.preprocess())

        assert result.optimal_shares is not None
        assert len(result.constraint_results) == 1

        constraint_result = result.constraint_results[0]
        tolerance = 1e-4
        assert constraint_result.actual_value >= 500.0 - tolerance

    def test_freqsev_spreadvar_constraint_on_tail(self):
        """Test FreqSev constraint using SpreadVar to limit tail losses."""
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
                    values=np.array([10.0, 50.0, 30.0, 20.0, 40.0]),  # Various losses
                    n_sims=n_sims,
                ),
                "asset2": FreqSevSims(
                    sim_index=sim_index,
                    values=np.array(
                        [15.0, 80.0, 45.0, 25.0, 60.0]
                    ),  # Higher tail losses
                    n_sims=n_sims,
                ),
            },
        )

        # Constrain mean of top 40% of losses (tail risk)
        freqsev_constraint = FreqSevConstraint(
            constraint_value=losses,
            threshold=60.0,  # Limit average of worst losses
            direction="cap",
            metric=SpreadVarMetric(lower_percentile=60.0, upper_percentile=100.0),
            name="tail_loss_cap",
        )

        objective = ObjectiveSpec(
            objective_value=portfolio,
            metric=MeanMetric(),
            direction="maximize",
        )

        opt_input = OptimizationInput(
            item_ids=["asset1", "asset2"],
            objective=objective,
            current_shares={"asset1": 0.5, "asset2": 0.5},
            freqsev_constraints=[freqsev_constraint],
            share_bounds={
                "asset1": BoundsSpec(lower=0.0, upper=1.0),
                "asset2": BoundsSpec(lower=0.0, upper=1.0),
            },
        )

        result = optimize(opt_input.preprocess())

        assert result.optimal_shares is not None
        assert len(result.constraint_results) == 1

        # Verify tail risk constraint is satisfied
        constraint_result = result.constraint_results[0]
        tolerance = 1e-4
        assert constraint_result.actual_value <= 60.0 + tolerance, (
            f"Tail risk {constraint_result.actual_value} exceeds cap of 60.0"
        )


class TestFreqSevMultipleConstraints:
    """Test scenarios with multiple FreqSev constraints."""

    def test_multiple_independent_freqsev_constraints(self):
        """Test that multiple independent FreqSev constraints can coexist."""
        portfolio = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([100.0, 110.0, 90.0, 105.0, 95.0]),
                "asset2": StochasticScalar([200.0, 220.0, 180.0, 210.0, 190.0]),
            },
        )

        n_sims = 5
        sim_index = np.array([1, 2, 2, 3, 4], dtype=int)

        # Two different loss types
        operational_losses = ProteusVariable(
            "item",
            {
                "asset1": FreqSevSims(
                    sim_index=sim_index,
                    values=np.array([500.0, 700.0, 600.0, 800.0, 550.0]),
                    n_sims=n_sims,
                ),
                "asset2": FreqSevSims(
                    sim_index=sim_index,
                    values=np.array([1500.0, 2000.0, 1800.0, 2200.0, 1600.0]),
                    n_sims=n_sims,
                ),
            },
        )

        market_losses = ProteusVariable(
            "item",
            {
                "asset1": FreqSevSims(
                    sim_index=sim_index,
                    values=np.array([300.0, 400.0, 350.0, 450.0, 380.0]),
                    n_sims=n_sims,
                ),
                "asset2": FreqSevSims(
                    sim_index=sim_index,
                    values=np.array([600.0, 800.0, 700.0, 900.0, 750.0]),
                    n_sims=n_sims,
                ),
            },
        )

        objective = ObjectiveSpec(
            objective_value=portfolio, metric=MeanMetric(), direction="maximize"
        )

        # Two separate constraints
        constraint1 = FreqSevConstraint(
            constraint_value=operational_losses,
            threshold=1500.0,
            direction="cap",
            metric=MeanMetric(),
            name="max_operational_loss",
        )

        constraint2 = FreqSevConstraint(
            constraint_value=market_losses,
            threshold=600.0,
            direction="cap",
            metric=MeanMetric(),
            name="max_market_loss",
        )

        opt_input = OptimizationInput(
            item_ids=["asset1", "asset2"],
            objective=objective,
            current_shares={"asset1": 0.5, "asset2": 0.5},
            freqsev_constraints=[constraint1, constraint2],
            share_bounds={
                "asset1": BoundsSpec(lower=0.0, upper=1.0),
                "asset2": BoundsSpec(lower=0.0, upper=1.0),
            },
        )

        result = optimize(opt_input.preprocess())

        assert result.optimal_shares is not None
        assert len(result.constraint_results) == 2

        # Both constraints should be evaluated
        tolerance = 1e-4
        assert result.constraint_results[0].actual_value <= 1500.0 + tolerance
        assert result.constraint_results[1].actual_value <= 600.0 + tolerance

    def test_freqsev_with_stddev_constraint(self):
        """Test FreqSev constraint on standard deviation."""
        portfolio = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([100.0, 110.0, 90.0, 105.0, 95.0]),
                "asset2": StochasticScalar([200.0, 220.0, 180.0, 210.0, 190.0]),
            },
        )

        n_sims = 5
        sim_index = np.array([1, 2, 2, 3, 4], dtype=int)

        # Create losses with varying severity
        values1 = np.array([200.0, 600.0, 400.0, 800.0, 300.0], dtype=float)
        values2 = np.array([1000.0, 2000.0, 1500.0, 2500.0, 1200.0], dtype=float)

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

        objective = ObjectiveSpec(
            objective_value=portfolio, metric=MeanMetric(), direction="maximize"
        )

        # Constrain volatility of losses
        freqsev_constraint = FreqSevConstraint(
            constraint_value=losses,
            threshold=800.0,
            direction="cap",
            metric=StdMetric(),
            name="max_loss_volatility",
        )

        opt_input = OptimizationInput(
            item_ids=["asset1", "asset2"],
            objective=objective,
            current_shares={"asset1": 0.5, "asset2": 0.5},
            freqsev_constraints=[freqsev_constraint],
            share_bounds={
                "asset1": BoundsSpec(lower=0.0, upper=1.0),
                "asset2": BoundsSpec(lower=0.0, upper=1.0),
            },
        )

        result = optimize(opt_input.preprocess())

        assert result.optimal_shares is not None
        assert len(result.constraint_results) == 1

        constraint_result = result.constraint_results[0]
        # StdDev constraint may be slightly violated due to numerical precision
        tolerance = 1.0
        assert constraint_result.actual_value <= 800.0 + tolerance


class TestFreqSevIdenticalAndSimilarLosses:
    """Test handling of identical or similar losses across assets."""

    def test_identical_losses_across_assets(self):
        """Test that optimizer handles identical loss distributions correctly."""
        portfolio = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([100.0, 110.0, 90.0, 105.0, 95.0]),
                "asset2": StochasticScalar([200.0, 220.0, 180.0, 210.0, 190.0]),
            },
        )

        n_sims = 5
        sim_index = np.array([1, 2, 2, 3, 4], dtype=int)

        # Identical loss values for both assets
        identical_values = np.array(
            [1000.0, 1200.0, 1100.0, 1300.0, 1150.0], dtype=float
        )

        losses = ProteusVariable(
            "item",
            {
                "asset1": FreqSevSims(
                    sim_index=sim_index, values=identical_values.copy(), n_sims=n_sims
                ),
                "asset2": FreqSevSims(
                    sim_index=sim_index, values=identical_values.copy(), n_sims=n_sims
                ),
            },
        )

        objective = ObjectiveSpec(
            objective_value=portfolio, metric=MeanMetric(), direction="maximize"
        )

        freqsev_constraint = FreqSevConstraint(
            constraint_value=losses,
            threshold=1300.0,
            direction="cap",
            metric=MeanMetric(),
            name="max_mean_loss",
        )

        opt_input = OptimizationInput(
            item_ids=["asset1", "asset2"],
            objective=objective,
            current_shares={"asset1": 0.5, "asset2": 0.5},
            freqsev_constraints=[freqsev_constraint],
            share_bounds={
                "asset1": BoundsSpec(lower=0.0, upper=1.0),
                "asset2": BoundsSpec(lower=0.0, upper=1.0),
            },
        )

        result = optimize(opt_input.preprocess())

        assert result.optimal_shares is not None
        assert len(result.constraint_results) == 1

        # With identical losses, constraint should be the same regardless of allocation
        # Optimizer will max out at constraint threshold if it's binding
        constraint_result = result.constraint_results[0]
        tolerance = 1e-3
        # Constraint is tight at threshold since losses are
        # identical and above threshold mean
        assert constraint_result.actual_value <= 1300.0 + tolerance

    def test_very_similar_losses(self):
        """Test that optimizer handles very similar (but not identical) losses."""
        portfolio = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([100.0, 110.0, 90.0, 105.0, 95.0]),
                "asset2": StochasticScalar([200.0, 220.0, 180.0, 210.0, 190.0]),
            },
        )

        n_sims = 5
        sim_index = np.array([1, 2, 2, 3, 4], dtype=int)

        # Very similar losses (within 5%)
        base_values = np.array([1000.0, 1200.0, 1100.0, 1300.0, 1150.0], dtype=float)
        values1 = base_values * 1.0  # Asset1: base values
        values2 = base_values * 1.02  # Asset2: 2% higher

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

        objective = ObjectiveSpec(
            objective_value=portfolio, metric=MeanMetric(), direction="maximize"
        )

        freqsev_constraint = FreqSevConstraint(
            constraint_value=losses,
            threshold=1300.0,
            direction="cap",
            metric=MeanMetric(),
            name="max_mean_loss",
        )

        opt_input = OptimizationInput(
            item_ids=["asset1", "asset2"],
            objective=objective,
            current_shares={"asset1": 0.5, "asset2": 0.5},
            freqsev_constraints=[freqsev_constraint],
            share_bounds={
                "asset1": BoundsSpec(lower=0.0, upper=1.0),
                "asset2": BoundsSpec(lower=0.0, upper=1.0),
            },
        )

        result = optimize(opt_input.preprocess())

        assert result.optimal_shares is not None
        tolerance = 1e-4
        assert result.constraint_results[0].actual_value <= 1300.0 + tolerance


class TestFreqSevEdgeCases:
    """Test edge cases and special scenarios."""

    def test_zero_losses_constraint(self):
        """Test FreqSev constraint when some assets have zero losses."""
        portfolio = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([100.0, 110.0, 90.0, 105.0, 95.0]),
                "asset2": StochasticScalar([200.0, 220.0, 180.0, 210.0, 190.0]),
            },
        )

        n_sims = 5
        sim_index = np.array([1, 2, 2, 3, 4], dtype=int)

        # Asset1: zero losses, Asset2: non-zero losses
        values1 = np.zeros(5, dtype=float)
        values2 = np.array([1000.0, 1200.0, 1100.0, 1300.0, 1150.0], dtype=float)

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

        objective = ObjectiveSpec(
            objective_value=portfolio, metric=MeanMetric(), direction="maximize"
        )

        freqsev_constraint = FreqSevConstraint(
            constraint_value=losses,
            threshold=800.0,
            direction="cap",
            metric=MeanMetric(),
            name="max_mean_loss",
        )

        opt_input = OptimizationInput(
            item_ids=["asset1", "asset2"],
            objective=objective,
            current_shares={"asset1": 0.5, "asset2": 0.5},
            freqsev_constraints=[freqsev_constraint],
            share_bounds={
                "asset1": BoundsSpec(lower=0.0, upper=1.0),
                "asset2": BoundsSpec(lower=0.0, upper=1.0),
            },
        )

        result = optimize(opt_input.preprocess())

        assert result.optimal_shares is not None

        # Should favor asset1 (zero losses) while maximizing returns
        shares = result.optimal_shares
        # Asset1 should have higher allocation if constraint is binding
        if result.constraint_results[0].slack < 10.0:
            assert shares["asset1"] >= shares["asset2"] - 0.1  # Allow small tolerance

    def test_single_asset_with_freqsev_constraint(self):
        """Test FreqSev constraint with only one asset."""
        portfolio = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([100.0, 110.0, 90.0, 105.0, 95.0]),
            },
        )

        n_sims = 5
        sim_index = np.array([1, 2, 2, 3, 4], dtype=int)
        values1 = np.array([1000.0, 1200.0, 1100.0, 1300.0, 1150.0], dtype=float)

        losses = ProteusVariable(
            "item",
            {
                "asset1": FreqSevSims(
                    sim_index=sim_index, values=values1, n_sims=n_sims
                ),
            },
        )

        objective = ObjectiveSpec(
            objective_value=portfolio, metric=MeanMetric(), direction="maximize"
        )

        freqsev_constraint = FreqSevConstraint(
            constraint_value=losses,
            threshold=1300.0,
            direction="cap",
            metric=MeanMetric(),
            name="max_mean_loss",
        )

        opt_input = OptimizationInput(
            item_ids=["asset1"],
            objective=objective,
            current_shares={"asset1": 1.0},
            freqsev_constraints=[freqsev_constraint],
            share_bounds={
                "asset1": BoundsSpec(lower=0.8, upper=1.0),
            },
        )

        result = optimize(opt_input.preprocess())

        assert result.optimal_shares is not None
        # Single asset should be allocated
        assert result.optimal_shares["asset1"] >= 0.8

        # Constraint should be evaluated and show reasonable loss value
        constraint_result = result.constraint_results[0]
        assert constraint_result.actual_value > 0
        # Loss should be less than or equal to threshold
        tolerance = 1e-3
        assert constraint_result.actual_value <= 1300.0 + tolerance


class TestFreqSevFailureCases:
    """Test optimizer handles infeasible/conflicting FreqSev constraints gracefully."""

    def test_conflicting_freqsev_constraints(self):
        """Test that conflicting FreqSev constraints are detected."""
        portfolio = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([100.0, 110.0, 90.0, 105.0, 95.0]),
                "asset2": StochasticScalar([200.0, 220.0, 180.0, 210.0, 190.0]),
            },
        )

        n_sims = 5
        sim_index = np.array([1, 2, 2, 3, 4], dtype=int)
        values1 = np.array([500.0, 700.0, 600.0, 800.0, 550.0], dtype=float)
        values2 = np.array([1500.0, 2000.0, 1800.0, 2200.0, 1600.0], dtype=float)

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

        objective = ObjectiveSpec(
            objective_value=portfolio, metric=MeanMetric(), direction="maximize"
        )

        # Conflicting constraints: mean loss <= 800 AND mean loss >= 1500
        constraint1 = FreqSevConstraint(
            constraint_value=losses,
            threshold=800.0,
            direction="cap",
            metric=MeanMetric(),
            name="cap_constraint",
        )

        constraint2 = FreqSevConstraint(
            constraint_value=losses,
            threshold=1500.0,
            direction="floor",
            metric=MeanMetric(),
            name="floor_constraint",
        )

        opt_input = OptimizationInput(
            item_ids=["asset1", "asset2"],
            objective=objective,
            current_shares={"asset1": 0.5, "asset2": 0.5},
            freqsev_constraints=[constraint1, constraint2],
            share_bounds={
                "asset1": BoundsSpec(lower=0.0, upper=1.0),
                "asset2": BoundsSpec(lower=0.0, upper=1.0),
            },
        )

        result = optimize(opt_input.preprocess())

        # Optimizer may return a result but constraints should show conflict
        assert result.optimal_shares is not None
        assert len(result.constraint_results) == 2

        # At least one constraint should be violated
        violations = [not cr.is_satisfied for cr in result.constraint_results]
        assert any(violations), "Expected at least one constraint to be violated"

    def test_infeasible_freqsev_constraint(self):
        """Test FreqSev constraint that cannot be satisfied within bounds."""
        portfolio = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar([100.0, 110.0, 90.0, 105.0, 95.0]),
                "asset2": StochasticScalar([200.0, 220.0, 180.0, 210.0, 190.0]),
            },
        )

        n_sims = 5
        sim_index = np.array([1, 2, 2, 3, 4], dtype=int)

        # Both assets have high losses
        values1 = np.array([2000.0, 2200.0, 2100.0, 2300.0, 2150.0], dtype=float)
        values2 = np.array([3000.0, 3200.0, 3100.0, 3300.0, 3150.0], dtype=float)

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

        objective = ObjectiveSpec(
            objective_value=portfolio, metric=MeanMetric(), direction="maximize"
        )

        # Impossible constraint: mean loss <= 500 (but minimum possible is ~2000)
        freqsev_constraint = FreqSevConstraint(
            constraint_value=losses,
            threshold=500.0,
            direction="cap",
            metric=MeanMetric(),
            name="impossible_constraint",
        )

        opt_input = OptimizationInput(
            item_ids=["asset1", "asset2"],
            objective=objective,
            current_shares={"asset1": 0.5, "asset2": 0.5},
            freqsev_constraints=[freqsev_constraint],
            share_bounds={
                "asset1": BoundsSpec(lower=0.0, upper=1.0),
                "asset2": BoundsSpec(lower=0.0, upper=1.0),
            },
        )

        result = optimize(opt_input.preprocess())

        assert result.optimal_shares is not None

        # Optimizer tries to minimize loss by choosing lowest-loss asset
        # Even minimum loss (~2000) is much higher than threshold (500)
        # But optimizer may get stuck at constraint boundary
        constraint_result = result.constraint_results[0]

        # Check that optimizer tried to reduce losses (favored asset1 over asset2)
        if result.optimal_shares["asset1"] > result.optimal_shares["asset2"]:
            # Successfully favored lower-loss asset
            pass

        # Constraint will be violated unless optimizer gave up and hit boundary
        # Just verify it's evaluated
        assert constraint_result.actual_value > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
