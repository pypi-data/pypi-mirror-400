# libsrg (Code and Documentation) is published under an MIT License
# Copyright (c) 2023,2024 Steven Goncalo
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# 2024 Steven Goncalo
import logging
import subprocess
from typing import List, Optional, Union

from libsrg.LoggingAppBase import LoggingAppBase

"""
Runner2 is a utility class to run a pair of commands as a subprocess and return results.

The output of cmd1 is piped into the input of cmd2. Primary usage is intended for zfs send/receive commands, 
where either or both ends of the pipeline may be on remote nodes.

* command is passed as a list of program followed by zero or more arguments
* Runner2 objects are single use
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
"""


class Runner2:

    def __init__(self, cmd1: Union[List[str], str], cmd2: Union[List[str], str], timeout=None, rethrow=False,
                 userat1=None,
                 userat2=None):
        """
        Forms a pipeline where cmd1 runs in one subprocess feeding into cmd2 in another subprocess
        :param cmd1: first command
        :param cmd2: second command
        :param timeout: overall timeout in seconds
        :param rethrow: rethrow any caught exception
        :param userat1: run cmd1 as ssh at this user1@host1
        :param userat2: run cmd2 as ssh at this user2@host2
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        # cmd2 is a list of program name and zero or mor eorguments
        # timeout (if specified) is a timeout to communicate in seconds
        if isinstance(cmd1, str):
            self.cmd1 = cmd1.split()
        else:
            self.cmd1 = cmd1
        if isinstance(cmd2, str):
            self.cmd2 = cmd2.split()
        else:
            self.cmd2 = cmd2
        if userat1:
            self.cmd1 = ["ssh", userat1] + self.cmd1
        if userat2:
            self.cmd2 = ["ssh", userat2] + self.cmd2

        self.success = False
        self.so_bytes: bytearray
        self.se_bytes: bytearray
        self.ret1: int = -1
        self.ret2: int = -1
        self.so_lines: List[str] = []
        self.se_lines: List[str] = []
        self.caught: Optional[Exception] = None
        self.p1 = None
        self.p2 = None
        self.rethrow = rethrow
        self.timeout = timeout
        self._execute()

    def _execute(self):
        """
        inner routine to execute piped commands
        :return:
        """
        try:
            self.logger.info(f'{" ".join(self.cmd1)} | {" ".join(self.cmd2)}')
            self.p2 = subprocess.Popen(self.cmd2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            # self.p2 = subprocess.Popen(self.cmd2,stdin=subprocess.PIPE)
            self.p1 = subprocess.Popen(self.cmd1, stdout=self.p2.stdin)

            (self.so_bytes, self.se_bytes) = self.p2.communicate()  # @UnusedVariable
            self.ret2 = self.p2.wait()
            self.ret1 = self.p1.wait()
            so_str0 = self.so_bytes.decode("utf-8")
            self.so_lines = so_str0.splitlines(keepends=False)
            se_str0 = self.se_bytes.decode("utf-8")
            self.se_lines = se_str0.splitlines(keepends=False)
            self.success = self.ret2 == 0
        except Exception as ex:
            self.logger.error(ex)
            self.success = False
            self.caught = ex
            if self.rethrow:
                raise ex

    def __str__(self):
        """
        Single line summary of the object.
        :return:
        """
        # noinspection PyPep8
        return (
                f'Runner2 success={self.success} ret1={self.ret1}' +
                f' ret2={self.ret2} cmd1={self.cmd1}  cmd2={self.cmd2}  so_lines={self.so_lines}'
        )


if __name__ == '__main__':
    class DemoApp(LoggingAppBase):
        logger = logging.getLogger("libsrg.SampleApp")

        def __init__(self):
            super().__init__()
            self.logger.info("before adding args")
            # setup any program specific command line arguments
            self.parser.add_argument('--zap', help="Zap something", dest='zap', action='store_true', default=False)
            self.parser.add_argument('--zip', help="Zip something", dest='zip', action='store_true', default=False)
            # invoke the parser
            self.perform_parse()
            #
            self.logger.info(f"after parsing {self.args}")
            r = Runner2(["ls"], ["tr", "[a-z]", "[A-Z]"])
            self.logger.info(f"{r}")
            s = Runner2(["ls"], ["tr", "[A-Z]", "[a-z]"])
            self.logger.info(f"{s}")


    demo = DemoApp()
