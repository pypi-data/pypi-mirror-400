# fit2sm.py
"""
Fitness-based Two-Star Model (Fit2SM) mean-field solver for undirected
binary networks.

Model
-----
For i != j, link probabilities are independent conditional on mean-field
degrees kappa = (kappa_i):

    p_ij = x_ij / (1 + x_ij).

A numerically stable parametrization is obtained in log-form:

    log x_ij = log z + log s_i + log s_j + (kappa_i + kappa_j) log y.

This expression is algebraically equivalent to the mean-shift factorization
based on (kappa_prime, y_tilde), because
(kappa_i + kappa_j) log y = (kappa'_i + kappa'_j) log y_tilde when
log y_tilde = kappa_mean log y and kappa'_i = kappa_i / kappa_mean.

Constraints
-----------
The two parameters (z, y) are fitted to match:

    L_hat = sum_{i<j} p_ij,
    S_hat = sum_i C(k_i, 2),   with k_i = sum_{j != i} p_ij.

Mean-field self-consistency
---------------------------
The hidden degrees kappa are solved by a fixed point iteration:

    kappa <- k,

where k is the degree expectation implied by the current probabilities.
This is performed in an outer loop. Inside each outer iteration, an inner
damped Newton method calibrates (log z, log y) to match (L, S) for the
current kappa.

Implementation notes
--------------------
The dominant operations are O(N^2) and are executed by Numba kernels in
nopython mode with caching enabled. The public API and return objects
remain fully compatible with the previous implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterator, Optional, Tuple

import math
import numpy as np
from numba import njit


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def _coerce_targets(
    L: Optional[float] = None,
    S: Optional[float] = None,
    L_obs: Optional[float] = None,
    S_obs: Optional[float] = None,
    L_target: Optional[float] = None,
    S_target: Optional[float] = None,
    Ltot: Optional[float] = None,
    Stot: Optional[float] = None,
    **_: Any,
) -> Tuple[Optional[float], Optional[float]]:
    """Normalize multiple aliases for constraint targets into (L, S)."""
    L_candidates = (L, L_obs, L_target, Ltot)
    S_candidates = (S, S_obs, S_target, Stot)
    L_val = next((float(x) for x in L_candidates if x is not None), None)
    S_val = next((float(x) for x in S_candidates if x is not None), None)
    return L_val, S_val


def _rel_err(a: float, b: float) -> float:
    """Scale-robust relative error |a-b| / max(1, |b|)."""
    return float(abs(a - b) / max(1.0, abs(b)))


def _validate_strengths(strengths: np.ndarray, eps: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    Validate strengths and return (s, log_s) where log_s uses eps for zeros.

    The log-transform is used as a stable parametrization of x_ij. Zeros are
    mapped to log(eps) to avoid -inf in expressions. The kernels additionally
    enforce p_ij=0 whenever s_i=0 or s_j=0, in agreement with feasibility checks.
    """
    s = np.asarray(strengths, dtype=np.float64).reshape(-1)
    if s.ndim != 1:
        raise ValueError("strengths must be a one-dimensional array.")
    if np.any(~np.isfinite(s)):
        raise ValueError("strengths must be finite.")
    if np.any(s < 0.0):
        raise ValueError("strengths must be non-negative.")
    s_clip = np.where(s > 0.0, s, float(eps)).astype(np.float64)
    log_s = np.log(s_clip).astype(np.float64)
    return s, log_s


def _effective_L_max_from_strengths(strengths: np.ndarray) -> float:
    """
    Maximum achievable link count given zero strengths.

    If s_i=0, then p_ij=0 for any j regardless of (z,y). Therefore, only nodes
    with positive strengths can form links.
    """
    m = int(np.sum(np.asarray(strengths) > 0.0))
    return 0.5 * m * (m - 1)


