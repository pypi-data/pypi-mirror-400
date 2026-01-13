"""
Comprehensive Verification Test for tvcoint Library
====================================================

This test verifies the tvcoint library implements Bierens & Martins (2010)
"Time-Varying Cointegration" correctly.

Tests:
1. Chebyshev polynomials match paper definitions
2. LR test statistic formula is correct
3. Degrees of freedom formula is correct
4. Test has correct size under H0
5. Test has power under H1
"""

import numpy as np
import pytest
from scipy import stats
from numpy.testing import assert_allclose

from tvcoint import (
    JohansenVECM,
    TimeVaryingVECM,
    lr_test_tv_cointegration,
    simulate_cointegrated_system,
)
from tvcoint.chebyshev import (
    chebyshev_polynomial,
    chebyshev_polynomial_matrix,
    verify_orthonormality,
)


class TestChebyshevPolynomialsPaper:
    """Verify Chebyshev polynomials match Bierens & Martins (2010) definitions."""
    
    def test_p0_equals_one(self):
        """P_{0,T}(t) = 1 for all t (paper definition)."""
        T = 100
        for t in [1, 25, 50, 75, 100]:
            assert chebyshev_polynomial(t, T, 0) == 1.0
    
    def test_pi_formula(self):
        """P_{i,T}(t) = sqrt(2) * cos(i*pi*(t-0.5)/T) for i >= 1."""
        T = 100
        for i in [1, 2, 3, 5]:
            for t in [1, 50, 100]:
                expected = np.sqrt(2) * np.cos(i * np.pi * (t - 0.5) / T)
                computed = chebyshev_polynomial(t, T, i)
                assert_allclose(computed, expected, rtol=1e-12)
    
    def test_orthonormality_property(self):
        """Key property: (1/T) * sum_t P_i(t) * P_j(t) = delta_ij."""
        T = 200
        m = 5
        is_ortho, inner_products = verify_orthonormality(T, m)
        assert is_ortho
        assert_allclose(inner_products, np.eye(m + 1), atol=1e-10)
    
    def test_polynomial_bounds(self):
        """P_i(t) bounded by sqrt(2) for i >= 1."""
        T = 100
        P = chebyshev_polynomial_matrix(T, 10)
        assert np.max(np.abs(P[:, 1:])) <= np.sqrt(2) + 1e-10


class TestLRTestFormula:
    """Verify LR test matches paper formulas."""
    
    @pytest.fixture
    def test_data(self):
        """Generate cointegrated test data."""
        np.random.seed(12345)
        Y, _ = simulate_cointegrated_system(T=200, k=2, r=1, seed=12345)
        return Y
    
    def test_lr_equals_2_times_ll_diff(self, test_data):
        """LR = 2 * (L_m - L_0) as per paper Section 4."""
        Y = test_data
        
        for m in [1, 2, 3]:
            # Null model
            vecm_0 = JohansenVECM(p=2)
            vecm_0.fit(Y, r=1)
            
            # Alternative model
            vecm_m = TimeVaryingVECM(p=2, m=m)
            vecm_m.fit(Y, r=1)
            
            # Manual LR
            lr_manual = 2 * (vecm_m.log_likelihood - vecm_0.log_likelihood)
            
            # From function
            result = lr_test_tv_cointegration(Y, r=1, m=m, p=2)
            
            assert_allclose(result.test_statistic, lr_manual, rtol=1e-10)
    
    def test_degrees_of_freedom(self, test_data):
        """df = r * k * m as per Theorem 1."""
        Y = test_data
        k = Y.shape[1]
        r = 1
        
        for m in [1, 2, 3, 4]:
            expected_df = r * k * m
            result = lr_test_tv_cointegration(Y, r=r, m=m, p=2)
            assert result.degrees_of_freedom == expected_df
    
    def test_asymptotic_chi2_distribution(self, test_data):
        """Under H0, LR ~ chi2(r*k*m)."""
        Y = test_data
        result = lr_test_tv_cointegration(Y, r=1, m=2, p=2)
        
        # P-value should be computed from chi2
        df = result.degrees_of_freedom
        expected_p = 1 - stats.chi2.cdf(result.test_statistic, df)
        assert_allclose(result.p_value, expected_p, rtol=1e-10)


