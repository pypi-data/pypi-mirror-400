# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-05

### Added
- Initial release of vecmbreak package
- `VECMBreak` class for structural break detection in VECMs
- `VECMBreakResults` class for storing and accessing estimation results
- Two estimation cases:
  - Case 1: Constant α, regime-specific β
  - Case 2: Regime-specific α and β
- Group LASSO screening with adaptive penalty selection
- Backward Elimination algorithm for break refinement
- Principal Component estimation for regime parameters
- Data generation functions:
  - `generate_dgp_case1()` - Case 1 DGP
  - `generate_dgp_case2()` - Case 2 DGP  
  - `generate_dgp_with_short_run()` - DGP with VAR dynamics
  - `simulate_vecm_breaks()` - Custom VECM simulation
- Utility functions:
  - `vec_operator()` - Column-major vectorization
  - `inv_vec_operator()` - Inverse vectorization
  - `normalize_cointegrating_vectors()` - β normalization
  - `check_stationarity()` - Companion matrix stationarity check
- Impulse Response Function computation
- Monte Carlo simulation tools
- Comprehensive test suite (44 tests)
- Full documentation and examples

### References
- Implementation based on Franjic, Mößler, and Schweikert (2025)
