# libsrg (Code and Documentation) is published under an MIT License
# Copyright (c) 2023,2024 Steven Goncalo
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

from typing import Optional, Callable, Any

from libsrg.Statistics.DiscreteStatsBase import DiscreteStatsBase

"""
For now, all functionality is in super()
"""


class DiscreteStatsCumulative(DiscreteStatsBase):
    class_callbacks: list[Callable] = []

    def __init__(self, name, callbacks: Optional[list[Callable]] = None):
        super().__init__(name=name, callbacks=callbacks)

    def get_all_callbacks(self) -> list[Callable]:
        lst = super().get_all_callbacks()
        lst.extend(DiscreteStatsCumulative.class_callbacks)
        return lst

    def sample(self, value: Any, sample_time: Optional[float] = None) -> bool:
        first = super().sample(value=value, sample_time=sample_time)
        return first

    def reset(self):
        super().reset()
