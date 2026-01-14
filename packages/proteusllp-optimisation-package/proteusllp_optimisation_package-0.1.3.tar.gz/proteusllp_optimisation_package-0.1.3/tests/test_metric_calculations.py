"""Tests for metric calculation correctness.

Validates that Mean, Std, and SpreadVar metrics:
- Calculate values correctly
- Compute gradients correctly
- Work with ProteusVariable and optimizer framework
"""

import numpy as np
import pytest
from pal import StochasticScalar
from pal.variables import ProteusVariable
from pop import MeanMetric, SpreadVarMetric, StdMetric
from pop.transforms import create_metric_calculator


class TestMeanMetricCalculations:
    """Test Mean metric value and gradient calculation."""

    def test_mean_value_single_asset(self):
        """Test mean calculation with single asset."""
        pv = ProteusVariable(
            "item",
            {
                "item1": StochasticScalar([1.0, 2.0, 3.0, 4.0, 5.0]),
            },
        )

        metric = MeanMetric()
        value_func, grad_func = create_metric_calculator(metric, pv, ["item1"])

        shares = np.array([1.0])
        value = value_func(shares)

        expected = 3.0  # mean of [1,2,3,4,5]
        np.testing.assert_allclose(value, expected)

    def test_mean_value_multiple_assets(self):
        """Test mean calculation with multiple assets."""
        pv = ProteusVariable(
            "item",
            {
                "item1": StochasticScalar([1.0, 2.0, 3.0, 4.0, 5.0]),
                "item2": StochasticScalar([2.0, 3.0, 4.0, 5.0, 6.0]),
            },
        )

        metric = MeanMetric()
        value_func, grad_func = create_metric_calculator(metric, pv, ["item1", "item2"])

        # Equal weights: 50% each
        shares = np.array([0.5, 0.5])
        value = value_func(shares)

        # item1 mean=3, item2 mean=4, weighted: 0.5*3 + 0.5*4 = 3.5
        expected = 3.5
        np.testing.assert_allclose(value, expected)

    def test_mean_gradient(self):
        """Test mean gradient calculation."""
        pv = ProteusVariable(
            "item",
            {
                "item1": StochasticScalar([1.0, 2.0, 3.0]),
                "item2": StochasticScalar([4.0, 5.0, 6.0]),
            },
        )

        metric = MeanMetric()
        value_func, grad_func = create_metric_calculator(metric, pv, ["item1", "item2"])

        shares = np.array([0.5, 0.5])
        gradient = grad_func(shares)

        # Gradient of mean should equal the mean of each asset
        # item1 mean=2, item2 mean=5
        expected = np.array([2.0, 5.0])
        np.testing.assert_allclose(gradient, expected)

    def test_mean_with_different_weights(self):
        """Test mean calculation with non-equal weights."""
        pv = ProteusVariable(
            "item",
            {
                "item1": StochasticScalar([10.0, 20.0]),
                "item2": StochasticScalar([30.0, 40.0]),
            },
        )

        metric = MeanMetric()
        value_func, grad_func = create_metric_calculator(metric, pv, ["item1", "item2"])

        # 70% item1, 30% item2
        shares = np.array([0.7, 0.3])
        value = value_func(shares)

        # item1 mean=15, item2 mean=35, weighted: 0.7*15 + 0.3*35 = 10.5 + 10.5 = 21
        expected = 21.0
        np.testing.assert_allclose(value, expected)


