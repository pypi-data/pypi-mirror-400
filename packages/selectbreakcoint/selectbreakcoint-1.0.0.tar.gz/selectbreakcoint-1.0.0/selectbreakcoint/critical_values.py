"""
Critical Values for Cointegration Tests with Structural Breaks
================================================================

Critical values from Table 1 of Schmidt and Schweikert (2021).
"Multiple structural breaks in cointegrating regressions: A model selection approach"
Studies in Nonlinear Dynamics & Econometrics.

These critical values are computed using 25,000 Monte Carlo replications.
"""

import numpy as np
from typing import Optional, Tuple, Dict

# Critical values for ADF test statistic
# Structure: CRITICAL_VALUES_ADF[max_breaks][(sample_size, significance_level)]
# Significance levels: 10%, 5%, 1%
# Sample sizes: 100, 200, 400, asymptotic (inf)

CRITICAL_VALUES_ADF: Dict[int, Dict[Tuple[int, float], float]] = {
    # m* = p* = 1 (maximum 1 break)
    1: {
        (100, 0.10): -4.02, (100, 0.05): -4.37, (100, 0.01): -5.00,
        (200, 0.10): -3.99, (200, 0.05): -4.32, (200, 0.01): -4.91,
        (400, 0.10): -3.99, (400, 0.05): -4.29, (400, 0.01): -4.88,
        (np.inf, 0.10): -3.97, (np.inf, 0.05): -4.26, (np.inf, 0.01): -4.83,
    },
    # m* = p* = 2 (maximum 2 breaks)
    2: {
        (100, 0.10): -4.68, (100, 0.05): -5.06, (100, 0.01): -5.72,
        (200, 0.10): -4.66, (200, 0.05): -4.99, (200, 0.01): -5.71,
        (400, 0.10): -4.62, (400, 0.05): -4.97, (400, 0.01): -5.57,
        (np.inf, 0.10): -4.61, (np.inf, 0.05): -4.93, (np.inf, 0.01): -5.56,
    },
    # m* = p* = 3 (maximum 3 breaks)
    3: {
        (100, 0.10): -5.19, (100, 0.05): -5.53, (100, 0.01): -6.17,
        (200, 0.10): -5.17, (200, 0.05): -5.51, (200, 0.01): -6.15,
        (400, 0.10): -5.11, (400, 0.05): -5.45, (400, 0.01): -6.10,
        (np.inf, 0.10): -5.10, (np.inf, 0.05): -5.44, (np.inf, 0.01): -6.09,
    },
    # m* = p* = 4 (maximum 4 breaks)
    4: {
        (100, 0.10): -5.56, (100, 0.05): -5.96, (100, 0.01): -6.56,
        (200, 0.10): -5.56, (200, 0.05): -5.92, (200, 0.01): -6.61,
        (400, 0.10): -5.51, (400, 0.05): -5.89, (400, 0.01): -6.51,
        (np.inf, 0.10): -5.51, (np.inf, 0.05): -5.87, (np.inf, 0.01): -6.54,
    },
    # m* = p* = 5 (maximum 5 breaks)
    5: {
        (100, 0.10): -5.87, (100, 0.05): -6.22, (100, 0.01): -6.93,
        (200, 0.10): -5.88, (200, 0.05): -6.22, (200, 0.01): -6.89,
        (400, 0.10): -5.84, (400, 0.05): -6.22, (400, 0.01): -6.83,
        (np.inf, 0.10): -5.84, (np.inf, 0.05): -6.22, (np.inf, 0.01): -6.81,
    },
    # m* = p* = 6 (maximum 6 breaks)
    6: {
        (100, 0.10): -5.90, (100, 0.05): -6.30, (100, 0.01): -7.03,
        (200, 0.10): -6.07, (200, 0.05): -6.46, (200, 0.01): -7.14,
        (400, 0.10): -6.10, (400, 0.05): -6.49, (400, 0.01): -7.15,
        (np.inf, 0.10): -6.18, (np.inf, 0.05): -6.57, (np.inf, 0.01): -7.20,
    },
}

