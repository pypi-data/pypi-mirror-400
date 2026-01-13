"""
Standard Vector Error Correction Model (VECM) Estimation
=========================================================

Implementation of Johansen's (1988, 1991, 1995) maximum likelihood estimation
procedure for cointegration analysis. This serves as the null hypothesis model
(time-invariant cointegration) in the time-varying cointegration test.

References:
    Johansen, S. (1988). "Statistical Analysis of Cointegration Vectors."
    Journal of Economic Dynamics and Control, 12, 231-254.
    
    Johansen, S. (1991). "Estimation and Hypothesis Testing of Cointegration
    Vectors in Gaussian Vector Autoregressive Models." Econometrica, 59, 1551-1580.
    
    Johansen, S. (1995). Likelihood-Based Inference in Cointegrated Vector
    Autoregressive Models. Oxford University Press.
    
    Bierens, H.J. and Martins, L.F. (2010). "Time-Varying Cointegration."
    Econometric Theory, 26(5), 1453-1490.
"""

import numpy as np
from scipy import linalg
from typing import Tuple, Optional, Dict, Any, List
from numpy.typing import NDArray
import warnings

from .utils import (
    compute_differenced_data,
    compute_residual_matrices,
    solve_generalized_eigenvalue,
    orthogonal_complement,
    information_criteria
)