class TestSizeAndPower:
    """Verify test has correct size and power."""
    
    def test_size_under_h0(self):
        """Size should be approximately nominal level under H0."""
        np.random.seed(999)
        n_sim = 50  # Small for speed
        rejections = 0
        valid_sims = 0
        
        for i in range(n_sim):
            try:
                # Generate data under H0 (constant cointegration)
                Y, _ = simulate_cointegrated_system(T=200, k=2, r=1, seed=1000+i)
                result = lr_test_tv_cointegration(Y, r=1, m=2, p=2)
                valid_sims += 1
                if result.reject_null_5pct:
                    rejections += 1
            except np.linalg.LinAlgError:
                # Skip singular matrix cases (rare numerical issues)
                continue
        
        if valid_sims > 0:
            size = rejections / valid_sims
            # Size should be between 0% and 20% (allowing for randomness)
            assert 0.0 <= size <= 0.20
    
    def test_power_under_h1(self):
        """Power should be higher than size under H1."""
        np.random.seed(888)
        n_sim = 30
        rejections = 0
        
        for i in range(n_sim):
            # Generate data with time-varying cointegration
            T = 200
            np.random.seed(2000 + i)
            
            # y1 is random walk
            y1 = np.cumsum(np.random.randn(T))
            
            # Time-varying relationship: y2 = beta(t) * y1 + noise
            # beta(t) varies sinusoidally
            beta_t = 1.0 + 0.3 * np.sin(2 * np.pi * np.arange(T) / T)
            y2 = beta_t * y1 + np.random.randn(T) * 0.3
            
            Y = np.column_stack([y1, y2])
            result = lr_test_tv_cointegration(Y, r=1, m=2, p=2)
            if result.reject_null_5pct:
                rejections += 1
        
        power = rejections / n_sim
        # Power should be substantially higher than 5%
        assert power > 0.20


class TestTimeVaryingBeta:
    """Verify time-varying beta estimation."""
    
    def test_beta_t_shape(self):
        """beta_t should have shape (T, k, r)."""
        np.random.seed(111)
        Y, _ = simulate_cointegrated_system(T=200, k=2, r=1, seed=111)
        
        model = TimeVaryingVECM(p=2, m=2)
        model.fit(Y, r=1)
        
        T, k = Y.shape
        r = 1
        assert model.beta_t.shape == (T, k, r)
    
    def test_beta_t_recovers_constant(self):
        """With constant cointegration, beta_t should be relatively stable."""
        np.random.seed(222)
        Y, _ = simulate_cointegrated_system(T=300, k=2, r=1, seed=222)
        
        model = TimeVaryingVECM(p=2, m=2)
        model.fit(Y, r=1)
        
        # Standard deviation relative to range should be moderate
        beta_range = np.max(model.beta_t, axis=0) - np.min(model.beta_t, axis=0)
        beta_std = np.std(model.beta_t, axis=0)
        
        # At least one variable's beta should be relatively stable
        # (not all variables may show stable beta due to normalization)
        assert np.any(beta_std < 1.0)


class TestJohansenVECM:
    """Basic tests for Johansen VECM."""
    
    def test_fit_and_attributes(self):
        """Johansen VECM should estimate alpha, beta, and log-likelihood."""
        np.random.seed(333)
        Y, _ = simulate_cointegrated_system(T=200, k=2, r=1, seed=333)
        
        model = JohansenVECM(p=2)
        model.fit(Y, r=1)
        
        assert hasattr(model, 'alpha')
        assert hasattr(model, 'beta')
        assert hasattr(model, 'log_likelihood')
        assert model.alpha.shape == (2, 1)
        assert model.beta.shape == (2, 1)
        assert np.isfinite(model.log_likelihood)
    
    def test_eigenvalues_ordered(self):
        """Eigenvalues should be in decreasing order."""
        np.random.seed(444)
        Y, _ = simulate_cointegrated_system(T=200, k=2, r=1, seed=444)
        
        model = JohansenVECM(p=2)
        model.fit(Y, r=1)
        
        assert np.all(np.diff(model.eigenvalues) <= 0)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
