"""
Likelihood Ratio Test for Time-Varying Cointegration
=====================================================

Implementation of the LR test proposed in Bierens and Martins (2010) to test
the null hypothesis of time-invariant (standard) cointegration against the
alternative of time-varying cointegration.

The test statistic is (equation 6):
    LR^{tvc} = T * Σ_{j=1}^{r} ln((1 - λ̂_{0,j}) / (1 - λ̂_{m,j}))

where:
    - λ̂_{0,j} are eigenvalues from standard Johansen estimation (m=0)
    - λ̂_{m,j} are eigenvalues from TV-VECM estimation with order m

Under the null hypothesis of time-invariant cointegration (Theorem 1):
    LR^{tvc} →^d χ²_{mkr}

Reference:
    Bierens, H.J. and Martins, L.F. (2010). "Time-Varying Cointegration."
    Econometric Theory, 26(5), 1453-1490.
"""

import numpy as np
from scipy import stats
from scipy import linalg
from typing import Tuple, Optional, Dict, Any, Union
from numpy.typing import NDArray
import warnings
from dataclasses import dataclass

from .vecm import JohansenVECM
from .tv_vecm import TimeVaryingVECM
from .chebyshev import construct_extended_y


@dataclass
class TVCointegrationTestResult:
    """
    Results container for the time-varying cointegration test.
    
    Attributes
    ----------
    test_statistic : float
        The LR test statistic LR^{tvc}.
    p_value : float
        Asymptotic p-value from χ²_{mkr} distribution.
    degrees_of_freedom : int
        Degrees of freedom (m × k × r).
    critical_value_5pct : float
        5% critical value from χ²_{mkr}.
    critical_value_1pct : float
        1% critical value from χ²_{mkr}.
    reject_null : bool
        Whether to reject H_0 at 5% significance.
    m : int
        Chebyshev order used in the test.
    k : int
        Number of variables.
    r : int
        Cointegration rank.
    eigenvalues_m0 : ndarray
        Eigenvalues from standard VECM (m=0).
    eigenvalues_m : ndarray
        Eigenvalues from TV-VECM (m>0).
    log_likelihood_m0 : float
        Log-likelihood under H_0 (m=0).
    log_likelihood_m : float
        Log-likelihood under H_1 (m>0).
    T : int
        Sample size.
    p : int
        Lag order.
    """
    test_statistic: float
    p_value: float
    degrees_of_freedom: int
    critical_value_5pct: float
    critical_value_1pct: float
    critical_value_10pct: float
    reject_null_5pct: bool
    reject_null_1pct: bool
    reject_null_10pct: bool
    m: int
    k: int
    r: int
    eigenvalues_m0: NDArray
    eigenvalues_m: NDArray
    log_likelihood_m0: float
    log_likelihood_m: float
    T: int
    p: int
    
    def __str__(self) -> str:
        """Generate formatted string representation."""
        lines = []
        lines.append("=" * 70)
        lines.append("Time-Varying Cointegration Test")
        lines.append("Bierens and Martins (2010)")
        lines.append("=" * 70)
        lines.append("")
        lines.append("Hypotheses:")
        lines.append("  H_0: Time-invariant cointegration (ξ_1 = ... = ξ_m = 0)")
        lines.append("  H_1: Time-varying cointegration (some ξ_i ≠ 0 for i ≥ 1)")
        lines.append("")
        lines.append("-" * 70)
        lines.append("Test Specification:")
        lines.append(f"  Sample size (T):            {self.T}")
        lines.append(f"  Number of variables (k):    {self.k}")
        lines.append(f"  Cointegration rank (r):     {self.r}")
        lines.append(f"  Lag order (p):              {self.p}")
        lines.append(f"  Chebyshev order (m):        {self.m}")
        lines.append(f"  Degrees of freedom:         {self.degrees_of_freedom}")
        lines.append("")
        lines.append("-" * 70)
        lines.append("Test Results:")
        lines.append(f"  LR test statistic:          {self.test_statistic:.4f}")
        lines.append(f"  p-value:                    {self.p_value:.6f}")
        lines.append("")
        lines.append("  Critical values:")
        lines.append(f"    10% level:                {self.critical_value_10pct:.4f}")
        lines.append(f"    5% level:                 {self.critical_value_5pct:.4f}")
        lines.append(f"    1% level:                 {self.critical_value_1pct:.4f}")
        lines.append("")
        lines.append("  Decision:")
        lines.append(f"    Reject H_0 at 10%:        {'Yes' if self.reject_null_10pct else 'No'}")
        lines.append(f"    Reject H_0 at 5%:         {'Yes' if self.reject_null_5pct else 'No'}")
        lines.append(f"    Reject H_0 at 1%:         {'Yes' if self.reject_null_1pct else 'No'}")
        lines.append("")
        lines.append("-" * 70)
        lines.append("Model Comparison:")
        lines.append(f"  Log-likelihood (m=0):       {self.log_likelihood_m0:.4f}")
        lines.append(f"  Log-likelihood (m={self.m}):       {self.log_likelihood_m:.4f}")
        lines.append("")
        lines.append("  Eigenvalues comparison:")
        lines.append("    j    λ̂(m=0)      λ̂(m={})      Ratio".format(self.m))
        for j in range(min(self.r, 5)):  # Show first 5
            ev0 = self.eigenvalues_m0[j] if j < len(self.eigenvalues_m0) else np.nan
            evm = self.eigenvalues_m[j] if j < len(self.eigenvalues_m) else np.nan
            ratio = (1 - ev0) / (1 - evm) if (1 - evm) > 1e-10 else np.nan
            lines.append(f"    {j+1}    {ev0:.6f}    {evm:.6f}    {ratio:.6f}")
        if self.r > 5:
            lines.append(f"    ... ({self.r - 5} more)")
        lines.append("")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'test_statistic': self.test_statistic,
            'p_value': self.p_value,
            'degrees_of_freedom': self.degrees_of_freedom,
            'critical_value_5pct': self.critical_value_5pct,
            'critical_value_1pct': self.critical_value_1pct,
            'critical_value_10pct': self.critical_value_10pct,
            'reject_null_5pct': self.reject_null_5pct,
            'reject_null_1pct': self.reject_null_1pct,
            'reject_null_10pct': self.reject_null_10pct,
            'm': self.m,
            'k': self.k,
            'r': self.r,
            'eigenvalues_m0': self.eigenvalues_m0,
            'eigenvalues_m': self.eigenvalues_m,
            'log_likelihood_m0': self.log_likelihood_m0,
            'log_likelihood_m': self.log_likelihood_m,
            'T': self.T,
            'p': self.p
        }


