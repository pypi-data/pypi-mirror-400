# libsrg (Code and Documentation) is published under an MIT License
# Copyright (c) 2023,2024 Steven Goncalo
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# 2024 Steven Goncalo
"""
Module before includes
"""
import logging
import os
import subprocess
from pathlib import Path
from typing import List, Optional, Union, Dict

from libsrg.Config import Config
from libsrg.ElapsedTime import ElapsedTime

"""
Module after includes
"""


class Runner:
    def __init__(self, cmd: Union[List[str], str], timeout=None, rethrow=False, verbose=False, throw=False,
                 cwd: Optional[Union[str, Path]] = None,
                 userat: Optional[str] = None,
                 env: Optional[Dict[str, str]] = None,
                 inherit_env: bool = False,
                 logger: Optional[logging.Logger] = None,
                 retries: int = 0,
                 silent: bool = False,
                 success_codes: Union[None, List[int]] = None,
                 ):
        """
        Runner is a utility class to run a command as a subprocess and return results
        * command is passed as a list of program followed by zero or more arguments
          * if provided as a single string, it calls split to make it a list
        * Runner objects are single use
          * command executed by constructor
          * results returned as fields of object
        * stdout and stderr are captured and returned as lists of utf-8 strings
          * one list element per line
          * end of line chars removed
          * empty list if no output captured
        * return code as integer
        * any exception raised is caught
          * returned in caught field
          * logged as an error
          * optionally rethrown if rethrow is set True
        * success field is true if no exceptions caught and return code is zero
        * exception raised if throw is True and success is false

        :param cmd: A list of strings, or a single string which Runner will str.split()
        :param timeout: If positive, number of seconds before a timeout exception is raised
        :param rethrow: If true, rethrow any exceptions caught, else success set False
        :param verbose: If true, log the command before execution
        :param cwd: If set, run in this location on local node
        :param userat: Prepend ssh to cammand with this user@remote.node string
        :param env: if provided, pass this env to subprocess
        :param inherit_env: If true, inherit env from process, else pass none to subprocess
        :param logger: Logger to use
        :param retries: Number of times to retry the command if not success
        :param silent if set, suppress all logging
        :param success_codes: If provided, any listed return code is reported as success. default is [0]

        """

        self.logger = logger if logger else logging.getLogger(self.__class__.__name__)
        self.runtime = ElapsedTime("runtime")

        # _cmd is a list of program name and zero or more arguments
        # split it into a list if provided as a string
        if isinstance(cmd, str):
            self._cmd = cmd.split()
        else:
            self._cmd = cmd
        if userat:
            self._cmd = ["ssh", userat, "-oPasswordAuthentication=no"] + self._cmd
        # timeout (if specified) is a timeout to communicate in seconds
        self.env = os.environ if inherit_env else env
        self.allowed_tries = retries + 1
        self.silent = silent
        self.try_number = 0
        self.timeout = timeout
        self.userat = userat
        self.success = False
        self.so_bytes: bytearray
        self.se_bytes: bytearray
        self.verbose = verbose
        self.cwd = cwd
        self.ret: int = -1
        self.so_lines: List[str] = []
        self.se_lines: List[str] = []
        self.caught: Optional[Exception] = None
        self.p = None
        self.throw = throw
        self.rethrow = rethrow
        self.success_codes = success_codes if success_codes else [0]
        with self.runtime:
            self._run_subprocess()
        if throw and not self.success:
            self.log()
            raise Exception(f"Runner failed {self}")
        if verbose:
            self.log()

    def log(self, lgr: logging.Logger = None, throw=False) -> None:
        """
        Log results to logger
        :param lgr: override default class logger
        :param throw: throw an exception if not successful
        :return:
        """
        if not self.silent:
            if not lgr:
                lgr = self.logger
            if self.success:
                lgr.info(
                    f'Runner success={self.success} ret={self.ret} _cmd={self._cmd}' +
                    f'  runtime={self.runtime.elapsed():5.3f} so_lines={self.so_lines}')
            else:
                # noinspection PyPep8
                lgr.warning(
                    f'Runner success={self.success} ret={self.ret} _cmd={self._cmd}' +
                    f'  runtime={self.runtime.elapsed():5.3f} so_lines={self.so_lines} se_lines={self.se_lines} ')
        if not self.success and throw:
            raise ChildProcessError(str(self))

    def raise_if_failed(self, lgr: logging.Logger = None, ) -> None:
        """
        Raise an exception if not successful
        :param lgr: override default class logger
        """
        self.log(lgr=lgr, throw=True)

    def _run_subprocess(self) -> None:
        """
        Internal method to run command as subprocess
        """
        for self.try_number in range(self.allowed_tries):
            if self.verbose:
                self.logger.debug(self._cmd)
            try:
                self.p = subprocess.Popen(self._cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE, cwd=self.cwd, env=self.env)
                (self.so_bytes, self.se_bytes) = self.p.communicate(timeout=self.timeout)
                self.ret = self.p.wait()
                self.so_str = self.so_bytes.decode("utf-8")
                self.so_lines = self.so_str.splitlines(keepends=False)
                self.se_str = self.se_bytes.decode("utf-8")
                self.se_lines = self.se_str.splitlines(keepends=False)
                self.success = self.ret in self.success_codes
                if self.success:
                    return
            except Exception as ex:
                if not self.silent:
                    self.logger.error(ex)
                self.success = False
                self.caught = ex
        if self.rethrow and self.caught:
            raise self.caught

    def config_from_so(self) -> Config:
        """
        Convert standard output to a config file
        :return: Config
        """
        return Config.text_to_config(self.so_str)

    def __str__(self):
        """
        One line of command and result
        :return:
        """
        # noinspection PyPep8
        cstr = " ".join(self._cmd)
        return f'Runner(success={self.success} ret={self.ret} cstr="{cstr}" runtime={self.runtime.elapsed():5.3f} so_lines={self.so_lines} se_lines={self.se_lines} userat={self.userat})'


if __name__ == "__main__":
    from libsrg.LoggingCounter import LoggingCounter

    LoggingCounter.config_and_attach()

    runner = Runner("sleep 5", timeout=10)
    print(runner)
    print(runner.try_number, runner.allowed_tries)

    runner = Runner("sleep 5", timeout=3)
    print(runner)
    print(runner.try_number, runner.allowed_tries)

    runner = Runner("sleep 5", timeout=3, retries=2)
    print(runner)
    print(runner.try_number, runner.allowed_tries)

    runner = Runner("wc")
    print(runner)

    runner = Runner("uname -a", userat="root@kylo")
    print(runner)

    runner = Runner("uname -a", userat="root@10.0.1.40")
    print(runner)

    runner = Runner("hostnamectl -j")
    con = runner.config_from_so()
    print(con)

    logging.info(f"Runner {con}")
