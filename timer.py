import time


class TimeError(Exception):
    """
    Errors on timer class.
    """


def set_timer(team_got_turn, white_team, black_team):
    white_timer = white_team.timer
    black_timer = black_team.timer
    if team_got_turn is white_team:
        white_timer.resume()
        black_timer.pause()
    else:
        black_timer.resume()
        white_timer.pause()


def set_game_length(minutes):
    Timer.GAME_LENGTH = minutes*60


def sleep(sleep_time):
    time.sleep(sleep_time)


class Timer:
    # IN_SECONDS.
    GAME_LENGTH = 300

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

    def get_seconds_left_to_last_minute(self):
        self._update_timer()
        return int(60 - self.get_seconds() % 60)

    def get_minutes_left(self):
        self._update_timer()
        return int(self.GAME_LENGTH / 60 - self.get_seconds() / 60)

    def _update_timer(self):
        if self.is_pause:
            return
        self.time_passed = time.perf_counter() - self.start_time - self.total_time_paused

    def is_game_ended(self):
        return self.get_seconds() >= self.GAME_LENGTH