def lr_test_tv_cointegration(
    Y: NDArray,
    r: int,
    m: int,
    p: int = 1,
    include_intercept: bool = True
) -> TVCointegrationTestResult:
    """
    Perform the Bierens-Martins LR test for time-varying cointegration.
    
    Tests the null hypothesis of time-invariant cointegration against the
    alternative of time-varying cointegration using the LR statistic from
    equation (6) of Bierens and Martins (2010):
    
        LR^{tvc} = T * Σ_{j=1}^{r} ln((1 - λ̂_{0,j}) / (1 - λ̂_{m,j}))
    
    Under H_0, this statistic is asymptotically χ²_{mkr} distributed (Theorem 1).
    
    Parameters
    ----------
    Y : ndarray of shape (T, k)
        The k-variate time series data.
    r : int
        Cointegration rank (assumed known, 0 < r < k).
    m : int
        Chebyshev polynomial order for the alternative (m ≥ 1).
    p : int, optional
        Lag order for the VECM (default: 1).
    include_intercept : bool, optional
        Whether to include an intercept (default: True).
        
    Returns
    -------
    result : TVCointegrationTestResult
        Test results including statistic, p-value, and critical values.
        
    Notes
    -----
    - The cointegration rank r must be known or pre-determined.
    - For m = 0, the test is not defined (trivially zero).
    - The test is one-sided: reject H_0 for large values of LR^{tvc}.
    - According to Section 3.4, there may be size distortion in small samples.
    
    Examples
    --------
    >>> import numpy as np
    >>> from tvcoint import lr_test_tv_cointegration
    >>> # Generate cointegrated data
    >>> T, k = 200, 2
    >>> Y = np.cumsum(np.random.randn(T, k), axis=0)
    >>> Y[:, 1] = Y[:, 0] + np.random.randn(T) * 0.5
    >>> # Test for time-varying cointegration
    >>> result = lr_test_tv_cointegration(Y, r=1, m=2, p=2)
    >>> print(result)
    
    References
    ----------
    Bierens, H.J. and Martins, L.F. (2010). "Time-Varying Cointegration."
    Econometric Theory, 26(5), 1453-1490.
    """
    Y = np.asarray(Y, dtype=np.float64)
    
    if Y.ndim != 2:
        raise ValueError(f"Y must be 2-dimensional, got {Y.ndim}")
    
    T, k = Y.shape
    
    # Input validation
    if r < 1 or r >= k:
        raise ValueError(f"Cointegration rank r={r} must satisfy 0 < r < k={k}")
    if m < 1:
        raise ValueError(f"Chebyshev order m={m} must be at least 1 for the test")
    if p < 1:
        raise ValueError(f"Lag order p={p} must be at least 1")
    
    # Check sample size
    min_T = max(k * (m + 1) + p + 10, 2 * k * (m + 1))
    if T < min_T:
        warnings.warn(
            f"Sample size T={T} may be too small for k={k}, m={m}, p={p}. "
            f"Recommended T >= {min_T}"
        )
    
    # Step 1: Estimate standard VECM (m=0)
    model_m0 = JohansenVECM(p=p, include_intercept=include_intercept)
    model_m0.fit(Y, r=r)
    
    # Step 2: Estimate time-varying VECM (m>0)
    model_m = TimeVaryingVECM(p=p, m=m, include_intercept=include_intercept)
    model_m.fit(Y, r=r)
    
    # Step 3: Compute LR test statistic - equation (6)
    # LR^{tvc} = T * Σ_{j=1}^{r} ln((1 - λ̂_{0,j}) / (1 - λ̂_{m,j}))
    T_eff = T - p
    
    eigenvalues_m0 = model_m0.eigenvalues[:r]
    eigenvalues_m = model_m.eigenvalues[:r]
    
    # Ensure eigenvalues are in valid range
    eigenvalues_m0 = np.clip(eigenvalues_m0, 1e-14, 1 - 1e-14)
    eigenvalues_m = np.clip(eigenvalues_m, 1e-14, 1 - 1e-14)
    
    # Compute LR statistic
    log_ratio = np.log((1 - eigenvalues_m0) / (1 - eigenvalues_m))
    lr_statistic = T_eff * np.sum(log_ratio)
    
    # Ensure non-negative (should be by construction, but numerical issues)
    lr_statistic = max(0, lr_statistic)
    
    # Step 4: Compute p-value and critical values
    # Degrees of freedom: m × k × r (Theorem 1)
    df = m * k * r
    
    # P-value from chi-square distribution
    p_value = 1 - stats.chi2.cdf(lr_statistic, df)
    
    # Critical values
    cv_10pct = stats.chi2.ppf(0.90, df)
    cv_5pct = stats.chi2.ppf(0.95, df)
    cv_1pct = stats.chi2.ppf(0.99, df)
    
    # Decision
    reject_10pct = lr_statistic > cv_10pct
    reject_5pct = lr_statistic > cv_5pct
    reject_1pct = lr_statistic > cv_1pct
    
    # Create result object
    result = TVCointegrationTestResult(
        test_statistic=lr_statistic,
        p_value=p_value,
        degrees_of_freedom=df,
        critical_value_5pct=cv_5pct,
        critical_value_1pct=cv_1pct,
        critical_value_10pct=cv_10pct,
        reject_null_5pct=reject_5pct,
        reject_null_1pct=reject_1pct,
        reject_null_10pct=reject_10pct,
        m=m,
        k=k,
        r=r,
        eigenvalues_m0=eigenvalues_m0,
        eigenvalues_m=eigenvalues_m,
        log_likelihood_m0=model_m0.log_likelihood,
        log_likelihood_m=model_m.log_likelihood,
        T=T,
        p=p
    )
    
    return result


