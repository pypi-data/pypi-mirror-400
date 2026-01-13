"""
Output Formatting for VECMBreak Results
=======================================

This module provides functions to generate publication-quality output 
matching the format of Tables and Figures in Franjic, Mößler, and 
Schweikert (2025).

Output Formats
--------------
- Monte Carlo simulation tables (Tables 1-3 style)
- Estimation results tables (Tables 4-6 style)
- Time series plots (Figure 1 style)
- IRF grid plots (Figure 2 style)

References
----------
Franjic, D., Mößler, M., & Schweikert, K. (2025). Multiple Structural Breaks 
in Vector Error Correction Models. University of Hohenheim.
"""

import numpy as np
from typing import Dict, List, Optional, Union, Tuple
import warnings

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


# =============================================================================
# Monte Carlo Simulation Tables (Tables 1-3 style)
# =============================================================================

def format_monte_carlo_table(
    mc_results: Dict,
    true_params: Dict,
    title: str = "Monte Carlo Simulation Results",
    case: int = 1,
    include_coefficients: bool = True,
    precision: int = 3
) -> str:
    """
    Format Monte Carlo simulation results as a paper-style table.
    
    Produces output matching Tables 1-2 in the paper with:
    - pce (percentage correct estimation)
    - τ (break fractions with standard deviations)
    - Coefficient estimates with standard deviations
    
    Parameters
    ----------
    mc_results : dict
        Results from monte_carlo_simulation() containing:
        - 'pce': Percentage correctly estimated
        - 'break_fractions': List of estimated break fractions
        - 'alpha_estimates': List of α estimates
        - 'beta_estimates': List of β estimates
    true_params : dict
        True parameter values for comparison
    title : str
        Table title
    case : int
        Case 1 or 2 (affects output format)
    include_coefficients : bool
        Whether to include coefficient estimates
    precision : int
        Decimal places for formatting
    
    Returns
    -------
    table_str : str
        Formatted table string
    
    Examples
    --------
    >>> from vecmbreak import monte_carlo_simulation, generate_dgp_case1
    >>> mc_results = monte_carlo_simulation(n_replications=100, T=200, case=1)
    >>> true_params = {'break_fractions': [0.5], 'alpha': [...], 'beta': [...]}
    >>> print(format_monte_carlo_table(mc_results, true_params))
    """
    lines = []
    lines.append("=" * 80)
    lines.append(f"{title}")
    lines.append("=" * 80)
    
    # Sample info
    n_reps = len(mc_results.get('n_breaks_estimated', []))
    lines.append(f"Number of replications: {n_reps}")
    
    # True breaks info
    true_breaks = true_params.get('break_fractions', [])
    n_breaks = len(true_breaks)
    lines.append(f"True number of breaks: {n_breaks}")
    if n_breaks > 0:
        tau_str = ", ".join([f"τ{i+1}={t:.2f}" for i, t in enumerate(true_breaks)])
        lines.append(f"True break fractions: {tau_str}")
    
    lines.append("-" * 80)
    
    # PCE (percentage correct estimation)
    pce = mc_results.get('pce', 0) * 100  # Convert to percentage
    lines.append(f"pce: {pce:.1f}%")
    
    # Break fraction estimates
    break_fracs = mc_results.get('break_fractions', [])
    if break_fracs and any(len(bf) > 0 for bf in break_fracs):
        lines.append("")
        lines.append("Estimated Break Fractions:")
        
        # Compute statistics for each break
        for k in range(n_breaks):
            k_estimates = []
            for bf in break_fracs:
                if len(bf) > k:
                    k_estimates.append(bf[k])
            
            if k_estimates:
                mean_tau = np.mean(k_estimates)
                std_tau = np.std(k_estimates)
                lines.append(f"  τ{k+1}: {mean_tau:.{precision}f} ({std_tau:.{precision}f})")
    
    # Coefficient estimates
    if include_coefficients:
        lines.append("")
        lines.append("-" * 80)
        lines.append("Coefficient Estimates (mean, std):")
        
        # Beta estimates
        beta_estimates = mc_results.get('beta_estimates', [])
        if beta_estimates:
            lines.append("")
            lines.append("Cointegrating Coefficients (β):")
            _format_coefficient_stats(lines, beta_estimates, 'b', case, precision)
        
        # Alpha estimates  
        alpha_estimates = mc_results.get('alpha_estimates', [])
        if alpha_estimates:
            lines.append("")
            lines.append("Adjustment Coefficients (α):")
            _format_alpha_stats(lines, alpha_estimates, case, precision)
    
    lines.append("=" * 80)
    
    return "\n".join(lines)


