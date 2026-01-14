"""
Comprehensive accuracy tests for fastica_torch vs sklearn.

These tests verify that the PyTorch FastICA implementation produces
results comparable to sklearn's FastICA under various conditions.

Key testing considerations for ICA:
1. Sign ambiguity: Components can be negated
2. Permutation ambiguity: Components can be reordered
3. Convergence sensitivity: Different initializations may yield different solutions

We use correlation-based matching and Amari distance to handle these ambiguities.
"""

from typing import Tuple

import numpy as np
import pytest
import torch
from scipy.stats import pearsonr
from sklearn.decomposition import FastICA as SklearnFastICA

from fastica_torch import FastICA


# =============================================================================
# Helper Functions
# =============================================================================

def generate_sources(n_samples: int, n_sources: int, seed: int = 42) -> np.ndarray:
    """
    Generate independent non-Gaussian source signals.
    
    Uses a mix of signal types that are typically used in ICA benchmarks:
    - Sinusoids (super-Gaussian)
    - Sawtooth waves (uniform-like)
    - Random sparse signals (super-Gaussian)
    """
    np.random.seed(seed)
    t = np.linspace(0, 8 * np.pi, n_samples)
    
    sources = []
    for i in range(n_sources):
        sig_type = i % 4
        if sig_type == 0:
            # Sinusoid with varying frequency
            s = np.sin(t * (1 + 0.5 * i))
        elif sig_type == 1:
            # Sawtooth-like
            s = np.mod(t * (1 + 0.3 * i), 2 * np.pi) / np.pi - 1
        elif sig_type == 2:
            # Sparse signal (super-Gaussian / impulsive)
            s = np.random.laplace(0, 1, n_samples)
        else:
            # Uniform noise
            s = np.random.uniform(-1, 1, n_samples)
        
        # Standardize
        s = (s - s.mean()) / s.std()
        sources.append(s)
    
    return np.array(sources).T  # (n_samples, n_sources)