# Critical values for Z_t (bias-corrected) test statistic
CRITICAL_VALUES_ZT: Dict[int, Dict[Tuple[int, float], float]] = {
    # m* = p* = 1 (maximum 1 break)
    1: {
        (100, 0.10): -4.18, (100, 0.05): -4.53, (100, 0.01): -5.13,
        (200, 0.10): -4.10, (200, 0.05): -4.42, (200, 0.01): -5.04,
        (400, 0.10): -4.06, (400, 0.05): -4.38, (400, 0.01): -4.92,
        (np.inf, 0.10): -4.02, (np.inf, 0.05): -4.32, (np.inf, 0.01): -4.88,
    },
    # m* = p* = 2 (maximum 2 breaks)
    2: {
        (100, 0.10): -4.93, (100, 0.05): -5.29, (100, 0.01): -5.96,
        (200, 0.10): -4.84, (200, 0.05): -5.17, (200, 0.01): -5.77,
        (400, 0.10): -4.75, (400, 0.05): -5.08, (400, 0.01): -5.72,
        (np.inf, 0.10): -4.70, (np.inf, 0.05): -5.02, (np.inf, 0.01): -5.62,
    },
    # m* = p* = 3 (maximum 3 breaks)
    3: {
        (100, 0.10): -5.52, (100, 0.05): -5.90, (100, 0.01): -6.68,
        (200, 0.10): -5.39, (200, 0.05): -5.74, (200, 0.01): -6.44,
        (400, 0.10): -5.30, (400, 0.05): -5.61, (400, 0.01): -6.23,
        (np.inf, 0.10): -5.23, (np.inf, 0.05): -5.53, (np.inf, 0.01): -6.11,
    },
    # m* = p* = 4 (maximum 4 breaks)
    4: {
        (100, 0.10): -5.99, (100, 0.05): -6.41, (100, 0.01): -7.14,
        (200, 0.10): -5.84, (200, 0.05): -6.20, (200, 0.01): -6.92,
        (400, 0.10): -5.72, (400, 0.05): -6.06, (400, 0.01): -6.71,
        (np.inf, 0.10): -5.64, (np.inf, 0.05): -5.95, (np.inf, 0.01): -6.60,
    },
    # m* = p* = 5 (maximum 5 breaks)
    5: {
        (100, 0.10): -6.29, (100, 0.05): -6.71, (100, 0.01): -7.50,
        (200, 0.10): -6.20, (200, 0.05): -6.58, (200, 0.01): -7.24,
        (400, 0.10): -6.08, (400, 0.05): -6.43, (400, 0.01): -7.12,
        (np.inf, 0.10): -6.04, (np.inf, 0.05): -6.36, (np.inf, 0.01): -6.99,
    },
    # m* = p* = 6 (maximum 6 breaks)
    6: {
        (100, 0.10): -6.45, (100, 0.05): -6.93, (100, 0.01): -7.82,
        (200, 0.10): -6.46, (200, 0.05): -6.87, (200, 0.01): -7.61,
        (400, 0.10): -6.36, (400, 0.05): -6.76, (400, 0.01): -7.44,
        (np.inf, 0.10): -6.37, (np.inf, 0.05): -6.73, (np.inf, 0.01): -7.34,
    },
}


def _find_nearest_sample_size(T: int, available_sizes: list) -> int:
    """
    Find the nearest available sample size for critical value lookup.
    
    Parameters
    ----------
    T : int
        Actual sample size.
    available_sizes : list
        List of available sample sizes in the critical value table.
        
    Returns
    -------
    int or float
        The nearest sample size from the table (uses asymptotic if T >= 400).
    """
    finite_sizes = [s for s in available_sizes if np.isfinite(s)]
    
    if T >= 400:
        return np.inf
    elif T >= 300:
        return 400
    elif T >= 150:
        return 200
    else:
        return 100


