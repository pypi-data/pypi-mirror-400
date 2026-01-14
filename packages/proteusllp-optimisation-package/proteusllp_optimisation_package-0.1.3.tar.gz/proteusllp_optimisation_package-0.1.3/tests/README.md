# Test Suite Guide

This directory contains comprehensive tests for the Proteus Portfolio Optimizer. The test suite is organized by functionality and complexity, making it easy to find relevant tests and understand the system's capabilities.

## 📊 Test Statistics

- **Total Tests**: 127
- **Test Files**: 7
- **Test Classes**: ~40
- **Coverage**: Core optimization, metrics, constraints, efficient frontier, and integration scenarios

## 🗂️ Test Organization

### Foundation Tests (68 tests)

#### `test_models.py` - 34 tests
**Purpose**: Pydantic model validation and structure

**What it tests**:
- Model creation and field validation
- Type checking and constraint enforcement
- Serialization/deserialization
- Error handling for invalid inputs

**Key test classes**:
- `TestBoundsSpec`: Bounds validation
- `TestMetricModels`: Metric type validation
- `TestConstraintVariation`: Constraint variation specs
- `TestOptimizationDirection`: Direction enum validation
- `TestOptimizationInput`: Complete input validation
- `TestEfficientFrontierInput`: Frontier input validation

**When to look here**: When debugging input validation errors or understanding model constraints

---

#### `test_metric_calculations.py` - 17 tests
**Purpose**: Metric correctness - values and gradients

**What it tests**:
- Mean metric calculations
- Standard deviation calculations
- SpreadVar (percentile-based) calculations
- Gradient correctness for all metrics
- Edge cases (single simulation, zero variance)

**Key test classes**:
- `TestMeanMetricCalculations`: Mean value and gradient
- `TestStdMetricCalculations`: Std dev value and gradient
- `TestSpreadVarMetricCalculations`: SpreadVar value and gradient
- `TestMetricEdgeCases`: Boundary conditions

**When to look here**: When debugging metric calculations or gradient issues

---

#### `test_simple_optimization.py` - 16 tests
**Purpose**: Core optimization with StochasticScalar variables

**What it tests**:
- Basic optimization (maximize/minimize)
- Bounds enforcement
- Simple constraints (floor/cap)
- Constraint satisfaction and slack
- Optimization failures (infeasible problems)

**Key test classes**:
- `TestBasicOptimization`: Objective optimization without constraints
- `TestBoundsHandling`: Bounds enforcement
- `TestSimpleConstraints`: Floor and cap constraints
- `TestConstraintEvaluation`: Constraint results and slack
- `TestOptimizationResult`: Result structure and immutability
- `TestOptimizationFailures`: Handling infeasible problems

**When to look here**: When debugging basic optimization issues or understanding the optimization flow

---

#### `test_metric_functions_with_simulations.py` - 11 tests
**Purpose**: Verify calculator functions match ground truth

**What it tests**:
- Value functions match manual computation on weighted portfolios
- Gradient functions consistent with value functions
- Correct application of weights to simulation data

**Distinction from test_metric_calculations.py**:
- `test_metric_calculations.py`: Tests calculators produce reasonable results
- **This file**: Tests calculators match ground truth from manual simulation computation

**Key test classes**:
- `TestMeanCalculatorAgainstSimulations`: Mean calculator validation
- `TestStdCalculatorAgainstSimulations`: Std calculator validation
- `TestSpreadVarCalculatorAgainstSimulations`: SpreadVar calculator validation
- `TestGradientConsistencyWithValues`: Gradient-value consistency

**When to look here**: When debugging discrepancies between expected and actual metric values

---

### Advanced Feature Tests (39 tests)

#### `test_composite_metrics.py` - 20 tests
**Purpose**: Composite metrics (ratios, products, sums, differences)

**What it tests**:
- RatioMetric (e.g., Sharpe ratio: mean/std)
- ProductMetric (e.g., mean * std)
- SumMetric (e.g., mean + std)
- DifferenceMetric (e.g., mean - std)
- Nested composite metrics (e.g., (mean/std) + mean)
- Gradient correctness via numerical differentiation
- Use in optimization objectives

