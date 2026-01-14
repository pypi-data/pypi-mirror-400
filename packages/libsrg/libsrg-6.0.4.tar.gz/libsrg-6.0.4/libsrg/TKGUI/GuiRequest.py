# libsrg (Code and Documentation) is published under an MIT License
# Copyright (c) 2023,2024 Steven Goncalo
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

import threading


class GuiRequest:
    GET_NEW_LABEL = "get_new_label"
    EXIT = "exit"

    def __init__(self, action: str, **kwargs):
        self.action = action
        self.kwargs = kwargs
        self.result = None
        self.success = False
        self.exception = None
        self.sem = threading.Semaphore(0)  # sem is initially BLOCKED

    def __str__(self):
        s = f"GuiRequest {self.action} {self.kwargs}"
        return s
