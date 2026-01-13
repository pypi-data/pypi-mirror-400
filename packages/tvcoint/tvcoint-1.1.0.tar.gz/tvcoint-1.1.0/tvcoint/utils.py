"""
Utility Functions Module
========================

Utility functions for the tvcoint package, including matrix operations,
numerical procedures, and data preparation functions.

Reference:
    Bierens, H.J. and Martins, L.F. (2010). "Time-Varying Cointegration."
    Econometric Theory, 26(5), 1453-1490.
"""

import numpy as np
from scipy import linalg
from typing import Tuple, Optional, Union, List
from numpy.typing import NDArray
import warnings


def compute_differenced_data(Y: NDArray, p: int = 1) -> Tuple[NDArray, NDArray, NDArray]:
    """
    Compute first differences and prepare lagged data for VECM estimation.
    
    Parameters
    ----------
    Y : ndarray of shape (T, k)
        The k-variate time series data.
    p : int, optional
        Lag order for the VECM. Default is 1.
        
    Returns
    -------
    DY : ndarray of shape (T_eff, k)
        First differences ΔY_t for t = p+1, ..., T.
    Y_lag1 : ndarray of shape (T_eff, k)
        Lagged levels Y_{t-1} for t = p+1, ..., T.
    X : ndarray of shape (T_eff, k*(p-1)) or None
        Lagged differences [ΔY_{t-1}, ..., ΔY_{t-p+1}] if p > 1, None otherwise.
    """
    Y = np.asarray(Y, dtype=np.float64)
    T, k = Y.shape
    
    # Compute first differences
    DY_full = np.diff(Y, axis=0)  # Shape: (T-1, k)
    
    if p == 1:
        # Simple case: no lagged differences needed
        DY = DY_full[p-1:, :]  # ΔY_t for t = 1, ..., T-1 (using 0-based: from index 0)
        Y_lag1 = Y[p-1:-1, :]   # Y_{t-1} for t = 1, ..., T-1
        X = None
    else:
        # VECM(p) case: need lagged differences
        T_eff = T - p
        DY = DY_full[p-1:, :]  # ΔY_t for t = p, ..., T-1
        Y_lag1 = Y[p-1:-1, :]  # Y_{t-1} for t = p, ..., T-1
        
        # Construct lagged differences
        X = np.zeros((T_eff, k * (p - 1)), dtype=np.float64)
        for j in range(1, p):
            X[:, (j-1)*k:j*k] = DY_full[p-1-j:T-1-j, :]
    
    return DY, Y_lag1, X


def compute_residual_matrices(
    DY: NDArray,
    Y_extended: NDArray,
    X: Optional[NDArray] = None,
    include_intercept: bool = False
) -> Tuple[NDArray, NDArray, NDArray]:
    """
    Compute the residual moment matrices S_{00}, S_{11}, S_{01} for ML estimation.
    
    As defined in Section 3.1 of Bierens and Martins (2010):
        S_{00,T} = (1/T) Σ ΔY_t ΔY'_t - Σ̂_{XΔY}' Σ̂_{XX}^{-1} Σ̂_{XΔY}
        S_{11,T} = (1/T) Σ Y^{(m)}_{t-1} Y^{(m)'}_{t-1} - Σ̂_{XY}' Σ̂_{XX}^{-1} Σ̂_{XY}
        S_{01,T} = (1/T) Σ ΔY_t Y^{(m)'}_{t-1} - Σ̂_{XΔY}' Σ̂_{XX}^{-1} Σ̂_{XY}
    
    Parameters
    ----------
    DY : ndarray of shape (T_eff, k)
        First differences ΔY_t.
    Y_extended : ndarray of shape (T_eff, k*(m+1))
        Extended Y matrix Y^{(m)}_{t-1}.
    X : ndarray of shape (T_eff, n_x) or None
        Regressors to be partialled out (lagged differences, intercept).
    include_intercept : bool
        Whether to include an intercept term.
        
    Returns
    -------
    S00 : ndarray of shape (k, k)
        Residual moment matrix for ΔY.
    S11 : ndarray of shape (k*(m+1), k*(m+1))
        Residual moment matrix for Y^{(m)}_{t-1}.
    S01 : ndarray of shape (k, k*(m+1))
        Cross moment matrix.
    """
    T_eff = DY.shape[0]
    
    # Add intercept to X if requested
    if include_intercept:
        intercept = np.ones((T_eff, 1), dtype=np.float64)
        if X is not None:
            X = np.hstack([intercept, X])
        else:
            X = intercept
    
    if X is not None and X.shape[1] > 0:
        # Partial out X using OLS
        # Residuals: R0 = DY - X @ (X'X)^{-1} X' DY
        #            R1 = Y_ext - X @ (X'X)^{-1} X' Y_ext
        
        XtX = X.T @ X
        XtX_inv = linalg.inv(XtX)
        
        XtDY = X.T @ DY
        XtY_ext = X.T @ Y_extended
        
        R0 = DY - X @ (XtX_inv @ XtDY)
        R1 = Y_extended - X @ (XtX_inv @ XtY_ext)
    else:
        R0 = DY
        R1 = Y_extended
    
    # Compute moment matrices
    S00 = R0.T @ R0 / T_eff
    S11 = R1.T @ R1 / T_eff
    S01 = R0.T @ R1 / T_eff
    
    return S00, S11, S01


