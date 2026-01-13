"""
Adaptive Lasso Estimation for Cointegrating Regressions with Structural Breaks
===============================================================================

This module implements the adaptive lasso approach for detecting and estimating
multiple structural breaks in cointegrating regressions.

Based on Schmidt and Schweikert (2021):
"Multiple structural breaks in cointegrating regressions: A model selection approach"
Studies in Nonlinear Dynamics & Econometrics.

The implementation follows:
- Algorithm 1 (Section 2.2): Diverging number of breakpoint candidates
- Section 2.1: Known breakpoint candidates
- Theorem 1: Oracle property of the adaptive lasso estimator

Author: Dr. Merwan Roudane
"""

import numpy as np
from sklearn.linear_model import Lasso, LassoCV
from scipy import linalg
from typing import Optional, List, Tuple, Union, Dict
import warnings

from .results import BreakEstimationResult
from .utils import (
    construct_break_indicators,
    construct_design_matrix,
    construct_full_break_matrix,
    compute_bic,
    compute_modified_bic,
    dynamic_augmentation,
    ols_estimation,
    check_rank,
    group_adjacent_breaks,
)


def lasso_estimation(
    X: np.ndarray,
    y: np.ndarray,
    lambda_grid: Optional[np.ndarray] = None,
    penalty_factor: Optional[np.ndarray] = None,
    n_lambda: int = 100
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Perform lasso estimation with specified penalty factors.
    
    Parameters
    ----------
    X : np.ndarray
        Design matrix (T x p).
    y : np.ndarray
        Response vector (T,).
    lambda_grid : np.ndarray, optional
        Grid of lambda values. If None, automatically generated.
    penalty_factor : np.ndarray, optional
        Penalty factors for each coefficient (0 = no penalty).
    n_lambda : int, optional
        Number of lambda values in the grid.
        
    Returns
    -------
    coef_path : np.ndarray
        Coefficient paths (p x n_lambda).
    lambda_values : np.ndarray
        Lambda values used.
    intercepts : np.ndarray
        Intercept values for each lambda.
    """
    T, p = X.shape
    y = np.asarray(y).flatten()
    
    # Generate lambda grid (10^5 to 10^-2 as in R code)
    if lambda_grid is None:
        lambda_grid = np.logspace(5, -2, n_lambda)
    
    # Handle penalty factors by rescaling X
    if penalty_factor is None:
        penalty_factor = np.ones(p)
    
    # Identify unpenalized variables (penalty_factor = 0)
    unpenalized_mask = penalty_factor == 0
    penalized_mask = ~unpenalized_mask
    
    coef_path = np.zeros((p, len(lambda_grid)))
    intercepts = np.zeros(len(lambda_grid))
    
    for i, lam in enumerate(lambda_grid):
        # Scale penalty factors
        if np.any(penalized_mask):
            # Rescale X for weighted lasso
            X_scaled = X.copy()
            for j in range(p):
                if penalty_factor[j] > 0:
                    X_scaled[:, j] = X[:, j] / penalty_factor[j]
            
            # Fit lasso
            model = Lasso(
                alpha=lam / T,  # sklearn uses alpha * n_samples as penalty
                fit_intercept=True,
                max_iter=10000,
                tol=1e-7,
                warm_start=False
            )
            model.fit(X_scaled, y)
            
            # Rescale coefficients back
            coef = model.coef_.copy()
            for j in range(p):
                if penalty_factor[j] > 0:
                    coef[j] = coef[j] / penalty_factor[j]
            
            coef_path[:, i] = coef
            intercepts[i] = model.intercept_
        else:
            # All variables unpenalized - use OLS
            coef, _, _ = ols_estimation(np.column_stack([np.ones(T), X]), y)
            intercepts[i] = coef[0]
            coef_path[:, i] = coef[1:]
    
    return coef_path, lambda_grid, intercepts


def adaptive_lasso_estimation(
    X: np.ndarray,
    y: np.ndarray,
    initial_weights: np.ndarray,
    penalty_factor: Optional[np.ndarray] = None,
    gamma: float = 1.0,
    lambda_grid: Optional[np.ndarray] = None,
    n_lambda: int = 100
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Perform adaptive lasso estimation.
    
    Following Equation (7) from Schmidt and Schweikert (2021):
    V_T = Σ(y_t - X_t'β)² + λ Σ w^γ |β_j|
    
    where w_j = 1/|β̂_j| are the adaptive weights.
    
    Parameters
    ----------
    X : np.ndarray
        Design matrix.
    y : np.ndarray
        Response vector.
    initial_weights : np.ndarray
        Initial coefficient estimates for computing adaptive weights.
    penalty_factor : np.ndarray, optional
        Base penalty factors (0 = unpenalized, 1 = penalized).
    gamma : float, optional
        Exponent for adaptive weights (default: 1.0).
    lambda_grid : np.ndarray, optional
        Grid of lambda values.
    n_lambda : int, optional
        Number of lambda values.
        
    Returns
    -------
    coef_path : np.ndarray
        Coefficient paths.
    lambda_values : np.ndarray
        Lambda values used.
    intercepts : np.ndarray
        Intercept values.
    """
    T, p = X.shape
    y = np.asarray(y).flatten()
    
    if lambda_grid is None:
        lambda_grid = np.logspace(5, -2, n_lambda)
    
    if penalty_factor is None:
        penalty_factor = np.ones(p)
    
    # Compute adaptive weights: w_j = |1/β̂_j|^γ
    # For zero coefficients, set weight to infinity (exclude from estimation)
    adaptive_weights = np.zeros(p)
    for j in range(p):
        if penalty_factor[j] == 0:
            # Unpenalized variable
            adaptive_weights[j] = 0
        elif abs(initial_weights[j]) < 1e-10:
            # Zero initial estimate - exclude (infinite weight)
            adaptive_weights[j] = np.inf
        else:
            adaptive_weights[j] = (1.0 / abs(initial_weights[j])) ** gamma
    
    # Combined penalty factors
    combined_penalty = penalty_factor * adaptive_weights
    
    # Identify variables to exclude (infinite penalty)
    include_mask = np.isfinite(combined_penalty)
    
    if not np.any(include_mask):
        # All variables excluded
        return np.zeros((p, len(lambda_grid))), lambda_grid, np.zeros(len(lambda_grid))
    
    # Estimation with included variables only
    X_incl = X[:, include_mask]
    penalty_incl = combined_penalty[include_mask]
    
    coef_path_incl, lambda_values, intercepts = lasso_estimation(
        X_incl, y, lambda_grid, penalty_incl, n_lambda
    )
    
    # Map back to full coefficient vector
    coef_path = np.zeros((p, len(lambda_grid)))
    coef_path[include_mask, :] = coef_path_incl
    
    return coef_path, lambda_values, intercepts


def post_lasso_ols(
    X: np.ndarray,
    y: np.ndarray,
    selected_indices: np.ndarray,
    include_intercept: bool = True
) -> Tuple[np.ndarray, np.ndarray, float]:
    """
    Post-lasso OLS estimation using only selected variables.
    
    Following Belloni and Chernozhukov (2013).
    
    Parameters
    ----------
    X : np.ndarray
        Full design matrix.
    y : np.ndarray
        Response vector.
    selected_indices : np.ndarray
        Indices of selected variables.
    include_intercept : bool, optional
        Whether to include an intercept.
        
    Returns
    -------
    coef : np.ndarray
        Coefficient estimates for selected variables.
    residuals : np.ndarray
        Residuals.
    ssr : float
        Sum of squared residuals.
    """
    y = np.asarray(y).flatten()
    T = len(y)
    
    if len(selected_indices) == 0:
        # No variables selected - intercept only
        if include_intercept:
            mean_y = np.mean(y)
            residuals = y - mean_y
            return np.array([mean_y]), residuals, np.sum(residuals ** 2)
        else:
            return np.array([]), y, np.sum(y ** 2)
    
    # Build design matrix with selected variables
    X_selected = X[:, selected_indices]
    
    if include_intercept:
        X_design = np.column_stack([np.ones(T), X_selected])
    else:
        X_design = X_selected
    
    # Check rank
    if check_rank(X_design) < X_design.shape[1]:
        warnings.warn("Design matrix is rank deficient. Results may be unreliable.")
    
    # OLS estimation
    coef, residuals, ssr = ols_estimation(X_design, y)
    
    return coef, residuals, ssr


class AdaptiveLassoBreaks:
    """
    Adaptive Lasso for Multiple Structural Breaks in Cointegrating Regressions.
    
    This class implements the methodology from Schmidt and Schweikert (2021)
    for detecting and estimating multiple structural breaks in bivariate
    cointegrating regressions.
    
    Parameters
    ----------
    max_breaks : int
        Maximum number of structural breaks allowed (m* = p* in the paper).
    trim : float, optional
        Lateral trimming parameter ξ. Default is 0.05 (5%).
    min_obs : int, optional
        Minimum observations per regime. Default is 1.
    n_lambda : int, optional
        Number of lambda values in the grid. Default is 100.
    gamma : float, optional
        Exponent for adaptive lasso weights. Default is 1.0.
    penalty_type : str, optional
        Type of information criterion: 'bic' or 'bic_star'.
        Default is 'bic_star' (modified BIC for diverging parameters).
    dynamic_lags : int, optional
        Number of leads and lags for dynamic augmentation.
        Set to 0 for no augmentation. Default is 0.
        
    Attributes
    ----------
    result_ : BreakEstimationResult
        Result object after fitting.
        
    References
    ----------
    Schmidt, A. and Schweikert, K. (2021). "Multiple structural breaks in 
    cointegrating regressions: A model selection approach." 
    Studies in Nonlinear Dynamics & Econometrics.
    
    Examples
    --------
    >>> from selectbreakcoint import AdaptiveLassoBreaks
    >>> import numpy as np
    >>> 
    >>> # Generate cointegrated data with one break at t=50
    >>> T = 100
    >>> x = np.cumsum(np.random.randn(T))  # I(1) regressor
    >>> y = 2 + 2*x + np.random.randn(T) * 0.5
    >>> y[50:] += 2 + 2*x[50:]  # Break in both intercept and slope
    >>> 
    >>> # Estimate breaks
    >>> model = AdaptiveLassoBreaks(max_breaks=2)
    >>> result = model.fit(x, y)
    >>> print(result)
    """
    
    def __init__(
        self,
        max_breaks: int = 1,
        trim: float = 0.05,
        min_obs: int = 1,
        n_lambda: int = 100,
        gamma: float = 1.0,
        penalty_type: str = 'bic_star',
        dynamic_lags: int = 0
    ):
        self.max_breaks = max_breaks
        self.trim = trim
        self.min_obs = min_obs
        self.n_lambda = n_lambda
        self.gamma = gamma
        self.penalty_type = penalty_type.lower()
        self.dynamic_lags = dynamic_lags
        
        self.result_ = None
        self._fitted = False
    
    def fit(
        self,
        x: np.ndarray,
        y: np.ndarray,
        known_breaks: Optional[List[float]] = None
    ) -> BreakEstimationResult:
        """
        Fit the model and detect structural breaks.
        
        Parameters
        ----------
        x : np.ndarray
            Regressor variable (should be I(1)).
        y : np.ndarray
            Dependent variable.
        known_breaks : list, optional
            If provided, uses known breakpoint candidates instead of
            searching over all possible break dates.
            
        Returns
        -------
        BreakEstimationResult
            Result object containing estimated breaks and coefficients.
        """
        x = np.asarray(x).flatten()
        y = np.asarray(y).flatten()
        T = len(y)
        
        if len(x) != T:
            raise ValueError("x and y must have the same length")
        
        if known_breaks is not None:
            result = self._fit_known_breaks(x, y, known_breaks)
        else:
            result = self._fit_diverging_breaks(x, y)
        
        self.result_ = result
        self._fitted = True
        
        return result
    
    def _fit_known_breaks(
        self,
        x: np.ndarray,
        y: np.ndarray,
        break_fractions: List[float]
    ) -> BreakEstimationResult:
        """
        Fit model with known breakpoint candidates.
        
        Implements the method from Section 2.1.
        """
        T = len(y)
        break_fractions = np.array(break_fractions)
        n_candidates = len(break_fractions)
        
        # Construct design matrix
        X, y_vec, col_names = construct_design_matrix(
            x, y, 
            break_fractions_intercept=break_fractions.tolist(),
            break_fractions_slope=break_fractions.tolist()
        )
        
        # Add dynamic augmentation if requested
        if self.dynamic_lags > 0:
            z_data = dynamic_augmentation(x, self.dynamic_lags)
            X = np.column_stack([X, z_data])
            n_dyn = z_data.shape[1]
        else:
            n_dyn = 0
        
        # Penalty factors: don't penalize baseline and dynamic terms
        n_params = X.shape[1]
        penalty_factor = np.ones(n_params)
        penalty_factor[0] = 0  # baseline intercept
        penalty_factor[n_candidates + 1] = 0  # baseline slope
        if n_dyn > 0:
            penalty_factor[-n_dyn:] = 0  # dynamic terms
        
        # Initial OLS estimation for weights
        coef_init, _, _ = ols_estimation(X, y_vec)
        
        # Adaptive lasso estimation
        coef_path, lambda_values, intercepts = adaptive_lasso_estimation(
            X[:, 1:], y_vec,  # Exclude intercept from X (handled separately)
            initial_weights=coef_init[1:],
            penalty_factor=penalty_factor[1:],
            gamma=self.gamma,
            n_lambda=self.n_lambda
        )
        
        # Add intercepts back
        full_coef_path = np.vstack([intercepts.reshape(1, -1), coef_path])
        
        # Select optimal lambda using BIC
        best_lambda_idx = self._select_lambda_bic(full_coef_path, X, y_vec, penalty_factor)
        optimal_coef = full_coef_path[:, best_lambda_idx]
        optimal_lambda = lambda_values[best_lambda_idx]
        
        # Extract break information
        result = self._extract_results_known_breaks(
            optimal_coef, break_fractions, T, optimal_lambda,
            lambda_values[0], X, y_vec, n_dyn
        )
        
        return result
    
    def _fit_diverging_breaks(
        self,
        x: np.ndarray,
        y: np.ndarray
    ) -> BreakEstimationResult:
        """
        Fit model with diverging number of breakpoint candidates.
        
        Implements Algorithm 1 from Section 2.2:
        1. Plain lasso for initial estimation
        2. Adaptive lasso for break selection
        3. Post-lasso OLS for final estimates
        """
        T = len(y)
        
        # Trimming boundaries
        trim_low = int(np.ceil(self.trim * T))
        trim_high = int(np.floor((1 - self.trim) * T))
        
        # Step 1: Construct full design matrix with all potential breaks
        X_full, break_indices = construct_full_break_matrix(x, self.trim)
        n_potential_breaks = X_full.shape[1] - 1  # excluding baseline
        
        # Add dynamic augmentation
        if self.dynamic_lags > 0:
            z_data = dynamic_augmentation(x, self.dynamic_lags)
            X_full = np.column_stack([X_full, z_data])
            n_dyn = z_data.shape[1]
        else:
            n_dyn = 0
            z_data = np.zeros((T, 0))
        
        # Penalty factors
        n_params = X_full.shape[1]
        penalty_factor = np.ones(n_params)
        penalty_factor[0] = 0  # baseline slope
        if n_dyn > 0:
            penalty_factor[-n_dyn:] = 0
        
        # Step 1: Initial lasso estimation
        # Following Horowitz & Huang (2013) approach
        lambda_grid = np.logspace(5, -2, self.n_lambda)
        
        coef_path_init, _, intercepts_init = lasso_estimation(
            X_full, y, lambda_grid, penalty_factor, self.n_lambda
        )
        
        # Add intercepts
        full_coef_path_init = np.vstack([intercepts_init.reshape(1, -1), coef_path_init])
        X_with_intercept = np.column_stack([np.ones(T), X_full])
        
        # Select initial lambda using modified BIC
        best_init_idx = self._select_lambda_bic(
            full_coef_path_init, X_with_intercept, y, 
            np.concatenate([[0], penalty_factor]),
            use_modified=True,
            n_total=n_potential_breaks + 2
        )
        
        initial_coef = full_coef_path_init[:, best_init_idx]
        initial_lambda = lambda_grid[best_init_idx]
        
        # Identify non-zero coefficients from initial lasso
        nonzero_mask = np.abs(initial_coef[2:n_params-n_dyn+1]) > 1e-10  # slope breaks only
        nonzero_indices = np.where(nonzero_mask)[0]
        
        if len(nonzero_indices) == 0:
            # No breaks detected - return baseline model
            return self._return_no_breaks(x, y, initial_lambda, z_data)
        
        # Step 2: Adaptive lasso on selected variables
        # Build reduced design matrix
        selected_break_indices = break_indices[nonzero_indices]
        
        # Construct design with selected breaks
        X_reduced = np.column_stack([np.ones(T), x])
        for bp in selected_break_indices:
            indicator = np.zeros(T)
            indicator[bp:] = 1.0
            X_reduced = np.column_stack([
                X_reduced,
                indicator,  # intercept break
                x * indicator  # slope break
            ])
        
        if n_dyn > 0:
            X_reduced = np.column_stack([X_reduced, z_data])
        
        # Re-estimate with OLS to get weights
        coef_reduced, _, _ = ols_estimation(X_reduced, y)
        
        # Penalty for adaptive lasso
        n_reduced = X_reduced.shape[1]
        penalty_reduced = np.ones(n_reduced)
        penalty_reduced[0] = 0  # intercept
        penalty_reduced[1] = 0  # baseline slope
        if n_dyn > 0:
            penalty_reduced[-n_dyn:] = 0
        
        # Adaptive lasso weights
        adaptive_weights = np.zeros(n_reduced)
        for j in range(n_reduced):
            if penalty_reduced[j] == 0:
                adaptive_weights[j] = 0
            elif abs(coef_reduced[j]) < 1e-10:
                adaptive_weights[j] = np.inf
            else:
                adaptive_weights[j] = (1.0 / abs(coef_reduced[j])) ** self.gamma
        
        # Perform adaptive lasso
        coef_path_adapt, lambda_adapt, intercepts_adapt = adaptive_lasso_estimation(
            X_reduced[:, 1:], y,
            initial_weights=coef_reduced[1:],
            penalty_factor=penalty_reduced[1:],
            gamma=self.gamma,
            n_lambda=self.n_lambda
        )
        
        full_coef_path_adapt = np.vstack([intercepts_adapt.reshape(1, -1), coef_path_adapt])
        
        # Select lambda
        best_adapt_idx = self._select_lambda_bic(
            full_coef_path_adapt, X_reduced, y, penalty_reduced
        )
        optimal_coef = full_coef_path_adapt[:, best_adapt_idx]
        optimal_lambda = lambda_adapt[best_adapt_idx]
        
        # Step 3: Post-lasso OLS
        # Identify significant breaks (top M largest coefficients)
        n_break_params = (n_reduced - 2 - n_dyn) // 2  # number of break pairs
        slope_coef_indices = [2 + 2*i + 1 for i in range(n_break_params)]  # slope break indices
        
        slope_changes = optimal_coef[slope_coef_indices]
        abs_changes = np.abs(slope_changes)
        
        # Select top M breaks
        if len(abs_changes) > self.max_breaks:
            top_indices = np.argsort(abs_changes)[-self.max_breaks:]
            selected_break_positions = selected_break_indices[top_indices]
        else:
            # Keep all non-zero breaks
            nonzero_change_mask = abs_changes > 1e-10
            top_indices = np.where(nonzero_change_mask)[0]
            selected_break_positions = selected_break_indices[top_indices]
        
        if len(selected_break_positions) == 0:
            return self._return_no_breaks(x, y, optimal_lambda, z_data)
        
        # Sort breaks chronologically
        selected_break_positions = np.sort(selected_break_positions)
        
        # Group adjacent breaks
        selected_break_positions, _ = group_adjacent_breaks(
            selected_break_positions,
            np.ones(len(selected_break_positions)),
            min_distance=self.min_obs
        )
        
        # Build final design matrix
        X_final = np.column_stack([np.ones(T), x])
        for bp in selected_break_positions:
            indicator = np.zeros(T)
            indicator[int(bp):] = 1.0
            X_final = np.column_stack([
                X_final,
                indicator,
                x * indicator
            ])
        
        if n_dyn > 0:
            X_final = np.column_stack([X_final, z_data])
        
        # Check rank
        if check_rank(X_final[:, :-n_dyn] if n_dyn > 0 else X_final) < X_final.shape[1] - n_dyn:
            # Singular matrix - remove some breaks
            warnings.warn("Singular design matrix. Removing adjacent breaks.")
            return self._return_no_breaks(x, y, optimal_lambda, z_data, error_code=2)
        
        # Final OLS estimation
        coef_final, residuals, ssr = ols_estimation(X_final, y)
        
        # Extract results
        n_detected = len(selected_break_positions)
        break_fractions = selected_break_positions / T
        
        # Coefficient extraction
        intercept_coefs = [coef_final[0]]
        slope_coefs = [coef_final[1]]
        intercept_changes = []
        slope_changes = []
        
        for i in range(n_detected):
            idx_intercept = 2 + 2 * i
            idx_slope = 2 + 2 * i + 1
            intercept_changes.append(coef_final[idx_intercept])
            slope_changes.append(coef_final[idx_slope])
        
        # Compute BIC
        n_params_final = 2 + 2 * n_detected
        bic = compute_bic(residuals, n_params_final, T)
        
        result = BreakEstimationResult(
            n_breaks=n_detected,
            break_fractions=np.array(break_fractions),
            break_dates=selected_break_positions.astype(int),
            intercept_coefs=np.array(intercept_coefs),
            slope_coefs=np.array(slope_coefs),
            intercept_changes=np.array(intercept_changes),
            slope_changes=np.array(slope_changes),
            residuals=residuals,
            bic=bic,
            optimal_lambda=optimal_lambda,
            initial_lambda=initial_lambda,
            sample_size=T,
            method='adaptive_lasso',
            converged=True,
            error_code=0
        )
        
        return result
    
    def _select_lambda_bic(
        self,
        coef_path: np.ndarray,
        X: np.ndarray,
        y: np.ndarray,
        penalty_factor: np.ndarray,
        use_modified: bool = False,
        n_total: Optional[int] = None
    ) -> int:
        """Select optimal lambda using BIC or modified BIC."""
        T = len(y)
        n_lambda = coef_path.shape[1]
        bic_values = np.full(n_lambda, np.inf)
        
        for i in range(n_lambda):
            coef = coef_path[:, i]
            
            # Compute residuals
            y_hat = X @ coef
            residuals = y - y_hat
            
            # Count non-zero coefficients (excluding unpenalized)
            n_nonzero = np.sum((np.abs(coef) > 1e-10) & (penalty_factor > 0))
            n_baseline = np.sum(penalty_factor == 0)
            df = n_nonzero + n_baseline
            
            if df >= 0:
                if use_modified and n_total is not None:
                    bic_values[i] = compute_modified_bic(residuals, df, T, n_total)
                else:
                    bic_values[i] = compute_bic(residuals, df, T)
        
        return np.argmin(bic_values)
    
    def _return_no_breaks(
        self,
        x: np.ndarray,
        y: np.ndarray,
        optimal_lambda: float,
        z_data: np.ndarray,
        error_code: int = 1
    ) -> BreakEstimationResult:
        """Return result when no breaks are detected."""
        T = len(y)
        
        # Baseline model
        X_base = np.column_stack([np.ones(T), x])
        if z_data.shape[1] > 0:
            X_base = np.column_stack([X_base, z_data])
        
        coef, residuals, ssr = ols_estimation(X_base, y)
        bic = compute_bic(residuals, 2, T)
        
        return BreakEstimationResult(
            n_breaks=0,
            break_fractions=np.array([]),
            break_dates=np.array([]),
            intercept_coefs=np.array([coef[0]]),
            slope_coefs=np.array([coef[1]]),
            intercept_changes=np.array([]),
            slope_changes=np.array([]),
            residuals=residuals,
            bic=bic,
            optimal_lambda=optimal_lambda,
            initial_lambda=optimal_lambda,
            sample_size=T,
            method='adaptive_lasso',
            converged=True,
            error_code=error_code
        )
    
    def _extract_results_known_breaks(
        self,
        coef: np.ndarray,
        break_fractions: np.ndarray,
        T: int,
        optimal_lambda: float,
        initial_lambda: float,
        X: np.ndarray,
        y: np.ndarray,
        n_dyn: int
    ) -> BreakEstimationResult:
        """Extract results from known breaks estimation."""
        n_candidates = len(break_fractions)
        
        # Identify active breaks (non-zero coefficients)
        intercept_changes = coef[1:n_candidates+1]
        slope_changes = coef[n_candidates+2:2*n_candidates+2]
        
        # Active breaks are those with non-zero changes in either intercept or slope
        active_mask = (np.abs(intercept_changes) > 1e-10) | (np.abs(slope_changes) > 1e-10)
        active_fractions = break_fractions[active_mask]
        active_intercept_changes = intercept_changes[active_mask]
        active_slope_changes = slope_changes[active_mask]
        
        n_detected = len(active_fractions)
        
        # Compute residuals
        y_hat = X @ coef
        residuals = y - y_hat
        bic = compute_bic(residuals, 2 + 2*n_detected, T)
        
        return BreakEstimationResult(
            n_breaks=n_detected,
            break_fractions=active_fractions,
            break_dates=(active_fractions * T).astype(int),
            intercept_coefs=np.array([coef[0]]),
            slope_coefs=np.array([coef[n_candidates+1]]),
            intercept_changes=active_intercept_changes,
            slope_changes=active_slope_changes,
            residuals=residuals,
            bic=bic,
            optimal_lambda=optimal_lambda,
            initial_lambda=initial_lambda,
            sample_size=T,
            method='adaptive_lasso_known',
            converged=True,
            error_code=0
        )
    
    def predict(
        self,
        x_new: np.ndarray
    ) -> np.ndarray:
        """
        Predict y values using the fitted model.
        
        Parameters
        ----------
        x_new : np.ndarray
            New x values for prediction.
            
        Returns
        -------
        np.ndarray
            Predicted y values.
        """
        if not self._fitted:
            raise RuntimeError("Model must be fitted before prediction")
        
        x_new = np.asarray(x_new).flatten()
        T_new = len(x_new)
        result = self.result_
        
        # Get regime values
        regime_mu = result.regime_intercepts
        regime_beta = result.regime_slopes
        
        # Determine regime for each observation
        y_pred = np.zeros(T_new)
        
        if result.n_breaks == 0:
            y_pred = regime_mu[0] + regime_beta[0] * x_new
        else:
            # Scale break dates to new sample size
            scaled_breaks = result.break_dates * T_new / result.sample_size
            scaled_breaks = scaled_breaks.astype(int)
            
            for t in range(T_new):
                regime = np.searchsorted(scaled_breaks, t, side='right')
                y_pred[t] = regime_mu[regime] + regime_beta[regime] * x_new[t]
        
        return y_pred
    
    def get_residuals(self) -> np.ndarray:
        """
        Get residuals from the fitted model.
        
        Returns
        -------
        np.ndarray
            Model residuals.
        """
        if not self._fitted:
            raise RuntimeError("Model must be fitted first")
        return self.result_.residuals
