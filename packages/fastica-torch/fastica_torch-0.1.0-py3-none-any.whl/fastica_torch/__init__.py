"""
fastica_torch: PyTorch implementation of the FastICA algorithm.

This package provides a GPU-accelerated FastICA implementation that is
compatible with the sklearn.decomposition.FastICA API.
"""

from fastica_torch.fastica import (
    FastICA,
    _gs_decorrelation,
    _sym_decorrelation,
    _logcosh,
    _exp,
    _cube,
    _ica_def,
    _ica_par,
    _randomized_svd,
)

__version__ = "0.1.0"
__author__ = "Richard Hakim"

__all__ = [
    "FastICA",
    "_gs_decorrelation",
    "_sym_decorrelation",
    "_logcosh",
    "_exp",
    "_cube",
    "_ica_def",
    "_ica_par",
    "_randomized_svd",
]
