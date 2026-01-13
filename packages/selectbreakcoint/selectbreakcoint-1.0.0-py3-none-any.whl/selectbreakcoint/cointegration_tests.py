"""
Cointegration Tests with Multiple Structural Breaks
=====================================================

This module implements residual-based cointegration tests that allow for
multiple structural breaks in the cointegrating relationship.

Based on Schmidt and Schweikert (2021):
"Multiple structural breaks in cointegrating regressions: A model selection approach"
Studies in Nonlinear Dynamics & Econometrics.

The tests follow Algorithm 2 (Section 2.3):
1. Use adaptive lasso to obtain model specification for each λ
2. Re-estimate using post-lasso OLS
3. Test residuals for stationarity using ADF and Z_t statistics
4. Select the model specification that minimizes the test statistic

Author: Dr. Merwan Roudane
"""

import numpy as np
from typing import Optional, List, Tuple, Union, Dict
import warnings

from .results import CointegrationTestResult
from .critical_values import get_critical_values, interpolate_critical_values
from .adaptive_lasso import AdaptiveLassoBreaks
from .utils import (
    estimate_long_run_variance,
    ols_estimation,
    compute_bic,
)


def adf_test(
    residuals: np.ndarray,
    max_lags: Optional[int] = None,
    lag_selection: str = 'aic'
) -> Tuple[float, int, np.ndarray]:
    """
    Augmented Dickey-Fuller test on residuals.
    
    Test the null hypothesis that residuals have a unit root.
    
    Parameters
    ----------
    residuals : np.ndarray
        Residuals from the cointegrating regression.
    max_lags : int, optional
        Maximum number of lags to consider. If None, uses T^(1/3).
    lag_selection : str, optional
        Lag selection method: 'aic', 'bic', or 'fixed'.
        Default is 'aic'.
        
    Returns
    -------
    adf_stat : float
        ADF test statistic.
    selected_lag : int
        Selected lag order.
    adf_regression_coefs : np.ndarray
        Coefficients from the ADF regression.
        
    Notes
    -----
    Implements the ADF regression:
    Δe_t = ρ·e_{t-1} + Σ_{j=1}^{K} γ_j·Δe_{t-j} + ε_t
    
    The test statistic is the t-ratio for ρ.
    """
    residuals = np.asarray(residuals).flatten()
    T = len(residuals)
    
    # Default max lags following Chang and Park (2002)
    if max_lags is None:
        max_lags = int(np.floor(T ** (1/3)))
    
    # First difference
    delta_e = np.diff(residuals)
    e_lag = residuals[:-1]
    
    T_eff = len(delta_e)
    
    def estimate_adf_regression(k):
        """Estimate ADF regression with k lags."""
        if k == 0:
            X = e_lag[max_lags:].reshape(-1, 1)
            y = delta_e[max_lags:]
        else:
            # Construct lag matrix
            X = np.zeros((T_eff - max_lags, k + 1))
            X[:, 0] = e_lag[max_lags:]
            for j in range(1, k + 1):
                X[:, j] = delta_e[max_lags - j:-j]
            y = delta_e[max_lags:]
        
        # OLS estimation
        coef, resid, ssr = ols_estimation(X, y, return_residuals=True)
        
        # Compute standard error of rho
        n = len(y)
        p = X.shape[1] if X.ndim > 1 else 1
        sigma2 = ssr / (n - p)
        
        # Variance-covariance matrix
        try:
            XtX_inv = np.linalg.inv(X.T @ X)
            if XtX_inv.ndim == 0:
                se_rho = np.sqrt(sigma2 * XtX_inv)
            else:
                se_rho = np.sqrt(sigma2 * XtX_inv[0, 0])
        except np.linalg.LinAlgError:
            se_rho = np.inf
        
        # t-statistic for rho
        rho_coef = coef[0] if isinstance(coef, np.ndarray) and len(coef) > 0 else coef
        t_stat = rho_coef / se_rho if se_rho > 0 else 0
        
        # Information criteria
        aic = n * np.log(ssr / n) + 2 * p
        bic = n * np.log(ssr / n) + np.log(n) * p
        
        return t_stat, coef, resid, aic, bic
    
    if lag_selection == 'fixed':
        selected_lag = min(max_lags, T_eff - 2)
        adf_stat, coef, resid, _, _ = estimate_adf_regression(selected_lag)
    else:
        # Search for optimal lag
        best_ic = np.inf
        selected_lag = 0
        adf_stat = 0
        coef = None
        
        for k in range(max_lags + 1):
            if T_eff - max_lags - k - 1 < 2:
                break
                
            t_stat, coef_k, resid_k, aic, bic = estimate_adf_regression(k)
            
            ic = aic if lag_selection == 'aic' else bic
            
            if ic < best_ic:
                best_ic = ic
                selected_lag = k
                adf_stat = t_stat
                coef = coef_k
    
    return adf_stat, selected_lag, coef


