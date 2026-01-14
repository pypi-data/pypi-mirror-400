# libsrg (Code and Documentation) is published under an MIT License
# Copyright (c) 2023,2024 Steven Goncalo
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

import logging
import sys
import threading
import tkinter as tk
from pathlib import Path

from libsrg.LoggingAppBase import LoggingAppBase


class GuiBase(LoggingAppBase):
    logger = logging.getLogger("GuiBase")

    def __init__(self, appcontrol, guirequests, width=1200, height=1000, title=None, logfile=None):
        self.appcontrol = appcontrol
        self.app_thread = threading.Thread(target=self.appcontrol.body, daemon=True)
        self.guirequests = guirequests
        self.me = Path(sys.argv[0])
        self.appname = self.me.name
        self.here = self.me.parent
        self.home = Path.home()
        self.root = None
        self.width = width
        self.height = height
        if title:
            self.title = title
        else:
            self.title = self.appname
        if logfile == "auto":
            logfile = str(self.home / (str(self.appname) + ".log"))
        ###
        super().__init__(logfile=logfile)
        ###
        # print("Hello\n")
        self._args_setup_and_parse()

    def _args_setup_and_parse(self):
        self.appcontrol.extend_parser(self.parser)
        self.perform_parse()
        self.appcontrol.parsed_args(self.args)

    def takeover_main_thread(self):
        # ### root window init
        self.root = tk.Tk()
        self._root_init()
        self._process_events()

    def _root_init(self):
        self.root.title(self.title)
        window_width = self.width
        window_height = self.height
        # get the screen dimension
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        # find the center point
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        # set the position of the window to the center of the screen
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.root.resizable(True, True)

    def _process_events(self):
        self.app_thread.start()
        self.guirequests.server_start_periodic(self.root, 100)
        self.root.mainloop()

    def get_args(self):
        return self.args

    def get_root(self):
        return self.root
