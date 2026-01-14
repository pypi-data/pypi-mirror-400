"""
PyTorch implementation of the FastICA algorithm for Independent Component Analysis.

This module provides a GPU-accelerated implementation of the FastICA algorithm,
replicating the interface and logic of ``sklearn.decomposition.FastICA``. It can
be used as a drop-in replacement when working with PyTorch tensors.

Algorithm Overview
------------------
Independent Component Analysis (ICA) is a computational method for separating a
multivariate signal into additive, statistically independent components. The
FastICA algorithm is a popular fixed-point iteration scheme that maximizes the
non-Gaussianity of the estimated components using a contrast function (negentropy
approximation).

The algorithm assumes the data model: ``X = A @ S``, where:
- ``X`` is the observed data matrix (n_samples, n_features)
- ``A`` is the unknown mixing matrix
- ``S`` is the matrix of latent independent sources

FastICA estimates an unmixing matrix ``W`` such that ``S_hat = W @ X`` recovers
the original sources (up to sign and permutation ambiguity).

Two algorithmic variants are supported:
- **parallel**: Updates all components simultaneously (faster on GPUs)
- **deflation**: Extracts components one-by-one (sequential)

References
----------
.. [1] A. Hyvarinen and E. Oja, "Independent Component Analysis: Algorithms
       and Applications", Neural Networks, 13(4-5):411-430, 2000.
.. [2] A. Hyvarinen, "Fast and Robust Fixed-Point Algorithms for Independent
       Component Analysis", IEEE Trans. Neural Networks, 10(3):626-634, 1999.
.. [3] scikit-learn FastICA implementation:
       https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.FastICA.html

Example
-------
.. code-block:: python

    import torch
    from fastica_torch import FastICA

    # Generate mixed signals
    n_samples, n_features = 1000, 5
    X = torch.randn(n_samples, n_features)

    # Fit FastICA
    ica = FastICA(n_components=3, random_state=42)
    sources = ica.fit_transform(X)

    # Recover sources from new data
    X_new = torch.randn(100, n_features)
    sources_new = ica.transform(X_new)

    # Reconstruct original space
    X_reconstructed = ica.inverse_transform(sources)

RH 2024
"""

import warnings
from typing import Optional, Union, Tuple, Callable, Dict, List

import torch
import torch.nn as nn
from torch import Tensor

import numpy as np


def _randomized_svd(
    M: Tensor, 
    n_components: int, 
    n_oversamples: int = 10, 
    n_iter: int = "auto",
    power_iteration_normalizer: str = 'auto',
    random_state: Optional[int] = None
) -> Tuple[Tensor, Tensor, Tensor]:
    """
    Computes a truncated randomized SVD.
    M is (m, n). 
    Returns u, s, vh (like torch.linalg.svd)
        u: (m, n_components)
        s: (n_components,)
        vh: (n_components, n)
    """
    m, n = M.shape
    
    if random_state is not None:
        torch.manual_seed(random_state)
        
    # Decide n_iter
    if n_iter == 'auto':
        # Simple heuristic or default to small number like sklearn
        n_iter = 7 if n_components < 0.1 * min(M.shape) else 4

    n_random = n_components + n_oversamples
    
    # 1. Random Projection Matrix Omega
    # Draw (n, n_random) Gaussian
    # If m < n (short fat), we might want to transpose logic? 
    # Standard algo: Q = Range(M @ Omega)
    # If M is (m, n), Omega should be (n, n_random), resulting Q is (m, n_random).
    
    Omega = torch.randn(n, n_random, dtype=M.dtype, device=M.device)
    
    # 2. Compute range Y
    Y = M @ Omega
    
    # 3. Power Iteration (to refine range)
    # Y = (M M^T)^q Y
    for _ in range(n_iter):
        # LU factorization or QR is typical for stabilization
        if power_iteration_normalizer == 'auto' or power_iteration_normalizer == 'QR':
            Y, _ = torch.linalg.qr(Y)
            
        Z = M.T @ Y
        if power_iteration_normalizer == 'auto' or power_iteration_normalizer == 'QR':
            Z, _ = torch.linalg.qr(Z)
            
        Y = M @ Z

    # 4. Orthogonalize Y -> Q
    Q, _ = torch.linalg.qr(Y)
    
    # 5. Form B = Q^T M
    B = Q.T @ M
    
    # 6. SVD of B (small: n_random x n)
    # B is (k, n)
    u_hat, s, vh = torch.linalg.svd(B, full_matrices=False)
    
    # 7. U = Q @ u_hat
    u = Q @ u_hat
    
    # Truncate
    return u[:, :n_components], s[:n_components], vh[:n_components, :]


