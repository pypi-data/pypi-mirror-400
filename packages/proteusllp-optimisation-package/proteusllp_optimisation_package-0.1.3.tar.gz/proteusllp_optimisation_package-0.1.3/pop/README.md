# POP Package Documentation

The `pop` package provides a domain-agnostic, metric-centric optimization framework built on top of PAL (Proteus Analytics Library). It enables portfolio optimization, risk analysis, and any stochastic optimization problem using a clean, type-safe API.

## 📦 Package Overview

**Total Code**: ~2,400 lines across 6 modules
**Architecture**: Pydantic models → scipy.optimize interface → PAL transformations
**Philosophy**: Metric-centric (same math for objectives and constraints)

---

## 🗂️ Module Organization

### Core API (`__init__.py`) - 129 lines
**Purpose**: Public interface and package exports

**What it exports**:
- **Models**: All Pydantic data structures (metrics, constraints, inputs, results)
- **Functions**: `optimize()` and `generate_efficient_frontier()`
- **Config**: Constants and enums (directions, statuses, tolerances)

**Key exports**:
```python
# Metrics
MeanMetric, StdMetric, SpreadVarMetric
RatioMetric, ProductMetric, SumMetric, DifferenceMetric

# Specifications
ObjectiveSpec, SimpleConstraint, FreqSevConstraint
OptimizationInput, BoundsSpec

# Results
OptimizationResult, ConstraintResult
EfficientFrontierInput, EfficientFrontierResult

# Functions
optimize, generate_efficient_frontier

# Configuration
OptimizationDirection, ConstraintDirection, OptimizationStatus
```

**When to look here**: Understanding what's available in the public API

---

### Configuration (`config.py`) - 79 lines
**Purpose**: Constants, enums, and default settings

**Key components**:

#### Enums
- `OptimizationDirection`: MINIMIZE | MAXIMIZE
- `ConstraintDirection`: CAP (≤) | FLOOR (≥)
- `OptimizationStatus`: Success codes (0-9)

#### Constants
- `MAX_ITERATIONS = 1000`: Default iteration limit
- `DEFAULT_TOLERANCES`: ftol for scipy SLSQP (only ftol is supported)
- `STATUS_DESCRIPTIONS`: Human-readable status messages

#### Default Configuration
```python
DEFAULT_CONFIG = {
    "max_iterations": 1000,
    "tolerances": {"ftol": 1e-8},
    "verbose": False,
    "autoscale": True  # Enable automatic problem scaling
}
```

**When to look here**:
- Adjusting default tolerances
- Understanding optimization status codes
- Checking valid directions for objectives/constraints
- Configuring autoscaling behavior
- Configuring autoscaling behavior

---

## 🔧 Automatic Problem Scaling (Autoscaling)

**Status**: Enabled by default (`autoscale: True`)
**Purpose**: Normalize optimization problems to O(1) scale for robust scipy convergence
**Transparency**: **Users always see original units** - scaling is completely internal

### Why Autoscaling?

Scipy's SLSQP optimizer uses **absolute tolerance checks** for convergence. Problems with vastly different scales can cause:
- **Premature termination**: Tiny gradients (e.g., 1e-5) trigger early exit even when optimization isn't complete
- **Poor convergence**: Large objective values (e.g., 1e6) combined with small gradients confuse convergence checks
- **Ratio metrics issues**: RoC (Return on Capital) metrics often have gradients 1000x smaller than profit metrics

**Example Problem**:
- Portfolio with shares = [100, 200, 300]
- Profit objective value = 879
- RoC objective value = -0.063
- RoC gradient norm = 0.00064 (18,000x smaller than profit gradient!)
- Result: **Optimizer exits after 1 iteration** with "success" despite not optimizing

### How Autoscaling Works

**During preprocessing** (`preprocess()` with `autoscale=True`):

1. **Normalize shares to 1.0**
   - Original: `{"asset1": 100, "asset2": 200}` → Scaled: `{"asset1": 1.0, "asset2": 1.0}`
   - Stores scale factors: `_share_scales = {"asset1": 100, "asset2": 200}`

2. **Scale ProteusVariables up** (compensation)
   - Multiplies each item's stochastic variable by its share scale
   - Ensures `scaled_var * scaled_shares = original_var * original_shares`

3. **Scale bounds down**
   - Original bounds: `[50, 150]` → Scaled bounds: `[0.5, 1.5]` (divided by 100)

