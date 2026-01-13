r"""Unit tests for dcGM, UBCM, and Fit2SM solvers.

These tests intentionally avoid private datasets (e.g., eMID) by generating
an undirected binary synthetic network with $N=200$ nodes. The generator
produces node strengths that are positively correlated with the realised
degrees, and then evaluates whether each solver reproduces its target
constraints within prescribed tolerances.

The constraints are:
- dcGM: reproduce the number of links $L$ given strengths.
- UBCM: reproduce the degree sequence $k$.
- Fit2SM: reproduce $(L, S)$ where $S = \sum_i \binom{k_i}{2}$.
"""

from __future__ import annotations

from dataclasses import is_dataclass
from typing import Tuple

import numpy as np
import pytest

from fit2sm.dcgm import DcGMModel
from fit2sm.ubcm import UBCMModel
from fit2sm.fit2sm import Fit2SMModel


# ------------------------------------------------------------
# Tolerances used to declare "constraints reproduced"
# ------------------------------------------------------------
TOL_L_REL = 1e-6  # relative tolerance on L
TOL_S_REL = 1e-6  # relative tolerance on S
TOL_K_REL = 1e-6  # relative tolerance on degrees (max over nodes)


def _numba_is_importable() -> bool:
    """Return True if Numba can be imported in the current environment."""
    try:  # pragma: no cover
        import numba  # noqa: F401

        return True
    except Exception:
        return False


def _rel_err(a: float, b: float) -> float:
    r"""Return $|a-b|/\max(1,|b|)$ to obtain a scale-robust relative error."""
    return float(abs(a - b) / max(1.0, abs(b)))


def _two_star_count_from_degrees(k: np.ndarray) -> float:
    r"""Return $S=\sum_i \binom{k_i}{2}$ for (possibly non-integer) degrees."""
    k = np.asarray(k, dtype=float)
    return float(0.5 * np.sum(k * (k - 1.0)))


def _generate_synthetic_snapshot(
    n: int = 200,
    mean_degree: float = 12.0,
    noise_std: float = 0.15,
    seed: int = 12345,
) -> Tuple[np.ndarray, np.ndarray]:
    r"""Generate a synthetic undirected binary network and correlated strengths.

    Construction
    -----------
    1) Draw positive strengths $s_i$ with small additive noise.
    2) Choose $z$ in the sparse approximation $L \approx z \sum_{i<j} s_i s_j$
       so that the expected number of links is close to $N \bar{k}/2$.
    3) Sample edges independently with
       $p_{ij} = \frac{z s_i s_j}{1 + z s_i s_j}$.

    In the sparse regime, $\mathbb{E}[k_i] \propto s_i$, yielding an
    approximately linear correlation between strengths and degrees.

    Returns
    -------
    A_bin:
        Symmetric adjacency matrix with zeros on the diagonal.
    strengths:
        Strength vector $s$ used as fitness proxy.
    """
    rng = np.random.default_rng(int(seed))

    # Strengths: positive and moderately heterogeneous.
    s0 = rng.uniform(0.1, 2.0, size=int(n))
    s = s0 + rng.normal(loc=0.0, scale=float(noise_std), size=int(n))
    s = np.clip(s, 1e-3, None)

    # Target link count.
    L_target = 0.5 * float(n) * float(mean_degree)

    # Sparse approximation for the product sum.
    sum_s = float(np.sum(s))
    sum_s2 = float(np.sum(s * s))
    sum_sisj = 0.5 * (sum_s * sum_s - sum_s2)
    z = L_target / max(sum_sisj, 1e-12)

    # Sample adjacency.
    A = np.zeros((int(n), int(n)), dtype=np.int8)
    for i in range(int(n)):
        for j in range(i):
            x = z * s[i] * s[j]
            p = x / (1.0 + x)
            if rng.random() < p:
                A[i, j] = 1
                A[j, i] = 1

    np.fill_diagonal(A, 0)
    return A.astype(float), s.astype(float)


@pytest.fixture(scope="session")
def synthetic_snapshot() -> Tuple[np.ndarray, np.ndarray, np.ndarray, float, float]:
    """Provide a deterministic synthetic snapshot for all tests."""
    # Without Numba JIT, quadratic kernels can be slow. Reduce the problem size
    # so that the correctness checks remain lightweight in pure-Python mode.
    n = 200 if _numba_is_importable() else 60
    A_bin, strengths = _generate_synthetic_snapshot(n=n)
    k_obs = A_bin.sum(axis=1).astype(float)
    L_obs = 0.5 * float(A_bin.sum())
    S_obs = _two_star_count_from_degrees(k_obs)

    # Sanity checks: non-trivial network and positive correlation.
    assert L_obs > 0.0
    corr = float(np.corrcoef(strengths, k_obs)[0, 1])
    assert corr > 0.6

    return A_bin, strengths, k_obs, float(L_obs), float(S_obs)