class JohansenVECM:
    """
    Johansen's Maximum Likelihood Estimation for Cointegrated VAR Models.
    
    This class implements the standard (time-invariant) VECM estimation procedure
    as described in Johansen (1988, 1991, 1995). In the context of Bierens and
    Martins (2010), this corresponds to the null hypothesis model where m=0.
    
    The model is:
        ΔY_t = α β' Y_{t-1} + Σ_{j=1}^{p-1} Γ_j ΔY_{t-j} + μ_0 + ε_t
    
    where:
        - Y_t is a k-dimensional time series
        - α is the k×r adjustment matrix
        - β is the k×r matrix of cointegrating vectors
        - Γ_j are k×k short-run dynamics matrices
        - μ_0 is an optional intercept (drift case)
        - ε_t ~ N(0, Ω)
    
    Parameters
    ----------
    p : int
        Lag order for the underlying VAR. The VECM has p-1 lagged differences.
    include_intercept : bool, optional
        Whether to include an intercept term (default: True).
        
    Attributes
    ----------
    eigenvalues : ndarray of shape (k,)
        Ordered eigenvalues from the reduced rank regression.
    eigenvectors : ndarray of shape (k, k)
        Corresponding eigenvectors (columns of β normalized by S11).
    alpha : ndarray of shape (k, r)
        Estimated adjustment matrix.
    beta : ndarray of shape (k, r)
        Estimated cointegrating vectors.
    Gamma : list of ndarray
        Estimated short-run dynamics matrices.
    Omega : ndarray of shape (k, k)
        Estimated error covariance matrix.
    log_likelihood : float
        Maximized log-likelihood value.
    S00, S11, S01 : ndarray
        Residual moment matrices from the concentrated likelihood.
        
    Examples
    --------
    >>> import numpy as np
    >>> from tvcoint.vecm import JohansenVECM
    >>> # Simulate cointegrated data
    >>> T, k = 200, 2
    >>> Y = np.cumsum(np.random.randn(T, k), axis=0)
    >>> Y[:, 1] = Y[:, 0] + np.random.randn(T) * 0.5  # Y2 cointegrated with Y1
    >>> # Estimate VECM
    >>> model = JohansenVECM(p=2)
    >>> model.fit(Y, r=1)
    >>> print(f"Cointegrating vector: {model.beta[:, 0]}")
    """
    
    def __init__(self, p: int = 1, include_intercept: bool = True):
        """
        Initialize the Johansen VECM estimator.
        
        Parameters
        ----------
        p : int
            Lag order for the underlying VAR (p >= 1).
        include_intercept : bool
            Whether to include an intercept in the model.
        """
        if p < 1:
            raise ValueError(f"Lag order p must be at least 1, got {p}")
        
        self.p = p
        self.include_intercept = include_intercept
        
        # Results (populated after fit)
        self.eigenvalues = None
        self.eigenvectors = None
        self.alpha = None
        self.beta = None
        self.Gamma = None
        self.Omega = None
        self.log_likelihood = None
        self.S00 = None
        self.S11 = None
        self.S01 = None
        self._fitted = False
        self._Y = None
        self._k = None
        self._T = None
        self._r = None
        
    def fit(self, Y: NDArray, r: int) -> 'JohansenVECM':
        """
        Fit the VECM model using Johansen's ML procedure.
        
        Parameters
        ----------
        Y : ndarray of shape (T, k)
            The k-variate time series data.
        r : int
            Assumed cointegration rank (0 < r < k).
            
        Returns
        -------
        self : JohansenVECM
            Fitted model instance.
        """
        Y = np.asarray(Y, dtype=np.float64)
        
        if Y.ndim != 2:
            raise ValueError(f"Y must be 2-dimensional, got {Y.ndim}")
        
        T, k = Y.shape
        
        if r < 1 or r >= k:
            raise ValueError(f"Cointegration rank r={r} must satisfy 0 < r < k={k}")
        
        if T < k + self.p + 1:
            raise ValueError(f"Sample size T={T} too small for k={k}, p={self.p}")
        
        self._Y = Y
        self._k = k
        self._T = T
        self._r = r
        
        # Step 1: Compute differenced data
        DY, Y_lag1, X = compute_differenced_data(Y, self.p)
        T_eff = DY.shape[0]
        
        # Step 2: Compute residual moment matrices
        self.S00, self.S11, self.S01 = compute_residual_matrices(
            DY, Y_lag1, X, self.include_intercept
        )
        
        # Step 3: Solve generalized eigenvalue problem
        self.eigenvalues, self.eigenvectors = solve_generalized_eigenvalue(
            self.S00, self.S11, self.S01
        )
        
        # Step 4: Extract alpha and beta for given rank r
        self.beta = self.eigenvectors[:, :r].copy()
        
        # Normalize beta: first r rows form identity
        # (Johansen's identification: first r elements normalized)
        try:
            beta_r = self.beta[:r, :]
            if np.abs(np.linalg.det(beta_r)) > 1e-10:
                self.beta = self.beta @ linalg.inv(beta_r)
        except:
            pass  # Keep unnormalized if normalization fails
        
        # Compute alpha from the relationship: S01 = S00 α β' S11 / T
        # or directly: α = S01 β (β' S11 β)^{-1}
        beta_S11_beta = self.beta.T @ self.S11 @ self.beta
        if np.abs(linalg.det(beta_S11_beta)) > 1e-14:
            self.alpha = self.S01 @ self.beta @ linalg.inv(beta_S11_beta)
        else:
            self.alpha = self.S01 @ self.beta @ linalg.pinv(beta_S11_beta)
        
        # Step 5: Compute Gamma matrices (short-run dynamics)
        self._estimate_gamma(DY, Y_lag1, X)
        
        # Step 6: Compute error covariance matrix
        self._estimate_omega(DY, Y_lag1, X)
        
        # Step 7: Compute log-likelihood
        self._compute_log_likelihood(T_eff)
        
        self._fitted = True
        
        return self
    
    def _estimate_gamma(
        self, 
        DY: NDArray, 
        Y_lag1: NDArray, 
        X: Optional[NDArray]
    ) -> None:
        """Estimate short-run dynamics matrices Γ_j."""
        T_eff, k = DY.shape
        
        # Residuals after removing error correction term
        ec_term = (self.alpha @ self.beta.T @ Y_lag1.T).T
        DY_adj = DY - ec_term
        
        if X is not None and X.shape[1] > 0:
            # Estimate Γ from OLS: DY_adj = X Γ' + residuals
            Gamma_mat = linalg.lstsq(X, DY_adj)[0]  # Shape: (n_x, k)
            
            # Parse into individual Γ_j matrices
            self.Gamma = []
            n_lags = X.shape[1] // k
            for j in range(n_lags):
                self.Gamma.append(Gamma_mat[j*k:(j+1)*k, :].T)
        else:
            self.Gamma = []
    
    def _estimate_omega(
        self,
        DY: NDArray,
        Y_lag1: NDArray,
        X: Optional[NDArray]
    ) -> None:
        """Estimate error covariance matrix Ω."""
        T_eff, k = DY.shape
        
        # Compute fitted values
        fitted = (self.alpha @ self.beta.T @ Y_lag1.T).T
        
        if X is not None and X.shape[1] > 0 and len(self.Gamma) > 0:
            Gamma_mat = np.vstack([G.T for G in self.Gamma])
            fitted += X @ Gamma_mat
        
        # Residuals
        residuals = DY - fitted
        
        # Estimate Ω = (1/T) Σ ε_t ε'_t
        self.Omega = residuals.T @ residuals / T_eff
    
    def _compute_log_likelihood(self, T_eff: int) -> None:
        """
        Compute the maximized log-likelihood.
        
        From Johansen (1988), the log-likelihood given rank r is:
            l_T(r) = -0.5 * T * Σ_{j=1}^{r} ln(1 - λ_j) - 0.5 * T * ln(det(S00))
        """
        r = self._r
        
        # Sum of log(1 - λ_j) for j = 1, ..., r
        log_term = np.sum(np.log(1 - self.eigenvalues[:r] + 1e-14))
        
        # Log determinant of S00
        sign, logdet_S00 = np.linalg.slogdet(self.S00)
        if sign <= 0:
            logdet_S00 = np.log(np.abs(np.linalg.det(self.S00)) + 1e-14)
        
        # Constant term
        k = self._k
        constant = -0.5 * T_eff * k * np.log(2 * np.pi) - 0.5 * T_eff * k
        
        self.log_likelihood = (
            -0.5 * T_eff * log_term 
            - 0.5 * T_eff * logdet_S00 
            + constant
        )
    
    def get_trace_statistic(self, r0: int) -> float:
        """
        Compute Johansen's trace statistic for testing H_0: r ≤ r0.
        
        The trace statistic is:
            LR_{trace}(r0) = -T Σ_{j=r0+1}^{k} ln(1 - λ_j)
        
        Parameters
        ----------
        r0 : int
            Null hypothesis rank.
            
        Returns
        -------
        trace_stat : float
            The trace test statistic.
        """
        if not self._fitted:
            raise RuntimeError("Model must be fitted first")
        
        if r0 < 0 or r0 >= self._k:
            raise ValueError(f"r0 must be in [0, k-1], got {r0}")
        
        T_eff = self._T - self.p
        
        trace_stat = -T_eff * np.sum(
            np.log(1 - self.eigenvalues[r0:] + 1e-14)
        )
        
        return trace_stat
    
    def get_max_eigenvalue_statistic(self, r0: int) -> float:
        """
        Compute Johansen's maximum eigenvalue statistic for testing H_0: r = r0 vs H_1: r = r0 + 1.
        
        The max eigenvalue statistic is:
            LR_{max}(r0) = -T ln(1 - λ_{r0+1})
        
        Parameters
        ----------
        r0 : int
            Null hypothesis rank.
            
        Returns
        -------
        max_stat : float
            The maximum eigenvalue test statistic.
        """
        if not self._fitted:
            raise RuntimeError("Model must be fitted first")
        
        if r0 < 0 or r0 >= self._k - 1:
            raise ValueError(f"r0 must be in [0, k-2], got {r0}")
        
        T_eff = self._T - self.p
        
        max_stat = -T_eff * np.log(1 - self.eigenvalues[r0] + 1e-14)
        
        return max_stat
    
    def predict(self, h: int = 1) -> NDArray:
        """
        Generate h-step ahead forecasts.
        
        Parameters
        ----------
        h : int
            Forecast horizon.
            
        Returns
        -------
        forecasts : ndarray of shape (h, k)
            Point forecasts.
        """
        if not self._fitted:
            raise RuntimeError("Model must be fitted first")
        
        Y = self._Y
        k = self._k
        p = self.p
        
        forecasts = np.zeros((h, k), dtype=np.float64)
        
        # Initialize with recent values
        Y_recent = Y[-p:, :].copy()
        
        for t in range(h):
            # Error correction term
            Y_last = Y_recent[-1, :]
            ec_term = self.alpha @ self.beta.T @ Y_last
            
            # Short-run dynamics
            sr_term = np.zeros(k)
            for j, Gamma_j in enumerate(self.Gamma):
                if j + 1 < len(Y_recent):
                    DY_lag = Y_recent[-j-1, :] - Y_recent[-j-2, :]
                    sr_term += Gamma_j @ DY_lag
            
            # Forecast
            DY_forecast = ec_term + sr_term
            Y_forecast = Y_last + DY_forecast
            
            forecasts[t, :] = Y_forecast
            
            # Update recent values
            Y_recent = np.vstack([Y_recent[1:, :], Y_forecast])
        
        return forecasts
    
    def summary(self) -> str:
        """
        Generate a summary of the estimation results.
        
        Returns
        -------
        summary_str : str
            Formatted summary string.
        """
        if not self._fitted:
            return "Model not fitted yet."
        
        lines = []
        lines.append("=" * 70)
        lines.append("Johansen VECM Estimation Results")
        lines.append("=" * 70)
        lines.append(f"Sample size (T):           {self._T}")
        lines.append(f"Effective sample size:     {self._T - self.p}")
        lines.append(f"Number of variables (k):   {self._k}")
        lines.append(f"Lag order (p):             {self.p}")
        lines.append(f"Cointegration rank (r):    {self._r}")
        lines.append(f"Include intercept:         {self.include_intercept}")
        lines.append("-" * 70)
        lines.append("Eigenvalues:")
        for i, ev in enumerate(self.eigenvalues):
            lines.append(f"  λ_{i+1} = {ev:.6f}")
        lines.append("-" * 70)
        lines.append(f"Log-likelihood:            {self.log_likelihood:.4f}")
        lines.append("-" * 70)
        lines.append("Cointegrating vectors (β):")
        lines.append(np.array2string(self.beta, precision=4, suppress_small=True))
        lines.append("-" * 70)
        lines.append("Adjustment coefficients (α):")
        lines.append(np.array2string(self.alpha, precision=4, suppress_small=True))
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def __repr__(self) -> str:
        if self._fitted:
            return f"JohansenVECM(p={self.p}, k={self._k}, r={self._r}, fitted=True)"
        else:
            return f"JohansenVECM(p={self.p}, fitted=False)"