def _format_coefficient_stats(
    lines: List[str], 
    estimates: List, 
    prefix: str,
    case: int,
    precision: int
) -> None:
    """Helper to format coefficient statistics."""
    if not estimates:
        return
    
    # Determine number of regimes from first valid estimate
    n_regimes = 0
    for est in estimates:
        if isinstance(est, list) and len(est) > 0:
            n_regimes = len(est)
            break
        elif isinstance(est, np.ndarray):
            n_regimes = 1
            break
    
    if n_regimes == 0:
        return
    
    # Collect estimates for each regime
    for j in range(n_regimes):
        regime_estimates = []
        for est in estimates:
            try:
                if isinstance(est, list) and len(est) > j:
                    regime_estimates.append(np.array(est[j]))
                elif isinstance(est, np.ndarray) and j == 0:
                    regime_estimates.append(est)
            except:
                continue
        
        if regime_estimates:
            # Stack and compute statistics
            stacked = np.array(regime_estimates)
            mean_est = np.mean(stacked, axis=0)
            std_est = np.std(stacked, axis=0)
            
            # Format output - extract free coefficients under triangular normalization
            if mean_est.ndim == 2:
                # For β, the free coefficient is b_{j,1} (second row, first column typically)
                N, r = mean_est.shape
                for col in range(r):
                    # Under triangular normalization, row > col contains free params
                    for row in range(col + 1, N):
                        lines.append(
                            f"  {prefix}{j},{row+1}: {mean_est[row, col]:.{precision}f} "
                            f"({std_est[row, col]:.{precision}f})"
                        )
            else:
                # 1D array
                for i, (m, s) in enumerate(zip(mean_est.flatten(), std_est.flatten())):
                    lines.append(f"  {prefix}{j},{i+1}: {m:.{precision}f} ({s:.{precision}f})")


def _format_alpha_stats(
    lines: List[str],
    estimates: List,
    case: int,
    precision: int
) -> None:
    """Helper to format alpha coefficient statistics."""
    if not estimates:
        return
    
    if case == 1:
        # Constant alpha - collect all estimates
        all_alphas = []
        for est in estimates:
            if isinstance(est, np.ndarray):
                all_alphas.append(est)
            elif isinstance(est, list) and len(est) > 0:
                all_alphas.append(np.array(est[0]))
        
        if all_alphas:
            stacked = np.array(all_alphas)
            mean_est = np.mean(stacked, axis=0)
            std_est = np.std(stacked, axis=0)
            
            for i in range(mean_est.shape[0]):
                for k in range(mean_est.shape[1] if mean_est.ndim > 1 else 1):
                    val = mean_est[i, k] if mean_est.ndim > 1 else mean_est[i]
                    sd = std_est[i, k] if std_est.ndim > 1 else std_est[i]
                    lines.append(f"  α{i+1}: {val:.{precision}f} ({sd:.{precision}f})")
    else:
        # Case 2: regime-specific alpha
        _format_coefficient_stats(lines, estimates, 'α', case, precision)


def create_monte_carlo_dataframe(
    mc_results: Dict,
    true_params: Dict,
    case: int = 1
) -> "pd.DataFrame":
    """
    Create a pandas DataFrame from Monte Carlo results.
    
    Produces a DataFrame matching the format of Tables 1-2 in the paper,
    suitable for export to LaTeX or Excel.
    
    Parameters
    ----------
    mc_results : dict
        Results from monte_carlo_simulation()
    true_params : dict
        True parameter values
    case : int
        Case 1 or 2
    
    Returns
    -------
    df : pd.DataFrame
        Formatted results DataFrame
    
    Examples
    --------
    >>> df = create_monte_carlo_dataframe(mc_results, true_params)
    >>> print(df.to_latex())
    """
    if not HAS_PANDAS:
        raise ImportError("pandas is required for DataFrame output. "
                         "Install with: pip install pandas")
    
    data = {}
    
    # PCE
    data['pce'] = [mc_results.get('pce', 0) * 100]
    
    # Break fractions
    break_fracs = mc_results.get('break_fractions', [])
    true_breaks = true_params.get('break_fractions', [])
    n_breaks = len(true_breaks)
    
    for k in range(n_breaks):
        k_estimates = [bf[k] for bf in break_fracs if len(bf) > k]
        if k_estimates:
            mean_tau = np.mean(k_estimates)
            std_tau = np.std(k_estimates)
            data[f'τ{k+1}'] = [f"{mean_tau:.3f} ({std_tau:.3f})"]
    
    df = pd.DataFrame(data)
    return df


