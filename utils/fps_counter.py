# Import the time module to access high-resolution performance clocks
import time

# Import deque (double-ended queue) to efficiently manage a rolling list of timestamps
from collections import deque

class FPSCounter:
    def __init__(self, history_size: int = 30):
        # Create a deque to store time records for the specified amount of frames (30 by default)
        # When it reaches the max length, adding a new item automatically drops the oldest one
        self._timestamps: deque = deque(maxlen=history_size)

    def tick(self) -> float:
        # Get a highly accurate timestamp of the exact moment this line executes
        now = time.perf_counter()
        
        # Add the current timestamp to the end of our rolling history
        self._timestamps.append(now)
        
        # Check if we have at least two timestamps to compare; FPS needs a time difference
        if len(self._timestamps) < 2:
            return 0.0
            
        # Calculate the total time elapsed between the oldest timestamp (index 0) and the newest (index -1)
        elapsed = self._timestamps[-1] - self._timestamps[0]
        
        # Calculate FPS: Divide the number of frame intervals (total timestamps minus 1) by the total elapsed time
        # The 'if elapsed > 0 else 0.0' prevents a division by zero error if the time difference is extremely small
        return (len(self._timestamps) - 1) / elapsed if elapsed > 0 else 0.0