def select_lag_order(
    Y: NDArray,
    max_p: int = 12,
    criterion: str = 'BIC',
    include_intercept: bool = True
) -> Tuple[int, Dict[str, NDArray]]:
    """
    Select optimal lag order for VAR/VECM using information criteria.
    
    Parameters
    ----------
    Y : ndarray of shape (T, k)
        The k-variate time series data.
    max_p : int
        Maximum lag order to consider.
    criterion : str
        Information criterion to use: 'AIC', 'BIC', or 'HQ'.
    include_intercept : bool
        Whether to include an intercept.
        
    Returns
    -------
    optimal_p : int
        Selected lag order.
    ic_values : dict
        Dictionary with arrays of IC values for each lag.
    """
    Y = np.asarray(Y, dtype=np.float64)
    T, k = Y.shape
    
    if max_p >= T - k - 2:
        max_p = T - k - 3
        warnings.warn(f"max_p reduced to {max_p} due to sample size constraints")
    
    aic_vals = np.zeros(max_p)
    bic_vals = np.zeros(max_p)
    hq_vals = np.zeros(max_p)
    
    for p in range(1, max_p + 1):
        try:
            # Fit VAR(p) to get residual covariance
            DY = np.diff(Y, axis=0)
            T_eff = T - p
            
            # Build lagged difference matrix
            X = np.zeros((T_eff, k * p), dtype=np.float64)
            for j in range(p):
                X[:, j*k:(j+1)*k] = DY[p-1-j:T-1-j, :]
            
            DY_dep = DY[p:, :]  # Dependent variable
            
            if include_intercept:
                X = np.hstack([np.ones((T_eff, 1)), X])
            
            # OLS estimation
            beta_hat = linalg.lstsq(X, DY_dep)[0]
            residuals = DY_dep - X @ beta_hat
            
            # Residual covariance
            Sigma = residuals.T @ residuals / T_eff
            
            # Log-likelihood (up to constant)
            sign, logdet = np.linalg.slogdet(Sigma)
            if sign <= 0:
                logdet = np.log(np.abs(np.linalg.det(Sigma)) + 1e-14)
            
            ll = -0.5 * T_eff * (k * np.log(2 * np.pi) + logdet + k)
            
            # Number of parameters
            n_params = k * (k * p + int(include_intercept))
            
            ic = information_criteria(ll, n_params, T_eff)
            
            aic_vals[p-1] = ic['AIC']
            bic_vals[p-1] = ic['BIC']
            hq_vals[p-1] = ic['HQ']
            
        except:
            aic_vals[p-1] = np.inf
            bic_vals[p-1] = np.inf
            hq_vals[p-1] = np.inf
    
    # Select optimal lag
    if criterion.upper() == 'AIC':
        optimal_p = np.argmin(aic_vals) + 1
    elif criterion.upper() == 'BIC':
        optimal_p = np.argmin(bic_vals) + 1
    elif criterion.upper() == 'HQ':
        optimal_p = np.argmin(hq_vals) + 1
    else:
        raise ValueError(f"Unknown criterion: {criterion}")
    
    ic_values = {
        'AIC': aic_vals,
        'BIC': bic_vals,
        'HQ': hq_vals,
        'lags': np.arange(1, max_p + 1)
    }
    
    return optimal_p, ic_values