4. **Normalize objective to base value = 1.0**
   - Evaluates objective at scaled shares (all 1.0)
   - If base value = 879, objective_scale = 879
   - Divides objective ProteusVariable by 879
   - Stores: `_obj_scale = 879`

5. **Normalize constraints to base value = 1.0**
   - Same process for each constraint
   - Stores: `_constraint_scales = [scale1, scale2, ...]`

**During optimization**:
- Scipy works with normalized problem (all O(1))
- Gradients are typically in range [0.01, 1.0]
- Convergence checks work reliably

**In results** (`process_scipy_result()`):
- **Shares unscaled**: Multiply by `_share_scales`
- **Objective unscaled**: Divide by `_obj_scale`
- **Constraints unscaled**: Divide threshold, actual_value, slack by `_constraint_scales`
- **User receives results in original units** 🎯

### User Perspective: Transparent Scaling

**✅ What users see**: Original units everywhere
```python
# Input in original units
opt_input = OptimizationInput(
    item_ids=["asset1", "asset2"],
    current_shares={"asset1": 100, "asset2": 200},
    objective=ObjectiveSpec(
        objective_value=profits,  # Values in dollars
        metric=RatioMetric(...),
        direction="maximize"
    ),
    share_bounds={
        "asset1": BoundsSpec(lower=50, upper=150),
        "asset2": BoundsSpec(lower=100, upper=300)
    }
)

# Preprocess (autoscaling happens internally)
preprocessed = opt_input.preprocess()

# Optimize (works with scaled data internally)
result = optimize(preprocessed)

# Results in original units!
print(result.optimal_shares)  # {"asset1": 120, "asset2": 250}
print(result.objective_value)  # 0.085 (RoC ratio)
```

**❌ What users DON'T see**: Internal scaling
- Scaled shares (always 1.0 internally)
- Scaled objective values
- Scaled gradients
- Scaling factors (stored in private `_share_scales`, `_obj_scale`, `_constraint_scales`)

### Performance Impact

**Before autoscaling**:
- RoC optimization: **1 iteration** (premature exit)
- Profit optimization: 66 iterations (worked fine)

**After autoscaling**:
- RoC optimization: **143 iterations** (proper convergence!)
- Profit optimization: 66 iterations (unchanged)

### Configuration

**Enable autoscaling** (default):
```python
opt_input = OptimizationInput(
    ...,
    config={"autoscale": True}  # or omit (default)
)
```

**Disable autoscaling** (if needed):
```python
opt_input = OptimizationInput(
    ...,
    config={"autoscale": False}
)
```

**Verbose autoscaling output**:
```python
opt_input = OptimizationInput(
    ...,
    config={
        "autoscale": True,
        "verbose": True  # Prints scaling factors
    }
)
```

**Output example**:
```
[Autoscaling] Share scales: {'asset1': 100, 'asset2': 200}
[Autoscaling] Objective scale: 8.790835e+02
[Autoscaling] Constraint scales: ['1.500000e+01', '5.000000e+02']
```

### When to Disable Autoscaling

Autoscaling is beneficial in 99% of cases. Consider disabling only if:
1. **Debugging**: Need to see exact internal values scipy uses
2. **Already normalized**: Your problem is already scaled to O(1)
3. **Custom scaling**: Implementing your own scaling strategy

**Note**: Disabling autoscaling may cause convergence issues with ratio metrics or problems with vastly different scales.

---

### Data Models (`models.py`) - 747 lines
**Purpose**: Pydantic models for type-safe data structures

**Model hierarchy**:

#### Metrics (7 models, ~200 lines)
1. **MeanMetric**: Expected value
2. **StdMetric**: Standard deviation (volatility)
3. **SpreadVarMetric**: Average between percentiles
   - Fields: `lower_percentile`, `upper_percentile` (0-100)
4. **RatioMetric**: Ratio of two metrics (e.g., mean/std for Sharpe)
   - Fields: `numerator`, `denominator`
5. **ProductMetric**: Product of two metrics
6. **SumMetric**: Sum of two metrics
7. **DifferenceMetric**: Difference of two metrics

```python
# Example: Sharpe ratio
sharpe = RatioMetric(
    numerator=MeanMetric(),
    denominator=StdMetric()
)
```