def _effective_S_max_from_strengths(strengths: np.ndarray) -> float:
    """
    Upper bound on the two-star count given zero strengths.

    The largest S occurs when the active subgraph (nodes with s_i>0) forms a clique.
    In that case, each active node has degree m-1, yielding:
        S_max = sum_i C(k_i,2) = m * C(m-1,2).
    """
    m = int(np.sum(np.asarray(strengths) > 0.0))
    if m < 3:
        return 0.0
    return float(m * 0.5 * (m - 1) * (m - 2))


def _validate_targets(L_target: float, S_target: float, strengths: np.ndarray) -> None:
    """Apply basic feasibility checks for L and S given strengths."""
    if (not np.isfinite(L_target)) or L_target < 0.0:
        raise ValueError("L_target must be finite and non-negative.")
    if (not np.isfinite(S_target)) or S_target < 0.0:
        raise ValueError("S_target must be finite and non-negative.")

    L_max_eff = _effective_L_max_from_strengths(strengths)
    if L_target > L_max_eff + 1e-9:
        raise ValueError(
            f"Infeasible L_target={L_target}: maximum achievable is {L_max_eff} "
            "because nodes with s_i=0 cannot form links."
        )

    S_max_eff = _effective_S_max_from_strengths(strengths)
    if S_target > S_max_eff + 1e-6:
        raise ValueError(
            f"Infeasible S_target={S_target}: an upper bound given strengths is {S_max_eff}."
        )


# ---------------------------------------------------------------------
# Numba kernels (O(N^2) statistics, Jacobian, and optional probability matrix)
# ---------------------------------------------------------------------
@njit(cache=True)
def _sigmoid_scalar(x: float) -> float:
    """Numerically stable logistic function for scalar inputs."""
    if x >= 0.0:
        return 1.0 / (1.0 + math.exp(-x))
    ex = math.exp(x)
    return ex / (1.0 + ex)


@njit(cache=True)
def _fit2sm_L_hat_only(
    logz: float,
    logy: float,
    s: np.ndarray,
    log_s: np.ndarray,
    kappa: np.ndarray,
) -> float:
    """
    Compute L_hat = sum_{i<j} p_ij for fixed (logz, logy, kappa).

    The kernel enforces p_ij=0 for any pair involving a node with s_i=0.
    """
    n = s.size
    L_hat = 0.0
    for i in range(n - 1):
        if s[i] <= 0.0:
            continue
        li = log_s[i]
        ki = kappa[i]
        for j in range(i + 1, n):
            if s[j] <= 0.0:
                continue
            logx = logz + li + log_s[j] + (ki + kappa[j]) * logy
            L_hat += _sigmoid_scalar(logx)
    return L_hat


@njit(cache=True)
def _fit2sm_stats_jacobian(
    logz: float,
    logy: float,
    s: np.ndarray,
    log_s: np.ndarray,
    kappa: np.ndarray,
) -> Tuple[float, float, np.ndarray, np.ndarray]:
    """
    Compute (L_hat, S_hat, k_hat, J) for fixed (logz, logy, kappa).

    The Jacobian is with respect to (logz, logy). The diagonal of P is
    implicitly zero and is excluded by construction.
    """
    n = s.size
    k_hat = np.zeros(n, dtype=np.float64)
    dk_dlogz = np.zeros(n, dtype=np.float64)
    dk_dlogy = np.zeros(n, dtype=np.float64)

    L_hat = 0.0
    dL_dlogz = 0.0
    dL_dlogy = 0.0

    for i in range(n - 1):
        if s[i] <= 0.0:
            continue
        li = log_s[i]
        ki = kappa[i]
        for j in range(i + 1, n):
            if s[j] <= 0.0:
                continue
            kij = ki + kappa[j]
            logx = logz + li + log_s[j] + kij * logy

            p = _sigmoid_scalar(logx)
            L_hat += p
            k_hat[i] += p
            k_hat[j] += p

            t = p * (1.0 - p)
            dL_dlogz += t
            dk_dlogz[i] += t
            dk_dlogz[j] += t

            dp_dlogy = t * kij
            dL_dlogy += dp_dlogy
            dk_dlogy[i] += dp_dlogy
            dk_dlogy[j] += dp_dlogy

    S_hat = 0.0
    dS_dlogz = 0.0
    dS_dlogy = 0.0
    for i in range(n):
        ki_hat = k_hat[i]
        S_hat += 0.5 * ki_hat * (ki_hat - 1.0)
        factor = 2.0 * ki_hat - 1.0
        dS_dlogz += 0.5 * factor * dk_dlogz[i]
        dS_dlogy += 0.5 * factor * dk_dlogy[i]

    J = np.empty((2, 2), dtype=np.float64)
    J[0, 0] = dL_dlogz
    J[0, 1] = dL_dlogy
    J[1, 0] = dS_dlogz
    J[1, 1] = dS_dlogy

    return L_hat, S_hat, k_hat, J


