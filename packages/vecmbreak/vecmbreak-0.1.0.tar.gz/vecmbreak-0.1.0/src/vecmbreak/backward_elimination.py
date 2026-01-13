"""
Backward Elimination Algorithm for Break Selection
===================================================

This module implements the second-step backward elimination algorithm (BEA)
for refining structural break estimates in VECMs.

The BEA eliminates spurious breaks identified by the Group LASSO in the first
step, using an information criterion to determine the optimal set of breaks.

Following Chan et al. (2014) and Schweikert (2025), the information criterion is:
    IC(m, t) = S_T(t_1, ..., t_m) + m * C * T^(3/4) * log(T)

References
----------
Chan, N.H., Yau, C.Y., & Zhang, R.M. (2014). Group LASSO for Structural Break 
    Time Series. Journal of the American Statistical Association, 109, 590-599.
Schweikert, K. (2025). Detecting Multiple Structural Breaks in Systems of 
    Linear Regression Equations. Oxford Bulletin of Economics and Statistics.
"""

import numpy as np
from numpy.linalg import lstsq, norm, inv
from typing import Tuple, List, Optional, Dict, Any
import warnings
from itertools import combinations


class BackwardElimination:
    """
    Backward Elimination Algorithm for structural break refinement.
    
    After the Group LASSO identifies break candidates, this algorithm
    eliminates irrelevant breakpoints to provide consistent estimates
    of the number and timing of structural breaks.
    
    The algorithm iteratively removes breakpoints that lead to the
    largest improvement in the information criterion until no further
    improvement is possible.
    
    Parameters
    ----------
    criterion : str, default='bic_modified'
        Information criterion to use:
        - 'bic_modified': Modified BIC from Schweikert (2025), Equation (11)
        - 'bic': Standard BIC
        - 'aic': Akaike Information Criterion
    C : float, default=0.1
        Penalty constant for the information criterion.
        Following Chan et al. (2014), smaller values lead to more breaks.
        Default reduced to 0.1 for better finite-sample performance.
    min_segment_length : int, default=10
        Minimum number of observations per regime.
    verbose : bool, default=False
        If True, print progress information.
    
    Attributes
    ----------
    breaks_ : list of int
        Final estimated break locations.
    n_breaks_ : int
        Number of breaks after elimination.
    ic_path_ : list of float
        Information criterion values during elimination.
    ssr_ : float
        Sum of squared residuals at the final model.
    
    References
    ----------
    Chan, N.H., Yau, C.Y., & Zhang, R.M. (2014). Group LASSO for Structural 
        Break Time Series. JASA, 109, 590-599.
    Schweikert, K. (2025). Detecting Multiple Structural Breaks.
        Oxford Bulletin of Economics and Statistics.
    
    Examples
    --------
    >>> bea = BackwardElimination(criterion='bic_modified')
    >>> bea.fit(R0, R1, break_candidates=[50, 100, 150, 200])
    >>> print(f"Final breaks: {bea.breaks_}")
    """
    
    def __init__(
        self,
        criterion: str = "bic_modified",
        C: float = 0.1,
        min_segment_length: int = 10,
        verbose: bool = False
    ):
        self.criterion = criterion
        self.C = C
        self.min_segment_length = min_segment_length
        self.verbose = verbose
        
        # Fitted attributes
        self.breaks_ = None
        self.n_breaks_ = None
        self.ic_path_ = None
        self.ssr_ = None
        self.coefficients_ = None
    
    def fit(
        self,
        R0: np.ndarray,
        R1: np.ndarray,
        break_candidates: List[int],
        deterministic: Optional[np.ndarray] = None
    ) -> List[int]:
        """
        Apply backward elimination to refine break estimates.
        
        Parameters
        ----------
        R0 : ndarray of shape (T, N)
            Residuals from regressing ΔY on control variables.
        R1 : ndarray of shape (T, N)
            Residuals from regressing Y_{t-1} on control variables.
        break_candidates : list of int
            Break candidate indices from Group LASSO step.
        deterministic : ndarray of shape (T, d), optional
            Deterministic terms to include.
        
        Returns
        -------
        breaks : list of int
            Final refined break locations.
        """
        T, N = R0.shape
        
        # Validate break candidates
        break_candidates = sorted([b for b in break_candidates 
                                   if self.min_segment_length <= b <= T - self.min_segment_length])
        
        if len(break_candidates) == 0:
            self.breaks_ = []
            self.n_breaks_ = 0
            self.ic_path_ = []
            self.ssr_ = self._compute_ssr(R0, R1, [], deterministic)
            return self.breaks_
        
        # Cluster nearby candidates to reduce computation
        # Keep only one representative per cluster
        break_candidates = self._cluster_candidates(break_candidates, R0, R1, deterministic)
        
        # Initialize with all candidates
        current_breaks = break_candidates.copy()
        self.ic_path_ = []
        
        # Compute initial IC
        current_ssr = self._compute_ssr(R0, R1, current_breaks, deterministic)
        current_ic = self._compute_ic(current_ssr, T, len(current_breaks), N)
        self.ic_path_.append(current_ic)
        
        if self.verbose:
            print(f"Initial: {len(current_breaks)} breaks, IC = {current_ic:.4f}")
        
        # Backward elimination loop
        improved = True
        while improved and len(current_breaks) > 0:
            improved = False
            best_ic = current_ic
            best_break_to_remove = None
            
            # Try removing each break
            for break_idx in current_breaks:
                test_breaks = [b for b in current_breaks if b != break_idx]
                
                # Check minimum segment length constraint
                if not self._check_segment_lengths(test_breaks, T):
                    continue
                
                test_ssr = self._compute_ssr(R0, R1, test_breaks, deterministic)
                test_ic = self._compute_ic(test_ssr, T, len(test_breaks), N)
                
                if test_ic < best_ic:
                    best_ic = test_ic
                    best_break_to_remove = break_idx
            
            # Remove the break that most improves IC
            if best_break_to_remove is not None:
                current_breaks.remove(best_break_to_remove)
                current_ic = best_ic
                current_ssr = self._compute_ssr(R0, R1, current_breaks, deterministic)
                self.ic_path_.append(current_ic)
                improved = True
                
                if self.verbose:
                    print(f"Removed break at {best_break_to_remove}: "
                          f"{len(current_breaks)} breaks, IC = {current_ic:.4f}")
        
        # Also try adding no breaks at all
        no_break_ssr = self._compute_ssr(R0, R1, [], deterministic)
        no_break_ic = self._compute_ic(no_break_ssr, T, 0, N)
        
        if no_break_ic < current_ic:
            current_breaks = []
            current_ic = no_break_ic
            current_ssr = no_break_ssr
            if self.verbose:
                print(f"No breaks model selected, IC = {current_ic:.4f}")
        
        self.breaks_ = current_breaks
        self.n_breaks_ = len(current_breaks)
        self.ssr_ = current_ssr
        
        # Compute final coefficients
        self.coefficients_ = self._estimate_coefficients(
            R0, R1, current_breaks, deterministic
        )
        
        return self.breaks_
    
    def _check_segment_lengths(
        self,
        breaks: List[int],
        T: int
    ) -> bool:
        """
        Check if all segments satisfy minimum length constraint.
        
        Parameters
        ----------
        breaks : list of int
            Break locations.
        T : int
            Sample size.
        
        Returns
        -------
        valid : bool
            True if all segments are long enough.
        """
        if len(breaks) == 0:
            return T >= self.min_segment_length
        
        # Add boundaries
        all_points = [0] + sorted(breaks) + [T]
        
        for i in range(len(all_points) - 1):
            if all_points[i + 1] - all_points[i] < self.min_segment_length:
                return False
        
        return True
    
    def _cluster_candidates(
        self,
        candidates: List[int],
        R0: np.ndarray,
        R1: np.ndarray,
        deterministic: Optional[np.ndarray] = None,
        cluster_width: int = None
    ) -> List[int]:
        """
        Cluster nearby break candidates and keep the best one from each cluster.
        
        This reduces computation time by merging candidates that are close together.
        From each cluster, we keep the candidate that produces the lowest SSR
        when used as a single break point.
        
        Parameters
        ----------
        candidates : list of int
            Break candidate indices.
        R0, R1 : ndarrays
            Data matrices.
        deterministic : ndarray, optional
            Deterministic terms.
        cluster_width : int, optional
            Maximum distance between candidates in same cluster.
            Default is min_segment_length // 2.
        
        Returns
        -------
        clustered : list of int
            Representative candidates from each cluster.
        """
        if len(candidates) <= 1:
            return candidates
        
        if cluster_width is None:
            cluster_width = max(self.min_segment_length // 2, 5)
        
        candidates = sorted(candidates)
        
        # Group into clusters
        clusters = []
        current_cluster = [candidates[0]]
        
        for c in candidates[1:]:
            if c - current_cluster[-1] <= cluster_width:
                current_cluster.append(c)
            else:
                clusters.append(current_cluster)
                current_cluster = [c]
        clusters.append(current_cluster)
        
        # From each cluster, pick the candidate with lowest SSR
        representatives = []
        for cluster in clusters:
            if len(cluster) == 1:
                representatives.append(cluster[0])
            else:
                best_ssr = float('inf')
                best_candidate = cluster[0]
                for c in cluster:
                    ssr = self._compute_ssr(R0, R1, [c], deterministic)
                    if ssr < best_ssr:
                        best_ssr = ssr
                        best_candidate = c
                representatives.append(best_candidate)
        
        if self.verbose and len(representatives) < len(candidates):
            print(f"Clustered {len(candidates)} candidates into {len(representatives)}")
        
        return representatives
    
    def _compute_ssr(
        self,
        R0: np.ndarray,
        R1: np.ndarray,
        breaks: List[int],
        deterministic: Optional[np.ndarray] = None
    ) -> float:
        """
        Compute sum of squared residuals for a given break configuration.
        
        Fits OLS for each regime and sums the squared residuals.
        
        Parameters
        ----------
        R0 : ndarray of shape (T, N)
            Dependent variable residuals.
        R1 : ndarray of shape (T, N)
            Independent variable residuals.
        breaks : list of int
            Break locations.
        deterministic : ndarray, optional
            Deterministic terms.
        
        Returns
        -------
        ssr : float
            Sum of squared residuals.
        """
        T, N = R0.shape
        
        # Define regimes
        if len(breaks) == 0:
            regimes = [(0, T)]
        else:
            all_points = [0] + sorted(breaks) + [T]
            regimes = [(all_points[i], all_points[i + 1]) 
                       for i in range(len(all_points) - 1)]
        
        total_ssr = 0.0
        
        for start, end in regimes:
            if end <= start:
                continue
            
            R0_regime = R0[start:end]
            R1_regime = R1[start:end]
            
            # Add deterministic terms if provided
            if deterministic is not None:
                X = np.hstack([R1_regime, deterministic[start:end]])
            else:
                X = R1_regime
            
            # Fit regime-specific OLS
            for n in range(N):
                y = R0_regime[:, n]
                coef, residuals, rank, s = lstsq(X, y, rcond=None)
                
                if len(residuals) > 0:
                    total_ssr += residuals[0]
                else:
                    # Compute residuals manually
                    fitted = X @ coef
                    total_ssr += np.sum((y - fitted) ** 2)
        
        return total_ssr
    
    def _compute_ic(
        self,
        ssr: float,
        T: int,
        m: int,
        N: int
    ) -> float:
        """
        Compute information criterion value.
        
        Following Equation (11) from the paper:
            IC(m, t) = S_T(t_1, ..., t_m) + m * C * T^(3/4) * log(T)
        
        Parameters
        ----------
        ssr : float
            Sum of squared residuals.
        T : int
            Sample size.
        m : int
            Number of breaks.
        N : int
            Number of equations.
        
        Returns
        -------
        ic : float
            Information criterion value.
        """
        if self.criterion == "bic_modified":
            # Equation (11): Modified BIC
            # The penalty penalizes the total number of nonzero coefficients
            n_params_per_break = N * N  # Dimension of Π
            penalty = m * self.C * (T ** 0.75) * np.log(T)
            ic = ssr + penalty
            
        elif self.criterion == "bic":
            # Standard BIC
            # BIC = T * log(SSR/T) + k * log(T)
            n_params = (m + 1) * N * N
            ic = T * np.log(ssr / T + 1e-10) + n_params * np.log(T)
            
        elif self.criterion == "aic":
            # AIC = T * log(SSR/T) + 2k
            n_params = (m + 1) * N * N
            ic = T * np.log(ssr / T + 1e-10) + 2 * n_params
            
        else:
            raise ValueError(f"Unknown criterion: {self.criterion}")
        
        return ic
    
    def _estimate_coefficients(
        self,
        R0: np.ndarray,
        R1: np.ndarray,
        breaks: List[int],
        deterministic: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Estimate regime-specific coefficients.
        
        Parameters
        ----------
        R0, R1, breaks, deterministic : as above
        
        Returns
        -------
        coefficients : dict
            Dictionary with regime-specific coefficient estimates.
        """
        T, N = R0.shape
        
        # Define regimes
        if len(breaks) == 0:
            regimes = [(0, T)]
        else:
            all_points = [0] + sorted(breaks) + [T]
            regimes = [(all_points[i], all_points[i + 1]) 
                       for i in range(len(all_points) - 1)]
        
        coefficients = {
            "Pi": [],
            "residuals": [],
            "regime_bounds": regimes
        }
        
        for start, end in regimes:
            if end <= start:
                continue
            
            R0_regime = R0[start:end]
            R1_regime = R1[start:end]
            
            # Add deterministic terms if provided
            if deterministic is not None:
                X = np.hstack([R1_regime, deterministic[start:end]])
            else:
                X = R1_regime
            
            # Fit OLS for each equation
            Pi_regime = np.zeros((N, X.shape[1]))
            residuals_regime = np.zeros((end - start, N))
            
            for n in range(N):
                y = R0_regime[:, n]
                coef, _, _, _ = lstsq(X, y, rcond=None)
                Pi_regime[n, :] = coef
                residuals_regime[:, n] = y - X @ coef
            
            # Extract Pi (first N columns) if deterministic terms present
            if deterministic is not None:
                coefficients["Pi"].append(Pi_regime[:, :N])
            else:
                coefficients["Pi"].append(Pi_regime)
            coefficients["residuals"].append(residuals_regime)
        
        return coefficients


class DynamicProgrammingOptimizer:
    """
    Dynamic programming approach for optimal break selection.
    
    This provides an alternative to backward elimination by exhaustively
    searching over break configurations using dynamic programming.
    
    Computationally more expensive but guarantees global optimum.
    
    Parameters
    ----------
    max_breaks : int, default=10
        Maximum number of breaks to consider.
    criterion : str, default='bic_modified'
        Information criterion.
    min_segment_length : int, default=10
        Minimum observations per regime.
    
    Attributes
    ----------
    breaks_ : list of int
        Optimal break locations.
    optimal_n_breaks_ : int
        Optimal number of breaks.
    all_ic_values_ : dict
        IC values for all configurations tested.
    """
    
    def __init__(
        self,
        max_breaks: int = 10,
        criterion: str = "bic_modified",
        min_segment_length: int = 10
    ):
        self.max_breaks = max_breaks
        self.criterion = criterion
        self.min_segment_length = min_segment_length
        
        self.breaks_ = None
        self.optimal_n_breaks_ = None
        self.all_ic_values_ = None
    
    def fit(
        self,
        R0: np.ndarray,
        R1: np.ndarray,
        candidate_locations: Optional[List[int]] = None
    ) -> "DynamicProgrammingOptimizer":
        """
        Find optimal breaks using dynamic programming.
        
        Parameters
        ----------
        R0 : ndarray of shape (T, N)
            Dependent variable residuals.
        R1 : ndarray of shape (T, N)
            Independent variable residuals.
        candidate_locations : list of int, optional
            Candidate break locations. If None, all valid locations used.
        
        Returns
        -------
        self : DynamicProgrammingOptimizer
            Fitted optimizer.
        """
        T, N = R0.shape
        
        # Generate candidate locations if not provided
        if candidate_locations is None:
            candidate_locations = list(range(
                self.min_segment_length, 
                T - self.min_segment_length + 1
            ))
        
        # Filter candidates
        candidate_locations = [
            c for c in candidate_locations 
            if self.min_segment_length <= c <= T - self.min_segment_length
        ]
        
        self.all_ic_values_ = {}
        best_ic = np.inf
        best_breaks = []
        
        # Try 0 to max_breaks
        for n_breaks in range(self.max_breaks + 1):
            if n_breaks == 0:
                ssr = self._compute_ssr_segment(R0, R1, 0, T)
                ic = self._compute_ic(ssr, T, 0, N)
                self.all_ic_values_[tuple()] = ic
                
                if ic < best_ic:
                    best_ic = ic
                    best_breaks = []
            else:
                # Generate all valid combinations
                if n_breaks <= len(candidate_locations):
                    for breaks in combinations(candidate_locations, n_breaks):
                        breaks_list = sorted(breaks)
                        
                        # Check segment lengths
                        all_points = [0] + breaks_list + [T]
                        valid = True
                        for i in range(len(all_points) - 1):
                            if all_points[i + 1] - all_points[i] < self.min_segment_length:
                                valid = False
                                break
                        
                        if not valid:
                            continue
                        
                        # Compute IC for this configuration
                        ssr = self._compute_total_ssr(R0, R1, breaks_list)
                        ic = self._compute_ic(ssr, T, n_breaks, N)
                        self.all_ic_values_[tuple(breaks_list)] = ic
                        
                        if ic < best_ic:
                            best_ic = ic
                            best_breaks = breaks_list
        
        self.breaks_ = best_breaks
        self.optimal_n_breaks_ = len(best_breaks)
        
        return self
    
    def _compute_ssr_segment(
        self,
        R0: np.ndarray,
        R1: np.ndarray,
        start: int,
        end: int
    ) -> float:
        """Compute SSR for a single segment."""
        R0_seg = R0[start:end]
        R1_seg = R1[start:end]
        N = R0.shape[1]
        
        ssr = 0.0
        for n in range(N):
            coef, residuals, _, _ = lstsq(R1_seg, R0_seg[:, n], rcond=None)
            if len(residuals) > 0:
                ssr += residuals[0]
            else:
                fitted = R1_seg @ coef
                ssr += np.sum((R0_seg[:, n] - fitted) ** 2)
        
        return ssr
    
    def _compute_total_ssr(
        self,
        R0: np.ndarray,
        R1: np.ndarray,
        breaks: List[int]
    ) -> float:
        """Compute total SSR across all regimes."""
        T = R0.shape[0]
        all_points = [0] + sorted(breaks) + [T]
        
        total_ssr = 0.0
        for i in range(len(all_points) - 1):
            total_ssr += self._compute_ssr_segment(
                R0, R1, all_points[i], all_points[i + 1]
            )
        
        return total_ssr
    
    def _compute_ic(
        self,
        ssr: float,
        T: int,
        m: int,
        N: int
    ) -> float:
        """Compute information criterion."""
        if self.criterion == "bic_modified":
            penalty = m * (T ** 0.75) * np.log(T)
            return ssr + penalty
        elif self.criterion == "bic":
            n_params = (m + 1) * N * N
            return T * np.log(ssr / T + 1e-10) + n_params * np.log(T)
        else:
            raise ValueError(f"Unknown criterion: {self.criterion}")


def refine_breaks_with_local_search(
    R0: np.ndarray,
    R1: np.ndarray,
    initial_breaks: List[int],
    search_radius: int = 5
) -> List[int]:
    """
    Refine break locations using local search.
    
    After backward elimination, this function fine-tunes break locations
    by searching in a neighborhood around each estimated break.
    
    Parameters
    ----------
    R0 : ndarray of shape (T, N)
        Dependent variable residuals.
    R1 : ndarray of shape (T, N)
        Independent variable residuals.
    initial_breaks : list of int
        Initial break estimates.
    search_radius : int, default=5
        Number of periods to search around each break.
    
    Returns
    -------
    refined_breaks : list of int
        Refined break locations.
    """
    if len(initial_breaks) == 0:
        return []
    
    T, N = R0.shape
    refined_breaks = initial_breaks.copy()
    
    # Iteratively refine each break
    for idx, break_point in enumerate(initial_breaks):
        best_ssr = np.inf
        best_location = break_point
        
        # Search in neighborhood
        for offset in range(-search_radius, search_radius + 1):
            test_location = break_point + offset
            
            # Check bounds
            if test_location < 10 or test_location > T - 10:
                continue
            
            # Check overlap with other breaks
            other_breaks = refined_breaks[:idx] + refined_breaks[idx + 1:]
            if any(abs(test_location - b) < 10 for b in other_breaks):
                continue
            
            # Compute SSR with this location
            test_breaks = refined_breaks.copy()
            test_breaks[idx] = test_location
            
            bea = BackwardElimination(verbose=False)
            ssr = bea._compute_ssr(R0, R1, sorted(test_breaks), None)
            
            if ssr < best_ssr:
                best_ssr = ssr
                best_location = test_location
        
        refined_breaks[idx] = best_location
    
    return sorted(refined_breaks)
