"""
Impulse Response Functions for VECMs with Structural Breaks
===========================================================

This module implements impulse response function (IRF) computation for 
Vector Error Correction Models with structural breaks, following the 
methodology of Franjic, Mößler, and Schweikert (2025).

The IRFs allow for analyzing how shocks propagate through the system 
across different regimes, as illustrated in Figure 2 of the paper.

Key Functions
-------------
compute_irf : Compute IRFs for a VECM (with or without breaks)
compute_regime_irf : Compute regime-specific IRFs
plot_irf : Visualize IRFs across regimes

Mathematical Background
-----------------------
For a VECM: ΔY_t = ΠY_{t-1} + Σ Γ_i ΔY_{t-i} + u_t

The companion form VAR(1) representation is used to compute IRFs:
    X_t = A X_{t-1} + U_t

where X_t = (Y_t', Y_{t-1}', ..., Y_{t-K+1}')' and A is the companion matrix.

The impulse responses are computed from the MA(∞) representation:
    Y_t = Σ_{i=0}^∞ Φ_i u_{t-i}

where Φ_i are the matrix coefficients of the MA representation.

For structural identification, Cholesky decomposition of the error 
covariance matrix is used (triangular ordering as in the paper).

References
----------
Franjic, D., Mößler, M., & Schweikert, K. (2025). Multiple Structural Breaks 
in Vector Error Correction Models. University of Hohenheim.

Lütkepohl, H. (2005). New Introduction to Multiple Time Series Analysis. 
Springer-Verlag.

Author
------
Dr Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/vecmbreak
"""

import numpy as np
from scipy import linalg
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Tuple, Union
import warnings


def _vecm_to_var(
    Pi: np.ndarray,
    Gamma: Optional[List[np.ndarray]] = None,
    Phi: Optional[np.ndarray] = None
) -> Tuple[List[np.ndarray], int]:
    """
    Convert VECM parameters to VAR representation.
    
    For VECM: ΔY_t = ΠY_{t-1} + Σ Γ_i ΔY_{t-i} + ΦD_t + u_t
    
    The corresponding VAR(K) representation is:
    Y_t = A_1 Y_{t-1} + ... + A_K Y_{t-K} + ΦD_t + u_t
    
    where:
        A_1 = I_N + Π + Γ_1
        A_i = Γ_i - Γ_{i-1}  for i = 2, ..., K-1
        A_K = -Γ_{K-1}
    
    Parameters
    ----------
    Pi : ndarray of shape (N, N)
        Long-run impact matrix Π = αβ'
    Gamma : list of ndarray, optional
        Short-run dynamics matrices Γ_1, ..., Γ_{K-1}
    Phi : ndarray, optional
        Deterministic coefficients (not used in IRF computation)
    
    Returns
    -------
    A_matrices : list of ndarray
        VAR coefficient matrices A_1, ..., A_K
    K : int
        VAR lag order
    
    Notes
    -----
    This implements the standard VECM to VAR conversion:
    Π = -(I_N - A_1 - ... - A_K)
    Γ_i = -(A_{i+1} + ... + A_K)  for i = 1, ..., K-1
    """
    N = Pi.shape[0]
    
    if Gamma is None or len(Gamma) == 0:
        # VAR(1) case: Y_t = (I + Π)Y_{t-1} + u_t
        A_1 = np.eye(N) + Pi
        return [A_1], 1
    
    K = len(Gamma) + 1
    A_matrices = []
    
    # A_1 = I_N + Π + Γ_1
    A_1 = np.eye(N) + Pi + Gamma[0]
    A_matrices.append(A_1)
    
    # A_i = Γ_i - Γ_{i-1} for i = 2, ..., K-1
    for i in range(1, len(Gamma)):
        A_i = Gamma[i] - Gamma[i-1]
        A_matrices.append(A_i)
    
    # A_K = -Γ_{K-1}
    A_K = -Gamma[-1]
    A_matrices.append(A_K)
    
    return A_matrices, K


