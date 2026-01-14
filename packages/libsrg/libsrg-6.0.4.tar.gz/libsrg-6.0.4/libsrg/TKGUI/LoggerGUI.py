# libsrg (Code and Documentation) is published under an MIT License
# Copyright (c) 2023,2024 Steven Goncalo
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

import logging
import sys
import threading
import tkinter as tk
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from logging import LogRecord
from pathlib import Path
from queue import Queue, Empty
from threading import Thread
from time import sleep
from tkinter import ttk

from libsrg.LoggerGUIProxy import LoggerGUIProxy, GUI_CONFIGURE, GUI_NEW_LINE, GUI_FREEZE_LINE
from libsrg.LoggingAppBase import LoggingAppBase
from libsrg.LoggingCounter import LoggingCounter
from libsrg.LoggingWatcher import LoggingWatcher
# noinspection PyPep8Naming
import tkinter.font as tkFont


class LoggerGUI:
    logger = logging.getLogger("LoggerGUI")
    _instance: "LoggerGUI" = None

    @classmethod
    def get_instance(cls, title: str = None):
        if cls._instance is None:
            cls._instance = LoggerGUI()
        if title:
            cls._instance.set_title(title)
        return cls._instance

    def set_title(self, title: str):
        self.root.title(title)

    def __init__(self):
        self.queue = Queue()
        self.exiting = False
        self.watcher = LoggingWatcher.attach()
        self.status_queue = self.watcher.get_queue()
        self.status_map: dict[int, ttk.Label] = {}
        self.dropped_gui_lines = Counter()
        self.terminate_callbacks = []

        # ### root window init
        self.root = tk.Tk()

        #        self.root.option_add("*Font", "Arial 12 normal")

        def_font = tkFont.nametofont("TkDefaultFont")
        self.logger.info(f"{tkFont.families()=}")
        self.logger.info(f"{tkFont.names()=}")

        for nam in tkFont.names():
            fon = tkFont.nametofont(nam)
            self.logger.info(f"{nam=} {fon.actual()}")
            fon.configure(size=48, family="liberation mono")
            self.logger.info(f"{nam=} {fon.actual()}")

        self.custom_font = tkFont.Font(family="liberation mono", size=24)
        self.logger.info(f"custom {self.custom_font=} {self.custom_font.actual()=}")
        self._root_init()

        # for f in ["fixed","Adwaita","Adwaita Sans","liberation mono"]:
        #     for s in [12,18,24,32,48]:
        #         # Define a custom font
        #         self.custom_font = tkFont.Font(family="liberation mono", size=s)
        #         self.logger.info(f"custom {f} {s} {self.custom_font=} {self.custom_font.actual()=}")

        self.logger.info("LoggerGUI Initiated")
        self.terminate_but = self._add_button_as_gui("TERMINATE", self.terminate)
        style_red = ttk.Style()
        sname = 'R.TButton'
        style_red.configure(sname, foreground='red', background='grey', font=self.custom_font)
        self.terminate_but.configure(style=sname)

        lab = ttk.Label(self.root, text="LOGGING SUMMARY", font=self.custom_font)
        lab.pack(fill=tk.X)
        lab.configure(justify=tk.LEFT, anchor='w', relief=tk.RAISED)
        self.watcher_lab = lab

    def schedule_terminate_callback(self, callback):
        self.terminate_callbacks.append(callback)

    def _perform_terminate_callbacks(self):
        for callback in self.terminate_callbacks:
            self.logger.info(f"callback to {callback}")
            callback()

    def schedule_callback(self, delayms, callback):
        self.root.after(delayms, callback)

    def gui_main_loop(self):
        self.root.after(100, self._service_queue)
        LoggerGUIProxy.gui_configure(background='dark green')
        self.logger.info("main thread is now in GUI main loop")
        self.root.mainloop()

    def req_new_label(self, txt: str) -> ttk.Label:
        self.logger.info(txt)
        qreq = QReq(QReq.GET_NEW_LABEL, txt=txt)
        self.queue.put(qreq)
        self.logger.info("acquiring")
        qreq.sem.acquire()
        self.logger.info("acquired")
        return qreq.lab

    def req_destroy_label(self, lab: ttk.Label):
        qreq = QReq(QReq.DESTROY_LABEL, lab=lab)
        self.queue.put(qreq)
        self.check_exit()
        self.logger.info("acquiring")
        qreq.sem.acquire()
        self.logger.info("acquired")
        self.check_exit()
        return

    def req_configure_label(self, lab: ttk.Label, **kwargs):
        qreq = QReq(QReq.CONFIGURE_LABEL, lab=lab, **kwargs)
        self.queue.put(qreq)
        self.check_exit()
        self.logger.info("acquiring")
        qreq.sem.acquire()
        self.logger.info("acquired")
        self.check_exit()
        return

    def tell_gui_to_exit(self):
        self.logger.info("request")
        qreq = QReq(QReq.EXIT)
        self.queue.put(qreq)
        # does not wait

    def check_exit(self):
        if self.exiting:
            exit()

    def terminate(self):
        self.exiting = True
        self._perform_terminate_callbacks()

    def _handle_req(self, req: "QReq"):

        if req.action == QReq.GET_NEW_LABEL:
            lab = ttk.Label(self.root, text=req.txt, font=self.custom_font)
            lab.pack(fill=tk.X, expand=True)  # was X
            lab.configure(justify=tk.LEFT, anchor='w', relief=tk.RAISED)
            req.lab = lab
            req.sem.release()
            print("QQQ _handle_req")
            self.logger.info("QQQ new lable")
            raise Exception("got here")
        if req.action == QReq.CONFIGURE_LABEL:
            lab = req.lab
            self.logger.info(req)
            lab.configure(**req.kwargs)
            req.sem.release()
        if req.action == QReq.DESTROY_LABEL:
            req.lab.destroy()
        if req.action == QReq.EXIT:
            self.exiting = True

    def _service_status(self):
        # batch up all current before processing more
        batch: list[LogRecord] = []
        while not self.status_queue.empty():
            record: LogRecord = self.status_queue.get()
            batch.append(record)
        if batch:
            self.watcher_lab[
                'text'] = f"Logging counters: {str(LoggingCounter.get_instance().count_at_level_name)}"
        for record in batch:
            uctext = record.message.upper()
            if uctext == GUI_NEW_LINE or uctext == GUI_FREEZE_LINE:
                if record.thread in self.status_map:
                    oldlab = self.status_map.pop(record.thread)
                    if uctext == GUI_NEW_LINE:
                        self.dropped_gui_lines[oldlab] = 1
            elif uctext.startswith(GUI_CONFIGURE):
                txt = record.message[13:].strip()
                parts = txt.split('=')
                if len(parts) == 2:
                    kwargs = {parts[0]: parts[1].strip(""""'""")}
                    lab = self._find_lab(record.thread, record.message)
                    lab.configure(**kwargs)
            else:
                lab = self._find_lab(record.thread, record.message)
                lab["text"] = f"{record.levelname} {record.message}"
        self._prune_status()

    def _prune_status(self):
        doomed = []
        for lab in self.dropped_gui_lines.keys():
            # lab.configure(foreground="red")
            self.dropped_gui_lines[lab] += 1
            cnt = self.dropped_gui_lines.get(lab)
            if cnt > 15:
                doomed.append(lab)
        for lab in doomed:
            self.dropped_gui_lines.pop(lab)
            lab.destroy()

    def _find_lab(self, ithread: int, text: str = None) -> ttk.Label:
        if ithread not in self.status_map:
            if not text:
                text = "..."
            lab = ttk.Label(self.root, text=text, font=self.custom_font)
            lab.pack(fill=tk.X)
            lab.configure(justify=tk.LEFT, anchor='w', relief=tk.RAISED)

            self.status_map[ithread] = lab
        else:
            lab = self.status_map[ithread]
        return lab

    def _service_queue(self):
        try:
            self._service_status()

            while not (self.queue.empty()):
                self.logger.info("getting")
                qreq: QReq = self.queue.get_nowait()
                self.logger.info(f"got {qreq}")
                self._handle_req(qreq)
        except Empty:
            pass
        except Exception as ex:
            self.logger.error(ex, exc_info=True)
        finally:
            self.check_exit()
            self.root.after(100, self._service_queue)

    def _root_init(self):
        self.root.title("LoggerGUI Default Title")

        # get the screen dimension
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = min(screen_width / 2, 1920)
        window_height = min(screen_height / 2, 1080)
        # find the center point
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        # set the position of the window to the center of the screen
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.root.resizable(True, True)

    def _add_button_as_gui(self, text: str, command):
        but = ttk.Button(self.root, text=text)
        but.pack(fill=tk.X)
        but.configure(command=command)
        return but