class TestStdMetricCalculations:
    """Test Standard Deviation metric value and gradient calculation."""

    def test_std_value_single_asset(self):
        """Test std calculation with single asset."""
        pv = ProteusVariable(
            "item",
            {
                "item1": StochasticScalar([1.0, 2.0, 3.0, 4.0, 5.0]),
            },
        )

        metric = StdMetric()
        value_func, grad_func = create_metric_calculator(metric, pv, ["item1"])

        shares = np.array([1.0])
        value = value_func(shares)

        expected = np.std([1.0, 2.0, 3.0, 4.0, 5.0], ddof=1)
        np.testing.assert_allclose(value, expected)

    def test_std_value_multiple_assets(self):
        """Test std calculation with multiple assets."""
        pv = ProteusVariable(
            "item",
            {
                "item1": StochasticScalar([1.0, 2.0, 3.0]),
                "item2": StochasticScalar([4.0, 5.0, 6.0]),
            },
        )

        metric = StdMetric()
        value_func, grad_func = create_metric_calculator(metric, pv, ["item1", "item2"])

        # Equal weights: 50% each
        shares = np.array([0.5, 0.5])
        value = value_func(shares)

        # Combined portfolio: [2.5, 3.5, 4.5]
        expected = np.std([2.5, 3.5, 4.5], ddof=1)
        np.testing.assert_allclose(value, expected)

    def test_std_gradient_exists(self):
        """Test that std gradient can be computed."""
        pv = ProteusVariable(
            "item",
            {
                "item1": StochasticScalar([1.0, 2.0, 3.0, 4.0, 5.0]),
                "item2": StochasticScalar([2.0, 3.0, 4.0, 5.0, 6.0]),
            },
        )

        metric = StdMetric()
        value_func, grad_func = create_metric_calculator(metric, pv, ["item1", "item2"])

        shares = np.array([0.5, 0.5])
        gradient = grad_func(shares)

        # Gradient should exist and have correct shape
        assert gradient is not None
        assert gradient.shape == (2,)

    def test_std_zero_with_constant_values(self):
        """Test that std is zero when all values are identical."""
        pv = ProteusVariable(
            "item",
            {
                "item1": StochasticScalar([5.0, 5.0, 5.0]),
            },
        )

        metric = StdMetric()
        value_func, grad_func = create_metric_calculator(metric, pv, ["item1"])

        shares = np.array([1.0])
        value = value_func(shares)

        # All values same, std should be 0
        np.testing.assert_allclose(value, 0.0, atol=1e-10)