# =============================================================================
# Estimation Results Tables (Tables 4-6 style)
# =============================================================================

def format_estimation_results(
    results,
    variable_names: Optional[List[str]] = None,
    date_index: Optional[List] = None,
    title: str = "VECM Estimation Results",
    include_se: bool = True,
    precision: int = 3
) -> str:
    """
    Format VECMBreak estimation results as paper-style tables.
    
    Produces output matching Tables 4-6 in the paper with:
    - Cointegrating coefficients (β̂) with standard errors
    - Adjustment coefficients (α̂) with standard errors
    - Regime-specific estimates
    
    Parameters
    ----------
    results : VECMBreakResults
        Results object from VECMBreak.fit()
    variable_names : list of str, optional
        Names for variables (e.g., ['r10y', 'r5y', 'r1y'])
    date_index : list, optional
        Date index for break date formatting
    title : str
        Table title
    include_se : bool
        Whether to include standard errors
    precision : int
        Decimal places
    
    Returns
    -------
    table_str : str
        Formatted table string
    
    Examples
    --------
    >>> model = VECMBreak(case=2, rank=1)
    >>> results = model.fit(Y)
    >>> print(format_estimation_results(results, 
    ...                                 variable_names=['y1', 'y2']))
    """
    lines = []
    lines.append("=" * 80)
    lines.append(f"{title}")
    lines.append("=" * 80)
    
    # Model info
    lines.append(f"Sample size (T): {results.T}")
    lines.append(f"Number of variables (N): {results.N}")
    lines.append(f"Cointegration rank (r): {results.r}")
    lines.append(f"Case: {results.case}")
    lines.append(f"Number of breaks: {results.n_breaks}")
    
    if results.n_breaks > 0:
        breaks_str = ", ".join([str(b) for b in results.breaks])
        fracs_str = ", ".join([f"{f:.3f}" for f in results.break_fractions])
        lines.append(f"Break locations: [{breaks_str}]")
        lines.append(f"Break fractions: [{fracs_str}]")
    
    lines.append("-" * 80)
    
    # Variable names
    if variable_names is None:
        variable_names = [f"y{i+1}" for i in range(results.N)]
    
    n_regimes = results.n_breaks + 1
    
    # Format regime-specific results
    for j in range(n_regimes):
        lines.append("")
        lines.append(f"--- Regime {j + 1} ---")
        
        # Period
        if j == 0:
            start = 1
        else:
            start = results.breaks[j-1] + 1
        
        if j < results.n_breaks:
            end = results.breaks[j]
        else:
            end = results.T
        
        # Format with dates if available
        if date_index is not None and len(date_index) >= results.T:
            try:
                start_date = date_index[start - 1]
                end_date = date_index[min(end - 1, len(date_index) - 1)]
                lines.append(f"Period: {start_date} - {end_date}")
            except:
                lines.append(f"Period: [{start}, {end}]")
        else:
            lines.append(f"Period: [{start}, {end}]")
        
        lines.append("")
        
        # Cointegrating coefficients (β)
        lines.append("Cointegrating Coefficients (β̂):")
        beta_j = results.beta[j] if isinstance(results.beta, list) else results.beta
        _format_beta_table(lines, beta_j, variable_names, precision)
        
        lines.append("")
        
        # Adjustment coefficients (α)
        lines.append("Adjustment Coefficients (α̂):")
        if results.case == 1:
            alpha_j = results.alpha
        else:
            alpha_j = results.alpha[j] if isinstance(results.alpha, list) else results.alpha
        _format_alpha_table(lines, alpha_j, variable_names, precision)
    
    lines.append("")
    lines.append("=" * 80)
    lines.append(f"Information Criterion: {results.ic:.4f}")
    lines.append(f"Sum of Squared Residuals: {results.ssr:.4f}")
    lines.append("=" * 80)
    
    return "\n".join(lines)


