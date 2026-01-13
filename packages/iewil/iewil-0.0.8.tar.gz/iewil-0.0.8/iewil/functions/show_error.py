import sys
import os
import atexit
import traceback
from datetime import datetime

from .display import Display


class ShowError:
    def __init__(self, log_file="error.log"):
        self.log_file = log_file
        self.last_error_msg = None

    def start(self):
        # hapus log lama
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

        Display.info(f"all errors are displayed and logged in {self.log_file}")
        Display.line()

        # hook error global
        sys.excepthook = self.handle_exception

        # shutdown handler
        atexit.register(self.handle_shutdown)

    def handle_exception(self, exc_type, exc, tb):
        filename = os.path.basename(tb.tb_frame.f_code.co_filename)
        line = tb.tb_lineno
        message = f"{exc} | {filename} | {line}"

        self.log(message)
        # jangan tampilkan traceback default
        # comment baris ini kalau mau traceback tetap muncul
        # return

    def handle_shutdown(self):
        # placeholder kalau mau logic tambahan saat exit
        pass

    def log(self, message):
        if self.last_error_msg == message:
            return

        self.last_error_msg = message
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{date}] {message}\n")
