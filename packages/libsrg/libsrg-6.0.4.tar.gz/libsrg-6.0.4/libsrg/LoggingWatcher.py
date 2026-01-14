#!/usr/bin/env  python3
# libsrg (Code and Documentation) is published under an MIT License
# Copyright (c) 2023,2024 Steven Goncalo
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# 2024 Steven Goncalo

import logging
from queue import Queue

log = logging.getLogger("libsrg.LoggingWatcher")


class LoggingWatcher(logging.Handler):
    """
    LoggingWatcher is a subclass of logging.Handler that puts logging records in a queue.
    This queue is read by the TKGUI logic to sort logging records per thread for display.

    This is a singleton and the constructor should not be explicitly called from outside the class methods.

    """

    __instance: "LoggingWatcher" = None

    def __init__(self, *args, **kwargs):
        """
        Constructor.
        :param args: positional arguments passed to logging.Handler
        :param kwargs: keyword arguments passed to logging.Handler
        """
        super(LoggingWatcher, self).__init__(*args, **kwargs)
        self.kwargs = kwargs
        self.seen = {}
        self.queue = Queue()
        self.do_print = self.kwargs.get("do_print", False)
        self.do_queue = self.kwargs.get("do_queue", True)

    def get_queue(self) -> Queue:
        """
        Get a queue of logging records.
        :return: the queue of logging records
        """
        return self.queue

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a record. (record is recorded to queue)
        :param record:
        :return:
        """
        self.queue.put(record)

    @classmethod
    def attach(cls) -> "LoggingWatcher":
        """
        Attach a logging watcher to logging
        """
        handler = cls.get_instance()
        logging.getLogger().addHandler(handler)
        return handler

    @classmethod
    def get_instance(cls):
        """
        Get the logging watcher instance
        :return:
        """
        if cls.__instance is None:
            cls.__instance = LoggingWatcher()
        return cls.__instance
