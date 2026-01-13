"""
Data Generation for VECMs with Structural Breaks
=================================================

This module provides functions for generating synthetic VECM data with
structural breaks for Monte Carlo simulations.

The DGPs are based on Andrade et al. (2005) and extended to multiple breaks
following the specifications in Franjic, Mößler, and Schweikert (2025).

References
----------
Andrade, P., Bruneau, C., & Gregoir, S. (2005). Testing for the cointegration 
    rank when some cointegrating directions are changing. JoE, 124, 269-310.
Franjic, D., Mößler, M., & Schweikert, K. (2025). Multiple Structural Breaks 
    in Vector Error Correction Models. University of Hohenheim.
"""

import numpy as np
from numpy.linalg import inv, eig, norm
from scipy.linalg import sqrtm
from typing import Tuple, List, Optional, Dict, Union
import warnings


def simulate_vecm_breaks(
    T: int,
    N: int,
    alpha_list: List[np.ndarray],
    beta_list: List[np.ndarray],
    breaks: Optional[List[int]] = None,
    break_points: Optional[List[int]] = None,
    r: int = 1,
    Gamma: Optional[List[np.ndarray]] = None,
    mu0: Optional[np.ndarray] = None,
    mu1: Optional[np.ndarray] = None,
    Sigma_u: Optional[np.ndarray] = None,
    burn_in: int = 100,
    seed: Optional[int] = None
) -> Tuple[np.ndarray, Dict]:
    """
    Simulate a VECM with multiple structural breaks.
    
    Generates data from the DGP:
        ΔY_t = Π(t) Y_{t-1} + Σ Γ_i ΔY_{t-i} + μ_0 + μ_1 t + u_t
    
    where Π(t) = α_j β'_j for t in regime j, and u_t ~ N(0, Σ_u).
    
    Parameters
    ----------
    T : int
        Sample size (number of observations after burn-in).
    N : int
        Number of variables.
    alpha_list : list of ndarrays
        Adjustment coefficients for each regime, shape (N, r).
    beta_list : list of ndarrays
        Cointegrating vectors for each regime, shape (N, r).
    breaks : list of int, optional
        Break locations (indices in the sample). Default is empty list (no breaks).
    break_points : list of int, optional
        Alias for breaks parameter.
    r : int, default=1
        Cointegration rank.
    Gamma : list of ndarrays, optional
        Short-run dynamics [Γ_1, ..., Γ_{K-1}]. Default is no short-run dynamics.
    mu0 : ndarray of shape (N,), optional
        Constant term. Default is zeros.
    mu1 : ndarray of shape (N,), optional
        Trend coefficient. Default is zeros.
    Sigma_u : ndarray of shape (N, N), optional
        Innovation covariance. Default is identity.
    burn_in : int, default=100
        Number of burn-in observations to discard.
    seed : int, optional
        Random seed for reproducibility.
    
    Returns
    -------
    Y : ndarray of shape (T, N)
        Simulated data in levels.
    info : dict
        Dictionary containing:
        - 'Y': Simulated data
        - 'delta_Y': First differences
        - 'breaks': True break locations
        - 'true_breaks': Alias for breaks
        - 'Pi': List of Π matrices
        - 'alpha': List of α matrices
        - 'beta': List of β matrices
    
    Examples
    --------
    >>> # Two-variable system with one break
    >>> alpha = [np.array([[-0.5], [0.5]]), np.array([[-0.5], [0.5]])]
    >>> beta = [np.array([[1], [-1]]), np.array([[1], [-2]])]
    >>> Y, info = simulate_vecm_breaks(T=200, N=2, r=1, breaks=[100],
    ...                                alpha_list=alpha, beta_list=beta)
    >>> # Or using break_points alias
    >>> Y, info = simulate_vecm_breaks(T=200, N=2, alpha_list=alpha, 
    ...                                beta_list=beta, break_points=[100])
    """
    # Handle break_points alias
    if break_points is not None and breaks is None:
        breaks = break_points
    elif breaks is None:
        breaks = []
    
    if seed is not None:
        np.random.seed(seed)
    
    # Validate inputs
    n_regimes = len(breaks) + 1
    if len(alpha_list) != n_regimes:
        raise ValueError(f"Expected {n_regimes} alpha matrices, got {len(alpha_list)}")
    if len(beta_list) != n_regimes:
        raise ValueError(f"Expected {n_regimes} beta matrices, got {len(beta_list)}")
    
    # Set defaults
    K = 1 if Gamma is None else len(Gamma) + 1
    if Gamma is None:
        Gamma = []
    
    if mu0 is None:
        mu0 = np.zeros(N)
    if mu1 is None:
        mu1 = np.zeros(N)
    if Sigma_u is None:
        Sigma_u = np.eye(N)
    
    # Total length including burn-in
    T_total = T + burn_in
    
    # Initialize Y
    Y = np.zeros((T_total + K, N))
    
    # Compute Π matrices for each regime
    Pi_list = []
    for j in range(n_regimes):
        Pi_j = alpha_list[j] @ beta_list[j].T
        Pi_list.append(Pi_j)
    
    # Define regime boundaries with burn-in offset
    regime_bounds = [0] + [b + burn_in for b in breaks] + [T_total]
    
    # Generate innovations
    # For correlated errors, use Cholesky decomposition
    L = np.linalg.cholesky(Sigma_u)
    u = np.random.randn(T_total, N) @ L.T
    
    # Simulate VECM
    for t in range(K, T_total):
        # Determine current regime
        regime_idx = 0
        for j, bound in enumerate(regime_bounds[1:], 1):
            if t < bound:
                regime_idx = j - 1
                break
        
        Pi_t = Pi_list[regime_idx]
        
        # Error correction term: Π Y_{t-1}
        ec_term = Pi_t @ Y[t - 1, :]
        
        # Short-run dynamics: Σ Γ_i ΔY_{t-i}
        sr_term = np.zeros(N)
        for i, Gamma_i in enumerate(Gamma):
            if t - i - 2 >= 0:
                delta_Y_lag = Y[t - i - 1, :] - Y[t - i - 2, :]
                sr_term += Gamma_i @ delta_Y_lag
        
        # Deterministic terms
        det_term = mu0 + mu1 * t
        
        # Update: ΔY_t = Π Y_{t-1} + short-run + deterministic + innovation
        delta_Y_t = ec_term + sr_term + det_term + u[t - K, :]
        
        # Y_t = Y_{t-1} + ΔY_t
        Y[t, :] = Y[t - 1, :] + delta_Y_t
    
    # Remove burn-in: keep T+1 observations for Y (so delta_Y has T observations)
    # Y_0, Y_1, ..., Y_T gives T+1 levels and T differences
    Y = Y[burn_in + K - 1:, :]  # Start one earlier to get T+1 observations
    
    # Compute first differences (T observations)
    delta_Y = np.diff(Y, axis=0)
    
    # Adjust break locations for output (remove burn-in offset)
    adjusted_breaks = breaks.copy()
    
    info = {
        'Y': Y,  # Include Y in info for convenience (T+1, N)
        'delta_Y': delta_Y,  # First differences (T, N)
        'breaks': adjusted_breaks,
        'true_breaks': adjusted_breaks,  # Alias for compatibility
        'Pi': Pi_list,
        'alpha': alpha_list,
        'beta': beta_list,
        'Gamma': Gamma,
        'mu0': mu0,
        'mu1': mu1,
        'Sigma_u': Sigma_u
    }
    
    return Y, info


