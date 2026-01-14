"""Pydantic models for the generic optimization API.

This module defines the core data models using Pydantic for validation,
serialization, and type safety. These models replace the dataclass-based
approach with comprehensive field validation and automatic error handling.

Key Features:
- Automatic validation with clear error messages
- Field constraints (ranges, lengths) declared in model definitions
- Type coercion (string→float, enum validation) built-in
- JSON serialization for debugging and storage
- Self-documenting models with field descriptions
"""

from typing import Any, Literal

import numpy as np
from pal import FreqSevSims, StochasticScalar  # type: ignore

# Import PAL for stochastic variables
from pal.variables import ProteusVariable  # type: ignore
from pydantic import BaseModel, Field, PrivateAttr, field_validator, model_validator

# Import configuration constants
from .config import VALID_CONSTRAINT_DIRECTIONS, VALID_DIRECTIONS

# ============================================================================
# METRIC MODELS - The 3 Core Metric Types
# ============================================================================


class MeanMetric(BaseModel):
    """Mean metric - expected value."""

    type: str = Field(default="mean", description="Metric type")

    class Config:
        """Pydantic configuration."""

        frozen = True


class StdMetric(BaseModel):
    """Standard deviation metric - volatility/risk."""

    type: str = Field(default="std", description="Metric type")

    class Config:
        """Pydantic configuration."""

        frozen = True


class SpreadVarMetric(BaseModel):
    """Spread VaR metric - average between two percentiles."""

    type: str = Field(default="spread_var", description="Metric type")
    lower_percentile: float = Field(default=0.0, description="Lower percentile (0-100)")
    upper_percentile: float = Field(
        default=100.0, description="Upper percentile (0-100)"
    )

    @field_validator("lower_percentile", "upper_percentile")
    @classmethod
    def validate_percentiles(cls, v: float) -> float:
        """Validate that percentiles are in [0, 100] range."""
        if not (0 <= v <= 100):
            raise ValueError(f"Percentiles must be between 0-100, got {v}")
        return v

    @field_validator("upper_percentile")
    @classmethod
    def validate_range(cls, v: float, info: Any) -> float:
        """Validate that upper_percentile > lower_percentile."""
        # Only validate range if lower_percentile is available and valid
        if "lower_percentile" in info.data:
            lower = info.data["lower_percentile"]
            if v <= lower:
                raise ValueError(
                    f"Upper percentile ({v}) must be greater than lower ({lower})"
                )
        return v

    class Config:
        """Pydantic configuration."""

        frozen = True


class RatioMetric(BaseModel):
    """Ratio of two metrics on the same variable.

    Example: mean/std for Sharpe-like ratio.
    """

    type: str = Field(default="ratio", description="Metric type")
    numerator: "Metric" = Field(description="Numerator metric")
    denominator: "Metric" = Field(description="Denominator metric")

    class Config:
        """Pydantic configuration."""

        frozen = True


class ProductMetric(BaseModel):
    """Product of two metrics on the same variable."""

    type: str = Field(default="product", description="Metric type")
    factor1: "Metric" = Field(description="First factor metric")
    factor2: "Metric" = Field(description="Second factor metric")

    class Config:
        """Pydantic configuration."""

        frozen = True


class SumMetric(BaseModel):
    """Sum of two metrics on the same variable."""

    type: str = Field(default="sum", description="Metric type")
    metric1: "Metric" = Field(description="First metric to sum")
    metric2: "Metric" = Field(description="Second metric to sum")

    class Config:
        """Pydantic configuration."""

        frozen = True


class DifferenceMetric(BaseModel):
    """Difference of two metrics on the same variable.

    Example: spreadvar - mean for deviation.
    """

    type: str = Field(default="difference", description="Metric type")
    metric1: "Metric" = Field(description="Metric to subtract from")
    metric2: "Metric" = Field(description="Metric to subtract")

    class Config:
        """Pydantic configuration."""

        frozen = True


# Union type for all metrics (including composite metrics)
Metric = (
    MeanMetric
    | StdMetric
    | SpreadVarMetric
    | RatioMetric
    | ProductMetric
    | SumMetric
    | DifferenceMetric
)


# ============================================================================
# BOUNDS MODEL
# ============================================================================


class BoundsSpec(BaseModel):
    """Bounds specification with automatic defaults."""

    lower: float = Field(default=-np.inf, description="Lower bound")
    upper: float = Field(default=np.inf, description="Upper bound")

    class Config:
        """Pydantic configuration."""

        frozen = True

    @model_validator(mode="after")
    def validate_bounds_order(self):
        """Validate lower <= upper."""
        if self.lower > self.upper:
            raise ValueError(
                f"Lower bound ({self.lower}) must be <= upper bound ({self.upper})"
            )
        return self


# ============================================================================
# OPTIMIZATION MODELS
# ============================================================================