def phillips_perron_test(
    residuals: np.ndarray,
    bandwidth: Optional[int] = None
) -> Tuple[float, float, float]:
    """
    Phillips-Perron test for unit root in residuals.
    
    Implements the bias-corrected Z_t statistic following Phillips (1987).
    
    Parameters
    ----------
    residuals : np.ndarray
        Residuals from the cointegrating regression.
    bandwidth : int, optional
        Bandwidth for long-run variance estimation.
        If None, uses Newey-West rule.
        
    Returns
    -------
    z_t : float
        Bias-corrected Z_t test statistic.
    rho_hat : float
        Estimated autoregressive coefficient.
    sigma2 : float
        Long-run variance estimate.
        
    Notes
    -----
    The bias-corrected estimator is:
    ρ* = Σ(e_t·e_{t-1} - ψ) / Σ(e_{t-1}²)
    
    where ψ is the bias correction term (weighted sum of autocovariances).
    """
    residuals = np.asarray(residuals).flatten()
    T = len(residuals)
    
    # Default bandwidth using Newey-West rule
    if bandwidth is None:
        bandwidth = int(np.floor(4 * (T / 100) ** (2/9)))
    
    # Lagged residuals
    e_lag = residuals[:-1]
    e_current = residuals[1:]
    
    # AR(1) regression: e_t = ρ·e_{t-1} + v_t
    sum_e_lag_sq = np.sum(e_lag ** 2)
    sum_e_prod = np.sum(e_current * e_lag)
    
    rho_hat = sum_e_prod / sum_e_lag_sq
    
    # Residuals from AR(1)
    v_hat = e_current - rho_hat * e_lag
    
    # Sample variance of v
    gamma_0 = np.mean(v_hat ** 2)
    
    # Autocovariances and bias correction
    psi_hat = 0.0
    for j in range(1, bandwidth + 1):
        gamma_j = np.mean(v_hat[j:] * v_hat[:-j])
        # Bartlett kernel weights
        w_j = 1 - j / (bandwidth + 1)
        psi_hat += w_j * gamma_j
    
    # Long-run variance estimate
    sigma2 = gamma_0 + 2 * psi_hat
    
    # Bias-corrected estimator
    rho_star = (sum_e_prod - T * psi_hat) / sum_e_lag_sq
    
    # Standard error for Z_t statistic
    s2 = sigma2 / sum_e_lag_sq
    s = np.sqrt(max(s2, 1e-10))
    
    # Z_t statistic
    z_t = (rho_star - 1) / s
    
    return z_t, rho_hat, sigma2


