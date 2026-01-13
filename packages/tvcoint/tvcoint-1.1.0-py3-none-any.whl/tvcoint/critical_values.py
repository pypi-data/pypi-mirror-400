"""
Critical Values for Time-Varying Cointegration Test
====================================================

This module provides critical values for the LR test of time-varying cointegration.
According to Theorem 1 of Bierens and Martins (2010), the test statistic is
asymptotically χ²_{mkr} distributed under the null hypothesis.

However, as noted in Section 3.4, there may be size distortion in finite samples.
This module provides:
1. Asymptotic critical values from χ²_{mkr}
2. Simulation-based critical values for improved finite-sample performance
3. Size-adjusted critical values based on Monte Carlo

Reference:
    Bierens, H.J. and Martins, L.F. (2010). "Time-Varying Cointegration."
    Econometric Theory, 26(5), 1453-1490.
"""

import numpy as np
from scipy import stats
from scipy import linalg
from typing import Tuple, Optional, Dict, Any, List, Union
from numpy.typing import NDArray
import warnings
from tqdm import tqdm  # Optional progress bar
import pickle
import os

from .chebyshev import chebyshev_polynomial_matrix, construct_extended_y
from .utils import simulate_cointegrated_system


def asymptotic_critical_value(
    m: int,
    k: int,
    r: int,
    alpha: float = 0.05
) -> float:
    """
    Compute asymptotic critical value from χ²_{mkr} distribution.
    
    Under the null hypothesis of time-invariant cointegration, the LR test
    statistic converges to χ²_{mkr} (Theorem 1).
    
    Parameters
    ----------
    m : int
        Chebyshev polynomial order.
    k : int
        Number of variables.
    r : int
        Cointegration rank.
    alpha : float
        Significance level (e.g., 0.05 for 5%).
        
    Returns
    -------
    cv : float
        Critical value such that P(χ²_{mkr} > cv) = alpha.
        
    Examples
    --------
    >>> cv = asymptotic_critical_value(m=2, k=3, r=1, alpha=0.05)
    >>> print(f"5% CV for m=2, k=3, r=1: {cv:.4f}")
    """
    df = m * k * r
    
    if df <= 0:
        raise ValueError(f"Degrees of freedom must be positive, got m*k*r = {df}")
    
    cv = stats.chi2.ppf(1 - alpha, df)
    
    return cv


def asymptotic_p_value(
    test_statistic: float,
    m: int,
    k: int,
    r: int
) -> float:
    """
    Compute asymptotic p-value from χ²_{mkr} distribution.
    
    Parameters
    ----------
    test_statistic : float
        The LR test statistic.
    m : int
        Chebyshev polynomial order.
    k : int
        Number of variables.
    r : int
        Cointegration rank.
        
    Returns
    -------
    p_value : float
        Asymptotic p-value.
    """
    df = m * k * r
    
    if df <= 0:
        raise ValueError(f"Degrees of freedom must be positive, got m*k*r = {df}")
    
    p_value = 1 - stats.chi2.cdf(test_statistic, df)
    
    return p_value


