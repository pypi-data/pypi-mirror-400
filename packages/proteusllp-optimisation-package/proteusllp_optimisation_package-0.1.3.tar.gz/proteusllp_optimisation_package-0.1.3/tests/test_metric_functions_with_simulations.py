"""Test that metric calculator functions correctly operate on simulation data.

This tests the ACTUAL FUNCTIONS returned by create_metric_calculator to verify they:
1. Correctly apply weights to simulation data
2. Calculate statistics that match manual computation on weighted portfolio
3. Produce gradients consistent with the value function

The distinction from test_metric_calculations.py:
- test_metric_calculations.py: Tests the calculator produces
  reasonable results
- THIS FILE: Tests the calculator functions match ground truth
  from manual simulation computation
"""

import numpy as np
from pal import StochasticScalar
from pal.variables import ProteusVariable
from pop import MeanMetric, SpreadVarMetric, StdMetric
from pop.transforms import create_metric_calculator


class TestMeanCalculatorAgainstSimulations:
    """Verify mean calculator matches ground truth from manual computation."""

    def test_mean_matches_weighted_portfolio_mean(self):
        """Test: value_func(weights) should equal mean of (sim1 * w1 + sim2 * w2).

        This verifies the mean calculator is actually computing the portfolio mean
        correctly from the underlying simulations.
        """
        # Create simple simulation data
        sims1 = np.array([10.0, 20.0, 30.0, 40.0])
        sims2 = np.array([5.0, 10.0, 15.0, 20.0])

        pv = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar(sims1),
                "asset2": StochasticScalar(sims2),
            },
        )

        # Get calculator functions
        value_func, grad_func = create_metric_calculator(
            MeanMetric(), pv, ["asset1", "asset2"]
        )

        # Test with various weight combinations
        test_weights = [
            np.array([1.0, 0.0]),  # 100% asset1
            np.array([0.0, 1.0]),  # 100% asset2
            np.array([0.5, 0.5]),  # Equal split
            np.array([0.7, 0.3]),  # 70/30
            np.array([0.3, 0.7]),  # 30/70
        ]

        for weights in test_weights:
            # Calculate using our function
            calculated_mean = value_func(weights)

            # Calculate ground truth: mean of weighted portfolio simulations
            weighted_portfolio = sims1 * weights[0] + sims2 * weights[1]
            expected_mean = np.mean(weighted_portfolio)

            # Verify they match
            np.testing.assert_allclose(
                calculated_mean,
                expected_mean,
                rtol=1e-10,
                err_msg=f"Mean calculation failed for weights {weights}",
            )

    def test_mean_gradient_matches_individual_asset_means(self):
        """Test: grad_func should return [mean(asset1), mean(asset2), ...].

        The gradient of portfolio mean w.r.t. weight_i is just mean(asset_i).
        """
        sims1 = np.array([10.0, 20.0, 30.0, 40.0])
        sims2 = np.array([5.0, 10.0, 15.0, 20.0])

        pv = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar(sims1),
                "asset2": StochasticScalar(sims2),
            },
        )

        value_func, grad_func = create_metric_calculator(
            MeanMetric(), pv, ["asset1", "asset2"]
        )

        # Gradient should be independent of weights for linear mean
        weights = np.array([0.6, 0.4])
        gradient = grad_func(weights)

        # Ground truth: mean of each asset
        expected_gradient = np.array([np.mean(sims1), np.mean(sims2)])

        np.testing.assert_allclose(gradient, expected_gradient, rtol=1e-10)