@njit(cache=True)
def _fit2sm_stats_jacobian_withP(
    logz: float,
    logy: float,
    s: np.ndarray,
    log_s: np.ndarray,
    kappa: np.ndarray,
) -> Tuple[float, float, np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute (L_hat, S_hat, k_hat, J, P) for fixed (logz, logy, kappa).

    The probability matrix P is symmetric, with a zero diagonal.
    """
    n = s.size
    P = np.zeros((n, n), dtype=np.float64)
    k_hat = np.zeros(n, dtype=np.float64)
    dk_dlogz = np.zeros(n, dtype=np.float64)
    dk_dlogy = np.zeros(n, dtype=np.float64)

    L_hat = 0.0
    dL_dlogz = 0.0
    dL_dlogy = 0.0

    for i in range(n - 1):
        if s[i] <= 0.0:
            continue
        li = log_s[i]
        ki = kappa[i]
        for j in range(i + 1, n):
            if s[j] <= 0.0:
                continue
            kij = ki + kappa[j]
            logx = logz + li + log_s[j] + kij * logy

            p = _sigmoid_scalar(logx)
            P[i, j] = p
            P[j, i] = p

            L_hat += p
            k_hat[i] += p
            k_hat[j] += p

            t = p * (1.0 - p)
            dL_dlogz += t
            dk_dlogz[i] += t
            dk_dlogz[j] += t

            dp_dlogy = t * kij
            dL_dlogy += dp_dlogy
            dk_dlogy[i] += dp_dlogy
            dk_dlogy[j] += dp_dlogy

    S_hat = 0.0
    dS_dlogz = 0.0
    dS_dlogy = 0.0
    for i in range(n):
        ki_hat = k_hat[i]
        S_hat += 0.5 * ki_hat * (ki_hat - 1.0)
        factor = 2.0 * ki_hat - 1.0
        dS_dlogz += 0.5 * factor * dk_dlogz[i]
        dS_dlogy += 0.5 * factor * dk_dlogy[i]

    J = np.empty((2, 2), dtype=np.float64)
    J[0, 0] = dL_dlogz
    J[0, 1] = dL_dlogy
    J[1, 0] = dS_dlogz
    J[1, 1] = dS_dlogy

    return L_hat, S_hat, k_hat, J, P


# ---------------------------------------------------------------------
# Diagnostics container
# ---------------------------------------------------------------------
@dataclass(frozen=True)
class Fit2SMDiagnostics:
    """Container for solver diagnostics."""
    inner_converged: bool
    outer_converged: bool
    inner_n_iter: int
    outer_n_iter: int
    message: str


# ---------------------------------------------------------------------
# Result container (dataclass, dcgm/ubcm-style)
# ---------------------------------------------------------------------
@dataclass(frozen=True)
class Fit2SMResult:
    """
    Container for Fit2SM calibration outputs.

    Notes
    -----
    This object supports both attribute access (res.L_hat) and legacy dict-like
    access (res["L_hat"]) to avoid breaking downstream notebooks.
    """
    # Core parameters
    z: float
    y: float
    logz: float
    logy: float

    # Targets and fitted moments
    L_target: float
    S_target: float
    L_hat: float
    S_hat: float

    # Mean-field degrees
    kappa: np.ndarray
    k_hat: np.ndarray
    kappa_mean: float
    kappa_prime: np.ndarray

    # Scale parameterization
    y_tilde: float
    log_y_tilde: float

    # Diagnostics
    inner_converged: bool
    outer_converged: bool
    inner_n_iter: int
    outer_n_iter: int
    message: str

    # Errors
    L_rel_err: float
    S_rel_err: float
    L_abs_err: float
    S_abs_err: float

    # Optional probability matrix
    P: Optional[np.ndarray] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the result to a plain dictionary (legacy-friendly)."""
        return {
            "z": float(self.z),
            "y": float(self.y),
            "logz": float(self.logz),
            "logy": float(self.logy),
            "L_target": float(self.L_target),
            "S_target": float(self.S_target),
            "L_hat": float(self.L_hat),
            "S_hat": float(self.S_hat),
            "kappa": np.asarray(self.kappa, dtype=float),
            "k_hat": np.asarray(self.k_hat, dtype=float),
            "kappa_mean": float(self.kappa_mean),
            "kappa_prime": np.asarray(self.kappa_prime, dtype=float),
            "y_tilde": float(self.y_tilde),
            "log_y_tilde": float(self.log_y_tilde),
            "inner_converged": bool(self.inner_converged),
            "outer_converged": bool(self.outer_converged),
            "inner_n_iter": int(self.inner_n_iter),
            "outer_n_iter": int(self.outer_n_iter),
            "message": str(self.message),
            "L_rel_err": float(self.L_rel_err),
            "S_rel_err": float(self.S_rel_err),
            "L_abs_err": float(self.L_abs_err),
            "S_abs_err": float(self.S_abs_err),
            "P": None if self.P is None else np.asarray(self.P, dtype=float),
        }

    def __getitem__(self, key: str) -> Any:
        """Provide legacy dict-style indexing (e.g., res['L_hat'])."""
        d = self.to_dict()
        return d[key]

    def get(self, key: str, default: Any = None) -> Any:
        """Provide dict-like get method."""
        d = self.to_dict()
        return d.get(key, default)

    def keys(self) -> Iterator[str]:
        """Iterate over legacy dictionary keys."""
        return iter(self.to_dict().keys())

    def items(self) -> Iterator[Tuple[str, Any]]:
        """Iterate over legacy dictionary items."""
        return iter(self.to_dict().items())


# ---------------------------------------------------------------------
# Main model
# ---------------------------------------------------------------------
class Fit2SMModel:
    """
    Fit2SM mean-field solver.

    Parameters
    ----------
    strengths:
        Nonnegative fitness proxies s_i, shape (N,).
    L, S and aliases:
        Targets for number of links and two-stars.
    eps:
        Small positive constant used in log-transform to avoid log(0) in dense algebra.
    """

    def __init__(
        self,
        strengths: np.ndarray,
        L: Optional[float] = None,
        S: Optional[float] = None,
        L_obs: Optional[float] = None,
        S_obs: Optional[float] = None,
        L_target: Optional[float] = None,
        S_target: Optional[float] = None,
        Ltot: Optional[float] = None,
        Stot: Optional[float] = None,
        eps: float = 1e-15,
        **_: Any,
    ) -> None:
        self.eps = float(eps)
        s, log_s = _validate_strengths(strengths, eps=self.eps)
        self.s = np.ascontiguousarray(s, dtype=np.float64)
        self.log_s = np.ascontiguousarray(log_s, dtype=np.float64)
        self.n = int(self.s.size)

        L_val, S_val = _coerce_targets(
            L=L, S=S, L_obs=L_obs, S_obs=S_obs, L_target=L_target, S_target=S_target, Ltot=Ltot, Stot=Stot
        )
        self.L_target = L_val
        self.S_target = S_val

        self._result: Optional[Fit2SMResult] = None

    # -----------------------------------------------------------------
    # Core statistics for fixed kappa (Numba-backed)
    # -----------------------------------------------------------------
    def _stats_and_jacobian(
        self,
        logz: float,
        logy: float,
        kappa: np.ndarray,
        return_P: bool = False,
    ) -> Tuple[float, float, np.ndarray, np.ndarray, Optional[np.ndarray], Dict[str, float]]:
        """
        Compute (L_hat, S_hat), implied degrees k_hat, and Jacobian wrt (logz, logy)
        for fixed mean-field degrees kappa.
        """
        kappa_arr = np.ascontiguousarray(np.asarray(kappa, dtype=np.float64).reshape(-1))
        if kappa_arr.size != self.n:
            raise ValueError("kappa has inconsistent size.")

        if return_P:
            L_hat, S_hat, k_hat, J, P = _fit2sm_stats_jacobian_withP(
                float(logz), float(logy), self.s, self.log_s, kappa_arr
            )
        else:
            L_hat, S_hat, k_hat, J = _fit2sm_stats_jacobian(
                float(logz), float(logy), self.s, self.log_s, kappa_arr
            )
            P = None

        kappa_mean = float(np.mean(kappa_arr)) if kappa_arr.size > 0 else 0.0
        log_y_tilde = float(kappa_mean * float(logy)) if kappa_mean > 0.0 else 0.0
        extras = {"kappa_mean": float(kappa_mean), "log_y_tilde": float(log_y_tilde)}

        return float(L_hat), float(S_hat), np.asarray(k_hat, dtype=float), np.asarray(J, dtype=float), P, extras

    # -----------------------------------------------------------------
    # Monotone bisection for logz at fixed (logy, kappa)
    # -----------------------------------------------------------------
    def _bisect_logz_for_L(
        self,
        L_target: float,
        logy: float,
        kappa: np.ndarray,
        bracket: Tuple[float, float] = (-50.0, 50.0),
        max_expand: int = 30,
        max_iter: int = 80,
    ) -> float:
        """
        Find logz such that L_hat(logz, logy; kappa) = L_target by monotone bisection.

        The function L_hat(logz) is monotone increasing for fixed (logy, kappa).
        """
        lo, hi = float(bracket[0]), float(bracket[1])
        kappa_arr = np.ascontiguousarray(np.asarray(kappa, dtype=np.float64).reshape(-1))
        if kappa_arr.size != self.n:
            raise ValueError("kappa has inconsistent size.")

        def L_of(x: float) -> float:
            return float(_fit2sm_L_hat_only(float(x), float(logy), self.s, self.log_s, kappa_arr))

        L_lo = L_of(lo)
        L_hi = L_of(hi)

        # Expand bracket until L_target is covered.
        for _ in range(int(max_expand)):
            if L_lo <= L_target <= L_hi:
                break
            if L_target < L_lo:
                hi = lo
                lo -= 10.0
                L_lo = L_of(lo)
            else:
                lo = hi
                hi += 10.0
                L_hi = L_of(hi)

        for _ in range(int(max_iter)):
            mid = 0.5 * (lo + hi)
            if L_of(mid) < L_target:
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi)

    # -----------------------------------------------------------------
    # Inner solver: damped Newton on (logz, logy) for fixed kappa
    # -----------------------------------------------------------------
    def _inner_newton(
        self,
        L_target: float,
        S_target: float,
        kappa: np.ndarray,
        inner_tol: float,
        inner_max_iter: int,
        logy_bounds: Tuple[float, float],
        jac_reg: float,
        line_search: bool,
        init_logy: float,
        init_logz: Optional[float],
        verbose: bool,
        return_P: bool,
    ) -> Tuple[float, float, float, float, np.ndarray, Optional[np.ndarray], Fit2SMDiagnostics, Dict[str, float]]:
        """
        Solve for (logz, logy) given kappa by matching (L, S) with a damped Newton method.
        """
        logy = float(np.clip(float(init_logy), float(logy_bounds[0]), float(logy_bounds[1])))
        logz = (
            self._bisect_logz_for_L(L_target=float(L_target), logy=logy, kappa=kappa)
            if init_logz is None
            else float(init_logz)
        )

        def merit(r: np.ndarray) -> float:
            """Quadratic merit function used for line search acceptance."""
            return float(0.5 * np.dot(r, r))

        inner_converged = False
        P_out: Optional[np.ndarray] = None
        extras_last: Dict[str, float] = {}

        msg = "Inner Newton: maximum iterations reached."
        it = 0

        for it in range(1, int(inner_max_iter) + 1):
            L_hat, S_hat, k_hat, J, P, extras = self._stats_and_jacobian(
                logz=logz, logy=logy, kappa=kappa, return_P=return_P
            )
            extras_last = extras

            relL = _rel_err(L_hat, float(L_target))
            relS = _rel_err(S_hat, float(S_target))

            if verbose:
                y_val = float(np.exp(logy))
                print(
                    f"[Fit2SM inner] it={it:3d}  logz={logz:+.4e}  logy={logy:+.4e}  y={y_val:.6e}  "
                    f"L_hat={L_hat:.6e}  S_hat={S_hat:.6e}  relL={relL:.3e}  relS={relS:.3e}"
                )

            if (relL <= float(inner_tol)) and (relS <= float(inner_tol)):
                inner_converged = True
                msg = "Inner Newton converged within tolerance."
                if return_P:
                    P_out = P
                break

            r = np.array([L_hat - float(L_target), S_hat - float(S_target)], dtype=float)
            J_reg = np.asarray(J, dtype=float) + float(jac_reg) * np.eye(2, dtype=float)

            try:
                step = np.linalg.solve(J_reg, -r)
            except np.linalg.LinAlgError:
                # Gradient step fallback for singular Jacobian.
                g = J_reg.T @ r
                gnorm = float(np.linalg.norm(g))
                if gnorm == 0.0:
                    msg = "Inner Newton: singular Jacobian and zero gradient."
                    break
                step = -g / gnorm

            t = 1.0
            old_merit = merit(r)
            accepted = False

            if line_search:
                for _ls in range(40):
                    logz_new = logz + t * float(step[0])
                    logy_new = float(np.clip(logy + t * float(step[1]), float(logy_bounds[0]), float(logy_bounds[1])))

                    L_new, S_new, _, _, _, _ = self._stats_and_jacobian(
                        logz=logz_new, logy=logy_new, kappa=kappa, return_P=False
                    )
                    r_new = np.array([L_new - float(L_target), S_new - float(S_target)], dtype=float)

                    if merit(r_new) <= old_merit * (1.0 - 1e-4 * t):
                        logz, logy = logz_new, logy_new
                        accepted = True
                        break
                    t *= 0.5
            else:
                logz = logz + float(step[0])
                logy = float(np.clip(logy + float(step[1]), float(logy_bounds[0]), float(logy_bounds[1])))
                accepted = True

            if not accepted:
                msg = "Inner Newton: line search failed."
                break

        # Final evaluation for consistent outputs.
        L_hat, S_hat, k_hat, _, P, extras = self._stats_and_jacobian(
            logz=logz, logy=logy, kappa=kappa, return_P=return_P
        )
        extras_last = extras
        if return_P:
            P_out = P

        diag = Fit2SMDiagnostics(
            inner_converged=bool(inner_converged),
            outer_converged=False,
            inner_n_iter=int(it),
            outer_n_iter=0,
            message=msg,
        )
        return (
            float(logz),
            float(logy),
            float(L_hat),
            float(S_hat),
            np.asarray(k_hat, dtype=float),
            P_out,
            diag,
            extras_last,
        )

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------
    def fit(
        self,
        # Targets (override __init__ if provided)
        L: Optional[float] = None,
        S: Optional[float] = None,
        L_obs: Optional[float] = None,
        S_obs: Optional[float] = None,
        L_target: Optional[float] = None,
        S_target: Optional[float] = None,
        Ltot: Optional[float] = None,
        Stot: Optional[float] = None,
        # Legacy args
        inner_tol: float = 1e-10,
        inner_max_iter: int = 50,
        outer_max_steps: int = 1,
        outer_tol: float = 1e-6,
        use_true_degrees: bool = False,
        degrees: Optional[np.ndarray] = None,
        # Solver controls
        jac_reg: float = 1e-10,
        line_search: bool = True,
        verbose: bool = False,
        # Initialization
        init_y: float = 1.0,
        init_z: Optional[float] = None,
        logy_bounds: Tuple[float, float] = (-20.0, 20.0),
        # Outputs
        return_P: bool = False,
        **_: Any,
    ) -> Fit2SMResult:
        """
        Fit the Fit2SM parameters and return a Fit2SMResult dataclass.

        Notes
        -----
        - outer_max_steps controls the self-consistency iterations on kappa.
        - If use_true_degrees=True, the outer fixed point is bypassed and kappa is fixed.
        """
        L_val, S_val = _coerce_targets(
            L=L, S=S, L_obs=L_obs, S_obs=S_obs, L_target=L_target, S_target=S_target, Ltot=Ltot, Stot=Stot
        )
        if L_val is None:
            if self.L_target is None:
                raise ValueError("Missing L target. Provide it in __init__ or fit().")
            L_val = float(self.L_target)
        if S_val is None:
            if self.S_target is None:
                raise ValueError("Missing S target. Provide it in __init__ or fit().")
            S_val = float(self.S_target)

        _validate_targets(float(L_val), float(S_val), self.s)

        # Initialize kappa.
        if use_true_degrees:
            if degrees is None:
                raise ValueError("use_true_degrees=True requires degrees=... to be provided.")
            kappa = np.asarray(degrees, dtype=np.float64).reshape(-1)
            if kappa.size != self.n:
                raise ValueError("degrees has inconsistent size.")
        else:
            # Initialization based on the dcGM limit (logy=0, kappa=0).
            kappa0 = np.zeros(self.n, dtype=np.float64)
            logy0 = 0.0
            if init_z is None:
                logz0 = self._bisect_logz_for_L(L_target=float(L_val), logy=logy0, kappa=kappa0)
            else:
                init_z_val = float(init_z)
                if init_z_val <= 0.0 or (not np.isfinite(init_z_val)):
                    raise ValueError("init_z must be a finite, positive number.")
                logz0 = float(np.log(init_z_val))

            _, _, k_dcgm, _, _, _ = self._stats_and_jacobian(logz=logz0, logy=logy0, kappa=kappa0, return_P=False)
            kappa = np.asarray(k_dcgm, dtype=np.float64)

        # Initialize logy and optionally logz.
        init_y_val = float(init_y)
        if (not np.isfinite(init_y_val)) or init_y_val <= 0.0:
            raise ValueError("init_y must be a finite, positive number.")
        init_logy = float(np.log(init_y_val))
        init_logz = None
        if init_z is not None:
            init_z_val = float(init_z)
            if (not np.isfinite(init_z_val)) or init_z_val <= 0.0:
                raise ValueError("init_z must be a finite, positive number.")
            init_logz = float(np.log(init_z_val))

        outer_converged = bool(use_true_degrees)
        outer_it = 0
        inner_diag: Optional[Fit2SMDiagnostics] = None
        P_last: Optional[np.ndarray] = None
        extras_last: Dict[str, float] = {}

        logz_last = 0.0
        logy_last = init_logy
        L_hat_last = np.nan
        S_hat_last = np.nan
        k_hat_last = np.asarray(kappa, dtype=np.float64).copy()

        for outer_it in range(1, int(max(1, outer_max_steps)) + 1):
            logz_last, logy_last, L_hat_last, S_hat_last, k_hat_last, P_last, diag, extras = self._inner_newton(
                L_target=float(L_val),
                S_target=float(S_val),
                kappa=kappa,
                inner_tol=float(inner_tol),
                inner_max_iter=int(inner_max_iter),
                logy_bounds=logy_bounds,
                jac_reg=float(jac_reg),
                line_search=bool(line_search),
                init_logy=logy_last,
                init_logz=init_logz,
                verbose=bool(verbose),
                return_P=bool(return_P),
            )
            inner_diag = diag
            extras_last = extras

            # If inner calibration fails, kappa updates are not propagated.
            if not bool(diag.inner_converged):
                outer_converged = False
                break

            if use_true_degrees:
                outer_converged = True
                break

            # Self-consistency check on kappa.
            denom = np.maximum(1.0, np.abs(kappa))
            rel = float(np.max(np.abs(k_hat_last - kappa) / denom))
            if rel <= float(outer_tol):
                outer_converged = True
                kappa = np.asarray(k_hat_last, dtype=np.float64).copy()
                break

            # Fixed point update.
            kappa = np.asarray(k_hat_last, dtype=np.float64).copy()

        # Final derived quantities.
        z = float(np.exp(float(logz_last)))
        y = float(np.exp(float(logy_last)))

        kappa_arr = np.asarray(kappa, dtype=np.float64).reshape(-1)
        kappa_mean = float(np.mean(kappa_arr)) if kappa_arr.size > 0 else 0.0
        if kappa_mean > 0.0:
            kappa_prime = (kappa_arr / kappa_mean).astype(float)
        else:
            kappa_prime = np.zeros_like(kappa_arr, dtype=float)

        log_y_tilde = float(extras_last.get("log_y_tilde", 0.0))
        y_tilde = float(np.exp(log_y_tilde)) if np.isfinite(log_y_tilde) else float("inf")

        result = Fit2SMResult(
            z=z,
            y=y,
            logz=float(logz_last),
            logy=float(logy_last),
            L_target=float(L_val),
            S_target=float(S_val),
            L_hat=float(L_hat_last),
            S_hat=float(S_hat_last),
            kappa=np.asarray(kappa_arr, dtype=float),
            k_hat=np.asarray(k_hat_last, dtype=float),
            kappa_mean=float(kappa_mean),
            kappa_prime=np.asarray(kappa_prime, dtype=float),
            y_tilde=float(y_tilde),
            log_y_tilde=float(log_y_tilde),
            inner_converged=bool(inner_diag.inner_converged) if inner_diag is not None else False,
            outer_converged=bool(outer_converged),
            inner_n_iter=int(inner_diag.inner_n_iter) if inner_diag is not None else 0,
            outer_n_iter=int(outer_it),
            message=str(inner_diag.message) if inner_diag is not None else "No diagnostics available.",
            L_rel_err=_rel_err(float(L_hat_last), float(L_val)),
            S_rel_err=_rel_err(float(S_hat_last), float(S_val)),
            L_abs_err=float(abs(float(L_hat_last) - float(L_val))),
            S_abs_err=float(abs(float(S_hat_last) - float(S_val))),
            P=None if not return_P else (None if P_last is None else np.asarray(P_last, dtype=float)),
        )

        self._result = result
        return result

    def probabilities(self) -> np.ndarray:
        """
        Return the calibrated probability matrix.

        Notes
        -----
        If fit(return_P=True) was used, the cached matrix is returned.
        Otherwise, the matrix is recomputed from the stored fitted parameters.
        """
        if self._result is None:
            raise RuntimeError("Model is not calibrated. Call fit() first.")
        if self._result.P is not None:
            return np.asarray(self._result.P, dtype=float)

        # Recompute from stored fitted parameters and kappa.
        _, _, _, _, P, _ = self._stats_and_jacobian(
            logz=float(self._result.logz),
            logy=float(self._result.logy),
            kappa=np.asarray(self._result.kappa, dtype=np.float64),
            return_P=True,
        )
        if P is None:
            raise RuntimeError("Probability matrix could not be computed.")
        return np.asarray(P, dtype=float)