def simulate_null_distribution(
    T: int,
    k: int,
    r: int,
    m: int,
    p: int = 1,
    n_simulations: int = 1000,
    alpha_true: NDArray = None,
    beta_true: NDArray = None,
    Omega_true: NDArray = None,
    seed: Optional[int] = None,
    show_progress: bool = True
) -> Dict[str, Any]:
    """
    Simulate the null distribution of the LR test statistic.
    
    Generates data under the null hypothesis (time-invariant cointegration)
    and computes the empirical distribution of the test statistic.
    
    Parameters
    ----------
    T : int
        Sample size.
    k : int
        Number of variables.
    r : int
        Cointegration rank.
    m : int
        Chebyshev order for the alternative.
    p : int
        Lag order.
    n_simulations : int
        Number of Monte Carlo replications.
    alpha_true : ndarray, optional
        True adjustment matrix for DGP.
    beta_true : ndarray, optional
        True cointegrating vectors for DGP.
    Omega_true : ndarray, optional
        True error covariance for DGP.
    seed : int, optional
        Random seed for reproducibility.
    show_progress : bool
        Whether to show progress bar.
        
    Returns
    -------
    dict with keys:
        'test_statistics' : Array of simulated test statistics
        'mean' : Mean of simulated statistics
        'std' : Standard deviation
        'quantiles' : Dictionary of quantiles
        'empirical_critical_values' : Critical values at 1%, 5%, 10%
        'empirical_size_5pct' : Empirical rejection rate using asymptotic 5% CV
        'asymptotic_df' : Degrees of freedom m*k*r
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Default DGP parameters
    if alpha_true is None:
        alpha_true = -0.2 * np.eye(k, r)
    if beta_true is None:
        beta_true = np.eye(k, r)
    if Omega_true is None:
        Omega_true = np.eye(k)
    
    # Asymptotic critical value for size comparison
    df = m * k * r
    cv_asymp_5pct = stats.chi2.ppf(0.95, df)
    
    # Storage for test statistics
    test_stats = np.zeros(n_simulations)
    
    # Import here to avoid circular imports
    from .tests import lr_test_tv_cointegration
    
    # Progress bar setup
    iterator = range(n_simulations)
    if show_progress:
        try:
            iterator = tqdm(iterator, desc="Simulating null distribution")
        except:
            pass
    
    n_failed = 0
    
    for i in iterator:
        try:
            # Generate cointegrated data under H0
            Y, _ = simulate_cointegrated_system(
                T=T, k=k, r=r,
                alpha=alpha_true,
                beta=beta_true,
                Omega=Omega_true
            )
            
            # Compute test statistic
            result = lr_test_tv_cointegration(
                Y, r=r, m=m, p=p, include_intercept=True
            )
            
            test_stats[i] = result.test_statistic
            
        except Exception as e:
            test_stats[i] = np.nan
            n_failed += 1
    
    # Remove failed simulations
    valid_stats = test_stats[~np.isnan(test_stats)]
    
    if len(valid_stats) < n_simulations * 0.5:
        warnings.warn(f"More than 50% of simulations failed ({n_failed}/{n_simulations})")
    
    # Compute summary statistics
    mean_stat = np.mean(valid_stats)
    std_stat = np.std(valid_stats)
    
    # Quantiles
    quantiles = {
        0.01: np.percentile(valid_stats, 1),
        0.05: np.percentile(valid_stats, 5),
        0.10: np.percentile(valid_stats, 10),
        0.25: np.percentile(valid_stats, 25),
        0.50: np.percentile(valid_stats, 50),
        0.75: np.percentile(valid_stats, 75),
        0.90: np.percentile(valid_stats, 90),
        0.95: np.percentile(valid_stats, 95),
        0.99: np.percentile(valid_stats, 99)
    }
    
    # Empirical critical values
    empirical_cvs = {
        '10%': np.percentile(valid_stats, 90),
        '5%': np.percentile(valid_stats, 95),
        '1%': np.percentile(valid_stats, 99)
    }
    
    # Empirical size (rejection rate using asymptotic CV)
    empirical_size = np.mean(valid_stats > cv_asymp_5pct)
    
    return {
        'test_statistics': valid_stats,
        'mean': mean_stat,
        'std': std_stat,
        'quantiles': quantiles,
        'empirical_critical_values': empirical_cvs,
        'empirical_size_5pct': empirical_size,
        'asymptotic_df': df,
        'asymptotic_cv_5pct': cv_asymp_5pct,
        'n_simulations': len(valid_stats),
        'n_failed': n_failed,
        'T': T,
        'k': k,
        'r': r,
        'm': m,
        'p': p
    }


def compute_critical_value_table(
    T_values: List[int] = [100, 200, 500],
    k_values: List[int] = [2, 3, 4],
    r_values: List[int] = [1, 2],
    m_values: List[int] = [1, 2, 3],
    n_simulations: int = 1000,
    seed: int = 42,
    show_progress: bool = True
) -> Dict[str, Any]:
    """
    Compute a table of critical values for various parameter combinations.
    
    This function generates a comprehensive table similar to those in
    econometrics textbooks, useful for applied researchers.
    
    Parameters
    ----------
    T_values : list
        Sample sizes to consider.
    k_values : list
        Number of variables to consider.
    r_values : list
        Cointegration ranks to consider.
    m_values : list
        Chebyshev orders to consider.
    n_simulations : int
        Number of Monte Carlo replications per combination.
    seed : int
        Random seed.
    show_progress : bool
        Whether to show progress.
        
    Returns
    -------
    dict with keys:
        'table' : List of dicts with critical values
        'parameters' : Parameter combinations
    """
    np.random.seed(seed)
    
    results = []
    
    total_combos = len(T_values) * len(k_values) * len(r_values) * len(m_values)
    combo_idx = 0
    
    for T in T_values:
        for k in k_values:
            for r in r_values:
                if r >= k:
                    continue
                for m in m_values:
                    combo_idx += 1
                    
                    # Check feasibility
                    if T < k * (m + 1) + 20:
                        continue
                    
                    if show_progress:
                        print(f"Computing ({combo_idx}/{total_combos}): T={T}, k={k}, r={r}, m={m}")
                    
                    try:
                        sim_result = simulate_null_distribution(
                            T=T, k=k, r=r, m=m, p=1,
                            n_simulations=n_simulations,
                            show_progress=False
                        )
                        
                        results.append({
                            'T': T,
                            'k': k,
                            'r': r,
                            'm': m,
                            'df': m * k * r,
                            'cv_10pct_empirical': sim_result['empirical_critical_values']['10%'],
                            'cv_5pct_empirical': sim_result['empirical_critical_values']['5%'],
                            'cv_1pct_empirical': sim_result['empirical_critical_values']['1%'],
                            'cv_10pct_asymptotic': stats.chi2.ppf(0.90, m * k * r),
                            'cv_5pct_asymptotic': stats.chi2.ppf(0.95, m * k * r),
                            'cv_1pct_asymptotic': stats.chi2.ppf(0.99, m * k * r),
                            'empirical_size_5pct': sim_result['empirical_size_5pct'],
                            'mean': sim_result['mean'],
                            'std': sim_result['std']
                        })
                        
                    except Exception as e:
                        warnings.warn(f"Failed for T={T}, k={k}, r={r}, m={m}: {str(e)}")
    
    return {
        'table': results,
        'parameters': {
            'T_values': T_values,
            'k_values': k_values,
            'r_values': r_values,
            'm_values': m_values,
            'n_simulations': n_simulations
        }
    }


def get_size_adjusted_critical_value(
    T: int,
    k: int,
    r: int,
    m: int,
    alpha: float = 0.05,
    n_simulations: int = 5000,
    seed: Optional[int] = None
) -> Tuple[float, float]:
    """
    Get size-adjusted critical value through simulation.
    
    For small samples, the asymptotic χ² approximation may not be accurate.
    This function provides simulation-based critical values.
    
    Parameters
    ----------
    T : int
        Sample size.
    k : int
        Number of variables.
    r : int
        Cointegration rank.
    m : int
        Chebyshev order.
    alpha : float
        Significance level.
    n_simulations : int
        Number of simulations.
    seed : int, optional
        Random seed.
        
    Returns
    -------
    cv_adjusted : float
        Size-adjusted critical value.
    cv_asymptotic : float
        Asymptotic critical value (for comparison).
    """
    cv_asymptotic = asymptotic_critical_value(m, k, r, alpha)
    
    sim_result = simulate_null_distribution(
        T=T, k=k, r=r, m=m, p=1,
        n_simulations=n_simulations,
        seed=seed,
        show_progress=False
    )
    
    cv_adjusted = np.percentile(sim_result['test_statistics'], 100 * (1 - alpha))
    
    return cv_adjusted, cv_asymptotic


def bootstrap_p_value(
    Y: NDArray,
    test_statistic: float,
    r: int,
    m: int,
    p: int = 1,
    n_bootstrap: int = 999,
    seed: Optional[int] = None,
    show_progress: bool = False
) -> Tuple[float, NDArray]:
    """
    Compute bootstrap p-value for the LR test.
    
    Uses a parametric bootstrap under the null hypothesis of
    time-invariant cointegration.
    
    Parameters
    ----------
    Y : ndarray
        Original data.
    test_statistic : float
        Observed test statistic.
    r : int
        Cointegration rank.
    m : int
        Chebyshev order.
    p : int
        Lag order.
    n_bootstrap : int
        Number of bootstrap replications.
    seed : int, optional
        Random seed.
    show_progress : bool
        Whether to show progress.
        
    Returns
    -------
    p_value : float
        Bootstrap p-value.
    bootstrap_stats : ndarray
        Bootstrap test statistics.
    """
    from .vecm import JohansenVECM
    from .tests import lr_test_tv_cointegration
    
    if seed is not None:
        np.random.seed(seed)
    
    Y = np.asarray(Y, dtype=np.float64)
    T, k = Y.shape
    
    # Estimate null model (time-invariant VECM)
    model_h0 = JohansenVECM(p=p, include_intercept=True)
    model_h0.fit(Y, r=r)
    
    # Extract null model parameters
    alpha = model_h0.alpha
    beta = model_h0.beta
    Omega = model_h0.Omega
    
    # Cholesky factor for generating errors
    L = linalg.cholesky(Omega, lower=True)
    
    bootstrap_stats = np.zeros(n_bootstrap)
    
    iterator = range(n_bootstrap)
    if show_progress:
        try:
            iterator = tqdm(iterator, desc="Bootstrap")
        except:
            pass
    
    for b in iterator:
        try:
            # Generate bootstrap sample under H0
            errors = np.random.randn(T, k) @ L.T
            
            Y_boot = np.zeros((T, k))
            Y_boot[0, :] = Y[0, :]
            
            Pi = alpha @ beta.T
            for t in range(1, T):
                Y_boot[t, :] = Y_boot[t-1, :] + Pi @ Y_boot[t-1, :] + errors[t, :]
            
            # Compute test statistic on bootstrap sample
            result = lr_test_tv_cointegration(
                Y_boot, r=r, m=m, p=p, include_intercept=True
            )
            bootstrap_stats[b] = result.test_statistic
            
        except:
            bootstrap_stats[b] = np.nan
    
    # Remove failed bootstraps
    valid_stats = bootstrap_stats[~np.isnan(bootstrap_stats)]
    
    # Compute p-value
    p_value = np.mean(valid_stats >= test_statistic)
    
    return p_value, valid_stats


class CriticalValueCache:
    """
    Cache for storing and retrieving critical values.
    
    Useful for avoiding repeated simulations when testing multiple series
    with the same dimensions.
    """
    
    def __init__(self, cache_file: Optional[str] = None):
        """
        Initialize cache.
        
        Parameters
        ----------
        cache_file : str, optional
            Path to cache file for persistence.
        """
        self.cache = {}
        self.cache_file = cache_file
        
        if cache_file and os.path.exists(cache_file):
            self.load()
    
    def get_key(self, T: int, k: int, r: int, m: int, alpha: float) -> str:
        """Generate cache key."""
        return f"T{T}_k{k}_r{r}_m{m}_a{alpha}"
    
    def get(
        self,
        T: int,
        k: int,
        r: int,
        m: int,
        alpha: float = 0.05
    ) -> Optional[float]:
        """
        Get cached critical value.
        
        Returns None if not in cache.
        """
        key = self.get_key(T, k, r, m, alpha)
        return self.cache.get(key)
    
    def set(
        self,
        T: int,
        k: int,
        r: int,
        m: int,
        alpha: float,
        cv: float
    ) -> None:
        """Store critical value in cache."""
        key = self.get_key(T, k, r, m, alpha)
        self.cache[key] = cv
    
    def save(self) -> None:
        """Save cache to file."""
        if self.cache_file:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.cache, f)
    
    def load(self) -> None:
        """Load cache from file."""
        if self.cache_file and os.path.exists(self.cache_file):
            with open(self.cache_file, 'rb') as f:
                self.cache = pickle.load(f)


# Pre-computed asymptotic critical values for common cases
# Format: (m, k, r): {alpha: cv}
ASYMPTOTIC_CRITICAL_VALUES = {}

def _precompute_common_cvs():
    """Pre-compute critical values for common parameter combinations."""
    alphas = [0.10, 0.05, 0.01]
    
    for m in range(1, 6):
        for k in range(2, 7):
            for r in range(1, k):
                df = m * k * r
                ASYMPTOTIC_CRITICAL_VALUES[(m, k, r)] = {
                    alpha: stats.chi2.ppf(1 - alpha, df)
                    for alpha in alphas
                }

# Initialize pre-computed values
_precompute_common_cvs()


def get_critical_value(
    m: int,
    k: int,
    r: int,
    alpha: float = 0.05,
    method: str = 'asymptotic'
) -> float:
    """
    Get critical value using specified method.
    
    Parameters
    ----------
    m : int
        Chebyshev order.
    k : int
        Number of variables.
    r : int
        Cointegration rank.
    alpha : float
        Significance level.
    method : str
        'asymptotic' for chi-square critical values,
        'precomputed' for cached values (faster).
        
    Returns
    -------
    cv : float
        Critical value.
    """
    if method == 'precomputed':
        key = (m, k, r)
        if key in ASYMPTOTIC_CRITICAL_VALUES:
            if alpha in ASYMPTOTIC_CRITICAL_VALUES[key]:
                return ASYMPTOTIC_CRITICAL_VALUES[key][alpha]
    
    return asymptotic_critical_value(m, k, r, alpha)