class TestStdCalculatorAgainstSimulations:
    """Verify std calculator matches ground truth from manual simulation computation."""

    def test_std_matches_weighted_portfolio_std(self):
        """Test: value_func(weights) should equal std of (sim1 * w1 + sim2 * w2).

        This verifies the std calculator computes portfolio volatility correctly.
        """
        sims1 = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
        sims2 = np.array([5.0, 15.0, 25.0, 35.0, 45.0])

        pv = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar(sims1),
                "asset2": StochasticScalar(sims2),
            },
        )

        value_func, grad_func = create_metric_calculator(
            StdMetric(), pv, ["asset1", "asset2"]
        )

        # Test with various weights
        test_weights = [
            np.array([1.0, 0.0]),  # 100% asset1
            np.array([0.0, 1.0]),  # 100% asset2
            np.array([0.5, 0.5]),  # Equal split
            np.array([0.8, 0.2]),  # 80/20
        ]

        for weights in test_weights:
            calculated_std = value_func(weights)

            # Ground truth: std of weighted portfolio (with ddof=1)
            weighted_portfolio = sims1 * weights[0] + sims2 * weights[1]
            expected_std = np.std(weighted_portfolio, ddof=1)

            np.testing.assert_allclose(
                calculated_std,
                expected_std,
                rtol=1e-10,
                err_msg=f"Std calculation failed for weights {weights}",
            )

    def test_std_gradient_direction_increases_risk(self):
        """Test: grad_func gradient should indicate direction of increasing volatility.

        If increasing weight on asset_i increases portfolio std, gradient[i] > 0.
        This is a consistency check (not exact value matching).
        """
        # Asset1: high volatility, Asset2: low volatility
        sims1 = np.array([0.0, 50.0, 100.0])  # Very volatile
        sims2 = np.array([49.0, 50.0, 51.0])  # Low volatility

        pv = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar(sims1),
                "asset2": StochasticScalar(sims2),
            },
        )

        value_func, grad_func = create_metric_calculator(
            StdMetric(), pv, ["asset1", "asset2"]
        )

        # Equal weights as baseline
        weights = np.array([0.5, 0.5])

        # Calculate gradient
        gradient = grad_func(weights)

        # Numerical gradient check: perturb weights slightly
        epsilon = 1e-5

        # Perturb asset1 weight up
        perturbed_weights_1 = weights + np.array([epsilon, -epsilon])
        std_plus_1 = value_func(perturbed_weights_1)
        std_base = value_func(weights)

        numerical_grad_1 = (std_plus_1 - std_base) / epsilon

        # Gradient[0] should be positive (increasing asset1 weight increases risk)
        assert gradient[0] > 0, (
            "Gradient should indicate high-volatility asset increases risk"
        )

        # Sign should match numerical gradient
        assert np.sign(gradient[0]) == np.sign(numerical_grad_1), (
            "Analytical gradient sign should match numerical gradient"
        )