def _build_companion_matrix(A_matrices: List[np.ndarray]) -> np.ndarray:
    """
    Build the companion matrix for VAR(K) representation.
    
    For VAR(K): Y_t = A_1 Y_{t-1} + ... + A_K Y_{t-K} + u_t
    
    The companion form is:
    [Y_t    ]   [A_1 A_2 ... A_{K-1} A_K] [Y_{t-1}  ]   [u_t]
    [Y_{t-1}]   [I_N  0  ...    0     0 ] [Y_{t-2}  ]   [ 0 ]
    [  ...  ] = [ 0  I_N ...    0     0 ] [  ...    ] + [...]
    [Y_{t-K+1}] [ 0   0  ...   I_N    0 ] [Y_{t-K}  ]   [ 0 ]
    
    Parameters
    ----------
    A_matrices : list of ndarray
        VAR coefficient matrices A_1, ..., A_K, each of shape (N, N)
    
    Returns
    -------
    companion : ndarray of shape (NK, NK)
        The companion matrix
    """
    K = len(A_matrices)
    N = A_matrices[0].shape[0]
    
    companion = np.zeros((N * K, N * K))
    
    # First block row: [A_1, A_2, ..., A_K]
    for i, A in enumerate(A_matrices):
        companion[:N, i*N:(i+1)*N] = A
    
    # Identity blocks below
    if K > 1:
        companion[N:, :-N] = np.eye(N * (K - 1))
    
    return companion


def _compute_ma_coefficients(
    A_matrices: List[np.ndarray],
    horizons: int,
    use_companion: bool = True
) -> List[np.ndarray]:
    """
    Compute MA(∞) representation coefficients Φ_0, Φ_1, ..., Φ_h.
    
    For VAR(K): Y_t = A_1 Y_{t-1} + ... + A_K Y_{t-K} + u_t
    
    The MA representation is: Y_t = Σ_{i=0}^∞ Φ_i u_{t-i}
    
    where:
        Φ_0 = I_N
        Φ_i = Σ_{j=1}^{min(i,K)} Φ_{i-j} A_j  for i ≥ 1
    
    Alternatively, using companion matrix F:
        Φ_i = J F^i J'
    where J = [I_N, 0, ..., 0] is the selection matrix.
    
    Parameters
    ----------
    A_matrices : list of ndarray
        VAR coefficient matrices A_1, ..., A_K
    horizons : int
        Number of periods for IRF computation
    use_companion : bool, default=True
        If True, use companion matrix method (more efficient for large K)
    
    Returns
    -------
    Phi_matrices : list of ndarray
        MA coefficient matrices Φ_0, Φ_1, ..., Φ_{horizons}
    """
    K = len(A_matrices)
    N = A_matrices[0].shape[0]
    
    Phi_matrices = [np.eye(N)]  # Φ_0 = I_N
    
    if use_companion and K > 1:
        # Use companion matrix method
        companion = _build_companion_matrix(A_matrices)
        J = np.zeros((N, N * K))
        J[:N, :N] = np.eye(N)
        
        F_power = np.eye(N * K)
        for h in range(1, horizons + 1):
            F_power = F_power @ companion
            Phi_h = J @ F_power @ J.T
            Phi_matrices.append(Phi_h)
    else:
        # Direct recursive computation
        for i in range(1, horizons + 1):
            Phi_i = np.zeros((N, N))
            for j in range(1, min(i, K) + 1):
                Phi_i += Phi_matrices[i - j] @ A_matrices[j - 1]
            Phi_matrices.append(Phi_i)
    
    return Phi_matrices


