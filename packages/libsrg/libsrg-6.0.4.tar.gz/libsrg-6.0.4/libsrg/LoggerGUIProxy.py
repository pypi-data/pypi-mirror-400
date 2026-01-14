# libsrg (Code and Documentation) is published under an MIT License
# Copyright (c) 2023,2024 Steven Goncalo
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# 2024 Steven Goncalo
import logging

GUI_NEW_LINE = "GUI_NEW_LINE"
GUI_FREEZE_LINE = "GUI_FREEZE_LINE"
GUI_CONFIGURE = "GUI_CONFIGURE"


class LoggerGUIProxy:
    """
    LoggerGUIProxy provides several methods to control the LoggerGUI via calls to logging.
    """

    logger = logging.getLogger("LoggerGUIProxy")

    @classmethod
    def gui_new_line(cls, logr=None):
        """
        Schedule the GUI line item for this thread to be deleted and disassociate it with this thread.
        If subsequent logging occurs from the same thread, a new GUI line is created.
        """
        if not logr:
            logr = cls.logger
        logr.info(GUI_NEW_LINE)

    @classmethod
    def gui_freeze_line(cls, logr=None):
        """
        Freeze the current contents of the GUI line for this thread.
        Do not schedule the GUI line item for this thread to be deleted but disassociate it with this thread.
        If subsequent logging occurs from the same thread, a new GUI line is created.
        """
        if not logr:
            logr = cls.logger
        logr.info(GUI_FREEZE_LINE)

    @classmethod
    def gui_configure(cls, logr=None, **kwargs):
        """
        Send one or more logs to set configuration values for the GUI line associated with this thread.
        Each log sent is a single name/value pair.
        """
        if not logr:
            logr = cls.logger
        for key, val in kwargs.items():
            txt = f"GUI_CONFIGURE {key}={val}"
            logr.info(txt)
