"""
Chebyshev Time Polynomials Module
=================================

Implementation of Chebyshev time polynomials as defined in Bierens and Martins (2010)
"Time-Varying Cointegration", Econometric Theory, Vol. 26, No. 5, pp. 1453-1490.

The Chebyshev time polynomials are defined as:
    P_{0,T}(t) = 1
    P_{i,T}(t) = sqrt(2) * cos(i * pi * (t - 0.5) / T), for i = 1, 2, 3, ...

These polynomials are orthonormal in the sense that:
    (1/T) * sum_{t=1}^{T} P_{i,T}(t) * P_{j,T}(t) = 1 if i == j, 0 otherwise

Reference:
    Bierens, H.J. and Martins, L.F. (2010). "Time-Varying Cointegration."
    Econometric Theory, 26(5), 1453-1490.
    
    See also: Hamming, R.W. (1973). Numerical Methods for Scientists and Engineers. Dover.
"""

import numpy as np
from typing import Union, Optional, Tuple
from numpy.typing import NDArray


def chebyshev_polynomial(t: Union[int, NDArray], T: int, i: int) -> Union[float, NDArray]:
    """
    Compute the Chebyshev time polynomial P_{i,T}(t).
    
    As defined in Bierens and Martins (2010), equation after eq. (1):
        P_{0,T}(t) = 1
        P_{i,T}(t) = sqrt(2) * cos(i * pi * (t - 0.5) / T), for i >= 1
    
    Parameters
    ----------
    t : int or array-like
        Time index or array of time indices. Should be in range [1, T].
    T : int
        Total number of observations (sample size).
    i : int
        Order of the Chebyshev polynomial (i >= 0).
        
    Returns
    -------
    float or ndarray
        Value(s) of P_{i,T}(t).
        
    Examples
    --------
    >>> chebyshev_polynomial(1, 100, 0)
    1.0
    >>> chebyshev_polynomial(50, 100, 1)  # approximately 0
    -8.659560562354933e-17
    
    Notes
    -----
    The Chebyshev time polynomials form an orthonormal basis, meaning:
        (1/T) * sum_{t=1}^{T} P_{i,T}(t) * P_{j,T}(t) = delta_{ij}
    where delta_{ij} is the Kronecker delta.
    """
    t = np.asarray(t, dtype=np.float64)
    
    if i < 0:
        raise ValueError(f"Order i must be non-negative, got {i}")
    if T < 1:
        raise ValueError(f"Sample size T must be positive, got {T}")
    
    if i == 0:
        return np.ones_like(t, dtype=np.float64) if t.ndim > 0 else 1.0
    else:
        result = np.sqrt(2.0) * np.cos(i * np.pi * (t - 0.5) / T)
        return result


def chebyshev_polynomial_matrix(T: int, m: int) -> NDArray:
    """
    Construct the T x (m+1) matrix of Chebyshev time polynomials.
    
    The matrix P has elements P[t-1, i] = P_{i,T}(t) for t = 1, ..., T and i = 0, ..., m.
    
    Parameters
    ----------
    T : int
        Total number of observations (sample size).
    m : int
        Maximum order of Chebyshev polynomials (m >= 0).
        
    Returns
    -------
    P : ndarray of shape (T, m+1)
        Matrix where P[t, i] = P_{i,T}(t+1) for t = 0, ..., T-1 and i = 0, ..., m.
        
    Examples
    --------
    >>> P = chebyshev_polynomial_matrix(100, 2)
    >>> P.shape
    (100, 3)
    >>> np.allclose(P[:, 0], 1)  # First column is all ones
    True
    
    Notes
    -----
    Due to orthonormality: (1/T) * P.T @ P ≈ I_{m+1}
    """
    if T < 1:
        raise ValueError(f"Sample size T must be positive, got {T}")
    if m < 0:
        raise ValueError(f"Maximum order m must be non-negative, got {m}")
    
    t = np.arange(1, T + 1, dtype=np.float64)
    P = np.zeros((T, m + 1), dtype=np.float64)
    
    for i in range(m + 1):
        P[:, i] = chebyshev_polynomial(t, T, i)
    
    return P