def generate_dgp_case1(
    T: int,
    n_breaks: int = 1,
    break_fractions: Optional[List[float]] = None,
    sigma_u: float = 1.0,
    seed: Optional[int] = None
) -> Dict:
    """
    Generate data from Case 1 DGP: constant α, changing β.
    
    Following the simulation setup in Table 1 of the paper:
        α = [-0.5, 0.5]'
        β_0 = [1, -1]'
        β_j = β_{j-1} + (-1)^j [0, 1]' (alternating between [1,-1] and [1,-2])
    
    Parameters
    ----------
    T : int
        Sample size.
    n_breaks : int, default=1
        Number of structural breaks.
    break_fractions : list of float, optional
        Break fractions on [0, 1]. If None, equally spaced.
    sigma_u : float, default=1.0
        Innovation standard deviation.
    seed : int, optional
        Random seed.
    
    Returns
    -------
    Y : ndarray of shape (T, 2)
        Simulated data.
    info : dict
        Simulation information.
    
    References
    ----------
    Table 1 in Franjic, Mößler, and Schweikert (2025).
    
    Examples
    --------
    >>> result = generate_dgp_case1(T=200, n_breaks=1)
    >>> print(f"Break at: {result['breaks']}")
    """
    N = 2
    r = 1
    
    # If break_fractions is provided, compute n_breaks from it
    if break_fractions is not None:
        n_breaks = len(break_fractions)
    
    # Default break fractions if not provided
    if break_fractions is None:
        if n_breaks == 0:
            break_fractions = []
        elif n_breaks == 1:
            break_fractions = [0.5]
        elif n_breaks == 2:
            break_fractions = [0.33, 0.67]
        elif n_breaks == 4:
            break_fractions = [0.2, 0.4, 0.6, 0.8]
        else:
            break_fractions = [(i + 1) / (n_breaks + 1) for i in range(n_breaks)]
    
    # Convert fractions to indices
    breaks = [int(f * T) for f in break_fractions]
    
    # Constant α
    alpha = np.array([[-0.5], [0.5]])
    
    # Regime-specific β: n_breaks + 1 regimes
    beta_list = []
    beta_0 = np.array([[1.0], [-1.0]])
    beta_list.append(beta_0)
    
    for j in range(n_breaks):
        change = np.array([[0.0], [(-1) ** (j + 1)]])
        beta_j = beta_list[-1] + change
        beta_list.append(beta_j)
    
    # α is constant across regimes (n_breaks + 1 copies)
    alpha_list = [alpha.copy() for _ in range(len(beta_list))]
    
    # Innovation covariance
    Sigma_u = sigma_u ** 2 * np.eye(N)
    
    # Generate data
    Y, info = simulate_vecm_breaks(
        T=T, N=N, r=r, breaks=breaks,
        alpha_list=alpha_list, beta_list=beta_list,
        Sigma_u=Sigma_u, seed=seed
    )
    
    # Add break magnitude to info
    break_magnitudes = []
    for j in range(len(info['Pi']) - 1):
        mag = norm(info['Pi'][j + 1] - info['Pi'][j], 'fro')
        break_magnitudes.append(mag)
    info['break_magnitudes'] = break_magnitudes
    
    # Return info dictionary (which includes Y)
    return info