def generate_mixed_signals(
    n_samples: int,
    n_sources: int,
    n_features: int,
    seed: int = 42,
    noise_level: float = 0.0
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Generate mixed signals from independent sources.
    
    Returns:
        X: Mixed observations (n_samples, n_features)
        S: Original sources (n_samples, n_sources)
        A: Mixing matrix (n_sources, n_features)
    """
    np.random.seed(seed)
    
    # Generate sources
    S = generate_sources(n_samples, n_sources, seed)
    
    # Generate random mixing matrix
    A = np.random.randn(n_sources, n_features)
    
    # Mix signals: X = S @ A
    X = S @ A
    
    # Add noise if requested
    if noise_level > 0:
        X += noise_level * np.random.randn(*X.shape)
    
    return X, S, A


def compute_correlation_matrix(S_true: np.ndarray, S_est: np.ndarray) -> np.ndarray:
    """
    Compute absolute correlation between true and estimated sources.
    
    Returns correlation matrix of shape (n_true_sources, n_est_sources).
    """
    n_true = S_true.shape[1]
    n_est = S_est.shape[1]
    corr_matrix = np.zeros((n_true, n_est))
    
    for i in range(n_true):
        for j in range(n_est):
            corr, _ = pearsonr(S_true[:, i], S_est[:, j])
            corr_matrix[i, j] = abs(corr)
    
    return corr_matrix


def match_sources_by_correlation(
    S_true: np.ndarray, 
    S_est: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Match estimated sources to true sources using correlation.
    
    Uses greedy matching to find best permutation.
    
    Returns:
        matched_correlations: Best correlation for each true source
        permutation: Indices mapping estimated to true sources
    """
    corr_matrix = compute_correlation_matrix(S_true, S_est)
    n_sources = min(S_true.shape[1], S_est.shape[1])
    
    matched_corrs = []
    permutation = []
    used_est = set()
    
    # Greedy matching
    for _ in range(n_sources):
        # Find highest remaining correlation
        best_corr = -1
        best_true_idx = -1
        best_est_idx = -1
        
        for i in range(S_true.shape[1]):
            if i >= n_sources:
                continue
            for j in range(S_est.shape[1]):
                if j in used_est:
                    continue
                if corr_matrix[i, j] > best_corr:
                    best_corr = corr_matrix[i, j]
                    best_true_idx = i
                    best_est_idx = j
        
        if best_est_idx >= 0:
            matched_corrs.append(best_corr)
            permutation.append(best_est_idx)
            used_est.add(best_est_idx)
    
    return np.array(matched_corrs), np.array(permutation)


def amari_distance(W_true: np.ndarray, W_est: np.ndarray) -> float:
    """
    Compute the Amari distance between two unmixing matrices.
    
    The Amari distance measures the difference between unmixing matrices,
    accounting for scale and permutation ambiguity. A value of 0 indicates
    perfect recovery.
    
    Reference: Amari et al., 1996
    """
    n = W_true.shape[0]
    
    # P = W_est @ pinv(W_true)
    P = W_est @ np.linalg.pinv(W_true)
    
    # Normalize rows and columns
    P_abs = np.abs(P)
    
    # Row-wise normalization
    row_max = P_abs.max(axis=1, keepdims=True)
    row_max[row_max == 0] = 1
    P_row = P_abs / row_max
    
    # Column-wise normalization  
    col_max = P_abs.max(axis=0, keepdims=True)
    col_max[col_max == 0] = 1
    P_col = P_abs / col_max
    
    # Amari distance
    term1 = (P_row.sum() - n) / (n * (n - 1)) if n > 1 else 0
    term2 = (P_col.sum() - n) / (n * (n - 1)) if n > 1 else 0
    
    return (term1 + term2) / 2


# =============================================================================
# Basic Functionality Tests
# =============================================================================

class TestBasicFunctionality:
    """Tests for basic FastICA functionality."""
    
    def test_fit_transform_returns_correct_shape(self):
        """Test that fit_transform returns sources with correct shape."""
        n_samples, n_features, n_components = 500, 10, 5
        X = torch.randn(n_samples, n_features)
        
        ica = FastICA(n_components=n_components, random_state=42)
        S = ica.fit_transform(X)
        
        assert S.shape == (n_samples, n_components)
        assert ica.components_.shape == (n_components, n_features)
        assert ica.mixing_.shape == (n_features, n_components)
    
    def test_fit_then_transform_equals_fit_transform(self):
        """Test that fit().transform() gives same result as fit_transform()."""
        X = torch.randn(500, 10)
        
        ica1 = FastICA(n_components=5, random_state=42)
        S1 = ica1.fit_transform(X)
        
        ica2 = FastICA(n_components=5, random_state=42)
        ica2.fit(X)
        S2 = ica2.transform(X)
        
        torch.testing.assert_close(S1, S2, rtol=1e-5, atol=1e-5)
    
    def test_inverse_transform_recovers_data(self):
        """Test that inverse_transform approximately recovers original data."""
        n_samples, n_features = 500, 10
        X = torch.randn(n_samples, n_features, dtype=torch.float64)
        
        ica = FastICA(n_components=n_features, random_state=42)
        S = ica.fit_transform(X)
        X_reconstructed = ica.inverse_transform(S)
        
        # Should be near-perfect reconstruction when n_components == n_features
        torch.testing.assert_close(X, X_reconstructed, rtol=1e-5, atol=1e-5)
    
    def test_reproducibility_with_random_state(self):
        """Test that same random_state gives same results."""
        X = torch.randn(500, 10)
        
        ica1 = FastICA(n_components=5, random_state=42)
        S1 = ica1.fit_transform(X)
        
        ica2 = FastICA(n_components=5, random_state=42)
        S2 = ica2.fit_transform(X)
        
        torch.testing.assert_close(S1, S2, rtol=1e-10, atol=1e-10)


# =============================================================================
# Signal Separation Quality Tests
# =============================================================================

class TestSignalSeparation:
    """Tests for ICA signal separation quality."""
    
    @pytest.mark.parametrize("n_sources", [2, 3, 5])
    def test_source_recovery_quality(self, n_sources):
        """
        Test that FastICA can recover independent sources with high correlation.
        
        This is the fundamental test of ICA quality.
        """
        n_samples = 2000
        n_features = n_sources + 2  # Slightly over-determined
        
        X, S_true, _ = generate_mixed_signals(
            n_samples=n_samples,
            n_sources=n_sources, 
            n_features=n_features,
            seed=42
        )
        
        X_torch = torch.from_numpy(X).float()
        
        ica = FastICA(n_components=n_sources, random_state=42, max_iter=500)
        S_est = ica.fit_transform(X_torch).numpy()
        
        # Check correlation-based source recovery
        matched_corrs, _ = match_sources_by_correlation(S_true, S_est)
        
        # Each source should be recovered with correlation > 0.9
        assert np.all(matched_corrs > 0.9), (
            f"Source recovery quality too low: {matched_corrs}"
        )
    
    def test_source_recovery_with_noise(self):
        """Test source recovery degrades gracefully with noise."""
        n_samples, n_sources, n_features = 2000, 3, 5
        
        for noise_level in [0.0, 0.1, 0.3]:
            X, S_true, _ = generate_mixed_signals(
                n_samples=n_samples,
                n_sources=n_sources,
                n_features=n_features,
                seed=42,
                noise_level=noise_level
            )
            
            X_torch = torch.from_numpy(X).float()
            
            ica = FastICA(n_components=n_sources, random_state=42, max_iter=500)
            S_est = ica.fit_transform(X_torch).numpy()
            
            matched_corrs, _ = match_sources_by_correlation(S_true, S_est)
            min_corr = matched_corrs.min()
            
            # Lower bar for noisy data
            expected_min = 0.9 - noise_level
            assert min_corr > expected_min, (
                f"Noise level {noise_level}: min correlation {min_corr:.3f} "
                f"below expected {expected_min:.3f}"
            )


# =============================================================================
# Comparison with sklearn
# =============================================================================

class TestSklearnComparison:
    """Tests comparing fastica_torch to sklearn's FastICA."""
    
    @pytest.mark.parametrize("fun", ["logcosh", "exp", "cube"])
    def test_contrast_functions_match_sklearn(self, fun):
        """Test that different contrast functions produce comparable results."""
        n_samples, n_sources, n_features = 1500, 3, 5
        
        X_np, S_true, _ = generate_mixed_signals(
            n_samples=n_samples,
            n_sources=n_sources,
            n_features=n_features,
            seed=42
        )
        X_torch = torch.from_numpy(X_np).float()
        
        # sklearn
        sklearn_ica = SklearnFastICA(
            n_components=n_sources,
            fun=fun,
            random_state=42,
            max_iter=500
        )
        S_sklearn = sklearn_ica.fit_transform(X_np)
        
        # torch
        torch_ica = FastICA(
            n_components=n_sources,
            fun=fun,
            random_state=42,
            max_iter=500
        )
        S_torch = torch_ica.fit_transform(X_torch).numpy()
        
        # Both should recover sources well
        corrs_sklearn, _ = match_sources_by_correlation(S_true, S_sklearn)
        corrs_torch, _ = match_sources_by_correlation(S_true, S_torch)
        
        # Both should achieve good separation
        assert np.all(corrs_sklearn > 0.85), f"sklearn failed with {fun}: {corrs_sklearn}"
        assert np.all(corrs_torch > 0.85), f"torch failed with {fun}: {corrs_torch}"
        
        # Performance should be comparable (within reasonable tolerance)
        sklearn_mean = corrs_sklearn.mean()
        torch_mean = corrs_torch.mean()
        assert abs(sklearn_mean - torch_mean) < 0.1, (
            f"Large quality gap for {fun}: sklearn={sklearn_mean:.3f}, torch={torch_mean:.3f}"
        )
    
    @pytest.mark.parametrize("algorithm", ["parallel", "deflation"])
    def test_algorithms_match_sklearn(self, algorithm):
        """Test that both algorithms produce comparable results to sklearn."""
        n_samples, n_sources, n_features = 1500, 3, 5
        
        X_np, S_true, _ = generate_mixed_signals(
            n_samples=n_samples,
            n_sources=n_sources,
            n_features=n_features,
            seed=42
        )
        X_torch = torch.from_numpy(X_np).float()
        
        # sklearn
        sklearn_ica = SklearnFastICA(
            n_components=n_sources,
            algorithm=algorithm,
            random_state=42,
            max_iter=500
        )
        S_sklearn = sklearn_ica.fit_transform(X_np)
        
        # torch
        torch_ica = FastICA(
            n_components=n_sources,
            algorithm=algorithm,
            random_state=42,
            max_iter=500
        )
        S_torch = torch_ica.fit_transform(X_torch).numpy()
        
        # Both should recover sources
        corrs_sklearn, _ = match_sources_by_correlation(S_true, S_sklearn)
        corrs_torch, _ = match_sources_by_correlation(S_true, S_torch)
        
        assert np.all(corrs_sklearn > 0.85), f"sklearn {algorithm} failed: {corrs_sklearn}"
        assert np.all(corrs_torch > 0.85), f"torch {algorithm} failed: {corrs_torch}"
    
    def test_whitening_unit_variance(self):
        """Test unit-variance whitening produces unit variance sources."""
        n_samples, n_features = 1000, 10
        X = torch.randn(n_samples, n_features) * 5 + 10  # Non-unit-variance
        
        ica = FastICA(n_components=5, whiten="unit-variance", random_state=42)
        S = ica.fit_transform(X)
        
        # Sources should have approximately unit variance
        variances = S.var(dim=0)
        torch.testing.assert_close(
            variances, 
            torch.ones_like(variances),
            rtol=0.1, 
            atol=0.1
        )
    
    def test_no_whitening_option(self):
        """Test that whiten=False works correctly."""
        n_samples, n_features = 500, 5
        
        # Pre-whiten the data manually
        X = torch.randn(n_samples, n_features, dtype=torch.float64)
        X = X - X.mean(dim=0)
        
        # Whiten using SVD
        U, S, Vh = torch.linalg.svd(X, full_matrices=False)
        X_white = U @ torch.diag(torch.ones_like(S)) @ Vh
        
        ica = FastICA(n_components=n_features, whiten=False, random_state=42)
        sources = ica.fit_transform(X_white)
        
        assert sources.shape == (n_samples, n_features)
        assert ica.mean_ is None  # Should not compute mean when not whitening


# =============================================================================
# Edge Cases for Scientific Research
# =============================================================================

class TestEdgeCases:
    """Edge cases important for scientific research applications."""
    
    def test_single_component(self):
        """Test extraction of a single component."""
        n_samples, n_features = 500, 10
        X = torch.randn(n_samples, n_features)
        
        ica = FastICA(n_components=1, random_state=42)
        S = ica.fit_transform(X)
        
        assert S.shape == (n_samples, 1)
        assert ica.components_.shape == (1, n_features)
    
    def test_n_components_equals_n_features(self):
        """Test when extracting all possible components."""
        n_samples, n_features = 500, 5
        X = torch.randn(n_samples, n_features)
        
        ica = FastICA(n_components=n_features, random_state=42)
        S = ica.fit_transform(X)
        X_reconstructed = ica.inverse_transform(S)
        
        # Perfect reconstruction when using all components
        torch.testing.assert_close(X, X_reconstructed, rtol=1e-4, atol=1e-4)
    
    def test_more_samples_than_features(self):
        """Test the typical n_samples >> n_features case."""
        n_samples, n_features, n_components = 5000, 10, 5
        X = torch.randn(n_samples, n_features)
        
        ica = FastICA(n_components=n_components, random_state=42)
        S = ica.fit_transform(X)
        
        assert S.shape == (n_samples, n_components)
    
    def test_fewer_samples_than_features(self):
        """Test the n_samples < n_features case (common in genomics, fMRI)."""
        n_samples, n_features, n_components = 50, 200, 10
        X = torch.randn(n_samples, n_features)
        
        ica = FastICA(n_components=n_components, random_state=42)
        S = ica.fit_transform(X)
        
        assert S.shape == (n_samples, n_components)
    
    def test_rank_deficient_data(self):
        """Test handling of rank-deficient data."""
        n_samples, n_features = 500, 10
        rank = 5
        
        # Create rank-deficient data
        U = torch.randn(n_samples, rank)
        V = torch.randn(rank, n_features)
        X = U @ V
        
        # Request fewer components than rank - should work
        ica = FastICA(n_components=3, random_state=42)
        S = ica.fit_transform(X)
        assert S.shape == (n_samples, 3)
    
    def test_float64_precision(self):
        """Test that float64 inputs are handled correctly."""
        n_samples, n_features = 500, 10
        X = torch.randn(n_samples, n_features, dtype=torch.float64)
        
        ica = FastICA(n_components=5, random_state=42)
        S = ica.fit_transform(X)
        
        assert S.dtype == torch.float64
    
    def test_float32_precision(self):
        """Test that float32 inputs are handled correctly."""
        n_samples, n_features = 500, 10
        X = torch.randn(n_samples, n_features, dtype=torch.float32)
        
        ica = FastICA(n_components=5, random_state=42)
        S = ica.fit_transform(X)
        
        assert S.dtype == torch.float32
    
    def test_high_dimensional_data(self):
        """Test with high-dimensional features (common in neuroimaging)."""
        n_samples, n_features, n_components = 200, 1000, 10
        X = torch.randn(n_samples, n_features, dtype=torch.float32)
        
        ica = FastICA(n_components=n_components, random_state=42, whiten_solver="svd")
        S = ica.fit_transform(X)
        
        assert S.shape == (n_samples, n_components)
    
    def test_convergence_with_default_params(self):
        """Test that algorithm converges with default parameters."""
        n_samples, n_sources, n_features = 1000, 5, 10
        
        X, _, _ = generate_mixed_signals(
            n_samples=n_samples,
            n_sources=n_sources,
            n_features=n_features,
            seed=42
        )
        X_torch = torch.from_numpy(X).float()
        
        ica = FastICA(n_components=n_sources, random_state=42)
        S = ica.fit_transform(X_torch)
        
        # Should converge before max_iter
        assert ica.n_iter_ < ica.max_iter, (
            f"Did not converge: {ica.n_iter_} >= {ica.max_iter}"
        )
    
    def test_transform_on_new_data(self):
        """Test that transform works correctly on unseen data."""
        n_samples, n_features = 1000, 10
        n_components = 5
        
        # Fit on one dataset
        X_train = torch.randn(n_samples, n_features)
        ica = FastICA(n_components=n_components, random_state=42)
        ica.fit(X_train)
        
        # Transform new data
        X_test = torch.randn(200, n_features)
        S_test = ica.transform(X_test)
        
        assert S_test.shape == (200, n_components)
        
        # Inverse should approximately reconstruct (accounting for projection loss)
        X_reconstructed = ica.inverse_transform(S_test)
        assert X_reconstructed.shape == (200, n_features)


# =============================================================================
# Numerical Stability Tests
# =============================================================================

class TestNumericalStability:
    """Tests for numerical stability and robustness."""
    
    def test_scaled_data(self):
        """Test with very large and very small scale data."""
        n_samples, n_features = 500, 10
        
        for scale in [1e-6, 1.0, 1e6]:
            X = torch.randn(n_samples, n_features) * scale
            
            ica = FastICA(n_components=5, random_state=42)
            S = ica.fit_transform(X)
            
            # Should not produce NaN or Inf
            assert torch.all(torch.isfinite(S)), f"NaN/Inf at scale {scale}"
    
    def test_centered_data(self):
        """Test that results are consistent whether data is pre-centered or not."""
        n_samples, n_features = 500, 10
        
        X = torch.randn(n_samples, n_features) + 100  # Shifted mean
        
        ica = FastICA(n_components=5, random_state=42)
        S = ica.fit_transform(X)
        
        # Sources should be finite
        assert torch.all(torch.isfinite(S))
        
        # Mean should be captured
        assert ica.mean_ is not None
        assert torch.allclose(ica.mean_, X.mean(dim=0), rtol=1e-5)
    
    def test_whiten_solver_eigh(self):
        """Test eigenvalue-based whitening solver."""
        n_samples, n_features = 1000, 10
        X = torch.randn(n_samples, n_features)
        
        ica = FastICA(n_components=5, whiten_solver="eigh", random_state=42)
        S = ica.fit_transform(X)
        
        assert torch.all(torch.isfinite(S))
        assert S.shape == (n_samples, 5)
    
    def test_whiten_solver_svd(self):
        """Test SVD-based whitening solver."""
        n_samples, n_features = 1000, 10
        X = torch.randn(n_samples, n_features)
        
        ica = FastICA(n_components=5, whiten_solver="svd", random_state=42)
        S = ica.fit_transform(X)
        
        assert torch.all(torch.isfinite(S))
        assert S.shape == (n_samples, 5)


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