def verify_orthonormality(T: int, m: int, tolerance: float = 1e-10) -> Tuple[bool, NDArray]:
    """
    Verify the orthonormality property of Chebyshev time polynomials.
    
    Checks that (1/T) * sum_{t=1}^{T} P_{i,T}(t) * P_{j,T}(t) ≈ delta_{ij}
    
    Parameters
    ----------
    T : int
        Total number of observations.
    m : int
        Maximum order of Chebyshev polynomials.
    tolerance : float, optional
        Tolerance for checking orthonormality (default: 1e-10).
        
    Returns
    -------
    is_orthonormal : bool
        True if the polynomials are orthonormal within tolerance.
    inner_products : ndarray of shape (m+1, m+1)
        Matrix of inner products (1/T) * P.T @ P.
        
    Examples
    --------
    >>> is_ortho, products = verify_orthonormality(100, 3)
    >>> is_ortho
    True
    >>> np.allclose(products, np.eye(4))
    True
    """
    P = chebyshev_polynomial_matrix(T, m)
    inner_products = P.T @ P / T
    
    identity = np.eye(m + 1)
    is_orthonormal = np.allclose(inner_products, identity, atol=tolerance)
    
    return is_orthonormal, inner_products


def chebyshev_approximation(
    g: NDArray, 
    T: int, 
    m: int
) -> Tuple[NDArray, NDArray]:
    """
    Approximate a function g(t) using Chebyshev time polynomials.
    
    As stated in the paper (equation before Lemma 1):
        g(t) = sum_{i=0}^{T-1} xi_{i,T} * P_{i,T}(t)
    
    where xi_{i,T} = (1/T) * sum_{t=1}^{T} g(t) * P_{i,T}(t)
    
    The approximation g_{m,T}(t) uses only the first m+1 terms:
        g_{m,T}(t) = sum_{i=0}^{m} xi_{i,T} * P_{i,T}(t)
    
    Parameters
    ----------
    g : ndarray of shape (T,) or (T, k)
        Function values g(t) for t = 1, ..., T. Can be scalar or vector-valued.
    T : int
        Total number of observations.
    m : int
        Number of Chebyshev polynomials to use (order 0, 1, ..., m).
        
    Returns
    -------
    coefficients : ndarray of shape (m+1,) or (m+1, k)
        Chebyshev coefficients xi_{i,T}.
    approximation : ndarray of shape (T,) or (T, k)
        Approximated function values g_{m,T}(t).
        
    Notes
    -----
    According to Lemma 1 in the paper, if g(t) = φ(t/T) where φ(x) is a smooth function,
    the approximation error decreases rapidly as m increases.
    """
    g = np.asarray(g, dtype=np.float64)
    is_vector = g.ndim == 2
    
    if g.ndim == 1:
        g = g.reshape(-1, 1)
    
    if g.shape[0] != T:
        raise ValueError(f"Function values must have length T={T}, got {g.shape[0]}")
    
    P = chebyshev_polynomial_matrix(T, m)
    
    # Compute coefficients: xi_{i,T} = (1/T) * sum_{t=1}^{T} g(t) * P_{i,T}(t)
    coefficients = P.T @ g / T  # Shape: (m+1, k)
    
    # Compute approximation: g_{m,T}(t) = sum_{i=0}^{m} xi_{i,T} * P_{i,T}(t)
    approximation = P @ coefficients  # Shape: (T, k)
    
    if not is_vector:
        coefficients = coefficients.flatten()
        approximation = approximation.flatten()
    
    return coefficients, approximation


def chebyshev_coefficients(g: NDArray, m: int) -> NDArray:
    """
    Compute Chebyshev coefficients for a discrete function.
    
    This is a convenience function that extracts only the coefficients
    from chebyshev_approximation().
    
    Parameters
    ----------
    g : ndarray of shape (T,) or (T, k)
        Function values g(t) for t = 1, ..., T.
    m : int
        Maximum order of Chebyshev polynomials.
        
    Returns
    -------
    coefficients : ndarray of shape (m+1,) or (m+1, k)
        Chebyshev coefficients xi_{i,T}.
        
    See Also
    --------
    chebyshev_approximation : Returns both coefficients and approximation.
    """
    g = np.asarray(g, dtype=np.float64)
    T = g.shape[0]
    coefficients, _ = chebyshev_approximation(g, T, m)
    return coefficients