def generate_dgp_case2(
    T: int,
    n_breaks: int = 1,
    break_fractions: Optional[List[float]] = None,
    sigma_u: float = 1.0,
    seed: Optional[int] = None
) -> Dict:
    """
    Generate data from Case 2 DGP: changing α and β.
    
    Following the simulation setup in Table 2 of the paper:
        α_0 = [-0.5, 0]'
        α_j = α_{j-1} + (-1)^j [-0.5, -0.5]' (alternating leader/lagger)
        β_0 = [1, -1]'
        β_j = β_{j-1} + (-1)^j [0, 1]' (as in Case 1)
    
    Parameters
    ----------
    T : int
        Sample size.
    n_breaks : int, default=1
        Number of structural breaks.
    break_fractions : list of float, optional
        Break fractions on [0, 1]. If None, equally spaced.
    sigma_u : float, default=1.0
        Innovation standard deviation.
    seed : int, optional
        Random seed.
    
    Returns
    -------
    info : dict
        Dictionary containing 'Y', 'delta_Y', 'alpha', 'beta', etc.
    
    References
    ----------
    Table 2 in Franjic, Mößler, and Schweikert (2025).
    
    Examples
    --------
    >>> result = generate_dgp_case2(T=200, n_breaks=1)
    >>> print(f"Break magnitude: {result['break_magnitudes']}")
    """
    N = 2
    r = 1
    
    # If break_fractions is provided, compute n_breaks from it
    if break_fractions is not None:
        n_breaks = len(break_fractions)
    
    # Default break fractions if not provided
    if break_fractions is None:
        if n_breaks == 0:
            break_fractions = []
        elif n_breaks == 1:
            break_fractions = [0.5]
        elif n_breaks == 2:
            break_fractions = [0.33, 0.67]
        elif n_breaks == 4:
            break_fractions = [0.2, 0.4, 0.6, 0.8]
        else:
            break_fractions = [(i + 1) / (n_breaks + 1) for i in range(n_breaks)]
    
    # Convert fractions to indices
    breaks = [int(f * T) for f in break_fractions]
    
    # Initial values
    alpha_0 = np.array([[-0.5], [0.0]])
    beta_0 = np.array([[1.0], [-1.0]])
    
    alpha_list = [alpha_0]
    beta_list = [beta_0]
    
    for j in range(n_breaks):
        # α changes
        alpha_change = np.array([[(-1) ** (j + 1) * (-0.5)], 
                                  [(-1) ** (j + 1) * (-0.5)]])
        alpha_j = alpha_list[-1] + alpha_change
        alpha_list.append(alpha_j)
        
        # β changes (same as Case 1)
        beta_change = np.array([[0.0], [(-1) ** (j + 1)]])
        beta_j = beta_list[-1] + beta_change
        beta_list.append(beta_j)
    
    # Innovation covariance
    Sigma_u = sigma_u ** 2 * np.eye(N)
    
    # Generate data
    Y, info = simulate_vecm_breaks(
        T=T, N=N, r=r, breaks=breaks,
        alpha_list=alpha_list, beta_list=beta_list,
        Sigma_u=Sigma_u, seed=seed
    )
    
    # Add break magnitude to info
    break_magnitudes = []
    for j in range(len(info['Pi']) - 1):
        mag = norm(info['Pi'][j + 1] - info['Pi'][j], 'fro')
        break_magnitudes.append(mag)
    info['break_magnitudes'] = break_magnitudes
    
    # Return info dictionary (which includes Y)
    return info