def _gs_decorrelation(
    w: Tensor, 
    W: Tensor, 
    j: int
) -> Tensor:
    """
    Orthonormalize the vector ``w`` with respect to the first ``j`` rows of ``W``
    using Gram-Schmidt decorrelation.

    This function subtracts the projection of ``w`` onto the subspace spanned by
    the first ``j`` vectors in ``W``, ensuring orthogonality.
    
    Args:
        w (Tensor): 
            The weight vector to be orthogonalized. 
            Shape: (n_features,).
        W (Tensor): 
            The matrix containing the previously extracted components.
            Shape: (n_components, n_features).
        j (int): 
            The index up to which the rows of ``W`` are used for orthogonalization.
            ``w`` will be made orthogonal to ``W[0], ..., W[j-1]``.

    Returns:
        (Tensor): 
            w_orth (Tensor):
                The orthogonalized weight vector.
                Shape: (n_features,).
    """
    # ---------------------------------------------------------
    # Gram-Schmidt Process:
    # w_new = w - sum_{k=0}^{j-1} <w, W[k]> * W[k]
    #
    # In matrix form:
    # w_new = w - (w @ W[:j].T) @ W[:j]
    #
    # Note: We assume that the rows of W are already normalized.
    # ---------------------------------------------------------
    
    if j > 0:
        # Calculate projection coefficients
        # Shape: (1, n_features) @ (n_features, j) -> (1, j) -> (j,)
        projections = w @ W[:j].T
        
        # Subtract projections
        # Shape: (j,) @ (j, n_features) -> (n_features,)
        w = w - projections @ W[:j]
    
    return w


def _sym_decorrelation(W: Tensor) -> Tensor:
    """
    Perform symmetric decorrelation on the matrix ``W``.
    
    This ensures that the rows of ``W`` are orthonormal (W @ W.T = I) by solving:
    ``W <- (W @ W.T)^{-1/2} @ W``
    
    This is used in the parallel FastICA algorithm to prevent all components
    from converging to the same independent component.
    
    Args:
        W (Tensor):
            The mixing matrix to decorrelate. 
            Shape: (n_components, n_features).
            
    Returns:
        (Tensor):
            W_orth (Tensor):
                The decorrelated matrix.
                Shape: (n_components, n_features).
    """
    # ---------------------------------------------------------
    # Symmetric Decorrelation
    # We want to find a matrix W' such that W' @ W'.T = I.
    # The symmetric solution is W' = (W @ W.T)^{-1/2} @ W.
    #
    # We compute (W @ W.T)^{-1/2} using Eigendecomposition:
    # 1. K = W @ W.T
    # 2. K = U @ S @ U.T (where S is diagonal matrix of eigenvalues)
    # 3. K^{-1/2} = U @ S^{-1/2} @ U.T
    # ---------------------------------------------------------

    # Eigen decomposition of the Gram matrix
    # W (n_comp, n_feat) @ W.T (n_feat, n_comp) -> (n_comp, n_comp)
    gram = W @ W.T
    
    # s: eigenvalues (n_comp,)
    # u: eigenvectors (n_comp, n_comp)
    s, u = torch.linalg.eigh(gram)
    
    # Clip small eigenvalues to avoid numerical instability
    tiny = torch.finfo(W.dtype).tiny
    s = torch.clamp(s, min=tiny)

    # Compute inverse square root of eigenvalues
    # Shape: (n_comp,)
    inv_sqrt_s = 1.0 / torch.sqrt(s)
    
    # Construct (W @ W.T)^{-1/2}
    # U @ S^{-1/2} @ U.T
    #
    # We can optimize the multiplication:
    # (U * inv_sqrt_s) scales columns of U by inv_sqrt_s
    # Proof: (U @ diag(s))_ij = sum_k U_ik * delta_kj * s_j = U_ij * s_j
    # So u * inv_sqrt_s is equivalent to U @ diag(inv_sqrt_s)
    
    # Shape: (n_comp, n_comp)
    K_inv_sqrt = (u * inv_sqrt_s) @ u.T
    
    # Apply to W
    # Shape: (n_comp, n_comp) @ (n_comp, n_features) -> (n_comp, n_features)
    W_orth = K_inv_sqrt @ W
    
    return W_orth


