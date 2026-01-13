"""
VECMBreak: Main Estimator Class
===============================

This module provides the main VECMBreak class that integrates all components
for detecting and estimating multiple structural breaks in VECMs.

The two-step estimation procedure follows:
1. Group LASSO for initial break candidate detection
2. Backward Elimination Algorithm for break refinement
3. Principal Component Estimation for regime-specific coefficients

References
----------
Franjic, D., Mößler, M., & Schweikert, K. (2025). Multiple Structural Breaks 
    in Vector Error Correction Models. University of Hohenheim.
"""

import numpy as np
from numpy.linalg import inv, lstsq, norm
from scipy.linalg import sqrtm
from typing import Tuple, List, Optional, Dict, Union
import warnings

from .group_lasso import GroupLassoBreakDetector
from .backward_elimination import BackwardElimination
from .principal_component import PrincipalComponentEstimator
from .utils import (
    frisch_waugh_projection,
    normalize_cointegrating_vectors,
    compute_information_criterion
)


class VECMBreakResults:
    """
    Container for VECMBreak estimation results.
    
    Attributes
    ----------
    n_breaks : int
        Number of detected structural breaks.
    breaks : list of int
        Break locations (time indices).
    break_dates : list of int
        Alias for breaks (for compatibility).
    break_fractions : list of float
        Break locations as fractions of sample size.
    alpha : ndarray or list
        Adjustment coefficients (single or per regime).
    beta : list of ndarrays
        Cointegrating vectors per regime.
    Pi : list of ndarrays
        Π = αβ' matrices per regime.
    residuals : ndarray
        Model residuals.
    eigenvalues : ndarray or list
        Eigenvalues from reduced rank regression.
    ssr : float
        Sum of squared residuals.
    ic : float
        Information criterion value.
    case : int
        Estimation case (1 or 2).
    T : int
        Sample size.
    N : int
        Number of variables.
    r : int
        Cointegration rank.
    rank : int
        Alias for r (cointegration rank).
    """
    
    def __init__(self):
        self.n_breaks = None
        self.breaks = None
        self.break_fractions = None
        self.alpha = None
        self.beta = None
        self.Pi = None
        self.residuals = None
        self.eigenvalues = None
        self.ssr = None
        self.ic = None
        self.case = None
        self.T = None
        self.N = None
        self.r = None
        self.deterministic = None
        self._fitted = False
    
    @property
    def break_dates(self):
        """Alias for breaks (for compatibility)."""
        return self.breaks
    
    @property
    def ic_value(self):
        """Alias for ic (information criterion value)."""
        return self.ic
    
    @property
    def rank(self):
        """Alias for r (cointegration rank)."""
        return self.r
    
    @property
    def n_regimes(self):
        """Number of regimes (n_breaks + 1)."""
        if self.n_breaks is not None:
            return self.n_breaks + 1
        return None
    
    def summary(self) -> str:
        """
        Generate formatted summary of results.
        
        Returns
        -------
        summary : str
            Formatted summary string.
        """
        if not self._fitted:
            return "Model not fitted."
        
        lines = []
        lines.append("=" * 70)
        lines.append("VECMBreak Estimation Results")
        lines.append("=" * 70)
        lines.append(f"Sample size (T): {self.T}")
        lines.append(f"Number of variables (N): {self.N}")
        lines.append(f"Cointegration rank (r): {self.r}")
        lines.append(f"Estimation case: {self.case}")
        lines.append(f"Deterministic terms: {self.deterministic}")
        lines.append("")
        lines.append(f"Number of breaks detected: {self.n_breaks}")
        
        if self.n_breaks > 0:
            lines.append(f"Break locations: {self.breaks}")
            lines.append(f"Break fractions: {[f'{f:.3f}' for f in self.break_fractions]}")
        
        lines.append("")
        lines.append(f"Information criterion: {self.ic:.4f}")
        lines.append(f"Sum of squared residuals: {self.ssr:.4f}")
        lines.append("")
        
        # Report coefficients for each regime
        n_regimes = self.n_breaks + 1
        for j in range(n_regimes):
            lines.append(f"--- Regime {j + 1} ---")
            
            if j < len(self.breaks):
                if j == 0:
                    lines.append(f"Period: [1, {self.breaks[j]}]")
                else:
                    lines.append(f"Period: [{self.breaks[j-1] + 1}, {self.breaks[j]}]")
            else:
                if self.n_breaks > 0:
                    lines.append(f"Period: [{self.breaks[-1] + 1}, {self.T}]")
                else:
                    lines.append(f"Period: [1, {self.T}]")
            
            # Alpha
            if self.case == 1:
                if j == 0:
                    lines.append("α (constant):")
                    lines.append(self._format_array(self.alpha))
            else:
                lines.append(f"α_{j + 1}:")
                lines.append(self._format_array(self.alpha[j]))
            
            # Beta
            lines.append(f"β_{j + 1} (normalized):")
            lines.append(self._format_array(self.beta[j]))
            
            # Pi
            lines.append(f"Π_{j + 1} = α β':")
            lines.append(self._format_array(self.Pi[j]))
            
            lines.append("")
        
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def _format_array(self, arr, precision: int = 4) -> str:
        """Format numpy array for display."""
        if arr is None:
            return "  None"
        
        # Handle case where arr is a list
        if isinstance(arr, list):
            if len(arr) == 0:
                return "  []"
            elif len(arr) == 1:
                return self._format_array(arr[0], precision)
            else:
                lines = []
                for i, a in enumerate(arr):
                    lines.append(f"  [{i}]: " + self._format_array(a, precision).strip())
                return "\n".join(lines)
        
        # Convert to numpy array if needed
        arr = np.asarray(arr)
        
        return "  " + np.array2string(arr, precision=precision, 
                                       suppress_small=True,
                                       formatter={'float_kind': lambda x: f'{x:.{precision}f}'})
    
    def to_dict(self) -> Dict:
        """
        Convert results to dictionary.
        
        Returns
        -------
        results_dict : dict
            Dictionary representation of results.
        """
        return {
            'n_breaks': self.n_breaks,
            'breaks': self.breaks,
            'break_dates': self.breaks,  # Alias
            'break_fractions': self.break_fractions,
            'alpha': self.alpha,
            'beta': self.beta,
            'Pi': self.Pi,
            'residuals': self.residuals,
            'eigenvalues': self.eigenvalues,
            'ssr': self.ssr,
            'ic': self.ic,
            'case': self.case,
            'T': self.T,
            'N': self.N,
            'r': self.r,
            'rank': self.r,  # Alias
        }


