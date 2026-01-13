"""
Bootstrap Tests for Time-Varying Cointegration
================================================

Implementation of the bootstrap tests proposed in Martins (2016) for testing
the null hypothesis of time-invariant (standard) cointegration against the
alternative of time-varying cointegration.

Two bootstrap methods are provided:
1. Wild Bootstrap (Cavaliere et al., 2010a): Better under conditional heteroskedasticity
2. i.i.d. Bootstrap (Swensen, 2006): Standard parametric bootstrap

Both methods can use either:
- Unrestricted residuals: from the TVC model (m > 0)
- Restricted residuals: from the standard VECM (m = 0)

The bootstrap tests share the same first-order asymptotic chi-square distribution
as the original LR test under the null hypothesis, but provide better finite-sample
size properties.

References
----------
Martins, L.F. (2016). "Bootstrap tests for time varying cointegration."
Econometric Reviews, DOI: 10.1080/07474938.2015.1092830

Bierens, H.J. and Martins, L.F. (2010). "Time-Varying Cointegration."
Econometric Theory, 26(5), 1453-1490.

Cavaliere, G., Rahbek, A., Taylor, A.M.R. (2010a). "Cointegration rank testing
under conditional heteroskedasticity." Econometric Theory 26:1719-1760.

Swensen, A.R. (2006). "Bootstrap algorithms for testing and determining the
cointegration rank in VAR Models." Econometrica 74:1699-1714.
"""

import numpy as np
from scipy import stats
from scipy import linalg
from typing import Tuple, Optional, Dict, Any, Union, Literal
from numpy.typing import NDArray
import warnings
from dataclasses import dataclass

from .vecm import JohansenVECM
from .tv_vecm import TimeVaryingVECM
from .chebyshev import construct_extended_y
from .utils import compute_residual_matrices, solve_generalized_eigenvalue


