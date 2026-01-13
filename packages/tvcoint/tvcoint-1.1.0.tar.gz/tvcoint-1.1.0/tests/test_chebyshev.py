"""
Unit Tests for Chebyshev Time Polynomials Module
=================================================

Tests for the Chebyshev polynomial implementation used in
Bierens and Martins (2010) time-varying cointegration framework.

These tests verify:
1. Correct polynomial computation
2. Orthonormality property: (1/T) Σ P_i(t) P_j(t) = δ_{ij}
3. Extended Y construction for TV-VECM
4. Approximation accuracy (Lemma 1)
"""

import pytest
import numpy as np
from numpy.testing import assert_array_almost_equal, assert_allclose

import sys
sys.path.insert(0, '/home/claude/tvcoint')

from tvcoint.chebyshev import (
    chebyshev_polynomial,
    chebyshev_polynomial_matrix,
    construct_extended_y,
    chebyshev_approximation,
    verify_orthonormality,
    chebyshev_coefficients,
)


class TestChebyshevPolynomial:
    """Tests for basic Chebyshev polynomial computation."""
    
    def test_p0_equals_one(self):
        """P_{0,T}(t) = 1 for all t."""
        T = 100
        for t in range(1, T + 1):
            # Signature is (t, T, i)
            assert chebyshev_polynomial(t, T, 0) == 1.0
    
    def test_p1_formula(self):
        """P_{i,T}(t) = √2 cos(iπ(t-0.5)/T) for i ≥ 1."""
        T = 100
        t = 50
        i = 2
        expected = np.sqrt(2) * np.cos(i * np.pi * (t - 0.5) / T)
        computed = chebyshev_polynomial(t, T, i)
        assert_allclose(computed, expected, rtol=1e-10)
    
    def test_polynomial_bounds(self):
        """Chebyshev polynomials should be bounded by √2."""
        T = 100
        for i in range(1, 10):
            for t in range(1, T + 1):
                p = chebyshev_polynomial(t, T, i)
                assert abs(p) <= np.sqrt(2) + 1e-10
    
    def test_array_input(self):
        """Function should handle array input for t."""
        T = 100
        t_array = np.arange(1, T + 1)
        result = chebyshev_polynomial(t_array, T, 1)
        assert result.shape == (T,)
        assert_allclose(result[0], chebyshev_polynomial(1, T, 1))


class TestChebyshevMatrix:
    """Tests for Chebyshev polynomial matrix construction."""
    
    def test_matrix_shape(self):
        """Matrix should have shape (T, m+1)."""
        T = 100
        m = 5
        P = chebyshev_polynomial_matrix(T, m)
        assert P.shape == (T, m + 1)
    
    def test_first_column_ones(self):
        """First column should be all ones (P_0 = 1)."""
        T = 100
        m = 3
        P = chebyshev_polynomial_matrix(T, m)
        assert_allclose(P[:, 0], np.ones(T))
    
    def test_orthonormality(self):
        """Columns should be orthonormal: (1/T) P'P = I."""
        T = 100
        m = 5
        P = chebyshev_polynomial_matrix(T, m)
        inner_products = P.T @ P / T
        identity = np.eye(m + 1)
        assert_allclose(inner_products, identity, atol=1e-10)
    
    def test_verify_orthonormality_function(self):
        """verify_orthonormality should return True."""
        T = 100
        m = 5
        is_ortho, products = verify_orthonormality(T, m)
        assert is_ortho
        assert_allclose(products, np.eye(m + 1), atol=1e-10)


class TestExtendedY:
    """Tests for extended Y matrix construction."""
    
    def test_extended_y_shape_m0(self):
        """With m=0, extended Y should equal lagged Y."""
        T = 100
        k = 3
        Y = np.random.randn(T, k)
        Y_ext = construct_extended_y(Y, m=0)
        # Shape should be (T-1, k) for m=0
        assert Y_ext.shape[1] == k
    
    def test_extended_y_shape_m_positive(self):
        """With m>0, extended Y should have shape (T-1, k*(m+1))."""
        T = 100
        k = 2
        m = 3
        Y = np.random.randn(T, k)
        Y_ext = construct_extended_y(Y, m=m)
        assert Y_ext.shape[1] == k * (m + 1)
    
    def test_extended_y_first_block(self):
        """First k columns should be Y_{t-1}."""
        T = 100
        k = 2
        m = 2
        Y = np.random.randn(T, k)
        Y_ext = construct_extended_y(Y, m=m)
        # First block should be lagged Y
        assert_allclose(Y_ext[:, :k], Y[:-1, :])


class TestChebyshevApproximation:
    """Tests for Chebyshev approximation of functions."""
    
    def test_approximation_constant_function(self):
        """Constant function should have only c_0 non-zero."""
        T = 100
        m = 5
        g = np.ones(T) * 5.0
        coeffs, approx = chebyshev_approximation(g, T, m)
        
        assert_allclose(coeffs[0], 5.0)
        assert_allclose(coeffs[1:], 0, atol=1e-10)
        assert_allclose(approx, g)
    
    def test_approximation_smooth_function(self):
        """Smooth function should be well-approximated."""
        T = 200
        m = 10
        t = np.arange(1, T + 1)
        # Smooth function
        g = np.sin(2 * np.pi * t / T)
        
        coeffs, approx = chebyshev_approximation(g, T, m)
        
        # Approximation error should be small
        error = np.mean((g - approx)**2)
        assert error < 0.01
    
    def test_coefficients_recovery(self):
        """Test that coefficients can be recovered correctly."""
        T = 100
        m = 3
        
        # Create function from known coefficients
        P = chebyshev_polynomial_matrix(T, m)
        true_coeffs = np.array([1.0, 0.5, -0.3, 0.2])
        g = P @ true_coeffs
        
        # Recover coefficients
        recovered_coeffs = chebyshev_coefficients(g, m)
        
        assert_allclose(recovered_coeffs, true_coeffs, atol=1e-10)


class TestNumericalStability:
    """Tests for numerical stability."""
    
    def test_large_m_stability(self):
        """Large m should not cause numerical issues."""
        T = 200
        m = 20
        P = chebyshev_polynomial_matrix(T, m)
        assert not np.any(np.isnan(P))
        assert not np.any(np.isinf(P))
    
    def test_small_T_stability(self):
        """Small T should work without issues."""
        T = 20
        m = 5
        P = chebyshev_polynomial_matrix(T, m)
        is_ortho, _ = verify_orthonormality(T, m)
        assert is_ortho
    
    def test_extended_y_no_nans(self):
        """Extended Y should not contain NaN values."""
        T = 100
        k = 3
        m = 5
        Y = np.random.randn(T, k)
        Y_ext = construct_extended_y(Y, m=m)
        assert not np.any(np.isnan(Y_ext))