#### Specifications (4 models, ~200 lines)
1. **BoundsSpec**: Share bounds per item
   - Fields: `lower`, `upper` (default: -inf to +inf)
   - Validation: lower < upper

2. **ObjectiveSpec**: What to optimize
   - Fields: `objective_value` (ProteusVariable), `metric`, `direction`
   - Auto-converts ProteusVariable items to optimization variables

3. **SimpleConstraint**: Portfolio-level constraint
   - Fields: `constraint_value`, `threshold`, `direction`, `metric`, `name`
   - Examples: "max std ≤ 0.1", "min mean ≥ 0.05"
   - Auto-converts FreqSevSims to aggregate losses (AEP) if present

4. **FreqSevConstraint**: OEP-based frequency-severity constraint
   - Fields: Same as SimpleConstraint but for FreqSevSims
   - Operates on occurrence (max event loss per simulation), not aggregate (AEP)
   - Use for catastrophe modeling and single-event tail risk analysis
   - Critical: All FreqSevSims must have identical `sim_index` arrays

#### Core Input (`OptimizationInput`, ~200 lines)
**Most important model** - complete optimization specification

**Required Fields**:
- `item_ids`: List of asset/item identifiers (must be unique)
- `objective`: ObjectiveSpec - what to optimize

**Optional Fields**:
- `current_shares`: Dict of current allocations (default: 1.0 for all items)
- `simple_constraints`: List of SimpleConstraint (default: empty list)
- `freqsev_constraints`: List of FreqSevConstraint (default: empty list)
- `share_bounds`: Dict of BoundsSpec per item (default: -inf to +inf for all)
- `config`: Dict of optimization settings (default: `DEFAULT_CONFIG`)