@dataclass
class BootstrapTVCTestResult:
    """
    Results container for the bootstrap time-varying cointegration test.
    
    Attributes
    ----------
    test_statistic : float
        The LR test statistic LR^{tvc}.
    bootstrap_p_value : float
        P-value from bootstrap distribution.
    asymptotic_p_value : float
        Asymptotic p-value from χ²_{mkr} distribution.
    bootstrap_critical_value_5pct : float
        5% critical value from bootstrap distribution.
    bootstrap_critical_value_1pct : float
        1% critical value from bootstrap distribution.
    bootstrap_critical_value_10pct : float
        10% critical value from bootstrap distribution.
    reject_null_5pct : bool
        Whether to reject H_0 at 5% significance (using bootstrap CV).
    reject_null_1pct : bool
        Whether to reject H_0 at 1% significance (using bootstrap CV).
    reject_null_10pct : bool
        Whether to reject H_0 at 10% significance (using bootstrap CV).
    bootstrap_method : str
        Bootstrap method used ('wild' or 'iid').
    residual_type : str
        Type of residuals used ('unrestricted' or 'restricted').
    n_bootstrap : int
        Number of bootstrap replications.
    bootstrap_statistics : ndarray
        Array of bootstrap test statistics.
    m : int
        Chebyshev order used in the test.
    k : int
        Number of variables.
    r : int
        Cointegration rank.
    degrees_of_freedom : int
        Degrees of freedom (m × k × r).
    T : int
        Sample size.
    p : int
        Lag order.
    """
    test_statistic: float
    bootstrap_p_value: float
    asymptotic_p_value: float
    bootstrap_critical_value_5pct: float
    bootstrap_critical_value_1pct: float
    bootstrap_critical_value_10pct: float
    reject_null_5pct: bool
    reject_null_1pct: bool
    reject_null_10pct: bool
    bootstrap_method: str
    residual_type: str
    n_bootstrap: int
    bootstrap_statistics: NDArray
    m: int
    k: int
    r: int
    degrees_of_freedom: int
    T: int
    p: int
    
    def __str__(self) -> str:
        """Generate formatted string representation."""
        lines = []
        lines.append("=" * 70)
        lines.append("Bootstrap Test for Time-Varying Cointegration")
        lines.append("Martins (2016)")
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
        lines.append("Bootstrap Configuration:")
        lines.append(f"  Bootstrap method:           {self.bootstrap_method.upper()}")
        lines.append(f"  Residual type:              {self.residual_type}")
        lines.append(f"  Number of replications:     {self.n_bootstrap}")
        lines.append("")
        lines.append("-" * 70)
        lines.append("Test Results:")
        lines.append(f"  LR test statistic:          {self.test_statistic:.4f}")
        lines.append(f"  Bootstrap p-value:          {self.bootstrap_p_value:.6f}")
        lines.append(f"  Asymptotic p-value:         {self.asymptotic_p_value:.6f}")
        lines.append("")
        lines.append("  Bootstrap critical values:")
        lines.append(f"    10% level:                {self.bootstrap_critical_value_10pct:.4f}")
        lines.append(f"    5% level:                 {self.bootstrap_critical_value_5pct:.4f}")
        lines.append(f"    1% level:                 {self.bootstrap_critical_value_1pct:.4f}")
        lines.append("")
        lines.append("  Decision (using bootstrap CVs):")
        lines.append(f"    Reject H_0 at 10%:        {'Yes' if self.reject_null_10pct else 'No'}")
        lines.append(f"    Reject H_0 at 5%:         {'Yes' if self.reject_null_5pct else 'No'}")
        lines.append(f"    Reject H_0 at 1%:         {'Yes' if self.reject_null_1pct else 'No'}")
        lines.append("")
        lines.append("-" * 70)
        
        # Bootstrap distribution summary
        lines.append("Bootstrap Distribution Summary:")
        lines.append(f"  Mean:                       {np.mean(self.bootstrap_statistics):.4f}")
        lines.append(f"  Std Dev:                    {np.std(self.bootstrap_statistics):.4f}")
        lines.append(f"  Min:                        {np.min(self.bootstrap_statistics):.4f}")
        lines.append(f"  Max:                        {np.max(self.bootstrap_statistics):.4f}")
        lines.append("")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'test_statistic': self.test_statistic,
            'bootstrap_p_value': self.bootstrap_p_value,
            'asymptotic_p_value': self.asymptotic_p_value,
            'bootstrap_critical_value_5pct': self.bootstrap_critical_value_5pct,
            'bootstrap_critical_value_1pct': self.bootstrap_critical_value_1pct,
            'bootstrap_critical_value_10pct': self.bootstrap_critical_value_10pct,
            'reject_null_5pct': self.reject_null_5pct,
            'reject_null_1pct': self.reject_null_1pct,
            'reject_null_10pct': self.reject_null_10pct,
            'bootstrap_method': self.bootstrap_method,
            'residual_type': self.residual_type,
            'n_bootstrap': self.n_bootstrap,
            'bootstrap_statistics': self.bootstrap_statistics,
            'm': self.m,
            'k': self.k,
            'r': self.r,
            'degrees_of_freedom': self.degrees_of_freedom,
            'T': self.T,
            'p': self.p
        }


def _compute_lr_statistic(
    eigenvalues_m0: NDArray, 
    eigenvalues_m: NDArray, 
    T_eff: int, 
    r: int
) -> float:
    """
    Compute the LR test statistic for time-varying cointegration.
    
    LR^{tvc} = T * Σ_{j=1}^{r} ln((1 - λ̂_{0,j}) / (1 - λ̂_{m,j}))
    
    Parameters
    ----------
    eigenvalues_m0 : ndarray
        Eigenvalues from standard VECM (m=0).
    eigenvalues_m : ndarray
        Eigenvalues from TV-VECM (m>0).
    T_eff : int
        Effective sample size.
    r : int
        Cointegration rank.
        
    Returns
    -------
    lr_stat : float
        LR test statistic.
    """
    ev_m0 = np.clip(eigenvalues_m0[:r], 1e-14, 1 - 1e-14)
    ev_m = np.clip(eigenvalues_m[:r], 1e-14, 1 - 1e-14)
    
    log_ratio = np.log((1 - ev_m0) / (1 - ev_m))
    lr_stat = T_eff * np.sum(log_ratio)
    
    return max(0, lr_stat)