def multiple_m_test(
    Y: NDArray,
    r: int,
    m_values: Union[int, list] = 5,
    p: int = 1,
    include_intercept: bool = True,
    bonferroni_correction: bool = True
) -> Dict[str, Any]:
    """
    Perform the TV cointegration test for multiple values of m.
    
    This function helps in selecting the appropriate Chebyshev order by
    testing across multiple values of m.
    
    Parameters
    ----------
    Y : ndarray of shape (T, k)
        The k-variate time series data.
    r : int
        Cointegration rank.
    m_values : int or list
        If int: test for m = 1, 2, ..., m_values.
        If list: test for each m in the list.
    p : int
        Lag order.
    include_intercept : bool
        Whether to include intercept.
    bonferroni_correction : bool
        Whether to apply Bonferroni correction for multiple testing.
        
    Returns
    -------
    dict with keys:
        'results' : list of TVCointegrationTestResult for each m
        'min_p_value' : Minimum p-value across all tests
        'min_p_value_m' : m value achieving minimum p-value
        'bonferroni_p_value' : Bonferroni-corrected minimum p-value
        'any_reject_5pct' : Whether any test rejects at 5%
        'summary' : Summary DataFrame
    """
    Y = np.asarray(Y, dtype=np.float64)
    T, k = Y.shape
    
    if isinstance(m_values, int):
        m_list = list(range(1, m_values + 1))
    else:
        m_list = list(m_values)
    
    # Filter out m values that are too large for sample size
    valid_m = [m for m in m_list if T >= k * (m + 1) + p + 10]
    if len(valid_m) == 0:
        raise ValueError("Sample size too small for any m value")
    
    if len(valid_m) < len(m_list):
        warnings.warn(
            f"Some m values removed due to sample size constraints. "
            f"Testing m = {valid_m}"
        )
    
    results = []
    for m in valid_m:
        try:
            result = lr_test_tv_cointegration(
                Y, r=r, m=m, p=p, include_intercept=include_intercept
            )
            results.append(result)
        except Exception as e:
            warnings.warn(f"Test failed for m={m}: {str(e)}")
    
    if len(results) == 0:
        raise RuntimeError("All tests failed")
    
    # Find minimum p-value
    p_values = [r.p_value for r in results]
    min_idx = np.argmin(p_values)
    min_p_value = p_values[min_idx]
    min_p_value_m = results[min_idx].m
    
    # Bonferroni correction
    n_tests = len(results)
    bonferroni_p_value = min(min_p_value * n_tests, 1.0)
    
    # Any rejection?
    any_reject = any(r.reject_null_5pct for r in results)
    any_reject_bonf = bonferroni_p_value < 0.05
    
    # Create summary
    summary_data = []
    for r in results:
        summary_data.append({
            'm': r.m,
            'LR_stat': r.test_statistic,
            'df': r.degrees_of_freedom,
            'p_value': r.p_value,
            'CV_5pct': r.critical_value_5pct,
            'reject': r.reject_null_5pct
        })
    
    return {
        'results': results,
        'min_p_value': min_p_value,
        'min_p_value_m': min_p_value_m,
        'bonferroni_p_value': bonferroni_p_value if bonferroni_correction else min_p_value,
        'any_reject_5pct': any_reject,
        'any_reject_bonferroni': any_reject_bonf if bonferroni_correction else any_reject,
        'summary': summary_data,
        'n_tests': n_tests
    }