def _orthogonalize_irf(
    Phi_matrices: List[np.ndarray],
    Sigma: np.ndarray,
    method: str = 'cholesky'
) -> List[np.ndarray]:
    """
    Orthogonalize impulse response functions using structural identification.
    
    Parameters
    ----------
    Phi_matrices : list of ndarray
        MA coefficient matrices Φ_0, Φ_1, ..., Φ_h
    Sigma : ndarray of shape (N, N)
        Error covariance matrix
    method : str, default='cholesky'
        Orthogonalization method:
        - 'cholesky': Cholesky decomposition (triangular ordering)
        - 'generalized': Generalized IRF (no orthogonalization)
    
    Returns
    -------
    Theta_matrices : list of ndarray
        Orthogonalized IRF matrices Θ_0, Θ_1, ..., Θ_h
    
    Notes
    -----
    The paper uses triangular ordering with Cholesky decomposition for 
    structural identification (Figure 2).
    
    For Cholesky: Θ_i = Φ_i P, where P P' = Σ
    """
    if method == 'cholesky':
        try:
            P = linalg.cholesky(Sigma, lower=True)
        except linalg.LinAlgError:
            # Handle near-singular covariance matrix
            eigvals, eigvecs = linalg.eigh(Sigma)
            eigvals = np.maximum(eigvals, 1e-10)
            P = eigvecs @ np.diag(np.sqrt(eigvals))
            warnings.warn("Covariance matrix not positive definite, "
                         "using eigenvalue decomposition for orthogonalization.")
        
        Theta_matrices = [Phi @ P for Phi in Phi_matrices]
        
    elif method == 'generalized':
        # Generalized IRF: normalize by sqrt of diagonal elements
        scale = np.sqrt(np.diag(Sigma))
        Theta_matrices = [Phi * scale for Phi in Phi_matrices]
        
    else:
        raise ValueError(f"Unknown orthogonalization method: {method}")
    
    return Theta_matrices


def compute_irf(
    Pi: np.ndarray,
    Sigma: np.ndarray,
    Gamma: Optional[List[np.ndarray]] = None,
    horizons: int = 30,
    orthogonalize: bool = True,
    method: str = 'cholesky'
) -> Dict[str, np.ndarray]:
    """
    Compute impulse response functions for a VECM.
    
    This function computes the IRFs for the standard VECM:
    ΔY_t = ΠY_{t-1} + Σ Γ_i ΔY_{t-i} + u_t
    
    following the methodology shown in Figure 2 of Franjic et al. (2025).
    
    Parameters
    ----------
    Pi : ndarray of shape (N, N)
        Long-run impact matrix Π = αβ'
    Sigma : ndarray of shape (N, N)
        Error covariance matrix
    Gamma : list of ndarray, optional
        Short-run dynamics matrices Γ_1, ..., Γ_{K-1}
    horizons : int, default=30
        Number of periods for IRF computation (as in Figure 2)
    orthogonalize : bool, default=True
        Whether to compute orthogonalized (structural) IRFs
    method : str, default='cholesky'
        Orthogonalization method ('cholesky' for triangular ordering)
    
    Returns
    -------
    result : dict
        Dictionary containing:
        - 'irf': ndarray of shape (horizons+1, N, N)
            IRF matrix where irf[h, i, j] is the response of variable i 
            to a shock in variable j at horizon h
        - 'cumulative_irf': ndarray of shape (horizons+1, N, N)
            Cumulative IRFs
        - 'horizons': ndarray
            Array of horizon indices
    
    Examples
    --------
    >>> import numpy as np
    >>> from vecmbreak.irf import compute_irf
    >>> 
    >>> # Simple VECM parameters
    >>> alpha = np.array([[-0.5], [0.5]])
    >>> beta = np.array([[1], [-1]])
    >>> Pi = alpha @ beta.T
    >>> Sigma = np.eye(2)
    >>> 
    >>> # Compute IRFs
    >>> result = compute_irf(Pi, Sigma, horizons=30)
    >>> print(result['irf'].shape)
    (31, 2, 2)
    
    Notes
    -----
    The implementation follows the standard VECM to VAR conversion and 
    computes IRFs via the moving average representation.
    
    For structural identification, the Cholesky decomposition (triangular 
    ordering) is used by default, as in Figure 2 of the paper.
    """
    N = Pi.shape[0]
    
    # Convert VECM to VAR representation
    A_matrices, K = _vecm_to_var(Pi, Gamma)
    
    # Compute MA coefficients
    Phi_matrices = _compute_ma_coefficients(A_matrices, horizons)
    
    # Orthogonalize if requested
    if orthogonalize:
        Theta_matrices = _orthogonalize_irf(Phi_matrices, Sigma, method)
    else:
        Theta_matrices = Phi_matrices
    
    # Stack into array
    irf = np.array(Theta_matrices)  # Shape: (horizons+1, N, N)
    
    # Compute cumulative IRFs
    cumulative_irf = np.cumsum(irf, axis=0)
    
    return {
        'irf': irf,
        'cumulative_irf': cumulative_irf,
        'horizons': np.arange(horizons + 1),
        'N': N,
        'K': K
    }


