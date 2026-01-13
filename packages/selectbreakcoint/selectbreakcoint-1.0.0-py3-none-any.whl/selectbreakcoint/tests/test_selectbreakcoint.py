"""
Unit Tests for selectbreakcoint Package
========================================

This module contains unit tests for the selectbreakcoint package.
"""

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_almost_equal


def test_imports():
    """Test that all modules can be imported."""
    from selectbreakcoint import (
        AdaptiveLassoBreaks,
        CointegrationTest,
        BreakEstimationResult,
        CointegrationTestResult,
        get_critical_values,
        construct_break_indicators,
        compute_bic,
        hausdorff_distance,
    )
    assert True


def test_critical_values():
    """Test critical value retrieval."""
    from selectbreakcoint import get_critical_values
    
    # Test for max_breaks = 1, T = 100
    cv = get_critical_values(max_breaks=1, sample_size=100, test_type='adf')
    assert 0.10 in cv
    assert 0.05 in cv
    assert 0.01 in cv
    assert cv[0.05] == pytest.approx(-4.37)
    
    # Test for max_breaks = 2, T = 200, Z_t test
    cv = get_critical_values(max_breaks=2, sample_size=200, test_type='zt')
    assert cv[0.05] == pytest.approx(-5.17)


def test_break_indicators():
    """Test break indicator construction."""
    from selectbreakcoint.utils import construct_break_indicators
    
    T = 100
    breaks = [0.5]
    indicators = construct_break_indicators(T, breaks, include_baseline=True)
    
    assert indicators.shape == (T, 2)
    assert indicators[:50, 1].sum() == 0  # Before break
    assert indicators[50:, 1].sum() == 50  # After break
    assert indicators[:, 0].sum() == T  # Baseline all ones


def test_design_matrix():
    """Test design matrix construction."""
    from selectbreakcoint.utils import construct_design_matrix
    
    T = 100
    x = np.random.randn(T)
    y = np.random.randn(T)
    
    X, y_out, col_names = construct_design_matrix(
        x, y,
        break_fractions_intercept=[0.5],
        break_fractions_slope=[0.5]
    )
    
    # Should have: intercept, mu_delta_2, x, x*indicator
    assert X.shape[1] == 4
    assert len(col_names) == 4


def test_bic_computation():
    """Test BIC computation."""
    from selectbreakcoint.utils import compute_bic, compute_modified_bic
    
    residuals = np.random.randn(100)
    n_params = 3
    T = 100
    
    bic = compute_bic(residuals, n_params, T)
    assert np.isfinite(bic)
    
    # Modified BIC should be different
    bic_star = compute_modified_bic(residuals, n_params, T, 50)
    assert np.isfinite(bic_star)


def test_hausdorff_distance():
    """Test Hausdorff distance computation."""
    from selectbreakcoint.utils import hausdorff_distance
    
    # Same sets should have distance 0
    assert hausdorff_distance([0.5], [0.5]) == 0.0
    
    # Test with different sets
    d = hausdorff_distance([0.3, 0.7], [0.33, 0.67])
    assert d == pytest.approx(0.03)
    
    # Empty sets
    assert hausdorff_distance([], []) == 0.0
    assert np.isinf(hausdorff_distance([0.5], []))


def test_dynamic_augmentation():
    """Test dynamic augmentation for endogeneity correction."""
    from selectbreakcoint.utils import dynamic_augmentation
    
    T = 100
    x = np.cumsum(np.random.randn(T))
    
    z = dynamic_augmentation(x, k=2)
    assert z.shape == (T, 5)  # dx and 2 leads + 2 lags


def generate_cointegrated_data(T, break_frac=None, seed=42):
    """Generate cointegrated data with optional break."""
    np.random.seed(seed)
    
    # I(1) regressor
    x = np.cumsum(np.random.randn(T))
    
    if break_frac is None:
        # No break
        y = 2 + 2 * x + np.random.randn(T) * 0.5
    else:
        # With break
        bp = int(break_frac * T)
        e = np.random.randn(T) * 0.5
        y = np.zeros(T)
        y[:bp] = 2 + 2 * x[:bp] + e[:bp]
        y[bp:] = 4 + 4 * x[bp:] + e[bp:]
    
    return x, y


def test_adaptive_lasso_no_breaks():
    """Test adaptive lasso when there are no true breaks."""
    from selectbreakcoint import AdaptiveLassoBreaks
    
    T = 100
    x, y = generate_cointegrated_data(T, break_frac=None)
    
    model = AdaptiveLassoBreaks(max_breaks=2, trim=0.1)
    result = model.fit(x, y)
    
    # Should detect 0 or very few breaks
    assert result.n_breaks <= 1
    assert len(result.residuals) == T


def test_adaptive_lasso_with_break():
    """Test adaptive lasso with a structural break."""
    from selectbreakcoint import AdaptiveLassoBreaks
    
    T = 200
    x, y = generate_cointegrated_data(T, break_frac=0.5, seed=123)
    
    model = AdaptiveLassoBreaks(max_breaks=2, trim=0.1)
    result = model.fit(x, y)
    
    # Should detect at least one break near 0.5
    assert result.n_breaks >= 1
    if result.n_breaks > 0:
        # Check break is roughly in the right place
        closest_break = min(result.break_fractions, key=lambda x: abs(x - 0.5))
        assert abs(closest_break - 0.5) < 0.15  # Within 15% of true break


