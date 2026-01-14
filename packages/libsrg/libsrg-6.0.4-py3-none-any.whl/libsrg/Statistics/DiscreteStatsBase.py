# libsrg (Code and Documentation) is published under an MIT License
# Copyright (c) 2023,2024 Steven Goncalo
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Callable, Any

from libsrg.Statistics.ADStatsBase import ADStatsBase, ADStatsRecord


@dataclass
class DStatsRecord(ADStatsRecord):
    """Record returned to DStats observer

    Note that value is an Any for internal use
    Saving to database should str() the value first"""
    value: Any


class DiscreteStatsBase(ADStatsBase):
    class_callbacks: list[Callable] = []

    def __init__(self, name, callbacks: Optional[list[Callable]] = None):
        super().__init__(name=name, callbacks=callbacks)
        self.counter = Counter()
        self.last_time: dict[str, datetime] = dict()

    def get_all_callbacks(self) -> list[Callable]:
        lst = super().get_all_callbacks()
        lst.extend(DiscreteStatsBase.class_callbacks)
        return lst

    def sample(self, value: Any, sample_time: Optional[float] = None) -> bool:
        first = super().sample(value=value, sample_time=sample_time)
        self.counter[value] += 1
        self.last_time[value] = datetime.now(timezone.utc)
        return first

    def reset(self):
        super().reset()
        self.counter.clear()

    def counts(self) -> Counter:
        return self.counter.copy()

    def datetimes(self) -> dict[str, datetime]:
        return self.last_time.copy()

    def count_for(self, value: Any) -> int:
        return self.counter[value]

    def most_common(self, n: int, time_format: str = None) -> list[tuple[Any, int, str]]:
        if time_format is None:
            time_format = "%Y-%m-%d %H:%M:%S %Z"
        mc = self.counter.most_common(n)
        mct = [(key, val, self.last_time[key].astimezone().strftime(time_format)) for key, val in mc]
        return mct

    def most_common_as_str(self, n: int, time_format: str = None) -> str:
        mct = self.most_common(n, time_format)
        return str(mct)

    def form_record(self, name: str, count: int, time: float, val: Any) -> DStatsRecord:
        return DStatsRecord(value=val, name=name, count=count, time=time)
