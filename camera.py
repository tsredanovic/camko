import logging
from queue import Queue
from threading import Thread
from time import sleep

import cv2


class VideoStream:
    def __init__(self, path, queue_size=3):
        self.path = path
        self.stream = cv2.VideoCapture(self.path)
        self.Q = Queue(maxsize=queue_size)

    def start(self):
        # start a thread to read frames from the video stream
        Thread(target=self.update, daemon=True).start()
        return self

    def reconnect(self):
        while True:
            logging.info('Camera reconnecting.')
            self.stream = cv2.VideoCapture(self.path)
            if self.stream.isOpened():
                logging.info('Camera reconnected.')
                break

            sleep(5)

    def update(self):
        try:
            while True:
                if not self.Q.full():
                    grabbed, frame = self.stream.read()

                    if not grabbed:
                        logging.info('Camera disconnected.')
                        self.stream.release()
                        self.reconnect()
                        continue

                    self.Q.put(frame)

                    # Clean the queue to keep only the latest frame
                    while self.Q.qsize() > 1:
                        self.Q.get()
        except Exception as e:
            logging.error(str(e))

    def read(self):
        return self.Q.get()

    def __exit__(self, exception_type, exception_value, traceback):
        self.stream.release()