def johansen_trace_test(
    Y: NDArray,
    p: int = 1,
    include_intercept: bool = True,
    significance_level: float = 0.05
) -> Dict[str, Any]:
    """
    Perform Johansen's trace test for cointegration rank.
    
    Tests the sequence of hypotheses:
        H_0: r = 0 vs H_1: r > 0
        H_0: r ≤ 1 vs H_1: r > 1
        ...
        H_0: r ≤ k-1 vs H_1: r = k
    
    Parameters
    ----------
    Y : ndarray of shape (T, k)
        The k-variate time series data.
    p : int
        Lag order for the VECM.
    include_intercept : bool
        Whether to include an intercept.
    significance_level : float
        Significance level for critical values.
        
    Returns
    -------
    dict with keys:
        'eigenvalues' : Eigenvalues
        'trace_statistics' : Trace statistics for each r0
        'critical_values' : Critical values (if available)
        'selected_rank' : Selected cointegration rank
    """
    Y = np.asarray(Y, dtype=np.float64)
    T, k = Y.shape
    
    # Fit with full rank to get eigenvalues
    model = JohansenVECM(p=p, include_intercept=include_intercept)
    model.fit(Y, r=k-1)  # Fit with maximum rank
    
    eigenvalues = model.eigenvalues
    trace_stats = np.zeros(k)
    
    T_eff = T - p
    
    for r0 in range(k):
        trace_stats[r0] = -T_eff * np.sum(np.log(1 - eigenvalues[r0:] + 1e-14))
    
    # Critical values (approximate, from Johansen & Juselius, 1990)
    # These are for the case with intercept in cointegrating relation
    # More precise values should be obtained from simulation
    critical_values_5pct = {
        1: [3.84],
        2: [15.41, 3.84],
        3: [29.68, 15.41, 3.84],
        4: [47.21, 29.68, 15.41, 3.84],
        5: [68.52, 47.21, 29.68, 15.41, 3.84],
        6: [94.15, 68.52, 47.21, 29.68, 15.41, 3.84]
    }
    
    if k in critical_values_5pct:
        cv = np.array(critical_values_5pct[k])
    else:
        # Approximate using asymptotic formula
        cv = np.zeros(k)
        for r0 in range(k):
            df = (k - r0) ** 2
            cv[r0] = 3.84 + 0.5 * (k - r0 - 1) * 7.5  # Rough approximation
    
    # Select rank
    selected_rank = 0
    for r0 in range(k):
        if trace_stats[r0] > cv[r0]:
            selected_rank = r0 + 1
        else:
            break
    
    return {
        'eigenvalues': eigenvalues,
        'trace_statistics': trace_stats,
        'critical_values': cv,
        'selected_rank': selected_rank,
        'p_value_approx': None  # Would need simulation
    }
