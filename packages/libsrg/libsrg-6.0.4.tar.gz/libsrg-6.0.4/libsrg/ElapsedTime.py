# libsrg (Code and Documentation) is published under an MIT License
# Copyright (c) 2023,2024 Steven Goncalo
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# 2024 Steven Goncalo
"""
ElapsedTime is a class to measure elapsed time between start and stop events.
It can be operated directly using start and stop methods, or it can
act as a context manager in a "with" statement block.
"""
import logging
from datetime import timedelta
from time import time


class ElapsedTime:

    def __init__(self, name=None):
        """
        Constructs ElapsedTime object, started

        :param name: Name of ElapsedTime
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        if name:
            self.name = name
        else:
            self.name = repr(self)
        self._starttime = 0
        self._endtime = 0
        self._elapsed = 0
        self.start()

    def elapsed_asc(self) -> str:
        """
        Returns elapsed time as formatted string.
        Note elapsed time is computed when stop() is called.
        Use current() to get the current elapsed time without stopping.
        :return:
        """
        td = timedelta(seconds=self._elapsed)
        return str(td)

    def __str__(self):
        """
        Returns name and elapsed time as formatted string.
        :return:
        """
        return f"ET({self.name!r},{self.elapsed_asc()},{self._elapsed})"



    def start(self):
        """
        records start time and zeros elapsed.
        * if called more than once, last call wipes any previous data
        * constructor also starts recording elapsed time, so this is only needed to restart timing

        """
        self._starttime = time()
        self._endtime = self._starttime
        self._elapsed = 0


    def stop(self) -> float:
        """records stop time, computes and returns elapsed in seconds
        if called more than once, each call records time since last start
        :return: elapsed time in seconds
        """
        self._endtime = time()
        self._elapsed = self._endtime - self._starttime
        return self._elapsed


    def elapsed(self) -> float:
        """returns elapsed time at last stop, but does not perform a stop
        :return: elapsed time in seconds
        """
        return self._elapsed


    def current(self) -> float:
        """returns time since last start, but does not perform a stop
        :return: elapsed time in seconds
        """
        return time() - self._starttime


    def __enter__(self):
        """translates enter "with" statement into start command"""
        self.start()


    def __exit__(self, exc_type, exc_value, exc_tb):
        """translates exit "with" statement into stop command"""
        self.stop()