def _generate_bootstrap_data_wild(
    Y: NDArray,
    residuals: NDArray,
    alpha: NDArray,
    beta: NDArray,
    Gamma: list,
    mu: Optional[NDArray],
    p: int,
    rng: np.random.Generator
) -> NDArray:
    """
    Generate bootstrap sample using wild bootstrap.
    
    Wild bootstrap: ε_t^b = ε̂_t * w_t where w_t ~ N(0, 1) i.i.d.
    
    Parameters
    ----------
    Y : ndarray of shape (T, k)
        Original data.
    residuals : ndarray of shape (T-p, k)
        Residuals from estimated model.
    alpha : ndarray of shape (k, r)
        Adjustment matrix.
    beta : ndarray of shape (k, r)
        Cointegrating vectors.
    Gamma : list of ndarray
        Short-run dynamics matrices.
    mu : ndarray of shape (k,) or None
        Intercept term.
    p : int
        Lag order.
    rng : numpy.random.Generator
        Random number generator.
        
    Returns
    -------
    Y_boot : ndarray of shape (T, k)
        Bootstrap sample.
    """
    T, k = Y.shape
    T_eff = T - p
    
    # Generate wild bootstrap weights
    w = rng.standard_normal(T_eff)
    
    # Generate bootstrap errors
    eps_boot = residuals * w[:, np.newaxis]
    
    # Initialize bootstrap sample with original initial values
    Y_boot = np.zeros((T, k), dtype=np.float64)
    Y_boot[:p, :] = Y[:p, :]
    
    # Compute Pi = alpha @ beta'
    Pi = alpha @ beta.T
    
    # Generate bootstrap data recursively: equation (10) in Martins (2016)
    # ΔY_t^b = μ + α β' Y_{t-1}^b + Σ Γ_j ΔY_{t-j}^b + ε_t^b
    for t in range(p, T):
        idx = t - p  # Index into residuals/eps_boot
        
        # Error correction term
        ec_term = Pi @ Y_boot[t-1, :]
        
        # Short-run dynamics
        sr_term = np.zeros(k)
        for j, Gamma_j in enumerate(Gamma):
            if j + 1 < t:
                DY_lag = Y_boot[t-1-j, :] - Y_boot[t-2-j, :]
                sr_term += Gamma_j @ DY_lag
        
        # Intercept
        mu_term = mu if mu is not None else np.zeros(k)
        
        # Bootstrap first difference
        DY_boot = mu_term + ec_term + sr_term + eps_boot[idx, :]
        
        # Update level
        Y_boot[t, :] = Y_boot[t-1, :] + DY_boot
    
    return Y_boot


def _generate_bootstrap_data_iid(
    Y: NDArray,
    residuals: NDArray,
    alpha: NDArray,
    beta: NDArray,
    Gamma: list,
    mu: Optional[NDArray],
    p: int,
    rng: np.random.Generator
) -> NDArray:
    """
    Generate bootstrap sample using i.i.d. bootstrap (Swensen, 2006).
    
    i.i.d. bootstrap: draw ε_t^b with replacement from centered residuals.
    
    Parameters
    ----------
    Y : ndarray of shape (T, k)
        Original data.
    residuals : ndarray of shape (T-p, k)
        Residuals from estimated model.
    alpha : ndarray of shape (k, r)
        Adjustment matrix.
    beta : ndarray of shape (k, r)
        Cointegrating vectors.
    Gamma : list of ndarray
        Short-run dynamics matrices.
    mu : ndarray of shape (k,) or None
        Intercept term.
    p : int
        Lag order.
    rng : numpy.random.Generator
        Random number generator.
        
    Returns
    -------
    Y_boot : ndarray of shape (T, k)
        Bootstrap sample.
    """
    T, k = Y.shape
    T_eff = T - p
    
    # Center residuals (following Cavaliere et al., 2010a)
    residuals_centered = residuals - np.mean(residuals, axis=0)
    
    # Draw bootstrap errors with replacement
    indices = rng.integers(0, T_eff, size=T_eff)
    eps_boot = residuals_centered[indices, :]
    
    # Initialize bootstrap sample with original initial values
    Y_boot = np.zeros((T, k), dtype=np.float64)
    Y_boot[:p, :] = Y[:p, :]
    
    # Compute Pi = alpha @ beta'
    Pi = alpha @ beta.T
    
    # Generate bootstrap data recursively
    for t in range(p, T):
        idx = t - p
        
        # Error correction term
        ec_term = Pi @ Y_boot[t-1, :]
        
        # Short-run dynamics
        sr_term = np.zeros(k)
        for j, Gamma_j in enumerate(Gamma):
            if j + 1 < t:
                DY_lag = Y_boot[t-1-j, :] - Y_boot[t-2-j, :]
                sr_term += Gamma_j @ DY_lag
        
        # Intercept
        mu_term = mu if mu is not None else np.zeros(k)
        
        # Bootstrap first difference
        DY_boot = mu_term + ec_term + sr_term + eps_boot[idx, :]
        
        # Update level
        Y_boot[t, :] = Y_boot[t-1, :] + DY_boot
    
    return Y_boot