class TestSpreadVarCalculatorAgainstSimulations:
    """Verify SpreadVar calculator matches ground truth from manual computation."""

    def test_spreadvar_full_range_matches_mean(self):
        """Test: SpreadVar(0, 100) should equal mean of weighted portfolio.

        Full percentile range should give the same result as mean.
        """
        sims1 = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
        sims2 = np.array([5.0, 15.0, 25.0, 35.0, 45.0])

        pv = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar(sims1),
                "asset2": StochasticScalar(sims2),
            },
        )

        # SpreadVar with full range
        sv_value_func, sv_grad_func = create_metric_calculator(
            SpreadVarMetric(lower_percentile=0.0, upper_percentile=100.0),
            pv,
            ["asset1", "asset2"],
        )

        # Mean for comparison
        mean_value_func, _ = create_metric_calculator(
            MeanMetric(), pv, ["asset1", "asset2"]
        )

        weights = np.array([0.6, 0.4])

        sv_value = sv_value_func(weights)
        mean_value = mean_value_func(weights)

        np.testing.assert_allclose(sv_value, mean_value, rtol=1e-10)

    def test_spreadvar_top_tail_matches_manual_computation(self):
        """Test: SpreadVar(80, 100) equals mean of top 20% of portfolio sims.

        This verifies percentile filtering works correctly.
        """
        # Use larger sample for reliable percentile calculation
        np.random.seed(42)
        n_sims = 100
        sims1 = np.random.normal(100, 20, n_sims)
        sims2 = np.random.normal(50, 10, n_sims)

        pv = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar(sims1),
                "asset2": StochasticScalar(sims2),
            },
        )

        value_func, grad_func = create_metric_calculator(
            SpreadVarMetric(lower_percentile=80.0, upper_percentile=100.0),
            pv,
            ["asset1", "asset2"],
        )

        weights = np.array([0.7, 0.3])
        calculated_spreadvar = value_func(weights)

        # Ground truth: compute weighted portfolio, then mean of top 20%
        weighted_portfolio = sims1 * weights[0] + sims2 * weights[1]

        # Get ranks and filter top 20%
        ranks = np.argsort(np.argsort(weighted_portfolio))
        n = len(weighted_portfolio)
        lower_bound = 80.0 / 100.0 * (n - 1)
        upper_bound = 100.0 / 100.0 * (n - 1)
        mask = (ranks >= lower_bound) & (ranks <= upper_bound)

        expected_spreadvar = np.mean(weighted_portfolio[mask])

        np.testing.assert_allclose(
            calculated_spreadvar,
            expected_spreadvar,
            rtol=1e-10,
            err_msg="SpreadVar top tail calculation doesn't match manual computation",
        )

    def test_spreadvar_bottom_tail_matches_manual_computation(self):
        """Test: SpreadVar(0, 20) equals mean of bottom 20% of sims."""
        np.random.seed(43)
        n_sims = 100
        sims1 = np.random.normal(100, 20, n_sims)
        sims2 = np.random.normal(50, 10, n_sims)

        pv = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar(sims1),
                "asset2": StochasticScalar(sims2),
            },
        )

        value_func, grad_func = create_metric_calculator(
            SpreadVarMetric(lower_percentile=0.0, upper_percentile=20.0),
            pv,
            ["asset1", "asset2"],
        )

        weights = np.array([0.5, 0.5])
        calculated_spreadvar = value_func(weights)

        # Ground truth
        weighted_portfolio = sims1 * weights[0] + sims2 * weights[1]
        ranks = np.argsort(np.argsort(weighted_portfolio))
        n = len(weighted_portfolio)
        lower_bound = 0.0 / 100.0 * (n - 1)
        upper_bound = 20.0 / 100.0 * (n - 1)
        mask = (ranks >= lower_bound) & (ranks <= upper_bound)

        expected_spreadvar = np.mean(weighted_portfolio[mask])

        np.testing.assert_allclose(
            calculated_spreadvar,
            expected_spreadvar,
            rtol=1e-10,
            err_msg=(
                "SpreadVar bottom tail calculation doesn't match manual computation"
            ),
        )

    def test_spreadvar_middle_range(self):
        """Test: SpreadVar(40, 60) equals mean of middle 20% of portfolio.

        Tests percentile range that doesn't include endpoints.
        """
        np.random.seed(44)
        n_sims = 100
        sims1 = np.random.normal(100, 15, n_sims)
        sims2 = np.random.normal(80, 12, n_sims)

        pv = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar(sims1),
                "asset2": StochasticScalar(sims2),
            },
        )

        value_func, grad_func = create_metric_calculator(
            SpreadVarMetric(lower_percentile=40.0, upper_percentile=60.0),
            pv,
            ["asset1", "asset2"],
        )

        weights = np.array([0.4, 0.6])
        calculated_spreadvar = value_func(weights)

        # Ground truth
        weighted_portfolio = sims1 * weights[0] + sims2 * weights[1]
        ranks = np.argsort(np.argsort(weighted_portfolio))
        n = len(weighted_portfolio)
        lower_bound = 40.0 / 100.0 * (n - 1)
        upper_bound = 60.0 / 100.0 * (n - 1)
        mask = (ranks >= lower_bound) & (ranks <= upper_bound)

        expected_spreadvar = np.mean(weighted_portfolio[mask])

        np.testing.assert_allclose(
            calculated_spreadvar,
            expected_spreadvar,
            rtol=1e-10,
            err_msg=(
                "SpreadVar middle range calculation doesn't match manual computation"
            ),
        )


