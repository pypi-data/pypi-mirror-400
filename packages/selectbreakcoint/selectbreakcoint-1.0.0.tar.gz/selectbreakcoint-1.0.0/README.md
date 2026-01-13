# selectbreakcoint

[![PyPI version](https://badge.fury.io/py/selectbreakcoint.svg)](https://badge.fury.io/py/selectbreakcoint)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Multiple Structural Breaks in Cointegrating Regressions: A Model Selection Approach**

A Python implementation of the adaptive lasso methodology for detecting and estimating multiple structural breaks in cointegrating regressions, based on:

> Schmidt, A. and Schweikert, K. (2021). "Multiple structural breaks in cointegrating regressions: A model selection approach." *Studies in Nonlinear Dynamics & Econometrics*.

## Features

- **Structural Break Detection**: Detect multiple structural breaks in both intercept and slope coefficients of cointegrating regressions
- **Adaptive Lasso Estimation**: Oracle-efficient estimation using the adaptive lasso with proper treatment of non-stationary regressors
- **Cointegration Testing**: Residual-based tests for cointegration allowing for multiple structural breaks
- **Flexible Model Specification**:
  - Known breakpoint candidates (Section 2.1)
  - Diverging number of breakpoint candidates (Algorithm 1, Section 2.2)
- **Complete Critical Values**: Tables from Schmidt and Schweikert (2021) for statistical inference
- **Comparison Methods**: Gregory-Hansen and Hatemi-J tests for benchmarking

## Installation

```bash
pip install selectbreakcoint
```

Or install from source:

```bash
git clone https://github.com/merwanroudane/selectbreakcoint.git
cd selectbreakcoint
pip install -e .
```

## Quick Start

### Detecting Structural Breaks

```python
import numpy as np
from selectbreakcoint import AdaptiveLassoBreaks

# Generate cointegrated data with a structural break at t=100
np.random.seed(42)
T = 200
x = np.cumsum(np.random.randn(T))  # I(1) regressor

# y with break at t=100 (intercept: 2→4, slope: 2→4)
e = np.random.randn(T) * 0.5
y = np.where(
    np.arange(T) < 100,
    2 + 2 * x + e,
    4 + 4 * x + e
)

# Estimate structural breaks
model = AdaptiveLassoBreaks(max_breaks=2, trim=0.05)
result = model.fit(x, y)

print(result)
```

### Cointegration Testing with Structural Breaks

```python
from selectbreakcoint import CointegrationTest

# Test for cointegration allowing up to 2 structural breaks
test = CointegrationTest(max_breaks=2, test_type='adf')
result = test.test(x, y)

print(result)
print(f"Cointegrated at 5%? {result.is_cointegrated}")
```

### Using Known Breakpoint Candidates

```python
# If you have prior information about potential break dates
model = AdaptiveLassoBreaks(max_breaks=3)
result = model.fit(x, y, known_breaks=[0.25, 0.5, 0.75])

print(f"Detected breaks at: {result.break_fractions}")
```

## Methodology

### Algorithm 1: Diverging Number of Breakpoint Candidates

The package implements the three-step procedure from Section 2.2:

1. **Initial Lasso**: Apply plain lasso to the full model with all potential break points
2. **Adaptive Lasso**: Use adaptive weights to distinguish active from inactive breaks
3. **Post-Lasso OLS**: Final estimation with selected breaks

### Algorithm 2: Cointegration Testing

The cointegration test (Section 2.3) follows:

1. For each tuning parameter λ, estimate breaks using adaptive lasso
2. Re-estimate using post-lasso OLS
3. Test residuals using ADF or bias-corrected Z_t statistics
4. Select model specification minimizing the test statistic (infimum test)

### Critical Values

Critical values from Table 1 of Schmidt and Schweikert (2021) are included for:
- ADF-type test statistics
- Bias-corrected Z_t test statistics
- Maximum breaks: 1 to 6
- Sample sizes: 100, 200, 400, asymptotic
- Significance levels: 10%, 5%, 1%

## API Reference

### Main Classes

#### `AdaptiveLassoBreaks`

```python
AdaptiveLassoBreaks(
    max_breaks=1,       # Maximum number of structural breaks
    trim=0.05,          # Lateral trimming parameter
    min_obs=1,          # Minimum observations per regime
    n_lambda=100,       # Number of lambda values in grid
    gamma=1.0,          # Exponent for adaptive lasso weights
    penalty_type='bic_star',  # 'bic' or 'bic_star' (modified BIC)
    dynamic_lags=0      # Number of leads/lags for endogeneity correction
)
```

**Methods:**
- `fit(x, y, known_breaks=None)`: Estimate structural breaks
- `predict(x_new)`: Predict y values
- `get_residuals()`: Get model residuals

#### `CointegrationTest`

```python
CointegrationTest(
    max_breaks=1,       # Maximum number of structural breaks
    trim=0.05,          # Lateral trimming parameter
    test_type='adf',    # 'adf' or 'zt' (bias-corrected)
    lag_selection='aic',# 'aic', 'bic', or 'fixed'
    n_lambda=100,       # Number of lambda values
    dynamic_lags=0      # Leads/lags for endogeneity correction
)
```

**Methods:**
- `test(x, y)`: Perform cointegration test
- `is_cointegrated(significance=0.05)`: Check cointegration status
- `get_breaks()`: Get estimated break dates

### Result Classes

#### `BreakEstimationResult`

Contains:
- `n_breaks`: Number of detected breaks
- `break_fractions`: Break fractions τ ∈ (0, 1)
- `break_dates`: Break date indices
- `intercept_coefs`, `slope_coefs`: Baseline coefficients
- `intercept_changes`, `slope_changes`: Parameter changes
- `regime_intercepts`, `regime_slopes`: Regime-specific values
- `residuals`: Model residuals
- `bic`: BIC value

#### `CointegrationTestResult`

Contains:
- `test_statistic`: Test statistic value
- `critical_values`: Critical values at different significance levels
- `is_cointegrated`: Boolean for 5% significance
- `reject_null`: Dict of rejection decisions
- `break_fractions`, `break_dates`: Estimated breaks under alternative

### Utility Functions

```python
from selectbreakcoint import (
    get_critical_values,        # Retrieve critical values
    construct_break_indicators, # Build indicator matrices
    compute_bic,               # Standard BIC
    compute_modified_bic,      # Modified BIC for diverging parameters
    dynamic_augmentation,      # Leads/lags for endogeneity correction
    hausdorff_distance,        # Performance metric for Monte Carlo
)
```

## Examples

### Example 1: PPP Analysis (Empirical Application)

```python
import pandas as pd
from selectbreakcoint import AdaptiveLassoBreaks, CointegrationTest

# Load PPP data (nominal exchange rate and price ratio)
data = pd.read_csv('ppp_data.csv')
exchange_rate = data['ex'].values
price_ratio = data['p_us'] - data['p_uk']  # log price differential

# Test for cointegration with up to 6 breaks
test = CointegrationTest(max_breaks=6, dynamic_lags=2)
result = test.test(price_ratio.values, exchange_rate)

print(result)
print(f"\nBreak dates: {result.break_dates}")
```

### Example 2: Monte Carlo Simulation

```python
from selectbreakcoint import AdaptiveLassoBreaks
from selectbreakcoint.utils import hausdorff_distance, percentage_correct_estimation

def run_monte_carlo(n_reps=1000, T=200, true_breaks=[0.33, 0.67]):
    pce_list = []
    hd_list = []
    
    for _ in range(n_reps):
        # Generate DGP as in Equation (18)
        x = np.cumsum(np.random.randn(T))
        e = np.random.randn(T) * 2
        
        # True coefficients: μ=2, β=2 with changes of 2 at each break
        y = np.zeros(T)
        bp1, bp2 = int(0.33*T), int(0.67*T)
        y[:bp1] = 2 + 2*x[:bp1] + e[:bp1]
        y[bp1:bp2] = 4 + 4*x[bp1:bp2] + e[bp1:bp2]
        y[bp2:] = 6 + 6*x[bp2:] + e[bp2:]
        
        # Estimate
        model = AdaptiveLassoBreaks(max_breaks=4)
        result = model.fit(x, y)
        
        pce_list.append(1 if result.n_breaks == 2 else 0)
        hd_list.append(hausdorff_distance(result.break_fractions, true_breaks))
    
    print(f"PCE: {np.mean(pce_list)*100:.1f}%")
    print(f"Mean Hausdorff distance: {np.mean(hd_list)*T:.2f}")

run_monte_carlo()
```

## Comparison with R Implementation

This Python package is designed to be compatible with the original R code from Schmidt and Schweikert (2021). Key correspondences:

| R Function | Python Method |
|------------|---------------|
| `lasso.est()` | `AdaptiveLassoBreaks.fit()` |
| `ur.df()` | `adf_test()` |
| `pp()` | `phillips_perron_test()` |

## Dependencies

- NumPy >= 1.20.0
- SciPy >= 1.7.0
- scikit-learn >= 1.0.0
- pandas >= 1.3.0
- statsmodels >= 0.13.0

## Citation

If you use this package in your research, please cite:

```bibtex
@article{schmidt2021multiple,
  title={Multiple structural breaks in cointegrating regressions: A model selection approach},
  author={Schmidt, Alexander and Schweikert, Karsten},
  journal={Studies in Nonlinear Dynamics \& Econometrics},
  year={2021},
  publisher={De Gruyter}
}
```

## Author

**Dr. Merwan Roudane**
- Email: merwanroudane920@gmail.com
- GitHub: [https://github.com/merwanroudane/selectbreakcoint](https://github.com/merwanroudane/selectbreakcoint)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## References

- Schmidt, A. and Schweikert, K. (2021). Multiple structural breaks in cointegrating regressions: A model selection approach. *Studies in Nonlinear Dynamics & Econometrics*.
- Gregory, A.W. and Hansen, B.E. (1996). Residual-based tests for cointegration in models with regime shifts. *Journal of Econometrics*.
- Hatemi-J, A. (2008). Tests for cointegration with two unknown regime shifts. *Empirical Economics*.
- Zou, H. (2006). The adaptive lasso and its oracle properties. *Journal of the American Statistical Association*.
- Phillips, P.C.B. (1987). Time series regression with a unit root. *Econometrica*.
