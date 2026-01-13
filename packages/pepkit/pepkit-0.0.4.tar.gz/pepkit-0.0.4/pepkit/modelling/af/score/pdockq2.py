from __future__ import annotations

import math
from typing import Any, Dict

from .base import BaseDockQScorer, ScoreOutput
from .models import PDOCKQ2_MODEL


class PDockQ2(BaseDockQScorer):
    def __init__(self):
        super().__init__(
            name="pDockQ2",
            model=PDOCKQ2_MODEL,
            required_keys=("interface_plddt", "mean_ptm_pdockq2"),
        )

    def x_from_analysis(self, d: Dict[str, Any]) -> float:
        p = float(d["interface_plddt"])
        m = float(d["mean_ptm_pdockq2"])
        if math.isnan(p) or math.isnan(m):
            return float("nan")
        return p * m

    def compute(self, d: Dict[str, Any]) -> ScoreOutput:
        out = super().compute(d)
        out.extras["mean_ptm_pdockq2"] = float(d["mean_ptm_pdockq2"])
        return out