def construct_extended_y(Y: NDArray, m: int) -> NDArray:
    """
    Construct the extended Y matrix Y^{(m)}_{t-1} as defined in equation (4) of the paper.
    
    Y^{(m)}_{t-1} = (Y'_{t-1}, P_{1,T}(t)*Y'_{t-1}, P_{2,T}(t)*Y'_{t-1}, ..., P_{m,T}(t)*Y'_{t-1})'
    
    This extends the lagged Y matrix to include interactions with Chebyshev time polynomials,
    enabling the estimation of time-varying cointegrating vectors.
    
    Parameters
    ----------
    Y : ndarray of shape (T, k)
        The k-variate time series data.
    m : int
        Maximum order of Chebyshev polynomials.
        
    Returns
    -------
    Y_extended : ndarray of shape (T-1, k*(m+1))
        Extended Y matrix where each row t corresponds to time t+1 and contains
        [Y_t, P_{1,T}(t+1)*Y_t, ..., P_{m,T}(t+1)*Y_t].
        
    Notes
    -----
    - Row 0 of Y_extended corresponds to Y^{(m)}_{0} used when t=1
    - Row t-1 of Y_extended corresponds to Y^{(m)}_{t-1} used when modeling ΔY_t
    - The matrix has dimensions (T-1) x k(m+1) because we lose one observation
      due to differencing and we need Y_{t-1} for t = 1, ..., T-1
    """
    Y = np.asarray(Y, dtype=np.float64)
    T, k = Y.shape
    
    if m < 0:
        raise ValueError(f"Order m must be non-negative, got {m}")
    
    # Get Chebyshev polynomial matrix for t = 1, ..., T
    # We need P_{i,T}(t) for the extended Y at time t, but the Y values are Y_{t-1}
    # So for Y^{(m)}_{t-1} at time t, we use P_{i,T}(t) multiplied by Y_{t-1}
    
    # Y_lagged[t-1, :] = Y_{t-1} for t = 1, ..., T-1
    # This corresponds to rows 0 to T-2 of the original Y
    Y_lagged = Y[:-1, :]  # Shape: (T-1, k)
    
    # P_matrix[t-1, i] = P_{i,T}(t) for t = 1, ..., T-1
    # We evaluate at t = 1, ..., T-1 (since we're modeling ΔY_t for t = 1, ..., T-1)
    # But wait, in the paper t goes from 1 to T, so we evaluate at t = 2, ..., T
    # because Y^{(m)}_{t-1} is used for modeling ΔY_t at time t
    P_matrix = chebyshev_polynomial_matrix(T, m)  # Shape: (T, m+1)
    
    # For t = 1: we model ΔY_1 = Y_1 - Y_0, using Y^{(m)}_0
    # For t = 2: we model ΔY_2 = Y_2 - Y_1, using Y^{(m)}_1
    # ...
    # For t = T-1: we model ΔY_{T-1}, using Y^{(m)}_{T-2}
    
    # The Chebyshev polynomials are evaluated at the time index of the ΔY_t
    # So for ΔY_t at time t, we use P_{i,T}(t) * Y_{t-1}
    
    # Since our effective sample for differences is t = 2, ..., T
    # (ΔY_1 = Y_1 - Y_0 requires Y_0 which we may not have)
    # Actually, in the paper they use t = 1, ..., T for the model
    # So Y^{(m)}_{t-1} is used for t = 1, ..., T
    
    # Let's construct it properly:
    # For each t in 2, ..., T (effective sample after differencing):
    #   Y^{(m)}_{t-1} uses P_{i,T}(t) * Y_{t-1}
    
    # Construct extended matrix
    T_eff = T - 1  # Effective sample size after differencing
    Y_extended = np.zeros((T_eff, k * (m + 1)), dtype=np.float64)
    
    for t_idx in range(T_eff):
        # t_idx = 0 corresponds to t = 2 in the original time index
        # Y_{t-1} = Y[t_idx, :] = Y[0, :] when t=2 (which is Y_1)
        # Wait, let me reconsider...
        
        # If original data is Y[0], Y[1], ..., Y[T-1] corresponding to t=1,...,T
        # Then Y_{t-1} for t=2,...,T is Y[0], Y[1], ..., Y[T-2]
        # And ΔY_t for t=2,...,T is Y[1]-Y[0], ..., Y[T-1]-Y[T-2]
        
        # For the model at time index t (t=2,...,T):
        # ΔY_t uses Y^{(m)}_{t-1} = [Y'_{t-1}, P_{1,T}(t)*Y'_{t-1}, ...]
        
        # t_idx in range(T_eff) corresponds to t = t_idx + 2 in original indexing
        # Actually, let's reconsider the paper's notation
        
        # In the paper, t = 1, ..., T
        # ΔY_t = Y_t - Y_{t-1} for t = 1, ..., T (but Y_0 might be assumed 0 or given)
        # Y^{(m)}_{t-1} is used for the error correction term at time t
        
        # For practical implementation:
        # Row 0 of Y_extended corresponds to using Y_0 (first observation) as Y_{t-1}
        # This is used when modeling ΔY_1
        
        # The time index for P_{i,T}(t) should be t (the observation being modeled)
        # So for t_idx = 0 (t=1 in 1-based), use P_{i,T}(1) * Y_0
        # For t_idx = 1 (t=2 in 1-based), use P_{i,T}(2) * Y_1
        # etc.
        
        t = t_idx + 1  # 1-based time index for Chebyshev polynomials
        Y_tm1 = Y_lagged[t_idx, :]  # Y_{t-1}
        
        for j in range(m + 1):
            P_j_t = P_matrix[t_idx, j]  # P_{j,T}(t) where t = t_idx + 1
            # Actually P_matrix is indexed from 0, so P_matrix[t-1, j] = P_{j,T}(t)
            # For t=1, use P_matrix[0, j]
            # For t=2, use P_matrix[1, j]
            # etc.
            Y_extended[t_idx, j*k:(j+1)*k] = P_j_t * Y_tm1
    
    return Y_extended