class ObjectiveSpec(BaseModel):
    """Optimization objectives using PAL ProteusVariable.

    Maintains item-level structure with ProteusVariable containing
    StochasticScalar data. Automatically converts other PAL data
    types to StochasticScalar if needed.
    """

    objective_value: ProteusVariable = Field(
        ...,
        description=(
            "ProteusVariable with StochasticScalar data for each "
            "item (auto-converted if needed)"
        ),
    )

    direction: str = Field(..., description="Optimization direction")
    metric: Metric = Field(..., description="Metric specification")

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True  # For PAL objects
        validate_assignment = True

    @field_validator("objective_value", mode="before")
    @classmethod
    def convert_proteus_to_scalar(cls, v: Any) -> ProteusVariable:
        """Convert ProteusVariable to ensure all items contain StochasticScalar data."""
        if isinstance(v, ProteusVariable):
            # Check and convert internal data to StochasticScalar if needed
            converted_values = {}
            conversion_needed = False

            for item_id, item_data in v.values.items():  # type: ignore
                if isinstance(item_data, StochasticScalar):
                    # Already StochasticScalar - keep as-is
                    converted_values[item_id] = item_data
                elif isinstance(item_data, FreqSevSims):
                    # Convert FreqSevSims to StochasticScalar using .aggregate()
                    conversion_needed = True
                    converted_values[item_id] = item_data.aggregate()  # type: ignore
                elif isinstance(item_data, ProteusVariable):
                    # Convert ProteusVariable to StochasticScalar using .sum()
                    conversion_needed = True
                    converted_values[item_id] = item_data.sum()  # type: ignore
                else:
                    # Unknown type - raise error instead of conversion
                    # type: ignore
                    type_name = type(item_data).__name__
                    raise ValueError(
                        f"Unknown data type for item '{item_id}': "
                        f"{type_name}. Expected StochasticScalar, "
                        f"FreqSevSims, or ProteusVariable."
                    )

            # Create new ProteusVariable with converted data
            # if conversions occurred
            if conversion_needed:
                return ProteusVariable(v.dim_name, converted_values)  # type: ignore

            return v  # No conversions needed
        else:
            raise ValueError(f"Expected ProteusVariable, got {type(v)}")

    @field_validator("direction")
    @classmethod
    def validate_direction(cls, v: str) -> str:  # type: ignore
        """Validate optimization direction."""
        if v not in VALID_DIRECTIONS:
            raise ValueError(f"Direction must be one of {VALID_DIRECTIONS}, got '{v}'")
        return v  # type: ignore


class SimpleConstraint(BaseModel):
    """Simple constraints using PAL ProteusVariable.

    Maintains item-level structure with ProteusVariable containing
    StochasticScalar data. Automatically converts other PAL data
    types to StochasticScalar if needed.
    """

    constraint_value: ProteusVariable = Field(
        ...,
        description=(
            "ProteusVariable with StochasticScalar data for each "
            "item (auto-converted if needed)"
        ),
    )

    threshold: float = Field(..., description="Constraint threshold value")
    direction: str = Field(..., description="Constraint direction")
    metric: Metric = Field(..., description="Metric specification")
    name: str | None = Field(
        None, description="Optional human-readable identifier for the constraint"
    )

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True
        validate_assignment = True

    @field_validator("constraint_value", mode="before")
    @classmethod
    def convert_proteus_to_scalar(cls, v: Any) -> ProteusVariable:
        """Convert ProteusVariable to ensure all items contain StochasticScalar data."""
        if isinstance(v, ProteusVariable):
            # Check and convert internal data to StochasticScalar if needed
            converted_values = {}
            conversion_needed = False

            for item_id, item_data in v.values.items():  # type: ignore
                if isinstance(item_data, StochasticScalar):
                    # Already StochasticScalar - keep as-is
                    converted_values[item_id] = item_data
                elif isinstance(item_data, FreqSevSims):
                    # Convert FreqSevSims to StochasticScalar using .aggregate()
                    conversion_needed = True
                    converted_values[item_id] = item_data.aggregate()  # type: ignore
                elif isinstance(item_data, ProteusVariable):
                    # Convert ProteusVariable to StochasticScalar using .sum()
                    conversion_needed = True
                    converted_values[item_id] = item_data.sum()  # type: ignore
                else:
                    # Unknown type - raise error instead of conversion
                    # type: ignore
                    type_name = type(item_data).__name__
                    raise ValueError(
                        f"Unknown data type for item '{item_id}': "
                        f"{type_name}. Expected StochasticScalar, "
                        f"FreqSevSims, or ProteusVariable."
                    )

            # Create new ProteusVariable with converted data
            # if conversions occurred
            if conversion_needed:
                return ProteusVariable(v.dim_name, converted_values)  # type: ignore

            return v  # No conversions needed
        else:
            raise ValueError(f"Expected ProteusVariable, got {type(v)}")  # type: ignore

    @field_validator("direction")
    @classmethod
    def validate_direction(cls, v: str) -> str:  # type: ignore
        """Validate constraint direction."""
        if v not in VALID_CONSTRAINT_DIRECTIONS:
            raise ValueError(
                f"Direction must be one of {VALID_CONSTRAINT_DIRECTIONS}, got '{v}'"
            )
        return v  # type: ignore

    @field_validator("threshold")
    @classmethod
    def validate_threshold(cls, v: float) -> float:  # type: ignore
        """Validate threshold is finite."""
        if not np.isfinite(v):  # type: ignore
            raise ValueError("Threshold must be a finite number")
        return v  # type: ignore


