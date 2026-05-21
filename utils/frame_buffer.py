# Import the threading module (often used alongside queues for multi-threaded applications)
import threading

# Import the queue module to create a thread-safe data structure for storing frames
import queue

class FrameBuffer:
    def __init__(self, maxsize=2):
        # Initialize a thread-safe Queue object that will hold the frames
        # By default, it limits the size to 2 frames to ensure we only process the most recent data
        self.queue = queue.Queue(maxsize=maxsize)

    def put(self, frame):
        # Check if the queue has already reached its maximum capacity
        if self.queue.full():
            try:
                # If full, immediately remove the oldest frame without waiting to make room
                self.queue.get_nowait()
            except queue.Empty:
                # If the queue was somehow emptied right before removing an item, ignore the error and proceed
                pass
                
        # Insert the fresh, newly captured frame into the queue
        self.queue.put(frame)

    def get(self):
        # Extract and return the oldest available frame from the buffer
        # If the queue is empty, wait up to 1.0 second for a frame to arrive before failing
        return self.queue.get(timeout=1.0)