from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class SigmoidModel:
    """
    DockQ-style sigmoid:

        score(x) = L / (1 + exp(-k(x - x0))) + b
    """

    L: float
    x0: float
    k: float
    b: float

    def __call__(self, x: float) -> float:
        return self.L / (1.0 + math.exp(-self.k * (x - self.x0))) + self.b


# ===============================
# Pre-fitted DockQ family models
# ===============================

PDOCKQ_MODEL = SigmoidModel(
    L=0.724,
    x0=152.611,
    k=0.052,
    b=0.018,
)

PDOCKQ2_MODEL = SigmoidModel(
    L=1.31,
    x0=84.733,
    k=0.075,
    b=0.005,
)

MPDOCKQ_MODEL = SigmoidModel(
    L=0.728,
    x0=309.375,
    k=0.098,
    b=0.262,
)