def _logcosh(x: Tensor, fun_args: Dict = None) -> Tuple[Tensor, Tensor]:
    """
    Logcosh approximation to neg-entropy.
    
    G(x) = (1/alpha) * log(cosh(alpha * x))
    g(x) = tanh(alpha * x)
    g'(x) = alpha * (1 - tanh^2(alpha * x))
    
    Args:
        x (Tensor): 
            Input tensor. 
            Shape: (n_components, n_samples).
        fun_args (Dict): 
            Arguments. 'alpha' defaults to 1.0.
        
    Returns:
        (Tuple[Tensor, Tensor]): 
            gx (Tensor): 
                The value of the first derivative g(x).
                Shape: (n_components, n_samples).
            g_x (Tensor): 
                The mean of the second derivative g'(x) along the sample dimension.
                Shape: (n_components,).
    """
    if fun_args is None:
        fun_args = {}
    alpha = fun_args.get("alpha", 1.0)

    # Apply alpha scaling
    x = x * alpha
    
    # Calculate tanh
    gx = torch.tanh(x)
    
    # Calculate derivative mean: alpha * (1 - tanh^2)
    # Note: gx is already tanh(alpha * x)
    g_x_prim = alpha * (1 - gx**2)
    
    # Average over samples (last dimension)
    g_x = g_x_prim.mean(dim=-1)
    
    return gx, g_x


def _exp(x: Tensor, fun_args: Dict = None) -> Tuple[Tensor, Tensor]:
    """
    Exp approximation to neg-entropy.
    
    G(x) = -exp(-x^2/2)
    g(x) = x * exp(-x^2/2)
    g'(x) = (1 - x^2) * exp(-x^2/2)
    
    Args:
        x (Tensor): 
            Input tensor.
            Shape: (n_components, n_samples).
        fun_args (Dict): 
            Unused in this function.
            
    Returns:
        (Tuple[Tensor, Tensor]): 
            gx (Tensor): 
                The value of the first derivative g(x).
            g_x (Tensor): 
                The mean of the second derivative g'(x) along the sample dimension.
    """
    exp = torch.exp(-(x**2) / 2)
    gx = x * exp
    g_x = ((1 - x**2) * exp).mean(dim=-1)
    return gx, g_x


def _cube(x: Tensor, fun_args: Dict = None) -> Tuple[Tensor, Tensor]:
    """
    Cube approximation to neg-entropy.
    
    G(x) = x^4 / 4
    g(x) = x^3
    g'(x) = 3 * x^2
    
    Args:
        x (Tensor): 
            Input tensor.
            Shape: (n_components, n_samples).
        fun_args (Dict): 
            Unused.
            
    Returns:
        (Tuple[Tensor, Tensor]): 
            gx (Tensor): 
                The value of the first derivative g(x).
            g_x (Tensor): 
                The mean of the second derivative g'(x) along the sample dimension.
    """
    return x**3, (3 * x**2).mean(dim=-1)


