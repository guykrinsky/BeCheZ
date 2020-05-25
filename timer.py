import time


class TimeError(Exception):
    """
    Errors on timer class.
    """


class Timer:
    def __init__(self):
        self.start_time = time.perf_counter()
        self.time_passed = 0
        self.time_paused = 0
        self.total_time_paused = 0
        self.is_pause = False

    def pause(self):
        if self.is_pause:
            raise TimeError("timer can't pause because already paused")
        self.time_paused = time.perf_counter()
        self.is_pause = True

    def resume(self):
        if not self.is_pause:
            raise TimeError("timer can't resume because timer isn't paused")
        self.is_pause = False
        self.total_time_paused += time.perf_counter() - self.time_paused

    def get_seconds(self):
        self._update_timer()
        return int(self.time_passed)

    def _update_timer(self):
        if self.is_pause:
            return
        self.time_passed = time.perf_counter() - self.start_time - self.total_time_paused
