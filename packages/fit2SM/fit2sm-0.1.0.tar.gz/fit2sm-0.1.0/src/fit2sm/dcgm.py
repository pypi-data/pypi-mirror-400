# dcgm.py
"""
Degree-corrected gravity model (dcGM) for binary undirected graphs.

Model
-----
For i != j, link probabilities are

    p_ij = (z s_i s_j) / (1 + z s_i s_j),

with scalar parameter z calibrated by matching the expected number of links

    L_hat(z) = sum_{i<j} p_ij = L_target.

Numerical strategy
------------------
- Probabilities are evaluated in log-space via the logistic sigmoid:
      p_ij = sigma(theta + log s_i + log s_j),  with theta = log z.
- z is calibrated by damped Newton iterations on theta with Armijo-type line search
  on the merit function phi(theta) = 0.5*(L_hat(theta) - L_target)^2.

Implementation notes
--------------------
- Numba kernels are strictly numerical: all input validation and error handling
  is performed in Python wrappers to ensure stable nopython compilation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

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
    """
    Logistic sigmoid sigma(t)=1/(1+exp(-t)) evaluated without overflow.

    The piecewise formulation avoids overflow in exp(±t) while preserving
    IEEE-754 behavior in extreme regimes.
    """
    if t >= 0.0:
        e = np.exp(-t)  # underflows to 0 for large positive t
        return 1.0 / (1.0 + e)
    e = np.exp(t)  # underflows to 0 for large negative t
    return e / (1.0 + e)


@jit(nopython=True, cache=True)
def _log_strengths_numba(strengths: np.ndarray) -> np.ndarray:
    """
    Map nonnegative strengths to logarithms, with log(0) = -inf.

    Under the expit evaluation of theta + log s_i + log s_j, a -inf term
    implies p_ij = 0 for any pair involving a zero strength.
    """
    n = strengths.size
    out = np.empty(n, dtype=np.float64)
    for i in range(n):
        si = strengths[i]
        if si > 0.0:
            out[i] = np.log(si)
        else:
            out[i] = -np.inf
    return out


@jit(nopython=True, cache=True)
def _dcgm_Lhat_and_dL_numba(theta: float, log_s: np.ndarray) -> Tuple[float, float]:
    """
    Compute L_hat(theta) and dL_hat/dtheta for dcGM.

    With theta = log z:
        p_ij = sigma(theta + log s_i + log s_j),
        d p_ij / dtheta = p_ij (1 - p_ij).
    """
    n = log_s.size
    L_hat = 0.0
    dL = 0.0
    for i in range(n):
        for j in range(i):
            t = theta + log_s[i] + log_s[j]
            p = _expit_scalar(t)
            L_hat += p
            dL += p * (1.0 - p)
    return L_hat, dL


@jit(nopython=True, cache=True)
def _dcgm_probabilities_from_theta_numba(log_s: np.ndarray, theta: float) -> np.ndarray:
    """
    Construct the symmetric probability matrix P for a given (log_s, theta).

    The diagonal is set to zero to represent a simple graph.
    """
    n = log_s.size
    P = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(i):
            t = theta + log_s[i] + log_s[j]
            p = _expit_scalar(t)
            P[i, j] = p
            P[j, i] = p
    return P


# ---------------------------------------------------------------------
# Public helpers (Python wrappers)
# ---------------------------------------------------------------------
def _validate_strengths(strengths: np.ndarray) -> np.ndarray:
    """Validate and coerce strengths to a 1D float64 array."""
    s = np.asarray(strengths, dtype=np.float64).reshape(-1)
    if s.ndim != 1:
        raise ValueError("strengths must be a one-dimensional array.")
    if np.any(~np.isfinite(s)):
        raise ValueError("strengths must be finite.")
    if np.any(s < 0.0):
        raise ValueError("strengths must be non-negative.")
    return s


def _effective_L_max_from_strengths(strengths: np.ndarray) -> float:
    """
    Maximum achievable expected link count given zero-strength nodes.

    If a node has s_i = 0, then p_ij = 0 for all j at any finite z.
    Therefore, only nodes with s_i > 0 can contribute to links.
    """
    m = int(np.sum(strengths > 0.0))
    return 0.5 * m * (m - 1)


def dcgm_probabilities(strengths: np.ndarray, z: float) -> np.ndarray:
    """
    Return the dcGM probability matrix for an undirected simple graph.

    Parameters
    ----------
    strengths:
        Nonnegative fitness proxies s_i, shape (N,).
    z:
        Nonnegative scalar parameter.

    Notes
    -----
    - Input validation is performed in Python. The numerical kernel is compiled
      in Numba nopython mode.
    """
    s = _validate_strengths(strengths)
    if not np.isfinite(z) or z < 0.0:
        raise ValueError("z must be a finite non-negative scalar.")

    n = int(s.size)
    if n == 0:
        return np.zeros((0, 0), dtype=np.float64)
    if n == 1:
        return np.zeros((1, 1), dtype=np.float64)

    log_s = _log_strengths_numba(s)
    theta = float(np.log(z)) if z > 0.0 else -np.inf
    return _dcgm_probabilities_from_theta_numba(log_s, theta)


def dcgm_expected_links(P: np.ndarray) -> float:
    """
    Return the expected number of undirected links from a symmetric probability matrix.
    """
    P = np.asarray(P, dtype=np.float64)
    if P.ndim != 2 or P.shape[0] != P.shape[1]:
        raise ValueError("P must be a square matrix.")
    return 0.5 * float(P.sum())


def dcgm_calibrate_z(
    strengths: np.ndarray,
    L: Optional[float] = None,
    *,
    L_obs: Optional[float] = None,
    tol: float = 1e-10,
    max_iter: int = 200,
    line_search: bool = True,
) -> float:
    """
    Calibrate z by Newton iterations on theta = log z, matching the expected link count.

    Parameters
    ----------
    strengths:
        Nonnegative strengths s_i.
    L / L_obs:
        Target number of links.
    tol:
        Absolute tolerance on |L_hat - L_target|.
    max_iter:
        Maximum Newton iterations.
    line_search:
        If True, use Armijo backtracking on phi = 0.5*(L_hat - L_target)^2.

    Returns
    -------
    z:
        Calibrated nonnegative scalar parameter.

    Raises
    ------
    ValueError:
        If the target link count is infeasible given strengths (e.g., many zeros).
    RuntimeError:
        If numerical degeneracy is encountered (e.g., derivative collapse).
    """
    if L is None and L_obs is None:
        raise ValueError("Provide either L or L_obs.")
    L_target = float(L_obs if L_obs is not None else L)
    if not np.isfinite(L_target) or L_target < 0.0:
        raise ValueError("L must be a finite non-negative scalar.")

    s = _validate_strengths(strengths)
    n = int(s.size)
    if n < 2:
        if L_target <= tol:
            return 0.0
        raise ValueError("Infeasible L for n<2.")

    # Feasibility under zero strengths
    L_max_eff = _effective_L_max_from_strengths(s)
    if L_target <= tol:
        return 0.0
    if L_target > L_max_eff + tol:
        raise ValueError(
            f"Infeasible L_target={L_target} given strengths: maximum achievable is {L_max_eff} "
            "because nodes with s_i=0 cannot form links."
        )
    if L_target >= L_max_eff - tol:
        # Any sufficiently large z yields p_ij ≈ 1 on the active (s_i>0) subgraph.
        return 1e300

    # Sparse approximation: p_ij ≈ z s_i s_j, hence L ≈ z * sum_{i<j} s_i s_j.
    sum_s = float(s.sum())
    sum_s2 = float((s * s).sum())
    sum_sisj = 0.5 * (sum_s * sum_s - sum_s2)
    if not np.isfinite(sum_sisj) or sum_sisj <= 0.0:
        raise RuntimeError("Sum of strength products is non-positive, dcGM is ill-defined.")

    z0 = max(1e-300, L_target / sum_sisj)
    theta = float(np.log(z0))
    log_s = _log_strengths_numba(s)

    for _ in range(int(max_iter)):
        L_hat, dL = _dcgm_Lhat_and_dL_numba(theta, log_s)
        diff = L_hat - L_target

        if abs(diff) <= tol:
            return float(np.exp(theta))

        if (not np.isfinite(dL)) or dL <= 0.0:
            raise RuntimeError("Non-positive derivative encountered during dcGM calibration.")

        # Newton step on theta.
        step = -diff / dL

        if not line_search:
            theta = float(theta + step)
            continue

        # Armijo-type decrease on phi(theta) = 0.5 * diff^2.
        phi_old = 0.5 * diff * diff
        alpha = 1.0
        c1 = 1e-4

        accepted = False
        for _ls in range(40):
            theta_trial = float(theta + alpha * step)
            L_trial, _ = _dcgm_Lhat_and_dL_numba(theta_trial, log_s)
            diff_trial = L_trial - L_target
            phi_new = 0.5 * diff_trial * diff_trial
            if phi_new <= phi_old * (1.0 - c1 * alpha):
                theta = theta_trial
                accepted = True
                break
            alpha *= 0.5

        if not accepted:
            # As a last resort, accept a small damped step.
            theta = float(theta + 1e-3 * step)

    return float(np.exp(theta))


# ---------------------------------------------------------------------
# Model container
# ---------------------------------------------------------------------
@dataclass(frozen=True)
class DcGMResult:
    """Container for dcGM calibration outputs."""
    z: float
    P: np.ndarray
    expected_degrees: np.ndarray
    L_target: float
    L_hat: float
    abs_error_L: float


class DcGMModel:
    """
    Degree-corrected gravity model (dcGM) calibrated from strengths and link count.

    After calling fit(), the probability matrix is cached and can be retrieved
    via probabilities().
    """

    def __init__(self, strengths: np.ndarray, L: float) -> None:
        self.strengths = _validate_strengths(strengths)
        self.L_target = float(L)
        if (not np.isfinite(self.L_target)) or self.L_target < 0.0:
            raise ValueError("L must be a finite non-negative scalar.")
        self._result: Optional[DcGMResult] = None

    def fit(self, tol: float = 1e-10, max_iter: int = 200) -> DcGMResult:
        """Calibrate z and cache the fitted probability matrix."""
        z = dcgm_calibrate_z(self.strengths, L=self.L_target, tol=tol, max_iter=max_iter)
        P = dcgm_probabilities(self.strengths, z)
        k_hat = P.sum(axis=1).astype(np.float64)
        L_hat = dcgm_expected_links(P)
        res = DcGMResult(
            z=float(z),
            P=P,
            expected_degrees=k_hat,
            L_target=float(self.L_target),
            L_hat=float(L_hat),
            abs_error_L=float(abs(L_hat - self.L_target)),
        )
        self._result = res
        return res

    def probabilities(self) -> np.ndarray:
        """Return the calibrated probability matrix."""
        if self._result is None:
            raise RuntimeError("Model is not calibrated. Call fit() first.")
        return self._result.P