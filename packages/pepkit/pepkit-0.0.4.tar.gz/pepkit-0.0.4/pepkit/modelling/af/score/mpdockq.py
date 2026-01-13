from __future__ import annotations

import math
import warnings
from typing import Any, Dict

from .base import BaseDockQScorer
from .models import MPDOCKQ_MODEL


class MPDockQ(BaseDockQScorer):
    def __init__(self, *, warn_if_lt3: bool = True):
        super().__init__(
            name="mpDockQ",
            model=MPDOCKQ_MODEL,
            required_keys=("interface_plddt", "n_contacts_pdockq"),
        )
        self.warn_if_lt3 = bool(warn_if_lt3)

    def x_from_analysis(self, d: Dict[str, Any]) -> float:
        p = float(d["interface_plddt"])
        n = int(d["n_contacts_pdockq"])
        if n <= 0 or math.isnan(p):
            return float("nan")
        return p * math.log10(n)

    def compute(self, d: Dict[str, Any]):
        n_chains = d.get("n_chains", None)
        if self.warn_if_lt3 and isinstance(n_chains, int) and n_chains < 3:
            warnings.warn(
                f"mpDockQ is calibrated for >=3 chains; n_chains={n_chains}. "
                f"Computing anyway (interpret with caution).",
                RuntimeWarning,
                stacklevel=2,
            )
        return super().compute(d)
