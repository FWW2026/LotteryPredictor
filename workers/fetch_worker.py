from PySide6.QtCore import QThread, Signal

import requests
import urllib3

urllib3.disable_warnings()


class FetchWorker(QThread):

    finished = Signal(list)
    error = Signal(str)

    def __init__(self, url, count):
        super().__init__()

        self.url = url
        self.count = count

    def run(self):

        try:

            r = requests.get(
                self.url,
                verify=False,
                timeout=20
            )

            data = r.json()

            if data["code"] != 1:
                raise Exception(data["msg"])

            records = data["data"]

            records = records[:self.count]

            self.finished.emit(records)

        except Exception as e:

            self.error.emit(str(e))