def engle_granger_test(
    y: np.ndarray,
    x: np.ndarray,
    max_lags: Optional[int] = None,
    test_type: str = 'adf'
) -> CointegrationTestResult:
    """
    Engle-Granger two-step cointegration test.
    
    This is the standard test without structural breaks, used as a benchmark.
    
    Parameters
    ----------
    y : np.ndarray
        Dependent variable.
    x : np.ndarray
        Regressor variable.
    max_lags : int, optional
        Maximum lags for ADF test.
    test_type : str, optional
        Test type: 'adf' or 'pp' (Phillips-Perron).
        
    Returns
    -------
    CointegrationTestResult
        Test results.
    """
    y = np.asarray(y).flatten()
    x = np.asarray(x).flatten()
    T = len(y)
    
    # Step 1: Estimate cointegrating regression
    X = np.column_stack([np.ones(T), x])
    coef, residuals, _ = ols_estimation(X, y)
    
    # Step 2: Test residuals for unit root
    if test_type.lower() == 'adf':
        stat, lag, _ = adf_test(residuals, max_lags)
        test_name = 'adf'
    else:
        stat, _, _ = phillips_perron_test(residuals)
        lag = 0
        test_name = 'zt'
    
    # Critical values for EG test (no structural breaks)
    # Using MacKinnon critical values
    critical_values = {
        0.10: -3.12,
        0.05: -3.41,
        0.01: -3.96
    }
    
    return CointegrationTestResult(
        test_statistic=stat,
        critical_values=critical_values,
        test_type=test_name,
        n_breaks=0,
        max_breaks=0,
        break_fractions=np.array([]),
        break_dates=np.array([]),
        coefficients={'intercept': np.array([coef[0]]), 'slope': np.array([coef[1]])},
        residuals=residuals,
        sample_size=T,
        lag_order=lag
    )


