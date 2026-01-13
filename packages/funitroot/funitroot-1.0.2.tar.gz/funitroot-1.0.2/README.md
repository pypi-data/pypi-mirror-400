# funitroot: Fourier Unit Root Tests

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.2-orange.svg)](https://pypi.org/project/funitroot/)

A comprehensive Python package for testing unit roots in time series with structural breaks using Fourier approximations. Implements the methodologies of Enders & Lee (2012) and Becker, Enders & Lee (2006).

## Features

- **Fourier ADF Test** (Enders & Lee, 2012): Tests for unit roots allowing for smooth structural breaks
- **Fourier KPSS Test** (Becker, Enders & Lee, 2006): Tests for stationarity with smooth breaks
- **F-tests for Linearity**: Test whether Fourier terms are statistically significant
- **Automatic Frequency Selection**: Optimal frequency selected via minimum SSR criterion
- **Proper P-value Computation**: Extrapolation beyond critical value bounds
- **Interactive Visualizations**: Beautiful plots using Plotly
- **Publication-Ready Output**: Results formatted for academic papers

## What's New in v1.0.2

- **Added F-tests for linearity**: Test H₀: γ₁ = γ₂ = 0 (no Fourier terms needed)
- **Fixed p-value computation**: Now properly extrapolates beyond 10% critical value
- **Corrected frequency selection**: Uses minimum SSR (matching original GAUSS code)
- **Improved validation**: Raises errors for invalid parameters instead of silent capping
- **Added standalone F-test functions**: `fourier_adf_f_test()` and `fourier_kpss_f_test()`

## Installation

```bash
pip install funitroot
```

Or install from source:

```bash
git clone https://github.com/merwanroudane/funitroot.git
cd funitroot
pip install -e .
```

## Quick Start

### Fourier ADF Test

```python
import numpy as np
from funitroot import fourier_adf_test

# Generate data with structural break
np.random.seed(42)
T = 200
t = np.arange(T)

# Stationary series with smooth mean shift (Fourier component)
y = 5 + 3 * np.sin(2 * np.pi * t / T) + np.random.randn(T) * 0.5

# Perform Fourier ADF test
result = fourier_adf_test(y, model='c', max_freq=3)
print(result.summary())
```

**Output:**
```
=================================================================
        Fourier ADF Unit Root Test Results
        Enders & Lee (2012) Economics Letters
=================================================================
Model: Constant
Sample size: 200
Maximum lag tested: 8
Maximum frequency: 3
Lag selection criterion: AIC
-----------------------------------------------------------------
Optimal frequency (k): 1
Optimal lag (p): 0
ADF statistic: -14.6971
P-value: 0.0010
-----------------------------------------------------------------
Critical values:
   1% : -4.3700 *
   5% : -3.7800 *
  10% : -3.4700
-----------------------------------------------------------------
F-test for linearity (H0: no Fourier terms needed):
  F-statistic: 104.2477
  Critical values: 1%=10.02, 5%=7.41, 10%=6.25
  → Reject linearity: Fourier terms ARE significant
-----------------------------------------------------------------
Conclusion: Reject null hypothesis of unit root
            at 5% significance level
=================================================================
```

### Fourier KPSS Test

```python
from funitroot import fourier_kpss_test

# Perform Fourier KPSS test
result = fourier_kpss_test(y, model='c', max_freq=3)
print(result.summary())

# For KPSS: Fail to reject = Evidence of stationarity
if not result.reject_null:
    print("Series is stationary around Fourier components")
```

### F-test for Linearity

The F-test determines whether Fourier terms are statistically significant. If not rejected, use standard ADF/KPSS instead.

```python
from funitroot import fourier_adf_test, fourier_adf_f_test

# Method 1: Via the main test object
result = fourier_adf_test(y, model='c', max_freq=3)
f_result = result.f_test_linearity()

print(f"F-statistic: {f_result.f_statistic:.4f}")
print(f"P-value: {f_result.pvalue:.4f}")
print(f"Reject linearity (use Fourier): {f_result.reject_null}")

# Method 2: Standalone function with specific k and p
f_result = fourier_adf_f_test(y, model='c', k=1, p=4)
```

### Complete Analysis Workflow

```python
import numpy as np
from funitroot import fourier_adf_test, fourier_kpss_test

def analyze_series(y, name="Series"):
    """Complete unit root analysis with Fourier tests."""
    print(f"\n{'='*60}")
    print(f"Analysis of: {name}")
    print('='*60)
    
    # Step 1: Fourier ADF test
    adf_result = fourier_adf_test(y, model='c', max_freq=5)
    f_adf = adf_result.f_test_linearity()
    
    print(f"\n[Fourier ADF Test]")
    print(f"  Statistic: {adf_result.statistic:.4f}")
    print(f"  P-value: {adf_result.pvalue:.4f}")
    print(f"  Optimal k: {adf_result.optimal_frequency}")
    print(f"  F-test (linearity): {f_adf.f_statistic:.2f} (p={f_adf.pvalue:.4f})")
    
    # Step 2: Fourier KPSS test
    kpss_result = fourier_kpss_test(y, model='c', max_freq=5)
    f_kpss = kpss_result.f_test_linearity()
    
    print(f"\n[Fourier KPSS Test]")
    print(f"  Statistic: {kpss_result.statistic:.6f}")
    print(f"  P-value: {kpss_result.pvalue:.4f}")
    print(f"  Optimal k: {kpss_result.optimal_frequency}")
    print(f"  F-test (linearity): {f_kpss.f_statistic:.2f} (p={f_kpss.pvalue:.4f})")
    
    # Step 3: Joint interpretation
    print(f"\n[Conclusion]")
    
    if f_adf.reject_null or f_kpss.reject_null:
        print("  Fourier terms are significant → Structural breaks present")
    else:
        print("  Fourier terms not significant → Consider standard tests")
    
    if adf_result.reject_null and not kpss_result.reject_null:
        print("  → Series is STATIONARY (both tests agree)")
    elif not adf_result.reject_null and kpss_result.reject_null:
        print("  → Series has UNIT ROOT (both tests agree)")
    elif not adf_result.reject_null and not kpss_result.reject_null:
        print("  → Inconclusive (ADF: unit root, KPSS: stationary)")
    else:
        print("  → Contradictory results (needs further analysis)")

# Example usage
np.random.seed(42)
T = 200
t = np.arange(T)

# Stationary with break
y_stationary = 5 + 3 * np.sin(2 * np.pi * t / T) + np.random.randn(T) * 0.5
analyze_series(y_stationary, "Stationary with Fourier break")

# Unit root (random walk)
y_random_walk = np.cumsum(np.random.randn(T))
analyze_series(y_random_walk, "Random Walk")
```

## Mathematical Background

### Fourier ADF Test (Enders & Lee, 2012)

The Fourier ADF test extends the standard ADF test by incorporating Fourier terms to capture smooth structural breaks:

**Test Equation:**
```
Δyₜ = α + δyₜ₋₁ + γ₁sin(2πkt/T) + γ₂cos(2πkt/T) + Σφᵢ Δyₜ₋ᵢ + εₜ
```

For model with trend (`model='ct'`):
```
Δyₜ = α + βt + δyₜ₋₁ + γ₁sin(2πkt/T) + γ₂cos(2πkt/T) + Σφᵢ Δyₜ₋ᵢ + εₜ
```

**Hypotheses:**
- H₀: δ = 0 (unit root)
- H₁: δ < 0 (stationary around Fourier components)

**Frequency Selection:** k is selected by minimizing the sum of squared residuals (SSR) over k ∈ {1, 2, ..., kmax}.

**F-test for Linearity:** Tests H₀: γ₁ = γ₂ = 0. If not rejected, standard ADF is appropriate.

### Fourier KPSS Test (Becker, Enders & Lee, 2006)

The Fourier KPSS test extends the standard KPSS test:

**Test Equation:**
```
yₜ = α + γ₁sin(2πkt/T) + γ₂cos(2πkt/T) + εₜ
```

For model with trend (`model='ct'`):
```
yₜ = α + βt + γ₁sin(2πkt/T) + γ₂cos(2πkt/T) + εₜ
```

**Hypotheses:**
- H₀: yₜ is stationary around Fourier components
- H₁: yₜ has a unit root

**Test Statistic:**
```
τ = (1/T²) × Σ Sₜ² / σ²_lr
```
where Sₜ = Σⱼ₌₁ᵗ êⱼ (partial sum of residuals) and σ²_lr is the long-run variance.

## API Reference

### FourierADF Class

```python
from funitroot import FourierADF

result = FourierADF(
    data,           # array-like: Time series data
    model='c',      # str: 'c' (constant) or 'ct' (constant + trend)
    max_lag=None,   # int: Maximum lag (default: 8)
    max_freq=5,     # int: Maximum frequency 1-5
    ic='aic'        # str: 'aic', 'bic', or 'tstat'
)

# Attributes
result.statistic          # float: Test statistic
result.pvalue             # float: P-value
result.optimal_frequency  # int: Selected frequency k
result.optimal_lag        # int: Selected lag p
result.critical_values    # dict: {'1%': ..., '5%': ..., '10%': ...}
result.reject_null        # bool: Reject unit root?

# Methods
result.summary()          # str: Formatted results
result.f_test_linearity() # FTestResult: F-test for Fourier terms
```

### FourierKPSS Class

```python
from funitroot import FourierKPSS

result = FourierKPSS(
    data,           # array-like: Time series data
    model='c',      # str: 'c' (level) or 'ct' (trend stationarity)
    max_freq=5,     # int: Maximum frequency 1-5
    lags='auto'     # str/int: Newey-West lags ('auto' or integer)
)

# Attributes
result.statistic          # float: KPSS statistic (τ)
result.pvalue             # float: P-value
result.optimal_frequency  # int: Selected frequency k
result.critical_values    # dict: {'1%': ..., '5%': ..., '10%': ...}
result.reject_null        # bool: Reject stationarity?

# Methods
result.summary()          # str: Formatted results
result.f_test_linearity() # FTestResult: F-test for Fourier terms
```

### Standalone F-test Functions

```python
from funitroot import fourier_adf_f_test, fourier_kpss_f_test

# F-test for Fourier ADF
f_result = fourier_adf_f_test(
    data,        # array-like: Time series
    model='c',   # str: 'c' or 'ct'
    k=1,         # int: Frequency to test
    p=0          # int: Number of lags
)

# F-test for Fourier KPSS
f_result = fourier_kpss_f_test(
    data,        # array-like: Time series
    model='c',   # str: 'c' or 'ct'
    k=1          # int: Frequency to test
)

# FTestResult attributes
f_result.f_statistic      # float: F-statistic
f_result.critical_values  # dict: Critical values
f_result.pvalue           # float: P-value
f_result.reject_null      # bool: Reject linearity?
f_result.frequency        # int: Tested frequency
```

### Convenience Functions

```python
from funitroot import fourier_adf_test, fourier_kpss_test

# Same as FourierADF() but returns result directly
result = fourier_adf_test(y, model='c', max_freq=5)

# Same as FourierKPSS() but returns result directly
result = fourier_kpss_test(y, model='c', max_freq=5)
```

## Visualization Functions

```python
from funitroot import (
    plot_series_with_fourier,
    plot_test_results,
    plot_frequency_search,
    plot_comparative_analysis,
    plot_residual_diagnostics
)

# Plot series with fitted Fourier components
plot_series_with_fourier(data, optimal_frequency, model='c')

# Plot test statistic with critical values
plot_test_results(test_result)

# Plot statistics across frequencies
plot_frequency_search(data, model='c', max_freq=5, test_type='adf')

# Compare ADF and KPSS results
plot_comparative_analysis(data, model='c', max_freq=5)

# Residual diagnostics
plot_residual_diagnostics(test_result)
```

## Critical Values

### Fourier ADF Critical Values (Enders & Lee, 2012)

**Model: Constant only (`model='c'`)**

| T     | k | 1%    | 5%    | 10%   |
|-------|---|-------|-------|-------|
| ≤150  | 1 | -4.42 | -3.81 | -3.49 |
| ≤150  | 2 | -3.97 | -3.27 | -2.91 |
| ≤150  | 3 | -3.77 | -3.07 | -2.71 |

**Model: Constant + Trend (`model='ct'`)**

| T     | k | 1%    | 5%    | 10%   |
|-------|---|-------|-------|-------|
| ≤150  | 1 | -4.95 | -4.35 | -4.05 |
| ≤150  | 2 | -4.69 | -4.05 | -3.71 |
| ≤150  | 3 | -4.45 | -3.78 | -3.44 |

### Fourier KPSS Critical Values (Becker et al., 2006)

**Model: Level stationarity (`model='c'`)**

| T     | k | 1%     | 5%     | 10%    |
|-------|---|--------|--------|--------|
| ≤250  | 1 | 0.2699 | 0.1720 | 0.1318 |
| ≤250  | 2 | 0.6671 | 0.4152 | 0.3150 |

**Model: Trend stationarity (`model='ct'`)**

| T     | k | 1%     | 5%     | 10%    |
|-------|---|--------|--------|--------|
| ≤250  | 1 | 0.0716 | 0.0546 | 0.0471 |
| ≤250  | 2 | 0.2022 | 0.1321 | 0.1034 |

## References

1. **Enders, W., and Lee, J. (2012)**  
   "The flexible Fourier form and Dickey-Fuller type unit root tests"  
   *Economics Letters*, 117, 196-199.

2. **Becker, R., Enders, W., and Lee, J. (2006)**  
   "A stationarity test in the presence of an unknown number of smooth breaks"  
   *Journal of Time Series Analysis*, 27(3), 381-409.

3. **Nazlioglu, S. (2019)**  
   GAUSS implementation (TSPDLIB)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Dr. Merwan Roudane**
- Email: merwanroudane920@gmail.com
- GitHub: https://github.com/merwanroudane/funitroot

## Citation

If you use this package in your research, please cite:

```bibtex
@software{funitroot2024,
  author = {Roudane, Merwan},
  title = {funitroot: Fourier Unit Root Tests for Python},
  version = {1.0.2},
  year = {2024},
  url = {https://github.com/merwanroudane/funitroot}
}
```

## Acknowledgments

This package implements the methods developed by:
- Walter Enders (University of Alabama)
- Junsoo Lee (University of Alabama)
- Ralf Becker (University of Manchester)

Based on the GAUSS implementation by Saban Nazlioglu (TSPDLIB).

## Support

If you encounter any issues or have questions, please open an issue on GitHub:
https://github.com/merwanroudane/funitroot/issues