class TestGradientConsistencyWithValues:
    """Test gradients match value functions via numerical differentiation."""

    def test_mean_gradient_via_numerical_differentiation(self):
        """Verify mean gradient matches numerical derivative of value function."""
        sims1 = np.array([10.0, 20.0, 30.0, 40.0])
        sims2 = np.array([5.0, 15.0, 25.0, 35.0])

        pv = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar(sims1),
                "asset2": StochasticScalar(sims2),
            },
        )

        value_func, grad_func = create_metric_calculator(
            MeanMetric(), pv, ["asset1", "asset2"]
        )

        weights = np.array([0.6, 0.4])
        analytical_grad = grad_func(weights)

        # Numerical gradient
        epsilon = 1e-7
        numerical_grad = np.zeros(2)

        for i in range(2):
            weights_plus = weights.copy()
            weights_plus[i] += epsilon

            weights_minus = weights.copy()
            weights_minus[i] -= epsilon

            numerical_grad[i] = (
                value_func(weights_plus) - value_func(weights_minus)
            ) / (2 * epsilon)

        np.testing.assert_allclose(
            analytical_grad,
            numerical_grad,
            rtol=1e-5,
            err_msg="Mean gradient doesn't match numerical differentiation",
        )

    def test_std_gradient_via_numerical_differentiation(self):
        """Verify std gradient matches numerical derivative of value function."""
        sims1 = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
        sims2 = np.array([5.0, 15.0, 25.0, 35.0, 45.0])

        pv = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar(sims1),
                "asset2": StochasticScalar(sims2),
            },
        )

        value_func, grad_func = create_metric_calculator(
            StdMetric(), pv, ["asset1", "asset2"]
        )

        weights = np.array([0.6, 0.4])
        analytical_grad = grad_func(weights)

        # Numerical gradient
        epsilon = 1e-7
        numerical_grad = np.zeros(2)

        for i in range(2):
            weights_plus = weights.copy()
            weights_plus[i] += epsilon

            weights_minus = weights.copy()
            weights_minus[i] -= epsilon

            numerical_grad[i] = (
                value_func(weights_plus) - value_func(weights_minus)
            ) / (2 * epsilon)

        np.testing.assert_allclose(
            analytical_grad,
            numerical_grad,
            rtol=1e-5,
            atol=1e-8,
            err_msg="Std gradient doesn't match numerical differentiation",
        )

    def test_spreadvar_gradient_via_numerical_differentiation(self):
        """Verify SpreadVar gradient matches numerical derivative of value function."""
        np.random.seed(45)
        sims1 = np.random.normal(100, 20, 50)
        sims2 = np.random.normal(50, 10, 50)

        pv = ProteusVariable(
            "item",
            {
                "asset1": StochasticScalar(sims1),
                "asset2": StochasticScalar(sims2),
            },
        )

        value_func, grad_func = create_metric_calculator(
            SpreadVarMetric(lower_percentile=20.0, upper_percentile=80.0),
            pv,
            ["asset1", "asset2"],
        )

        weights = np.array([0.6, 0.4])
        analytical_grad = grad_func(weights)

        # Numerical gradient
        epsilon = 1e-6  # Larger epsilon for percentile-based calculation
        numerical_grad = np.zeros(2)

        for i in range(2):
            weights_plus = weights.copy()
            weights_plus[i] += epsilon

            weights_minus = weights.copy()
            weights_minus[i] -= epsilon

            numerical_grad[i] = (
                value_func(weights_plus) - value_func(weights_minus)
            ) / (2 * epsilon)

        # Use looser tolerance for percentile-based calculations (discontinuous)
        np.testing.assert_allclose(
            analytical_grad,
            numerical_grad,
            rtol=0.01,  # 1% relative tolerance
            atol=0.1,  # Absolute tolerance for near-zero gradients
            err_msg="SpreadVar gradient doesn't match numerical differentiation",
        )