def _ica_def(
    X: Tensor,
    tol: float,
    g: Callable,
    fun_args: Dict,
    max_iter: int,
    w_init: Tensor
) -> Tuple[Tensor, int]:
    """
    Deflationary FastICA: Extracts components one by one.
    
    Args:
        X (Tensor): 
            Whitened data matrix. 
            Shape: (n_features, n_samples).
        tol (float): 
            Convergence tolerance.
        g (Callable): 
            Contrast function generator (returns gx and g_x mean).
        fun_args (Dict): 
            Arguments for the contrast function.
        max_iter (int): 
            Maximum number of iterations.
        w_init (Tensor): 
            Initial unmixing matrix. 
            Shape: (n_components, n_features).

    Returns:
        (Tuple[Tensor, int]):
            W (Tensor): 
                The estimated unmixing matrix.
                Shape: (n_components, n_features).
            n_iter (int): 
                Maximum iterations taken for any component.
    """
    n_components = w_init.shape[0]
    dtype = X.dtype
    device = X.device
    W = torch.zeros((n_components, n_components), dtype=dtype, device=device)
    n_iter = []

    # Loop over each component to extract
    for j in range(n_components):
        w = w_init[j, :].clone()
        
        # Normalize
        w /= torch.sqrt((w**2).sum())

        i = 0
        for i in range(max_iter):
            # Project data onto current w
            # Shape: (n_features,) @ (n_features, n_samples) -> (n_samples,)
            wtx = w @ X
            
            # Apply non-linearity
            # gx shape: (n_samples,)
            # g_wtx shape: scalar (mean)
            gx, g_wtx = g(wtx, fun_args)
            
            # Update rule for deflation:
            # w+ = E[x * g(w^T x)] - E[g'(w^T x)] * w
            #
            # X * gx is (n_features, n_samples) * (n_samples,) [broadcasting]
            # Mean is over samples (dim=1)
            
            w1 = (X * gx.unsqueeze(0)).mean(dim=1) - g_wtx.mean() * w
            
            # Decorrelate w1 with respect to previously found vectors W[:j]
            w1 = _gs_decorrelation(w1, W, j)
            
            # Normalize
            w1 /= torch.sqrt((w1**2).sum())
            
            # Check convergence
            # Convergence happens if w1 is parallel to w (dot product is 1 or -1)
            lim = torch.abs(torch.abs((w1 * w).sum()) - 1)
            w = w1
            
            if lim < tol:
                break
        
        n_iter.append(i + 1)
        W[j, :] = w

    return W, max(n_iter)