class FreqSevConstraint(BaseModel):
    """OEP (Occurrence Exceedance Probability) constraints for frequency-severity data.

    Operates on occurrence - the maximum event loss per simulation - rather than
    aggregate losses (AEP). This preserves the frequency-severity structure and enables
    analysis of single-event tail risk, making it suitable for catastrophe modeling
    and scenarios where individual large events drive risk.

    Requires ProteusVariable containing FreqSevSims data. Use SimpleConstraint for
    aggregate loss constraints (AEP) or non-frequency-severity variables.
    """

    constraint_value: ProteusVariable = Field(
        ...,
        description=(
            "ProteusVariable containing FreqSevSims data for OEP (occurrence) analysis"
        ),
    )

    threshold: float = Field(..., description="Constraint threshold value")
    direction: str = Field(..., description="Constraint direction")
    metric: Metric = Field(..., description="Metric specification")
    name: str | None = Field(
        None, description="Optional human-readable identifier for the constraint"
    )

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True
        validate_assignment = True

    @field_validator("constraint_value")
    @classmethod
    def validate_freqsev_data(cls, v: ProteusVariable) -> ProteusVariable:  # type: ignore
        """Validate that ProteusVariable contains FreqSevSims objects."""
        # Check that all items are FreqSevSims
        for item_id, item_data in v.values.items():  # type: ignore
            if not isinstance(item_data, FreqSevSims):
                raise ValueError(
                    f"FreqSevConstraint requires FreqSevSims data "
                    f"for item '{item_id}', got "
                    f"{type(item_data).__name__}. "  # type: ignore
                    f"Use SimpleConstraint for other data types."
                )

        return v

    @field_validator("direction")
    @classmethod
    def validate_direction(cls, v: str) -> str:  # type: ignore
        """Validate constraint direction."""
        if v not in VALID_CONSTRAINT_DIRECTIONS:
            raise ValueError(
                f"Direction must be one of {VALID_CONSTRAINT_DIRECTIONS}, got '{v}'"
            )
        return v  # type: ignore