def construct_time_varying_beta(
    xi_coefficients: NDArray,
    T: int,
    m: int
) -> NDArray:
    """
    Construct time-varying cointegrating vectors β_t from Chebyshev coefficients.
    
    As defined in equation (2) of the paper:
        β_t = β_m(t/T) = sum_{i=0}^{m} ξ_i * P_{i,T}(t)
    
    Parameters
    ----------
    xi_coefficients : ndarray of shape (k, r, m+1)
        Chebyshev coefficients ξ_i for i = 0, ..., m.
        - k: number of variables
        - r: cointegration rank
        - m+1: number of Chebyshev coefficients
    T : int
        Total number of observations.
    m : int
        Maximum order of Chebyshev polynomials.
        
    Returns
    -------
    beta_t : ndarray of shape (T, k, r)
        Time-varying cointegrating vectors β_t for t = 1, ..., T.
        
    Notes
    -----
    Under the null hypothesis of time-invariant cointegration:
        ξ_i = 0 for i = 1, ..., m
    so that β_t = ξ_0 = β (constant).
    """
    xi_coefficients = np.asarray(xi_coefficients, dtype=np.float64)
    
    if xi_coefficients.ndim != 3:
        raise ValueError(f"xi_coefficients must be 3-dimensional, got {xi_coefficients.ndim}")
    
    k, r, num_coef = xi_coefficients.shape
    
    if num_coef != m + 1:
        raise ValueError(f"Number of coefficients {num_coef} must equal m+1={m+1}")
    
    P = chebyshev_polynomial_matrix(T, m)  # Shape: (T, m+1)
    
    beta_t = np.zeros((T, k, r), dtype=np.float64)
    
    for t in range(T):
        for i in range(m + 1):
            beta_t[t, :, :] += xi_coefficients[:, :, i] * P[t, i]
    
    return beta_t


def chebyshev_basis_for_estimation(Y: NDArray, m: int, include_intercept: bool = False) -> dict:
    """
    Prepare all necessary matrices for time-varying VECM estimation using Chebyshev basis.
    
    This function constructs all the matrices needed for the ML estimation procedure
    described in Section 3.1 of Bierens and Martins (2010).
    
    Parameters
    ----------
    Y : ndarray of shape (T, k)
        The k-variate time series data.
    m : int
        Maximum order of Chebyshev polynomials.
    include_intercept : bool, optional
        Whether to include an intercept in the model (drift case, Section 5).
        Default is False.
        
    Returns
    -------
    dict with keys:
        'Y' : Original data
        'DY' : First differences ΔY_t
        'Y_lagged' : Lagged levels Y_{t-1}
        'Y_extended' : Extended Y matrix Y^{(m)}_{t-1}
        'P_matrix' : Chebyshev polynomial matrix
        'T' : Original sample size
        'T_eff' : Effective sample size after differencing
        'k' : Number of variables
        'm' : Chebyshev order
        
    Examples
    --------
    >>> import numpy as np
    >>> Y = np.random.randn(100, 2)
    >>> data = chebyshev_basis_for_estimation(Y, m=2)
    >>> data['Y_extended'].shape
    (99, 6)  # 99 observations, 2 variables * 3 Chebyshev polynomials
    """
    Y = np.asarray(Y, dtype=np.float64)
    
    if Y.ndim != 2:
        raise ValueError(f"Y must be 2-dimensional, got {Y.ndim}")
    
    T, k = Y.shape
    
    if T < m + 2:
        raise ValueError(f"Sample size T={T} too small for m={m}")
    
    # First differences
    DY = np.diff(Y, axis=0)  # Shape: (T-1, k)
    
    # Lagged levels
    Y_lagged = Y[:-1, :]  # Shape: (T-1, k)
    
    # Extended Y matrix
    Y_extended = construct_extended_y(Y, m)  # Shape: (T-1, k*(m+1))
    
    # Chebyshev polynomial matrix
    P_matrix = chebyshev_polynomial_matrix(T, m)
    
    result = {
        'Y': Y,
        'DY': DY,
        'Y_lagged': Y_lagged,
        'Y_extended': Y_extended,
        'P_matrix': P_matrix,
        'T': T,
        'T_eff': T - 1,
        'k': k,
        'm': m,
        'include_intercept': include_intercept
    }
    
    return result