def _ica_par(
    X: Tensor,
    tol: float,
    g: Callable,
    fun_args: Dict,
    max_iter: int,
    w_init: Tensor
) -> Tuple[Tensor, int]:
    """
    Parallel FastICA: Extracts all components simultaneously.
    
    Args:
        X (Tensor): 
            Whitened data matrix. 
            Shape: (n_features, n_samples).
        tol (float): 
            Convergence tolerance.
        g (Callable): 
            Contrast function generator.
        fun_args (Dict): 
            Arguments for the contrast function.
        max_iter (int): 
            Maximum number of iterations.
        w_init (Tensor): 
            Initial unmixing matrix. 
            Shape: (n_components, n_features).

    Returns:
        (Tuple[Tensor, int]):
            W (Tensor): 
                The estimated unmixing matrix.
                Shape: (n_components, n_features).
            n_iter (int): 
                Number of iterations taken.
    """
    # Initialize W with symmetric decorrelation to ensure starting orthonormality
    W = _sym_decorrelation(w_init)
    
    # p_ is the number of samples, used for correct scaling if needed, 
    # though mean() handles 1/N.
    # Here it seems unused in scalar form because mean() is used.
    # Wait, the sklearn implementation is:
    # W1 = (np.dot(gwtx, X.T) / p_ - g_wtx[:, np.newaxis] * W)
    # If using torch.mean, we don't need explicit division by p_.
    
    ii = 0
    for ii in range(max_iter):
        # 1. Project data onto all components
        # (n_comp, n_feat) @ (n_feat, n_samples) -> (n_comp, n_samples)
        wtx = W @ X
        
        # 2. Apply non-linearity
        # gwtx: (n_comp, n_samples), g_wtx: (n_comp,)
        gwtx, g_wtx = g(wtx, fun_args)
        
        # 3. Update rule
        # W+ = E[g(Wx)x^T] - diag(E[g'(Wx)])W
        #
        # Term 1: E[g(Wx)x^T]
        # (n_comp, n_samples) @ (n_samples, n_feat) -> (n_comp, n_feat)
        # We use mean, so it includes 1/N factor.
        term1 = (gwtx @ X.T) / X.shape[1] 
        
        # Term 2: diag(E[g'(Wx)])W
        # g_wtx is (n_comp,) -> unsqueeze -> (n_comp, 1)
        # Broadcasts to scale rows of W
        term2 = g_wtx.unsqueeze(1) * W
        
        W1 = term1 - term2
        
        # 4. Symmetric decorrelation (Orthogonalization)
        # This prevents components from collapsing onto the same subspace
        W1 = _sym_decorrelation(W1)
        
        # 5. Check convergence
        # We check the max change in direction for any component.
        # Ideally <w_new, w_old> should be close to 1 or -1.
        #
        # Element-wise product then sum over features -> dot product for each row
        # dot_products shape: (n_components,)
        dot_products = torch.sum(W1 * W, dim=1)
        
        lim = torch.max(torch.abs(torch.abs(dot_products) - 1))
        
        W = W1
        if lim < tol:
            break
            
    return W, ii + 1