class OptimizationInput(BaseModel):
    """Complete specification of an optimization problem.

    This model brings together all the pieces needed for optimization:
    objectives, constraints, bounds, and current state.
    """

    item_ids: list[str] = Field(
        ..., min_length=1, description="Identifiers for optimization items"
    )
    current_shares: dict[str, float] | None = Field(
        None, description="Current allocation per item"
    )
    objective: ObjectiveSpec = Field(
        ..., description="Optimization objective specification"
    )
    simple_constraints: list[SimpleConstraint] = Field(
        default=[], description="Simple portfolio constraints"
    )
    freqsev_constraints: list[FreqSevConstraint] = Field(
        default=[], description="OEP-based constraints (occurrence)"
    )
    share_bounds: dict[str, BoundsSpec] | None = Field(
        None, description="Bounds per item using BoundsSpec"
    )
    config: dict[str, Any] | None = Field(
        None, description="Optimization config (max_iterations, tolerances, etc.)"
    )
    is_preprocessed: bool = Field(
        default=False, description="Whether preprocessing has been completed"
    )

    # Private attributes for autoscaling (not part of serialization)
    _share_scales: dict[str, float] | None = PrivateAttr(default=None)
    _obj_scale: float | None = PrivateAttr(default=None)
    _constraint_scales: list[float] | None = PrivateAttr(default=None)

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True
        validate_assignment = True

    @field_validator("current_shares")
    @classmethod
    def validate_current_shares(
        cls, v: dict[str, float] | None
    ) -> dict[str, float] | None:
        """Validate current shares values are finite."""
        if v is None:
            return v
        if not all(np.isfinite(x) for x in v.values()):
            raise ValueError("All current_shares values must be finite numbers")
        return v

    @field_validator("item_ids")
    @classmethod
    def validate_item_ids(cls, v: list[str]) -> list[str]:
        """Validate item IDs are unique and non-empty."""
        if len(set(v)) != len(v):
            duplicates = [item for item in set(v) if v.count(item) > 1]
            raise ValueError(f"Duplicate item_ids found: {duplicates}")
        if any(not item.strip() for item in v):
            raise ValueError("All item_ids must be non-empty strings")
        return v

    # ========================================================================
    # PREPROCESSING PIPELINE - 3-Step Clean Flow
    # ========================================================================

    def preprocess(self) -> "OptimizationInput":
        """Execute the complete 3-step preprocessing pipeline.

        Steps:
        1. Validate simulation consistency across all PAL variables
        2. Align objective, constraint items, bounds, and shares with target item_ids
        3. Apply autoscaling if enabled (normalize to O(1))
        4. Finalize preprocessing state

        Returns:
            New OptimizationInput with processed objective, constraints,
            bounds, and shares

        Raises:
            ValueError: If preprocessing fails at any step with
            detailed error message
        """
        try:
            # Step 1: Check Simulation Consistency
            self._validate_simulation_consistency()

            # Step 2: Align Items, Bounds, and Shares
            aligned_objective = self._align_objective()
            aligned_simple_constraints = self._align_simple_constraints()
            aligned_freqsev_constraints = self._align_freqsev_constraints()
            aligned_bounds = self._align_bounds_with_items()
            aligned_shares = self._align_shares_with_items()

            # Step 3: Create preprocessed copy
            preprocessed = self.model_copy(
                update={
                    "objective": aligned_objective,
                    "simple_constraints": aligned_simple_constraints,
                    "freqsev_constraints": aligned_freqsev_constraints,
                    "share_bounds": aligned_bounds,
                    "current_shares": aligned_shares,
                    "is_preprocessed": True,
                }
            )

            # Step 4: Apply autoscaling if enabled
            config = self.config or {}
            if config.get("autoscale", True):  # Default True
                verbose = config.get("verbose", False)
                preprocessed = preprocessed._apply_autoscaling(verbose)

            return preprocessed

        except Exception as e:
            raise ValueError(f"Preprocessing failed: {str(e)}") from e

    def _validate_simulation_consistency(self) -> None:
        """Step 1: Validate global simulation consistency across all PAL variables."""
        # Validate FreqSevSims integrity within each ProteusVariable first
        for i, constraint in enumerate(self.freqsev_constraints):
            is_valid, error_msg, _ = (
                constraint.constraint_value.validate_freqsev_consistency()
            )
            if not is_valid:
                raise ValueError(
                    f"FreqSevSims validation failed in "
                    f"freqsev_constraint[{i}]: {error_msg}"
                )

        # TODO: If PAL ProteusVariable.n_sims was correctly
        # implemented, this could be simplified to just:
        #
        # all_pvs = ([self.objective.objective_value] +
        #   [c.constraint_value for c in self.simple_constraints] +
        #   [c.constraint_value for c in self.freqsev_constraints])
        # effective_n_sims = [pv.n_sims for pv in all_pvs
        #   for _ in pv.values]
        # non_one_sims = {n for n in effective_n_sims if n != 1}
        # if len(non_one_sims) > 1:
        #   raise ValueError(
        #     f"Inconsistent simulation counts: "
        #     f"{sorted(set(effective_n_sims))}")

        # Workaround: Manually extract effective simulation counts
        # since PAL's n_sims is unreliable
        def get_effective_n_sims(pv: ProteusVariable, expected_type: str) -> list[int]:
            """Extract all simulation counts from a ProteusVariable."""
            return [
                len(pv[item_id].values)
                if expected_type == "scalar"
                else pv[item_id].n_sims  # type: ignore
                for item_id in pv.values.keys()  # type: ignore
            ]

        effective_n_sims: list[int] = []
        effective_n_sims.extend(
            get_effective_n_sims(self.objective.objective_value, "scalar")
        )
        effective_n_sims.extend(
            [
                n
                for c in self.simple_constraints
                for n in get_effective_n_sims(c.constraint_value, "scalar")
            ]
        )
        effective_n_sims.extend(
            [
                n
                for c in self.freqsev_constraints
                for n in get_effective_n_sims(c.constraint_value, "freqsev")
            ]
        )

        # Check number of non-1 simulations and raise error if there is more than 1
        non_one_sims = {n for n in effective_n_sims if n != 1}
        if len(non_one_sims) > 1:
            raise ValueError(
                f"Simulation count mismatch across variables: "
                f"{sorted(set(effective_n_sims))}"
            )

    def _align_objective(self) -> ObjectiveSpec:
        """Step 2A: Align objective items with target item_ids."""
        # Create zero template with matching n_sims from ProteusVariable
        n_sims: int = self.objective.objective_value.n_sims  # type: ignore
        template = StochasticScalar(values=[0.0] * n_sims)

        aligned_objective_value = self._align_proteus_variable_items(
            self.objective.objective_value, template
        )

        # Create new objective with aligned items
        return self.objective.model_copy(
            update={"objective_value": aligned_objective_value}
        )

    def _align_simple_constraints(self) -> list[SimpleConstraint]:
        """Step 2B: Align simple constraint items with target item_ids."""
        aligned_constraints: list[SimpleConstraint] = []

        for constraint in self.simple_constraints:
            # Create zero template with matching n_sims from ProteusVariable
            n_sims: int = constraint.constraint_value.n_sims  # type: ignore
            template: StochasticScalar = StochasticScalar(values=[0.0] * n_sims)

            aligned_constraint = self._align_proteus_variable_items(
                constraint.constraint_value, template
            )

            # Create new constraint with aligned items
            new_constraint = constraint.model_copy(
                update={"constraint_value": aligned_constraint}
            )
            aligned_constraints.append(new_constraint)

        return aligned_constraints

    def _align_freqsev_constraints(self) -> list[FreqSevConstraint]:
        """Step 2C: Align FreqSev constraint items with target item_ids."""
        aligned_constraints: list[FreqSevConstraint] = []

        for constraint in self.freqsev_constraints:
            # Create zero template by multiplying first item by 0
            first_item_id = next(iter(constraint.constraint_value.values.keys()))  # type: ignore
            first_item = constraint.constraint_value[first_item_id]
            template: FreqSevSims = first_item * 0  # type: ignore  # Creates zero version with same structure

            aligned_constraint = self._align_proteus_variable_items(
                constraint.constraint_value, template
            )

            # Create new constraint with aligned items
            new_constraint = constraint.model_copy(
                update={"constraint_value": aligned_constraint}
            )
            aligned_constraints.append(new_constraint)

        return aligned_constraints

    def _align_proteus_variable_items(
        self,
        proteus_var: ProteusVariable,
        template_item: StochasticScalar | FreqSevSims,
    ) -> ProteusVariable:
        """Align ProteusVariable items with target item_ids using provided template."""
        import warnings

        aligned_items: dict[str, StochasticScalar | FreqSevSims] = {}

        # Check for unused items in the constraint
        constraint_items = set(proteus_var.values.keys())  # type: ignore
        target_items = set(self.item_ids)
        unused_items = constraint_items - target_items

        if unused_items:
            warnings.warn(
                f"Constraint has items {sorted(unused_items)} that are "
                f"not in item_ids {sorted(self.item_ids)}. "
                f"These items will be ignored. Did you mean to include "
                f"them in item_ids?",
                UserWarning,
                stacklevel=4,
            )

        for item_id in self.item_ids:
            if item_id in proteus_var.values:  # type: ignore
                # Keep existing item
                aligned_items[item_id] = proteus_var[item_id]  # type: ignore
            else:
                # Create zero dummy item
                aligned_items[item_id] = template_item

        return ProteusVariable(proteus_var.dim_name, aligned_items)  # type: ignore

    def _align_bounds_with_items(self) -> dict[str, BoundsSpec]:
        """Step 2D: Align bounds with final item set."""
        if self.share_bounds is None:
            # No bounds provided - generate default bounds for all items
            return {item_id: BoundsSpec() for item_id in self.item_ids}

        # Align existing bounds with target items
        aligned_bounds: dict[str, BoundsSpec] = {}

        for item_id in self.item_ids:
            if item_id in self.share_bounds:
                # Keep existing bounds
                aligned_bounds[item_id] = self.share_bounds[item_id]
            else:
                # Add default bounds for missing item using Pydantic defaults
                aligned_bounds[item_id] = BoundsSpec()

        return aligned_bounds

    def _align_shares_with_items(self) -> dict[str, float]:
        """Step 2E: Align current shares with final item set and ensure feasibility.

        Adjusts shares to be within bounds to ensure starting point is feasible:
        - If share is zero or below lower bound → set slightly above lower bound
        - If share is above upper bound → set slightly below upper bound
        """
        if self.current_shares is None:
            # Generate default shares (1.0) for all items
            return dict.fromkeys(self.item_ids, 1.0)

        # Align existing shares with target items and enforce bounds
        aligned_shares: dict[str, float] = {}
        epsilon = 1e-6  # Small offset to ensure strict feasibility

        for item_id in self.item_ids:
            if item_id in self.current_shares:
                share = self.current_shares[item_id]
            else:
                share = 1.0  # Default for missing item

            # Enforce bounds if they exist
            if self.share_bounds and item_id in self.share_bounds:
                bounds = self.share_bounds[item_id]

                # Adjust to be within bounds
                # (only if bounds require positive values)
                if (
                    bounds.lower is not None
                    and bounds.lower > 1e-10
                    and share <= bounds.lower
                ):
                    # Below or at positive lower bound → move slightly above
                    share = bounds.lower + epsilon
                elif bounds.upper is not None and share >= bounds.upper:
                    # Above or at upper bound → move slightly below
                    share = bounds.upper - epsilon
                # Note: If lower=0 and share=0, leave it as 0 (don't force to epsilon)

            aligned_shares[item_id] = share

        return aligned_shares

    # ========================================================================
    # AUTOSCALING METHODS - Normalize Problem to O(1)
    # ========================================================================

    def _apply_autoscaling(self, verbose: bool = False) -> "OptimizationInput":
        """Apply comprehensive autoscaling to normalize the optimization problem.

        Scaling Strategy:
        1. Normalize shares to 1.0 (store scale factors in _share_scales)
        2. Scale ProteusVariables up by inverse to compensate
        3. Scale objective to base value 1.0 (store in _obj_scale)
        4. Scale constraints to base value 1.0 (store in _constraint_scales)

        Args:
            verbose: If True, print scaling information

        Returns:
            New OptimizationInput with scaled problem and stored scaling factors
        """
        if not self.current_shares:
            raise ValueError("Cannot autoscale without current_shares")

        # Step 1: Calculate share scales (normalize each share to 1.0)
        # Scaling threshold = 1.0:
        #   - Shares ≤ 1.0: No scaling (scale=1.0, keep original)
        #     Rationale: Avoids tiny scale factors
        #     (e.g., share=1e-6 → scale=1e-6 → bounds/1e-6 = huge)
        #   - Shares > 1.0: Normalize to 1.0 for numerical stability
        #     Rationale: Brings large premiums (millions) down to
        #     O(1) for optimizer
        share_scales = {}
        scaled_shares = {}
        near_zero_shares = []  # Track shares close to zero for warning

        for item_id, share in self.current_shares.items():
            if abs(share) <= 1.0:
                # Small share - don't scale (avoids tiny scale factors)
                share_scales[item_id] = 1.0
                scaled_shares[item_id] = share  # Keep original value

                # Warn about shares very close to zero
                # (may indicate initialization issue)
                if abs(share) < 1e-6 and abs(share) > 0:
                    near_zero_shares.append((item_id, share))
            else:
                # Large share (> 1) - normalize to 1.0
                share_scales[item_id] = share
                scaled_shares[item_id] = 1.0

        # Warn if any shares are suspiciously close to zero
        if near_zero_shares and verbose:
            print(
                f"\n[Autoscaling] WARNING: {len(near_zero_shares)} "
                f"shares are very small (< 1e-6):"
            )
            for item_id, share in near_zero_shares[:5]:  # Show first 5
                print(f"  - {item_id}: {share:.2e}")
            if len(near_zero_shares) > 5:
                print(f"  ... and {len(near_zero_shares) - 5} more")
            print(
                "  These may cause numerical issues. Consider using "
                "_align_shares_with_items() first."
            )

        # Step 2: Scale bounds (divide by share scales)
        scaled_bounds = {}
        for item_id, bounds in self.share_bounds.items() if self.share_bounds else {}:  # type: ignore
            scale = share_scales[item_id]
            # For zero shares (scale=1.0), bounds pass through unchanged
            scaled_bounds[item_id] = BoundsSpec(
                lower=bounds.lower / scale if bounds.lower is not None else None,
                upper=bounds.upper / scale if bounds.upper is not None else None,
            )

        # DEBUG: Check feasibility of scaled starting point
        if verbose:
            print("\n[DEBUG] Checking scaled starting point feasibility:")
            infeasible_count = 0
            for item_id in self.item_ids:
                share = scaled_shares[item_id]
                bounds = scaled_bounds.get(item_id)
                if bounds:
                    if (bounds.lower is not None and share < bounds.lower - 1e-10) or (
                        bounds.upper is not None and share > bounds.upper + 1e-10
                    ):
                        orig_share = self.current_shares[item_id]
                        scale = share_scales[item_id]
                        print(
                            f"  ⚠️  {item_id}: "
                            f"orig={orig_share:.4f}, "
                            f"scaled={share:.4f}, "
                            f"bounds=[{bounds.lower:.4f}, "
                            f"{bounds.upper:.4f}]"
                        )
                        infeasible_count += 1
            if infeasible_count == 0:
                print("  ✓ All starting points feasible")
            else:
                print(f"  ⚠️  {infeasible_count} infeasible starting points!")

        # Step 3: Scale ProteusVariables (multiply by share scales to compensate)
        scaled_objective_value = self._scale_proteus_variable(
            self.objective.objective_value, share_scales
        )
        scaled_objective = self.objective.model_copy(
            update={"objective_value": scaled_objective_value}
        )

        scaled_simple_constraints = []
        for constraint in self.simple_constraints:
            scaled_constraint_value = self._scale_proteus_variable(
                constraint.constraint_value, share_scales
            )
            scaled_simple_constraints.append(
                constraint.model_copy(
                    update={"constraint_value": scaled_constraint_value}
                )
            )

        scaled_freqsev_constraints = []
        for constraint in self.freqsev_constraints:
            scaled_constraint_value = self._scale_proteus_variable(
                constraint.constraint_value, share_scales
            )
            scaled_freqsev_constraints.append(
                constraint.model_copy(
                    update={"constraint_value": scaled_constraint_value}
                )
            )

        # Step 4: Objective and Constraint Scaling - DISABLED
        #
        # IMPORTANT: Objective/constraint scaling is currently
        # disabled because composite metrics like RatioMetric are
        # scale-invariant (scaling the variable doesn't change the
        # ratio). When we divide ProteusVariable by a scale, both
        # numerator and denominator scale equally, so the ratio
        # remains unchanged. This causes optimization to work on
        # unscaled values.
        #
        # TODO: To properly implement metric-based scaling, add a
        # method/property to Metric class:
        #   - Metric.determine_scaling_factor(variable, item_ids)
        #     -> float
        #   - Returns how the metric value scales when variable is
        #     scaled uniformly
        #   - Examples:
        #     * MeanMetric: returns 1.0 (scales linearly)
        #     * RatioMetric: returns 0.0 (scale-invariant,
        #       num/den cancel)
        #     * ProductMetric: returns 2.0 (scales by scale²)
        #   - Then: effective_scale = base_value ** scaling_factor
        #
        # For now, we only apply share scaling (Step 1-3) and skip
        # objective/constraint scaling.

        obj_scale = 1.0  # No objective scaling
        constraint_scales = [1.0] * (
            len(scaled_simple_constraints) + len(scaled_freqsev_constraints)
        )

        # Step 5: Use share-scaled values directly (no additional scaling)
        final_objective = scaled_objective
        final_simple_constraints = scaled_simple_constraints
        final_freqsev_constraints = scaled_freqsev_constraints

        # Step 7: Create scaled copy and store scaling factors
        scaled_input = self.model_copy(
            update={
                "current_shares": scaled_shares,
                "share_bounds": scaled_bounds,
                "objective": final_objective,
                "simple_constraints": final_simple_constraints,
                "freqsev_constraints": final_freqsev_constraints,
            }
        )

        # Store scaling factors in private attributes
        scaled_input._share_scales = share_scales
        scaled_input._obj_scale = obj_scale
        scaled_input._constraint_scales = constraint_scales

        return scaled_input

    def _scale_proteus_variable(
        self, proteus_var: ProteusVariable, scales: dict[str, float]
    ) -> ProteusVariable:
        """Scale a ProteusVariable by multiplying each item by its scale factor.

        Uses PAL multiplication pattern: creates a ProteusVariable with constant
        StochasticScalar values containing the scale factors, then multiplies.

        Args:
            proteus_var: Original ProteusVariable to scale
            scales: Dictionary mapping item_id to scale factor

        Returns:
            Scaled ProteusVariable
        """
        # Get simulation count from first item
        first_item_id = next(iter(proteus_var.values.keys()))  # type: ignore
        first_item = proteus_var[first_item_id]

        # Determine n_sims based on item type
        if isinstance(first_item, StochasticScalar):
            n_sims = len(first_item.values)  # type: ignore
        elif isinstance(first_item, FreqSevSims):
            n_sims = first_item.n_sims
        else:
            raise ValueError(
                f"Unknown item type in ProteusVariable: {type(first_item)}"
            )

        # Create scale ProteusVariable with constant values
        scale_dict = {}
        for item_id in proteus_var.values.keys():  # type: ignore
            scale_value = scales.get(item_id, 1.0)
            scale_dict[item_id] = StochasticScalar(np.full(n_sims, scale_value))

        scale_var = ProteusVariable(proteus_var.dim_name, scale_dict)  # type: ignore

        # Multiply to scale
        return proteus_var * scale_var  # type: ignore