def _format_beta_table(
    lines: List[str],
    beta: np.ndarray,
    var_names: List[str],
    precision: int
) -> None:
    """Format beta matrix with triangular normalization display."""
    if beta is None:
        lines.append("  Not estimated")
        return
    
    beta = np.atleast_2d(beta)
    N, r = beta.shape
    
    # Header
    header = "         " + "  ".join([f"β{k+1:>8}" for k in range(r)])
    lines.append(header)
    
    # Rows
    for i in range(N):
        var_name = var_names[i] if i < len(var_names) else f"y{i+1}"
        row_vals = "  ".join([f"{beta[i, k]:>10.{precision}f}" for k in range(r)])
        lines.append(f"  {var_name:<6}{row_vals}")


def _format_alpha_table(
    lines: List[str],
    alpha: np.ndarray,
    var_names: List[str],
    precision: int
) -> None:
    """Format alpha matrix."""
    if alpha is None:
        lines.append("  Not estimated")
        return
    
    alpha = np.atleast_2d(alpha)
    N, r = alpha.shape
    
    # Header  
    header = "         " + "  ".join([f"α{k+1:>8}" for k in range(r)])
    lines.append(header)
    
    # Rows
    for i in range(N):
        var_name = var_names[i] if i < len(var_names) else f"y{i+1}"
        row_vals = "  ".join([f"{alpha[i, k]:>10.{precision}f}" for k in range(r)])
        lines.append(f"  {var_name:<6}{row_vals}")


def create_coefficient_table(
    results,
    regime: int = 0,
    variable_names: Optional[List[str]] = None,
    include_se: bool = True
) -> "pd.DataFrame":
    """
    Create a DataFrame of coefficient estimates for a specific regime.
    
    Parameters
    ----------
    results : VECMBreakResults
        Estimation results
    regime : int
        Regime index (0-indexed)
    variable_names : list, optional
        Variable names
    include_se : bool
        Include standard errors
    
    Returns
    -------
    df : pd.DataFrame
        Coefficient table
    """
    if not HAS_PANDAS:
        raise ImportError("pandas required. Install with: pip install pandas")
    
    if variable_names is None:
        variable_names = [f"y{i+1}" for i in range(results.N)]
    
    beta = results.beta[regime] if isinstance(results.beta, list) else results.beta
    if results.case == 1:
        alpha = results.alpha
    else:
        alpha = results.alpha[regime] if isinstance(results.alpha, list) else results.alpha
    
    data = {'Variable': variable_names}
    
    # Add beta columns
    beta = np.atleast_2d(beta)
    for k in range(beta.shape[1]):
        data[f'β{k+1}'] = beta[:, k]
    
    # Add alpha columns
    alpha = np.atleast_2d(alpha)
    for k in range(alpha.shape[1]):
        data[f'α{k+1}'] = alpha[:, k]
    
    return pd.DataFrame(data)


def results_to_latex(
    results,
    caption: str = "VECM Estimation Results",
    label: str = "tab:vecm_results",
    variable_names: Optional[List[str]] = None
) -> str:
    """
    Export estimation results to LaTeX table format.
    
    Parameters
    ----------
    results : VECMBreakResults
        Estimation results
    caption : str
        LaTeX table caption
    label : str
        LaTeX table label
    variable_names : list, optional
        Variable names
    
    Returns
    -------
    latex_str : str
        LaTeX table code
    """
    if not HAS_PANDAS:
        raise ImportError("pandas required for LaTeX export")
    
    df = create_coefficient_table(results, regime=0, variable_names=variable_names)
    
    latex = df.to_latex(
        index=False,
        caption=caption,
        label=label,
        float_format="%.4f"
    )
    
    return latex


# =============================================================================
# Plotting Functions (Figures 1-2 style)
# =============================================================================

