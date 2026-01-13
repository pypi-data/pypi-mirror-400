# ubcm.py
"""
Undirected Binary Configuration Model (UBCM) calibrated by Newton iterations.

Model
-----
For i != j:

    p_ij = (x_i x_j) / (1 + x_i x_j) = sigma(eta_i + eta_j),

where x_i > 0 are Lagrange multipliers and eta_i = log x_i are the
optimization variables.

Calibration
-----------
The parameters are obtained by solving the degree-matching constraints:

    k_hat_i(eta) = sum_{j != i} p_ij(eta) = k_i,    for all i.

This implementation
-------------------
- uses stable evaluation of sigma(t) without clipping,
- uses an analytic Jacobian of the constraint map eta -> k_hat(eta),
- performs damped Newton iterations with diagonal (Levenberg-type) regularization,
- applies Armijo backtracking on the merit function phi(eta)=0.5*||k_hat-k||^2.

Feasibility checks
------------------
Before starting the solver, the target degrees are checked for basic feasibility:
    0 <= k_i <= n-1,
    sum_i k_i <= n(n-1).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Callable

import numpy as np

# Numba is an optional accelerator. When it cannot be imported (e.g., due to
# platform-specific build constraints or third-party instrumentation packages),
# the code falls back to a pure-Python execution path.
try:  # pragma: no cover
    from numba import jit  # type: ignore
except Exception:  # pragma: no cover
    def jit(*_args, **_kwargs):  # type: ignore
        """Return an identity decorator when Numba is unavailable."""

        def _decorator(func):
            return func

        return _decorator


# ---------------------------------------------------------------------
# Low-level numerics (Numba)
# ---------------------------------------------------------------------
@jit(nopython=True, cache=True)
def _expit_scalar(t: float) -> float:
    """Logistic sigmoid evaluated without overflow."""
    if t >= 0.0:
        e = np.exp(-t)
        return 1.0 / (1.0 + e)
    e = np.exp(t)
    return e / (1.0 + e)


@jit(nopython=True, cache=True)
def _expected_degrees_from_eta_numba(eta: np.ndarray) -> np.ndarray:
    """Compute expected degrees k_hat under the UBCM for variables eta=log x."""
    n = eta.size
    k_hat = np.zeros(n, dtype=np.float64)
    for i in range(n):
        for j in range(i):
            p = _expit_scalar(eta[i] + eta[j])
            k_hat[i] += p
            k_hat[j] += p
    return k_hat


@jit(nopython=True, cache=True)
def _jacobian_from_eta_numba(eta: np.ndarray) -> np.ndarray:
    """
    Jacobian J_{ij} = d k_hat_i / d eta_j.

    For i != j:
        d p_ij / d eta_j = p_ij(1-p_ij) = w_ij,
    hence:
        J_{ij} = w_ij  (i != j),
        J_{ii} = sum_{j != i} w_ij.
    """
    n = eta.size
    J = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(i):
            p = _expit_scalar(eta[i] + eta[j])
            w = p * (1.0 - p)
            J[i, i] += w
            J[j, j] += w
            J[i, j] += w
            J[j, i] += w
    return J


@jit(nopython=True, cache=True)
def _prob_matrix_from_eta_numba(eta: np.ndarray) -> np.ndarray:
    """Construct the symmetric probability matrix P from eta=log x (diagonal set to zero)."""
    n = eta.size
    P = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(i):
            p = _expit_scalar(eta[i] + eta[j])
            P[i, j] = p
            P[j, i] = p
    return P


def _expected_degrees_from_eta(eta: np.ndarray) -> np.ndarray:
    return _expected_degrees_from_eta_numba(np.asarray(eta, dtype=np.float64))


def _jacobian(eta: np.ndarray) -> np.ndarray:
    return _jacobian_from_eta_numba(np.asarray(eta, dtype=np.float64))


def _prob_matrix_from_eta(eta: np.ndarray) -> np.ndarray:
    return _prob_matrix_from_eta_numba(np.asarray(eta, dtype=np.float64))


# ---------------------------------------------------------------------
# Newton solver
# ---------------------------------------------------------------------
@dataclass(frozen=True)
class NewtonResult:
    """Container for Newton solver diagnostics."""
    x: np.ndarray
    n_steps: int
    converged: bool
    last_phi: float


def _newton_solve(
    x0: np.ndarray,
    fun: Callable[[np.ndarray], np.ndarray],
    jac: Callable[[np.ndarray], np.ndarray],
    step_fun: Callable[[np.ndarray], float],
    *,
    tol: float = 1e-10,
    eps: float = 1e-12,
    max_steps: int = 2000,
    regularise: bool = True,
    regularise_eps: float = 1e-8,
    line_search: bool = True,
) -> NewtonResult:
    """
    Solve fun(x)=0 by damped Newton iterations with Armijo backtracking.

    The Jacobian is regularized by adding a diagonal shift (Levenberg-type),
    which stabilizes the linear solve in ill-conditioned regimes.
    """
    x = np.asarray(x0, dtype=np.float64).copy()
    phi = float(step_fun(x))

    for it in range(int(max_steps)):
        r = np.asarray(fun(x), dtype=np.float64)
        if float(np.linalg.norm(r)) <= tol:
            return NewtonResult(x=x, n_steps=it, converged=True, last_phi=float(step_fun(x)))

        J = np.asarray(jac(x), dtype=np.float64)

        if regularise:
            lam = float(regularise_eps * max(1.0, np.max(np.abs(r))))
            J = J + lam * np.eye(J.shape[0], dtype=np.float64)

        # Newton direction: J p = -r.
        try:
            p = np.linalg.solve(J, -r)
        except np.linalg.LinAlgError:
            p, *_ = np.linalg.lstsq(J, -r, rcond=None)

        if float(np.linalg.norm(p)) <= eps:
            return NewtonResult(x=x, n_steps=it, converged=True, last_phi=float(step_fun(x)))

        if not line_search:
            x = x + p
            phi = float(step_fun(x))
            continue

        phi_old = float(phi)
        alpha = 1.0
        c1 = 1e-4

        accepted = False
        for _ls in range(40):
            x_trial = x + alpha * p
            phi_new = float(step_fun(x_trial))
            if phi_new <= phi_old * (1.0 - c1 * alpha):
                x = x_trial
                phi = phi_new
                accepted = True
                break
            alpha *= 0.5

        if not accepted:
            x = x + 1e-3 * p
            phi = float(step_fun(x))

    return NewtonResult(x=x, n_steps=int(max_steps), converged=False, last_phi=float(step_fun(x)))


# ---------------------------------------------------------------------
# Model container
# ---------------------------------------------------------------------
@dataclass(frozen=True)
class UBCMResult:
    """Container for UBCM calibration outputs."""
    eta: np.ndarray
    x: np.ndarray
    expected_degrees: np.ndarray
    max_abs_error: float
    n_steps: int
    converged: bool


class UBCMModel:
    """Undirected Binary Configuration Model (UBCM)."""

    def __init__(self, degrees: np.ndarray) -> None:
        k = np.asarray(degrees, dtype=np.float64).reshape(-1)
        if k.ndim != 1:
            raise ValueError("degrees must be a one-dimensional array.")
        if np.any(~np.isfinite(k)):
            raise ValueError("degrees must be finite.")
        if np.any(k < 0.0):
            raise ValueError("degrees must be non-negative.")

        self.degrees = k
        self.n_nodes = int(k.size)

        # Internal fitted state
        self.eta_: Optional[np.ndarray] = None

        # Basic feasibility checks for a simple undirected graph.
        n = self.n_nodes
        if n < 2:
            if float(np.max(k)) > 0.0:
                raise ValueError("Infeasible degrees for n<2.")
            return
        if float(np.max(k)) > (n - 1) + 1e-12:
            raise ValueError("Infeasible degrees: some k_i exceeds n-1.")
        if float(k.sum()) > n * (n - 1) + 1e-9:
            raise ValueError("Infeasible degrees: sum(k) exceeds n(n-1).")

    def fit(
        self,
        max_steps: int = 2000,
        tol: float = 1e-10,
        eps: float = 1e-12,
        regularise_eps: float = 1e-8,
    ) -> UBCMResult:
        """
        Calibrate UBCM multipliers to match the target degrees.

        Initialization uses a Chung–Lu approximation:
            x_i ≈ k_i / sqrt(2L), with L = sum_i k_i / 2.
        """
        k = self.degrees
        n = self.n_nodes

        if n < 2:
            eta = np.zeros(n, dtype=np.float64)
            self.eta_ = eta
            return UBCMResult(
                eta=eta,
                x=np.ones(n, dtype=np.float64),
                expected_degrees=np.zeros(n, dtype=np.float64),
                max_abs_error=float(np.max(np.abs(k))) if n > 0 else 0.0,
                n_steps=0,
                converged=True,
            )

        L = float(k.sum()) / 2.0
        L = max(L, 1.0)

        x0 = k / np.sqrt(2.0 * L)
        x0 = np.maximum(x0, 1e-300)  # ensures finite eta0
        eta0 = np.log(x0)

        def fun(eta: np.ndarray) -> np.ndarray:
            return _expected_degrees_from_eta(eta) - k

        def jac(eta: np.ndarray) -> np.ndarray:
            return _jacobian(eta)

        def step_fun(eta: np.ndarray) -> float:
            r = fun(eta)
            return 0.5 * float(r @ r)

        res = _newton_solve(
            x0=eta0,
            fun=fun,
            jac=jac,
            step_fun=step_fun,
            tol=tol,
            eps=eps,
            max_steps=max_steps,
            regularise=True,
            regularise_eps=regularise_eps,
            line_search=True,
        )

        eta = np.asarray(res.x, dtype=np.float64)
        x = np.exp(eta)
        k_hat = _expected_degrees_from_eta(eta)
        max_abs = float(np.max(np.abs(k_hat - k)))

        self.eta_ = eta

        return UBCMResult(
            eta=eta,
            x=x,
            expected_degrees=k_hat,
            max_abs_error=max_abs,
            n_steps=int(res.n_steps),
            converged=bool(res.converged),
        )

    def probabilities(self) -> np.ndarray:
        """Return the calibrated UBCM probability matrix."""
        if self.eta_ is None:
            raise RuntimeError("Model is not calibrated. Call fit() first.")
        return _prob_matrix_from_eta(self.eta_)