# ============================================================================
# OPTIMIZATION RESULT MODELS
# ============================================================================


class ConstraintResult(BaseModel):
    """Result for a single constraint evaluation."""

    constraint_type: str = Field(
        ..., description="Type of constraint (simple or freqsev)"
    )
    constraint_index: int = Field(..., description="Index in the constraints list")
    metric_type: str = Field(
        ..., description="Metric type (mean, std, spread_var, etc.)"
    )
    name: str | None = Field(
        None, description="Human-readable constraint name (from constraint definition)"
    )
    threshold: float = Field(..., description="Constraint threshold value")
    direction: str = Field(..., description="Constraint direction (cap or floor)")
    actual_value: float = Field(
        ..., description="Actual portfolio value for this constraint"
    )
    slack: float = Field(
        ..., description="Constraint slack (positive = satisfied, negative = violated)"
    )
    is_satisfied: bool = Field(..., description="Whether constraint is satisfied")

    class Config:
        """Pydantic configuration."""

        frozen = True


class OptimizationResult(BaseModel):
    """Complete optimization result with constraint evaluations."""

    success: bool = Field(
        ..., description="Whether optimization converged successfully"
    )
    optimal_shares: dict[str, float] = Field(
        ..., description="Optimal portfolio weights by item_id"
    )
    objective_value: float = Field(..., description="Optimal objective function value")
    constraint_results: list[ConstraintResult] = Field(
        default=[], description="Evaluation of all constraints at optimal solution"
    )
    status: int = Field(..., description="Optimization status code")
    message: str = Field(..., description="Optimization status message")
    n_iterations: int = Field(..., description="Number of optimizer iterations")
    optimization_time: float = Field(
        ..., description="Total optimization time in seconds"
    )

    class Config:
        """Pydantic configuration."""

        frozen = True

    @property
    def violated_constraints(self) -> list[ConstraintResult]:
        """Return list of violated constraints."""
        return [c for c in self.constraint_results if not c.is_satisfied]

    @property
    def all_constraints_satisfied(self) -> bool:
        """Check if all constraints are satisfied."""
        return all(c.is_satisfied for c in self.constraint_results)


