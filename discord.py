from queue import Queue
from threading import Thread

import requests


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
                person = self.Q.get()
                requests.post(url=self.webhook_url,
                              files={
                                  'content': (None, person.msg_door()),
                                  'file': ('{}.png'.format(person.name.replace(' ', '_').lower()), person.detected_img)
                              })
                self.Q.task_done()
        except Exception as e:
            print('Got error: {}'.format(str(e)))

    def report(self, person):
        self.Q.put(person)