class CointegrationTest:
    """
    Cointegration Test with Multiple Structural Breaks.
    
    Implements the residual-based cointegration test from Schmidt and Schweikert (2021)
    that accounts for multiple structural breaks in both the intercept and slope
    of the cointegrating relationship.
    
    Parameters
    ----------
    max_breaks : int
        Maximum number of structural breaks allowed.
    trim : float, optional
        Lateral trimming parameter. Default is 0.05.
    test_type : str, optional
        Type of test statistic: 'adf' or 'zt'. Default is 'adf'.
    lag_selection : str, optional
        Lag selection method for ADF: 'aic', 'bic', or 'fixed'.
        Default is 'aic'.
    n_lambda : int, optional
        Number of lambda values in the tuning parameter grid.
        Default is 100.
    dynamic_lags : int, optional
        Number of leads and lags for dynamic augmentation.
        Default is 0.
        
    Attributes
    ----------
    result_ : CointegrationTestResult
        Test result after calling test().
    break_result_ : BreakEstimationResult
        Break estimation result under the alternative.
        
    Notes
    -----
    The test procedure follows Algorithm 2:
    1. For each λ in the grid, estimate structural breaks using adaptive lasso
    2. Re-estimate the model using post-lasso OLS
    3. Compute the cointegration test statistic on the residuals
    4. Select the model that minimizes the test statistic (infimum test)
    5. Compare with critical values from Table 1
    
    Examples
    --------
    >>> from selectbreakcoint import CointegrationTest
    >>> import numpy as np
    >>> 
    >>> # Test for cointegration allowing up to 2 breaks
    >>> test = CointegrationTest(max_breaks=2)
    >>> result = test.test(x, y)
    >>> print(result)
    """
    
    def __init__(
        self,
        max_breaks: int = 1,
        trim: float = 0.05,
        test_type: str = 'adf',
        lag_selection: str = 'aic',
        n_lambda: int = 100,
        dynamic_lags: int = 0
    ):
        self.max_breaks = max_breaks
        self.trim = trim
        self.test_type = test_type.lower()
        self.lag_selection = lag_selection
        self.n_lambda = n_lambda
        self.dynamic_lags = dynamic_lags
        
        self.result_ = None
        self.break_result_ = None
        self._fitted = False
    
    def test(
        self,
        x: np.ndarray,
        y: np.ndarray
    ) -> CointegrationTestResult:
        """
        Perform the cointegration test with structural breaks.
        
        Parameters
        ----------
        x : np.ndarray
            Regressor variable (should be I(1)).
        y : np.ndarray
            Dependent variable.
            
        Returns
        -------
        CointegrationTestResult
            Test results including statistic, critical values, and break estimates.
        """
        x = np.asarray(x).flatten()
        y = np.asarray(y).flatten()
        T = len(y)
        
        if len(x) != T:
            raise ValueError("x and y must have the same length")
        
        # Generate lambda grid
        lambda_grid = np.logspace(5, -2, self.n_lambda)
        
        # Track best (minimum) test statistic across all lambda values
        best_stat = np.inf
        best_break_result = None
        best_residuals = None
        best_lag = 0
        
        # Estimate for each number of breaks (0 to max_breaks)
        for m in range(self.max_breaks + 1):
            if m == 0:
                # No breaks - standard regression
                X = np.column_stack([np.ones(T), x])
                coef, residuals, _ = ols_estimation(X, y)
                
                # Test residuals
                if self.test_type == 'adf':
                    stat, lag, _ = adf_test(residuals, lag_selection=self.lag_selection)
                else:
                    stat, _, _ = phillips_perron_test(residuals)
                    lag = 0
                
                if stat < best_stat:
                    best_stat = stat
                    best_residuals = residuals
                    best_lag = lag
                    best_break_result = None
            else:
                # Fit adaptive lasso model with up to m breaks
                model = AdaptiveLassoBreaks(
                    max_breaks=m,
                    trim=self.trim,
                    n_lambda=self.n_lambda,
                    dynamic_lags=self.dynamic_lags
                )
                
                try:
                    break_result = model.fit(x, y)
                    residuals = break_result.residuals
                    
                    if len(residuals) > 0:
                        # Test residuals
                        if self.test_type == 'adf':
                            stat, lag, _ = adf_test(
                                residuals, 
                                lag_selection=self.lag_selection
                            )
                        else:
                            stat, _, _ = phillips_perron_test(residuals)
                            lag = 0
                        
                        if stat < best_stat:
                            best_stat = stat
                            best_break_result = break_result
                            best_residuals = residuals
                            best_lag = lag
                            
                except Exception as e:
                    warnings.warn(f"Error fitting model with {m} breaks: {e}")
                    continue
        
        # Get critical values
        cv = get_critical_values(
            max_breaks=self.max_breaks,
            sample_size=T,
            test_type=self.test_type
        )
        
        # Determine break information
        if best_break_result is not None:
            n_breaks = best_break_result.n_breaks
            break_fractions = best_break_result.break_fractions
            break_dates = best_break_result.break_dates
            coefficients = {
                'intercept': best_break_result.intercept_coefs,
                'slope': best_break_result.slope_coefs,
                'intercept_changes': best_break_result.intercept_changes,
                'slope_changes': best_break_result.slope_changes
            }
        else:
            n_breaks = 0
            break_fractions = np.array([])
            break_dates = np.array([])
            coefficients = {}
        
        self.result_ = CointegrationTestResult(
            test_statistic=best_stat,
            critical_values=cv,
            test_type=self.test_type,
            n_breaks=n_breaks,
            max_breaks=self.max_breaks,
            break_fractions=break_fractions,
            break_dates=break_dates,
            coefficients=coefficients,
            residuals=best_residuals if best_residuals is not None else np.array([]),
            sample_size=T,
            lag_order=best_lag
        )
        
        self.break_result_ = best_break_result
        self._fitted = True
        
        return self.result_
    
    def is_cointegrated(self, significance: float = 0.05) -> bool:
        """
        Check if series are cointegrated at given significance level.
        
        Parameters
        ----------
        significance : float, optional
            Significance level (0.01, 0.05, or 0.10).
            
        Returns
        -------
        bool
            True if null hypothesis of no cointegration is rejected.
        """
        if not self._fitted:
            raise RuntimeError("Test must be run first")
        
        return self.result_.reject_null.get(significance, False)
    
    def get_breaks(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get estimated break dates and fractions.
        
        Returns
        -------
        break_fractions : np.ndarray
            Break fractions τ.
        break_dates : np.ndarray
            Break date indices.
        """
        if not self._fitted:
            raise RuntimeError("Test must be run first")
        
        return self.result_.break_fractions, self.result_.break_dates


def gregory_hansen_test(
    y: np.ndarray,
    x: np.ndarray,
    model: str = 'C',
    trim: float = 0.15
) -> CointegrationTestResult:
    """
    Gregory-Hansen cointegration test with one structural break.
    
    Implementation of Gregory and Hansen (1996) for comparison purposes.
    
    Parameters
    ----------
    y : np.ndarray
        Dependent variable.
    x : np.ndarray
        Regressor variable.
    model : str, optional
        Model type:
        'C' - Level shift
        'C/T' - Level shift with trend
        'C/S' - Regime shift (intercept and slope)
    trim : float, optional
        Trimming parameter. Default is 0.15.
        
    Returns
    -------
    CointegrationTestResult
        Test results.
    """
    y = np.asarray(y).flatten()
    x = np.asarray(x).flatten()
    T = len(y)
    
    trim_low = int(np.ceil(trim * T))
    trim_high = int(np.floor((1 - trim) * T))
    
    best_stat = np.inf
    best_break = None
    best_residuals = None
    
    for tb in range(trim_low, trim_high + 1):
        # Construct design matrix
        indicator = np.zeros(T)
        indicator[tb:] = 1.0
        
        if model == 'C':
            X = np.column_stack([np.ones(T), indicator, x])
        elif model == 'C/T':
            trend = np.arange(1, T + 1)
            X = np.column_stack([np.ones(T), indicator, trend, x])
        elif model == 'C/S':
            X = np.column_stack([np.ones(T), indicator, x, x * indicator])
        else:
            raise ValueError(f"Unknown model: {model}")
        
        coef, residuals, _ = ols_estimation(X, y)
        stat, _, _ = adf_test(residuals)
        
        if stat < best_stat:
            best_stat = stat
            best_break = tb
            best_residuals = residuals
    
    # Critical values from Gregory and Hansen (1996)
    if model == 'C':
        cv = {0.10: -4.61, 0.05: -4.92, 0.01: -5.47}
    elif model == 'C/T':
        cv = {0.10: -4.99, 0.05: -5.29, 0.01: -5.97}
    elif model == 'C/S':
        cv = {0.10: -4.95, 0.05: -5.28, 0.01: -5.97}
    
    return CointegrationTestResult(
        test_statistic=best_stat,
        critical_values=cv,
        test_type='adf',
        n_breaks=1,
        max_breaks=1,
        break_fractions=np.array([best_break / T]) if best_break else np.array([]),
        break_dates=np.array([best_break]) if best_break else np.array([]),
        coefficients={},
        residuals=best_residuals if best_residuals is not None else np.array([]),
        sample_size=T,
        lag_order=0
    )


def hatemi_j_test(
    y: np.ndarray,
    x: np.ndarray,
    trim: float = 0.15
) -> CointegrationTestResult:
    """
    Hatemi-J cointegration test with two structural breaks.
    
    Implementation of Hatemi-J (2008) for comparison purposes.
    
    Parameters
    ----------
    y : np.ndarray
        Dependent variable.
    x : np.ndarray
        Regressor variable.
    trim : float, optional
        Trimming parameter.
        
    Returns
    -------
    CointegrationTestResult
        Test results.
    """
    y = np.asarray(y).flatten()
    x = np.asarray(x).flatten()
    T = len(y)
    
    trim_low = int(np.ceil(trim * T))
    trim_high = int(np.floor((1 - trim) * T))
    
    best_stat = np.inf
    best_breaks = None
    best_residuals = None
    
    for tb1 in range(trim_low, trim_high - trim_low):
        for tb2 in range(tb1 + trim_low, trim_high + 1):
            # Construct design matrix (regime shift model)
            ind1 = np.zeros(T)
            ind1[tb1:] = 1.0
            ind2 = np.zeros(T)
            ind2[tb2:] = 1.0
            
            X = np.column_stack([
                np.ones(T), ind1, ind2,
                x, x * ind1, x * ind2
            ])
            
            coef, residuals, _ = ols_estimation(X, y)
            stat, _, _ = adf_test(residuals)
            
            if stat < best_stat:
                best_stat = stat
                best_breaks = (tb1, tb2)
                best_residuals = residuals
    
    # Critical values from Hatemi-J (2008)
    cv = {0.10: -5.54, 0.05: -5.83, 0.01: -6.41}
    
    if best_breaks:
        fractions = np.array([best_breaks[0] / T, best_breaks[1] / T])
        dates = np.array(best_breaks)
    else:
        fractions = np.array([])
        dates = np.array([])
    
    return CointegrationTestResult(
        test_statistic=best_stat,
        critical_values=cv,
        test_type='adf',
        n_breaks=2,
        max_breaks=2,
        break_fractions=fractions,
        break_dates=dates,
        coefficients={},
        residuals=best_residuals if best_residuals is not None else np.array([]),
        sample_size=T,
        lag_order=0
    )
