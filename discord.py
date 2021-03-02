import logging
from queue import Queue
from threading import Thread

import requests


class DiscordReportData:
    def __init__(self, image, image_name, message):
        self.image = image
        self.image_name = image_name
        self.message = message


class DiscordReporter:
    def __init__(self, webhook_url, queue_size=10):
        self.webhook_url = webhook_url
        self.Q = Queue(maxsize=queue_size)

    def start(self):
        # start a thread to check and report
        Thread(target=self.check_and_report, daemon=True).start()
        return self

    def check_and_report(self):
        try:
            while True:
                data = self.Q.get()

                requests.post(url=self.webhook_url,
                              files={
                                  'content': (None, data.message),
                                  'file': (data.image_name, data.image)
                              })

                self.Q.task_done()
        except Exception as e:
            logging.error(str(e))

    def report(self, data):
        self.Q.put(data)
