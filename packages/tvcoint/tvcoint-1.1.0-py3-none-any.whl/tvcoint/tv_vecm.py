"""
Time-Varying Vector Error Correction Model (TV-VECM) Estimation
================================================================

Implementation of the time-varying VECM as proposed in Bierens and Martins (2010).
This module extends Johansen's framework to allow the cointegrating vectors to
vary smoothly over time using Chebyshev time polynomials.

The model is:
    ΔY_t = α ξ' Y^{(m)}_{t-1} + Σ_{j=1}^{p-1} Γ_j ΔY_{t-j} + μ_0 + ε_t

where:
    Y^{(m)}_{t-1} = (Y'_{t-1}, P_{1,T}(t)Y'_{t-1}, ..., P_{m,T}(t)Y'_{t-1})'
    ξ = (ξ_0, ξ_1, ..., ξ_m)' with ξ_i being k×r matrices
    β_t = Σ_{i=0}^{m} ξ_i P_{i,T}(t)

Under the null hypothesis of time-invariant cointegration:
    ξ_1 = ξ_2 = ... = ξ_m = 0
    
so that β_t = ξ_0 = β (constant).

Reference:
    Bierens, H.J. and Martins, L.F. (2010). "Time-Varying Cointegration."
    Econometric Theory, 26(5), 1453-1490.
"""

import numpy as np
from scipy import linalg
from typing import Tuple, Optional, Dict, Any, List, Union
from numpy.typing import NDArray
import warnings

from .chebyshev import (
    chebyshev_polynomial_matrix,
    construct_extended_y,
    construct_time_varying_beta,
    chebyshev_basis_for_estimation
)
from .utils import (
    compute_differenced_data,
    compute_residual_matrices,
    solve_generalized_eigenvalue,
    orthogonal_complement,
    information_criteria
)


