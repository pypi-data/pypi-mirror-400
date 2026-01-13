"""
Utility Functions for VECMBreak
===============================

This module provides utility functions for:
- Normalizing cointegrating vectors
- Computing information criteria
- Frisch-Waugh-Lovell projection
- Matrix operations for VECM analysis

References
----------
Phillips, P.C.B. (1991). Optimal Inference in Cointegrated Systems. 
    Econometrica, 59, 283-306.
Phillips, P.C.B. (1995). Fully Modified Least Squares and Vector Autoregression.
    Econometrica, 63, 1023-1078.
Hurn, S., Martin, V.L., & Harris, D. (2013). Econometric Modelling with Time Series.
    Cambridge University Press.
"""

import numpy as np
from numpy.linalg import inv, eig, svd, matrix_rank, lstsq
from scipy.linalg import sqrtm, pinv, eigh
from typing import Tuple, Optional, List, Union
import warnings


def normalize_cointegrating_vectors(
    beta: np.ndarray,
    alpha: Optional[np.ndarray] = None,
    normalization: str = "triangular",
    c: Optional[np.ndarray] = None,
    r: Optional[int] = None
) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
    """
    Normalize cointegrating vectors using specified normalization scheme.
    
    Following Phillips (1991, 1995), the triangular normalization imposes
    a structure such that:
        β_c = β(c'β)^(-1)
        α_c = αβ'c
    
    With c' = [I_r, 0_(r×(N-r))], this yields:
        β_c = [I_r, β_1^(-1)β_2']' = [I_r, b_1]
    
    Parameters
    ----------
    beta : ndarray of shape (N, r)
        Matrix of cointegrating vectors.
    alpha : ndarray of shape (N, r), optional
        Matrix of adjustment coefficients (loadings).
        If None, only beta_c is returned.
    normalization : str, default='triangular'
        Type of normalization:
        - 'triangular': Phillips triangular normalization
        - 'orthogonal': Orthogonal normalization
        - 'custom': Use provided c matrix
    c : ndarray of shape (N, r), optional
        Custom normalization matrix. Required if normalization='custom'.
    r : int, optional
        Cointegration rank (inferred from beta if not provided).
    
    Returns
    -------
    beta_c : ndarray of shape (N, r)
        Normalized cointegrating vectors.
    alpha_c : ndarray of shape (N, r), optional
        Correspondingly normalized adjustment coefficients.
        Only returned if alpha is provided.
    
    References
    ----------
    Phillips, P.C.B. (1991). Optimal Inference in Cointegrated Systems.
        Econometrica, 59, 283-306.
    Hurn, S., Martin, V.L., Yu, J., & Phillips, P.C.B. (2020). 
        Financial Econometric Modeling. Oxford University Press.
    
    Examples
    --------
    >>> beta = np.array([[-0.5, 0.3], [0.5, -0.2], [0.0, 0.5]])
    >>> alpha = np.array([[-0.1, 0.05], [0.2, -0.1], [0.0, 0.15]])
    >>> beta_c, alpha_c = normalize_cointegrating_vectors(beta, alpha)
    >>> 
    >>> # Or just normalize beta
    >>> beta_c = normalize_cointegrating_vectors(beta, r=2)
    """
    # Handle 1D beta
    if beta.ndim == 1:
        beta = beta.reshape(-1, 1)
    
    N = beta.shape[0]
    if r is None:
        r = beta.shape[1]
    
    if normalization == "triangular":
        # Triangular normalization: c' = [I_r, 0_(r×(N-r))]
        c = np.zeros((N, r))
        c[:r, :r] = np.eye(r)
    elif normalization == "orthogonal":
        # Orthogonal normalization
        c = beta.copy()
    elif normalization == "custom":
        if c is None:
            raise ValueError("Custom normalization requires a c matrix")
    else:
        raise ValueError(f"Unknown normalization: {normalization}")
    
    # Compute β_c = β(c'β)^(-1)
    c_prime_beta = c.T @ beta
    try:
        c_prime_beta_inv = inv(c_prime_beta)
    except np.linalg.LinAlgError:
        warnings.warn("Singular matrix in normalization, using pseudo-inverse")
        c_prime_beta_inv = pinv(c_prime_beta)
    
    beta_c = beta @ c_prime_beta_inv
    
    # If alpha is provided, compute and return both
    if alpha is not None:
        # Compute α_c = αβ'c
        alpha_c = alpha @ beta.T @ c
        return beta_c, alpha_c
    
    return beta_c


