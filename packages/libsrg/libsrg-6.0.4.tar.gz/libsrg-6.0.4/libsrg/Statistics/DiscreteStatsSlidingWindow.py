# libsrg (Code and Documentation) is published under an MIT License
# Copyright (c) 2023,2024 Steven Goncalo
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

from typing import Optional, Callable, Any

from libsrg.Statistics.DiscreteStatsBase import DiscreteStatsBase


class DiscreteStatsSlidingWindow(DiscreteStatsBase):
    class_callbacks: list[Callable] = []

    def __init__(self, name, callbacks: Optional[list[Callable]] = None, window: int = 100):
        super().__init__(name=name, callbacks=callbacks)
        self.window = window
        self.history = []

    def get_all_callbacks(self) -> list[Callable]:
        lst = super().get_all_callbacks()
        lst.extend(DiscreteStatsSlidingWindow.class_callbacks)
        return lst

    def sample(self, value: Any, sample_time: Optional[float] = None) -> bool:
        first = super().sample(value=value, sample_time=sample_time)
        self.history.append(value)
        if len(self.history) > self.window:
            xvalue = self.history.pop(0)
            self.counter[xvalue] -= 1
        return first

    def reset(self):
        super().reset()

    def window_full(self) -> bool:
        """
        Checks if the window is full.
        :return: true if history full to window size, otherwise false
        """
        return len(self.history) >= self.window

    def window_at_least_half_full(self) -> bool:
        """
        Checks if the window is at least half full.
        :return: true if history full to at least half window size, otherwise false
        """
        return len(self.history) * 2 >= self.window

    def window(self) -> int:
        """
        Returns the window size.
        :return: window size
        """
        return self.window
