# libsrg (Code and Documentation) is published under an MIT License
# Copyright (c) 2023,2024 Steven Goncalo
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

import math
from typing import Optional, Callable

from libsrg.Statistics.AnalogStatsBase import AnalogStatsBase


class AnalogStatsFading(AnalogStatsBase):
    """
    RunningStatistics class calculates running mean and standard deviation for data accumulated one sample at a time
    It also produces fading window statistics based on alpha/beta filtering the data.
    Normally beta will be set to (1-alpha) but if alpha and beta are set to one, the windowed statistics should
    match the non-fading.


    """

    def __lt__(self, other: "AnalogStatsFading") -> bool:
        """Allow sorting by name"""
        return self._name < other._name

    def __init__(self, name: str, callbacks: Optional[list[Callable]] = None, alpha: float = 0.99, beta: float = 0):
        super().__init__(name=name, callbacks=callbacks)
        self._alpha: float = alpha
        self._beta: float = beta if beta > 0 else 1 - self._alpha
        self._wsum_weight: float = 0.
        self._wsum_samples: float = 0
        self._wsum_samples_sq: float = 0.

    def reset(self) -> None:
        super().reset()
        self._wsum_weight: float = 0.
        self._wsum_samples: float = 0
        self._wsum_samples_sq: float = 0.

    def _faded(self, old_sum: float, value: float) -> float:
        return self._alpha * old_sum + self._beta * value

    def sample_bool(self, bvalue: bool, sample_time: Optional[float] = None) -> None:
        value = 1 if bvalue else 0
        self.sample(value=value, sample_time=sample_time)

    def sample(self, value: float, sample_time: Optional[float] = None, weight: float = 1, sd=0) -> bool:
        first = super().sample(value=value, sample_time=sample_time)
        self._wsum_weight = self._faded(self._wsum_weight, weight)
        self._wsum_samples = self._faded(self._wsum_samples, value * weight)
        self._wsum_samples_sq = self._faded(self._wsum_samples_sq, ((value * value) + (sd * sd)) * weight)
        return first

    def mean(self) -> float:
        try:
            return self._wsum_samples / self._wsum_weight
        except ZeroDivisionError:
            return math.nan

    def mean_squared(self) -> float:
        try:
            return self._wsum_samples_sq / self._wsum_weight
        except ZeroDivisionError:
            return math.nan