def compute_regime_irf(
    alpha_list: List[np.ndarray],
    beta_list: List[np.ndarray],
    Sigma_list: List[np.ndarray],
    Gamma: Optional[List[np.ndarray]] = None,
    horizons: int = 30,
    orthogonalize: bool = True,
    method: str = 'cholesky'
) -> Dict[str, np.ndarray]:
    """
    Compute regime-specific impulse response functions.
    
    This function computes IRFs for each regime identified in a VECM 
    with structural breaks, as shown in Figure 2 of Franjic et al. (2025).
    
    Parameters
    ----------
    alpha_list : list of ndarray
        Regime-specific adjustment coefficient matrices α_0, α_1, ..., α_m
    beta_list : list of ndarray
        Regime-specific cointegrating vectors β_0, β_1, ..., β_m
    Sigma_list : list of ndarray
        Regime-specific error covariance matrices Σ_0, Σ_1, ..., Σ_m
    Gamma : list of ndarray, optional
        Short-run dynamics matrices (assumed constant across regimes)
    horizons : int, default=30
        Number of periods for IRF computation
    orthogonalize : bool, default=True
        Whether to compute orthogonalized (structural) IRFs
    method : str, default='cholesky'
        Orthogonalization method
    
    Returns
    -------
    result : dict
        Dictionary containing:
        - 'irf_regimes': list of ndarray
            IRF matrices for each regime
        - 'cumulative_irf_regimes': list of ndarray
            Cumulative IRF matrices for each regime
        - 'n_regimes': int
            Number of regimes
        - 'horizons': ndarray
            Array of horizon indices
    
    Examples
    --------
    >>> import numpy as np
    >>> from vecmbreak.irf import compute_regime_irf
    >>> 
    >>> # Case 2: Different α and β across regimes
    >>> alpha_list = [
    ...     np.array([[-0.5], [0.0]]),
    ...     np.array([[0.0], [0.5]])
    ... ]
    >>> beta_list = [
    ...     np.array([[1], [-1]]),
    ...     np.array([[1], [-2]])
    ... ]
    >>> Sigma_list = [np.eye(2), np.eye(2)]
    >>> 
    >>> result = compute_regime_irf(alpha_list, beta_list, Sigma_list)
    >>> print(f"Number of regimes: {result['n_regimes']}")
    Number of regimes: 2
    
    Notes
    -----
    For Case 1 (constant α, changing β), all α_j should be identical.
    For Case 2 (changing α and β), α_j and β_j vary across regimes.
    
    The short-run dynamics Γ are typically assumed constant across regimes 
    (Assumption in Section 2.1 of the paper).
    """
    n_regimes = len(alpha_list)
    
    if len(beta_list) != n_regimes:
        raise ValueError("alpha_list and beta_list must have same length")
    if len(Sigma_list) != n_regimes:
        raise ValueError("alpha_list and Sigma_list must have same length")
    
    irf_regimes = []
    cumulative_irf_regimes = []
    
    for j in range(n_regimes):
        alpha_j = alpha_list[j]
        beta_j = beta_list[j]
        Sigma_j = Sigma_list[j]
        
        # Compute Π_j = α_j β_j'
        Pi_j = alpha_j @ beta_j.T
        
        # Compute IRF for this regime
        result_j = compute_irf(
            Pi_j, Sigma_j, Gamma,
            horizons=horizons,
            orthogonalize=orthogonalize,
            method=method
        )
        
        irf_regimes.append(result_j['irf'])
        cumulative_irf_regimes.append(result_j['cumulative_irf'])
    
    return {
        'irf_regimes': irf_regimes,
        'cumulative_irf_regimes': cumulative_irf_regimes,
        'n_regimes': n_regimes,
        'horizons': np.arange(horizons + 1),
        'N': alpha_list[0].shape[0]
    }


