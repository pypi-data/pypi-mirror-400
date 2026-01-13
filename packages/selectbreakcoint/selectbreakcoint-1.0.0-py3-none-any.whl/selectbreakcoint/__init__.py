"""
selectbreakcoint - Multiple Structural Breaks in Cointegrating Regressions
============================================================================

A Python implementation of the adaptive lasso approach for detecting multiple 
structural breaks in cointegrating regressions, based on:

Schmidt, A. and Schweikert, K. (2021). "Multiple structural breaks in cointegrating 
regressions: A model selection approach." Studies in Nonlinear Dynamics & Econometrics.

Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/selectbreakcoint

This package provides:
- Adaptive lasso estimation for cointegrating regressions with structural breaks
- Cointegration tests allowing for multiple structural breaks
- Support for both known breakpoint candidates and unknown break dates
- Critical values from Schmidt and Schweikert (2021)

"""

__version__ = "1.0.0"
__author__ = "Dr. Merwan Roudane"
__email__ = "merwanroudane920@gmail.com"

from .adaptive_lasso import (
    AdaptiveLassoBreaks,
    lasso_estimation,
    adaptive_lasso_estimation,
    post_lasso_ols,
)

from .cointegration_tests import (
    CointegrationTest,
    adf_test,
    phillips_perron_test,
    engle_granger_test,
    gregory_hansen_test,
    hatemi_j_test,
)

from .critical_values import (
    get_critical_values,
    CRITICAL_VALUES_ADF,
    CRITICAL_VALUES_ZT,
)

from .utils import (
    construct_break_indicators,
    construct_design_matrix,
    compute_bic,
    compute_modified_bic,
    dynamic_augmentation,
    hausdorff_distance,
)

from .results import (
    BreakEstimationResult,
    CointegrationTestResult,
)

__all__ = [
    # Main classes
    "AdaptiveLassoBreaks",
    "CointegrationTest",
    "BreakEstimationResult",
    "CointegrationTestResult",
    # Estimation functions
    "lasso_estimation",
    "adaptive_lasso_estimation",
    "post_lasso_ols",
    # Test functions
    "adf_test",
    "phillips_perron_test",
    "engle_granger_test",
    "gregory_hansen_test",
    "hatemi_j_test",
    # Critical values
    "get_critical_values",
    "CRITICAL_VALUES_ADF",
    "CRITICAL_VALUES_ZT",
    # Utility functions
    "construct_break_indicators",
    "construct_design_matrix",
    "compute_bic",
    "compute_modified_bic",
    "dynamic_augmentation",
    "hausdorff_distance",
]