**Internal Fields** (don't set manually):
- `is_preprocessed`: Flag indicating preprocessing is complete

**Configuration Options** (`config` parameter):

All config options are optional and have sensible defaults:

```python
config = {
    # Optimization control
    "max_iterations": 1000,           # Maximum SLSQP iterations (int)
    "tolerances": {"ftol": 1e-8},     # Function tolerance for convergence (dict)

    # Problem scaling
    "autoscale": True,                 # Auto-normalize problem to O(1) (bool)

    # Diagnostics
    "verbose": False,                  # Print iteration details and scaling info (bool)
}
```

**Config Details**:

1. **`max_iterations`** (int, default: 1000)
   - Maximum number of SLSQP iterations before termination
   - Increase for complex problems that need more iterations
   - Decrease for faster (but potentially incomplete) optimization

2. **`tolerances`** (dict, default: `{"ftol": 1e-8}`)
   - `ftol`: Function value tolerance - optimization stops when change < ftol
   - Only ftol is supported by SLSQP
   - Smaller values = more precise but slower convergence

3. **`autoscale`** (bool, default: True)
   - True: Automatically normalize problem to O(1) for robust convergence
   - False: Use original problem scale (may cause convergence issues)
   - See [Autoscaling section](#-automatic-problem-scaling-autoscaling) for details

4. **`verbose`** (bool, default: False)
   - True: Print iteration-by-iteration progress and scaling information
   - False: Silent optimization (only result returned)
   - Useful for debugging convergence issues

**Key method**: `preprocess()`
- Validates simulation consistency
- Aligns items across objective/constraints/bounds
- Applies autoscaling if enabled (normalizes problem to O(1))
- Returns new OptimizationInput ready for optimization
- **Always call before optimize()**

**Basic Example**:
```python
opt_input = OptimizationInput(
    item_ids=["asset1", "asset2"],
    objective=objective_spec,
    current_shares={"asset1": 100, "asset2": 200},
    simple_constraints=[risk_constraint],
    share_bounds={
        "asset1": BoundsSpec(lower=0, upper=150),
        "asset2": BoundsSpec(lower=0, upper=250)
    }
)

# Must preprocess before optimizing
preprocessed = opt_input.preprocess()
result = optimize(preprocessed)
```

**Example with Custom Config**:
```python
opt_input = OptimizationInput(
    item_ids=["asset1", "asset2"],
    objective=objective_spec,
    current_shares={"asset1": 100, "asset2": 200},
    config={
        "max_iterations": 500,        # Limit iterations
        "tolerances": {"ftol": 1e-6}, # Looser tolerance for speed
        "autoscale": True,             # Keep autoscaling enabled
        "verbose": True                # See iteration progress
    }
)

preprocessed = opt_input.preprocess()
result = optimize(preprocessed)
```

#### Results (2 models, ~100 lines)
1. **OptimizationResult**: Complete optimization outcome
   - Fields: `success`, `optimal_shares`, `objective_value`, `constraint_results`
   - Properties: `is_satisfied`, `violated_constraints`
   - Frozen: Immutable after creation

2. **ConstraintResult**: Per-constraint evaluation
   - Fields: `constraint_type`, `threshold`, `actual_value`, `slack`, `is_satisfied`
   - Slack: Positive = satisfied, negative = violated

#### Efficient Frontier (2 models, ~50 lines)
1. **ConstraintVariation**: How to vary a constraint
   - Fields: `constraint_type`, `constraint_name`, `min_threshold`, `max_threshold`

2. **EfficientFrontierInput**: Frontier specification
   - Fields: `base_optimization`, `constraint_variations`, `n_points`
   - Generates n_points optimizations by varying thresholds

3. **EfficientFrontierResult**: Frontier outcomes
   - Fields: `optimization_results` (list of OptimizationResult)
   - Properties: `n_successful`, `n_failed`, `total_time`

**When to look here**:
- Understanding data structures
- Debugging validation errors
- Learning what fields are available
- Implementing new features

---

### Optimization Interface (`scipy_interface.py`) - 312 lines
**Purpose**: Bridge between Pydantic models and scipy.optimize.minimize

**Key functions**:

#### `optimize(optimization_input: OptimizationInput) -> OptimizationResult`
**Main optimization entry point** - 150 lines

**Flow**:
1. Validate input is preprocessed
2. Transform objective → scipy functions (value + gradient)
3. Transform constraints → scipy constraint dicts
4. Transform bounds → scipy bounds array
5. Generate initial guess from current_shares
6. Call `scipy.optimize.minimize()` with SLSQP
7. Evaluate all constraints at optimal solution
8. Build OptimizationResult with all metrics

**Example**:
```python
result = optimize(preprocessed_input)
if result.success:
    print(f"Optimal shares: {result.optimal_shares}")
    print(f"Objective value: {result.objective_value}")
    for cr in result.constraint_results:
        print(f"{cr.name}: {cr.actual_value} (slack: {cr.slack})")
```

#### Helper Functions (4 functions, ~160 lines)
1. **get_initial_guess()**: Convert current_shares dict → numpy array
2. **bounds_to_scipy_bounds()**: Convert BoundsSpec dicts → scipy bounds format
3. **process_scipy_result()**: Transform scipy OptimizeResult → OptimizationResult
4. **_evaluate_constraints()**: Evaluate all constraints at optimal solution

**When to look here**:
- Understanding optimization flow
- Debugging scipy integration
- Adding new scipy options
- Investigating convergence issues

---

### Mathematical Transformations (`transforms.py`) - 1,004 lines
**Purpose**: Convert metrics and PAL variables into scipy-compatible functions

**Architecture**: Metric-centric dispatch system

#### Core Dispatcher (~50 lines)
**`create_metric_calculator(metric, proteus_variable, item_ids)`**
- Analyzes metric type and data type
- Dispatches to appropriate calculator
- Returns (value_func, gradient_func) tuple

**Dispatch logic**:
```
Metric Type × Data Type → Calculator
────────────────────────────────────
Mean × StochasticScalar → create_scalar_mean
Mean × FreqSevSims      → create_freqsev_mean
Std × StochasticScalar  → create_scalar_std
SpreadVar × StochasticScalar → create_scalar_spreadvar
Ratio/Product/Sum/Diff  → create_composite_calculator
```

#### StochasticScalar Calculators (~400 lines)
**Base calculators for simple stochastic variables**

1. **`create_scalar_mean()`** (~80 lines)
   - Value: `mean(sim_matrix @ shares)`
   - Gradient: `mean(sim_matrix)` (analytical)

2. **`create_scalar_std()`** (~120 lines)
   - Value: `std(sim_matrix @ shares)`
   - Gradient: Analytical via covariance

3. **`create_scalar_spreadvar()`** (~200 lines)
   - Value: Mean of percentile range
   - Gradient: Numerical (complex to derive analytically)

#### FreqSevSims Calculators (~300 lines)
**Specialized calculators for frequency-severity simulations**

1. **`create_freqsev_mean()`** (~100 lines)
   - Aggregates losses per simulation
   - Computes mean across simulations

2. **`create_freqsev_std()`** (~100 lines)
   - Aggregates losses per simulation
   - Computes std dev across simulations

3. **`create_freqsev_spreadvar()`** (~100 lines)
   - Aggregates losses per simulation
   - Computes percentile-based spread

**Critical**: All FreqSevSims must have identical `sim_index` arrays within a ProteusVariable

#### Composite Calculators (~200 lines)
**Combine base metrics into composite metrics**

1. **`create_ratio_calculator()`**: numerator / denominator
   - Gradient: Quotient rule
   - Example: Sharpe ratio (mean/std)

2. **`create_product_calculator()`**: factor1 * factor2
   - Gradient: Product rule

3. **`create_sum_calculator()`**: term1 + term2
   - Gradient: Sum of gradients

4. **`create_difference_calculator()`**: minuend - subtrahend
   - Gradient: Difference of gradients

**Handles nesting**: Composites can contain other composites

#### Context Wrappers (~50 lines)
**Adapt calculators to objective/constraint contexts**

1. **`objective_wrapper()`**:
   - Handles maximize vs minimize (negates for maximize)
   - Returns scipy-compatible (func, jac) tuple

2. **`constraint_wrapper()`**:
   - Handles cap vs floor (negates for cap)
   - Returns scipy constraint dict with type='ineq'

**When to look here**:
- Understanding metric calculations
- Debugging gradient issues
- Adding new metric types
- Investigating numerical accuracy

---

### Efficient Frontier (`efficient_frontier.py`) - 91 lines
**Purpose**: Generate efficient frontier by varying constraints

**Key function**: `generate_efficient_frontier()`

**Algorithm**:
1. Preprocess base optimization once (for efficiency)
2. Generate threshold arrays using `np.linspace`
3. For each frontier point:
   - Deep copy preprocessed base
   - Update constraint thresholds
   - Run optimization
   - Collect result
4. Return EfficientFrontierResult with all results

**Features**:
- Parallel constraint variation (multiple constraints varied together)
- Supports both simple and FreqSev constraints
- Robust to individual optimization failures
- Efficient preprocessing (once, not per point)

**Example**:
```python
frontier_input = EfficientFrontierInput(
    base_optimization=opt_input,
    constraint_variations=[
        ConstraintVariation(
            constraint_type="simple",
            constraint_name="max_risk",
            min_threshold=0.05,
            max_threshold=0.15
        )
    ],
    n_points=11
)

result = generate_efficient_frontier(frontier_input)
print(f"Generated {result.n_successful}/{len(result.optimization_results)} successful points")
```

**When to look here**:
- Generating efficient frontiers
- Understanding constraint variation
- Debugging frontier issues

---

## 🎯 Common Usage Patterns

### Basic Optimization
```python
from pop import (
    OptimizationInput, ObjectiveSpec, SimpleConstraint,
    MeanMetric, StdMetric, BoundsSpec, optimize
)
from pal.variables import ProteusVariable
from pal import StochasticScalar

# 1. Create portfolio variable
portfolio = ProteusVariable("item", {
    "asset1": StochasticScalar([100, 110, 90]),
    "asset2": StochasticScalar([200, 220, 180])
})

# 2. Define objective
objective = ObjectiveSpec(
    objective_value=portfolio,
    metric=MeanMetric(),
    direction="maximize"
)

# 3. Add constraint
risk_constraint = SimpleConstraint(
    constraint_value=portfolio,
    threshold=15.0,
    direction="cap",
    metric=StdMetric(),
    name="max_risk"
)

# 4. Create optimization input
opt_input = OptimizationInput(
    item_ids=["asset1", "asset2"],
    objective=objective,
    current_shares={"asset1": 50, "asset2": 50},
    simple_constraints=[risk_constraint],
    share_bounds={
        "asset1": BoundsSpec(lower=0, upper=100),
        "asset2": BoundsSpec(lower=0, upper=100)
    }
)

# 5. Preprocess and optimize
preprocessed = opt_input.preprocess()
result = optimize(preprocessed)

# 6. Check results
if result.success:
    print(f"Optimal: {result.optimal_shares}")
```

### Composite Metrics (Sharpe Ratio)
```python
from pop import RatioMetric, MeanMetric, StdMetric

# Define Sharpe-like ratio
sharpe = RatioMetric(
    numerator=MeanMetric(),
    denominator=StdMetric()
)

objective = ObjectiveSpec(
    objective_value=portfolio,
    metric=sharpe,
    direction="maximize"
)
```

### FreqSev Constraints
```python
from pop import FreqSevConstraint
from pal import FreqSevSims
import numpy as np

# Create loss variable (CRITICAL: same sim_index for all assets!)
sim_index = np.array([1, 2, 2, 3, 4], dtype=int)
losses = ProteusVariable("item", {
    "asset1": FreqSevSims(
        sim_index=sim_index,
        values=np.array([500, 700, 600, 800, 550]),
        n_sims=5
    ),
    "asset2": FreqSevSims(
        sim_index=sim_index,  # MUST be identical!
        values=np.array([1500, 2000, 1800, 2200, 1600]),
        n_sims=5
    )
})

# Constrain mean loss
loss_constraint = FreqSevConstraint(
    constraint_value=losses,
    threshold=1200.0,
    direction="cap",
    metric=MeanMetric(),
    name="max_mean_loss"
)
```

---

## 🔍 Debugging Guide

### Validation Errors
**File**: `models.py`
- Check field types and constraints
- Verify percentile ranges (0-100)
- Ensure lower < upper for bounds and percentiles

### Optimization Failures
**File**: `scipy_interface.py`
- Check `result.message` for scipy error
- Verify constraints are not conflicting
- Check if initial guess is feasible
- Review bounds for reasonableness

### Gradient Issues
**File**: `transforms.py`
- Verify data types (StochasticScalar vs FreqSevSims)
- Check for NaN or infinite values
- Test with numerical differentiation
- Verify covariance matrix is valid

### FreqSev Errors
**Files**: `models.py`, `transforms.py`
- **CRITICAL**: Verify identical `sim_index` arrays
- Check `n_sims` matches across all FreqSevSims
- Ensure values array length matches sim_index length

### Preprocessing Errors
**File**: `models.py` (OptimizationInput.preprocess)
- Verify item_ids match across all components
- Check simulation consistency
- Ensure all required fields are set

---

## 📊 Performance Considerations

### Expensive Operations
1. **SpreadVar gradient**: Numerical differentiation (O(n²) with n = items)
2. **Covariance calculation**: O(n_sims × n_items²)
3. **Percentile masking**: O(n_sims log n_sims) for sorting

### Optimization Tips
1. **Reuse preprocessed input**: Preprocess once, optimize many times
2. **Use analytical gradients**: Much faster than numerical
3. **Efficient frontier**: Preprocesses once, then varies thresholds
4. **Reasonable tolerances**: Default tolerances balance speed vs accuracy

---

## 🛠️ Extension Points

### Adding New Metrics
1. Create Pydantic model in `models.py`
2. Implement calculator in `transforms.py`
3. Add dispatch case in `create_metric_calculator()`
4. Export from `__init__.py`
5. Add tests in `tests/test_metric_calculations.py`

### Adding New Constraint Types
1. Create constraint model in `models.py`
2. Add preprocessing in `OptimizationInput._align_*_constraints()`
3. Handle in `scipy_interface.py` constraint loop
4. Export from `__init__.py`
5. Add tests

### Customizing Scipy Options
**File**: `scipy_interface.py`
- Modify `minimize()` call parameters
- Change method from SLSQP to others
- Adjust tolerance values
- Add callback functions

---

## 📚 Related Documentation

- **Test Guide**: `/tests/README.md` - Comprehensive test documentation
- **Project README**: `/README.md` - High-level overview
- **Copilot Instructions**: `/.github/copilot-instructions.md` - Development guidelines
- **Design Docs**: `/temp/` - Architectural decisions (not committed)

---

## ✨ Code Quality Standards

All code in this package meets:
- ✅ Comprehensive docstrings (module, class, function)
- ✅ Type hints throughout
- ✅ Pydantic validation with clear error messages
- ✅ Frozen models where appropriate (immutability)
- ✅ Efficient mathematical implementations
- ✅ Well-tested (127 tests covering all functionality)

---

**Last Updated**: December 12, 2025
**Total Lines**: ~2,700 lines across 6 modules
**Test Coverage**: 127 tests passing
**New Feature**: Automatic problem scaling (autoscale) for robust convergence
