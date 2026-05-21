import threading
import queue

class FrameBuffer:
    def __init__(self, maxsize=2):
        self.queue = queue.Queue(maxsize=maxsize)

    def put(self, frame):
        if self.queue.full():
            try:
                self.queue.get_nowait()
            except queue.Empty:
                pass
        self.queue.put(frame)

    def get(self):
        return self.queue.get(timeout=1.0)