**Key test classes**:
- `TestRatioMetricCalculations`: Ratio metrics
- `TestProductMetricCalculations`: Product metrics
- `TestSumMetricCalculations`: Sum metrics
- `TestDifferenceMetricCalculations`: Difference metrics
- `TestNestedCompositeMetrics`: Nested combinations
- `TestCompositeMetricsInOptimization`: Using composites in optimization
- `TestCompositeMetricEdgeCases`: Edge cases and error handling

**When to look here**: When working with Sharpe ratios or other composite metrics

---

#### `test_freqsev_constraints.py` - 12 tests
**Purpose**: FreqSev (frequency-severity) constraint optimization

**What it tests**:
- Basic FreqSev constraints (floor/cap on mean)
- Multiple independent FreqSev constraints
- FreqSev + simple constraints combined
- Identical and similar losses across assets
- Conflicting and infeasible constraints
- Edge cases (zero losses, extreme values)

**FreqSevSims structure reminder**:
- `sim_index`: Maps each event to its simulation number
- `values`: Severity values for each event
- `n_sims`: Total number of simulations
- **CRITICAL**: All FreqSevSims in a ProteusVariable MUST have IDENTICAL sim_index arrays

**Key test classes**:
- `TestFreqSevBasicConstraints`: Basic FreqSev functionality
- `TestFreqSevMultipleConstraints`: Multiple FreqSev constraints
- `TestFreqSevIdenticalAndSimilarLosses`: Handling similar loss distributions
- `TestFreqSevEdgeCases`: Boundary conditions
- `TestFreqSevFailureCases`: Conflicting/infeasible constraints

**When to look here**: When working with loss constraints or FreqSev simulations

---

#### `test_efficient_frontier.py` - 6 tests
**Purpose**: Efficient frontier generation

**What it tests**:
- Single constraint variation (classic efficient frontier)
- Multiple parallel constraint variations
- FreqSev constraints in frontier
- Narrow threshold ranges
- Failure handling
- Result properties and validation

**Key test classes**:
- `TestBasicEfficientFrontier`: Single constraint variation
- `TestMultipleConstraintVariations`: Parallel constraint sweeps
- `TestFreqSevEfficientFrontier`: FreqSev in frontier
- `TestEfficientFrontierEdgeCases`: Edge cases
- `TestEfficientFrontierResultProperties`: Result validation

**When to look here**: When generating efficient frontiers or debugging frontier issues

---

### Integration Tests (11 tests)

#### `test_integration.py` - 11 tests
**Purpose**: End-to-end workflows and realistic scenarios

**What it tests**:
- Mixed constraint types (simple + FreqSev)
- Composite metrics in constraints (not just objectives)
- Large portfolios (10+ assets)
- Complete API workflow (input → preprocess → optimize → result)
- Efficient frontier with complex setups
- Real-world scenarios (risk parity, tail risk optimization)

**Key test classes**:
- `TestMixedConstraintTypes`: Combining simple and FreqSev constraints
- `TestCompositeMetricsInConstraints`: Sharpe ratio as constraint
- `TestLargePortfolio`: Scalability testing (10 assets)
- `TestFullAPIWorkflow`: Complete workflow validation
- `TestEfficientFrontierIntegration`: Frontier with complex setups
- `TestRealWorldScenarios`: Realistic portfolio strategies

**When to look here**: When understanding how features work together or validating complete workflows

---

## 🎯 Finding the Right Tests

### By Use Case

| Use Case | Relevant Test File(s) |
|----------|----------------------|
| Basic optimization | `test_simple_optimization.py` |
| Input validation | `test_models.py` |
| Metric calculations | `test_metric_calculations.py`, `test_metric_functions_with_simulations.py` |
| Sharpe ratio / composite metrics | `test_composite_metrics.py` |
| Loss constraints | `test_freqsev_constraints.py` |
| Efficient frontier | `test_efficient_frontier.py` |
| End-to-end workflows | `test_integration.py` |

### By Component

| Component | Test Coverage |
|-----------|--------------|
| Pydantic Models | `test_models.py` (34 tests) |
| Metrics (Mean, Std, SpreadVar) | `test_metric_calculations.py` (17 tests) |
| Composite Metrics | `test_composite_metrics.py` (20 tests) |
| Optimization Engine | `test_simple_optimization.py` (16 tests) |
| FreqSev Constraints | `test_freqsev_constraints.py` (12 tests) |
| Efficient Frontier | `test_efficient_frontier.py` (6 tests) |
| Integration | `test_integration.py` (11 tests) |
| Calculator Functions | `test_metric_functions_with_simulations.py` (11 tests) |

