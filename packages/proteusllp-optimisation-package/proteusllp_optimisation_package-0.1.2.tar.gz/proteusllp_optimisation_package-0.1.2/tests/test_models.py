"""Tests for Pydantic model validation and structure.

This module tests the basic model creation, field validation, and
serialization/deserialization without running actual optimizations.
"""

import pytest
from pal import StochasticScalar
from pal.variables import ProteusVariable
from pop import (
    BoundsSpec,
    ConstraintVariation,
    DifferenceMetric,
    EfficientFrontierInput,
    MeanMetric,
    ObjectiveSpec,
    OptimizationDirection,
    OptimizationInput,
    ProductMetric,
    RatioMetric,
    SimpleConstraint,
    SpreadVarMetric,
    StdMetric,
    SumMetric,
)
from pydantic import ValidationError


class TestBoundsSpec:
    """Test BoundsSpec model validation."""

    def test_default_bounds(self):
        """Test default infinite bounds."""
        bounds = BoundsSpec()
        assert bounds.lower == float("-inf")
        assert bounds.upper == float("inf")

    def test_custom_bounds(self):
        """Test custom bounds."""
        bounds = BoundsSpec(lower=0.0, upper=100.0)
        assert bounds.lower == 0.0
        assert bounds.upper == 100.0

    def test_bounds_validation_fails_when_lower_greater_than_upper(self):
        """Test that lower > upper raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            BoundsSpec(lower=100.0, upper=50.0)
        assert "Lower bound" in str(exc_info.value)
        assert "must be <=" in str(exc_info.value)

    def test_bounds_equal_is_valid(self):
        """Test that lower == upper is allowed."""
        bounds = BoundsSpec(lower=50.0, upper=50.0)
        assert bounds.lower == 50.0
        assert bounds.upper == 50.0

    def test_bounds_frozen(self):
        """Test that BoundsSpec is immutable."""
        bounds = BoundsSpec(lower=0.0, upper=100.0)
        with pytest.raises(ValidationError):
            bounds.lower = 10.0


class TestMetricModels:
    """Test metric model creation."""

    def test_mean_metric_creation(self):
        """Test MeanMetric can be created."""
        metric = MeanMetric()
        assert metric is not None

    def test_std_metric_creation(self):
        """Test StdMetric can be created."""
        metric = StdMetric()
        assert metric is not None

    def test_spreadvar_metric_creation(self):
        """Test SpreadVarMetric with default percentiles."""
        metric = SpreadVarMetric()
        assert metric.lower_percentile == 0.0
        assert metric.upper_percentile == 100.0

    def test_spreadvar_metric_custom_percentiles(self):
        """Test SpreadVarMetric with custom percentiles."""
        metric = SpreadVarMetric(lower_percentile=95.0, upper_percentile=99.0)
        assert metric.lower_percentile == 95.0
        assert metric.upper_percentile == 99.0

    def test_spreadvar_metric_validation_lower_greater_than_upper(self):
        """Test that SpreadVarMetric validates lower < upper."""
        with pytest.raises(ValidationError) as exc_info:
            SpreadVarMetric(lower_percentile=99.0, upper_percentile=90.0)
        assert (
            "upper" in str(exc_info.value).lower()
            or "greater" in str(exc_info.value).lower()
        )

    def test_spreadvar_metric_validation_out_of_range(self):
        """Test that SpreadVarMetric validates percentiles are in [0, 100]."""
        with pytest.raises(ValidationError):
            SpreadVarMetric(lower_percentile=-5.0, upper_percentile=95.0)
        with pytest.raises(ValidationError):
            SpreadVarMetric(lower_percentile=5.0, upper_percentile=105.0)

    def test_spreadvar_metric_equal_percentiles_fails(self):
        """Test that SpreadVarMetric requires upper > lower (not equal)."""
        with pytest.raises(ValidationError) as exc_info:
            SpreadVarMetric(lower_percentile=95.0, upper_percentile=95.0)
        assert "greater" in str(exc_info.value).lower()

    def test_spreadvar_metric_frozen(self):
        """Test that SpreadVarMetric is immutable."""
        metric = SpreadVarMetric(lower_percentile=90.0, upper_percentile=100.0)
        with pytest.raises(ValidationError):
            metric.lower_percentile = 85.0  # type: ignore

    def test_ratio_metric_creation(self):
        """Test RatioMetric with nested metrics."""
        numerator = MeanMetric()
        denominator = StdMetric()
        metric = RatioMetric(numerator=numerator, denominator=denominator)
        assert metric.numerator == numerator
        assert metric.denominator == denominator

    def test_product_metric_creation(self):
        """Test ProductMetric with nested metrics."""
        factor1 = MeanMetric()
        factor2 = StdMetric()
        metric = ProductMetric(factor1=factor1, factor2=factor2)
        assert metric.factor1 == factor1
        assert metric.factor2 == factor2

    def test_sum_metric_creation(self):
        """Test SumMetric with nested metrics."""
        metric1 = MeanMetric()
        metric2 = StdMetric()
        metric = SumMetric(metric1=metric1, metric2=metric2)
        assert metric.metric1 == metric1
        assert metric.metric2 == metric2

    def test_difference_metric_creation(self):
        """Test DifferenceMetric with nested metrics."""
        metric1 = MeanMetric()
        metric2 = StdMetric()
        metric = DifferenceMetric(metric1=metric1, metric2=metric2)
        assert metric.metric1 == metric1
        assert metric.metric2 == metric2

    def test_nested_composite_metrics(self):
        """Test deeply nested composite metrics."""
        mean = MeanMetric()
        std = StdMetric()
        ratio = RatioMetric(numerator=mean, denominator=std)
        product = ProductMetric(factor1=ratio, factor2=mean)
        assert product.factor1 == ratio
        assert product.factor2 == mean

    def test_metrics_frozen(self):
        """Test that metric models are immutable."""
        metric = MeanMetric()
        with pytest.raises(ValidationError):
            metric.some_field = "value"  # type: ignore


class TestConstraintVariation:
    """Test ConstraintVariation model for efficient frontier."""

    def test_valid_simple_constraint_variation(self):
        """Test valid simple constraint variation."""
        variation = ConstraintVariation(
            constraint_type="simple",
            constraint_name="max_loss",
            min_threshold=10.0,
            max_threshold=20.0,
        )
        assert variation.constraint_type == "simple"
        assert variation.constraint_name == "max_loss"
        assert variation.min_threshold == 10.0
        assert variation.max_threshold == 20.0

    def test_valid_freqsev_constraint_variation(self):
        """Test valid freqsev constraint variation."""
        variation = ConstraintVariation(
            constraint_type="freqsev",
            constraint_name="max_frequency",
            min_threshold=5.0,
            max_threshold=15.0,
        )
        assert variation.constraint_type == "freqsev"
        assert variation.constraint_name == "max_frequency"

    def test_threshold_validation_fails_when_min_greater_than_max(self):
        """Test that min_threshold > max_threshold raises error."""
        with pytest.raises(ValidationError) as exc_info:
            ConstraintVariation(
                constraint_type="simple",
                constraint_name="test",
                min_threshold=20.0,
                max_threshold=10.0,
            )
        assert "must be less than" in str(exc_info.value)

    def test_threshold_validation_fails_when_equal(self):
        """Test that min_threshold == max_threshold raises error."""
        with pytest.raises(ValidationError) as exc_info:
            ConstraintVariation(
                constraint_type="simple",
                constraint_name="test",
                min_threshold=10.0,
                max_threshold=10.0,
            )
        assert "must be less than" in str(exc_info.value)

    def test_invalid_constraint_type(self):
        """Test that invalid constraint_type raises error."""
        with pytest.raises(ValidationError) as exc_info:
            ConstraintVariation(
                constraint_type="invalid",  # type: ignore
                constraint_name="test",
                min_threshold=10.0,
                max_threshold=20.0,
            )
        assert "constraint_type" in str(exc_info.value).lower()

    def test_constraint_variation_frozen(self):
        """Test that ConstraintVariation is immutable."""
        variation = ConstraintVariation(
            constraint_type="simple",
            constraint_name="test",
            min_threshold=10.0,
            max_threshold=20.0,
        )
        with pytest.raises(ValidationError):
            variation.min_threshold = 15.0  # type: ignore


class TestOptimizationDirection:
    """Test OptimizationDirection enum."""

    def test_optimization_directions_exist(self):
        """Test that optimization direction constants exist."""
        assert hasattr(OptimizationDirection, "MAXIMIZE")
        assert hasattr(OptimizationDirection, "MINIMIZE")

    def test_direction_values(self):
        """Test direction string values."""
        assert OptimizationDirection.MAXIMIZE.value == "maximize"
        assert OptimizationDirection.MINIMIZE.value == "minimize"


class TestOptimizationInput:
    """Test OptimizationInput model validation."""

    def test_minimal_optimization_input(self):
        """Test creating minimal OptimizationInput with required fields."""
        # Create simple PAL variables
        pv = ProteusVariable(
            "item",
            {
                "item1": StochasticScalar([1.0, 2.0, 3.0]),
                "item2": StochasticScalar([2.0, 3.0, 4.0]),
            },
        )

        objective = ObjectiveSpec(
            objective_value=pv, metric=MeanMetric(), direction="maximize"
        )

        opt_input = OptimizationInput(item_ids=["item1", "item2"], objective=objective)

        assert opt_input.item_ids == ["item1", "item2"]
        assert opt_input.objective == objective
        assert opt_input.simple_constraints == []
        assert opt_input.freqsev_constraints == []
        assert opt_input.is_preprocessed is False

    def test_duplicate_item_ids_fails(self):
        """Test that duplicate item_ids raise validation error."""
        pv = ProteusVariable(
            "item",
            {
                "item1": StochasticScalar([1.0, 2.0, 3.0]),
            },
        )

        objective = ObjectiveSpec(
            objective_value=pv, metric=MeanMetric(), direction="maximize"
        )

        with pytest.raises(ValidationError) as exc_info:
            OptimizationInput(
                item_ids=["item1", "item1"], objective=objective
            )  # Duplicate
        assert "Duplicate item_ids" in str(exc_info.value)

    def test_simple_constraint_with_name(self):
        """Test SimpleConstraint can have optional name."""
        pv = ProteusVariable(
            "item",
            {
                "item1": StochasticScalar([1.0, 2.0, 3.0]),
                "item2": StochasticScalar([2.0, 3.0, 4.0]),
            },
        )

        constraint = SimpleConstraint(
            constraint_value=pv,
            threshold=100.0,
            direction="cap",
            metric=MeanMetric(),
            name="max_loss",  # Named constraint
        )

        assert constraint.name == "max_loss"
        assert constraint.threshold == 100.0


class TestEfficientFrontierInput:
    """Test EfficientFrontierInput model validation."""

    def test_valid_efficient_frontier_input(self):
        """Test creating valid EfficientFrontierInput."""
        # Create base optimization
        pv = ProteusVariable(
            "item",
            {
                "item1": StochasticScalar([1.0, 2.0, 3.0]),
                "item2": StochasticScalar([2.0, 3.0, 4.0]),
            },
        )

        objective = ObjectiveSpec(
            objective_value=pv, metric=MeanMetric(), direction="maximize"
        )

        constraint = SimpleConstraint(
            constraint_value=pv,
            threshold=100.0,
            direction="cap",
            metric=StdMetric(),
            name="max_risk",
        )

        opt_input = OptimizationInput(
            item_ids=["item1", "item2"],
            objective=objective,
            simple_constraints=[constraint],
        )

        # Create frontier input
        frontier_input = EfficientFrontierInput(
            base_optimization=opt_input,
            constraint_variations=[
                ConstraintVariation(
                    constraint_type="simple",
                    constraint_name="max_risk",
                    min_threshold=50.0,
                    max_threshold=150.0,
                )
            ],
            n_points=10,
        )

        assert frontier_input.n_points == 10
        assert len(frontier_input.constraint_variations) == 1

    def test_constraint_name_not_found_fails(self):
        """Test that referencing non-existent constraint name fails."""
        pv = ProteusVariable(
            "item",
            {
                "item1": StochasticScalar([1.0, 2.0, 3.0]),
            },
        )

        objective = ObjectiveSpec(
            objective_value=pv, metric=MeanMetric(), direction="maximize"
        )

        constraint = SimpleConstraint(
            constraint_value=pv,
            threshold=100.0,
            direction="cap",
            metric=StdMetric(),
            name="max_risk",
        )

        opt_input = OptimizationInput(
            item_ids=["item1"], objective=objective, simple_constraints=[constraint]
        )

        with pytest.raises(ValidationError) as exc_info:
            EfficientFrontierInput(
                base_optimization=opt_input,
                constraint_variations=[
                    ConstraintVariation(
                        constraint_type="simple",
                        constraint_name="nonexistent",  # Wrong name
                        min_threshold=50.0,
                        max_threshold=150.0,
                    )
                ],
                n_points=10,
            )
        assert "not found" in str(exc_info.value)

    def test_unnamed_constraint_cannot_be_referenced(self):
        """Test that unnamed constraints cannot be used in frontier."""
        pv = ProteusVariable(
            "item",
            {
                "item1": StochasticScalar([1.0, 2.0, 3.0]),
            },
        )

        objective = ObjectiveSpec(
            objective_value=pv, metric=MeanMetric(), direction="maximize"
        )

        constraint = SimpleConstraint(
            constraint_value=pv,
            threshold=100.0,
            direction="cap",
            metric=StdMetric(),
            # No name provided
        )

        opt_input = OptimizationInput(
            item_ids=["item1"], objective=objective, simple_constraints=[constraint]
        )

        with pytest.raises(ValidationError) as exc_info:
            EfficientFrontierInput(
                base_optimization=opt_input,
                constraint_variations=[
                    ConstraintVariation(
                        constraint_type="simple",
                        constraint_name="some_name",
                        min_threshold=50.0,
                        max_threshold=150.0,
                    )
                ],
                n_points=10,
            )
        assert "not found" in str(exc_info.value)

    def test_duplicate_constraint_variations_fails(self):
        """Test that duplicate constraint variations fail."""
        pv = ProteusVariable(
            "item",
            {
                "item1": StochasticScalar([1.0, 2.0, 3.0]),
            },
        )

        objective = ObjectiveSpec(
            objective_value=pv, metric=MeanMetric(), direction="maximize"
        )

        constraint = SimpleConstraint(
            constraint_value=pv,
            threshold=100.0,
            direction="cap",
            metric=StdMetric(),
            name="max_risk",
        )

        opt_input = OptimizationInput(
            item_ids=["item1"], objective=objective, simple_constraints=[constraint]
        )

        with pytest.raises(ValidationError) as exc_info:
            EfficientFrontierInput(
                base_optimization=opt_input,
                constraint_variations=[
                    ConstraintVariation(
                        constraint_type="simple",
                        constraint_name="max_risk",
                        min_threshold=50.0,
                        max_threshold=150.0,
                    ),
                    ConstraintVariation(
                        constraint_type="simple",
                        constraint_name="max_risk",  # Duplicate
                        min_threshold=60.0,
                        max_threshold=160.0,
                    ),
                ],
                n_points=10,
            )
        assert "Duplicate" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
