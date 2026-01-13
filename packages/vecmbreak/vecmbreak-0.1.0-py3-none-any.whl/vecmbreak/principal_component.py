"""
Principal Component Estimation for VECMs with Structural Breaks
================================================================

This module implements the principal component estimator for obtaining
regime-specific cointegrating vectors and adjustment coefficients
after structural breaks have been detected.

Following Andrade et al. (2005), the estimator handles two cases:
- Case 1: Constant α but regime-specific β
- Case 2: Regime-specific α and β

References
----------
Andrade, P., Bruneau, C., & Gregoir, S. (2005). Testing for the cointegration 
    rank when some cointegrating directions are changing. Journal of Econometrics, 
    124, 269-310.
Johansen, S. (1988). Statistical Analysis of Cointegration Vectors. 
    Journal of Economic Dynamics and Control, 12, 231-254.
Johansen, S. (1991). Estimation and Hypothesis Testing of Cointegration Vectors 
    in Gaussian Vector Autoregressive Models. Econometrica, 59, 1551-1580.
"""

import numpy as np
from numpy.linalg import eig, inv, lstsq, norm, svd, eigh
from scipy.linalg import sqrtm, pinv, fractional_matrix_power
from typing import Tuple, List, Optional, Dict, Union
import warnings


class PrincipalComponentEstimator:
    """
    Principal Component Estimator for cointegration analysis with breaks.
    
    This class implements the estimation procedure from Section 2.3 of
    Franjic, Mößler, and Schweikert (2025) for obtaining regime-specific
    estimates of α and β after break detection.
    
    The estimator handles two cases:
    
    Case 1 (constant α): Following Equation (12)-(15)
        - R0_t = α β̃' [R1_t^(0), ..., R1_t^(m̂)]' + e_t
        - β̃' = (β'_0, ..., β'_m̂)' contains regime-specific cointegrating vectors
        - α is constant across regimes
    
    Case 2 (varying α and β): Following Equation (16)-(18)
        - R0_t = diag(α_0, ..., α_m̂) × diag(β'_0, ..., β'_m̂) × R1_regime + e_t
        - Both α and β can vary across regimes
    
    Parameters
    ----------
    case : int, default=2
        Estimation case:
        - 1: Constant α, regime-specific β
        - 2: Regime-specific α and β
    rank : int, default=1
        Cointegration rank (number of cointegrating vectors).
    normalization : str, default='triangular'
        Normalization scheme for cointegrating vectors:
        - 'triangular': Phillips triangular normalization
        - 'orthogonal': Orthogonal normalization
    
    Attributes
    ----------
    alpha_ : ndarray or list of ndarrays
        Estimated adjustment coefficients.
        For Case 1: single (N, r) array
        For Case 2: list of (N, r) arrays, one per regime
    beta_ : list of ndarrays
        Estimated cointegrating vectors, one (N, r) array per regime.
    residuals_ : ndarray
        Estimation residuals.
    eigenvalues_ : ndarray
        Eigenvalues from the reduced rank regression.
    
    References
    ----------
    Andrade, P., Bruneau, C., & Gregoir, S. (2005). Testing for the cointegration 
        rank. Journal of Econometrics, 124, 269-310.
    
    Examples
    --------
    >>> pce = PrincipalComponentEstimator(case=2, rank=2)
    >>> pce.fit(R0, R1, breaks=[100, 200])
    >>> print(f"Alpha in regime 1: {pce.alpha_[0]}")
    >>> print(f"Beta in regime 1: {pce.beta_[0]}")
    """
    
    def __init__(
        self,
        case: int = 2,
        rank: int = 1,
        normalization: str = "triangular"
    ):
        if case not in [1, 2]:
            raise ValueError("case must be 1 or 2")
        
        self.case = case
        self.rank = rank
        self.normalization = normalization
        
        # Fitted attributes
        self.alpha_ = None
        self.beta_ = None
        self.residuals_ = None
        self.eigenvalues_ = None
        self.Sigma_e_ = None
        self.covariance_matrices_ = None
    
    def fit(
        self,
        R0: np.ndarray,
        R1: np.ndarray,
        breaks: List[int],
        deterministic: Optional[np.ndarray] = None
    ) -> Dict:
        """
        Estimate regime-specific cointegrating vectors and adjustment coefficients.
        
        Parameters
        ----------
        R0 : ndarray of shape (T, N)
            Residuals from regressing ΔY on control variables.
        R1 : ndarray of shape (T, N)
            Residuals from regressing Y_{t-1} on control variables.
        breaks : list of int
            Estimated break locations.
        deterministic : ndarray of shape (T, d), optional
            Deterministic terms (handled separately).
        
        Returns
        -------
        results : dict
            Dictionary containing 'alpha', 'beta', 'residuals', 'eigenvalues'.
        """
        T, N = R0.shape
        r = self.rank
        
        if r > N:
            raise ValueError(f"Cointegration rank ({r}) cannot exceed dimension ({N})")
        
        # Define regimes
        breaks = sorted(breaks)
        m = len(breaks)  # Number of breaks
        
        if m == 0:
            # No breaks - standard Johansen estimation
            self._fit_no_breaks(R0, R1)
            return self._get_results()
        
        # Define regime boundaries: t_0=0, t_1, ..., t_m, t_{m+1}=T
        regime_bounds = [0] + breaks + [T]
        n_regimes = len(regime_bounds) - 1
        
        if self.case == 1:
            self._fit_case1(R0, R1, regime_bounds)
        else:
            self._fit_case2(R0, R1, regime_bounds)
        
        # Apply normalization
        self._apply_normalization()
        
        # Compute residuals
        self._compute_residuals(R0, R1, regime_bounds)
        
        return self._get_results()
    
    def _get_results(self) -> Dict:
        """Return results as a dictionary."""
        return {
            'alpha': self.alpha_,
            'beta': self.beta_,
            'residuals': getattr(self, 'residuals_', None),
            'eigenvalues': getattr(self, 'eigenvalues_', None)
        }
    
    def _fit_no_breaks(
        self,
        R0: np.ndarray,
        R1: np.ndarray
    ) -> None:
        """
        Standard Johansen estimation without breaks.
        
        Parameters
        ----------
        R0, R1 : ndarrays
            Residual matrices.
        """
        T, N = R0.shape
        r = self.rank
        
        # Compute moment matrices
        S00 = R0.T @ R0 / T
        S01 = R0.T @ R1 / T
        S10 = R1.T @ R0 / T
        S11 = R1.T @ R1 / T
        
        # Solve generalized eigenvalue problem
        # S01 @ S11^{-1} @ S10 v = λ S00 v
        try:
            S11_inv = inv(S11)
            S00_inv_sqrt = fractional_matrix_power(S00, -0.5)
        except np.linalg.LinAlgError:
            S11_inv = pinv(S11)
            S00_inv_sqrt = pinv(sqrtm(S00))
        
        M = S00_inv_sqrt @ S01 @ S11_inv @ S10 @ S00_inv_sqrt
        
        eigenvalues, eigenvectors = eigh(M)
        # Sort in descending order
        idx = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]
        
        self.eigenvalues_ = eigenvalues
        
        # Extract r largest eigenvectors
        V = eigenvectors[:, :r]
        
        # Compute α and β
        S00_sqrt = sqrtm(S00)
        alpha = S00_sqrt @ V
        beta = S11_inv @ S10 @ alpha @ inv(alpha.T @ S00 @ alpha)
        
        self.alpha_ = alpha  # Single matrix for no breaks case
        self.beta_ = [beta]
        
        # Store covariance matrices
        self.covariance_matrices_ = {
            "S00": [S00],
            "S01": [S01],
            "S10": [S10],
            "S11": [S11]
        }
        
        # Compute residuals
        Pi = alpha @ beta.T
        fitted = R1 @ Pi.T
        self.residuals_ = R0 - fitted
    
    def _fit_case1(
        self,
        R0: np.ndarray,
        R1: np.ndarray,
        regime_bounds: List[int]
    ) -> None:
        """
        Fit Case 1: Constant α, regime-specific β.
        
        Following Equations (12)-(15) in the paper.
        
        Parameters
        ----------
        R0, R1 : ndarrays
            Residual matrices.
        regime_bounds : list
            Regime boundary indices.
        """
        T, N = R0.shape
        r = self.rank
        n_regimes = len(regime_bounds) - 1
        
        # Build regime-specific R1 matrices
        # R1^(j)_t = R1_t * 1{t̂_j < t ≤ t̂_{j+1}}
        R1_regime_list = []
        for j in range(n_regimes):
            start, end = regime_bounds[j], regime_bounds[j + 1]
            R1_j = np.zeros_like(R1)
            R1_j[start:end, :] = R1[start:end, :]
            R1_regime_list.append(R1_j)
        
        # Stack R1 matrices: [R1^(0), ..., R1^(m)]
        R1_stacked = np.hstack(R1_regime_list)  # Shape: (T, N * n_regimes)
        
        # Compute covariance matrices
        # S00 = T^{-1} Σ R0_t R0_t'
        S00 = R0.T @ R0 / T
        
        # S^(j)_{01} = T^{-1} Σ_{t̂_j}^{t̂_{j+1}} R0_t R1^(j)'_t
        # S^(j)_{10} = (S^(j)_{01})'
        # S^(j)_{11} = T^{-1} Σ_{t̂_j}^{t̂_{j+1}} R1^(j)_t R1^(j)'_t
        S01_list = []
        S10_list = []
        S11_list = []
        
        for j in range(n_regimes):
            start, end = regime_bounds[j], regime_bounds[j + 1]
            R0_j = R0[start:end, :]
            R1_j = R1[start:end, :]
            
            S01_j = R0_j.T @ R1_j / T
            S10_j = R1_j.T @ R0_j / T
            S11_j = R1_j.T @ R1_j / T
            
            S01_list.append(S01_j)
            S10_list.append(S10_j)
            S11_list.append(S11_j)
        
        # OLS estimation: R0_t = Π_stacked R1_stacked_t + e_t
        # To get residual covariance Σ_e
        Pi_stacked, _, _, _ = lstsq(R1_stacked, R0, rcond=None)
        residuals = R0 - R1_stacked @ Pi_stacked
        Sigma_e = residuals.T @ residuals / T
        self.Sigma_e_ = Sigma_e
        
        # Compute matrix for eigenvalue decomposition
        # Equation (14): Σ_e^{-1/2} [Σ S^(j)_{01} (S^(j)_{11})^{-1} S^(j)_{10}] Σ_e^{-1/2}'
        try:
            Sigma_e_inv_sqrt = fractional_matrix_power(Sigma_e, -0.5)
        except:
            Sigma_e_inv_sqrt = pinv(sqrtm(Sigma_e))
        
        M = np.zeros((N, N))
        for j in range(n_regimes):
            try:
                S11_j_inv = inv(S11_list[j])
            except:
                S11_j_inv = pinv(S11_list[j])
            M += S01_list[j] @ S11_j_inv @ S10_list[j]
        
        M_transformed = Sigma_e_inv_sqrt @ M @ Sigma_e_inv_sqrt.T
        
        # Eigenvalue decomposition
        eigenvalues, eigenvectors = eigh(M_transformed)
        idx = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[idx].real
        eigenvectors = eigenvectors[:, idx].real
        
        self.eigenvalues_ = eigenvalues
        
        # Extract r largest eigenvectors
        V = eigenvectors[:, :r]
        
        # Compute α (constant across regimes)
        # Equation (15): α̂ = Σ_e^{1/2} V̂
        try:
            Sigma_e_sqrt = sqrtm(Sigma_e)
        except:
            Sigma_e_sqrt = fractional_matrix_power(Sigma_e, 0.5)
        
        alpha = Sigma_e_sqrt @ V
        self.alpha_ = alpha  # Single matrix for Case 1
        
        # Compute regime-specific β
        # Equation (15): β̂'_j = α̂' Σ_e^{-1} S^(j)_{01} (S^(j)_{11})^{-1}
        try:
            Sigma_e_inv = inv(Sigma_e)
        except:
            Sigma_e_inv = pinv(Sigma_e)
        
        beta_list = []
        for j in range(n_regimes):
            try:
                S11_j_inv = inv(S11_list[j])
            except:
                S11_j_inv = pinv(S11_list[j])
            
            beta_j_T = alpha.T @ Sigma_e_inv @ S01_list[j] @ S11_j_inv
            beta_j = beta_j_T.T
            beta_list.append(beta_j)
        
        self.beta_ = beta_list
        
        # Store covariance matrices for inference
        self.covariance_matrices_ = {
            "S00": S00,
            "S01": S01_list,
            "S10": S10_list,
            "S11": S11_list,
            "Sigma_e": Sigma_e
        }
    
    def _fit_case2(
        self,
        R0: np.ndarray,
        R1: np.ndarray,
        regime_bounds: List[int]
    ) -> None:
        """
        Fit Case 2: Regime-specific α and β.
        
        Following Equations (16)-(18) in the paper.
        
        Parameters
        ----------
        R0, R1 : ndarrays
            Residual matrices.
        regime_bounds : list
            Regime boundary indices.
        """
        T, N = R0.shape
        r = self.rank
        n_regimes = len(regime_bounds) - 1
        
        alpha_list = []
        beta_list = []
        S00_list = []
        S01_list = []
        S10_list = []
        S11_list = []
        eigenvalues_list = []
        
        for j in range(n_regimes):
            start, end = regime_bounds[j], regime_bounds[j + 1]
            
            if end - start < r + 1:
                warnings.warn(f"Regime {j} has too few observations for rank {r}")
                # Use pooled estimate as fallback
                alpha_list.append(np.zeros((N, r)))
                beta_list.append(np.zeros((N, r)))
                continue
            
            R0_j = R0[start:end, :]
            R1_j = R1[start:end, :]
            T_j = end - start
            
            # Compute regime-specific covariance matrices
            S00_j = R0_j.T @ R0_j / T_j
            S01_j = R0_j.T @ R1_j / T_j
            S10_j = R1_j.T @ R0_j / T_j
            S11_j = R1_j.T @ R1_j / T_j
            
            S00_list.append(S00_j)
            S01_list.append(S01_j)
            S10_list.append(S10_j)
            S11_list.append(S11_j)
            
            # Eigenvalue problem for this regime
            # Equation (17): (S^(j)_{00})^{-1/2} S^(j)_{01} (S^(j)_{11})^{-1} S^(j)_{10} (S^(j)_{00})^{-1/2}
            try:
                S00_j_inv_sqrt = fractional_matrix_power(S00_j, -0.5)
                S11_j_inv = inv(S11_j)
            except:
                S00_j_inv_sqrt = pinv(sqrtm(S00_j))
                S11_j_inv = pinv(S11_j)
            
            M_j = S00_j_inv_sqrt @ S01_j @ S11_j_inv @ S10_j @ S00_j_inv_sqrt
            
            eigenvalues_j, eigenvectors_j = eigh(M_j)
            idx = np.argsort(eigenvalues_j)[::-1]
            eigenvalues_j = eigenvalues_j[idx].real
            eigenvectors_j = eigenvectors_j[:, idx].real
            
            eigenvalues_list.append(eigenvalues_j)
            
            # Extract r largest eigenvectors
            V_j = eigenvectors_j[:, :r]
            
            # Compute α_j and β_j
            # Equation (18): α̂_j = (S^(j)_{00})^{1/2} V̂_j
            #                β̂'_j = α̂'_j (S^(j)_{00})^{-1} S^(j)_{01} (S^(j)_{11})^{-1}
            try:
                S00_j_sqrt = sqrtm(S00_j)
                S00_j_inv = inv(S00_j)
            except:
                S00_j_sqrt = fractional_matrix_power(S00_j, 0.5)
                S00_j_inv = pinv(S00_j)
            
            alpha_j = S00_j_sqrt @ V_j
            beta_j_T = alpha_j.T @ S00_j_inv @ S01_j @ S11_j_inv
            beta_j = beta_j_T.T
            
            alpha_list.append(alpha_j)
            beta_list.append(beta_j)
        
        self.alpha_ = alpha_list
        self.beta_ = beta_list
        self.eigenvalues_ = eigenvalues_list
        
        # Store covariance matrices
        self.covariance_matrices_ = {
            "S00": S00_list,
            "S01": S01_list,
            "S10": S10_list,
            "S11": S11_list
        }
    
    def _apply_normalization(self) -> None:
        """
        Apply normalization to estimated cointegrating vectors.
        
        Uses triangular normalization by default:
            β_c = [I_r, b_1']'
        
        This ensures c'β_c = I_r for interpretable coefficients.
        """
        if self.normalization != "triangular":
            return
        
        N = self.beta_[0].shape[0]
        r = self.rank
        
        if r > N:
            warnings.warn("Cannot apply triangular normalization: rank > N")
            return
        
        # Normalization matrix c: c' = [I_r, 0]
        c = np.zeros((N, r))
        c[:r, :r] = np.eye(r)
        
        # Normalize each β
        for j in range(len(self.beta_)):
            beta_j = self.beta_[j]
            
            # β_c = β(c'β)^{-1}
            c_prime_beta = c.T @ beta_j
            try:
                c_prime_beta_inv = inv(c_prime_beta)
                self.beta_[j] = beta_j @ c_prime_beta_inv
                
                # Adjust α accordingly: α_c = αβ'c
                if self.case == 1:
                    # α is not regime-specific in Case 1
                    pass  # Handle after loop
                else:
                    self.alpha_[j] = self.alpha_[j] @ beta_j.T @ c
            except:
                warnings.warn(f"Singular matrix in normalization for regime {j}")
        
        # Handle α normalization for Case 1
        if self.case == 1:
            # Compute average normalization across regimes
            # This is a simplification - proper handling would use pooled estimate
            pass
    
    def _compute_residuals(
        self,
        R0: np.ndarray,
        R1: np.ndarray,
        regime_bounds: List[int]
    ) -> None:
        """
        Compute estimation residuals.
        
        Parameters
        ----------
        R0, R1 : ndarrays
            Residual matrices.
        regime_bounds : list
            Regime boundary indices.
        """
        T, N = R0.shape
        n_regimes = len(regime_bounds) - 1
        
        residuals = np.zeros_like(R0)
        
        for j in range(n_regimes):
            start, end = regime_bounds[j], regime_bounds[j + 1]
            
            if self.case == 1:
                alpha = self.alpha_
            else:
                alpha = self.alpha_[j]
            
            beta = self.beta_[j]
            
            # Fitted values: α β' R1_t
            Pi_j = alpha @ beta.T
            fitted = R1[start:end, :] @ Pi_j.T
            residuals[start:end, :] = R0[start:end, :] - fitted
        
        self.residuals_ = residuals
    
    def get_Pi_matrices(self) -> List[np.ndarray]:
        """
        Get the Π = αβ' matrices for each regime.
        
        Returns
        -------
        Pi_list : list of ndarrays
            Π matrices for each regime.
        """
        Pi_list = []
        
        for j in range(len(self.beta_)):
            if self.case == 1:
                alpha = self.alpha_
            else:
                alpha = self.alpha_[j]
            
            beta = self.beta_[j]
            Pi_j = alpha @ beta.T
            Pi_list.append(Pi_j)
        
        return Pi_list
    
    def summary(self) -> str:
        """
        Generate summary of estimation results.
        
        Returns
        -------
        summary : str
            Formatted summary string.
        """
        lines = []
        lines.append("=" * 60)
        lines.append("Principal Component Estimation Results")
        lines.append("=" * 60)
        lines.append(f"Case: {self.case}")
        lines.append(f"Cointegration rank: {self.rank}")
        lines.append(f"Number of regimes: {len(self.beta_)}")
        lines.append("")
        
        for j, beta_j in enumerate(self.beta_):
            lines.append(f"--- Regime {j + 1} ---")
            
            if self.case == 1:
                lines.append("α (constant across regimes):")
                lines.append(str(self.alpha_))
            else:
                lines.append(f"α_{j + 1}:")
                lines.append(str(self.alpha_[j]))
            
            lines.append(f"β_{j + 1}:")
            lines.append(str(beta_j))
            
            # Print eigenvalues if available
            if self.eigenvalues_ is not None:
                if self.case == 2 and isinstance(self.eigenvalues_, list):
                    lines.append(f"Eigenvalues: {self.eigenvalues_[j][:self.rank]}")
                elif j == 0:
                    lines.append(f"Eigenvalues: {self.eigenvalues_[:self.rank]}")
            
            lines.append("")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)