def get_critical_values(
    max_breaks: int,
    sample_size: int,
    test_type: str = "adf",
    significance_levels: Optional[list] = None
) -> Dict[float, float]:
    """
    Get critical values for the cointegration test with structural breaks.
    
    Parameters
    ----------
    max_breaks : int
        Maximum number of structural breaks allowed (1 to 6).
    sample_size : int
        Sample size for which to retrieve critical values.
    test_type : str, optional
        Type of test statistic: "adf" or "zt" (bias-corrected).
        Default is "adf".
    significance_levels : list, optional
        List of significance levels to retrieve. 
        Default is [0.10, 0.05, 0.01].
        
    Returns
    -------
    dict
        Dictionary mapping significance levels to critical values.
        
    Examples
    --------
    >>> cv = get_critical_values(max_breaks=2, sample_size=200)
    >>> print(cv)
    {0.1: -4.66, 0.05: -4.99, 0.01: -5.71}
    
    References
    ----------
    Schmidt, A. and Schweikert, K. (2021). Table 1.
    """
    if significance_levels is None:
        significance_levels = [0.10, 0.05, 0.01]
    
    if max_breaks < 1 or max_breaks > 6:
        raise ValueError("max_breaks must be between 1 and 6")
    
    test_type = test_type.lower()
    if test_type == "adf":
        cv_table = CRITICAL_VALUES_ADF
    elif test_type in ["zt", "z_t", "pp", "phillips_perron"]:
        cv_table = CRITICAL_VALUES_ZT
    else:
        raise ValueError(f"Unknown test_type: {test_type}. Use 'adf' or 'zt'.")
    
    # Find the nearest sample size
    available_sizes = list(set([k[0] for k in cv_table[max_breaks].keys()]))
    T_lookup = _find_nearest_sample_size(sample_size, available_sizes)
    
    result = {}
    for level in significance_levels:
        key = (T_lookup, level)
        if key in cv_table[max_breaks]:
            result[level] = cv_table[max_breaks][key]
        else:
            raise ValueError(f"Critical value not available for T={T_lookup}, level={level}")
    
    return result


def interpolate_critical_values(
    max_breaks: int,
    sample_size: int,
    test_type: str = "adf"
) -> Dict[float, float]:
    """
    Interpolate critical values for intermediate sample sizes.
    
    Uses linear interpolation between available sample sizes.
    
    Parameters
    ----------
    max_breaks : int
        Maximum number of structural breaks allowed.
    sample_size : int
        Sample size for which to interpolate critical values.
    test_type : str, optional
        Type of test statistic: "adf" or "zt".
        
    Returns
    -------
    dict
        Dictionary mapping significance levels to interpolated critical values.
    """
    test_type = test_type.lower()
    if test_type == "adf":
        cv_table = CRITICAL_VALUES_ADF
    elif test_type in ["zt", "z_t"]:
        cv_table = CRITICAL_VALUES_ZT
    else:
        raise ValueError(f"Unknown test_type: {test_type}")
    
    # Available sample sizes (finite only for interpolation)
    sizes = [100, 200, 400]
    levels = [0.10, 0.05, 0.01]
    
    result = {}
    
    for level in levels:
        # Get critical values at each sample size
        cvs = [cv_table[max_breaks][(s, level)] for s in sizes]
        
        # Use asymptotic for very large samples
        if sample_size >= 400:
            result[level] = cv_table[max_breaks][(np.inf, level)]
        elif sample_size <= 100:
            result[level] = cv_table[max_breaks][(100, level)]
        else:
            # Linear interpolation
            result[level] = np.interp(sample_size, sizes, cvs)
    
    return result


def print_critical_values_table(max_breaks: int, test_type: str = "adf"):
    """
    Print the critical values table for a given maximum number of breaks.
    
    Parameters
    ----------
    max_breaks : int
        Maximum number of structural breaks.
    test_type : str, optional
        Type of test: "adf" or "zt".
    """
    test_type = test_type.lower()
    if test_type == "adf":
        cv_table = CRITICAL_VALUES_ADF
        test_name = "ADF"
    else:
        cv_table = CRITICAL_VALUES_ZT
        test_name = "Z_t"
    
    print(f"\nCritical Values for {test_name} Test with m* = p* = {max_breaks}")
    print("=" * 60)
    print(f"{'T':<10} {'10%':<12} {'5%':<12} {'1%':<12}")
    print("-" * 60)
    
    for T in [100, 200, 400, np.inf]:
        T_str = "∞" if np.isinf(T) else str(int(T))
        cv_10 = cv_table[max_breaks][(T, 0.10)]
        cv_05 = cv_table[max_breaks][(T, 0.05)]
        cv_01 = cv_table[max_breaks][(T, 0.01)]
        print(f"{T_str:<10} {cv_10:<12.2f} {cv_05:<12.2f} {cv_01:<12.2f}")
    
    print("-" * 60)
