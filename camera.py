from queue import Queue
from threading import Thread

import cv2


class VideoStream:
    def __init__(self, path, queue_size=3):
        self.stream = cv2.VideoCapture(path)
        self.Q = Queue(maxsize=queue_size)

    def start(self):
        # start a thread to read frames from the video stream
        Thread(target=self.update, daemon=True).start()
        return self

    def update(self):
        try:
            while True:
                if not self.Q.full():
                    grabbed, frame = self.stream.read()

                    self.Q.put(frame)

                    # Clean the queue to keep only the latest frame
                    while self.Q.qsize() > 1:
                        self.Q.get()
        except Exception as e:
            print('Got error: {}'.format(str(e)))

    def read(self):
        return self.Q.get()

    def __exit__(self, exception_type, exception_value, traceback):
        self.stream.release()
