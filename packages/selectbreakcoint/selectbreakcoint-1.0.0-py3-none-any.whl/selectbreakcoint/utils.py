"""
Utility Functions for Structural Break Detection
=================================================

This module provides utility functions for:
- Constructing break indicator matrices
- Computing information criteria (BIC, modified BIC)
- Dynamic augmentation for endogeneity correction
- Performance metrics (Hausdorff distance)

Based on Schmidt and Schweikert (2021):
"Multiple structural breaks in cointegrating regressions: A model selection approach"
"""

import numpy as np
from scipy import linalg
from typing import Optional, List, Tuple, Union
import warnings


def construct_break_indicators(
    T: int,
    break_fractions: Union[List[float], np.ndarray],
    include_baseline: bool = True
) -> np.ndarray:
    """
    Construct indicator variables for structural breaks.
    
    For a break at fraction τ, the indicator φ_t,τ = 1 if t > [T*τ], 0 otherwise.
    Following Equation (6) from Schmidt and Schweikert (2021).
    
    Parameters
    ----------
    T : int
        Sample size.
    break_fractions : array-like
        List of break fractions τ ∈ (0, 1).
    include_baseline : bool, optional
        If True, include the baseline indicator (all ones).
        
    Returns
    -------
    np.ndarray
        Matrix of shape (T, n_breaks + include_baseline) containing indicators.
        
    Examples
    --------
    >>> indicators = construct_break_indicators(100, [0.5])
    >>> indicators[:51].sum(axis=0)  # First 51 obs with baseline
    array([51.,  1.])
    """
    break_fractions = np.asarray(break_fractions)
    n_breaks = len(break_fractions)
    
    n_cols = n_breaks + (1 if include_baseline else 0)
    indicators = np.zeros((T, n_cols))
    
    col_idx = 0
    if include_baseline:
        indicators[:, 0] = 1.0
        col_idx = 1
    
    for i, tau in enumerate(break_fractions):
        break_point = int(np.floor(T * tau))
        indicators[break_point:, col_idx + i] = 1.0
    
    return indicators


def construct_design_matrix(
    x: np.ndarray,
    y: np.ndarray,
    break_fractions_intercept: Optional[List[float]] = None,
    break_fractions_slope: Optional[List[float]] = None,
    trim: float = 0.05
) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """
    Construct the design matrix for cointegrating regression with structural breaks.
    
    Following Equation (5) from Schmidt and Schweikert (2021):
    y_t = Σ μ*_i φ_{t,τ_{1,i-1}} + Σ β*_j x_t φ_{t,τ_{2,j-1}} + u_t
    
    Parameters
    ----------
    x : np.ndarray
        Regressor variable (integrated process).
    y : np.ndarray
        Dependent variable.
    break_fractions_intercept : list, optional
        Break fractions for the intercept.
    break_fractions_slope : list, optional
        Break fractions for the slope coefficient.
    trim : float, optional
        Lateral trimming parameter (default: 0.05).
        
    Returns
    -------
    X : np.ndarray
        Design matrix.
    y : np.ndarray
        Response vector.
    col_names : list
        Column names for the design matrix.
    """
    T = len(y)
    x = np.asarray(x).flatten()
    y = np.asarray(y).flatten()
    
    if break_fractions_intercept is None:
        break_fractions_intercept = []
    if break_fractions_slope is None:
        break_fractions_slope = []
    
    columns = []
    col_names = []
    
    # Baseline intercept
    columns.append(np.ones(T))
    col_names.append('mu_1')
    
    # Intercept break indicators
    for i, tau in enumerate(break_fractions_intercept):
        bp = int(np.floor(T * tau))
        indicator = np.zeros(T)
        indicator[bp:] = 1.0
        columns.append(indicator)
        col_names.append(f'mu_delta_{i+2}')
    
    # Baseline slope (x)
    columns.append(x)
    col_names.append('beta_1')
    
    # Slope break indicators (x * indicator)
    for j, tau in enumerate(break_fractions_slope):
        bp = int(np.floor(T * tau))
        indicator = np.zeros(T)
        indicator[bp:] = 1.0
        columns.append(x * indicator)
        col_names.append(f'beta_delta_{j+2}')
    
    X = np.column_stack(columns)
    
    return X, y, col_names


