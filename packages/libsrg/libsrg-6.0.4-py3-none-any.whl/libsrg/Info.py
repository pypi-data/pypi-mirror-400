#! /usr/bin/env python3
# libsrg (Code and Documentation) is published under an MIT License
# Copyright (c) 2023,2024 Steven Goncalo
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# 2024 Steven Goncalo
import configparser
import logging
import os
import platform
import sys
from importlib.metadata import version

from libsrg.Config import Config
from libsrg.LoggingCounter import LoggingCounter
from libsrg.Runner import ElapsedTime
from libsrg.Runner import Runner
from libsrg.LoggingUtils import libsrg_version


class Info:
    """
    The Info class returns information about a given hostname (default is localhost)
    * uname
    * hostname
    * host
    * /etc/os-release

    To work on a host other than localhost, ssh keys to the other host are required.
    """

    def __init__(self, hostname: str = None, timeout: int = 10, retries: int = 0):
        """
        All available information is fetched from the constructor.
        :param hostname: ssh to this remote host, localhost if None
        :param timeout: max time to wait on ssh calls
        :param retries: max number of retries before giving up


        """
        self.uefi = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.kernel_dnf = None
        self.boot_mode = None
        self.uid = None
        self.pretty_name = None
        self.id_like = None
        self.id = None
        self.osrelease = None
        self.ip = None
        self.short = None
        self.fqdn = None
        self.kernel = None
        self.machine = None
        self.runtime = ElapsedTime("Info_runtime")
        with self.runtime:
            self.retries = retries
            self.libsrg_ver = libsrg_version()
            self.local_node = platform.node()
            self.local_node_short = self.local_node.split('.')[0]
            self.config = configparser.ConfigParser()
            self.like_fedora = False
            self.like_rhel = False
            self.like_redhat = False
            self.like_debian = False
            self.userat = None
            self.success = True
            if hostname:
                self.userat = f"root@{hostname}"
                self.hostname = hostname
            else:
                self.userat = None
                self.hostname = self.local_node_short
            try:
                self._inner(timeout=timeout, retries=retries)
            except Exception as e:
                self.success = False
                self.logger.exception(e, stack_info=True)

    def _inner(self, timeout: int = 10, retries: int = 0):
        """
        Internal function that fetches information from the remote host.
        :param timeout:
        :param retries:
        :return: None
        """
        # return
        if self.userat:
            rh = Runner(f"host {self.hostname}")
            if not rh.success:
                raise Exception(f"Failed name lookup for remote host {self.hostname}")

        rm = Runner("uname -m", userat=self.userat, rethrow=True, timeout=timeout, throw=True, retries=retries)
        self.machine = rm.so_lines[-1]

        rk = Runner("uname -r", userat=self.userat, rethrow=True, timeout=timeout, throw=True, retries=retries)
        self.kernel = rk.so_lines[-1]

        rs = Runner("uname -s", userat=self.userat, rethrow=True, timeout=timeout, throw=True, retries=retries)
        self.kernel_name = rs.so_lines[-1]

        rfqdn = Runner("hostname -f", userat=self.userat, rethrow=True, timeout=timeout, throw=True, retries=retries)
        self.fqdn = rfqdn.so_lines[-1]

        rshort = Runner("hostname -s", userat=self.userat, rethrow=True, timeout=timeout, throw=True, retries=retries)
        self.short = rshort.so_lines[-1]

        rip = Runner("hostname -i", userat=self.userat, rethrow=True, timeout=timeout, throw=True, retries=retries)
        self.ip = rip.so_lines[-1]

        r = Runner("cat /etc/os-release", userat=self.userat, rethrow=True, timeout=timeout, throw=True,
                   retries=retries)
        data = r.so_lines
        # add a section header
        data.insert(0, "[osrelease]")
        self.config.read_string("\n".join(data))
        # for key in self.config:
        #     self.logger.info(key)
        osrelease = self.config['osrelease']
        self.osrelease = osrelease
        # for key, val in osrelease.items():
        #     self.logger.info(f"{key} = {val}")

        # fedora has 'id' lower case, raspian upper
        # configparser says keys are case insensitive
        self.id = (osrelease['ID']).strip('"\'')
        if 'id' in osrelease:
            self.id = osrelease['id'].strip('"\'')
        else:
            self.id = 'unknown'
            self.logger.error(f"'id' not found in {osrelease}")

        # raspian 'ID_LIKE' says, "But you can call me Debian"
        if 'ID_LIKE' in osrelease:
            self.id_like = (osrelease['ID_LIKE']).strip('"\'')
        else:
            self.id_like = self.id
        # self.logger.info(f"id={self.id}, id_like={self.id_like} ")

        if 'PRETTY_NAME' in osrelease:
            self.pretty_name = (osrelease['PRETTY_NAME']).replace('"', '')
        else:
            self.pretty_name = self.id + " " + osrelease['VERSION_ID']

        if "rhel" in self.id or "rhel" in self.id_like:
            self.like_rhel = True
        elif "fedora" in self.id or "fedora" in self.id_like:
            self.like_fedora = True
        elif "debian" in self.id or "debian" in self.id_like:
            self.like_debian = True
        elif "ubuntu" in self.id or "ubuntu" in self.id_like:
            self.like_debian = True

        self.like_redhat = self.like_fedora or self.like_rhel

        self.uid = os.getuid()
        bios = "ARM" if "aarch64" in self.machine else "BIOS"
        # These next few Runner calls may return non zero status
        rhow = Runner(f"test -d /sys/firmware/efi", userat=self.userat, rethrow=False, timeout=timeout, throw=False,
                      retries=retries)
        self.uefi = "UEFI" if rhow.success else bios

        r2 = Runner("grep 'exclude=kernel' /etc/dnf/dnf.conf", userat=self.userat, rethrow=False, timeout=timeout,
                    throw=False, retries=retries)
        ret = r2.ret
        if ret == 0:
            self.kernel_dnf = "locked"
        elif ret == 1:
            self.kernel_dnf = "unlocked"
        else:
            self.kernel_dnf = "NA"

    def __str__(self):
        """
        One line string representation of the Info object.
        :return: string representation of the Info object
        """
        return f"Info({self.hostname=} {self.id=} {self.id_like=} {self.pretty_name=} {self.machine=})"

    def is_root(self) -> bool:
        """
        Checks if the user calling Info is root or not.
        :return: true if the user calling Info is root
        """
        return self.uid == 0

    def is_linux(self) -> bool:
        """
        Checks if uname -s reported Linux.
        :return: true if the system is Linux
        """
        return self.kernel_name == "Linux"

    def exit_if_not_root(self):
        """
        Checks if the user calling Info is root and calls exit if not root.
        :return: None or exit without explicit return
        """
        if not self.is_root():
            self.logger.critical("Must run as root, uid={self.uid}, hostname={self.hostname}")
            exit(-1)

    def is_x86_64(self) -> bool:
        """
        :return: true if host is x86_64
        """
        return self.machine == "x86_64"

    def dump(self):
        """
        print a dump of all data obtained about host
        """
        # print(self)
        for k, v in self.__dict__.items():
            if k not in ["logger", "config", "osrelease"]:
                print(f"{k}={v}")
        if "osrelease" in self.__dict__ and self.__dict__["osrelease"]:
            for k, v in self.osrelease.items():
                print(f"osrelease.{k}={v}")
        print("-----------------------------------------------")

    def to_config(self, prefix: str = None) -> Config:
        """
        Load discovered info into a Config object.
        :param prefix:  string top be prepended at the start of field names
        """
        config = Config()
        if prefix is None:
            prefix = ""
        for k, v in self.__dict__.items():
            if k not in ["logger", "config", "osrelease"]:
                if isinstance(v, (int, float, str, bool)):
                    config.set_item(f"{prefix}{k.lower()}", v)

        if "osrelease" in self.__dict__ and self.__dict__["osrelease"]:
            for k, v in self.osrelease.items():
                if isinstance(v, (int, float, str, bool)):
                    config.set_item(f"{prefix}osrelease.{k}", v)
                    config.set_item(f"{prefix}osrelease.{k.lower()}", v)
        return config


if __name__ == '__main__':
    import pprint

    # info = Info("nas0")
    LoggingCounter.config_and_attach()
    argv = sys.argv[1:]
    if len(argv) == 0:
        argv = ["localhost"]
    for arg in argv:
        i = Info(arg)
        pprint.pp(i.to_config(arg + "__"))
    # for name in [None, "nas1", "web", "nowhere"]:
    #     logging.info(f"start {name}")
    #     t1 = ElapsedTime(f"Outer {name}")
    #     print(name, "*" * 80)
    #     with t1:
    #         info = Info(name)
    #     logging.info(f"returned {name} {info} {t1}")
    #     with t1:
    #         info.dump()
    #     logging.info(f"dump complete {name} {t1}")