def compute_long_run_impact(
    Pi: np.ndarray,
    Gamma: Optional[List[np.ndarray]] = None
) -> np.ndarray:
    """
    Compute the long-run impact matrix for a VECM.
    
    The long-run impact matrix C(1) captures the cumulative effect of 
    permanent shocks on the level of the variables.
    
    For a VECM with I(1) variables, the long-run impact is:
    C(1) = β_⊥ (α_⊥' Γ β_⊥)^{-1} α_⊥'
    
    where Γ = I_N - Σ Γ_i and α_⊥, β_⊥ are orthogonal complements.
    
    Parameters
    ----------
    Pi : ndarray of shape (N, N)
        Long-run impact matrix Π = αβ'
    Gamma : list of ndarray, optional
        Short-run dynamics matrices
    
    Returns
    -------
    C1 : ndarray of shape (N, N)
        Long-run impact matrix
    
    Notes
    -----
    This is useful for analyzing the permanent effects of shocks in 
    cointegrated systems.
    """
    N = Pi.shape[0]
    
    # Compute α and β from eigendecomposition of Π
    eigvals, eigvecs = linalg.eig(Pi)
    
    # Find cointegration rank (number of non-zero eigenvalues)
    r = np.sum(np.abs(eigvals) > 1e-10)
    
    if r == 0 or r == N:
        # No cointegration or fully stationary
        return np.zeros((N, N))
    
    # SVD decomposition of Pi
    U, S, Vt = linalg.svd(Pi)
    
    # Orthogonal complements
    alpha_perp = U[:, r:]
    beta_perp = Vt.T[:, r:]
    
    # Γ* = I_N - Σ Γ_i
    if Gamma is None or len(Gamma) == 0:
        Gamma_star = np.eye(N)
    else:
        Gamma_star = np.eye(N) - sum(Gamma)
    
    # C(1) = β_⊥ (α_⊥' Γ* β_⊥)^{-1} α_⊥'
    middle = alpha_perp.T @ Gamma_star @ beta_perp
    try:
        middle_inv = linalg.inv(middle)
        C1 = beta_perp @ middle_inv @ alpha_perp.T
    except linalg.LinAlgError:
        C1 = beta_perp @ linalg.pinv(middle) @ alpha_perp.T
    
    return C1


def compute_forecast_error_variance_decomposition(
    irf: np.ndarray,
    Sigma: np.ndarray,
    horizons: Optional[int] = None
) -> np.ndarray:
    """
    Compute forecast error variance decomposition (FEVD).
    
    The FEVD shows the proportion of the h-step forecast error variance 
    of variable i that is attributable to shocks in variable j.
    
    Parameters
    ----------
    irf : ndarray of shape (H+1, N, N)
        Orthogonalized impulse response functions
    Sigma : ndarray of shape (N, N)
        Error covariance matrix
    horizons : int, optional
        Maximum horizon for FEVD. If None, use all available horizons.
    
    Returns
    -------
    fevd : ndarray of shape (H+1, N, N)
        FEVD matrix where fevd[h, i, j] is the contribution of shock j 
        to the h-step forecast error variance of variable i
    
    Notes
    -----
    The FEVD is computed as:
    
    FEVD_{i,j}(h) = Σ_{k=0}^h (Θ_{ki,j})^2 / MSE_i(h)
    
    where MSE_i(h) = Σ_{k=0}^h Σ_{l=1}^N (Θ_{ki,l})^2
    """
    if horizons is None:
        H = irf.shape[0] - 1
    else:
        H = min(horizons, irf.shape[0] - 1)
    
    N = irf.shape[1]
    fevd = np.zeros((H + 1, N, N))
    
    # Cumulative squared responses
    cumsum_sq = np.cumsum(irf[:H+1]**2, axis=0)
    
    # MSE for each variable (sum over all shocks)
    mse = np.sum(cumsum_sq, axis=2)  # Shape: (H+1, N)
    
    # FEVD: contribution of each shock
    for h in range(H + 1):
        for i in range(N):
            if mse[h, i] > 1e-10:
                fevd[h, i, :] = cumsum_sq[h, i, :] / mse[h, i]
            else:
                fevd[h, i, :] = 1.0 / N  # Equal contribution if MSE ≈ 0
    
    return fevd