def plot_time_series(
    Y: np.ndarray,
    breaks: Optional[List[int]] = None,
    variable_names: Optional[List[str]] = None,
    date_index: Optional[List] = None,
    title: str = "Time Series with Structural Breaks",
    figsize: Tuple[int, int] = (12, 6),
    show_breaks: bool = True,
    save_path: Optional[str] = None
) -> "plt.Figure":
    """
    Plot time series data with structural break markers.
    
    Creates a plot matching Figure 1 style in the paper.
    
    Parameters
    ----------
    Y : ndarray of shape (T, N)
        Data in levels
    breaks : list of int, optional
        Break locations to mark
    variable_names : list of str, optional
        Names for each variable
    date_index : list, optional
        Date index for x-axis
    title : str
        Plot title
    figsize : tuple
        Figure size
    show_breaks : bool
        Whether to show vertical lines at breaks
    save_path : str, optional
        Path to save figure
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object
    
    Examples
    --------
    >>> from vecmbreak import VECMBreak
    >>> model = VECMBreak(case=2, rank=1)
    >>> results = model.fit(Y)
    >>> fig = plot_time_series(Y, breaks=results.breaks,
    ...                        variable_names=['r10y', 'r5y', 'r1y'])
    >>> plt.show()
    """
    if not HAS_MATPLOTLIB:
        raise ImportError("matplotlib is required for plotting. "
                         "Install with: pip install matplotlib")
    
    Y = np.atleast_2d(Y)
    T, N = Y.shape
    
    if variable_names is None:
        variable_names = [f"y{i+1}" for i in range(N)]
    
    # Create x-axis
    if date_index is not None:
        x = date_index[:T]
    else:
        x = np.arange(T)
    
    # Line styles matching paper
    line_styles = ['-', '--', '-.', ':']
    
    fig, ax = plt.subplots(figsize=figsize)
    
    for i in range(N):
        ax.plot(x, Y[:, i], 
                linestyle=line_styles[i % len(line_styles)],
                label=variable_names[i],
                linewidth=1.5)
    
    # Add break markers
    if show_breaks and breaks:
        for b in breaks:
            if date_index is not None:
                b_x = date_index[b] if b < len(date_index) else b
            else:
                b_x = b
            ax.axvline(x=b_x, color='red', linestyle='--', 
                      alpha=0.7, linewidth=1)
    
    ax.set_xlabel('Time')
    ax.set_ylabel('Value')
    ax.set_title(title)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_irf_grid(
    irf: Optional[np.ndarray] = None,
    variable_names: Optional[List[str]] = None,
    regime_irfs: Optional[Dict[str, np.ndarray]] = None,
    title: str = "Impulse Response Functions",
    figsize: Optional[Tuple[int, int]] = None,
    save_path: Optional[str] = None,
    results: Optional["VECMBreakResults"] = None,
    horizons: int = 30,
    Gamma: Optional[List[np.ndarray]] = None
) -> "plt.Figure":
    """
    Plot IRFs in a grid format matching Figure 2 in the paper.
    
    Creates an N×N grid of IRF plots showing the response of each
    variable to shocks in each variable.
    
    Parameters
    ----------
    irf : ndarray of shape (H, N, N), optional
        IRF matrix where irf[h, i, j] is response of variable i
        to shock in variable j at horizon h. If None, computed from results.
    variable_names : list of str, optional
        Variable names
    regime_irfs : dict, optional
        Dictionary mapping regime names to IRF arrays for comparison.
        E.g., {'Full sample': irf1, 'Regime 1': irf2, 'Regime 3': irf3}
    title : str
        Overall figure title
    figsize : tuple, optional
        Figure size. If None, computed from N
    save_path : str, optional
        Path to save figure
    results : VECMBreakResults, optional
        Results object to compute IRFs from. If provided, irf is ignored
        and IRFs are computed for each regime.
    horizons : int, default=30
        Number of IRF horizons (used when computing from results)
    Gamma : list of ndarray, optional
        Short-run dynamics matrices. IMPORTANT: Include this for curved
        IRF patterns like in Figure 2. Without Gamma, IRFs are monotonic.
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object
    
    Examples
    --------
    >>> # Method 1: From VECMBreakResults (recommended)
    >>> model = VECMBreak(case=2, rank=1)
    >>> model.fit(Y)
    >>> fig = plot_irf_grid(results=model.results_, 
    ...                     variable_names=['y1', 'y2'],
    ...                     Gamma=[np.array([[-0.1, 0], [0, -0.1]])])
    
    >>> # Method 2: From pre-computed IRF array
    >>> from vecmbreak import compute_irf
    >>> irf_result = compute_irf(Pi, Sigma, Gamma=Gamma, horizons=30)
    >>> fig = plot_irf_grid(irf_result['irf'], variable_names=['y1', 'y2'])
    
    Notes
    -----
    To get curved IRF patterns like Figure 2 in the paper, you MUST include
    short-run dynamics (Gamma). Without Gamma, IRFs show monotonic adjustment.
    """
    if not HAS_MATPLOTLIB:
        raise ImportError("matplotlib required for plotting")
    
    # Import here to avoid circular imports
    from .irf import compute_regime_irf, compute_irf as _compute_irf
    
    # Compute IRFs from results if provided
    if results is not None:
        # Get alpha and beta lists
        if isinstance(results.alpha, list):
            alpha_list = results.alpha
        else:
            alpha_list = [results.alpha] * results.n_regimes
        
        if isinstance(results.beta, list):
            beta_list = results.beta
        else:
            beta_list = [results.beta] * results.n_regimes
        
        # Estimate error covariance from residuals if available
        if hasattr(results, 'residuals') and results.residuals is not None:
            Sigma = np.cov(results.residuals.T)
        else:
            Sigma = np.eye(results.N)
        
        Sigma_list = [Sigma] * results.n_regimes
        
        # Compute regime-specific IRFs
        irf_result = compute_regime_irf(
            alpha_list=alpha_list,
            beta_list=beta_list,
            Sigma_list=Sigma_list,
            Gamma=Gamma,
            horizons=horizons
        )
        
        # Build regime_irfs dict for plotting
        regime_irfs = {}
        for j in range(irf_result['n_regimes']):
            regime_irfs[f'Regime {j+1}'] = irf_result['irf_regimes'][j]
        
        # Use first regime as main IRF
        irf = irf_result['irf_regimes'][0]
        N = results.N
        
    elif irf is not None:
        H, N, _ = irf.shape
    else:
        raise ValueError("Either 'irf' array or 'results' must be provided")
    
    H = irf.shape[0]
    
    if variable_names is None:
        variable_names = [f"y{i+1}" for i in range(N)]
    
    if figsize is None:
        figsize = (4 * N, 3.5 * N)
    
    fig, axes = plt.subplots(N, N, figsize=figsize)
    if N == 1:
        axes = np.array([[axes]])
    axes = np.atleast_2d(axes)
    
    # Line styles for different regimes (matching paper's Figure 2)
    colors = ['black', 'blue', 'red', 'green', 'purple']
    styles = ['-', '--', '-.', ':']
    
    horizon_arr = np.arange(H)
    
    for i in range(N):
        for j in range(N):
            ax = axes[i, j]
            
            # Plot regime-specific IRFs
            if regime_irfs:
                for k, (regime_name, regime_irf) in enumerate(regime_irfs.items()):
                    color = colors[k % len(colors)]
                    style = styles[k % len(styles)]
                    ax.plot(horizon_arr, regime_irf[:, i, j], 
                           color=color, linestyle=style, 
                           linewidth=1.5 if k == 0 else 1.2,
                           label=regime_name)
            else:
                # Plot single IRF
                ax.plot(horizon_arr, irf[:, i, j], 'k-', linewidth=1.5)
            
            # Formatting
            ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.5)
            ax.set_xlabel('t')
            
            # Title showing shock → response
            ax.set_title(f"{variable_names[j]} → {variable_names[i]}", 
                        fontsize=10)
            
            # Add legend only to first subplot
            if i == 0 and j == 0 and regime_irfs:
                ax.legend(fontsize=8, loc='best')
    
    fig.suptitle(title, fontsize=12, y=1.02)
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def compute_irfs_from_results(
    results,
    horizons: int = 30,
    Gamma: Optional[List[np.ndarray]] = None
) -> Dict:
    """
    Compute IRFs from VECMBreakResults object.
    
    This is a convenience function that extracts the necessary parameters
    from estimation results and computes regime-specific IRFs.
    
    Parameters
    ----------
    results : VECMBreakResults
        Estimation results from VECMBreak.fit()
    horizons : int, default=30
        Number of IRF horizons
    Gamma : list of ndarray, optional
        Short-run dynamics matrices [Γ₁, Γ₂, ...]. IMPORTANT: Include
        this for curved IRF patterns. Without Gamma, IRFs are monotonic
        (straight lines).
    
    Returns
    -------
    irf_dict : dict
        Dictionary containing:
        - 'irf_regimes': List of IRF arrays for each regime
        - 'n_regimes': Number of regimes
        - 'horizons': Array of horizon indices
        - 'N': Number of variables
    
    Examples
    --------
    >>> model = VECMBreak(case=2, rank=1)
    >>> model.fit(Y)
    >>> 
    >>> # Without Gamma - monotonic IRFs
    >>> irfs_mono = compute_irfs_from_results(model.results_)
    >>> 
    >>> # With Gamma - curved IRFs (like Figure 2)
    >>> Gamma = [np.array([[-0.1, 0.05], [0.05, -0.1]])]
    >>> irfs_curved = compute_irfs_from_results(model.results_, Gamma=Gamma)
    
    Notes
    -----
    The short-run dynamics (Gamma) create the curved patterns seen in
    Figure 2 of the paper. The VECM model is:
    
        ΔY_t = ΠY_{t-1} + Γ₁ΔY_{t-1} + ... + Γ_{K-1}ΔY_{t-K+1} + u_t
    
    Without Gamma, the model reduces to a simple VAR(1) in levels,
    which produces monotonic adjustment paths.
    """
    from .irf import compute_regime_irf
    
    # Get alpha and beta lists
    if isinstance(results.alpha, list):
        alpha_list = results.alpha
    else:
        alpha_list = [results.alpha] * results.n_regimes
    
    if isinstance(results.beta, list):
        beta_list = results.beta
    else:
        beta_list = [results.beta] * results.n_regimes
    
    # Estimate error covariance
    if hasattr(results, 'residuals') and results.residuals is not None:
        Sigma = np.cov(results.residuals.T)
    else:
        Sigma = np.eye(results.N)
    
    Sigma_list = [Sigma] * results.n_regimes
    
    # Compute regime-specific IRFs
    return compute_regime_irf(
        alpha_list=alpha_list,
        beta_list=beta_list,
        Sigma_list=Sigma_list,
        Gamma=Gamma,
        horizons=horizons
    )