def compute_information_criterion(
    ssr: float,
    T: int,
    m: int,
    N: int = 2,
    criterion: str = "bic_modified",
    C: float = 1.0
) -> float:
    """
    Compute information criterion for model selection in structural break detection.
    
    Following Chan et al. (2014) and Schweikert (2025), the modified BIC
    is given by:
        IC(m, t) = S_T(t_1, ..., t_m) + m * C * T^(3/4) * log(T)
    
    Parameters
    ----------
    ssr : float
        Sum of squared residuals over all equations.
    T : int
        Sample size (number of observations).
    m : int
        Number of structural breaks.
    N : int
        Number of equations in the VECM.
    criterion : str, default='bic_modified'
        Information criterion to use:
        - 'bic_modified': Modified BIC from Schweikert (2025)
        - 'bic': Standard BIC
        - 'aic': Akaike Information Criterion
        - 'hqc': Hannan-Quinn Criterion
    C : float, default=1.0
        Penalty constant. Following the paper, C is set to penalize
        the total number of nonzero coefficients.
    
    Returns
    -------
    ic : float
        Information criterion value.
    
    References
    ----------
    Chan, N.H., Yau, C.Y., & Zhang, R.M. (2014). Group LASSO for Structural 
        Break Time Series. JASA, 109, 590-599.
    Schweikert, K. (2025). Detecting Multiple Structural Breaks. 
        Oxford Bulletin of Economics and Statistics.
    
    Notes
    -----
    The modified BIC (Equation 11 in the paper) uses T^(3/4) * log(T) 
    as the penalty term, which provides consistent break detection.
    """
    if criterion == "bic_modified":
        # Equation (11) from the paper
        # IC(m, t) = S_T(t_1, ..., t_m) + m * C * T^(3/4) * log(T)
        # In finite samples, C is set so that the penalty equals
        # the number of nonzero coefficients
        n_params = m * N * N  # Number of parameters per break
        penalty = m * C * (T ** 0.75) * np.log(T)
        ic = ssr + penalty
    elif criterion == "bic":
        # Standard BIC: log(SSR/T) + (k/T) * log(T)
        n_params = (m + 1) * N * N
        ic = T * np.log(ssr / T) + n_params * np.log(T)
    elif criterion == "aic":
        # AIC: log(SSR/T) + 2k/T
        n_params = (m + 1) * N * N
        ic = T * np.log(ssr / T) + 2 * n_params
    elif criterion == "hqc":
        # Hannan-Quinn: log(SSR/T) + 2k * log(log(T)) / T
        n_params = (m + 1) * N * N
        ic = T * np.log(ssr / T) + 2 * n_params * np.log(np.log(T))
    else:
        raise ValueError(f"Unknown criterion: {criterion}")
    
    return ic


