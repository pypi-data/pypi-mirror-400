"""
Result Classes for Structural Break and Cointegration Analysis
===============================================================

This module provides result classes that store and display results
from break estimation and cointegration testing.

Based on Schmidt and Schweikert (2021):
"Multiple structural breaks in cointegrating regressions: A model selection approach"
"""

import numpy as np
from typing import Optional, List, Dict, Union, Any
from dataclasses import dataclass, field
import warnings


@dataclass
class BreakEstimationResult:
    """
    Result class for structural break estimation.
    
    Attributes
    ----------
    n_breaks : int
        Number of detected structural breaks.
    break_fractions : np.ndarray
        Estimated break fractions τ ∈ (0, 1).
    break_dates : np.ndarray
        Estimated break date indices.
    intercept_coefs : np.ndarray
        Estimated intercept coefficients (μ_1, μ_2, ...).
    slope_coefs : np.ndarray
        Estimated slope coefficients (β_1, β_2, ...).
    intercept_changes : np.ndarray
        Parameter changes at each break (μ*_i for i > 1).
    slope_changes : np.ndarray
        Parameter changes at each break (β*_j for j > 1).
    residuals : np.ndarray
        Estimated residuals from the cointegrating regression.
    bic : float
        BIC value for the selected model.
    optimal_lambda : float
        Optimal tuning parameter from adaptive lasso.
    initial_lambda : float
        Initial tuning parameter from first-stage lasso.
    sample_size : int
        Sample size T.
    method : str
        Estimation method used ('adaptive_lasso', 'known_breaks', etc.).
    converged : bool
        Whether the estimation converged successfully.
    error_code : int
        Error code (0 = no error, 1 = no breaks found, 2 = singular matrix).
    
    Notes
    -----
    Following the notation from Schmidt and Schweikert (2021):
    - μ*_1 and β*_1 are the baseline (regime 1) coefficients
    - μ*_i (i > 1) and β*_j (j > 1) are the parameter changes
    """
    n_breaks: int
    break_fractions: np.ndarray
    break_dates: np.ndarray
    intercept_coefs: np.ndarray
    slope_coefs: np.ndarray
    intercept_changes: np.ndarray = field(default_factory=lambda: np.array([]))
    slope_changes: np.ndarray = field(default_factory=lambda: np.array([]))
    residuals: np.ndarray = field(default_factory=lambda: np.array([]))
    bic: float = np.nan
    optimal_lambda: float = np.nan
    initial_lambda: float = np.nan
    sample_size: int = 0
    method: str = ''
    converged: bool = True
    error_code: int = 0
    
    def __post_init__(self):
        """Convert lists to arrays and validate."""
        self.break_fractions = np.atleast_1d(np.asarray(self.break_fractions))
        self.break_dates = np.atleast_1d(np.asarray(self.break_dates))
        self.intercept_coefs = np.atleast_1d(np.asarray(self.intercept_coefs))
        self.slope_coefs = np.atleast_1d(np.asarray(self.slope_coefs))
        self.intercept_changes = np.atleast_1d(np.asarray(self.intercept_changes))
        self.slope_changes = np.atleast_1d(np.asarray(self.slope_changes))
        self.residuals = np.asarray(self.residuals)
    
    @property
    def regime_intercepts(self) -> np.ndarray:
        """
        Get the intercept values for each regime (cumulative sum).
        
        Returns
        -------
        np.ndarray
            Intercept values for each regime.
        """
        if len(self.intercept_changes) == 0:
            return self.intercept_coefs[:1]
        
        regime_values = [self.intercept_coefs[0]]
        for change in self.intercept_changes:
            regime_values.append(regime_values[-1] + change)
        return np.array(regime_values)
    
    @property
    def regime_slopes(self) -> np.ndarray:
        """
        Get the slope values for each regime (cumulative sum).
        
        Returns
        -------
        np.ndarray
            Slope values for each regime.
        """
        if len(self.slope_changes) == 0:
            return self.slope_coefs[:1]
        
        regime_values = [self.slope_coefs[0]]
        for change in self.slope_changes:
            regime_values.append(regime_values[-1] + change)
        return np.array(regime_values)
    
    @property
    def ssr(self) -> float:
        """Sum of squared residuals."""
        if len(self.residuals) == 0:
            return np.nan
        return np.sum(self.residuals ** 2)
    
    @property
    def mse(self) -> float:
        """Mean squared error."""
        if len(self.residuals) == 0:
            return np.nan
        return np.mean(self.residuals ** 2)
    
    def summary(self) -> str:
        """
        Generate a summary string of the estimation results.
        
        Returns
        -------
        str
            Formatted summary string.
        """
        lines = []
        lines.append("=" * 70)
        lines.append("Structural Break Estimation Results")
        lines.append("=" * 70)
        lines.append(f"Method: {self.method}")
        lines.append(f"Sample size: {self.sample_size}")
        lines.append(f"Number of breaks detected: {self.n_breaks}")
        lines.append("")
        
        if self.n_breaks > 0:
            lines.append("Break Dates:")
            lines.append("-" * 40)
            for i, (frac, date) in enumerate(zip(self.break_fractions, self.break_dates)):
                lines.append(f"  Break {i+1}: t = {date} (τ = {frac:.4f})")
            lines.append("")
        
        lines.append("Coefficient Estimates (Regime-Specific):")
        lines.append("-" * 40)
        regime_mu = self.regime_intercepts
        regime_beta = self.regime_slopes
        
        for i in range(len(regime_mu)):
            lines.append(f"  Regime {i+1}: μ = {regime_mu[i]:.4f}, β = {regime_beta[i]:.4f}")
        lines.append("")
        
        if self.n_breaks > 0:
            lines.append("Parameter Changes:")
            lines.append("-" * 40)
            if len(self.intercept_changes) > 0:
                for i, change in enumerate(self.intercept_changes):
                    lines.append(f"  Δμ_{i+2} = {change:.4f}")
            if len(self.slope_changes) > 0:
                for i, change in enumerate(self.slope_changes):
                    lines.append(f"  Δβ_{i+2} = {change:.4f}")
            lines.append("")
        
        lines.append("Model Selection:")
        lines.append("-" * 40)
        lines.append(f"  BIC: {self.bic:.4f}")
        if not np.isnan(self.optimal_lambda):
            lines.append(f"  Optimal λ: {self.optimal_lambda:.6f}")
        lines.append("")
        
        lines.append("Residual Statistics:")
        lines.append("-" * 40)
        lines.append(f"  SSR: {self.ssr:.4f}")
        lines.append(f"  MSE: {self.mse:.6f}")
        
        if self.error_code > 0:
            lines.append("")
            lines.append("Warnings:")
            if self.error_code == 1:
                lines.append("  No structural breaks were detected.")
            elif self.error_code == 2:
                lines.append("  Singular design matrix - adjacent breaks removed.")
        
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def __str__(self) -> str:
        return self.summary()
    
    def __repr__(self) -> str:
        return (f"BreakEstimationResult(n_breaks={self.n_breaks}, "
                f"break_fractions={self.break_fractions}, "
                f"method='{self.method}')")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary.
        
        Returns
        -------
        dict
            Dictionary representation of the result.
        """
        return {
            'n_breaks': self.n_breaks,
            'break_fractions': self.break_fractions.tolist(),
            'break_dates': self.break_dates.tolist(),
            'intercept_coefs': self.intercept_coefs.tolist(),
            'slope_coefs': self.slope_coefs.tolist(),
            'intercept_changes': self.intercept_changes.tolist(),
            'slope_changes': self.slope_changes.tolist(),
            'regime_intercepts': self.regime_intercepts.tolist(),
            'regime_slopes': self.regime_slopes.tolist(),
            'bic': self.bic,
            'optimal_lambda': self.optimal_lambda,
            'sample_size': self.sample_size,
            'method': self.method,
            'error_code': self.error_code,
        }


@dataclass
class CointegrationTestResult:
    """
    Result class for cointegration tests with structural breaks.
    
    Attributes
    ----------
    test_statistic : float
        Test statistic value (ADF or Z_t).
    critical_values : dict
        Critical values at different significance levels.
    p_value : float
        P-value (if available, otherwise NaN).
    reject_null : dict
        Boolean indicators for rejection at each significance level.
    test_type : str
        Type of test ('adf' or 'zt').
    n_breaks : int
        Number of breaks in the selected model.
    max_breaks : int
        Maximum number of breaks allowed.
    break_fractions : np.ndarray
        Estimated break fractions under the alternative.
    break_dates : np.ndarray
        Estimated break dates under the alternative.
    coefficients : dict
        Coefficient estimates (intercept and slope).
    residuals : np.ndarray
        Residuals from the cointegrating regression.
    sample_size : int
        Sample size.
    lag_order : int
        Lag order in ADF regression (if applicable).
    """
    test_statistic: float
    critical_values: Dict[float, float]
    p_value: float = np.nan
    reject_null: Dict[float, bool] = field(default_factory=dict)
    test_type: str = 'adf'
    n_breaks: int = 0
    max_breaks: int = 0
    break_fractions: np.ndarray = field(default_factory=lambda: np.array([]))
    break_dates: np.ndarray = field(default_factory=lambda: np.array([]))
    coefficients: Dict[str, np.ndarray] = field(default_factory=dict)
    residuals: np.ndarray = field(default_factory=lambda: np.array([]))
    sample_size: int = 0
    lag_order: int = 0
    
    def __post_init__(self):
        """Compute rejection decisions."""
        if not self.reject_null:
            self.reject_null = {
                level: bool(self.test_statistic < cv)
                for level, cv in self.critical_values.items()
            }
        self.break_fractions = np.atleast_1d(np.asarray(self.break_fractions))
        self.break_dates = np.atleast_1d(np.asarray(self.break_dates))
    
    @property
    def is_cointegrated(self) -> bool:
        """
        Check if null hypothesis of no cointegration is rejected at 5% level.
        
        Returns
        -------
        bool
            True if cointegration is detected at 5% significance.
        """
        return bool(self.reject_null.get(0.05, False))
    
    def summary(self) -> str:
        """
        Generate a summary string of the test results.
        
        Returns
        -------
        str
            Formatted summary string.
        """
        lines = []
        lines.append("=" * 70)
        if self.test_type.lower() == 'adf':
            lines.append("Cointegration Test with Structural Breaks (ADF-type)")
        else:
            lines.append("Cointegration Test with Structural Breaks (Z_t bias-corrected)")
        lines.append("=" * 70)
        lines.append(f"Sample size: {self.sample_size}")
        lines.append(f"Maximum breaks allowed: {self.max_breaks}")
        lines.append(f"Number of breaks selected: {self.n_breaks}")
        if self.test_type.lower() == 'adf':
            lines.append(f"Lag order: {self.lag_order}")
        lines.append("")
        
        lines.append("Test Results:")
        lines.append("-" * 40)
        lines.append(f"  Test statistic: {self.test_statistic:.4f}")
        lines.append("")
        lines.append("  Critical Values:")
        for level, cv in sorted(self.critical_values.items(), reverse=True):
            reject = "***" if self.reject_null.get(level, False) else ""
            lines.append(f"    {int(level*100)}%: {cv:.4f} {reject}")
        lines.append("")
        
        lines.append("Conclusion:")
        lines.append("-" * 40)
        if self.is_cointegrated:
            lines.append("  Reject null hypothesis of no cointegration at 5% level.")
            lines.append("  Evidence suggests the series are cointegrated.")
        else:
            lines.append("  Cannot reject null hypothesis of no cointegration at 5% level.")
            lines.append("  No evidence of cointegration found.")
        lines.append("")
        
        if self.n_breaks > 0:
            lines.append("Structural Breaks (under alternative):")
            lines.append("-" * 40)
            for i, (frac, date) in enumerate(zip(self.break_fractions, self.break_dates)):
                if not np.isnan(frac):
                    lines.append(f"  Break {i+1}: t = {date} (τ = {frac:.4f})")
            lines.append("")
        
        lines.append("=" * 70)
        lines.append("*** indicates rejection of the null at that significance level")
        
        return "\n".join(lines)
    
    def __str__(self) -> str:
        return self.summary()
    
    def __repr__(self) -> str:
        return (f"CointegrationTestResult(test_statistic={self.test_statistic:.4f}, "
                f"is_cointegrated={self.is_cointegrated}, "
                f"n_breaks={self.n_breaks})")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary.
        
        Returns
        -------
        dict
            Dictionary representation of the result.
        """
        return {
            'test_statistic': self.test_statistic,
            'critical_values': self.critical_values,
            'p_value': self.p_value,
            'reject_null': self.reject_null,
            'is_cointegrated': self.is_cointegrated,
            'test_type': self.test_type,
            'n_breaks': self.n_breaks,
            'max_breaks': self.max_breaks,
            'break_fractions': self.break_fractions.tolist() if len(self.break_fractions) > 0 else [],
            'break_dates': self.break_dates.tolist() if len(self.break_dates) > 0 else [],
            'sample_size': self.sample_size,
            'lag_order': self.lag_order,
        }
