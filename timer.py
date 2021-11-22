import time
import uuid


class TimerManager:
    def __init__(self):
        self._timers = {}

    def add_timer(self, interval, callback, repeat=False):
        self._timers[uuid.uuid4()] = {
            "target_time": int(time.time_ns() / 1000000) + interval,
            "interval": interval,
            "repeat": repeat,
            "callback": callback,
        }

    def remove_timer(self, timer_id):
        del self._timers[timer_id]

    def run(self):
        current_time_ms = int(time.time_ns() / 1000000)

        for timer_id, t in self._timers.items():
            if t["target_time"] <= current_time_ms:
                t["callback"]()

                if t["repeat"] is False:
                    t["target_time"] = int(time.time_ns() / 1000000) + t["interval"]
                    self.remove_timer(timer_id)