def solve_generalized_eigenvalue(
    S00: NDArray,
    S11: NDArray,
    S01: NDArray
) -> Tuple[NDArray, NDArray]:
    """
    Solve the generalized eigenvalue problem for cointegration analysis.
    
    Solves: det(λ S11 - S10 S00^{-1} S01) = 0
    
    As described in equation (5) of Bierens and Martins (2010).
    
    Parameters
    ----------
    S00 : ndarray of shape (k, k)
        Residual moment matrix for ΔY.
    S11 : ndarray of shape (n, n)
        Residual moment matrix for Y^{(m)}_{t-1}.
    S01 : ndarray of shape (k, n)
        Cross moment matrix.
        
    Returns
    -------
    eigenvalues : ndarray of shape (min(k, n),)
        Ordered eigenvalues λ_1 ≥ λ_2 ≥ ... ≥ λ_r.
    eigenvectors : ndarray of shape (n, min(k, n))
        Corresponding eigenvectors (columns).
        
    Notes
    -----
    The eigenvalues are guaranteed to be in [0, 1] and the eigenvectors
    are normalized such that V' S11 V = I.
    """
    k = S00.shape[0]
    n = S11.shape[0]
    
    # Compute S00^{-1/2}
    S00_eigvals, S00_eigvecs = linalg.eigh(S00)
    
    # Handle numerical issues with small eigenvalues
    S00_eigvals = np.maximum(S00_eigvals, 1e-14)
    
    S00_inv_sqrt = S00_eigvecs @ np.diag(1.0 / np.sqrt(S00_eigvals)) @ S00_eigvecs.T
    
    # Form the matrix: S00^{-1/2} S01 S11^{-1} S10 S00^{-1/2}
    # But we solve a different form to avoid inverting S11
    
    # Alternative: solve the generalized eigenvalue problem
    # S10 S00^{-1} S01 v = λ S11 v
    
    S10 = S01.T
    S00_inv = linalg.inv(S00)
    
    A = S10 @ S00_inv @ S01
    B = S11
    
    try:
        # Use scipy's generalized eigenvalue solver
        eigenvalues, eigenvectors = linalg.eig(A, B)
        
        # Extract real parts (should be real for symmetric matrices)
        eigenvalues = np.real(eigenvalues)
        eigenvectors = np.real(eigenvectors)
        
        # Clip eigenvalues to [0, 1] to handle numerical issues
        eigenvalues = np.clip(eigenvalues, 0, 1)
        
        # Sort in descending order
        idx = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]
        
    except linalg.LinAlgError:
        # Fallback: use pseudo-inverse
        warnings.warn("Generalized eigenvalue problem: using pseudo-inverse fallback")
        B_inv = linalg.pinv(B)
        eigenvalues, eigenvectors = linalg.eig(B_inv @ A)
        eigenvalues = np.real(eigenvalues)
        eigenvectors = np.real(eigenvectors)
        eigenvalues = np.clip(eigenvalues, 0, 1)
        idx = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]
    
    # Normalize eigenvectors: V' S11 V = I
    for j in range(eigenvectors.shape[1]):
        v = eigenvectors[:, j:j+1]
        norm = np.sqrt(v.T @ S11 @ v)[0, 0]
        if norm > 1e-14:
            eigenvectors[:, j] /= norm
    
    return eigenvalues, eigenvectors


