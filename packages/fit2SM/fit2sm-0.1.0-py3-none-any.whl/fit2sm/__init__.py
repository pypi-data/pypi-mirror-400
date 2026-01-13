"""Top-level public API for the fit2sm package."""

from __future__ import annotations

from ._version import __version__
from .dcgm import DcGMModel
from .fit2sm import Fit2SMModel
from .motifs import calculate_S
from .ubcm import UBCMModel

__all__ = [
    "__version__",
    "DcGMModel",
    "Fit2SMModel",
    "UBCMModel",
    "calculate_S",
]
