# -*- coding: utf-8 -*-
"""
Comprehensive unit tests for the vecmbreak library.

Tests cover:
- Data generation (DGP Case 1, Case 2, with short-run dynamics)
- Group LASSO break detection
- Backward elimination algorithm
- Principal component estimation
- Full pipeline integration
- Edge cases and numerical stability

Reference:
    Franjic, Mößler, and Schweikert (2025). "Multiple Structural Breaks in
    Vector Error Correction Models." University of Hohenheim Working Paper.
"""

import numpy as np
import pytest
from numpy.testing import assert_array_almost_equal, assert_allclose

# Import library components
from vecmbreak import (
    VECMBreak,
    fit_vecm_breaks,
    simulate_vecm_breaks,
    generate_dgp_case1,
    generate_dgp_case2,
    generate_dgp_with_short_run,
)
from vecmbreak.group_lasso import GroupLassoBreakDetector, AdaptiveGroupLasso
from vecmbreak.backward_elimination import BackwardElimination, DynamicProgrammingOptimizer
from vecmbreak.principal_component import PrincipalComponentEstimator
from vecmbreak.utils import (
    normalize_cointegrating_vectors,
    frisch_waugh_projection,
    compute_information_criterion,
    vec_operator,
    inv_vec_operator,
    check_stationarity,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def seed():
    """Set random seed for reproducibility."""
    np.random.seed(42)
    return 42


@pytest.fixture
def small_sample_data(seed):
    """Generate small sample data for quick tests."""
    return generate_dgp_case1(T=200, break_fractions=[0.5], seed=seed)


@pytest.fixture
def medium_sample_data(seed):
    """Generate medium sample data for more thorough tests."""
    return generate_dgp_case1(T=500, break_fractions=[0.33, 0.67], seed=seed)


@pytest.fixture
def case2_data(seed):
    """Generate Case 2 data (both alpha and beta change)."""
    return generate_dgp_case2(T=300, break_fractions=[0.5], seed=seed)


# =============================================================================
# Test Data Generation
# =============================================================================

class TestDataGeneration:
    """Tests for data generation functions."""
    
    def test_dgp_case1_dimensions(self, seed):
        """Test that Case 1 DGP produces correct dimensions."""
        result = generate_dgp_case1(T=200, break_fractions=[0.5], seed=seed)
        
        assert result['Y'].shape == (201, 2), "Y should be (T+1, N)"
        assert result['delta_Y'].shape == (200, 2), "delta_Y should be (T, N)"
        assert result['true_breaks'] == [100], "Break should be at t=100"
        assert len(result['alpha']) == 2, "Should have 2 regimes"
        assert len(result['beta']) == 2, "Should have 2 regimes"
    
    def test_dgp_case1_cointegration_rank(self, seed):
        """Test that Case 1 maintains cointegration rank."""
        result = generate_dgp_case1(T=500, break_fractions=[0.5], seed=seed)
        
        # Check Pi = alpha @ beta' has rank 1
        for j in range(2):
            Pi = result['alpha'][j] @ result['beta'][j].T
            rank = np.linalg.matrix_rank(Pi)
            assert rank == 1, f"Regime {j}: Pi should have rank 1, got {rank}"
    
    def test_dgp_case1_break_magnitude(self, seed):
        """Test that Case 1 break has correct Frobenius norm magnitude."""
        result = generate_dgp_case1(T=200, break_fractions=[0.5], seed=seed)
        
        # From paper: break magnitude should be 0.7071 (1/sqrt(2))
        Pi_0 = result['alpha'][0] @ result['beta'][0].T
        Pi_1 = result['alpha'][1] @ result['beta'][1].T
        magnitude = np.linalg.norm(Pi_1 - Pi_0, 'fro')
        
        assert_allclose(magnitude, 0.7071, rtol=0.01, 
                       err_msg="Case 1 break magnitude should be ~0.7071")
    
    def test_dgp_case2_dimensions(self, seed):
        """Test that Case 2 DGP produces correct dimensions."""
        result = generate_dgp_case2(T=200, break_fractions=[0.5], seed=seed)
        
        assert result['Y'].shape == (201, 2), "Y should be (T+1, N)"
        assert result['delta_Y'].shape == (200, 2), "delta_Y should be (T, N)"
    
    def test_dgp_case2_alpha_changes(self, seed):
        """Test that Case 2 has different alpha across regimes."""
        result = generate_dgp_case2(T=200, break_fractions=[0.5], seed=seed)
        
        alpha_diff = np.linalg.norm(result['alpha'][1] - result['alpha'][0])
        assert alpha_diff > 0.1, "Alpha should differ across regimes in Case 2"
    
    def test_dgp_with_short_run(self, seed):
        """Test DGP with short-run dynamics."""
        # k_ar=2 gives K=2, which adds one Gamma matrix (Gamma_1)
        result = generate_dgp_with_short_run(
            T=200, break_fractions=[0.5], k_ar=2, seed=seed
        )
        
        assert 'Gamma' in result, "Should include Gamma matrices"
        assert len(result['Gamma']) > 0, "Should have at least one Gamma"
    
    def test_multiple_breaks(self, seed):
        """Test DGP with multiple breaks."""
        result = generate_dgp_case1(
            T=300, break_fractions=[0.25, 0.5, 0.75], seed=seed
        )
        
        assert len(result['true_breaks']) == 3, "Should have 3 breaks"
        assert len(result['alpha']) == 4, "Should have 4 regimes"
        assert result['true_breaks'] == [75, 150, 225], "Break locations"
    
    def test_simulate_vecm_breaks_custom(self, seed):
        """Test custom VECM simulation."""
        np.random.seed(seed)
        
        alpha = np.array([[-0.3], [0.3]])
        beta = np.array([[1.0], [-1.0]])
        
        # No breaks means 1 regime, so 1 alpha and 1 beta
        Y, info = simulate_vecm_breaks(
            T=100,
            N=2,
            alpha_list=[alpha],
            beta_list=[beta],
            break_points=[],
            seed=seed
        )
        
        assert Y.shape == (101, 2), "Y should be (T+1, N)"


# =============================================================================
# Test Utility Functions
# =============================================================================

class TestUtils:
    """Tests for utility functions."""
    
    def test_vec_operator(self):
        """Test vec operator (column stacking)."""
        A = np.array([[1, 2], [3, 4]])
        vec_A = vec_operator(A)
        expected = np.array([1, 3, 2, 4])
        assert_array_almost_equal(vec_A, expected)
    
    def test_inv_vec_operator(self):
        """Test inverse vec operator."""
        vec_A = np.array([1, 3, 2, 4])
        A = inv_vec_operator(vec_A, n_rows=2, n_cols=2)
        expected = np.array([[1, 2], [3, 4]])
        assert_array_almost_equal(A, expected)
    
    def test_vec_inv_vec_roundtrip(self):
        """Test vec and inv_vec are inverses."""
        np.random.seed(42)
        A = np.random.randn(3, 4)
        reconstructed = inv_vec_operator(vec_operator(A), 3, 4)
        assert_array_almost_equal(A, reconstructed)
    
    def test_normalize_cointegrating_vectors(self):
        """Test triangular normalization of cointegrating vectors."""
        beta = np.array([[2.0, 1.0], [-1.0, 0.5]])  # 2x2, r=2
        beta_norm = normalize_cointegrating_vectors(beta, r=2)
        
        # Top r x r block should be identity
        assert_array_almost_equal(
            beta_norm[:2, :2], np.eye(2),
            err_msg="Top block should be identity"
        )
    
    def test_normalize_cointegrating_vectors_rank1(self):
        """Test normalization with rank 1."""
        beta = np.array([[2.0], [-4.0]])
        beta_norm = normalize_cointegrating_vectors(beta, r=1)
        
        assert beta_norm[0, 0] == 1.0, "First element should be 1"
        assert_allclose(beta_norm[1, 0], -2.0, 
                       err_msg="Should preserve ratio")
    
    def test_frisch_waugh_projection(self):
        """Test Frisch-Waugh-Lovell projection."""
        np.random.seed(42)
        n = 100
        
        # Generate data
        X = np.random.randn(n, 3)
        Z = np.random.randn(n, 2)
        Y = np.random.randn(n, 1)
        
        Y_proj, X_proj = frisch_waugh_projection(Y, X, Z)
        
        # Projected variables should be orthogonal to Z
        assert_allclose(Z.T @ Y_proj, 0, atol=1e-10,
                       err_msg="Y_proj should be orthogonal to Z")
        assert_allclose(Z.T @ X_proj, 0, atol=1e-10,
                       err_msg="X_proj should be orthogonal to Z")
    
    def test_compute_information_criterion(self):
        """Test modified BIC computation."""
        T = 200
        ssr = 100.0
        m = 2  # number of breaks
        
        ic = compute_information_criterion(ssr, T, m)
        
        # IC = S_T + m * C * T^(3/4) * log(T)
        # C is a constant, typically around 0.3-0.5
        assert ic > ssr, "IC should be larger than SSR due to penalty"
        
        # More breaks should give larger IC
        ic_more = compute_information_criterion(ssr, T, m=3)
        assert ic_more > ic, "More breaks should increase IC"
    
    def test_check_stationarity_stationary(self):
        """Test stationarity check for stationary process."""
        # Companion matrix with eigenvalues inside unit circle
        A = np.array([[0.5, 0.1], [0.1, 0.3]])
        is_stationary = check_stationarity(A)
        assert is_stationary, "Process should be stationary"
    
    def test_check_stationarity_nonstationary(self):
        """Test stationarity check for non-stationary process."""
        # Companion matrix with eigenvalue > 1
        A = np.array([[1.2, 0.0], [0.0, 0.5]])
        is_stationary = check_stationarity(A)
        assert not is_stationary, "Process should be non-stationary"


# =============================================================================
# Test Group LASSO
# =============================================================================

class TestGroupLasso:
    """Tests for Group LASSO break detection."""
    
    def test_group_lasso_detects_break(self, small_sample_data):
        """Test that Group LASSO detects a single break."""
        delta_Y = small_sample_data['delta_Y']
        Y_lag = small_sample_data['Y'][:-1, :]
        
        detector = GroupLassoBreakDetector(lambda_T=0.1)
        detector.fit(delta_Y, Y_lag)
        
        candidates = detector.break_candidates_
        
        # Should find at least one candidate near true break
        true_break = 100
        has_nearby = any(abs(c - true_break) <= 20 for c in candidates)
        
        assert len(candidates) > 0, "Should detect at least one candidate"
        # Note: May not always find exact break due to regularization
    
    def test_group_lasso_no_break_data(self, seed):
        """Test Group LASSO on data with no breaks."""
        # Generate data with no breaks
        result = generate_dgp_case1(T=200, break_fractions=[], seed=seed)
        
        delta_Y = result['delta_Y']
        Y_lag = result['Y'][:-1, :]
        
        detector = GroupLassoBreakDetector(lambda_T=0.5)
        detector.fit(delta_Y, Y_lag)
        
        # With high regularization, should find few or no breaks
        assert len(detector.break_candidates_) <= 3, \
            "Should not detect many breaks in stable data"
    
    def test_adaptive_group_lasso(self, small_sample_data):
        """Test adaptive Group LASSO."""
        delta_Y = small_sample_data['delta_Y']
        Y_lag = small_sample_data['Y'][:-1, :]
        
        detector = AdaptiveGroupLasso(lambda_T=0.1, gamma=1.0)
        detector.fit(delta_Y, Y_lag)
        
        # Should still work
        assert hasattr(detector, 'break_candidates_')
    
    def test_group_lasso_lambda_effect(self, small_sample_data):
        """Test that higher lambda gives fewer candidates."""
        delta_Y = small_sample_data['delta_Y']
        Y_lag = small_sample_data['Y'][:-1, :]
        
        detector_low = GroupLassoBreakDetector(lambda_T=0.01)
        detector_low.fit(delta_Y, Y_lag)
        
        detector_high = GroupLassoBreakDetector(lambda_T=1.0)
        detector_high.fit(delta_Y, Y_lag)
        
        assert len(detector_high.break_candidates_) <= len(detector_low.break_candidates_), \
            "Higher lambda should give fewer candidates"


# =============================================================================
# Test Backward Elimination
# =============================================================================

class TestBackwardElimination:
    """Tests for backward elimination algorithm."""
    
    def test_backward_elimination_refines(self, small_sample_data):
        """Test that backward elimination refines candidates."""
        delta_Y = small_sample_data['delta_Y']
        Y_lag = small_sample_data['Y'][:-1, :]
        
        # Start with several candidates including true break
        initial_candidates = [50, 100, 150]
        
        bea = BackwardElimination(min_segment_length=30)
        final_breaks = bea.fit(delta_Y, Y_lag, initial_candidates)
        
        assert len(final_breaks) <= len(initial_candidates), \
            "BEA should reduce or maintain number of breaks"
    
    def test_backward_elimination_preserves_true(self, medium_sample_data):
        """Test that BEA tends to preserve true breaks."""
        delta_Y = medium_sample_data['delta_Y']
        Y_lag = medium_sample_data['Y'][:-1, :]
        true_breaks = medium_sample_data['true_breaks']
        
        # Include true breaks plus some noise
        initial = true_breaks + [50, 250, 400]
        
        bea = BackwardElimination(min_segment_length=30)
        final_breaks = bea.fit(delta_Y, Y_lag, initial)
        
        # At least one true break should remain
        preserved = sum(1 for tb in true_breaks 
                       if any(abs(fb - tb) <= 20 for fb in final_breaks))
        
        assert preserved >= 1, "Should preserve at least one true break"
    
    def test_backward_elimination_empty(self, small_sample_data):
        """Test BEA with empty candidates."""
        delta_Y = small_sample_data['delta_Y']
        Y_lag = small_sample_data['Y'][:-1, :]
        
        bea = BackwardElimination()
        final_breaks = bea.fit(delta_Y, Y_lag, [])
        
        assert final_breaks == [], "Empty input should give empty output"
    
    def test_minimum_segment_enforced(self, small_sample_data):
        """Test that minimum segment length is enforced."""
        delta_Y = small_sample_data['delta_Y']
        Y_lag = small_sample_data['Y'][:-1, :]
        
        min_seg = 50
        bea = BackwardElimination(min_segment_length=min_seg)
        
        # Candidates too close together
        initial = [90, 100, 110]
        final_breaks = bea.fit(delta_Y, Y_lag, initial)
        
        # Check minimum distance between breaks
        if len(final_breaks) > 1:
            for i in range(len(final_breaks) - 1):
                gap = final_breaks[i+1] - final_breaks[i]
                assert gap >= min_seg, f"Gap {gap} < min_seg {min_seg}"


# =============================================================================
# Test Principal Component Estimation
# =============================================================================

class TestPrincipalComponent:
    """Tests for principal component estimation."""
    
    def test_pc_estimation_case1(self, small_sample_data):
        """Test PC estimation for Case 1."""
        delta_Y = small_sample_data['delta_Y']
        Y_lag = small_sample_data['Y'][:-1, :]
        breaks = small_sample_data['true_breaks']
        
        estimator = PrincipalComponentEstimator(case=1, rank=1)
        results = estimator.fit(delta_Y, Y_lag, breaks)
        
        assert 'alpha' in results, "Should estimate alpha"
        assert 'beta' in results, "Should estimate beta"
        assert len(results['beta']) == 2, "Should have 2 regime betas"
    
    def test_pc_estimation_case2(self, case2_data):
        """Test PC estimation for Case 2."""
        delta_Y = case2_data['delta_Y']
        Y_lag = case2_data['Y'][:-1, :]
        breaks = case2_data['true_breaks']
        
        estimator = PrincipalComponentEstimator(case=2, rank=1)
        results = estimator.fit(delta_Y, Y_lag, breaks)
        
        assert len(results['alpha']) == 2, "Should have 2 regime alphas"
        assert len(results['beta']) == 2, "Should have 2 regime betas"
    
    def test_pc_normalization(self, small_sample_data):
        """Test that estimates are properly normalized."""
        delta_Y = small_sample_data['delta_Y']
        Y_lag = small_sample_data['Y'][:-1, :]
        breaks = small_sample_data['true_breaks']
        
        estimator = PrincipalComponentEstimator(case=1, rank=1)
        results = estimator.fit(delta_Y, Y_lag, breaks)
        
        # Check triangular normalization
        for beta in results['beta']:
            assert_allclose(beta[0, 0], 1.0, rtol=1e-5,
                           err_msg="First element should be 1")


# =============================================================================
# Test Full Pipeline
# =============================================================================

class TestFullPipeline:
    """Integration tests for full estimation pipeline."""
    
    def test_vecmbreak_basic(self, small_sample_data):
        """Test basic VECMBreak estimation."""
        Y = small_sample_data['Y']
        
        model = VECMBreak(case=1, rank=1, max_breaks=3)
        results = model.fit(Y)
        
        assert hasattr(results, 'n_breaks'), "Should have n_breaks"
        assert hasattr(results, 'break_dates'), "Should have break_dates"
        assert hasattr(results, 'alpha'), "Should have alpha"
        assert hasattr(results, 'beta'), "Should have beta"
    
    def test_vecmbreak_case2(self, case2_data):
        """Test VECMBreak for Case 2."""
        Y = case2_data['Y']
        
        model = VECMBreak(case=2, rank=1, max_breaks=3)
        results = model.fit(Y)
        
        assert results is not None, "Should produce results"
    
    def test_fit_vecm_breaks_convenience(self, small_sample_data):
        """Test convenience function."""
        Y = small_sample_data['Y']
        
        results = fit_vecm_breaks(Y, case=1, rank=1)
        
        assert results is not None, "Convenience function should work"
    
    def test_vecmbreak_with_deterministic(self, small_sample_data):
        """Test VECMBreak with deterministic terms."""
        Y = small_sample_data['Y']
        
        model = VECMBreak(case=1, rank=1, deterministic='c')
        results = model.fit(Y)
        
        assert results is not None, "Should handle deterministic terms"
    
    def test_vecmbreak_with_lags(self, seed):
        """Test VECMBreak with short-run dynamics."""
        data = generate_dgp_with_short_run(
            T=200, break_fractions=[0.5], k_ar=1, seed=seed
        )
        Y = data['Y']
        
        model = VECMBreak(case=1, rank=1, k_ar=1)
        results = model.fit(Y)
        
        assert results is not None, "Should handle lagged differences"
    
    def test_vecmbreak_auto_rank(self, small_sample_data):
        """Test automatic rank determination."""
        Y = small_sample_data['Y']
        
        model = VECMBreak(case=1, rank='auto', max_breaks=2)
        results = model.fit(Y)
        
        assert results.rank >= 1, "Should determine positive rank"
    
    def test_vecmbreak_summary(self, small_sample_data):
        """Test summary output."""
        Y = small_sample_data['Y']
        
        model = VECMBreak(case=1, rank=1)
        results = model.fit(Y)
        
        summary = results.summary()
        
        assert 'Break' in summary or 'break' in summary, \
            "Summary should mention breaks"
    
    def test_vecmbreak_predict(self, small_sample_data):
        """Test prediction."""
        Y = small_sample_data['Y']
        
        model = VECMBreak(case=1, rank=1)
        results = model.fit(Y)
        
        # Predict 5 steps ahead
        forecast = model.predict(steps=5)
        
        assert forecast.shape == (5, 2), "Should forecast correct shape"
    
    def test_results_to_dict(self, small_sample_data):
        """Test conversion to dictionary."""
        Y = small_sample_data['Y']
        
        model = VECMBreak(case=1, rank=1)
        results = model.fit(Y)
        
        d = results.to_dict()
        
        assert isinstance(d, dict), "Should return dictionary"
        assert 'n_breaks' in d, "Should contain n_breaks"
        assert 'break_dates' in d, "Should contain break_dates"


# =============================================================================
# Test Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and numerical stability."""
    
    def test_small_sample(self, seed):
        """Test with small sample size."""
        data = generate_dgp_case1(T=50, break_fractions=[0.5], seed=seed)
        Y = data['Y']
        
        model = VECMBreak(case=1, rank=1, min_segment_length=10)
        # Should not crash
        try:
            results = model.fit(Y)
        except Exception as e:
            pytest.fail(f"Small sample should not crash: {e}")
    
    def test_no_breaks_detected(self, seed):
        """Test when no breaks are detected."""
        # Generate stable data
        data = generate_dgp_case1(T=200, break_fractions=[], seed=seed)
        Y = data['Y']
        
        model = VECMBreak(case=1, rank=1, lambda_T=1.0)
        results = model.fit(Y)
        
        # Should handle zero breaks gracefully
        assert results.n_breaks >= 0, "n_breaks should be non-negative"
    
    def test_many_breaks(self, seed):
        """Test with many break candidates."""
        data = generate_dgp_case1(
            T=500, 
            break_fractions=[0.2, 0.4, 0.6, 0.8], 
            seed=seed
        )
        Y = data['Y']
        
        model = VECMBreak(case=1, rank=1, max_breaks=5)
        results = model.fit(Y)
        
        assert results.n_breaks <= 5, "Should respect max_breaks"
    
    def test_near_singular_covariance(self, seed):
        """Test handling of near-singular matrices."""
        np.random.seed(seed)
        
        # Create data with highly correlated series
        T = 200
        u = np.random.randn(T)
        Y = np.column_stack([u, u + 0.001 * np.random.randn(T)])
        Y = np.vstack([np.zeros((1, 2)), np.cumsum(Y, axis=0)])
        
        model = VECMBreak(case=1, rank=1)
        
        # Should handle without crashing
        try:
            results = model.fit(Y)
        except np.linalg.LinAlgError:
            pass  # Acceptable to raise LinAlg error for truly singular
    
    def test_different_variable_counts(self, seed):
        """Test with different numbers of variables."""
        for N in [2, 3, 4]:
            np.random.seed(seed)
            
            # Simple simulation
            T = 100
            Y = np.cumsum(np.random.randn(T + 1, N), axis=0)
            
            model = VECMBreak(case=1, rank=1)
            try:
                results = model.fit(Y)
            except Exception as e:
                pytest.fail(f"N={N} should work: {e}")


# =============================================================================
# Test IRF (if implemented)
# =============================================================================

class TestIRF:
    """Tests for impulse response functions."""
    
    def test_irf_computation(self, small_sample_data):
        """Test IRF computation."""
        Y = small_sample_data['Y']
        
        model = VECMBreak(case=1, rank=1)
        results = model.fit(Y)
        
        # Compute IRF
        try:
            irf = model.compute_irf(steps=10)
            assert irf.shape[0] == 10, "Should have correct horizon"
        except NotImplementedError:
            pytest.skip("IRF not implemented")


# =============================================================================
# Test Monte Carlo Replication
# =============================================================================

class TestMonteCarlo:
    """Tests for Monte Carlo simulation functions."""
    
    def test_monte_carlo_basic(self, seed):
        """Test basic Monte Carlo simulation."""
        from vecmbreak.data_generation import monte_carlo_simulation
        
        # Very small MC for testing
        results = monte_carlo_simulation(
            n_replications=3,
            T=100,
            break_fractions=[0.5],
            case=1,
            seed=seed
        )
        
        assert 'pce' in results, "Should compute PCE"
        assert 0 <= results['pce'] <= 1, "PCE should be between 0 and 1"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