def ols_residuals(Y: NDArray, X: NDArray) -> NDArray:
    """
    Compute OLS residuals.
    
    Parameters
    ----------
    Y : ndarray of shape (n, k)
        Dependent variables.
    X : ndarray of shape (n, p)
        Regressors.
        
    Returns
    -------
    residuals : ndarray of shape (n, k)
        OLS residuals.
    """
    if X.shape[0] != Y.shape[0]:
        raise ValueError("X and Y must have same number of rows")
    
    beta = linalg.lstsq(X, Y)[0]
    residuals = Y - X @ beta
    
    return residuals


def matrix_sqrt(A: NDArray) -> NDArray:
    """
    Compute the matrix square root of a positive semi-definite matrix.
    
    Parameters
    ----------
    A : ndarray of shape (n, n)
        Positive semi-definite matrix.
        
    Returns
    -------
    A_sqrt : ndarray of shape (n, n)
        Matrix square root such that A_sqrt @ A_sqrt.T = A.
    """
    eigvals, eigvecs = linalg.eigh(A)
    eigvals = np.maximum(eigvals, 0)  # Ensure non-negative
    return eigvecs @ np.diag(np.sqrt(eigvals)) @ eigvecs.T


def matrix_sqrt_inv(A: NDArray, tol: float = 1e-14) -> NDArray:
    """
    Compute the inverse square root of a positive definite matrix.
    
    Parameters
    ----------
    A : ndarray of shape (n, n)
        Positive definite matrix.
    tol : float
        Tolerance for eigenvalue truncation.
        
    Returns
    -------
    A_inv_sqrt : ndarray of shape (n, n)
        Inverse matrix square root such that A_inv_sqrt @ A @ A_inv_sqrt = I.
    """
    eigvals, eigvecs = linalg.eigh(A)
    eigvals = np.maximum(eigvals, tol)
    return eigvecs @ np.diag(1.0 / np.sqrt(eigvals)) @ eigvecs.T


def orthogonal_complement(A: NDArray) -> NDArray:
    """
    Compute the orthogonal complement of a matrix.
    
    Parameters
    ----------
    A : ndarray of shape (n, r)
        Matrix with r linearly independent columns (r < n).
        
    Returns
    -------
    A_perp : ndarray of shape (n, n-r)
        Orthogonal complement such that A.T @ A_perp = 0.
    """
    n, r = A.shape
    
    if r >= n:
        raise ValueError(f"Matrix must have fewer columns ({r}) than rows ({n})")
    
    # Use QR decomposition
    Q, R = linalg.qr(A, mode='full')
    
    # The last n-r columns of Q form the orthogonal complement
    A_perp = Q[:, r:]
    
    return A_perp


def vec(A: NDArray) -> NDArray:
    """
    Vectorize a matrix column by column.
    
    Parameters
    ----------
    A : ndarray of shape (m, n)
        Input matrix.
        
    Returns
    -------
    v : ndarray of shape (m*n,)
        Vectorized matrix.
    """
    return A.flatten('F')


def unvec(v: NDArray, shape: Tuple[int, int]) -> NDArray:
    """
    Reshape a vector into a matrix.
    
    Parameters
    ----------
    v : ndarray of shape (m*n,)
        Input vector.
    shape : tuple of (m, n)
        Target shape.
        
    Returns
    -------
    A : ndarray of shape (m, n)
        Reshaped matrix.
    """
    return v.reshape(shape, order='F')


