from __future__ import annotations

import math
from typing import Any, Dict

from .base import BaseDockQScorer
from .models import PDOCKQ_MODEL


class PDockQ(BaseDockQScorer):
    def __init__(self, *, use_log10: bool = False):
        super().__init__(
            name="pDockQ",
            model=PDOCKQ_MODEL,
            required_keys=("interface_plddt", "n_contacts_pdockq"),
        )
        self.use_log10 = bool(use_log10)

    def x_from_analysis(self, d: Dict[str, Any]) -> float:
        p = float(d["interface_plddt"])
        n = int(d["n_contacts_pdockq"])
        if n <= 0 or math.isnan(p):
            return float("nan")
        logn = math.log10(n) if self.use_log10 else math.log(n)
        return p * logn