# ============================================================================
# EFFICIENT FRONTIER MODELS
# ============================================================================


class ConstraintVariation(BaseModel):
    """Specification for how to vary a single constraint across the frontier."""

    constraint_type: Literal["simple", "freqsev"] = Field(
        ..., description="Type of constraint ('simple' or 'freqsev')"
    )
    constraint_name: str = Field(..., description="Name of the constraint to vary")
    min_threshold: float = Field(..., description="Starting threshold value")
    max_threshold: float = Field(..., description="Ending threshold value")

    class Config:
        """Pydantic configuration."""

        frozen = True

    @model_validator(mode="after")
    def validate_threshold_order(self):
        """Validate min_threshold < max_threshold."""
        if self.min_threshold >= self.max_threshold:
            raise ValueError(
                f"min_threshold ({self.min_threshold}) must be less than "
                f"max_threshold ({self.max_threshold})"
            )
        return self


class EfficientFrontierInput(BaseModel):
    """Input specification for efficient frontier generation."""

    base_optimization: OptimizationInput = Field(
        ..., description="Base optimization problem to vary"
    )
    constraint_variations: list[ConstraintVariation] = Field(
        ..., min_length=1, description="Constraints to vary in parallel"
    )
    n_points: int = Field(
        default=20, ge=3, le=100, description="Number of frontier points to generate"
    )

    class Config:
        """Pydantic configuration."""

        frozen = True

    @model_validator(mode="after")
    def validate_constraint_names_exist(self):
        """Validate all constraint names exist in their specified lists."""
        for variation in self.constraint_variations:
            # Get the appropriate constraint list
            if variation.constraint_type == "simple":
                constraints = self.base_optimization.simple_constraints
            else:  # "freqsev"
                constraints = self.base_optimization.freqsev_constraints

            # Check if name exists in this list
            names_in_list = {c.name for c in constraints if c.name}
            if variation.constraint_name not in names_in_list:
                # Build helpful error message
                available = (
                    ", ".join(sorted(names_in_list)) if names_in_list else "none"
                )
                unnamed_count = len([c for c in constraints if not c.name])

                error_msg = (
                    f"Constraint '{variation.constraint_name}' not "
                    f"found in {variation.constraint_type} constraints. "
                    f"Available named {variation.constraint_type} "
                    f"constraints: {available}."
                )
                if unnamed_count > 0:
                    error_msg += (
                        f" ({unnamed_count} unnamed "
                        f"{variation.constraint_type} constraints exist)"
                    )
                raise ValueError(error_msg)

        # Check for duplicate (type, name) pairs in variations
        variation_keys = [
            (v.constraint_type, v.constraint_name) for v in self.constraint_variations
        ]
        if len(variation_keys) != len(set(variation_keys)):
            duplicates = [
                key for key in set(variation_keys) if variation_keys.count(key) > 1
            ]
            raise ValueError(f"Duplicate constraint variations: {duplicates}")

        return self


class EfficientFrontierResult(BaseModel):
    """Result from efficient frontier generation."""

    optimization_results: list[OptimizationResult] = Field(
        ..., description="List of optimization results, one per frontier point"
    )

    class Config:
        """Pydantic configuration."""

        frozen = True

    @property
    def successful_results(self) -> list[OptimizationResult]:
        """Return only successful optimization results."""
        return [r for r in self.optimization_results if r.success]

    @property
    def failed_results(self) -> list[OptimizationResult]:
        """Return only failed optimization results."""
        return [r for r in self.optimization_results if not r.success]

    @property
    def n_successful(self) -> int:
        """Count of successful optimizations."""
        return len(self.successful_results)

    @property
    def n_failed(self) -> int:
        """Count of failed optimizations."""
        return len(self.failed_results)

    @property
    def total_time(self) -> float:
        """Total time spent on all optimizations."""
        return sum(r.optimization_time for r in self.optimization_results)