class MaximumLikelihoodEstimator:
    """
    Maximum Likelihood Estimator for VECM with structural breaks.
    
    This provides an alternative to PCE using Johansen's MLE approach.
    
    Parameters
    ----------
    rank : int, default=1
        Cointegration rank.
    deterministic : str, default='ci'
        Deterministic terms specification:
        - 'nc': No constant
        - 'ci': Constant in cointegration
        - 'co': Constant outside
        - 'li': Linear trend in cointegration
        - 'lo': Linear trend outside
    
    Attributes
    ----------
    alpha_ : list of ndarrays
        Adjustment coefficients per regime.
    beta_ : list of ndarrays
        Cointegrating vectors per regime.
    Gamma_ : list of ndarrays
        Short-run dynamics matrices.
    
    References
    ----------
    Johansen, S. (1991). Estimation and Hypothesis Testing of Cointegration 
        Vectors in Gaussian Vector Autoregressive Models. Econometrica.
    """
    
    def __init__(
        self,
        rank: int = 1,
        deterministic: str = "ci"
    ):
        self.rank = rank
        self.deterministic = deterministic
        
        self.alpha_ = None
        self.beta_ = None
        self.Gamma_ = None
        self.log_likelihood_ = None
    
    def fit(
        self,
        Y: np.ndarray,
        breaks: List[int],
        k_ar: int = 1
    ) -> "MaximumLikelihoodEstimator":
        """
        Fit VECM using maximum likelihood.
        
        Parameters
        ----------
        Y : ndarray of shape (T, N)
            Endogenous variables in levels.
        breaks : list of int
            Break locations.
        k_ar : int, default=1
            AR lag order (K in the paper).
        
        Returns
        -------
        self : MaximumLikelihoodEstimator
            Fitted estimator.
        """
        try:
            from statsmodels.tsa.vector_ar.vecm import VECM
        except ImportError:
            raise ImportError("statsmodels required for MLE estimation")
        
        T, N = Y.shape
        r = self.rank
        
        # Define regimes
        if len(breaks) == 0:
            regime_bounds = [(0, T)]
        else:
            all_points = [0] + sorted(breaks) + [T]
            regime_bounds = [(all_points[i], all_points[i + 1]) 
                           for i in range(len(all_points) - 1)]
        
        self.alpha_ = []
        self.beta_ = []
        self.Gamma_ = []
        self.log_likelihood_ = 0
        
        for start, end in regime_bounds:
            if end - start < k_ar + r + 10:
                warnings.warn(f"Regime [{start}, {end}) has too few observations")
                self.alpha_.append(np.zeros((N, r)))
                self.beta_.append(np.zeros((N, r)))
                self.Gamma_.append([])
                continue
            
            Y_regime = Y[start:end, :]
            
            # Fit VECM using statsmodels
            model = VECM(
                Y_regime,
                k_ar_diff=k_ar - 1,
                coint_rank=r,
                deterministic=self.deterministic
            )
            result = model.fit()
            
            self.alpha_.append(result.alpha)
            self.beta_.append(result.beta)
            
            # Get short-run dynamics
            if hasattr(result, 'gamma'):
                self.Gamma_.append(result.gamma)
            else:
                self.Gamma_.append([])
            
            # Accumulate log-likelihood
            if hasattr(result, 'llf'):
                self.log_likelihood_ += result.llf
        
        return self