def kronecker_product(A: NDArray, B: NDArray) -> NDArray:
    """
    Compute the Kronecker product A ⊗ B.
    
    Parameters
    ----------
    A : ndarray of shape (m, n)
        First matrix.
    B : ndarray of shape (p, q)
        Second matrix.
        
    Returns
    -------
    C : ndarray of shape (m*p, n*q)
        Kronecker product.
    """
    return np.kron(A, B)


def check_stationarity(Y: NDArray, max_lag: int = 12) -> dict:
    """
    Check if a time series appears to be stationary using simple diagnostics.
    
    Parameters
    ----------
    Y : ndarray of shape (T,) or (T, k)
        Time series data.
    max_lag : int
        Maximum lag for autocorrelation computation.
        
    Returns
    -------
    dict with keys:
        'mean' : Mean of each series
        'std' : Standard deviation of each series
        'autocorr' : Autocorrelation at lag 1 for each series
        'appears_stationary' : Boolean indicating if series appears stationary
    """
    Y = np.asarray(Y, dtype=np.float64)
    
    if Y.ndim == 1:
        Y = Y.reshape(-1, 1)
    
    T, k = Y.shape
    
    # Compute mean and std
    mean = np.mean(Y, axis=0)
    std = np.std(Y, axis=0)
    
    # Compute first-order autocorrelation
    autocorr = np.zeros(k)
    for j in range(k):
        y = Y[:, j]
        y_demean = y - np.mean(y)
        if np.var(y_demean) > 1e-14:
            autocorr[j] = np.corrcoef(y_demean[:-1], y_demean[1:])[0, 1]
        else:
            autocorr[j] = 0
    
    # Simple heuristic: high autocorrelation suggests non-stationarity
    appears_stationary = np.all(np.abs(autocorr) < 0.9)
    
    return {
        'mean': mean,
        'std': std,
        'autocorr': autocorr,
        'appears_stationary': appears_stationary
    }


def lag_matrix(Y: NDArray, p: int) -> NDArray:
    """
    Create a matrix of lagged values.
    
    Parameters
    ----------
    Y : ndarray of shape (T, k)
        Time series data.
    p : int
        Number of lags.
        
    Returns
    -------
    Y_lagged : ndarray of shape (T-p, k*p)
        Matrix where each row contains [Y_{t-1}, Y_{t-2}, ..., Y_{t-p}].
    """
    Y = np.asarray(Y, dtype=np.float64)
    T, k = Y.shape
    
    if p >= T:
        raise ValueError(f"Number of lags p={p} must be less than T={T}")
    
    Y_lagged = np.zeros((T - p, k * p), dtype=np.float64)
    
    for j in range(p):
        Y_lagged[:, j*k:(j+1)*k] = Y[p-1-j:T-1-j, :]
    
    return Y_lagged


def information_criteria(
    log_likelihood: float,
    n_params: int,
    T: int
) -> dict:
    """
    Compute information criteria for model selection.
    
    Parameters
    ----------
    log_likelihood : float
        Log-likelihood value.
    n_params : int
        Number of estimated parameters.
    T : int
        Sample size.
        
    Returns
    -------
    dict with keys:
        'AIC' : Akaike Information Criterion
        'BIC' : Bayesian (Schwarz) Information Criterion
        'HQ' : Hannan-Quinn Criterion
    """
    aic = -2 * log_likelihood + 2 * n_params
    bic = -2 * log_likelihood + n_params * np.log(T)
    hq = -2 * log_likelihood + 2 * n_params * np.log(np.log(T))
    
    return {
        'AIC': aic,
        'BIC': bic,
        'HQ': hq
    }