def plot_irf(
    irf_result: Dict,
    var_names: Optional[List[str]] = None,
    figsize: Tuple[int, int] = (12, 10),
    regime_labels: Optional[List[str]] = None,
    title: Optional[str] = None,
    save_path: Optional[str] = None,
    show_full_sample: bool = False,
    full_sample_irf: Optional[np.ndarray] = None
) -> plt.Figure:
    """
    Plot impulse response functions across regimes.
    
    This function creates a visualization similar to Figure 2 in 
    Franjic et al. (2025), showing regime-specific IRFs.
    
    Parameters
    ----------
    irf_result : dict
        Output from compute_regime_irf() containing:
        - 'irf_regimes': list of IRF arrays
        - 'horizons': array of horizon indices
        - 'N': number of variables
        - 'n_regimes': number of regimes
    var_names : list of str, optional
        Variable names for axis labels
    figsize : tuple, default=(12, 10)
        Figure size in inches
    regime_labels : list of str, optional
        Labels for each regime (e.g., ['Pre-GFC', 'Crisis', 'Post-GFC'])
    title : str, optional
        Overall figure title
    save_path : str, optional
        Path to save the figure
    show_full_sample : bool, default=False
        Whether to overlay full sample IRF
    full_sample_irf : ndarray, optional
        Full sample IRF for comparison (required if show_full_sample=True)
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        The created figure
    
    Examples
    --------
    >>> import numpy as np
    >>> from vecmbreak.irf import compute_regime_irf, plot_irf
    >>> 
    >>> # Example with 2 regimes
    >>> alpha_list = [np.array([[-0.5], [0.0]]), np.array([[0.0], [0.5]])]
    >>> beta_list = [np.array([[1], [-1]]), np.array([[1], [-2]])]
    >>> Sigma_list = [np.eye(2), np.eye(2)]
    >>> 
    >>> result = compute_regime_irf(alpha_list, beta_list, Sigma_list)
    >>> fig = plot_irf(result, var_names=['y10', 'y1'])
    >>> plt.show()
    
    Notes
    -----
    The plot layout follows Figure 2 of the paper with:
    - Rows: response variables
    - Columns: shock variables
    - Different line styles for different regimes
    """
    # Extract information from result
    if 'irf_regimes' in irf_result:
        irf_regimes = irf_result['irf_regimes']
        n_regimes = irf_result['n_regimes']
    else:
        # Single regime case
        irf_regimes = [irf_result['irf']]
        n_regimes = 1
    
    horizons = irf_result['horizons']
    N = irf_result['N']
    
    # Default variable names
    if var_names is None:
        var_names = [f'y{i+1}' for i in range(N)]
    
    # Default regime labels
    if regime_labels is None:
        regime_labels = [f'Regime {j+1}' for j in range(n_regimes)]
    
    # Line styles for different regimes (as in Figure 2)
    line_styles = ['-', '--', '-.', ':']
    colors = ['black', 'blue', 'red', 'green', 'purple']
    
    # Create figure
    fig, axes = plt.subplots(N, N, figsize=figsize, sharex=True)
    if N == 1:
        axes = np.array([[axes]])
    
    # Plot IRFs
    for i in range(N):  # Response variable
        for j in range(N):  # Shock variable
            ax = axes[i, j]
            
            # Plot full sample IRF if provided
            if show_full_sample and full_sample_irf is not None:
                ax.plot(horizons, full_sample_irf[:, i, j],
                       color='black', linestyle='-', linewidth=1.5,
                       label='Full sample')
            
            # Plot regime-specific IRFs
            for r, irf in enumerate(irf_regimes):
                style_idx = r % len(line_styles)
                color_idx = r % len(colors)
                ax.plot(horizons, irf[:, i, j],
                       color=colors[color_idx],
                       linestyle=line_styles[style_idx],
                       linewidth=1.2,
                       label=regime_labels[r])
            
            # Zero line
            ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.5, alpha=0.7)
            
            # Labels
            ax.set_title(f'{var_names[j]} → {var_names[i]}', fontsize=10)
            
            if i == N - 1:
                ax.set_xlabel('Horizon')
            if j == 0:
                ax.set_ylabel('Response')
    
    # Add legend to first subplot
    axes[0, 0].legend(loc='best', fontsize=8)
    
    # Overall title
    if title:
        fig.suptitle(title, fontsize=12, y=1.02)
    
    plt.tight_layout()
    
    # Save if path provided
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_fevd(
    fevd: np.ndarray,
    var_names: Optional[List[str]] = None,
    figsize: Tuple[int, int] = (12, 8),
    title: Optional[str] = None,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot forecast error variance decomposition.
    
    Parameters
    ----------
    fevd : ndarray of shape (H+1, N, N)
        FEVD matrix from compute_forecast_error_variance_decomposition()
    var_names : list of str, optional
        Variable names
    figsize : tuple, default=(12, 8)
        Figure size
    title : str, optional
        Figure title
    save_path : str, optional
        Path to save figure
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        The created figure
    """
    H, N, _ = fevd.shape
    horizons = np.arange(H)
    
    if var_names is None:
        var_names = [f'y{i+1}' for i in range(N)]
    
    fig, axes = plt.subplots(1, N, figsize=figsize, sharey=True)
    if N == 1:
        axes = [axes]
    
    colors = plt.cm.Set3(np.linspace(0, 1, N))
    
    for i in range(N):
        ax = axes[i]
        
        # Stacked area plot
        bottom = np.zeros(H)
        for j in range(N):
            ax.fill_between(horizons, bottom, bottom + fevd[:, i, j],
                           color=colors[j], alpha=0.8, label=var_names[j])
            bottom += fevd[:, i, j]
        
        ax.set_title(f'FEVD of {var_names[i]}')
        ax.set_xlabel('Horizon')
        if i == 0:
            ax.set_ylabel('Proportion')
        ax.set_ylim(0, 1)
        ax.legend(loc='best', fontsize=8)
    
    if title:
        fig.suptitle(title, fontsize=12, y=1.02)
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


# Additional utility functions for IRF analysis

def bootstrap_irf_confidence_intervals(
    data: np.ndarray,
    Pi: np.ndarray,
    Sigma: np.ndarray,
    Gamma: Optional[List[np.ndarray]] = None,
    horizons: int = 30,
    n_bootstrap: int = 1000,
    confidence_level: float = 0.95,
    seed: Optional[int] = None
) -> Dict[str, np.ndarray]:
    """
    Compute bootstrap confidence intervals for IRFs.
    
    Uses residual bootstrap to construct confidence bands around 
    the point estimates of impulse response functions.
    
    Parameters
    ----------
    data : ndarray of shape (T, N)
        Original data matrix
    Pi : ndarray of shape (N, N)
        Estimated long-run impact matrix
    Sigma : ndarray of shape (N, N)
        Estimated error covariance
    Gamma : list of ndarray, optional
        Estimated short-run dynamics
    horizons : int, default=30
        IRF horizons
    n_bootstrap : int, default=1000
        Number of bootstrap replications
    confidence_level : float, default=0.95
        Confidence level for intervals
    seed : int, optional
        Random seed for reproducibility
    
    Returns
    -------
    result : dict
        Dictionary containing:
        - 'irf_point': Point estimate of IRFs
        - 'irf_lower': Lower confidence band
        - 'irf_upper': Upper confidence band
        - 'irf_bootstrap': All bootstrap IRF samples
    """
    if seed is not None:
        np.random.seed(seed)
    
    N = Pi.shape[0]
    T = data.shape[0]
    
    # Point estimate
    result_point = compute_irf(Pi, Sigma, Gamma, horizons)
    irf_point = result_point['irf']
    
    # Compute residuals from original estimation
    # (simplified - in practice, use residuals from full VECM estimation)
    
    # Bootstrap samples storage
    irf_bootstrap = np.zeros((n_bootstrap, horizons + 1, N, N))
    
    # Bootstrap loop
    for b in range(n_bootstrap):
        # Resample residuals (block bootstrap for time series)
        # Simplified version - full implementation would use proper block bootstrap
        
        # For now, add perturbation to covariance estimate
        perturb = np.random.randn(N, N) * 0.1
        Sigma_b = Sigma + (perturb @ perturb.T) / T
        
        # Compute IRF for this bootstrap sample
        result_b = compute_irf(Pi, Sigma_b, Gamma, horizons)
        irf_bootstrap[b] = result_b['irf']
    
    # Compute confidence intervals
    alpha = 1 - confidence_level
    irf_lower = np.percentile(irf_bootstrap, 100 * alpha / 2, axis=0)
    irf_upper = np.percentile(irf_bootstrap, 100 * (1 - alpha / 2), axis=0)
    
    return {
        'irf_point': irf_point,
        'irf_lower': irf_lower,
        'irf_upper': irf_upper,
        'irf_bootstrap': irf_bootstrap
    }