def generate_dgp_with_short_run(
    T: int,
    n_breaks: int = 1,
    break_fractions: Optional[List[float]] = None,
    case: int = 1,
    K: int = 2,
    k_ar: Optional[int] = None,
    sigma_u: float = 1.0,
    seed: Optional[int] = None
) -> Dict:
    """
    Generate VECM data with short-run dynamics.
    
    Includes Γ_1 matrix following Equation (23) in the paper:
        Γ_1 = [[-0.1, 0], [0, -0.1]]
    
    Parameters
    ----------
    T : int
        Sample size.
    n_breaks : int, default=1
        Number of breaks.
    break_fractions : list of float, optional
        Break fractions.
    case : int, default=1
        DGP case (1 or 2).
    K : int, default=2
        VAR lag order.
    k_ar : int, optional
        Alias for K (VAR lag order).
    sigma_u : float, default=1.0
        Innovation SD.
    seed : int, optional
        Random seed.
    
    Returns
    -------
    info : dict
        Dictionary containing 'Y', 'delta_Y', 'Gamma', etc.
    
    References
    ----------
    Tables A1-A2 in Franjic, Mößler, and Schweikert (2025).
    """
    # Handle k_ar alias
    if k_ar is not None:
        K = k_ar
    
    # Get base DGP parameters (don't use the data, just get config)
    if case == 1:
        base_info = generate_dgp_case1(T, n_breaks, break_fractions, sigma_u, seed)
    else:
        base_info = generate_dgp_case2(T, n_breaks, break_fractions, sigma_u, seed)
    
    N = base_info['Y'].shape[1]
    
    # Short-run dynamics from Equation (23)
    Gamma = []
    if K >= 2:
        Gamma1 = np.array([[-0.1, 0.0], [0.0, -0.1]])
        Gamma.append(Gamma1)
    
    # Re-simulate with short-run dynamics
    Y, info = simulate_vecm_breaks(
        T=T, N=N, r=1,
        breaks=base_info['breaks'],
        alpha_list=base_info['alpha'],
        beta_list=base_info['beta'],
        Gamma=Gamma,
        Sigma_u=base_info['Sigma_u'],
        seed=seed
    )
    
    info['K'] = K
    
    # Return info dictionary (which includes Y)
    return info


