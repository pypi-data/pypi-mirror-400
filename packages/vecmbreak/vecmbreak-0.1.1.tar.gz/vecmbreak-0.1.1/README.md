# vecmbreak

[![PyPI version](https://badge.fury.io/py/vecmbreak.svg)](https://badge.fury.io/py/vecmbreak)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Multiple Structural Break Detection in Vector Error Correction Models**

A Python implementation of the methodology from Franjic, Mößler, and Schweikert (2025) for detecting and estimating multiple structural breaks in Vector Error Correction Models (VECMs) using Group LASSO with Backward Elimination.

## Features

- **Two-Step Estimation**: Group LASSO screening followed by Backward Elimination refinement
- **Two Cases Supported**:
  - Case 1: Constant adjustment coefficients (α), regime-specific cointegrating vectors (β)
  - Case 2: Both α and β vary across regimes
- **Principal Component Estimation**: Efficient estimation of cointegrating parameters
- **Automatic Break Detection**: Data-driven selection of break locations and number of breaks
- **Impulse Response Functions**: Regime-specific IRF computation
- **Monte Carlo Simulation**: Tools for simulation studies and model validation
- **Paper-Style Output** (NEW in v0.1.1): Publication-quality tables and figures matching the original paper

## Installation

```bash
pip install vecmbreak
```

For plotting and DataFrame support (recommended):

```bash
pip install vecmbreak[plotting]
```

For development installation:

```bash
pip install vecmbreak[dev]
```

## Quick Start

```python
import numpy as np
from vecmbreak import VECMBreak, generate_dgp_case1

# Generate simulated data with one structural break
np.random.seed(42)
data = generate_dgp_case1(T=300, break_fractions=[0.5])
Y = data['Y']

# Detect structural breaks
model = VECMBreak(case=1, rank=1)
results = model.fit(Y)

# View results
print(results.summary())
print(f"Detected breaks: {results.breaks}")
print(f"Number of regimes: {results.n_regimes}")
```

## Paper-Style Output (NEW in v0.1.1)

The package now provides functions to generate publication-quality output matching the tables and figures in Franjic, Mößler, and Schweikert (2025).

### Monte Carlo Simulation Tables (Tables 1-2 Style)

```python
from vecmbreak import (
    monte_carlo_simulation, 
    format_monte_carlo_table,
    create_monte_carlo_dataframe
)

# Run Monte Carlo simulation
mc_results = monte_carlo_simulation(
    n_replications=1000,
    T=200,
    case=1,
    break_fractions=[0.5],
    seed=42
)

# Format as paper-style table
true_params = {'break_fractions': [0.5]}
print(format_monte_carlo_table(mc_results, true_params, case=1))

# Or export to DataFrame for LaTeX
df = create_monte_carlo_dataframe(mc_results, true_params)
print(df.to_latex())
```

Output format matches Table 1 from the paper:
```
================================================================================
Monte Carlo Simulation Results
================================================================================
Number of replications: 1000
True number of breaks: 1
True break fractions: τ1=0.50
--------------------------------------------------------------------------------
pce: 95.4%

Estimated Break Fractions:
  τ1: 0.502 (0.037)

Coefficient Estimates (mean, std):
...
================================================================================
```

### Estimation Results Tables (Tables 4-6 Style)

```python
from vecmbreak import VECMBreak, format_estimation_results

# Fit model
model = VECMBreak(case=2, rank=2)
results = model.fit(Y)

# Paper-style output
print(format_estimation_results(
    results,
    variable_names=['r10y', 'r5y', 'r1y'],
    title="Term Structure Model Results"
))
```

### Time Series Plots (Figure 1 Style)

```python
from vecmbreak import plot_time_series

# Plot with structural break markers
fig = plot_time_series(
    Y, 
    breaks=results.breaks,
    variable_names=['10-year', '5-year', '1-year'],
    title='US Interest Rates with Structural Breaks'
)
fig.savefig('time_series.png', dpi=300)
```

### IRF Grid Plots (Figure 2 Style)

```python
from vecmbreak import compute_irf, plot_irf_grid

# Compute IRFs
irfs = compute_irf(results, horizon=30)

# Create N×N grid plot
fig = plot_irf_grid(
    irfs['irf'],
    variable_names=['y10', 'y5', 'y1'],
    title='Impulse Response Functions'
)
fig.savefig('irf_grid.png', dpi=300)
```

### Full Analysis Report

```python
from vecmbreak import generate_full_report

# Generate comprehensive report
report = generate_full_report(
    results, Y,
    variable_names=['r10y', 'r5y', 'r1y'],
    include_plots=True,
    save_dir='./results/'
)
print(report)
```

## Detailed Usage

### Basic Break Detection

```python
from vecmbreak import VECMBreak, fit_vecm_breaks

# Method 1: Using the class
model = VECMBreak(
    case=2,              # Both α and β change
    rank=1,              # Cointegration rank
    k_ar=2,              # VAR lag order
    deterministic='c',   # Include constant
    max_breaks=5         # Maximum breaks to consider
)
results = model.fit(Y)

# Method 2: Using convenience function
results = fit_vecm_breaks(Y, rank=1, case=2)
```

### Accessing Results

```python
# Break locations
print(results.breaks)        # [100, 200] - break indices
print(results.break_dates)   # Alias for breaks

# Estimated parameters
print(results.alpha)         # Adjustment coefficients
print(results.beta)          # Cointegrating vectors (list, one per regime)

# Model diagnostics
print(results.n_breaks)      # Number of detected breaks
print(results.n_regimes)     # Number of regimes
print(results.ic_value)      # Information criterion value
print(results.residuals)     # Model residuals

# Export to dictionary
results_dict = results.to_dict()
```

### Data Generation for Simulation

```python
from vecmbreak import (
    generate_dgp_case1,
    generate_dgp_case2,
    generate_dgp_with_short_run,
    simulate_vecm_breaks
)

# Case 1: Only β changes at breaks
data1 = generate_dgp_case1(
    T=300, 
    break_fractions=[0.33, 0.67],  # Two breaks
    sigma_u=1.0,
    seed=42
)

# Case 2: Both α and β change
data2 = generate_dgp_case2(
    T=300,
    break_fractions=[0.5],
    seed=42
)

# With short-run dynamics
data3 = generate_dgp_with_short_run(
    T=300,
    break_fractions=[0.5],
    k_ar=2,  # VAR(2) short-run dynamics
    seed=42
)

# Custom simulation
alpha_list = [np.array([[-0.3], [0.2]]), np.array([[-0.5], [0.3]])]
beta_list = [np.array([[1.0], [-1.0]]), np.array([[1.0], [-0.8]])]

Y, info = simulate_vecm_breaks(
    T=300,
    N=2,
    alpha_list=alpha_list,
    beta_list=beta_list,
    breaks=[150],
    seed=42
)
```

### Impulse Response Functions

```python
from vecmbreak import compute_irf, plot_irf

# Compute IRFs for each regime
irfs = compute_irf(results, horizon=20)

# Plot IRFs (requires matplotlib)
plot_irf(irfs, variable_names=['y1', 'y2', 'y3'])
```

### Monte Carlo Simulation

```python
from vecmbreak import monte_carlo_simulation

# Run Monte Carlo study
mc_results = monte_carlo_simulation(
    n_simulations=100,
    T=300,
    case=1,
    true_breaks=[150],
    seed=42
)

print(f"Break detection rate: {mc_results['detection_rate']:.2%}")
print(f"Mean break location error: {mc_results['mean_location_error']:.2f}")
```

## Methodology

The package implements the two-step procedure from Franjic, Mößler, and Schweikert (2025):

### Step 1: Group LASSO Screening

The VECM is reformulated to allow for potential breaks at each time point:

$$\Delta Y_t = \Pi_t Y_{t-1} + \sum_{i=1}^{K-1} \Gamma_i \Delta Y_{t-i} + \mu_0 + u_t$$

where $\Pi_t = \alpha \beta'_t$ (Case 1) or $\Pi_t = \alpha_t \beta'_t$ (Case 2).

Group LASSO is applied with the modified BIC penalty:

$$\lambda_T = c \cdot T^{-3/4} \sqrt{\log(T)}$$

### Step 2: Backward Elimination

Starting from Group LASSO candidates, breaks are sequentially removed if removal improves the information criterion:

$$IC(m) = \log|\hat{\Sigma}_u| + p(m) \cdot \frac{\log(T)}{T}$$

where $p(m)$ is the effective number of parameters.

### Parameter Estimation

Regime-specific parameters are estimated via Principal Components:

1. For each regime, compute $\hat{\beta}_j$ from eigenvectors of $S_{11,j}^{-1} S_{10,j} S_{00,j}^{-1} S_{01,j}$
2. Estimate $\hat{\alpha}_j = S_{01,j} \hat{\beta}_j (\hat{\beta}'_j S_{11,j} \hat{\beta}_j)^{-1}$

## API Reference

### Main Classes

- `VECMBreak`: Main estimation class
- `VECMBreakResults`: Results container with summary methods

### Key Functions

- `fit_vecm_breaks()`: Convenience function for break detection
- `generate_dgp_case1()`: Generate Case 1 DGP data
- `generate_dgp_case2()`: Generate Case 2 DGP data
- `simulate_vecm_breaks()`: Custom VECM simulation
- `compute_irf()`: Impulse response function computation

### Utility Functions

- `vec_operator()`: Matrix vectorization (column-major)
- `inv_vec_operator()`: Inverse vectorization
- `normalize_cointegrating_vectors()`: β normalization
- `check_stationarity()`: Stationarity verification

## References

Franjic, D., Mößler, M., & Schweikert, K. (2025). *Multiple Structural Breaks in Vector Error Correction Models*. University of Hohenheim Working Paper.

## Citation

If you use this package in your research, please cite:

```bibtex
@article{franjic2025vecmbreak,
  title={Multiple Structural Breaks in Vector Error Correction Models},
  author={Franjic, D. and M{\"o}{\ss}ler, M. and Schweikert, K.},
  journal={University of Hohenheim Working Paper},
  year={2025}
}
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