def sequential_test(
    Y: NDArray,
    r: int,
    max_m: int = 5,
    p: int = 1,
    include_intercept: bool = True,
    alpha: float = 0.05
) -> Dict[str, Any]:
    """
    Perform sequential testing to determine the optimal Chebyshev order.
    
    Tests H_0(m=1) against H_1(m=2), then H_0(m=2) against H_1(m=3), etc.
    Stops when the test no longer rejects.
    
    Parameters
    ----------
    Y : ndarray of shape (T, k)
        The k-variate time series data.
    r : int
        Cointegration rank.
    max_m : int
        Maximum m to consider.
    p : int
        Lag order.
    include_intercept : bool
        Whether to include intercept.
    alpha : float
        Significance level.
        
    Returns
    -------
    dict with keys:
        'selected_m' : Selected Chebyshev order
        'test_sequence' : List of test results
        'first_non_rejection_m' : First m where H_0 is not rejected
    """
    Y = np.asarray(Y, dtype=np.float64)
    T, k = Y.shape
    
    test_sequence = []
    selected_m = 0  # Default: time-invariant
    
    for m in range(1, max_m + 1):
        # Check feasibility
        if T < k * (m + 1) + p + 10:
            break
        
        try:
            result = lr_test_tv_cointegration(
                Y, r=r, m=m, p=p, include_intercept=include_intercept
            )
            test_sequence.append(result)
            
            if result.p_value < alpha:
                selected_m = m  # Evidence of time-variation up to order m
            else:
                break  # Stop at first non-rejection
                
        except Exception as e:
            warnings.warn(f"Test failed for m={m}: {str(e)}")
            break
    
    return {
        'selected_m': selected_m,
        'test_sequence': test_sequence,
        'first_non_rejection_m': selected_m + 1 if test_sequence else 1
    }


