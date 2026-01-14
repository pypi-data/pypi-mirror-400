# libsrg (Code and Documentation) is published under an MIT License
# Copyright (c) 2023,2024 Steven Goncalo
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

import math
from typing import Optional, Callable

from libsrg.Statistics.AnalogStatsBase import AnalogStatsBase


class AnalogStatsCumulative(AnalogStatsBase):
    """
        Continuous Analog summation of statistics


    """

    def __init__(self, name, callbacks: Optional[list[Callable]] = None):
        super().__init__(name=name, callbacks=callbacks)
        self._sum_samples: float = 0.
        self._sum_samples_sq: float = 0.

    def reset(self) -> None:
        """
        Clear all statistics
        if overriden by subclass, call super
        """
        super().reset()
        self._sum_samples: float = 0.
        self._sum_samples_sq = 0.

    def sample_bool(self, bvalue: bool, sample_time: Optional[float] = None) -> None:
        value = 1 if bvalue else 0
        self.sample(value=value, sample_time=sample_time)

    def sample(self, value: float, sample_time: Optional[float] = None) -> bool:
        first = super().sample(value=value, sample_time=sample_time)
        self._sum_samples += value
        self._sum_samples_sq += value * value
        return first

    def mean(self) -> float:
        try:
            return self._sum_samples / self._sample_count
        except ZeroDivisionError:
            return math.nan

    def mean_squared(self) -> float:
        try:
            return self._sum_samples_sq / self._sample_count
        except ZeroDivisionError:
            return math.nan