class TestSpreadVarMetricCalculations:
    """Test SpreadVar metric value and gradient calculation."""

    def test_spreadvar_full_range_equals_mean(self):
        """Test SpreadVar with 0-100 percentile (should equal mean)."""
        pv = ProteusVariable(
            "item",
            {
                "item1": StochasticScalar([1.0, 2.0, 3.0, 4.0, 5.0]),
            },
        )

        metric = SpreadVarMetric(lower_percentile=0.0, upper_percentile=100.0)
        value_func, grad_func = create_metric_calculator(metric, pv, ["item1"])

        shares = np.array([1.0])
        value = value_func(shares)

        # Full range should equal mean
        expected = 3.0
        np.testing.assert_allclose(value, expected)

    def test_spreadvar_top_tail(self):
        """Test SpreadVar selecting top tail (high percentiles)."""
        pv = ProteusVariable(
            "item",
            {
                "item1": StochasticScalar(
                    [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
                ),
            },
        )

        metric = SpreadVarMetric(lower_percentile=80.0, upper_percentile=100.0)
        value_func, grad_func = create_metric_calculator(metric, pv, ["item1"])

        shares = np.array([1.0])
        value = value_func(shares)

        # Top 20% should be higher than overall mean
        overall_mean = 5.5
        assert value > overall_mean

    def test_spreadvar_bottom_tail(self):
        """Test SpreadVar selecting bottom tail (low percentiles)."""
        pv = ProteusVariable(
            "item",
            {
                "item1": StochasticScalar(
                    [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
                ),
            },
        )

        metric = SpreadVarMetric(lower_percentile=0.0, upper_percentile=20.0)
        value_func, grad_func = create_metric_calculator(metric, pv, ["item1"])

        shares = np.array([1.0])
        value = value_func(shares)

        # Bottom 20% should be lower than overall mean
        overall_mean = 5.5
        assert value < overall_mean

    def test_spreadvar_multiple_assets(self):
        """Test SpreadVar with multiple assets."""
        pv = ProteusVariable(
            "item",
            {
                "item1": StochasticScalar([1.0, 2.0, 3.0, 4.0, 5.0]),
                "item2": StochasticScalar([2.0, 3.0, 4.0, 5.0, 6.0]),
            },
        )

        metric = SpreadVarMetric(lower_percentile=60.0, upper_percentile=100.0)
        value_func, grad_func = create_metric_calculator(metric, pv, ["item1", "item2"])

        shares = np.array([0.5, 0.5])
        value = value_func(shares)

        # Should compute successfully
        assert value > 0

    def test_spreadvar_gradient_exists(self):
        """Test that SpreadVar gradient can be computed."""
        pv = ProteusVariable(
            "item",
            {
                "item1": StochasticScalar([1.0, 2.0, 3.0, 4.0, 5.0]),
                "item2": StochasticScalar([2.0, 3.0, 4.0, 5.0, 6.0]),
            },
        )

        metric = SpreadVarMetric(lower_percentile=90.0, upper_percentile=100.0)
        value_func, grad_func = create_metric_calculator(metric, pv, ["item1", "item2"])

        shares = np.array([0.5, 0.5])
        gradient = grad_func(shares)

        # Gradient should exist and have correct shape
        assert gradient is not None
        assert gradient.shape == (2,)

    def test_spreadvar_gradient_direction(self):
        """Test that SpreadVar gradient points in sensible direction."""
        # item2 has consistently higher values
        pv = ProteusVariable(
            "item",
            {
                "item1": StochasticScalar([1.0, 2.0, 3.0, 4.0, 5.0]),
                "item2": StochasticScalar([10.0, 11.0, 12.0, 13.0, 14.0]),
            },
        )

        metric = SpreadVarMetric(lower_percentile=80.0, upper_percentile=100.0)
        value_func, grad_func = create_metric_calculator(metric, pv, ["item1", "item2"])

        shares = np.array([0.5, 0.5])
        gradient = grad_func(shares)

        # item2 has higher values in tail, so gradient[1] should be > gradient[0]
        assert gradient[1] > gradient[0]


class TestMetricEdgeCases:
    """Test edge cases for all metrics."""

    def test_metrics_with_negative_values(self):
        """Test that all metrics handle negative values correctly."""
        pv = ProteusVariable(
            "item",
            {
                "item1": StochasticScalar([-5.0, -3.0, -1.0, 1.0, 3.0]),
            },
        )

        # Mean
        mean_value_func, grad_func = create_metric_calculator(
            MeanMetric(), pv, ["item1"]
        )
        mean_value = mean_value_func(np.array([1.0]))
        expected_mean = np.mean([-5.0, -3.0, -1.0, 1.0, 3.0])
        np.testing.assert_allclose(mean_value, expected_mean)

        # Std
        std_value_func, grad_func = create_metric_calculator(StdMetric(), pv, ["item1"])
        std_value = std_value_func(np.array([1.0]))
        expected_std = np.std([-5.0, -3.0, -1.0, 1.0, 3.0], ddof=1)
        np.testing.assert_allclose(std_value, expected_std)

        # SpreadVar
        sv_metric = SpreadVarMetric(lower_percentile=0.0, upper_percentile=100.0)
        sv_value_func, grad_func = create_metric_calculator(sv_metric, pv, ["item1"])
        sv_value = sv_value_func(np.array([1.0]))
        np.testing.assert_allclose(sv_value, expected_mean)

    def test_metrics_with_single_simulation(self):
        """Test metrics with only one simulation."""
        pv = ProteusVariable(
            "item",
            {
                "item1": StochasticScalar([5.0]),
            },
        )

        # Mean
        mean_value_func, grad_func = create_metric_calculator(
            MeanMetric(), pv, ["item1"]
        )
        mean_value = mean_value_func(np.array([1.0]))
        np.testing.assert_allclose(mean_value, 5.0)

        # Std with single simulation should be NaN (ddof=1 with n=1 is undefined)
        std_value_func, grad_func = create_metric_calculator(StdMetric(), pv, ["item1"])
        std_value = std_value_func(np.array([1.0]))
        # With ddof=1 and n=1, standard deviation is mathematically undefined
        assert np.isnan(std_value), (
            "Standard deviation with single simulation should be NaN"
        )

        # SpreadVar
        sv_metric = SpreadVarMetric(lower_percentile=0.0, upper_percentile=100.0)
        sv_value_func, grad_func = create_metric_calculator(sv_metric, pv, ["item1"])
        sv_value = sv_value_func(np.array([1.0]))
        np.testing.assert_allclose(sv_value, 5.0)

    def test_metrics_with_zero_shares(self):
        """Test metrics when all shares are zero (degenerate case)."""
        pv = ProteusVariable(
            "item",
            {
                "item1": StochasticScalar([1.0, 2.0, 3.0]),
                "item2": StochasticScalar([4.0, 5.0, 6.0]),
            },
        )

        shares = np.array([0.0, 0.0])

        # Mean should be zero
        mean_value_func, grad_func = create_metric_calculator(
            MeanMetric(), pv, ["item1", "item2"]
        )
        mean_value = mean_value_func(shares)
        np.testing.assert_allclose(mean_value, 0.0)

        # Std should be zero (no variation)
        std_value_func, grad_func = create_metric_calculator(
            StdMetric(), pv, ["item1", "item2"]
        )
        std_value = std_value_func(shares)
        np.testing.assert_allclose(std_value, 0.0, atol=1e-10)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