def test_cointegration_test():
    """Test cointegration test procedure."""
    from selectbreakcoint import CointegrationTest
    
    T = 100
    x, y = generate_cointegrated_data(T, break_frac=None)
    
    test = CointegrationTest(max_breaks=1)
    result = test.test(x, y)
    
    assert np.isfinite(result.test_statistic)
    assert 0.05 in result.critical_values
    assert isinstance(result.is_cointegrated, bool)


def test_adf_test():
    """Test ADF unit root test."""
    from selectbreakcoint.cointegration_tests import adf_test
    
    # Stationary series (should reject unit root)
    residuals = np.random.randn(200)
    stat, lag, _ = adf_test(residuals)
    assert np.isfinite(stat)
    assert stat < -2  # Should be significantly negative for stationary series
    
    # Unit root series (should not reject)
    residuals_ur = np.cumsum(np.random.randn(200))
    stat_ur, _, _ = adf_test(residuals_ur)
    assert stat_ur > -3  # Should be close to zero for unit root


def test_phillips_perron_test():
    """Test Phillips-Perron unit root test."""
    from selectbreakcoint.cointegration_tests import phillips_perron_test
    
    # Stationary series
    residuals = np.random.randn(200)
    z_t, rho, sigma2 = phillips_perron_test(residuals)
    
    assert np.isfinite(z_t)
    assert np.isfinite(rho)
    assert sigma2 > 0


def test_result_classes():
    """Test result class functionality."""
    from selectbreakcoint import BreakEstimationResult, CointegrationTestResult
    
    # Test BreakEstimationResult
    result = BreakEstimationResult(
        n_breaks=1,
        break_fractions=np.array([0.5]),
        break_dates=np.array([50]),
        intercept_coefs=np.array([2.0]),
        slope_coefs=np.array([2.0]),
        intercept_changes=np.array([1.0]),
        slope_changes=np.array([1.0]),
        residuals=np.random.randn(100),
        sample_size=100,
        method='test'
    )
    
    assert result.n_breaks == 1
    assert len(result.regime_intercepts) == 2
    assert len(result.regime_slopes) == 2
    
    # Test summary generation
    summary = result.summary()
    assert 'Break' in summary
    
    # Test CointegrationTestResult
    coint_result = CointegrationTestResult(
        test_statistic=-4.5,
        critical_values={0.10: -4.0, 0.05: -4.3, 0.01: -5.0},
        test_type='adf',
        sample_size=100
    )
    
    assert coint_result.is_cointegrated
    assert coint_result.reject_null[0.05]


def test_engle_granger_test():
    """Test Engle-Granger cointegration test."""
    from selectbreakcoint.cointegration_tests import engle_granger_test
    
    T = 200
    x, y = generate_cointegrated_data(T, break_frac=None)
    
    result = engle_granger_test(y, x)
    
    assert np.isfinite(result.test_statistic)
    assert result.n_breaks == 0


def test_gregory_hansen_test():
    """Test Gregory-Hansen cointegration test."""
    from selectbreakcoint.cointegration_tests import gregory_hansen_test
    
    T = 200
    x, y = generate_cointegrated_data(T, break_frac=0.5, seed=456)
    
    result = gregory_hansen_test(y, x, model='C/S')
    
    assert np.isfinite(result.test_statistic)
    assert result.n_breaks == 1
    if len(result.break_fractions) > 0:
        assert 0 < result.break_fractions[0] < 1


def test_known_breaks_estimation():
    """Test estimation with known breakpoint candidates."""
    from selectbreakcoint import AdaptiveLassoBreaks
    
    T = 100
    np.random.seed(42)
    x = np.cumsum(np.random.randn(T))
    y = 2 + 2 * x + np.random.randn(T) * 0.5
    
    # Test with known break candidates
    model = AdaptiveLassoBreaks(max_breaks=3)
    result = model.fit(x, y, known_breaks=[0.25, 0.5, 0.75])
    
    assert result.method == 'adaptive_lasso_known'
    assert len(result.residuals) == T


def test_prediction():
    """Test prediction with fitted model."""
    from selectbreakcoint import AdaptiveLassoBreaks
    
    T = 100
    x, y = generate_cointegrated_data(T, break_frac=None)
    
    model = AdaptiveLassoBreaks(max_breaks=1)
    model.fit(x, y)
    
    y_pred = model.predict(x)
    assert len(y_pred) == T
    
    # Predictions should be reasonable
    assert np.corrcoef(y, y_pred)[0, 1] > 0.9


def run_all_tests():
    """Run all tests."""
    test_functions = [
        test_imports,
        test_critical_values,
        test_break_indicators,
        test_design_matrix,
        test_bic_computation,
        test_hausdorff_distance,
        test_dynamic_augmentation,
        test_adaptive_lasso_no_breaks,
        test_adaptive_lasso_with_break,
        test_cointegration_test,
        test_adf_test,
        test_phillips_perron_test,
        test_result_classes,
        test_engle_granger_test,
        test_gregory_hansen_test,
        test_known_breaks_estimation,
        test_prediction,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            print(f"✓ {test_func.__name__}")
            passed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__}: {e}")
            failed += 1
    
    print(f"\n{passed} passed, {failed} failed")
    return failed == 0


if __name__ == '__main__':
    run_all_tests()