def generate_dgp_three_variables(
    T: int,
    n_breaks: int = 1,
    break_fractions: Optional[List[float]] = None,
    case: int = 1,
    sigma_u: float = 1.0,
    seed: Optional[int] = None
) -> Tuple[np.ndarray, Dict]:
    """
    Generate three-variable VECM with r=2 cointegrating relations.
    
    Following Equations (25)-(26) in the paper:
        N = 3, r = 2
        β_0 = [[1, 0], [0, 1], [-1, -1]]'
    
    Parameters
    ----------
    T : int
        Sample size.
    n_breaks : int, default=1
        Number of breaks.
    break_fractions : list of float, optional
        Break fractions.
    case : int, default=1
        DGP case (1 or 2).
    sigma_u : float, default=1.0
        Innovation SD.
    seed : int, optional
        Random seed.
    
    Returns
    -------
    Y : ndarray of shape (T, 3)
        Simulated data.
    info : dict
        Simulation information.
    
    References
    ----------
    Table A3 in Franjic, Mößler, and Schweikert (2025).
    """
    N = 3
    r = 2
    
    # Default break fractions
    if break_fractions is None:
        if n_breaks == 1:
            break_fractions = [0.5]
        elif n_breaks == 2:
            break_fractions = [0.33, 0.67]
        elif n_breaks == 4:
            break_fractions = [0.2, 0.4, 0.6, 0.8]
        else:
            break_fractions = [(i + 1) / (n_breaks + 1) for i in range(n_breaks)]
    
    breaks = [int(f * T) for f in break_fractions]
    
    # Initial values from Equation (25)/(26)
    alpha_0 = np.array([[-0.5, 0.0], [0.0, -0.5], [0.0, 0.0]])
    beta_0 = np.array([[1.0, 0.0], [0.0, 1.0], [-1.0, -1.0]])
    
    alpha_list = [alpha_0]
    beta_list = [beta_0]
    
    for j in range(n_breaks):
        if case == 1:
            # Case 1: constant α, changing β
            alpha_j = alpha_0.copy()
            beta_change = np.array([[0.0, 0.0], [0.0, 0.0], 
                                   [(-1) ** (j + 1), (-1) ** (j + 1)]])
        else:
            # Case 2: changing α and β
            alpha_change = np.array([[0.25, 0.0], [0.0, 0.25], [0.25, 0.25]])
            alpha_j = alpha_list[-1] + (-1) ** (j + 1) * alpha_change
            beta_change = np.array([[0.0, 0.0], [0.0, 0.0], 
                                   [(-1) ** (j + 1), (-1) ** (j + 1)]])
        
        beta_j = beta_list[-1] + beta_change
        
        alpha_list.append(alpha_j)
        beta_list.append(beta_j)
    
    if case == 1:
        alpha_list = [alpha_0] * (n_breaks + 1)
    
    # Innovation covariance
    Sigma_u = sigma_u ** 2 * np.eye(N)
    
    Y, info = simulate_vecm_breaks(
        T=T, N=N, r=r, breaks=breaks,
        alpha_list=alpha_list, beta_list=beta_list,
        Sigma_u=Sigma_u, seed=seed
    )
    
    # Break magnitudes
    break_magnitudes = []
    for j in range(len(info['Pi']) - 1):
        mag = norm(info['Pi'][j + 1] - info['Pi'][j], 'fro')
        break_magnitudes.append(mag)
    info['break_magnitudes'] = break_magnitudes
    
    return Y, info


def generate_dgp_correlated_errors(
    T: int,
    n_breaks: int = 1,
    case: int = 1,
    rho: float = 0.8,
    sigma_u: float = 1.0,
    seed: Optional[int] = None
) -> Tuple[np.ndarray, Dict]:
    """
    Generate VECM with correlated innovations.
    
    Follows Tables S1-S2 in the Supplementary Material with
    contemporaneously correlated innovations.
    
    Parameters
    ----------
    T : int
        Sample size.
    n_breaks : int, default=1
        Number of breaks.
    case : int, default=1
        DGP case.
    rho : float, default=0.8
        Correlation coefficient between innovations.
    sigma_u : float, default=1.0
        Innovation SD.
    seed : int, optional
        Random seed.
    
    Returns
    -------
    Y : ndarray
        Simulated data.
    info : dict
        Simulation information.
    """
    # Get base parameters
    if case == 1:
        _, base_info = generate_dgp_case1(T, n_breaks, seed=seed)
    else:
        _, base_info = generate_dgp_case2(T, n_breaks, seed=seed)
    
    N = 2
    
    # Correlated innovation covariance
    Sigma_u = sigma_u ** 2 * np.array([[1.0, rho], [rho, 1.0]])
    
    Y, info = simulate_vecm_breaks(
        T=T, N=N, r=1,
        breaks=base_info['breaks'],
        alpha_list=base_info['alpha'],
        beta_list=base_info['beta'],
        Sigma_u=Sigma_u,
        seed=seed
    )
    
    info['rho'] = rho
    
    return Y, info


