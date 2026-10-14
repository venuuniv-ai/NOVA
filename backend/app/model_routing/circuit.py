import threading
import time


class Circuit:
    """Single-process protection: one half-open probe, bounded cooldown, no health polling loop."""

    def __init__(self, threshold=3, cooldown=30, clock=time.monotonic):
        self.threshold, self.cooldown, self.clock = threshold, cooldown, clock
        self.failures, self.until, self.probing = 0, 0.0, False
        self.lock = threading.Lock()

    def state(self):
        with self.lock:
            if self.until and self.clock() < self.until:
                return "OPEN"
            if self.until:
                return "HALF_OPEN"
            return "CLOSED"

    def admit(self):
        with self.lock:
            if self.until and self.clock() < self.until:
                return False
            if self.until:
                if self.probing:
                    return False
                self.probing = True
            return True

    def success(self):
        with self.lock:
            self.failures, self.until, self.probing = 0, 0.0, False

    def failure(self):
        with self.lock:
            self.failures += 1
            if self.failures >= self.threshold or self.probing:
                self.until = self.clock() + self.cooldown
            self.probing = False

    def cancel(self):
        with self.lock:
            self.probing = False