def test_dcgm_reproduces_L(synthetic_snapshot):
    """dcGM reproduces the observed link count given strengths."""
    A_bin, strengths, _k_obs, L_obs, _S_obs = synthetic_snapshot

    model = DcGMModel(strengths=strengths, L=float(L_obs))
    res = model.fit(tol=1e-12, max_iter=5000)

    assert hasattr(res, "P")
    P = np.asarray(res.P, dtype=float)
    L_hat = 0.5 * float(P.sum())

    assert _rel_err(L_hat, float(L_obs)) <= TOL_L_REL


def test_ubcm_reproduces_degrees(synthetic_snapshot):
    """UBCM reproduces the degree sequence of the synthetic adjacency."""
    _A_bin, _strengths, k_obs, _L_obs, _S_obs = synthetic_snapshot

    model = UBCMModel(k_obs)
    res = model.fit(max_steps=500, tol=1e-8, eps=1e-10)

    k_hat = np.asarray(res.expected_degrees, dtype=float)
    rel_vec = np.abs(k_hat - k_obs) / np.maximum(1.0, np.abs(k_obs))
    k_rel_err_max = float(np.max(rel_vec))

    assert bool(res.converged)
    assert k_rel_err_max <= TOL_K_REL


def _get_fit2sm_field(res, name: str):
    r"""Retrieve a field from Fit2SM outputs for either dataclass or mapping."""
    if hasattr(res, name):
        return getattr(res, name)
    if isinstance(res, dict) and name in res:
        return res[name]
    raise AttributeError(f"Fit2SM result has no field '{name}'.")


def test_fit2sm_output_is_dataclass(synthetic_snapshot):
    """Fit2SMModel.fit returns a dataclass-style result container."""
    _A_bin, strengths, _k_obs, L_obs, S_obs = synthetic_snapshot

    model = Fit2SMModel(strengths=strengths, L=float(L_obs), S=float(S_obs))
    res = model.fit(outer_max_steps=1, inner_tol=1e-6, inner_max_iter=200, outer_tol=1e-6)

    assert is_dataclass(res)


def test_fit2sm_reproduces_L_and_S_one_outer_step(synthetic_snapshot):
    """Fit2SM reproduces (L,S) for a fixed kappa update (outer_max_steps=1)."""
    _A_bin, strengths, _k_obs, L_obs, S_obs = synthetic_snapshot

    model = Fit2SMModel(strengths=strengths, L=float(L_obs), S=float(S_obs))
    res = model.fit(
        outer_max_steps=1,
        inner_tol=1e-6,
        inner_max_iter=200,
        outer_tol=1e-6,
        use_true_degrees=False,
    )

    L_hat = float(_get_fit2sm_field(res, "L_hat"))
    S_hat = float(_get_fit2sm_field(res, "S_hat"))
    inner_ok = bool(_get_fit2sm_field(res, "inner_converged"))

    assert inner_ok
    assert _rel_err(L_hat, float(L_obs)) <= TOL_L_REL
    assert _rel_err(S_hat, float(S_obs)) <= TOL_S_REL


def test_fit2sm_reproduces_L_and_S_self_consistent(synthetic_snapshot):
    """Fit2SM reproduces (L,S) after several outer iterations (self-consistency)."""
    _A_bin, strengths, _k_obs, L_obs, S_obs = synthetic_snapshot

    model = Fit2SMModel(strengths=strengths, L=float(L_obs), S=float(S_obs))
    res = model.fit(
        outer_max_steps=10,
        inner_tol=1e-6,
        inner_max_iter=200,
        outer_tol=1e-6,
        use_true_degrees=False,
    )

    L_hat = float(_get_fit2sm_field(res, "L_hat"))
    S_hat = float(_get_fit2sm_field(res, "S_hat"))
    inner_ok = bool(_get_fit2sm_field(res, "inner_converged"))

    assert inner_ok
    assert _rel_err(L_hat, float(L_obs)) <= TOL_L_REL
    assert _rel_err(S_hat, float(S_obs)) <= TOL_S_REL


def test_fit2sm_true_degrees_mode(synthetic_snapshot):
    """Fit2SM can be run with imposed degrees (use_true_degrees=True)."""
    _A_bin, strengths, k_obs, L_obs, S_obs = synthetic_snapshot

    model = Fit2SMModel(strengths=strengths, L=float(L_obs), S=float(S_obs))
    res = model.fit(
        outer_max_steps=1,
        inner_tol=1e-6,
        inner_max_iter=200,
        outer_tol=1e-6,
        use_true_degrees=True,
        degrees=k_obs,
    )

    L_hat = float(_get_fit2sm_field(res, "L_hat"))
    S_hat = float(_get_fit2sm_field(res, "S_hat"))
    inner_ok = bool(_get_fit2sm_field(res, "inner_converged"))
    outer_ok = bool(_get_fit2sm_field(res, "outer_converged"))

    assert inner_ok
    assert outer_ok
    assert _rel_err(L_hat, float(L_obs)) <= TOL_L_REL
    assert _rel_err(S_hat, float(S_obs)) <= TOL_S_REL