def construct_full_break_matrix(
    x: np.ndarray,
    trim: float = 0.05
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Construct design matrix with all possible break points.
    
    This is used for the diverging number of breakpoint candidates setting.
    Following Section 2.2 of Schmidt and Schweikert (2021).
    
    Parameters
    ----------
    x : np.ndarray
        Regressor variable.
    trim : float, optional
        Lateral trimming parameter.
        
    Returns
    -------
    X : np.ndarray
        Full design matrix with all potential break indicators.
    break_indices : np.ndarray
        Indices corresponding to each potential break point.
    """
    T = len(x)
    x = np.asarray(x).flatten()
    
    # Apply lateral trimming
    trim_low = int(np.ceil(trim * T))
    trim_high = int(np.floor((1 - trim) * T))
    
    # Number of potential break points
    n_breaks = trim_high - trim_low - 1
    
    # Construct lower triangular matrix for cumulative indicators
    lower_ones = np.tril(np.ones((T, T)))
    
    # Extract relevant columns (after trimming)
    # Columns correspond to break points at positions trim_low+1 to trim_high-1
    relevant_cols = list(range(trim_low + 1, trim_high))
    
    # Construct X*ɸ for slope breaks
    X_slope = np.zeros((T, len(relevant_cols) + 1))
    X_slope[:, 0] = x  # Baseline x
    
    for i, bp in enumerate(relevant_cols):
        indicator = np.zeros(T)
        indicator[bp:] = 1.0
        X_slope[:, i + 1] = x * indicator
    
    break_indices = np.array(relevant_cols)
    
    return X_slope, break_indices


def compute_bic(
    residuals: np.ndarray,
    n_params: int,
    T: int
) -> float:
    """
    Compute the Bayesian Information Criterion (BIC).
    
    Following Equation (8) from Schmidt and Schweikert (2021):
    BIC(λ) = log(SSR/T) + log(T)/T * df
    
    Parameters
    ----------
    residuals : np.ndarray
        Model residuals.
    n_params : int
        Number of non-zero parameters (degrees of freedom).
    T : int
        Sample size.
        
    Returns
    -------
    float
        BIC value.
    """
    ssr = np.sum(residuals ** 2)
    rss_mean = ssr / T
    
    if rss_mean <= 0:
        return np.inf
    
    bic = np.log(rss_mean) + (np.log(T) / T) * n_params
    
    return bic


def compute_modified_bic(
    residuals: np.ndarray,
    n_params: int,
    T: int,
    n_total_params: int
) -> float:
    """
    Compute the modified BIC for diverging number of parameters.
    
    Following Equation (11) from Schmidt and Schweikert (2021),
    based on Wang, Li & Leng (2009):
    BIC*(λ) = log(SSR/T) + log(T)/T * df * log(log(d*_T))
    
    Parameters
    ----------
    residuals : np.ndarray
        Model residuals.
    n_params : int
        Number of non-zero parameters.
    T : int
        Sample size.
    n_total_params : int
        Total number of potential parameters (d*_T).
        
    Returns
    -------
    float
        Modified BIC value.
    """
    ssr = np.sum(residuals ** 2)
    rss_mean = ssr / T
    
    if rss_mean <= 0:
        return np.inf
    
    # Modified penalty following Wang, Li & Leng (2009)
    log_log_d = np.log(np.log(max(n_total_params, 3)))
    penalty = (np.log(T) / T) * n_params * log_log_d
    
    bic_star = np.log(rss_mean) + penalty
    
    return bic_star


def dynamic_augmentation(
    x: np.ndarray,
    k: int
) -> np.ndarray:
    """
    Construct leads and lags of first-differenced regressor.
    
    Following Saikkonen (1991) and Stock and Watson (1993) for
    endogeneity correction in cointegrating regressions.
    
    Parameters
    ----------
    x : np.ndarray
        Regressor variable.
    k : int
        Number of leads and lags.
        
    Returns
    -------
    np.ndarray
        Matrix of shape (T, 2*k+1) containing Δx and its leads/lags.
    """
    T = len(x)
    x = np.asarray(x).flatten()
    
    # First difference
    dx = np.diff(x)
    dx = np.concatenate([[0], dx])  # Pad with zero at the beginning
    
    if k == 0:
        return dx.reshape(-1, 1)
    
    # Create matrix for leads and lags
    z_data = np.zeros((T, 2 * k + 1))
    z_data[:, 0] = dx  # Current difference
    
    for i in range(1, k + 1):
        # Lag
        lag = np.zeros(T)
        lag[i:] = dx[:-i]
        z_data[:, 2 * i - 1] = lag
        
        # Lead
        lead = np.zeros(T)
        lead[:-i] = dx[i:]
        z_data[:, 2 * i] = lead
    
    return z_data


def hausdorff_distance(
    estimated_breaks: Union[List[float], np.ndarray],
    true_breaks: Union[List[float], np.ndarray]
) -> float:
    """
    Compute the Hausdorff distance between estimated and true break points.
    
    The Hausdorff distance measures the maximum of the supremum of distances
    from points in one set to the closest point in the other set.
    
    Parameters
    ----------
    estimated_breaks : array-like
        Estimated break fractions.
    true_breaks : array-like
        True break fractions.
        
    Returns
    -------
    float
        Hausdorff distance.
        
    Notes
    -----
    Used in Monte Carlo simulations to evaluate the accuracy of break
    date estimation (Tables 3-5 in Schmidt and Schweikert, 2021).
    """
    est = np.asarray(estimated_breaks)
    true = np.asarray(true_breaks)
    
    if len(est) == 0 and len(true) == 0:
        return 0.0
    elif len(est) == 0 or len(true) == 0:
        return np.inf
    
    # Compute directed Hausdorff distances
    def directed_hausdorff(A, B):
        """sup_{a in A} inf_{b in B} |a - b|"""
        if len(A) == 0:
            return 0.0
        return max(min(abs(a - b) for b in B) for a in A)
    
    d1 = directed_hausdorff(est, true)
    d2 = directed_hausdorff(true, est)
    
    return max(d1, d2)


def percentage_correct_estimation(
    n_estimated: int,
    n_true: int
) -> float:
    """
    Compute the percentage of correct estimation of number of breaks.
    
    Parameters
    ----------
    n_estimated : int
        Estimated number of breaks.
    n_true : int
        True number of breaks.
        
    Returns
    -------
    float
        1.0 if n_estimated == n_true, 0.0 otherwise.
    """
    return 1.0 if n_estimated == n_true else 0.0


def estimate_long_run_variance(
    residuals: np.ndarray,
    bandwidth: Optional[int] = None,
    kernel: str = 'bartlett'
) -> float:
    """
    Estimate the long-run variance using kernel-based HAC estimator.
    
    Following Phillips (1987) for bias-corrected test statistics.
    
    Parameters
    ----------
    residuals : np.ndarray
        Model residuals.
    bandwidth : int, optional
        Bandwidth for kernel estimation. If None, uses Newey-West rule.
    kernel : str, optional
        Kernel type: 'bartlett', 'parzen', or 'quadratic_spectral'.
        
    Returns
    -------
    float
        Long-run variance estimate.
    """
    T = len(residuals)
    residuals = np.asarray(residuals).flatten()
    
    # Default bandwidth using Newey-West rule
    if bandwidth is None:
        bandwidth = int(np.floor(4 * (T / 100) ** (2/9)))
    
    # Autocovariance at lag 0
    gamma_0 = np.mean(residuals ** 2)
    
    # Weighted sum of autocovariances
    weighted_sum = 0.0
    for j in range(1, bandwidth + 1):
        # Autocovariance at lag j
        gamma_j = np.mean(residuals[j:] * residuals[:-j])
        
        # Kernel weight
        if kernel == 'bartlett':
            w_j = 1 - j / (bandwidth + 1)
        elif kernel == 'parzen':
            k = j / (bandwidth + 1)
            if k <= 0.5:
                w_j = 1 - 6 * k ** 2 + 6 * k ** 3
            else:
                w_j = 2 * (1 - k) ** 3
        elif kernel == 'quadratic_spectral':
            k = j / (bandwidth + 1)
            w_j = (25 / (12 * np.pi ** 2 * k ** 2)) * (
                np.sin(6 * np.pi * k / 5) / (6 * np.pi * k / 5) - 
                np.cos(6 * np.pi * k / 5)
            )
        else:
            raise ValueError(f"Unknown kernel: {kernel}")
        
        weighted_sum += w_j * gamma_j
    
    # Long-run variance estimate
    sigma2 = gamma_0 + 2 * weighted_sum
    
    return max(sigma2, 1e-10)  # Ensure positive


def ols_estimation(
    X: np.ndarray,
    y: np.ndarray,
    return_residuals: bool = True
) -> Tuple[np.ndarray, np.ndarray, float]:
    """
    Perform OLS estimation.
    
    Parameters
    ----------
    X : np.ndarray
        Design matrix.
    y : np.ndarray
        Response vector.
    return_residuals : bool, optional
        Whether to return residuals.
        
    Returns
    -------
    coef : np.ndarray
        Coefficient estimates.
    residuals : np.ndarray
        Residuals (if return_residuals is True).
    ssr : float
        Sum of squared residuals.
    """
    y = np.asarray(y).flatten()
    X = np.asarray(X)
    
    # Ensure X is 2D
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    
    try:
        # Use pseudo-inverse for numerical stability
        coef, residuals, rank, s = np.linalg.lstsq(X, y, rcond=None)
    except np.linalg.LinAlgError:
        # Fallback to normal equations with regularization
        XtX = X.T @ X
        Xty = X.T @ y
        if XtX.ndim == 0:
            # Scalar case
            coef = np.array([Xty / (XtX + 1e-10)])
        else:
            coef = np.linalg.solve(XtX + 1e-10 * np.eye(XtX.shape[0]), Xty)
    
    # Compute residuals
    y_hat = X @ coef
    residuals = y - y_hat
    ssr = np.sum(residuals ** 2)
    
    if return_residuals:
        return coef, residuals, ssr
    return coef, None, ssr


def check_rank(X: np.ndarray, tol: float = 1e-10) -> int:
    """
    Check the numerical rank of a matrix.
    
    Parameters
    ----------
    X : np.ndarray
        Matrix to check.
    tol : float, optional
        Tolerance for determining rank.
        
    Returns
    -------
    int
        Numerical rank of X.
    """
    s = np.linalg.svd(X, compute_uv=False)
    return np.sum(s > tol * s[0])


def group_adjacent_breaks(
    break_indices: np.ndarray,
    coefficients: np.ndarray,
    min_distance: int = 1
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Group adjacent break points and select the one with largest coefficient.
    
    This is used in post-lasso selection to avoid singularity issues
    when break dates are too close together.
    
    Parameters
    ----------
    break_indices : np.ndarray
        Break point indices.
    coefficients : np.ndarray
        Corresponding coefficient estimates.
    min_distance : int, optional
        Minimum distance between breaks.
        
    Returns
    -------
    selected_indices : np.ndarray
        Selected break indices.
    selected_coefs : np.ndarray
        Corresponding coefficients.
    """
    if len(break_indices) <= 1:
        return break_indices, coefficients
    
    # Sort by index
    sort_idx = np.argsort(break_indices)
    sorted_indices = break_indices[sort_idx]
    sorted_coefs = coefficients[sort_idx]
    
    # Group adjacent breaks
    groups = []
    current_group = [(sorted_indices[0], sorted_coefs[0])]
    
    for i in range(1, len(sorted_indices)):
        if sorted_indices[i] - sorted_indices[i-1] <= min_distance:
            current_group.append((sorted_indices[i], sorted_coefs[i]))
        else:
            groups.append(current_group)
            current_group = [(sorted_indices[i], sorted_coefs[i])]
    groups.append(current_group)
    
    # Select break with largest absolute coefficient from each group
    selected_indices = []
    selected_coefs = []
    
    for group in groups:
        max_idx = np.argmax([abs(c) for _, c in group])
        selected_indices.append(group[max_idx][0])
        selected_coefs.append(group[max_idx][1])
    
    return np.array(selected_indices), np.array(selected_coefs)