def simulate_cointegrated_system(
    T: int,
    k: int,
    r: int,
    alpha: Optional[NDArray] = None,
    beta: Optional[NDArray] = None,
    Omega: Optional[NDArray] = None,
    seed: Optional[int] = None
) -> Tuple[NDArray, dict]:
    """
    Simulate a cointegrated time series system.
    
    Generates data from:
        ΔY_t = α β' Y_{t-1} + ε_t
        ε_t ~ N(0, Ω)
    
    Parameters
    ----------
    T : int
        Sample size.
    k : int
        Number of variables.
    r : int
        Cointegration rank.
    alpha : ndarray of shape (k, r), optional
        Adjustment matrix. Default: random.
    beta : ndarray of shape (k, r), optional
        Cointegrating vectors. Default: first r columns of identity.
    Omega : ndarray of shape (k, k), optional
        Error covariance matrix. Default: identity.
    seed : int, optional
        Random seed for reproducibility.
        
    Returns
    -------
    Y : ndarray of shape (T, k)
        Simulated time series.
    params : dict
        True parameters used in simulation.
    """
    if seed is not None:
        np.random.seed(seed)
    
    if r > k:
        raise ValueError(f"Cointegration rank r={r} cannot exceed k={k}")
    
    # Default parameters
    if alpha is None:
        alpha = -0.1 * np.random.randn(k, r)
    
    if beta is None:
        beta = np.eye(k, r)
    
    if Omega is None:
        Omega = np.eye(k)
    
    # Generate errors
    L = linalg.cholesky(Omega, lower=True)
    errors = np.random.randn(T, k) @ L.T
    
    # Initialize
    Y = np.zeros((T, k), dtype=np.float64)
    Y[0, :] = errors[0, :]
    
    # Generate process
    Pi = alpha @ beta.T
    for t in range(1, T):
        Y[t, :] = Y[t-1, :] + Pi @ Y[t-1, :] + errors[t, :]
    
    params = {
        'alpha': alpha,
        'beta': beta,
        'Omega': Omega,
        'Pi': Pi
    }
    
    return Y, params


def simulate_tv_cointegrated_system(
    T: int,
    k: int,
    r: int,
    alpha: Optional[NDArray] = None,
    beta_func: Optional[callable] = None,
    Omega: Optional[NDArray] = None,
    seed: Optional[int] = None
) -> Tuple[NDArray, dict]:
    """
    Simulate a time-varying cointegrated time series system.
    
    Generates data from:
        ΔY_t = α β'_t Y_{t-1} + ε_t
        ε_t ~ N(0, Ω)
    
    where β_t varies smoothly over time.
    
    Parameters
    ----------
    T : int
        Sample size.
    k : int
        Number of variables.
    r : int
        Cointegration rank.
    alpha : ndarray of shape (k, r), optional
        Adjustment matrix. Default: random.
    beta_func : callable, optional
        Function that takes t/T (in [0,1]) and returns beta (k, r).
        Default: linear transition.
    Omega : ndarray of shape (k, k), optional
        Error covariance matrix. Default: identity.
    seed : int, optional
        Random seed for reproducibility.
        
    Returns
    -------
    Y : ndarray of shape (T, k)
        Simulated time series.
    params : dict
        True parameters used in simulation.
    """
    if seed is not None:
        np.random.seed(seed)
    
    if r > k:
        raise ValueError(f"Cointegration rank r={r} cannot exceed k={k}")
    
    # Default parameters
    if alpha is None:
        alpha = -0.1 * np.random.randn(k, r)
    
    if beta_func is None:
        # Default: linear transition from beta_0 to beta_1
        beta_0 = np.eye(k, r)
        beta_1 = np.eye(k, r)
        beta_1[0, 0] = 1.5  # Small change
        beta_func = lambda tau: beta_0 * (1 - tau) + beta_1 * tau
    
    if Omega is None:
        Omega = np.eye(k)
    
    # Generate errors
    L = linalg.cholesky(Omega, lower=True)
    errors = np.random.randn(T, k) @ L.T
    
    # Initialize
    Y = np.zeros((T, k), dtype=np.float64)
    Y[0, :] = errors[0, :]
    
    # Store time-varying beta
    beta_t = np.zeros((T, k, r), dtype=np.float64)
    
    # Generate process
    for t in range(1, T):
        tau = t / T
        beta_t[t, :, :] = beta_func(tau)
        Pi_t = alpha @ beta_t[t, :, :].T
        Y[t, :] = Y[t-1, :] + Pi_t @ Y[t-1, :] + errors[t, :]
    
    params = {
        'alpha': alpha,
        'beta_t': beta_t,
        'beta_func': beta_func,
        'Omega': Omega
    }
    
    return Y, params
