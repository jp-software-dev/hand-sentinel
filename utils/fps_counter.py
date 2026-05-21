import time
from collections import deque

class FPSCounter:
    def __init__(self, history_size: int = 30):
        self._timestamps: deque = deque(maxlen=history_size)

    def tick(self) -> float:
        now = time.perf_counter()
        self._timestamps.append(now)
        if len(self._timestamps) < 2:
            return 0.0
        elapsed = self._timestamps[-1] - self._timestamps[0]
        return (len(self._timestamps) - 1) / elapsed if elapsed > 0 else 0.0