class QReq:
    GET_NEW_LABEL = "get_new_label"
    EXIT = "exit"
    DESTROY_LABEL = "destroy_label"
    CONFIGURE_LABEL = "configure_label"

    def __init__(self, action: str, lab: ttk.Label = None, txt: str = None, **kwargs):
        self.action = action
        self.lab = lab
        self.txt = txt
        self.sem = threading.Semaphore(0)  # sem is initially BLOCKED
        self.kwargs = kwargs

    def __str__(self):
        s = f"QReq {self.action} {self.kwargs}"
        if self.txt:
            s += self.txt
        return s


class DummyMain(LoggingAppBase):

    def __init__(self):
        me = Path(sys.argv[0])
        self.project_dir = me.parent
        if self.project_dir.name == "vidscrape":
            self.project_dir = self.project_dir.parent
        logfile = str(self.project_dir / "DummyMain.log")
        super().__init__(logfile=logfile)

        self.args_setup_then_parse()

        self.gui = LoggerGUI.get_instance()

        self.executor = ThreadPoolExecutor(4)

        self.logger.info("Starting scraper")
        self.scrape_thread = Thread(target=self.scrape_in_thread)
        self.scrape_thread.start()
        self.scrape_thread2 = Thread(target=self.scrape_in_thread2)
        self.scrape_thread2.start()

        # must run LoggerGUI in main thread
        self.gui.gui_main_loop()

    def args_setup_then_parse(self):
        ssp = self.project_dir / "ScrapeScript.txt"
        sss = str(ssp)
        self.parser.add_argument('--script', help='script of files to scrape', default=sss,
                                 type=str)
        # from base app
        self.perform_parse()
        #

    def scrape_in_thread(self):
        self.logger.info(GUI_NEW_LINE)
        i = 0
        for i in range(8):
            i += 1
            sleep(1)
            if i == 4:
                self.logger.info(GUI_CONFIGURE + " background=pink")
            self.logger.info(f"Idle loop {i}")
            kwa = {"num": f"X{i}"}
            th = Thread(target=self.bottlerocket, kwargs=kwa, name=f"Y{i}")
            th.start()

    def scrape_in_thread2(self):
        self.logger.info(GUI_NEW_LINE)
        for i in range(8):
            sleep(1.5)
            self.logger.info(f"Idle loop2 {i}")
            self.executor.submit(self.bottlerocket, num=i)
        self.logger.info("Dirt nap...")
        LoggerGUI.get_instance().schedule_callback(delayms=200, callback=self.bye())

    @staticmethod
    def bye():
        LoggerGUI.get_instance().tell_gui_to_exit()

    def bottlerocket(self, num):
        self.logger.info(GUI_NEW_LINE)
        for i in range(4):
            if i == 3:
                LoggerGUIProxy.gui_configure(background='cyan')
            sleep(1)
            self.logger.info(f"Bottle Rocket {num} cycle {i}")
        self.logger.debug(GUI_NEW_LINE)
        sleep(2)


if __name__ == '__main__':
    scraper = DummyMain()
