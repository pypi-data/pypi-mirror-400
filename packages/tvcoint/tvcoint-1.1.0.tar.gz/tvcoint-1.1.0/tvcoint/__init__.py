"""
tvcoint: Time-Varying Cointegration Analysis in Python
=======================================================

A comprehensive Python library implementing the time-varying cointegration 
framework of Bierens and Martins (2010) from Econometric Theory.

This library provides:
- Time-varying VECM estimation using Chebyshev time polynomials
- Likelihood ratio test for time-invariant vs. time-varying cointegration
- Bootstrap tests for TVC (Martins, 2016): wild and i.i.d. bootstrap
- Standard Johansen cointegration analysis
- Critical values (asymptotic and Monte Carlo simulated)
- Tools for simulation and analysis

Main Classes
------------
JohansenVECM : Standard Johansen VECM estimation (null hypothesis, m=0)
TimeVaryingVECM : Time-varying VECM estimation (alternative, m>0)
TVCointegrationTestResult : Container for asymptotic test results
BootstrapTVCTestResult : Container for bootstrap test results

Main Functions
--------------
lr_test_tv_cointegration : Perform the LR test for time-varying cointegration
bootstrap_tvc_test : Perform bootstrap test for TVC (Martins, 2016)
wild_bootstrap_tvc_test : Wild bootstrap test for TVC
iid_bootstrap_tvc_test : i.i.d. bootstrap test for TVC (Swensen, 2006)
chebyshev_polynomial : Compute Chebyshev time polynomials
construct_extended_y : Build extended regressor for TV-VECM
simulate_cointegrated_system : Simulate cointegrated processes
simulate_tv_cointegrated_system : Simulate time-varying cointegrated processes

References
----------
Bierens, H.J. and Martins, L.F. (2010). "Time-Varying Cointegration."
Econometric Theory, 26(5), 1453-1490.
doi:10.1017/S0266466609990648

Martins, L.F. (2016). "Bootstrap tests for time varying cointegration."
Econometric Reviews, DOI: 10.1080/07474938.2015.1092830

Author
------
Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/tvcoint

License
-------
MIT License
"""

__version__ = "1.1.0"
__author__ = "Dr. Merwan Roudane"
__email__ = "merwanroudane920@gmail.com"
__license__ = "MIT"

# Import main classes and functions for public API
from .chebyshev import (
    chebyshev_polynomial,
    chebyshev_polynomial_matrix,
    construct_extended_y,
    chebyshev_approximation,
    verify_orthonormality,
    construct_time_varying_beta,
    chebyshev_basis_for_estimation,
)

from .utils import (
    compute_residual_matrices,
    solve_generalized_eigenvalue,
    orthogonal_complement,
    kronecker_product,
    vec,
    unvec,
    simulate_cointegrated_system,
    simulate_tv_cointegrated_system,
    information_criteria,
    lag_matrix,
)

from .vecm import (
    JohansenVECM,
    select_lag_order,
    johansen_trace_test,
)

from .tv_vecm import (
    TimeVaryingVECM,
    select_chebyshev_order,
    estimate_tv_vecm,
)

from .tests import (
    lr_test_tv_cointegration,
    TVCointegrationTestResult,
    multiple_m_test,
    sequential_test,
    test_ppp_application,
)

from .bootstrap_tests import (
    bootstrap_tvc_test,
    wild_bootstrap_tvc_test,
    iid_bootstrap_tvc_test,
    bootstrap_multiple_m_test,
    compare_asymptotic_bootstrap,
    BootstrapTVCTestResult,
)

from .critical_values import (
    asymptotic_critical_value,
    asymptotic_p_value,
    simulate_null_distribution,
    compute_critical_value_table,
    get_size_adjusted_critical_value,
    bootstrap_p_value,
    CriticalValueCache,
    get_critical_value,
)

# Define public API
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    
    # Chebyshev polynomials
    "chebyshev_polynomial",
    "chebyshev_polynomial_matrix",
    "construct_extended_y",
    "chebyshev_approximation",
    "verify_orthonormality",
    "construct_time_varying_beta",
    "chebyshev_basis_for_estimation",
    
    # Utility functions
    "compute_residual_matrices",
    "solve_generalized_eigenvalue",
    "orthogonal_complement",
    "kronecker_product",
    "vec",
    "unvec",
    "simulate_cointegrated_system",
    "simulate_tv_cointegrated_system",
    "information_criteria",
    "lag_matrix",
    
    # VECM estimation
    "JohansenVECM",
    "select_lag_order",
    "johansen_trace_test",
    
    # Time-varying VECM
    "TimeVaryingVECM",
    "select_chebyshev_order",
    "estimate_tv_vecm",
    
    # Testing
    "lr_test_tv_cointegration",
    "TVCointegrationTestResult",
    "multiple_m_test",
    "sequential_test",
    "test_ppp_application",
    
    # Bootstrap Testing (Martins, 2016)
    "bootstrap_tvc_test",
    "wild_bootstrap_tvc_test",
    "iid_bootstrap_tvc_test",
    "bootstrap_multiple_m_test",
    "compare_asymptotic_bootstrap",
    "BootstrapTVCTestResult",
    
    # Critical values
    "asymptotic_critical_value",
    "asymptotic_p_value",
    "simulate_null_distribution",
    "compute_critical_value_table",
    "get_size_adjusted_critical_value",
    "bootstrap_p_value",
    "CriticalValueCache",
    "get_critical_value",
]


def test():
    """
    Run basic tests to verify installation.
    
    Returns
    -------
    bool
        True if all tests pass.
        
    Examples
    --------
    >>> import tvcoint
    >>> tvcoint.test()
    True
    """
    import numpy as np
    
    try:
        # Test Chebyshev polynomials
        T = 100
        P = chebyshev_polynomial_matrix(T, m=3)
        orthonormal = verify_orthonormality(P)
        assert orthonormal, "Chebyshev orthonormality test failed"
        
        # Test simulation
        Y = simulate_cointegrated_system(T=T, k=2, r=1, seed=42)
        assert Y.shape == (T, 2), "Simulation shape test failed"
        
        # Test VECM estimation
        vecm = JohansenVECM(Y, p=2, r=1)
        vecm.fit()
        assert vecm.eigenvalues is not None, "VECM estimation test failed"
        
        # Test TV-VECM estimation
        tv_vecm = TimeVaryingVECM(Y, p=2, r=1, m=1)
        tv_vecm.fit()
        assert tv_vecm.eigenvalues is not None, "TV-VECM estimation test failed"
        
        # Test LR test
        result = lr_test_tv_cointegration(Y, p=2, r=1, m=1)
        assert result.test_statistic >= 0, "LR test failed"
        
        print("All tests passed!")
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False


def info():
    """
    Print information about the tvcoint library.
    """
    print("=" * 70)
    print("tvcoint: Time-Varying Cointegration Analysis")
    print("=" * 70)
    print(f"Version: {__version__}")
    print(f"Author: {__author__}")
    print(f"Email: {__email__}")
    print(f"License: {__license__}")
    print()
    print("Reference:")
    print("  Bierens, H.J. and Martins, L.F. (2010).")
    print("  'Time-Varying Cointegration.'")
    print("  Econometric Theory, 26(5), 1453-1490.")
    print()
    print("GitHub: https://github.com/merwanroudane/tvcoint")
    print("=" * 70)
