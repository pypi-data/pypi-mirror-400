#!/usr/bin/env  python3
# libsrg (Code and Documentation) is published under an MIT License
# Copyright (c) 2023,2024 Steven Goncalo
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# 2024 Steven Goncalo

import atexit
import logging
import sys
import time
from collections import Counter
from importlib.metadata import version, PackageNotFoundError
from logging.handlers import RotatingFileHandler
from typing import List

from libsrg.ElapsedTime import ElapsedTime
from libsrg.LevelBanner import LevelBanner
from libsrg.LoggingUtils import level2str, libsrg_version

log = logging.getLogger("libsrg.LoggingCounter")


class LoggingCounter(logging.Handler):
    """LoggingCounter is a subclass of logging.Handler that counts the number of logs performed at each logging.Level
    self.count_at_level_name is a dictionary indexed by logging.Level, in which counts are maintained
    self.frozen is a flag which freezes counts while logging counts

    This is a singleton and the constructor should not be explicitly called from outside of the class methods.

    """

    __instance: "LoggingCounter" = None

    __rotating_file_handler: RotatingFileHandler = None

    def __init__(self, *args, **kwargs):
        """
        Constructor registers the logging counter instance.

        It will throw an exception if another instance is already created.

        :param args: passed to logging.Handler
        :param kwargs: passed to logging.Handler
        """
        super(LoggingCounter, self).__init__(*args, **kwargs)
        if self.__instance is not None:
            log.critical("Constructor called on existing singleton")
            raise Exception("LoggingCounter is designed as a singleton")
        self.__class__.__instance = self
        # index is name of level, not numeric value
        self.count_at_level_name = Counter()
        self.frozen = False
        self.runtime = ElapsedTime("Runtime")

    def emit(self, record):
        """
        When handler is told to emit a record, it counts the number of logs performed at each level.
        :param record:
        """
        if not self.frozen:
            lev = record.levelname
            # if lev not in self.count_at_level_name:
            #     self.count_at_level_name[lev] = 0
            self.count_at_level_name[lev] += 1

    def count_for_level(self, lev) -> int:
        """
        Returns count of logs performed at given level
        :param lev: level name or numeric level
        """
        lev_str: str = level2str(lev)
        return self.count_at_level_name[lev_str]

    def __log_atexit(self, logger: logging.Logger = None, log_level=logging.INFO):
        """
        At Exit routine to print logging and runtime summary
        :param logger: logger to use for printing
        :param log_level: level at which to print summary
        """
        if logger is None:
            logger = log
        self.frozen = True
        self.runtime.stop()
        ver = libsrg_version()
        olist: List[str] = [f"\n\n{sys.argv[0]} Using libsrg {ver} from {libsrg_version()}", "Logging Summary:"]
        lasttag = None
        for tag in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            if tag in self.count_at_level_name:
                count = self.count_at_level_name[tag]
                olist.append(f"Logging at Level {tag:10s} occurred {count:10d} times")
                if count:
                    lasttag = tag
        if lasttag:
            banner = LevelBanner.find(lasttag, logging.WARNING)
            olist.append(banner)
        olist.append(f"Elapsed time was {self.runtime.elapsed_asc()} ({self.runtime.elapsed():.3f} seconds)")
        logger.log(log_level, "\n".join(olist))
        self.frozen = False

    # noinspection PyPep8Naming
    @classmethod
    def config_and_attach(cls, filename: str = None, maxBytes: int = 10 * 1024 * 1024, backupCount: int = 5,
                          **kwargs) -> "LoggingCounter":
        """Performs logging.basicConfig and attaches counter
        see https://docs.python.org/3/library/logging.html#logging.basicConfig
        """
        already_exists = cls.__instance is not None
        # format0 = '%(asctime)s %(levelname)s %(message)s'
        if 'format' not in kwargs:
            # see https://docs.python.org/3/library/logging.html#logging.LogRecord
            kwargs['format'] = "%(asctime)s %(levelname)-8s %(lineno)4d %(name) 20s.%(funcName)-22s -- %(message)s"
        format_ = kwargs.get("format")
        if 'level' not in kwargs:
            kwargs['level'] = logging.DEBUG
        # logging.basicConfig(filename=filename, format=fmt, level=level)

        logging.basicConfig(**kwargs)
        if filename:
            cls.__rotating_file_handler = RotatingFileHandler(filename,
                                                              maxBytes=maxBytes,
                                                              backupCount=backupCount,
                                                              mode='a')
            formatter = logging.Formatter(format_)
            cls.__rotating_file_handler.setFormatter(formatter)
            logging.getLogger().addHandler(cls.__rotating_file_handler)
            logging.getLogger().info(
                f"Rotating file handler {cls.__rotating_file_handler} {filename=} {maxBytes=} {backupCount=}")
        handler = cls.get_instance()
        logging.getLogger().addHandler(handler)
        if already_exists:
            log.critical("Looks like a LoggingCounter was already created? Good luck with that...")
        else:
            # log.info("Logging system configured")
            atexit.register(cls.log_counters)
        return handler

    @classmethod
    def rotate_files(cls) -> None:
        """
        Rotates all log files
        :return:
        """
        if cls.__rotating_file_handler is not None:
            cls.__rotating_file_handler.doRollover()

    @classmethod
    def get_instance(cls):
        """
        Returns the LoggingCounter instance
        :return:
        """
        if cls.__instance is None:
            cls.__instance = LoggingCounter()
        return cls.__instance

    @classmethod
    def log_counters(cls, logger: logging.Logger = None, log_level=logging.INFO):
        """
        Logs the number of logs performed at each level (same as __log_atexit)
        :param logger:
        :param log_level:
        :return:
        """
        cls.get_instance().__log_atexit(logger, log_level)

    @classmethod
    def add_logfile(cls, filename, tgt_logger=None, **kwargs):
        """
        Adds a new logfile
        :param filename:
        :param tgt_logger:
        :param kwargs:
        :return:
        """
        if tgt_logger is None:
            tgt_logger = logging.getLogger()

        kwargs.setdefault("maxBytes", 10 * 1024 * 1024)
        kwargs.setdefault("backupCount", 5)
        h = RotatingFileHandler(filename, **kwargs)
        fmt = logging.getLogger().handlers[0].formatter
        h.setFormatter(fmt)
        tgt_logger.addHandler(h)
        if cls.__rotating_file_handler is None:
            cls.__rotating_file_handler = h
        tgt_logger.info(f"Rotating file handler {cls.__rotating_file_handler}")

    # @classmethod
    # def get_elapsed_time(cls):
    #     return cls.get_instance().runtime.elapsed()


# pytest appears to initialize logging before running the user supplied tests
# the code below does not work as intended when converted to a pytest script

# simple demo code
if __name__ == '__main__':
    ctr = LoggingCounter.config_and_attach(level=logging.DEBUG)

    assert ctr.count_for_level('INFO') == 0
    log.debug(f"Runtime {ctr} {ctr.runtime} {ctr.runtime.current()}")

    log.info("Info 1")
    log.info("Info 2")
    log.info("Info 3")
    assert ctr.count_for_level('INFO') == 3
    assert ctr.count_for_level(logging.INFO) == 3
    time.sleep(2)
    log.debug(f"Runtime {ctr} {ctr.runtime} {ctr.runtime.current()}")
    log.warning("Warn 1")
    assert ctr.count_for_level('WARNING') == 1

    time.sleep(2)
    log.debug(f"Runtime {ctr} {ctr.runtime} {ctr.runtime.current()}")

    et = ctr.runtime.current()
    log.debug(f"Elapsed {et} {ctr.runtime}")
    assert et > 3.95
    assert et < 4.05

    log.info(ctr.__class__.__qualname__)
    # now atexit
    # LoggingCounter.log_counters(log)