def plot_regime_comparison(
    results,
    variable_names: Optional[List[str]] = None,
    param_type: str = 'beta',
    figsize: Tuple[int, int] = (10, 6),
    save_path: Optional[str] = None
) -> "plt.Figure":
    """
    Plot coefficient estimates across regimes for comparison.
    
    Parameters
    ----------
    results : VECMBreakResults
        Estimation results
    variable_names : list, optional
        Variable names
    param_type : str
        'beta' or 'alpha'
    figsize : tuple
        Figure size
    save_path : str, optional
        Path to save figure
    
    Returns
    -------
    fig : matplotlib.figure.Figure
    """
    if not HAS_MATPLOTLIB:
        raise ImportError("matplotlib required for plotting")
    
    n_regimes = results.n_breaks + 1
    
    if variable_names is None:
        variable_names = [f"y{i+1}" for i in range(results.N)]
    
    fig, ax = plt.subplots(figsize=figsize)
    
    x = np.arange(n_regimes)
    width = 0.8 / results.N
    
    if param_type == 'beta':
        params = results.beta
        ylabel = 'Cointegrating Coefficient (β)'
    else:
        params = results.alpha
        ylabel = 'Adjustment Coefficient (α)'
    
    for i in range(results.N):
        values = []
        for j in range(n_regimes):
            if isinstance(params, list) and len(params) > j:
                p = np.atleast_2d(params[j])
                values.append(p[i, 0] if p.shape[1] > 0 else 0)
            elif isinstance(params, np.ndarray):
                values.append(params[i, 0] if params.ndim > 1 else params[i])
            else:
                values.append(0)
        
        ax.bar(x + i * width, values, width, 
               label=variable_names[i], alpha=0.8)
    
    ax.set_xlabel('Regime')
    ax.set_ylabel(ylabel)
    ax.set_title(f'{ylabel} Across Regimes')
    ax.set_xticks(x + width * (results.N - 1) / 2)
    ax.set_xticklabels([f'Regime {j+1}' for j in range(n_regimes)])
    ax.legend()
    ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.5)
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