class VECMBreak:
    """
    Multiple Structural Break Detection in Vector Error Correction Models.
    
    This class implements the two-step estimator from Franjic, Mößler, and 
    Schweikert (2025) for detecting and estimating multiple structural breaks
    in VECMs using Group LASSO with Backward Elimination.
    
    The procedure:
    1. Apply Frisch-Waugh to concentrate out short-run dynamics/deterministics
    2. Use Group LASSO to identify break candidates
    3. Apply Backward Elimination to refine breaks using IC
    4. Estimate regime-specific α and β via Principal Components
    
    Parameters
    ----------
    case : int, default=2
        Estimation case:
        - 1: Constant α, regime-specific β
        - 2: Regime-specific α and β (more flexible)
    rank : int or 'auto', default='auto'
        Cointegration rank. If 'auto', determined from data.
    k_ar : int, default=1
        VAR lag order (K in the paper).
    deterministic : str, default='c'
        Deterministic terms:
        - 'nc': No deterministic terms
        - 'c': Constant
        - 'ct': Constant and linear trend
    max_breaks : int, default=20
        Maximum number of breaks to consider.
    min_segment_length : int, default=None
        Minimum observations per regime. Default: 5 * N * (r + 1)
    lambda_T : float or 'auto', default='auto'
        Group LASSO regularization parameter.
    ic_criterion : str, default='bic_modified'
        Information criterion for backward elimination.
    verbose : bool, default=False
        Print progress information.
    
    Attributes
    ----------
    results_ : VECMBreakResults
        Container with all estimation results.
    n_breaks_ : int
        Number of detected breaks.
    breaks_ : list of int
        Break locations.
    alpha_ : ndarray or list
        Adjustment coefficients.
    beta_ : list of ndarrays
        Cointegrating vectors.
    
    References
    ----------
    Franjic, D., Mößler, M., & Schweikert, K. (2025). Multiple Structural Breaks 
        in Vector Error Correction Models. University of Hohenheim.
    
    Examples
    --------
    >>> from vecmbreak import VECMBreak
    >>> model = VECMBreak(case=2, rank=2, k_ar=2)
    >>> model.fit(Y)
    >>> print(model.results_.summary())
    
    >>> # Access individual results
    >>> print(f"Detected {model.n_breaks_} breaks at {model.breaks_}")
    """
    
    def __init__(
        self,
        case: int = 2,
        rank: Union[int, str] = "auto",
        k_ar: int = 1,
        deterministic: str = "c",
        max_breaks: int = 20,
        min_segment_length: Optional[int] = None,
        lambda_T: Union[float, str] = "auto",
        ic_criterion: str = "bic_modified",
        verbose: bool = False
    ):
        if case not in [1, 2]:
            raise ValueError("case must be 1 or 2")
        if deterministic not in ['nc', 'c', 'ct']:
            raise ValueError("deterministic must be 'nc', 'c', or 'ct'")
        
        self.case = case
        self._rank_param = rank  # Store original parameter
        self.k_ar = k_ar
        self.deterministic = deterministic
        self.max_breaks = max_breaks
        self.min_segment_length = min_segment_length
        self.lambda_T = lambda_T
        self.ic_criterion = ic_criterion
        self.verbose = verbose
        
        # Fitted attributes
        self.results_ = None
        self.n_breaks_ = None
        self.breaks_ = None
        self.alpha_ = None
        self.beta_ = None
        self._is_fitted = False
    
    @property
    def rank(self):
        """Cointegration rank (computed value after fitting, parameter before)."""
        if self.results_ is not None:
            return self.results_.r
        return self._rank_param
    
    # Properties to delegate to results_ for test compatibility
    @property
    def n_breaks(self):
        """Number of detected breaks (delegates to results_)."""
        if self.results_ is not None:
            return self.results_.n_breaks
        return None
    
    @property
    def breaks(self):
        """Break locations (delegates to results_)."""
        if self.results_ is not None:
            return self.results_.breaks
        return None
    
    @property
    def break_dates(self):
        """Break locations - alias for breaks (delegates to results_)."""
        if self.results_ is not None:
            return self.results_.breaks
        return None
    
    @property
    def alpha(self):
        """Adjustment coefficients (delegates to results_)."""
        if self.results_ is not None:
            return self.results_.alpha
        return None
    
    @property
    def beta(self):
        """Cointegrating vectors (delegates to results_)."""
        if self.results_ is not None:
            return self.results_.beta
        return None
    
    @property
    def r(self):
        """Cointegration rank (delegates to results_)."""
        if self.results_ is not None:
            return self.results_.r
        return None
    
    @property
    def n_regimes(self):
        """Number of regimes (delegates to results_)."""
        if self.results_ is not None:
            return self.results_.n_regimes
        return None
    
    @property
    def ic_value(self):
        """Information criterion value (delegates to results_)."""
        if self.results_ is not None:
            return self.results_.ic
        return None
    
    @property
    def residuals(self):
        """Model residuals (delegates to results_)."""
        if self.results_ is not None:
            return self.results_.residuals
        return None
    
    def summary(self):
        """Generate summary (delegates to results_)."""
        if self.results_ is not None:
            return self.results_.summary()
        raise ValueError("Model not fitted. Call fit() first.")
    
    def to_dict(self):
        """Convert to dictionary (delegates to results_)."""
        if self.results_ is not None:
            return self.results_.to_dict()
        raise ValueError("Model not fitted. Call fit() first.")
    
    def fit(
        self,
        Y: np.ndarray,
        exog: Optional[np.ndarray] = None
    ) -> "VECMBreak":
        """
        Fit the VECMBreak model to detect structural breaks.
        
        Parameters
        ----------
        Y : ndarray of shape (T, N)
            Endogenous variables in levels.
        exog : ndarray of shape (T, d), optional
            Exogenous variables (not implemented yet).
        
        Returns
        -------
        self : VECMBreak
            Fitted estimator.
        """
        Y = np.asarray(Y)
        if Y.ndim == 1:
            Y = Y.reshape(-1, 1)
        
        T, N = Y.shape
        
        if self.verbose:
            print(f"Fitting VECMBreak: T={T}, N={N}, case={self.case}")
        
        # Determine cointegration rank
        if self._rank_param == "auto":
            r = self._determine_rank(Y)
        else:
            r = self._rank_param
        
        if r >= N:
            raise ValueError(f"Cointegration rank ({r}) must be less than N ({N})")
        
        # Set minimum segment length
        if self.min_segment_length is None:
            self.min_segment_length = max(5 * N * (r + 1), 10)
        
        if self.verbose:
            print(f"Cointegration rank: {r}")
            print(f"Minimum segment length: {self.min_segment_length}")
        
        # Step 1: Prepare data
        delta_Y, Y_lag, Z_control, det = self._prepare_data(Y)
        
        # Step 2: Frisch-Waugh projection to concentrate out short-run dynamics
        if Z_control is not None and Z_control.shape[1] > 0:
            R0, R1 = frisch_waugh_projection(delta_Y, Y_lag, Z_control)
        else:
            R0, R1 = delta_Y, Y_lag
        
        if self.verbose:
            print(f"Data prepared: R0 shape={R0.shape}, R1 shape={R1.shape}")
        
        # Step 3: Group LASSO for break candidate detection
        if self.verbose:
            print("Running Group LASSO...")
        
        group_lasso = GroupLassoBreakDetector(
            lambda_T=self.lambda_T,
            verbose=self.verbose
        )
        group_lasso.fit(R0, R1, det)
        break_candidates = group_lasso.break_candidates_
        
        if self.verbose:
            print(f"Group LASSO found {len(break_candidates)} candidates")
        
        # Step 4: Backward Elimination for break refinement
        if self.verbose:
            print("Running Backward Elimination...")
        
        bea = BackwardElimination(
            criterion=self.ic_criterion,
            min_segment_length=self.min_segment_length,
            verbose=self.verbose
        )
        bea.fit(R0, R1, break_candidates, det)
        
        final_breaks = bea.breaks_
        
        if self.verbose:
            print(f"BEA retained {len(final_breaks)} breaks")
        
        # Step 5: Principal Component Estimation
        if self.verbose:
            print("Estimating coefficients...")
        
        pce = PrincipalComponentEstimator(
            case=self.case,
            rank=r
        )
        pce.fit(R0, R1, final_breaks, det)
        
        # Store results
        self._store_results(Y, R0, R1, final_breaks, pce, bea)
        
        # Store Y for prediction
        self._Y_fitted = Y.copy()
        
        if self.verbose:
            print("Fitting complete.")
            print(self.results_.summary())
        
        self._is_fitted = True
        
        return self
    
    def _determine_rank(self, Y: np.ndarray) -> int:
        """
        Determine cointegration rank using Johansen test.
        
        Parameters
        ----------
        Y : ndarray of shape (T, N)
            Data in levels.
        
        Returns
        -------
        rank : int
            Estimated cointegration rank.
        """
        try:
            from statsmodels.tsa.vector_ar.vecm import coint_johansen, select_coint_rank
            
            # Determine deterministic order for Johansen test
            if self.deterministic == 'nc':
                det_order = -1
            elif self.deterministic == 'c':
                det_order = 0
            else:  # 'ct'
                det_order = 1
            
            result = coint_johansen(Y, det_order=det_order, k_ar_diff=self.k_ar - 1)
            
            # Use trace test at 5% level
            N = Y.shape[1]
            for r in range(N):
                if result.trace_stat[r] < result.trace_stat_crit_vals[r, 1]:
                    return r
            
            return N - 1
            
        except ImportError:
            warnings.warn("statsmodels not available, using default rank=1")
            return 1
    
    def _prepare_data(
        self,
        Y: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Optional[np.ndarray]]:
        """
        Prepare data for VECM estimation.
        
        Constructs:
        - delta_Y: First differences ΔY_t
        - Y_lag: Lagged levels Y_{t-1}
        - Z_control: Control variables (lagged differences, deterministics)
        
        Parameters
        ----------
        Y : ndarray of shape (T, N)
            Data in levels.
        
        Returns
        -------
        delta_Y : ndarray of shape (T-K, N)
            First differences.
        Y_lag : ndarray of shape (T-K, N)
            Lagged levels.
        Z_control : ndarray of shape (T-K, p)
            Control variables.
        det : ndarray or None
            Deterministic terms for break detection.
        """
        T, N = Y.shape
        K = self.k_ar
        
        # First differences
        delta_Y = np.diff(Y, axis=0)  # Shape: (T-1, N)
        
        # Lagged levels (Y_{t-1})
        Y_lag = Y[:-1, :]  # Shape: (T-1, N)
        
        # Adjust for lag structure
        # Effective sample: t = K, ..., T-1 (indices in delta_Y: K-1, ..., T-2)
        T_eff = T - K
        
        # Build control variables (lagged differences)
        Z_parts = []
        
        if K > 1:
            for i in range(1, K):
                # ΔY_{t-i} for i = 1, ..., K-1
                delta_Y_lag_i = delta_Y[K - 1 - i:-i, :]
                Z_parts.append(delta_Y_lag_i)
        
        # Deterministic terms
        det = None
        if self.deterministic == 'c':
            const = np.ones((T_eff, 1))
            Z_parts.append(const)
            det = const
        elif self.deterministic == 'ct':
            const = np.ones((T_eff, 1))
            trend = np.arange(K, T).reshape(-1, 1)
            Z_parts.append(const)
            Z_parts.append(trend)
            det = np.hstack([const, trend])
        
        # Trim delta_Y and Y_lag to effective sample
        delta_Y = delta_Y[K - 1:, :]
        Y_lag = Y_lag[K - 1:, :]
        
        # Combine control variables
        if Z_parts:
            Z_control = np.hstack(Z_parts)
        else:
            Z_control = np.zeros((T_eff, 0))
        
        return delta_Y, Y_lag, Z_control, det
    
    def _store_results(
        self,
        Y: np.ndarray,
        R0: np.ndarray,
        R1: np.ndarray,
        breaks: List[int],
        pce: PrincipalComponentEstimator,
        bea: BackwardElimination
    ) -> None:
        """
        Store estimation results.
        
        Parameters
        ----------
        Y : ndarray
            Original data.
        R0, R1 : ndarrays
            Residual matrices.
        breaks : list
            Final break locations.
        pce : PrincipalComponentEstimator
            Fitted PCE.
        bea : BackwardElimination
            Fitted BEA.
        """
        T, N = Y.shape
        T_eff = R0.shape[0]
        r = pce.rank
        
        results = VECMBreakResults()
        results.T = T
        results.N = N
        results.r = r
        results.case = self.case
        results.deterministic = self.deterministic
        
        results.n_breaks = len(breaks)
        results.breaks = breaks
        results.break_fractions = [b / T_eff for b in breaks]
        
        results.alpha = pce.alpha_
        results.beta = pce.beta_
        results.Pi = pce.get_Pi_matrices()
        results.residuals = pce.residuals_
        results.eigenvalues = pce.eigenvalues_
        
        results.ssr = bea.ssr_
        results.ic = bea.ic_path_[-1] if bea.ic_path_ else np.nan
        
        results._fitted = True
        
        # Store in instance
        self.results_ = results
        self.n_breaks_ = results.n_breaks
        self.breaks_ = results.breaks
        self.alpha_ = results.alpha
        self.beta_ = results.beta
    
    def predict(
        self,
        Y: Optional[np.ndarray] = None,
        steps: int = 1
    ) -> np.ndarray:
        """
        Generate forecasts from the fitted VECM.
        
        Parameters
        ----------
        Y : ndarray of shape (T, N), optional
            Historical data. If None, uses stored data from fitting.
        steps : int, default=1
            Number of forecast steps.
        
        Returns
        -------
        forecasts : ndarray of shape (steps, N)
            Point forecasts.
        """
        if not self._is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")
        
        # Use stored data if Y not provided
        if Y is None:
            if not hasattr(self, '_Y_fitted') or self._Y_fitted is None:
                raise ValueError("No data available. Provide Y or refit the model.")
            Y = self._Y_fitted
        
        T, N = Y.shape
        r = self.results_.r
        
        forecasts = np.zeros((steps, N))
        Y_extended = np.vstack([Y, np.zeros((steps, N))])
        
        # Use the last regime's parameters for forecasting
        if self.case == 1:
            alpha = self.alpha_
        else:
            alpha = self.alpha_[-1]
        
        beta = self.beta_[-1]
        Pi = alpha @ beta.T
        
        for h in range(steps):
            t = T + h
            
            # Error correction term
            ec_term = Pi @ Y_extended[t - 1, :]
            
            # Simple random walk forecast + EC adjustment
            Y_extended[t, :] = Y_extended[t - 1, :] + ec_term
            forecasts[h, :] = Y_extended[t, :]
        
        return forecasts
    
    def compute_irf(
        self,
        periods: int = 20,
        steps: Optional[int] = None,
        regime: Optional[int] = None,
        orthogonalize: bool = True
    ) -> np.ndarray:
        """
        Compute impulse response functions.
        
        Parameters
        ----------
        periods : int, default=20
            Number of periods for IRF.
        steps : int, optional
            Alias for periods (for compatibility).
        regime : int, optional
            Regime for which to compute IRF. If None, uses last regime.
        orthogonalize : bool, default=True
            Whether to orthogonalize shocks.
        
        Returns
        -------
        irf : ndarray of shape (periods, N, N)
            IRF matrix. irf[h, i, j] is response of variable i 
            to shock in variable j at horizon h.
        """
        if not self._is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")
        
        # Allow steps as alias for periods
        if steps is not None:
            periods = steps
        
        from .irf import compute_irf
        
        if regime is None:
            regime = self.n_breaks_  # Last regime
        
        if self.case == 1:
            alpha = self.alpha_
        else:
            alpha = self.alpha_[regime]
        
        beta = self.beta_[regime]
        
        # Compute Pi = alpha @ beta'
        Pi = alpha @ beta.T
        
        # Get residual covariance from last regime
        residuals = self.results_.residuals
        Sigma = residuals.T @ residuals / len(residuals)
        
        # Compute IRF (returns horizons+1 periods including impact)
        irf_result = compute_irf(Pi, Sigma, horizons=periods, orthogonalize=orthogonalize)
        
        # Return only the first 'periods' elements (excluding impact period h=0)
        # to match user expectation of "steps" future periods
        return irf_result['irf'][1:periods+1]


def fit_vecm_breaks(
    Y: np.ndarray,
    case: int = 2,
    rank: int = 1,
    k_ar: int = 1,
    deterministic: str = "c",
    **kwargs
) -> VECMBreakResults:
    """
    Convenience function to fit VECMBreak model.
    
    Parameters
    ----------
    Y : ndarray of shape (T, N)
        Data in levels.
    case : int, default=2
        Estimation case.
    rank : int, default=1
        Cointegration rank.
    k_ar : int, default=1
        VAR lag order.
    deterministic : str, default='c'
        Deterministic terms.
    **kwargs
        Additional arguments passed to VECMBreak.
    
    Returns
    -------
    results : VECMBreakResults
        Estimation results.
    
    Examples
    --------
    >>> results = fit_vecm_breaks(Y, case=2, rank=2)
    >>> print(results.summary())
    """
    model = VECMBreak(
        case=case,
        rank=rank,
        k_ar=k_ar,
        deterministic=deterministic,
        **kwargs
    )
    model.fit(Y)
    
    return model.results_
