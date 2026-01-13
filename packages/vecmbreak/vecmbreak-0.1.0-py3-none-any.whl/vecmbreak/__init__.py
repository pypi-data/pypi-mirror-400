"""
VECMBreak: Multiple Structural Breaks in Vector Error Correction Models
========================================================================

A Python implementation of the methodology proposed by Franjic, Mößler, and 
Schweikert (2025) for detecting and estimating multiple structural breaks 
in Vector Error Correction Models using Group LASSO with Backward Elimination.

This package provides tools for:
- Detecting multiple structural breaks in VECMs
- Estimating regime-specific cointegrating vectors and adjustment coefficients
- Computing impulse response functions with structural breaks
- Post-detection inference and coverage analysis
- Monte Carlo simulation for method evaluation

Main Classes
------------
VECMBreak : Main estimator class for structural break detection
VECMBreakResults : Container for estimation results
GroupLassoBreakDetector : First-step Group LASSO estimator
BackwardElimination : Second-step backward elimination algorithm
PrincipalComponentEstimator : Coefficient estimation via principal components

References
----------
Franjic, D., Mößler, M., & Schweikert, K. (2025). Multiple Structural Breaks 
in Vector Error Correction Models. University of Hohenheim.

Chan, N.H., Yau, C.Y., & Zhang, R.M. (2014). Group LASSO for Structural Break 
Time Series. Journal of the American Statistical Association, 109, 590-599.

Schweikert, K. (2025). Detecting Multiple Structural Breaks in Systems of 
Linear Regression Equations. Oxford Bulletin of Economics and Statistics.

Authors
-------
Franjic, D., Mößler, M., & Schweikert, K.
University of Hohenheim
"""

__version__ = "0.1.0"
__author__ = "Franjic, Mößler, Schweikert"
__email__ = "vecmbreak@example.com"

from .vecm_break import (
    VECMBreak,
    VECMBreakResults,
    fit_vecm_breaks,
)

from .group_lasso import (
    GroupLassoBreakDetector,
)

from .backward_elimination import (
    BackwardElimination,
)

from .principal_component import (
    PrincipalComponentEstimator,
)

from .data_generation import (
    simulate_vecm_breaks,
    generate_dgp_case1,
    generate_dgp_case2,
    generate_dgp_with_short_run,
    monte_carlo_simulation,
)

from .irf import (
    compute_irf,
    compute_regime_irf,
    plot_irf,
)

from .utils import (
    normalize_cointegrating_vectors,
    compute_information_criterion,
    frisch_waugh_projection,
)

from .inference import (
    compute_standard_errors,
    compute_coverage_rates,
    post_detection_inference,
)

__all__ = [
    # Main classes
    "VECMBreak",
    "VECMBreakResults",
    "fit_vecm_breaks",
    "GroupLassoBreakDetector",
    "BackwardElimination",
    "PrincipalComponentEstimator",
    # Data generation
    "simulate_vecm_breaks",
    "generate_dgp_case1",
    "generate_dgp_case2",
    "generate_dgp_with_short_run",
    "monte_carlo_simulation",
    # Impulse response functions
    "compute_irf",
    "compute_regime_irf",
    "plot_irf",
    # Utilities
    "normalize_cointegrating_vectors",
    "compute_information_criterion",
    "frisch_waugh_projection",
    # Inference
    "compute_standard_errors",
    "compute_coverage_rates",
    "post_detection_inference",
]