def frisch_waugh_projection(
    Y: np.ndarray,
    X: np.ndarray,
    Z: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Apply Frisch-Waugh-Lovell theorem to concentrate out control variables.
    
    The FWL theorem states that in the regression:
        Y = Xβ + Zγ + ε
    
    The OLS estimate of β can be obtained from:
        M_Z Y = M_Z X β + ε*
    
    where M_Z = I - Z(Z'Z)^(-1)Z' is the residual maker matrix.
    
    Parameters
    ----------
    Y : ndarray of shape (T, N)
        Dependent variable matrix (ΔY_t in VECM context).
    X : ndarray of shape (T, k)
        Variables of interest (Y_{t-1} for error correction term).
    Z : ndarray of shape (T, p)
        Control variables to concentrate out (lagged differences, deterministics).
    
    Returns
    -------
    R0 : ndarray of shape (T, N)
        Residuals from regressing Y on Z.
    R1 : ndarray of shape (T, k)
        Residuals from regressing X on Z.
    
    Notes
    -----
    This is used in the VECM context to concentrate out short-run dynamics
    and deterministic terms before applying the break detection procedure.
    As stated in Equation (4) of the paper:
        R0_t = Π R1_t + e_t
    
    Examples
    --------
    >>> T, N = 200, 2
    >>> delta_Y = np.random.randn(T, N)
    >>> Y_lag = np.random.randn(T, N)
    >>> delta_Y_lag = np.random.randn(T, N)
    >>> R0, R1 = frisch_waugh_projection(delta_Y, Y_lag, delta_Y_lag)
    """
    T = Y.shape[0]
    
    # Compute M_Z = I - Z(Z'Z)^(-1)Z'
    # For numerical stability, use QR decomposition or SVD
    if Z.shape[1] > 0:
        # Use least squares to compute residuals
        # R0 = Y - Z @ (Z'Z)^(-1) @ Z' @ Y
        coef_Y, _, _, _ = lstsq(Z, Y, rcond=None)
        R0 = Y - Z @ coef_Y
        
        coef_X, _, _, _ = lstsq(Z, X, rcond=None)
        R1 = X - Z @ coef_X
    else:
        R0 = Y.copy()
        R1 = X.copy()
    
    return R0, R1


def construct_design_matrix(
    R1: np.ndarray,
    T: int,
    N: int
) -> np.ndarray:
    """
    Construct the design matrix Z for the group LASSO estimation.
    
    Following Equation (8) in the paper, the design matrix is:
    
    Z = | Z'_1   0     0    ...  0   |
        | Z'_2  Z'_2   0    ...  0   |
        | Z'_3  Z'_3  Z'_3  ...  0   |
        | ...                        |
        | Z'_T  Z'_T  Z'_T  ... Z'_T |
    
    Parameters
    ----------
    R1 : ndarray of shape (T, N)
        Residuals from projecting Y_{t-1} on control variables.
    T : int
        Sample size.
    N : int
        Number of equations.
    
    Returns
    -------
    Z_design : ndarray of shape (T, T*N)
        Design matrix for break detection.
    
    Notes
    -----
    The full design matrix Z from Equation (9) is:
        Z = I_N ⊗ Z_design
    which has dimensions (T*N) × (T*N²)
    """
    Z_design = np.zeros((T, T * N))
    
    for t in range(T):
        # Row t has R1'_t in columns 0 to (t+1)*N
        for s in range(t + 1):
            Z_design[t, s * N:(s + 1) * N] = R1[t, :]
    
    return Z_design


def vec_operator(A: np.ndarray) -> np.ndarray:
    """
    Vectorize a matrix by stacking columns into a column vector.
    
    Parameters
    ----------
    A : ndarray of shape (m, n)
        Input matrix.
    
    Returns
    -------
    vec_A : ndarray of shape (m*n,)
        Vectorized matrix (column-major order).
    """
    return A.flatten(order='F')


def inv_vec_operator(
    vec_A: np.ndarray, 
    n_rows: Optional[int] = None, 
    n_cols: Optional[int] = None,
    shape: Optional[Tuple[int, int]] = None
) -> np.ndarray:
    """
    Reshape a vector back into a matrix.
    
    Parameters
    ----------
    vec_A : ndarray of shape (m*n,)
        Vectorized matrix.
    n_rows : int, optional
        Number of rows.
    n_cols : int, optional
        Number of columns.
    shape : tuple of (m, n), optional
        Target shape (alternative to n_rows, n_cols).
    
    Returns
    -------
    A : ndarray of shape (m, n)
        Reshaped matrix.
    """
    if shape is not None:
        return vec_A.reshape(shape, order='F')
    elif n_rows is not None and n_cols is not None:
        return vec_A.reshape((n_rows, n_cols), order='F')
    else:
        # Try to infer square matrix
        n = int(np.sqrt(len(vec_A)))
        if n * n == len(vec_A):
            return vec_A.reshape((n, n), order='F')
        raise ValueError("Must provide shape or (n_rows, n_cols)")


def compute_pi_from_alpha_beta(
    alpha: np.ndarray,
    beta: np.ndarray
) -> np.ndarray:
    """
    Compute the Π matrix from α and β.
    
    Π = αβ'
    
    Parameters
    ----------
    alpha : ndarray of shape (N, r)
        Adjustment coefficients.
    beta : ndarray of shape (N, r)
        Cointegrating vectors.
    
    Returns
    -------
    Pi : ndarray of shape (N, N)
        Product matrix.
    """
    return alpha @ beta.T


def decompose_pi(
    Pi: np.ndarray,
    r: int,
    method: str = "eigenvalue"
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Decompose Π matrix into α and β components.
    
    Given Π = αβ' with rank r, find α (N×r) and β (N×r).
    
    Parameters
    ----------
    Pi : ndarray of shape (N, N)
        Matrix to decompose.
    r : int
        Cointegration rank.
    method : str, default='eigenvalue'
        Decomposition method:
        - 'eigenvalue': Use eigenvalue decomposition
        - 'svd': Use singular value decomposition
    
    Returns
    -------
    alpha : ndarray of shape (N, r)
        Adjustment coefficients.
    beta : ndarray of shape (N, r)
        Cointegrating vectors.
    """
    N = Pi.shape[0]
    
    if method == "eigenvalue":
        # Use eigenvalue decomposition
        eigenvalues, eigenvectors = eig(Pi)
        # Sort by absolute value of eigenvalues
        idx = np.argsort(np.abs(eigenvalues))[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]
        
        # Take r largest eigenvectors
        beta = eigenvectors[:, :r].real
        # Compute alpha such that Pi = alpha @ beta'
        alpha = (Pi @ beta @ inv(beta.T @ beta)).real
        
    elif method == "svd":
        # Use SVD: Pi = U @ S @ V'
        U, S, Vt = svd(Pi)
        # Take r largest singular values
        alpha = U[:, :r] @ np.diag(np.sqrt(S[:r]))
        beta = Vt[:r, :].T @ np.diag(np.sqrt(S[:r]))
    else:
        raise ValueError(f"Unknown method: {method}")
    
    return alpha, beta


def recover_deterministic_contributions(
    alpha: np.ndarray,
    mu: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Recover short-run and long-run contributions of deterministic terms.
    
    Following Equation (19) in the paper:
        δ_j = α_⊥(α'_⊥ α_⊥)^(-1) α'_⊥ μ_j  (short-run)
        β_j = (α'α)^(-1) α' μ_j              (long-run)
    
    where j=1 for constant and j=2 for trend.
    
    Parameters
    ----------
    alpha : ndarray of shape (N, r)
        Adjustment coefficients.
    mu : ndarray of shape (N,) or (N, 2)
        Unrestricted deterministic coefficients.
        If shape is (N, 2), first column is constant, second is trend.
    
    Returns
    -------
    delta : ndarray
        Short-run contributions of deterministics.
    beta_det : ndarray
        Long-run contributions to cointegrating relationships.
    
    References
    ----------
    Hurn, S., Martin, V.L., & Harris, D. (2013). Econometric Modelling 
        with Time Series. Cambridge University Press, Equation (19).
    """
    N, r = alpha.shape
    
    # Compute α_⊥ (orthogonal complement of α)
    # α_⊥ spans the null space of α'
    U, S, Vt = svd(alpha)
    alpha_perp = U[:, r:]  # Last N-r columns
    
    if mu.ndim == 1:
        mu = mu.reshape(-1, 1)
    
    n_det = mu.shape[1]
    delta = np.zeros((N, n_det))
    beta_det = np.zeros((r, n_det))
    
    for j in range(n_det):
        # Short-run contribution
        # δ_j = α_⊥(α'_⊥ α_⊥)^(-1) α'_⊥ μ_j
        alpha_perp_gram = alpha_perp.T @ alpha_perp
        if alpha_perp.shape[1] > 0:
            delta[:, j] = alpha_perp @ inv(alpha_perp_gram) @ alpha_perp.T @ mu[:, j]
        
        # Long-run contribution
        # β_j = (α'α)^(-1) α' μ_j
        alpha_gram = alpha.T @ alpha
        beta_det[:, j] = inv(alpha_gram) @ alpha.T @ mu[:, j]
    
    return delta.squeeze(), beta_det.squeeze()


def check_stationarity_conditions(
    alpha: np.ndarray,
    beta: np.ndarray,
    Gamma: Optional[List[np.ndarray]] = None,
    K: int = 1
) -> bool:
    """
    Check if the VECM satisfies stationarity conditions (Assumption 1).
    
    The characteristic polynomial of the VECM is:
        det[(1-z)I_N - αβ'z - Σ Γ_i(1-z)z^i] = 0
    
    All roots must satisfy either z=1 or |z|>1.
    
    Parameters
    ----------
    alpha : ndarray of shape (N, r)
        Adjustment coefficients.
    beta : ndarray of shape (N, r)
        Cointegrating vectors.
    Gamma : list of ndarrays, optional
        Short-run dynamics matrices [Γ_1, ..., Γ_{K-1}].
    K : int, default=1
        Lag order of the VAR.
    
    Returns
    -------
    is_stationary : bool
        True if stationarity conditions are satisfied.
    
    Notes
    -----
    This implements the check from Assumption 1(ii) in the paper.
    """
    N = alpha.shape[0]
    
    if Gamma is None:
        Gamma = []
    
    # Build companion form matrix
    Pi = alpha @ beta.T
    
    # For K=1, just check eigenvalues of I + Π
    if K == 1:
        companion = np.eye(N) + Pi
        eigenvalues = eig(companion)[0]
        # All eigenvalues should be inside unit circle or at 1
        return all(np.abs(eigenvalues) <= 1 + 1e-10)
    
    # For K>1, build full companion form
    # This is more complex - simplified version
    companion_dim = N * K
    companion = np.zeros((companion_dim, companion_dim))
    
    # Fill in the companion form
    # First block row
    companion[:N, :N] = np.eye(N) + Pi
    for i, Gamma_i in enumerate(Gamma):
        if i < K - 1:
            companion[:N, N*(i+1):N*(i+2)] = Gamma_i
    
    # Shift matrix for remaining rows
    companion[N:, :-N] = np.eye(N * (K - 1))
    
    eigenvalues = eig(companion)[0]
    
    # Check: all eigenvalues should have modulus <= 1
    # with exactly r eigenvalues at 1 (cointegration)
    return all(np.abs(eigenvalues) <= 1 + 1e-10)


def check_stationarity(A: np.ndarray) -> bool:
    """
    Check if a companion matrix represents a stationary process.
    
    A process is stationary if all eigenvalues of the companion matrix
    have modulus strictly less than 1.
    
    Parameters
    ----------
    A : ndarray of shape (N, N) or (NK, NK)
        Companion matrix from VAR representation.
    
    Returns
    -------
    is_stationary : bool
        True if the process is stationary.
    """
    eigenvalues = eig(A)[0]
    return np.all(np.abs(eigenvalues) < 1.0)


def compute_residual_covariance(
    residuals: np.ndarray,
    ddof: int = 0
) -> np.ndarray:
    """
    Compute the covariance matrix of residuals.
    
    Parameters
    ----------
    residuals : ndarray of shape (T, N)
        Residual matrix.
    ddof : int, default=0
        Degrees of freedom correction.
    
    Returns
    -------
    Sigma : ndarray of shape (N, N)
        Estimated covariance matrix.
    """
    T = residuals.shape[0]
    return (residuals.T @ residuals) / (T - ddof)


def compute_frobenius_norm(A: np.ndarray) -> float:
    """
    Compute Frobenius norm of a matrix.
    
    ||A||_F = sqrt(sum_ij a_ij^2)
    
    Parameters
    ----------
    A : ndarray
        Input matrix.
    
    Returns
    -------
    norm : float
        Frobenius norm.
    """
    return np.sqrt(np.sum(A ** 2))


def compute_break_magnitude(
    Pi_before: np.ndarray,
    Pi_after: np.ndarray
) -> float:
    """
    Compute the magnitude of a structural break.
    
    The break magnitude is the Frobenius norm of the change:
        ||Π_j - Π_{j-1}||_F
    
    Parameters
    ----------
    Pi_before : ndarray of shape (N, N)
        Pi matrix before break.
    Pi_after : ndarray of shape (N, N)
        Pi matrix after break.
    
    Returns
    -------
    magnitude : float
        Break magnitude (Frobenius norm).
    """
    return compute_frobenius_norm(Pi_after - Pi_before)