def monte_carlo_simulation(
    n_replications: int,
    T: int,
    dgp_func: callable = None,
    estimator: "VECMBreak" = None,
    break_fractions: Optional[List[float]] = None,
    case: int = 1,
    seed: Optional[int] = None,
    **dgp_kwargs
) -> Dict:
    """
    Run Monte Carlo simulation.
    
    Parameters
    ----------
    n_replications : int
        Number of Monte Carlo replications.
    T : int
        Sample size.
    dgp_func : callable, optional
        Data generating function. If None, uses default DGP based on case.
    estimator : VECMBreak, optional
        Estimator to use. If None, creates default VECMBreak estimator.
    break_fractions : list of float, optional
        Break fractions for default DGP. Default is [0.5].
    case : int, default=1
        DGP/estimation case (1 or 2). Used when dgp_func is None.
    seed : int, optional
        Random seed for reproducibility.
    **dgp_kwargs
        Additional arguments for DGP function.
    
    Returns
    -------
    results : dict
        Dictionary containing:
        - 'pce': Percentage correctly estimated (number of breaks)
        - 'mean_n_breaks': Mean number of breaks detected
        - 'break_fractions': List of estimated break fractions
        - 'alpha_estimates': List of α estimates
        - 'beta_estimates': List of β estimates
    """
    # Import VECMBreak here to avoid circular imports
    from .vecm_break import VECMBreak
    
    # Default break fractions
    if break_fractions is None:
        break_fractions = [0.5]
    
    # Set up default DGP function based on case
    if dgp_func is None:
        if case == 1:
            dgp_func = generate_dgp_case1
        else:
            dgp_func = generate_dgp_case2
        dgp_kwargs['break_fractions'] = break_fractions
    
    # Set up default estimator
    if estimator is None:
        estimator = VECMBreak(case=case, rank=1)
    
    # Set seed
    if seed is not None:
        np.random.seed(seed)
    
    results = {
        'n_breaks_estimated': [],
        'break_locations': [],
        'break_fractions': [],
        'alpha_estimates': [],
        'beta_estimates': [],
        'correct_detection': []
    }
    
    for rep in range(n_replications):
        # Generate data
        dgp_result = dgp_func(T=T, seed=rep if seed is None else seed + rep, **dgp_kwargs)
        
        # Handle both return types (dict or tuple)
        if isinstance(dgp_result, tuple):
            Y, true_info = dgp_result
        else:
            true_info = dgp_result
            Y = true_info['Y']
        
        true_breaks = true_info.get('breaks', true_info.get('true_breaks', []))
        n_true_breaks = len(true_breaks)
        
        # Fit estimator
        try:
            estimator.fit(Y)
            
            # Record results
            n_estimated = estimator.n_breaks_
            results['n_breaks_estimated'].append(n_estimated)
            results['break_locations'].append(estimator.breaks_)
            results['break_fractions'].append([b / T for b in estimator.breaks_])
            
            # Check correct detection
            correct = (n_estimated == n_true_breaks)
            results['correct_detection'].append(correct)
            
            # Store coefficient estimates
            if hasattr(estimator, 'alpha_'):
                results['alpha_estimates'].append(estimator.alpha_)
            if hasattr(estimator, 'beta_'):
                results['beta_estimates'].append(estimator.beta_)
                
        except Exception as e:
            warnings.warn(f"Replication {rep} failed: {e}")
            results['n_breaks_estimated'].append(np.nan)
            results['correct_detection'].append(False)
    
    # Compute summary statistics
    valid_detections = [c for c in results['correct_detection'] if c is not None]
    results['pce'] = np.mean(valid_detections) if valid_detections else 0.0
    
    valid_n_breaks = [n for n in results['n_breaks_estimated'] if not np.isnan(n)]
    results['mean_n_breaks'] = np.mean(valid_n_breaks) if valid_n_breaks else 0.0
    
    return results
