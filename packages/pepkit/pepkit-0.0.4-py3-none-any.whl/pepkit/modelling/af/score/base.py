from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Iterable
import math

from .models import SigmoidModel


@dataclass(frozen=True)
class ScoreOutput:
    score: float
    x: float
    extras: Dict[str, Any]


class BaseDockQScorer(ABC):
    """
    Abstract base for DockQ-family scorers.

    Input: dict returned by Analysis.single_analysis()
    Output: ScoreOutput(score, x, extras)
    """

    def __init__(self, *, name: str, model: SigmoidModel, required_keys: Iterable[str]):
        self.name = name
        self.model = model
        self.required_keys = list(required_keys)

    def _require(self, d: Dict[str, Any]) -> None:
        missing = [k for k in self.required_keys if k not in d]
        if missing:
            raise KeyError(f"{self.name}: missing Analysis keys: {missing}")

    @abstractmethod
    def x_from_analysis(self, d: Dict[str, Any]) -> float: ...

    def compute(self, d: Dict[str, Any]) -> ScoreOutput:
        self._require(d)
        x = float(self.x_from_analysis(d))
        if math.isnan(x):
            return ScoreOutput(score=float("nan"), x=x, extras={})
        return ScoreOutput(score=float(self.model(x)), x=x, extras={})