# =============================================================================
# Summary Report Generation
# =============================================================================

def generate_full_report(
    results,
    Y: np.ndarray,
    variable_names: Optional[List[str]] = None,
    date_index: Optional[List] = None,
    title: str = "VECM Structural Break Analysis Report",
    include_plots: bool = True,
    save_dir: Optional[str] = None
) -> str:
    """
    Generate a comprehensive report of estimation results.
    
    Produces a full report including:
    - Model specification summary
    - Break detection results
    - Regime-specific coefficient tables
    - Time series plot with breaks
    - IRF analysis (if computed)
    
    Parameters
    ----------
    results : VECMBreakResults
        Estimation results
    Y : ndarray
        Original data
    variable_names : list, optional
        Variable names
    date_index : list, optional
        Date index
    title : str
        Report title
    include_plots : bool
        Whether to generate plots
    save_dir : str, optional
        Directory to save report files
    
    Returns
    -------
    report : str
        Full report text
    
    Examples
    --------
    >>> model = VECMBreak(case=2, rank=2)
    >>> results = model.fit(Y)
    >>> report = generate_full_report(results, Y,
    ...                               variable_names=['r10y', 'r5y', 'r1y'],
    ...                               save_dir='./results/')
    >>> print(report)
    """
    lines = []
    
    # Header
    lines.append("=" * 80)
    lines.append(f"{title}")
    lines.append("=" * 80)
    lines.append("")
    
    # Model specification
    lines.append("1. MODEL SPECIFICATION")
    lines.append("-" * 40)
    lines.append(f"   Sample size (T):          {results.T}")
    lines.append(f"   Number of variables (N):  {results.N}")
    lines.append(f"   Cointegration rank (r):   {results.r}")
    lines.append(f"   Estimation case:          {results.case}")
    lines.append(f"   Deterministic terms:      {results.deterministic}")
    lines.append("")
    
    # Break detection results
    lines.append("2. STRUCTURAL BREAK DETECTION")
    lines.append("-" * 40)
    lines.append(f"   Number of breaks detected: {results.n_breaks}")
    lines.append(f"   Number of regimes:         {results.n_regimes}")
    
    if results.n_breaks > 0:
        lines.append(f"   Break locations:           {results.breaks}")
        lines.append(f"   Break fractions:           {[f'{f:.3f}' for f in results.break_fractions]}")
    lines.append("")
    
    # Model fit
    lines.append("3. MODEL FIT")
    lines.append("-" * 40)
    lines.append(f"   Information criterion:     {results.ic:.4f}")
    lines.append(f"   Sum of squared residuals:  {results.ssr:.4f}")
    lines.append("")
    
    # Coefficient tables
    lines.append("4. COEFFICIENT ESTIMATES")
    lines.append("-" * 40)
    lines.append(format_estimation_results(
        results, 
        variable_names=variable_names,
        date_index=date_index,
        title=""
    ))
    
    # Save plots if requested
    if include_plots and HAS_MATPLOTLIB and save_dir:
        import os
        os.makedirs(save_dir, exist_ok=True)
        
        # Time series plot
        fig = plot_time_series(
            Y, 
            breaks=results.breaks,
            variable_names=variable_names,
            date_index=date_index,
            save_path=os.path.join(save_dir, 'time_series.png')
        )
        plt.close(fig)
        
        lines.append("")
        lines.append(f"   Time series plot saved to: {save_dir}/time_series.png")
    
    lines.append("")
    lines.append("=" * 80)
    lines.append("End of Report")
    lines.append("=" * 80)
    
    report = "\n".join(lines)
    
    # Save report text
    if save_dir:
        import os
        os.makedirs(save_dir, exist_ok=True)
        with open(os.path.join(save_dir, 'report.txt'), 'w') as f:
            f.write(report)
    
    return report


