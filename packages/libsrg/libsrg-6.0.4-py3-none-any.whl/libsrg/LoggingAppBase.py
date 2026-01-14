#!/usr/bin/env  python3
# libsrg (Code and Documentation) is published under an MIT License
# Copyright (c) 2023,2024 Steven Goncalo
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# 2024 Steven Goncalo

import argparse
import logging
from importlib.metadata import version
from typing import Optional

from libsrg.LoggingCounter import LoggingCounter
from libsrg.LoggingUtils import level2str, level2int, libsrg_version
from libsrg.Runner import Runner


class LoggingAppBase:
    """This base class initializes the logger and creates a minimal argparse command line parser in __init__
    The parser is not run in this call. The application code can then add arguments to the parser.
    Since calls to derived class functions can not be made in the base class constructor, this must be done
    in separate steps.

    After augmenting the parser, the application code should call perform_parse after adding arguments to the
    parser before attempting to access the parsed results.

    https://docs.python.org/3/howto/argparse.html

     """

    def __init__(self, level=logging.INFO, logfile=None, parser_args: Optional[dict[str, str]] = None,**vargs):
        self.logger = logging.getLogger(self.__class__.__name__)
        LoggingCounter.config_and_attach(**vargs)
        self.args = {}
        self.initial_level = level2str(level)
        try:
            # set usage if missing
            if parser_args is None:
                parser_args = {}
            parser_args.setdefault("epilog", f"Build using libsrg {libsrg_version()}")
            self.parser = argparse.ArgumentParser(**parser_args)
            self.parser.add_argument('--libsrg', help='Print version of libsrg and exit', action='version',
                                     version=f"libsrg {libsrg_version()}")
            self.parser.add_argument('--logfile', help='file to log to (default = stdout)', dest='logfile',
                                     type=str, default=logfile)
            self.parser.add_argument("--logging", "--level", action='store',
                                     choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"],
                                     default=self.initial_level, dest='logging')
        except Exception as e:
            self.logger.exception(f"Unexpected exception: {e}")
            raise e

    def perform_parse(self):
        self.args = self.parser.parse_args()
        # set logging level at base logger
        level = level2int(self.args.logging)
        logging.getLogger().setLevel(level)
        if 'logfile' in self.args and self.args.logfile is not None:
            LoggingCounter.add_logfile(self.args.logfile, mode='a')


class SampleApp(LoggingAppBase):
    """
    This is just a simple demo application to show how the LoggingAppBase class should be extended.

    It serves no real purpose other than serving as a regression test.

    pytest mucks with logging before running test code
    """

    def __init__(self):
        pargs = {"description": "This is an example application", }
        LoggingAppBase.__init__(self, parser_args=pargs)
        self.logger.info("before adding args")
        # setup any program specific command line arguments
        self.parser.add_argument('--version', action='version', version=f"libsrg {libsrg_version()}")

        self.parser.add_argument('--zap', help="Zap something", dest='zap', action='store_true', default=False)
        self.parser.add_argument('--zip', help="Zip something", dest='zip', action='store_true', default=False)
        # invoke the parser
        self.perform_parse()
        #
        self.logger.info(f"after parsing {self.args}")

    def demo_levels(self):
        ctr = LoggingCounter.get_instance()
        self.logger.info(f"getEffectiveLevel is {self.logger.getEffectiveLevel()}  logging.INFO={logging.INFO}")
        oldcount = ctr.count_for_level(logging.DEBUG)
        self.logger.info("call to debug below will be suppressed")
        self.logger.debug("debug log wont show or count this line")
        newcount = ctr.count_for_level(logging.DEBUG)
        assert oldcount == newcount
        self.logger.setLevel(logging.DEBUG)
        self.logger.info("Changed level to DEBUG")
        self.logger.info(f"getEffectiveLevel is {self.logger.getEffectiveLevel()} logging.DEBUG={logging.DEBUG}")
        self.logger.debug("This should show and count")
        newcount = ctr.count_for_level(logging.DEBUG)
        assert (oldcount + 1) == newcount

    def demo_runner(self):
        self.logger.warning("A warning")
        try:
            # linux with systemd assumed in self-test
            #   this is just an external command with multiple lines of output
            r = Runner(["env"])
            self.logger.info(r)
            r = Runner(["env"], inherit_env=True)
            self.logger.info(r)
            r = Runner(["env"], env={"apple": "aaa", "bannana": "bbb"}, logger=self.logger)
            self.logger.info(r)

            r = Runner(["hostnamectl"])
            self.logger.info(r)
            r2 = Runner(["missing program trapped exception"])
            self.logger.info(r2)
            r3 = Runner(["missing program rethrow exception"], rethrow=True)
            self.logger.info(r3)
        except Exception as ex:
            self.logger.info("VVVVV Exception optionally propagated to calling program")
            self.logger.critical(ex, exc_info=True)
            self.logger.info("^^^^^ that was supposed to throw an exception")

    def demo_final_checks(self):
        ctr = LoggingCounter.get_instance()
        self.logger.info("Asserts check actual versus expected logging counts as logged at end of run (atexit)")
        self.logger.info("  note that counters are frozen in atexit code, so atexit output does not change counts\n\n")
        assert ctr.count_for_level(logging.DEBUG) == 1
        assert ctr.count_for_level(logging.INFO) == 15
        assert ctr.count_for_level(logging.WARNING) == 1
        assert ctr.count_for_level(logging.ERROR) == 2
        assert ctr.count_for_level(logging.CRITICAL) == 1

    @classmethod
    def demo(cls):
        app = SampleApp()
        app.demo_levels()
        app.demo_runner()
        app.demo_final_checks()


if __name__ == '__main__':
    SampleApp.demo()