def _compute_bootstrap_lr_statistic(
    Y_boot: NDArray,
    r: int,
    m: int,
    p: int,
    include_intercept: bool
) -> float:
    """
    Compute the LR test statistic for a bootstrap sample.
    
    Parameters
    ----------
    Y_boot : ndarray of shape (T, k)
        Bootstrap sample.
    r : int
        Cointegration rank.
    m : int
        Chebyshev polynomial order.
    p : int
        Lag order.
    include_intercept : bool
        Whether to include intercept.
        
    Returns
    -------
    lr_stat : float
        Bootstrap LR statistic.
    """
    T, k = Y_boot.shape
    T_eff = T - p
    
    try:
        # Estimate standard VECM (m=0)
        model_m0 = JohansenVECM(p=p, include_intercept=include_intercept)
        model_m0.fit(Y_boot, r=r)
        
        # Estimate TV-VECM (m>0)
        model_m = TimeVaryingVECM(p=p, m=m, include_intercept=include_intercept)
        model_m.fit(Y_boot, r=r)
        
        # Compute LR statistic
        lr_stat = _compute_lr_statistic(
            model_m0.eigenvalues,
            model_m.eigenvalues,
            T_eff,
            r
        )
        
        return lr_stat
        
    except Exception:
        # Return NaN if estimation fails
        return np.nan