class TimeVaryingVECM:
    """
    Time-Varying Vector Error Correction Model Estimation.
    
    This class implements the ML estimation procedure for time-varying
    cointegration as described in Bierens and Martins (2010). The cointegrating
    vectors β_t are modeled as smooth functions of time using Chebyshev polynomials:
    
        β_t = Σ_{i=0}^{m} ξ_i P_{i,T}(t)
    
    where P_{i,T}(t) are Chebyshev time polynomials.
    
    Parameters
    ----------
    p : int
        Lag order for the underlying VAR. The VECM has p-1 lagged differences.
    m : int
        Order of Chebyshev polynomial expansion for time-varying parameters.
    include_intercept : bool, optional
        Whether to include an intercept term (default: True).
        This corresponds to the "drift case" in Section 5 of the paper.
        
    Attributes
    ----------
    eigenvalues : ndarray of shape (k*(m+1),)
        Ordered eigenvalues from the extended reduced rank regression.
    eigenvectors : ndarray of shape (k*(m+1), k*(m+1))
        Corresponding eigenvectors.
    xi : ndarray of shape ((m+1)*k, r)
        Estimated Chebyshev coefficients (vectorized ξ_0, ξ_1, ..., ξ_m).
    alpha : ndarray of shape (k, r)
        Estimated adjustment matrix.
    beta_t : ndarray of shape (T, k, r)
        Time-varying cointegrating vectors β_t for each time period.
    log_likelihood : float
        Maximized log-likelihood value.
    S00, S11, S01 : ndarray
        Residual moment matrices from the concentrated likelihood.
        
    Examples
    --------
    >>> import numpy as np
    >>> from tvcoint.tv_vecm import TimeVaryingVECM
    >>> # Simulate data
    >>> T, k = 200, 2
    >>> Y = np.cumsum(np.random.randn(T, k), axis=0)
    >>> # Estimate TV-VECM
    >>> model = TimeVaryingVECM(p=2, m=2)
    >>> model.fit(Y, r=1)
    >>> print(f"Log-likelihood: {model.log_likelihood:.4f}")
    """
    
    def __init__(self, p: int = 1, m: int = 1, include_intercept: bool = True):
        """
        Initialize the Time-Varying VECM estimator.
        
        Parameters
        ----------
        p : int
            Lag order for the underlying VAR (p >= 1).
        m : int
            Order of Chebyshev polynomial expansion (m >= 0).
            m = 0 corresponds to standard (time-invariant) cointegration.
        include_intercept : bool
            Whether to include an intercept in the model.
        """
        if p < 1:
            raise ValueError(f"Lag order p must be at least 1, got {p}")
        if m < 0:
            raise ValueError(f"Chebyshev order m must be non-negative, got {m}")
        
        self.p = p
        self.m = m
        self.include_intercept = include_intercept
        
        # Results (populated after fit)
        self.eigenvalues = None
        self.eigenvectors = None
        self.xi = None
        self.alpha = None
        self.beta_t = None
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
        
    def fit(self, Y: NDArray, r: int) -> 'TimeVaryingVECM':
        """
        Fit the time-varying VECM model using ML estimation.
        
        The estimation follows Section 3.1 of Bierens and Martins (2010):
        
        1. Construct the extended Y matrix Y^{(m)}_{t-1}
        2. Compute residual moment matrices S_{00}, S^{(m)}_{11}, S^{(m)}_{01}
        3. Solve the generalized eigenvalue problem
        4. Extract the r largest eigenvalues and corresponding eigenvectors
        5. Recover time-varying β_t from the Chebyshev expansion
        
        Parameters
        ----------
        Y : ndarray of shape (T, k)
            The k-variate time series data.
        r : int
            Assumed cointegration rank (0 < r < k).
            
        Returns
        -------
        self : TimeVaryingVECM
            Fitted model instance.
        """
        Y = np.asarray(Y, dtype=np.float64)
        
        if Y.ndim != 2:
            raise ValueError(f"Y must be 2-dimensional, got {Y.ndim}")
        
        T, k = Y.shape
        m = self.m
        
        if r < 1 or r >= k:
            raise ValueError(f"Cointegration rank r={r} must satisfy 0 < r < k={k}")
        
        if T < k * (m + 1) + self.p + 1:
            raise ValueError(
                f"Sample size T={T} too small for k={k}, m={m}, p={self.p}. "
                f"Need T >= {k * (m + 1) + self.p + 1}"
            )
        
        self._Y = Y
        self._k = k
        self._T = T
        self._r = r
        
        # Step 1: Prepare data matrices
        # Compute differenced data
        DY = np.diff(Y, axis=0)  # Shape: (T-1, k)
        
        # Construct extended Y^{(m)}_{t-1} - equation (4)
        Y_extended = construct_extended_y(Y, m)  # Shape: (T-1, k*(m+1))
        
        # Construct lagged differences X_t if p > 1
        if self.p > 1:
            T_eff = T - self.p
            
            # Adjust DY and Y_extended to match effective sample
            DY_adj = DY[self.p-1:, :]  # Shape: (T_eff, k)
            Y_ext_adj = Y_extended[self.p-1:, :]  # Shape: (T_eff, k*(m+1))
            
            # Build lagged differences matrix
            X = np.zeros((T_eff, k * (self.p - 1)), dtype=np.float64)
            for j in range(1, self.p):
                X[:, (j-1)*k:j*k] = DY[self.p-1-j:T-1-j, :]
        else:
            T_eff = T - 1
            DY_adj = DY
            Y_ext_adj = Y_extended
            X = None
        
        # Step 2: Compute residual moment matrices - Section 3.1
        self.S00, self.S11, self.S01 = compute_residual_matrices(
            DY_adj, Y_ext_adj, X, self.include_intercept
        )
        
        # Step 3: Solve generalized eigenvalue problem - equation (5)
        self.eigenvalues, self.eigenvectors = solve_generalized_eigenvalue(
            self.S00, self.S11, self.S01
        )
        
        # Step 4: Extract ξ (vectorized Chebyshev coefficients) for rank r
        # The first r eigenvectors correspond to ξ
        self.xi = self.eigenvectors[:, :r].copy()  # Shape: (k*(m+1), r)
        
        # Step 5: Compute α from the relationship
        # α = S_{01} ξ (ξ' S_{11} ξ)^{-1}
        xi_S11_xi = self.xi.T @ self.S11 @ self.xi
        if np.abs(linalg.det(xi_S11_xi)) > 1e-14:
            self.alpha = self.S01 @ self.xi @ linalg.inv(xi_S11_xi)
        else:
            self.alpha = self.S01 @ self.xi @ linalg.pinv(xi_S11_xi)
        
        # Step 6: Reconstruct time-varying β_t from ξ - equation (2)
        self._reconstruct_beta_t()
        
        # Step 7: Estimate Γ matrices (short-run dynamics)
        self._estimate_gamma(DY_adj, Y_ext_adj, X)
        
        # Step 8: Estimate Ω (error covariance)
        self._estimate_omega(DY_adj, Y_ext_adj, X)
        
        # Step 9: Compute log-likelihood
        self._compute_log_likelihood(T_eff)
        
        self._fitted = True
        
        return self
    
    def _reconstruct_beta_t(self) -> None:
        """
        Reconstruct time-varying cointegrating vectors β_t from Chebyshev coefficients.
        
        From equation (2): β_t = Σ_{i=0}^{m} ξ_i P_{i,T}(t)
        
        where ξ_i is stored in self.xi[i*k:(i+1)*k, :].
        """
        T = self._T
        k = self._k
        r = self._r
        m = self.m
        
        # Get Chebyshev polynomial matrix
        P = chebyshev_polynomial_matrix(T, m)  # Shape: (T, m+1)
        
        # Initialize β_t
        self.beta_t = np.zeros((T, k, r), dtype=np.float64)
        
        # Reconstruct: β_t = Σ_{i=0}^{m} ξ_i P_{i,T}(t)
        for t in range(T):
            for i in range(m + 1):
                xi_i = self.xi[i*k:(i+1)*k, :]  # Shape: (k, r)
                self.beta_t[t, :, :] += xi_i * P[t, i]
    
    def _estimate_gamma(
        self, 
        DY: NDArray, 
        Y_extended: NDArray, 
        X: Optional[NDArray]
    ) -> None:
        """Estimate short-run dynamics matrices Γ_j."""
        T_eff, k = DY.shape
        
        # Compute error correction term at each time
        # EC_t = α ξ' Y^{(m)}_{t-1}
        ec_term = Y_extended @ self.xi @ self.alpha.T  # Shape: (T_eff, k)
        
        # Residuals after removing EC term
        DY_adj = DY - ec_term
        
        if X is not None and X.shape[1] > 0:
            # Estimate Γ from OLS
            Gamma_mat = linalg.lstsq(X, DY_adj)[0]
            
            self.Gamma = []
            n_lags = X.shape[1] // k
            for j in range(n_lags):
                self.Gamma.append(Gamma_mat[j*k:(j+1)*k, :].T)
        else:
            self.Gamma = []
    
    def _estimate_omega(
        self,
        DY: NDArray,
        Y_extended: NDArray,
        X: Optional[NDArray]
    ) -> None:
        """Estimate error covariance matrix Ω."""
        T_eff, k = DY.shape
        
        # Compute fitted values
        ec_term = Y_extended @ self.xi @ self.alpha.T
        fitted = ec_term
        
        if X is not None and X.shape[1] > 0 and len(self.Gamma) > 0:
            Gamma_mat = np.vstack([G.T for G in self.Gamma])
            fitted += X @ Gamma_mat
        
        # Residuals
        residuals = DY - fitted
        
        # Estimate Ω
        self.Omega = residuals.T @ residuals / T_eff
    
    def _compute_log_likelihood(self, T_eff: int) -> None:
        """
        Compute the maximized log-likelihood.
        
        From Section 3.1, the log-likelihood for the TV-VECM with rank r is:
            l_T(r, m) = -0.5 * T * Σ_{j=1}^{r} ln(1 - λ_{m,j}) - 0.5 * T * ln(det(S00))
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
    
    def get_beta_at_time(self, t: int) -> NDArray:
        """
        Get the cointegrating vectors at a specific time.
        
        Parameters
        ----------
        t : int
            Time index (1-based, as in the paper).
            
        Returns
        -------
        beta : ndarray of shape (k, r)
            Cointegrating vectors at time t.
        """
        if not self._fitted:
            raise RuntimeError("Model must be fitted first")
        
        if t < 1 or t > self._T:
            raise ValueError(f"Time t={t} must be in [1, {self._T}]")
        
        return self.beta_t[t-1, :, :]
    
    def get_xi_coefficients(self) -> List[NDArray]:
        """
        Get the Chebyshev coefficients ξ_0, ξ_1, ..., ξ_m as separate matrices.
        
        Returns
        -------
        xi_list : list of ndarray
            List of (k, r) matrices [ξ_0, ξ_1, ..., ξ_m].
        """
        if not self._fitted:
            raise RuntimeError("Model must be fitted first")
        
        k = self._k
        r = self._r
        m = self.m
        
        xi_list = []
        for i in range(m + 1):
            xi_i = self.xi[i*k:(i+1)*k, :]
            xi_list.append(xi_i.copy())
        
        return xi_list
    
    def test_time_invariance(self) -> Dict[str, float]:
        """
        Quick diagnostic for whether cointegrating vectors appear time-varying.
        
        Computes the ratio of variation in higher-order Chebyshev coefficients
        relative to the constant term.
        
        Returns
        -------
        dict with keys:
            'variation_ratio' : Ratio of ||ξ_1, ..., ξ_m|| / ||ξ_0||
            'max_coefficient_norm' : Maximum norm among ξ_1, ..., ξ_m
        """
        if not self._fitted:
            raise RuntimeError("Model must be fitted first")
        
        xi_list = self.get_xi_coefficients()
        
        # Norm of constant term
        xi_0_norm = linalg.norm(xi_list[0], 'fro')
        
        # Norms of time-varying terms
        tv_norms = [linalg.norm(xi_i, 'fro') for xi_i in xi_list[1:]]
        
        if xi_0_norm > 1e-14:
            variation_ratio = np.sum(tv_norms) / xi_0_norm
        else:
            variation_ratio = np.inf if np.sum(tv_norms) > 0 else 0
        
        max_tv_norm = max(tv_norms) if tv_norms else 0
        
        return {
            'variation_ratio': variation_ratio,
            'max_coefficient_norm': max_tv_norm
        }
    
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
        lines.append("Time-Varying VECM Estimation Results")
        lines.append("Bierens and Martins (2010) Framework")
        lines.append("=" * 70)
        lines.append(f"Sample size (T):              {self._T}")
        lines.append(f"Effective sample size:        {self._T - self.p}")
        lines.append(f"Number of variables (k):      {self._k}")
        lines.append(f"Lag order (p):                {self.p}")
        lines.append(f"Chebyshev order (m):          {self.m}")
        lines.append(f"Cointegration rank (r):       {self._r}")
        lines.append(f"Include intercept:            {self.include_intercept}")
        lines.append("-" * 70)
        lines.append(f"Number of TV-VECM parameters: {self._k * (self.m + 1) * self._r}")
        lines.append("-" * 70)
        lines.append("First 10 eigenvalues:")
        for i, ev in enumerate(self.eigenvalues[:min(10, len(self.eigenvalues))]):
            lines.append(f"  λ_{i+1} = {ev:.6f}")
        lines.append("-" * 70)
        lines.append(f"Log-likelihood:               {self.log_likelihood:.4f}")
        lines.append("-" * 70)
        
        # Time variation diagnostic
        tv_diag = self.test_time_invariance()
        lines.append("Time-variation diagnostics:")
        lines.append(f"  Variation ratio:            {tv_diag['variation_ratio']:.6f}")
        lines.append(f"  Max TV coefficient norm:    {tv_diag['max_coefficient_norm']:.6f}")
        lines.append("-" * 70)
        
        # Chebyshev coefficients
        xi_list = self.get_xi_coefficients()
        lines.append("Chebyshev coefficients (ξ_0 = constant term):")
        for i, xi_i in enumerate(xi_list[:3]):  # Show first 3
            lines.append(f"  ξ_{i}:")
            lines.append(np.array2string(xi_i, precision=4, suppress_small=True))
        if len(xi_list) > 3:
            lines.append(f"  ... ({len(xi_list) - 3} more coefficients)")
        
        lines.append("-" * 70)
        lines.append("Adjustment coefficients (α):")
        lines.append(np.array2string(self.alpha, precision=4, suppress_small=True))
        lines.append("-" * 70)
        
        # β_t at selected time points
        lines.append("Cointegrating vectors at selected times:")
        for t in [1, self._T // 4, self._T // 2, 3 * self._T // 4, self._T]:
            t = min(t, self._T)
            lines.append(f"  β(t={t}):")
            lines.append(np.array2string(self.beta_t[t-1], precision=4, suppress_small=True))
        
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def __repr__(self) -> str:
        if self._fitted:
            return (
                f"TimeVaryingVECM(p={self.p}, m={self.m}, "
                f"k={self._k}, r={self._r}, fitted=True)"
            )
        else:
            return f"TimeVaryingVECM(p={self.p}, m={self.m}, fitted=False)"


def estimate_tv_vecm(
    Y: NDArray,
    r: int,
    p: int = 1,
    m: int = 1,
    include_intercept: bool = True
) -> TimeVaryingVECM:
    """
    Convenience function to estimate a time-varying VECM.
    
    Parameters
    ----------
    Y : ndarray of shape (T, k)
        The k-variate time series data.
    r : int
        Cointegration rank.
    p : int
        Lag order.
    m : int
        Chebyshev polynomial order.
    include_intercept : bool
        Whether to include intercept.
        
    Returns
    -------
    model : TimeVaryingVECM
        Fitted TV-VECM model.
        
    Examples
    --------
    >>> import numpy as np
    >>> from tvcoint import estimate_tv_vecm
    >>> Y = np.random.randn(200, 2)
    >>> Y[:, 1] = np.cumsum(Y[:, 0]) + np.random.randn(200) * 0.1
    >>> model = estimate_tv_vecm(Y, r=1, p=2, m=2)
    """
    model = TimeVaryingVECM(p=p, m=m, include_intercept=include_intercept)
    model.fit(Y, r=r)
    return model


def select_chebyshev_order(
    Y: NDArray,
    r: int,
    p: int = 1,
    max_m: int = 5,
    criterion: str = 'BIC',
    include_intercept: bool = True
) -> Tuple[int, Dict[str, NDArray]]:
    """
    Select optimal Chebyshev order m using information criteria.
    
    Similar to lag order selection for VAR, this function helps determine
    the appropriate degree of time variation in the cointegrating vectors.
    
    Parameters
    ----------
    Y : ndarray of shape (T, k)
        The k-variate time series data.
    r : int
        Cointegration rank.
    p : int
        Lag order.
    max_m : int
        Maximum Chebyshev order to consider.
    criterion : str
        Information criterion: 'AIC', 'BIC', or 'HQ'.
    include_intercept : bool
        Whether to include intercept.
        
    Returns
    -------
    optimal_m : int
        Selected Chebyshev order.
    ic_values : dict
        Dictionary with IC values for each m.
    """
    Y = np.asarray(Y, dtype=np.float64)
    T, k = Y.shape
    
    aic_vals = np.zeros(max_m + 1)
    bic_vals = np.zeros(max_m + 1)
    hq_vals = np.zeros(max_m + 1)
    ll_vals = np.zeros(max_m + 1)
    
    for m in range(max_m + 1):
        try:
            # Check sample size constraints
            if T < k * (m + 1) + p + 5:
                aic_vals[m] = np.inf
                bic_vals[m] = np.inf
                hq_vals[m] = np.inf
                continue
            
            model = TimeVaryingVECM(p=p, m=m, include_intercept=include_intercept)
            model.fit(Y, r=r)
            
            ll = model.log_likelihood
            ll_vals[m] = ll
            
            # Number of free parameters
            # α: k × r
            # ξ: (m+1) × k × r (but some normalization needed)
            # Γ: (p-1) × k × k
            # Ω: k × (k+1) / 2 (symmetric)
            n_params = (
                k * r +  # α
                (m + 1) * k * r - r * r +  # ξ (with normalization)
                (p - 1) * k * k +  # Γ
                k * (k + 1) // 2 +  # Ω
                k * int(include_intercept)  # intercept
            )
            
            T_eff = T - p
            ic = information_criteria(ll, n_params, T_eff)
            
            aic_vals[m] = ic['AIC']
            bic_vals[m] = ic['BIC']
            hq_vals[m] = ic['HQ']
            
        except Exception as e:
            warnings.warn(f"Estimation failed for m={m}: {str(e)}")
            aic_vals[m] = np.inf
            bic_vals[m] = np.inf
            hq_vals[m] = np.inf
    
    # Select optimal m
    valid_mask = np.isfinite(bic_vals)
    if not np.any(valid_mask):
        raise RuntimeError("All estimations failed")
    
    if criterion.upper() == 'AIC':
        optimal_m = np.argmin(np.where(valid_mask, aic_vals, np.inf))
    elif criterion.upper() == 'BIC':
        optimal_m = np.argmin(np.where(valid_mask, bic_vals, np.inf))
    elif criterion.upper() == 'HQ':
        optimal_m = np.argmin(np.where(valid_mask, hq_vals, np.inf))
    else:
        raise ValueError(f"Unknown criterion: {criterion}")
    
    ic_values = {
        'AIC': aic_vals,
        'BIC': bic_vals,
        'HQ': hq_vals,
        'log_likelihood': ll_vals,
        'm_values': np.arange(max_m + 1)
    }
    
    return int(optimal_m), ic_values