# =============================================================================
# Coverage Rate Table (Table 3 style)
# =============================================================================

def format_coverage_table(
    coverage_results: Dict,
    case: int = 1,
    title: str = "Post-detection Coverage Rates"
) -> str:
    """
    Format coverage rate results as Table 3 in the paper.
    
    Parameters
    ----------
    coverage_results : dict
        Results containing coverage rates for β and α
    case : int
        Case 1 or 2
    title : str
        Table title
    
    Returns
    -------
    table_str : str
        Formatted table
    """
    lines = []
    lines.append("=" * 60)
    lines.append(f"{title}")
    lines.append("=" * 60)
    lines.append("")
    lines.append("Note: Coverage rates for 95% confidence intervals")
    lines.append("      (Target: 95.0%)")
    lines.append("-" * 60)
    
    if case == 1:
        lines.append("Case 1: Constant α, regime-specific β")
    else:
        lines.append("Case 2: Regime-specific α and β")
    
    lines.append("")
    
    # Beta coverage
    beta_cov = coverage_results.get('beta_coverage', {})
    if beta_cov:
        lines.append("Cointegrating Coefficients (β):")
        for key, val in beta_cov.items():
            lines.append(f"  {key}: {val*100:.1f}%")
    
    lines.append("")
    
    # Alpha coverage
    alpha_cov = coverage_results.get('alpha_coverage', {})
    if alpha_cov:
        lines.append("Adjustment Coefficients (α):")
        for key, val in alpha_cov.items():
            lines.append(f"  {key}: {val*100:.1f}%")
    
    lines.append("=" * 60)
    
    return "\n".join(lines)