def bootstrap_tvc_test(
    Y: NDArray,
    r: int,
    m: int,
    p: int = 1,
    include_intercept: bool = True,
    bootstrap_method: Literal['wild', 'iid'] = 'wild',
    residual_type: Literal['unrestricted', 'restricted'] = 'unrestricted',
    n_bootstrap: int = 399,
    seed: Optional[int] = None
) -> BootstrapTVCTestResult:
    """
    Perform bootstrap test for time-varying cointegration.
    
    Tests the null hypothesis of time-invariant cointegration against the
    alternative of time-varying cointegration using bootstrap methods
    from Martins (2016).
    
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
    bootstrap_method : str, optional
        Bootstrap method: 'wild' or 'iid' (default: 'wild').
        - 'wild': Wild bootstrap (Cavaliere et al., 2010a), better under 
          conditional heteroskedasticity.
        - 'iid': i.i.d. bootstrap (Swensen, 2006), standard parametric bootstrap.
    residual_type : str, optional
        Type of residuals to use: 'unrestricted' or 'restricted' (default: 'unrestricted').
        - 'unrestricted': Use residuals from TV-VECM (m > 0).
        - 'restricted': Use residuals from standard VECM (m = 0) as in 
          Cavaliere et al. (2012).
    n_bootstrap : int, optional
        Number of bootstrap replications (default: 399).
    seed : int, optional
        Random seed for reproducibility.
        
    Returns
    -------
    result : BootstrapTVCTestResult
        Test results including bootstrap p-value and critical values.
        
    Notes
    -----
    - The wild bootstrap is recommended as it provides better results under
      conditional heteroskedasticity (Cavaliere et al., 2010a).
    - The restricted residuals approach may not work well for models with
      r > 1 under conditionally heteroskedastic errors (Martins, 2016).
    - Bootstrap replications where estimation fails are discarded.
    
    Examples
    --------
    >>> import numpy as np
    >>> from tvcoint import bootstrap_tvc_test
    >>> # Generate cointegrated data
    >>> T, k = 200, 2
    >>> Y = np.cumsum(np.random.randn(T, k), axis=0)
    >>> Y[:, 1] = Y[:, 0] + np.random.randn(T) * 0.5
    >>> # Test for time-varying cointegration with wild bootstrap
    >>> result = bootstrap_tvc_test(Y, r=1, m=2, p=2, bootstrap_method='wild')
    >>> print(result)
    
    References
    ----------
    Martins, L.F. (2016). "Bootstrap tests for time varying cointegration."
    Econometric Reviews.
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
    if bootstrap_method not in ['wild', 'iid']:
        raise ValueError(f"bootstrap_method must be 'wild' or 'iid', got {bootstrap_method}")
    if residual_type not in ['unrestricted', 'restricted']:
        raise ValueError(f"residual_type must be 'unrestricted' or 'restricted', got {residual_type}")
    if n_bootstrap < 1:
        raise ValueError(f"n_bootstrap must be at least 1, got {n_bootstrap}")
    
    # Check sample size
    min_T = max(k * (m + 1) + p + 10, 2 * k * (m + 1))
    if T < min_T:
        warnings.warn(
            f"Sample size T={T} may be too small for k={k}, m={m}, p={p}. "
            f"Recommended T >= {min_T}"
        )
    
    T_eff = T - p
    
    # Step 1: Estimate standard VECM (m=0) - null hypothesis model
    model_m0 = JohansenVECM(p=p, include_intercept=include_intercept)
    model_m0.fit(Y, r=r)
    
    # Step 2: Estimate time-varying VECM (m>0) - alternative hypothesis model
    model_m = TimeVaryingVECM(p=p, m=m, include_intercept=include_intercept)
    model_m.fit(Y, r=r)
    
    # Step 3: Compute original LR test statistic
    lr_statistic = _compute_lr_statistic(
        model_m0.eigenvalues,
        model_m.eigenvalues,
        T_eff,
        r
    )
    
    # Step 4: Get parameters for bootstrap DGP (from null hypothesis model)
    alpha_h0 = model_m0.alpha
    beta_h0 = model_m0.beta
    Gamma_h0 = model_m0.Gamma if model_m0.Gamma else []
    
    # Estimate intercept if needed
    if include_intercept:
        # Compute intercept from model residuals
        DY = np.diff(Y, axis=0)
        ec_term = (alpha_h0 @ beta_h0.T @ Y[p-1:-1, :].T).T
        sr_term = np.zeros_like(DY[p-1:, :])
        for j, Gamma_j in enumerate(Gamma_h0):
            sr_term += (Gamma_j @ DY[p-2-j:T-2-j, :].T).T if p > 1 else np.zeros_like(sr_term)
        mu_h0 = np.mean(DY[p-1:, :] - ec_term - sr_term, axis=0)
    else:
        mu_h0 = None
    
    # Step 5: Get residuals for bootstrap
    if residual_type == 'unrestricted':
        # Use residuals from TV-VECM
        residuals = model_m.residuals if hasattr(model_m, 'residuals') else _compute_residuals(
            Y, model_m.alpha, model_m.xi, model_m.Gamma, p, m, include_intercept
        )
    else:
        # Use residuals from standard VECM (restricted)
        residuals = model_m0.residuals if hasattr(model_m0, 'residuals') else _compute_residuals_m0(
            Y, alpha_h0, beta_h0, Gamma_h0, p, include_intercept
        )
    
    # Step 6: Bootstrap loop
    rng = np.random.default_rng(seed)
    bootstrap_stats = np.zeros(n_bootstrap)
    valid_count = 0
    
    for b in range(n_bootstrap):
        # Generate bootstrap sample
        if bootstrap_method == 'wild':
            Y_boot = _generate_bootstrap_data_wild(
                Y, residuals, alpha_h0, beta_h0, Gamma_h0, mu_h0, p, rng
            )
        else:  # iid
            Y_boot = _generate_bootstrap_data_iid(
                Y, residuals, alpha_h0, beta_h0, Gamma_h0, mu_h0, p, rng
            )
        
        # Compute bootstrap LR statistic
        lr_boot = _compute_bootstrap_lr_statistic(
            Y_boot, r, m, p, include_intercept
        )
        
        if np.isfinite(lr_boot):
            bootstrap_stats[valid_count] = lr_boot
            valid_count += 1
    
    # Trim to valid statistics
    bootstrap_stats = bootstrap_stats[:valid_count]
    
    if valid_count < n_bootstrap * 0.5:
        warnings.warn(
            f"Only {valid_count}/{n_bootstrap} bootstrap replications succeeded. "
            "Results may be unreliable."
        )
    
    if valid_count == 0:
        raise RuntimeError("All bootstrap replications failed")
    
    # Step 7: Compute bootstrap p-value and critical values
    bootstrap_p_value = np.mean(bootstrap_stats > lr_statistic)
    
    cv_90 = np.percentile(bootstrap_stats, 90)
    cv_95 = np.percentile(bootstrap_stats, 95)
    cv_99 = np.percentile(bootstrap_stats, 99)
    
    # Asymptotic p-value
    df = m * k * r
    asymptotic_p_value = 1 - stats.chi2.cdf(lr_statistic, df)
    
    # Decision using bootstrap critical values
    reject_10pct = lr_statistic > cv_90
    reject_5pct = lr_statistic > cv_95
    reject_1pct = lr_statistic > cv_99
    
    # Create result object
    result = BootstrapTVCTestResult(
        test_statistic=lr_statistic,
        bootstrap_p_value=bootstrap_p_value,
        asymptotic_p_value=asymptotic_p_value,
        bootstrap_critical_value_5pct=cv_95,
        bootstrap_critical_value_1pct=cv_99,
        bootstrap_critical_value_10pct=cv_90,
        reject_null_5pct=reject_5pct,
        reject_null_1pct=reject_1pct,
        reject_null_10pct=reject_10pct,
        bootstrap_method=bootstrap_method,
        residual_type=residual_type,
        n_bootstrap=valid_count,
        bootstrap_statistics=bootstrap_stats,
        m=m,
        k=k,
        r=r,
        degrees_of_freedom=df,
        T=T,
        p=p
    )
    
    return result


def _compute_residuals(
    Y: NDArray,
    alpha: NDArray,
    xi: NDArray,
    Gamma: list,
    p: int,
    m: int,
    include_intercept: bool
) -> NDArray:
    """Compute residuals from TV-VECM."""
    T, k = Y.shape
    T_eff = T - p
    
    DY = np.diff(Y, axis=0)[p-1:, :]  # Shape: (T_eff, k)
    Y_extended = construct_extended_y(Y, m)[p-1:, :]  # Shape: (T_eff, k*(m+1))
    
    # Error correction term: α ξ' Y^{(m)}_{t-1}
    ec_term = (alpha @ xi.T @ Y_extended.T).T
    
    # Short-run dynamics
    sr_term = np.zeros((T_eff, k))
    if Gamma:
        DY_full = np.diff(Y, axis=0)
        for j, Gamma_j in enumerate(Gamma):
            if j + 1 < p:
                sr_term += (Gamma_j @ DY_full[p-2-j:T-2-j, :].T).T
    
    residuals = DY - ec_term - sr_term
    
    if include_intercept:
        residuals = residuals - np.mean(residuals, axis=0)
    
    return residuals


def _compute_residuals_m0(
    Y: NDArray,
    alpha: NDArray,
    beta: NDArray,
    Gamma: list,
    p: int,
    include_intercept: bool
) -> NDArray:
    """Compute residuals from standard VECM (m=0)."""
    T, k = Y.shape
    T_eff = T - p
    
    DY = np.diff(Y, axis=0)[p-1:, :]  # Shape: (T_eff, k)
    Y_lag = Y[p-1:-1, :]  # Shape: (T_eff, k)
    
    # Error correction term: α β' Y_{t-1}
    Pi = alpha @ beta.T
    ec_term = (Pi @ Y_lag.T).T
    
    # Short-run dynamics
    sr_term = np.zeros((T_eff, k))
    if Gamma:
        DY_full = np.diff(Y, axis=0)
        for j, Gamma_j in enumerate(Gamma):
            if j + 1 < p:
                sr_term += (Gamma_j @ DY_full[p-2-j:T-2-j, :].T).T
    
    residuals = DY - ec_term - sr_term
    
    if include_intercept:
        residuals = residuals - np.mean(residuals, axis=0)
    
    return residuals


def wild_bootstrap_tvc_test(
    Y: NDArray,
    r: int,
    m: int,
    p: int = 1,
    include_intercept: bool = True,
    residual_type: Literal['unrestricted', 'restricted'] = 'unrestricted',
    n_bootstrap: int = 399,
    seed: Optional[int] = None
) -> BootstrapTVCTestResult:
    """
    Perform wild bootstrap test for time-varying cointegration.
    
    Convenience function that calls bootstrap_tvc_test with bootstrap_method='wild'.
    
    The wild bootstrap is recommended under conditional heteroskedasticity
    (Cavaliere et al., 2010a).
    
    Parameters
    ----------
    Y : ndarray of shape (T, k)
        The k-variate time series data.
    r : int
        Cointegration rank.
    m : int
        Chebyshev polynomial order.
    p : int, optional
        Lag order (default: 1).
    include_intercept : bool, optional
        Whether to include intercept (default: True).
    residual_type : str, optional
        'unrestricted' or 'restricted' (default: 'unrestricted').
    n_bootstrap : int, optional
        Number of bootstrap replications (default: 399).
    seed : int, optional
        Random seed.
        
    Returns
    -------
    result : BootstrapTVCTestResult
        Test results.
        
    See Also
    --------
    bootstrap_tvc_test : Main bootstrap test function.
    iid_bootstrap_tvc_test : i.i.d. bootstrap test.
    
    References
    ----------
    Cavaliere, G., Rahbek, A., Taylor, A.M.R. (2010a). "Cointegration rank
    testing under conditional heteroskedasticity." Econometric Theory.
    """
    return bootstrap_tvc_test(
        Y=Y,
        r=r,
        m=m,
        p=p,
        include_intercept=include_intercept,
        bootstrap_method='wild',
        residual_type=residual_type,
        n_bootstrap=n_bootstrap,
        seed=seed
    )


def iid_bootstrap_tvc_test(
    Y: NDArray,
    r: int,
    m: int,
    p: int = 1,
    include_intercept: bool = True,
    residual_type: Literal['unrestricted', 'restricted'] = 'unrestricted',
    n_bootstrap: int = 399,
    seed: Optional[int] = None
) -> BootstrapTVCTestResult:
    """
    Perform i.i.d. bootstrap test for time-varying cointegration (Swensen, 2006).
    
    Convenience function that calls bootstrap_tvc_test with bootstrap_method='iid'.
    
    Parameters
    ----------
    Y : ndarray of shape (T, k)
        The k-variate time series data.
    r : int
        Cointegration rank.
    m : int
        Chebyshev polynomial order.
    p : int, optional
        Lag order (default: 1).
    include_intercept : bool, optional
        Whether to include intercept (default: True).
    residual_type : str, optional
        'unrestricted' or 'restricted' (default: 'unrestricted').
    n_bootstrap : int, optional
        Number of bootstrap replications (default: 399).
    seed : int, optional
        Random seed.
        
    Returns
    -------
    result : BootstrapTVCTestResult
        Test results.
        
    See Also
    --------
    bootstrap_tvc_test : Main bootstrap test function.
    wild_bootstrap_tvc_test : Wild bootstrap test.
    
    References
    ----------
    Swensen, A.R. (2006). "Bootstrap algorithms for testing and determining
    the cointegration rank in VAR Models." Econometrica.
    """
    return bootstrap_tvc_test(
        Y=Y,
        r=r,
        m=m,
        p=p,
        include_intercept=include_intercept,
        bootstrap_method='iid',
        residual_type=residual_type,
        n_bootstrap=n_bootstrap,
        seed=seed
    )


def bootstrap_multiple_m_test(
    Y: NDArray,
    r: int,
    m_values: Union[int, list] = 5,
    p: int = 1,
    include_intercept: bool = True,
    bootstrap_method: Literal['wild', 'iid'] = 'wild',
    residual_type: Literal['unrestricted', 'restricted'] = 'unrestricted',
    n_bootstrap: int = 399,
    seed: Optional[int] = None,
    bonferroni_correction: bool = True
) -> Dict[str, Any]:
    """
    Perform bootstrap TVC test for multiple values of m.
    
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
    bootstrap_method : str
        'wild' or 'iid'.
    residual_type : str
        'unrestricted' or 'restricted'.
    n_bootstrap : int
        Number of bootstrap replications.
    seed : int, optional
        Random seed.
    bonferroni_correction : bool
        Whether to apply Bonferroni correction.
        
    Returns
    -------
    dict with keys:
        'results' : List of BootstrapTVCTestResult for each m.
        'min_p_value' : Minimum bootstrap p-value across all tests.
        'min_p_value_m' : m value achieving minimum p-value.
        'bonferroni_p_value' : Bonferroni-corrected minimum p-value.
        'any_reject_5pct' : Whether any test rejects at 5%.
        'summary' : List of summary dicts.
    """
    Y = np.asarray(Y, dtype=np.float64)
    T, k = Y.shape
    
    if isinstance(m_values, int):
        m_list = list(range(1, m_values + 1))
    else:
        m_list = list(m_values)
    
    # Filter out m values that are too large
    valid_m = [m for m in m_list if T >= k * (m + 1) + p + 10]
    if len(valid_m) == 0:
        raise ValueError("Sample size too small for any m value")
    
    if len(valid_m) < len(m_list):
        warnings.warn(
            f"Some m values removed due to sample size constraints. "
            f"Testing m = {valid_m}"
        )
    
    results = []
    rng = np.random.default_rng(seed)
    
    for m in valid_m:
        try:
            result = bootstrap_tvc_test(
                Y=Y,
                r=r,
                m=m,
                p=p,
                include_intercept=include_intercept,
                bootstrap_method=bootstrap_method,
                residual_type=residual_type,
                n_bootstrap=n_bootstrap,
                seed=rng.integers(0, 2**31)
            )
            results.append(result)
        except Exception as e:
            warnings.warn(f"Bootstrap test failed for m={m}: {str(e)}")
    
    if len(results) == 0:
        raise RuntimeError("All tests failed")
    
    # Find minimum p-value
    p_values = [r.bootstrap_p_value for r in results]
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
            'bootstrap_p_value': r.bootstrap_p_value,
            'asymptotic_p_value': r.asymptotic_p_value,
            'bootstrap_CV_5pct': r.bootstrap_critical_value_5pct,
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


def compare_asymptotic_bootstrap(
    Y: NDArray,
    r: int,
    m: int,
    p: int = 1,
    include_intercept: bool = True,
    n_bootstrap: int = 399,
    seed: Optional[int] = None
) -> Dict[str, Any]:
    """
    Compare asymptotic and bootstrap test results.
    
    This function performs both the asymptotic chi-square test and
    bootstrap tests (wild and i.i.d.) for comparison.
    
    Parameters
    ----------
    Y : ndarray of shape (T, k)
        The k-variate time series data.
    r : int
        Cointegration rank.
    m : int
        Chebyshev polynomial order.
    p : int
        Lag order.
    include_intercept : bool
        Whether to include intercept.
    n_bootstrap : int
        Number of bootstrap replications.
    seed : int, optional
        Random seed.
        
    Returns
    -------
    dict with comparison results.
    """
    from .tests import lr_test_tv_cointegration
    
    rng = np.random.default_rng(seed)
    
    # Asymptotic test
    asymptotic_result = lr_test_tv_cointegration(
        Y, r=r, m=m, p=p, include_intercept=include_intercept
    )
    
    # Wild bootstrap
    wild_result = wild_bootstrap_tvc_test(
        Y, r=r, m=m, p=p,
        include_intercept=include_intercept,
        n_bootstrap=n_bootstrap,
        seed=rng.integers(0, 2**31)
    )
    
    # i.i.d. bootstrap
    iid_result = iid_bootstrap_tvc_test(
        Y, r=r, m=m, p=p,
        include_intercept=include_intercept,
        n_bootstrap=n_bootstrap,
        seed=rng.integers(0, 2**31)
    )
    
    return {
        'test_statistic': asymptotic_result.test_statistic,
        'asymptotic': {
            'p_value': asymptotic_result.p_value,
            'cv_5pct': asymptotic_result.critical_value_5pct,
            'reject_5pct': asymptotic_result.reject_null_5pct
        },
        'wild_bootstrap': {
            'p_value': wild_result.bootstrap_p_value,
            'cv_5pct': wild_result.bootstrap_critical_value_5pct,
            'reject_5pct': wild_result.reject_null_5pct
        },
        'iid_bootstrap': {
            'p_value': iid_result.bootstrap_p_value,
            'cv_5pct': iid_result.bootstrap_critical_value_5pct,
            'reject_5pct': iid_result.reject_null_5pct
        },
        'asymptotic_result': asymptotic_result,
        'wild_result': wild_result,
        'iid_result': iid_result
    }