def test_ppp_application(
    S: NDArray,
    P_domestic: NDArray,
    P_foreign: NDArray,
    m: int = 1,
    p: int = 2,
    include_intercept: bool = True
) -> Dict[str, Any]:
    """
    Apply the TV cointegration test to PPP (Purchasing Power Parity) hypothesis.
    
    Tests whether the PPP relationship between exchange rates and price levels
    exhibits time-varying cointegration, as in Section 6 of the paper.
    
    The trivariate system is: Y_t = (ln S_t, ln P^n_t, ln P^f_t)'
    
    Parameters
    ----------
    S : ndarray of shape (T,)
        Nominal exchange rate (domestic currency per unit of foreign currency).
    P_domestic : ndarray of shape (T,)
        Domestic price index.
    P_foreign : ndarray of shape (T,)
        Foreign price index.
    m : int
        Chebyshev order.
    p : int
        Lag order.
    include_intercept : bool
        Whether to include intercept.
        
    Returns
    -------
    dict with keys:
        'test_result' : TVCointegrationTestResult
        'time_varying_beta' : Time-varying cointegrating vectors
        'ppp_deviations' : β'_t Y_{t-1} (equilibrium errors)
        'summary' : Formatted summary string
    """
    S = np.asarray(S, dtype=np.float64).flatten()
    P_domestic = np.asarray(P_domestic, dtype=np.float64).flatten()
    P_foreign = np.asarray(P_foreign, dtype=np.float64).flatten()
    
    T = len(S)
    
    if len(P_domestic) != T or len(P_foreign) != T:
        raise ValueError("All series must have the same length")
    
    # Construct Y = (ln S, ln P_domestic, ln P_foreign)
    Y = np.column_stack([
        np.log(S),
        np.log(P_domestic),
        np.log(P_foreign)
    ])
    
    # Test with r=1 (PPP implies one cointegrating relationship)
    test_result = lr_test_tv_cointegration(
        Y, r=1, m=m, p=p, include_intercept=include_intercept
    )
    
    # Estimate TV-VECM to get time-varying beta
    tv_model = TimeVaryingVECM(p=p, m=m, include_intercept=include_intercept)
    tv_model.fit(Y, r=1)
    
    # Compute PPP deviations (equilibrium errors)
    ppp_deviations = np.zeros(T - 1)
    for t in range(1, T):
        beta_t = tv_model.beta_t[t, :, 0]  # Cointegrating vector at time t
        ppp_deviations[t-1] = np.dot(beta_t, Y[t-1, :])
    
    # Summary
    summary_lines = []
    summary_lines.append("=" * 70)
    summary_lines.append("PPP Time-Varying Cointegration Analysis")
    summary_lines.append("=" * 70)
    summary_lines.append(f"Sample size: {T}")
    summary_lines.append(f"Variables: ln(S), ln(P_domestic), ln(P_foreign)")
    summary_lines.append("")
    summary_lines.append(str(test_result))
    summary_lines.append("")
    summary_lines.append("Interpretation:")
    if test_result.reject_null_5pct:
        summary_lines.append("  Evidence of TIME-VARYING PPP relationship")
        summary_lines.append("  The cointegrating vector changes over time")
    else:
        summary_lines.append("  No evidence against STANDARD PPP relationship")
        summary_lines.append("  Time-invariant cointegration cannot be rejected")
    summary_lines.append("=" * 70)
    
    return {
        'test_result': test_result,
        'time_varying_beta': tv_model.beta_t,
        'ppp_deviations': ppp_deviations,
        'tv_model': tv_model,
        'summary': "\n".join(summary_lines)
    }
