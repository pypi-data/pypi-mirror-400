#!/usr/bin/env  python3
# libsrg (Code and Documentation) is published under an MIT License
# Copyright (c) 2023,2024 Steven Goncalo
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# 2024 Steven Goncalo

# from optparse import OptionParser
import sys
from enum import Enum

from libsrg.LoggingAppBase import LoggingAppBase


class NagiosReturn(Enum):
    """
    Enum class to represent Nagios return codes.
    """
    NOCALL = -1
    OK = 0
    WARNING = 1
    CRITICAL = 2
    UNKNOWN = 3


# noinspection PyPep8Naming
class NagiosBase(LoggingAppBase):
    """
    Base class for Nagios applications.
    """
    def __init__(self):
        """
        Constructor. Initializes logging and sets up default command line arguments.
        """
        super().__init__()

        self.curReturn = NagiosReturn.NOCALL
        self.curReturnStr = "nocall?"
        self.defReturn = NagiosReturn.UNKNOWN
        self.defReturnStr = "no status reported?"
        try:
            self.createParser()
            self.runTest()
        except Exception as e:
            self.logger.critical(f"Unexpected error: {e}")
        finally:
            self.report()

    # noinspection PyPep8Naming
    def createParser(self):
        """
        Creates command line parser.
        * host address
        * username
        * verbose flag
        :return:
        """

        self.parser.add_argument("-H", "--hostaddress",
                                 action="store", dest="host", default="nas0.home.goncalo.name",
                                 help="FQDN or IP of host to check via ssh")
        self.parser.add_argument("-U", "--user",
                                 action="store", dest="user", default="root",
                                 help="username at hostaddress")
        self.parser.add_argument('-v', '--verbose', help='enable verbose output', dest='verbose', action='store_true',
                                 default=False)
        # self.parser.add_argument('--log-file', nargs=1, help='file to log to (default = stdout)', dest='logfile',
        #                          type=str, default=None)

        self.extendParser()
        self.perform_parse()

    def nocallResult(self, retCode, retStr):
        """
        Sets return code directly to Nagios return code.
        :param retCode:
        :param retStr:
        :return:
        """
        self.defReturn = retCode
        self.defReturnStr = retStr

    def setResult(self, retCode, retStr):
        """
        Sets return code to worse of given and previous codes
        :param retCode:
        :param retStr:
        :return:
        """
        if retCode.value > self.curReturn.value:
            self.curReturn = retCode
            self.curReturnStr = retStr

    def report(self):
        """
        Prints worst case return code and message at end of test
        :return:
        """
        if self.curReturn == NagiosReturn.NOCALL:
            self.logger.error("using nocall result")
            self.curReturn = self.defReturn
            self.curReturnStr = self.defReturnStr
        self.logger.info(f"{self.curReturn.name}={self.curReturn.value} {self.curReturnStr}")
        print(self.curReturn.name, " - ", self.curReturnStr)
        sys.exit(self.curReturn.value)

    # these need to be overriden in the subclass
    def extendParser(self):
        """
        Extends command line parser.
        :return:
        """
        self.logger.error("createSubclassParser should be overridden in Subclass")

    def runTest(self):
        """
        This is where the actual test is executed.
        :return:
        """
        self.logger.error("runTest should be overridden in Subclass")


if __name__ == '__main__':
    print("This module cannot be run standalone")
    sys.exit(-1)
