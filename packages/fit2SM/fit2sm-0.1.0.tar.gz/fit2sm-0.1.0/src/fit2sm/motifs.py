"""Motif-related utilities for binary undirected graphs."""

from __future__ import annotations

import numpy as np


def calculate_S(adjacency: np.ndarray) -> float:
    """Compute the number of v-motifs (wedges) in a binary undirected network.

    The function implements:
        S = 0.5 * sum_i k_i (k_i - 1),
    where k_i is the degree of node i.

    Parameters
    ----------
    adjacency : numpy.ndarray
        Binary symmetric adjacency matrix with a zero diagonal.

    Returns
    -------
    S : float
        Number of wedges (v-motifs).
    """
    A = np.asarray(adjacency, dtype=float)
    k = A.sum(axis=1)
    S = 0.5 * (np.sum(k * k) - np.sum(k))
    return float(S)