### By Complexity

1. **Start here**: `test_models.py` - Understand data structures
2. **Then**: `test_metric_calculations.py` - Learn how metrics work
3. **Next**: `test_simple_optimization.py` - See basic optimization
4. **Advanced**: `test_composite_metrics.py`, `test_freqsev_constraints.py` - Complex features
5. **Frontier**: `test_efficient_frontier.py` - Multi-point optimization
6. **Real world**: `test_integration.py` - Complete scenarios

---

## 🏃 Running Tests

### Run All Tests
```bash
python3 -m pytest tests/ -v
```

### Run Specific Test File
```bash
python3 -m pytest tests/test_simple_optimization.py -v
```

### Run Specific Test Class
```bash
python3 -m pytest tests/test_simple_optimization.py::TestBasicOptimization -v
```

### Run Specific Test Function
```bash
python3 -m pytest tests/test_simple_optimization.py::TestBasicOptimization::test_maximize_mean_return -v
```

### Run Tests Matching Pattern
```bash
python3 -m pytest tests/ -k "freqsev" -v  # All FreqSev tests
python3 -m pytest tests/ -k "metric" -v   # All metric tests
```

### Run with Coverage
```bash
python3 -m pytest tests/ --cov=optimizer --cov-report=html
```

---

## 📝 Test Naming Conventions

### Test Files
- `test_<feature>.py` - Tests for specific feature
- Focus on one major component or concept per file

### Test Classes
- `Test<Component><Aspect>` - e.g., `TestMeanMetricCalculations`
- Organized by functionality within the feature

### Test Functions
- `test_<what>_<scenario>` - e.g., `test_maximize_mean_return`
- Descriptive names that explain what's being tested
- Each test has a docstring explaining the scenario

---

## 🔍 Understanding Test Results

### Success Indicators
- ✅ All assertions pass
- ✅ No exceptions raised
- ✅ Results within expected tolerances (typically 1e-6)

### Common Failure Patterns
1. **Validation errors**: Check `test_models.py` for similar patterns
2. **Gradient mismatches**: Look at `test_metric_calculations.py` gradient tests
3. **Optimization failures**: Review `TestOptimizationFailures` class
4. **FreqSev errors**: Check FreqSevSims structure in `test_freqsev_constraints.py`

### Debugging Tips
- Run with `-v` flag for verbose output
- Use `--tb=short` for shorter tracebacks
- Check docstrings for expected behavior
- Look at similar tests for patterns

---

## 🛠️ Test Development Guidelines

### Adding New Tests

1. **Choose the right file**: Based on feature being tested
2. **Follow naming conventions**: Descriptive names with docstrings
3. **Keep tests focused**: One concept per test
4. **Use realistic data**: Representative of actual use cases
5. **Test edge cases**: Boundary conditions, errors, etc.

### Test Structure Pattern
```python
def test_<description>(self):
    """Docstring explaining what this tests and why."""
    # 1. Setup: Create test data
    # 2. Execute: Run the functionality
    # 3. Assert: Verify results
    # 4. Optional: Additional validation
```

### Good Test Characteristics
- **Independent**: Can run in any order
- **Repeatable**: Same results every time
- **Fast**: Complete in < 1 second (most tests)
- **Clear**: Name and docstring explain purpose
- **Focused**: Tests one thing well

---

## 📚 Additional Resources

- **Project README**: `/README.md` - High-level overview
- **GitHub Copilot Instructions**: `/.github/copilot-instructions.md` - Development guidelines
- **Architecture Docs**: `/temp/` - Design documents (not committed)
- **Optimizer Package**: `/optimizer/` - Source code with comprehensive docstrings

---

## ✨ Test Quality Standards

All tests in this suite meet the following standards:
- ✅ Comprehensive docstrings (file, class, function level)
- ✅ Clear, descriptive naming
- ✅ Realistic test data (real PAL objects when possible)
- ✅ Proper error validation
- ✅ Numerical tolerance handling (typically 1e-6)
- ✅ Fast execution (< 2 seconds total suite time)

---

**Last Updated**: November 28, 2025
**Total Test Count**: 127 tests across 7 files
