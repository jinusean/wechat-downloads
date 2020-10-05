from multiprocessing import Process
from tkinter import Tk, messagebox
from tkinter.filedialog import askdirectory
import time

import logging
logger = logging.getLogger(__name__)


class TkinterProcess(Process):
    def __init__(self, pipe_conn):
        self.pipe_conn = pipe_conn
        super().__init__()


    def run(self):
        tk = Tk()
        tk.withdraw()

        logger.info('Running TkinterProcess')
        while True:
            try:
                recv = self.pipe_conn.recv()
                cmd = recv[0]
                logger.info('TkinterProcess:',cmd)

                if cmd == 'terminate':
                    break

                if cmd == 'askdirectory':
                    res = askdirectory(initialdir=recv[1])
                    logger.info('askdirectory', res)
                    self.pipe_conn.send(res)
                elif cmd == 'showinfo':
                    res = messagebox.showinfo(title='WeChatDownloads',message=recv[1])
                    logger.info('showinfo', res)
                    self.pipe_conn.send(res)
                elif cmd == 'askyesno':
                    res = messagebox.askyesno(title='WeChatDownloads', message=recv[1])
                    logger.info('askokcancel', res)
                    self.pipe_conn.send(res)
            except EOFError:
                pass

            time.sleep(10)

        logger.info('TkinterProcess closing')
        tk.destroy()