class FastICA(nn.Module):
    """
    FastICA: a fast algorithm for Independent Component Analysis.
    
    PyTorch implementation which replicates ``sklearn.decomposition.FastICA``.
    
    The algorithm assumes input data can be modeled as linear combinations of
    independent, non-Gaussian sources. It attempts to "un-mix" the data by
    finding an unmixing matrix W such that ``S = W @ K @ X`` (if whitened)
    or ``S = W @ X`` (if not whitened) are the independent sources.

    RH 2024

    Args:
        n_components (int, optional):
            Number of components to use. If None is passed, all are used.
        algorithm (str): 
            'parallel' or 'deflation'.
            'parallel' is generally faster on modern hardware (GPUs).
            'deflation' extracts components one by one.
        whiten (str or bool): 
            Specify the whitening strategy.
            - 'unit-variance' (default): Whitens data so each component has unit variance.
            - False: No whitening is performed.
            - 'arbitrary-variance': treated similarly to unit-variance logic.
        fun (str or callable):
            The functional form of the G function used in the approximation to
            neg-entropy. Could be 'logcosh', 'exp', or 'cube'.
        fun_args (dict, optional):
            Arguments to send to the functional form (e.g. {'alpha': 1.0}).
        max_iter (int):
            Maximum number of iterations during fit.
        tol (float):
            Tolerance on update at each iteration.
        w_init (Tensor, optional):
            Initial un-mixing array. Shape (n_components, n_components).
            If None, a random initialization is used.
        whiten_solver (str):
            'svd' or 'eigh'.
            - 'eigh': Using eigen-decomposition. Efficient for large N, small D.
            - 'svd': Using Singular Value Decomposition. Efficient for N < D.
        svd_solver (str):
            'auto', 'full', or 'randomized'.
            If 'auto': uses 'randomized' if input is large and n_components is small, else 'full'.
            If 'full': uses torch.linalg.svd (standard).
            If 'randomized': uses a robust randomized SVD implementation.
        float64_covariance (bool):
            If True, computes covariance matrix in float64 precision to avoid overflow
            likely to happen with large tensors. Defaults to True.
        random_state (int, optional):
            Seed for random number generator.

    Attributes:
        components_ (Tensor):
            The linear operator to apply to the data to get the independent sources.
            Shape: (n_components, n_features).
        mixing_ (Tensor):
            The pseudo-inverse of ``components_``. Maps sources to data.
            Shape: (n_features, n_components).
        mean_ (Tensor):
            The mean over features. Only set if ``whiten`` is True.
        whitening_ (Tensor):
            The pre-whitening matrix. Shape: (n_components, n_features).
        n_iter_ (int):
            Number of iterations taken to converge.
    """
    def __init__(
        self,
        n_components: Optional[int] = None,
        algorithm: str = "parallel",
        whiten: Union[str, bool] = "unit-variance",
        fun: str = "logcosh",
        fun_args: Optional[Dict] = None,
        max_iter: int = 200,
        tol: float = 1e-4,
        w_init: Optional[Tensor] = None,
        whiten_solver: str = "svd",
        svd_solver: str = "auto",
        float64_covariance: bool = False,
        random_state: Optional[int] = None,
    ):
        super().__init__()
        self.n_components = n_components
        self.algorithm = algorithm
        self.whiten = whiten
        self.fun = fun
        self.fun_args = fun_args
        self.max_iter = max_iter
        self.tol = tol
        self.w_init = w_init
        self.whiten_solver = whiten_solver
        self.svd_solver = svd_solver
        self.float64_covariance = float64_covariance
        self.random_state = random_state
        
        # Attributes to be set during adaptation
        self.components_: Optional[Tensor] = None
        self.mixing_: Optional[Tensor] = None
        self.mean_: Optional[Tensor] = None
        self.whitening_: Optional[Tensor] = None
        self._unmixing: Optional[Tensor] = None
        self.n_iter_: Optional[int] = None
        
    def _fit_transform(self, X: Tensor, compute_sources: bool = False) -> Optional[Tensor]:
        """
        Fit the model and optionally return sources.
        
        Args:
            X (Tensor): 
                Training data. 
                Shape: (n_samples, n_features).
            compute_sources (bool): 
                Whether to return the estimated sources.
            
        Returns:
            (Tensor or None): 
                Sources matrix. 
                Shape: (n_samples, n_components).
        """
        if not torch.all(torch.isfinite(X)):
             raise ValueError("Input X contains NaN or Inf.")
             
        n_samples, n_features = X.shape
        
        # Handle Random State
        if self.random_state is not None:
            torch.manual_seed(self.random_state)
            
        # Parse non-linear function
        fun_args = {} if self.fun_args is None else self.fun_args
        
        if self.fun == "logcosh":
            g = _logcosh
        elif self.fun == "exp":
            g = _exp
        elif self.fun == "cube":
            g = _cube
        elif callable(self.fun):
            g = self.fun
        else:
            raise ValueError(f"Unknown function {self.fun}")
            
        # Transpose data to (n_features, n_samples) for algorithm usage
        # This keeps features as rows, which is typical for ICA literature logic
        XT = X.T 
        
        # Determine n_components
        n_components = self.n_components
        if not self.whiten and n_components is not None:
            n_components = None # Sklearn ignores n_components if whiten=False
        
        if n_components is None:
            n_components = min(n_samples, n_features)
            
        # ----------------------------------------------------------------------
        # Whitening
        # ----------------------------------------------------------------------
        if self.whiten:
            # Centering
            X_mean = XT.mean(dim=-1)
            XT = XT - X_mean.unsqueeze(1)
            
            # Compute Covariance / SVD
            if self.whiten_solver == "eigh":
                # Decision: Standard Eigh (N >= D) vs Dual Eigh (N < D)
                # Standard: Covariance is D x D (n_features x n_features)
                # Dual: Covariance is N x N (n_samples x n_samples)
                
                if n_samples < n_features:
                    # Dual Eigh
                    if self.float64_covariance:
                        # Compute covariance in float64 to avoid overflow with large sums
                        XT_cov = XT.to(torch.float64)
                    else:
                        XT_cov = XT
                        
                    covariance = XT_cov.T @ XT_cov # (n_samples, n_samples)
                    
                    if not torch.all(torch.isfinite(covariance)):
                         raise ValueError("Covariance matrix contains NaN or Inf. Input data may be too large for float32 accumulation or contains invalid values.")

                    d, v = torch.linalg.eigh(covariance)
                    
                    # Cast back to original dtype
                    d = d.to(XT.dtype)
                    v = v.to(XT.dtype)
                    
                    # Sort eigenvectors
                    d = torch.flip(d, dims=[0])
                    v = torch.flip(v, dims=[1])
                    
                    # Filter
                    eps = torch.finfo(d.dtype).eps * 10
                    valid_mask = d > eps
                    d = d[valid_mask]
                    v = v[:, valid_mask]
                    
                    # Calculate u (features x valid)
                    # u = X @ v / sqrt(lambda)
                    # Shape: (n_features, n_samples) @ (n_samples, k) -> (n_features, k)
                    
                    d_sqrt = torch.sqrt(d)
                    u = (XT @ v) / d_sqrt.unsqueeze(0)
                    
                    # Keep only top n_components
                    # Note: we might have fewer valid components than n_components
                    current_k = min(n_components, u.shape[1])
                    if current_k < n_components:
                         warnings.warn(f"n_components={n_components} larger than rank {u.shape[1]}.")
                    
                    u = u[:, :current_k]
                    d = d_sqrt[:current_k]
                
                else:
                    # Standard Eigh (D x D)
                    covariance = XT @ XT.T
                    d, u = torch.linalg.eigh(covariance) 
                    
                    # Sort
                    d = torch.flip(d, dims=[0])
                    u = torch.flip(u, dims=[1])
                    
                    # Filter
                    eps = torch.finfo(d.dtype).eps * 10
                    d[d < eps] = eps
                    d = torch.sqrt(d)
                
            elif self.whiten_solver == "svd":
                use_randomized = False
                if self.svd_solver == 'randomized':
                    use_randomized = True
                elif self.svd_solver == 'auto':
                    # Heuristic: if matrix is large and we want small k
                    # Thresholds are arbitrary, based on sklearn logic
                    max_dim = max(XT.shape)
                    if max_dim >= 2000 and n_components < 0.1 * min(XT.shape):
                        use_randomized = True
                
                if use_randomized:
                    u, d, _ = _randomized_svd(XT, n_components=n_components, random_state=self.random_state)
                else:
                    # SVD of data matrix directly
                    # XT = U @ S @ V.T
                    # Try default driver first, if it fails, fallback to gesvd
                    try:
                        u, d, _ = torch.linalg.svd(XT, full_matrices=False)
                    except RuntimeError as e:
                        if 'gesdd' in str(e) or 'LAPACK' in str(e) or 'Parameter' in str(e):
                             warnings.warn("SVD failed with default driver (likely gesdd). Retrying with driver='gesvd'.")
                             u, d, _ = torch.linalg.svd(XT, full_matrices=False, driver='gesvd')
                        else:
                            raise e
            
            # Flip signs (optional)
            u = u * torch.sign(u[0:1, :])
            
            # Compute Whitening Matrix K
            K = (u / d.unsqueeze(0)).T[:n_components] # (n_components, n_features)
            
            # Project Data
            X1 = K @ XT 
            X1 *= np.sqrt(n_samples)
            
        else:
            X1 = XT
            K = None
            X_mean = None
            
        # ----------------------------------------------------------------------
        # Initialization
        # ----------------------------------------------------------------------
        if self.w_init is None:
            # Random initialization
            w_init = torch.randn(
                n_components, n_components, 
                dtype=X1.dtype, device=X1.device
            )
        else:
            w_init = self.w_init
            
        kwargs = {
            "tol": self.tol,
            "g": g,
            "fun_args": fun_args,
            "max_iter": self.max_iter,
            "w_init": w_init,
        }
        
        # ----------------------------------------------------------------------
        # ICA Optimization Loop
        # ----------------------------------------------------------------------
        if self.algorithm == "parallel":
            W, n_iter = _ica_par(X1, **kwargs)
        elif self.algorithm == "deflation":
            W, n_iter = _ica_def(X1, **kwargs)
        else:
            raise ValueError(f"Unknown algorithm {self.algorithm}")
            
        self.n_iter_ = n_iter
        
        # ----------------------------------------------------------------------
        # Reconstruct Sources
        # ----------------------------------------------------------------------
        if compute_sources:
            if self.whiten:
                S = (W @ K @ XT).T
            else:
                S = (W @ XT).T
        else:
            S = None
            
        # ----------------------------------------------------------------------
        # Post-processing and Attribute storage
        # ----------------------------------------------------------------------
        if self.whiten:
            if self.whiten == "unit-variance":
                if S is None:
                    S = (W @ K @ XT).T
                
                S_std = torch.std(S, dim=0, keepdim=True, correction=0)
                
                S = S / S_std
                W = W / S_std.T
            
            self.components_ = W @ K
            self.mean_ = X_mean
            self.whitening_ = K
        else:
            self.components_ = W
            
        # mixing_
        self.mixing_ = torch.linalg.pinv(self.components_)
        self._unmixing = W
        
        return S

    def fit(self, X: Tensor, y=None) -> "FastICA":
        """
        Fit the model to X.

        Computes the unmixing matrix by maximizing the non-Gaussianity of
        the estimated sources. Does not compute the sources themselves.

        Args:
            X (Tensor):
                Training data of shape (n_samples, n_features).
            y:
                Ignored. Present for API consistency with sklearn.

        Returns:
            (FastICA):
                self (FastICA):
                    Returns the fitted instance.
        """
        self._fit_transform(X, compute_sources=False)
        return self
        
    def fit_transform(self, X: Tensor, y=None) -> Tensor:
        """
        Fit the model and recover the sources from X.

        This is equivalent to calling ``fit(X)`` followed by ``transform(X)``,
        but more efficient as it avoids recomputing projections.

        Args:
            X (Tensor):
                Training data of shape (n_samples, n_features).
            y:
                Ignored. Present for API consistency with sklearn.

        Returns:
            (Tensor):
                S (Tensor):
                    Estimated source signals of shape (n_samples, n_components).
                    Each column is an independent component.
        """
        return self._fit_transform(X, compute_sources=True)
    
    def transform(self, X: Tensor) -> Tensor:
        """
        Apply the unmixing matrix to recover sources from X.

        Projects the data onto the learned independent components. The model
        must be fitted before calling this method.

        Args:
            X (Tensor):
                Data to transform of shape (n_samples, n_features).

        Returns:
            (Tensor):
                S (Tensor):
                    Estimated sources of shape (n_samples, n_components).
        """
        if self.whiten:
            X = X - self.mean_
        return X @ self.components_.T

    def inverse_transform(self, S: Tensor) -> Tensor:
        """
        Transform the sources back to the original mixed data space.

        Applies the mixing matrix to reconstruct the data. This is the inverse
        operation of ``transform``.

        Args:
            S (Tensor):
                Source signals of shape (n_samples, n_components).

        Returns:
            (Tensor):
                X_reconstructed (Tensor):
                    Reconstructed data of shape (n_samples, n_features).
        """
        X = S @ self.mixing_.T
        if self.whiten:
            X = X + self.mean_
        return X
